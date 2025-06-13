import numpy as np
import logging
import random
import re
import os
from sentence_transformers import SentenceTransformer, util
from .adaptive_engine import get_db_connection
import psycopg2.extras
from typing import Tuple, Optional, Dict, Any
import time
from functools import lru_cache

# --- GLOBAL MODEL CACHE ---
_model_cache = None
_model_load_time = None

def load_similarity_model():
    """Load the similarity model with proper error handling, caching, and faster loading."""
    global _model_cache, _model_load_time
    
    # Return cached model if available and loaded recently
    if _model_cache is not None:
        return _model_cache
    
    model_name = 'all-MiniLM-L6-v2'  # This is already a fast, lightweight model
    cache_dir = os.environ.get('TRANSFORMERS_CACHE', './model_cache')
    
    try:
        start_time = time.time()
        logging.info("Loading Semantic Similarity model...")
        
        # Load with optimizations
        model = SentenceTransformer(
            model_name, 
            cache_folder=cache_dir,
            device='cpu'  # Explicitly use CPU for consistency
        )
        
        # Cache the model globally
        _model_cache = model
        _model_load_time = time.time() - start_time
        
        logging.info(f"Semantic Similarity model loaded successfully in {_model_load_time:.2f}s")
        return model
        
    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")
        
        # Try minimal fallback
        try:
            logging.info("Attempting fallback model loading...")
            model = SentenceTransformer(model_name, cache_folder=cache_dir, use_auth_token=False)
            _model_cache = model
            return model
        except Exception as e2:
            logging.error(f"All model loading attempts failed: {str(e2)}")
            _model_cache = None
            return None

# Initialize model on import
similarity_model = load_similarity_model()

@lru_cache(maxsize=1000)
def cached_similarity_check(user_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """Cached version of similarity checking for repeated answer patterns."""
    return _perform_similarity_check(user_answer, correct_answer)

def extract_number(text: str, target_number: str = None) -> Optional[str]:
    """Enhanced number extraction with better patterns."""
    if not text:
        return None
        
    if target_number:
        # Look for the specific target number with word boundaries
        patterns = [
            r'\b' + re.escape(target_number) + r'\b',  # Exact word match
            r'(?<!\d)' + re.escape(target_number) + r'(?!\d)',  # No adjacent digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
    
    # Enhanced number finding patterns
    patterns = [
        r'\b\d+\.\d+\b',  # Decimals
        r'\b\d+\b',       # Integers
        r'\d+',           # Any digits
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None

def _perform_similarity_check(user_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """Core similarity checking logic."""
    if not user_answer or not correct_answer:
        return False, 0.0
    
    # Fast numeric check first
    if correct_answer.replace('.', '').isdigit():
        extracted_number = extract_number(user_answer, correct_answer)
        if extracted_number == correct_answer:
            return True, 1.0
        # Check for close numeric matches
        try:
            user_num = float(extract_number(user_answer) or '0')
            correct_num = float(correct_answer)
            if abs(user_num - correct_num) < 0.01:  # Very close numbers
                return True, 0.95
        except (ValueError, TypeError):
            pass
    
    # Use similarity model if available
    if similarity_model is not None:
        try:
            # Preprocess for better similarity
            user_clean = user_answer.lower().strip()
            correct_clean = correct_answer.lower().strip()
            
            embedding1 = similarity_model.encode(user_clean, convert_to_tensor=True)
            embedding2 = similarity_model.encode(correct_clean, convert_to_tensor=True)
            similarity_score = util.cos_sim(embedding1, embedding2).item()
            
            # More nuanced thresholds
            if similarity_score > 0.85:
                return True, similarity_score
            elif similarity_score > 0.7:
                # Additional checks for partial correctness
                return _additional_similarity_checks(user_clean, correct_clean, similarity_score)
            else:
                return False, similarity_score
                
        except Exception as e:
            logging.error(f"Error in semantic similarity: {str(e)}")
    
    # Enhanced fallback logic
    return _fallback_similarity_check(user_answer, correct_answer)

def _additional_similarity_checks(user_answer: str, correct_answer: str, base_score: float) -> Tuple[bool, float]:
    """Additional checks for borderline similarity scores."""
    user_words = set(user_answer.split())
    correct_words = set(correct_answer.split())
    
    # Key word overlap
    overlap_ratio = len(user_words.intersection(correct_words)) / max(len(correct_words), 1)
    
    # Boost score if good word overlap
    if overlap_ratio > 0.6:
        return True, min(base_score + 0.1, 1.0)
    
    # Check for containing relationship
    if correct_answer in user_answer or user_answer in correct_answer:
        return True, min(base_score + 0.05, 1.0)
    
    return base_score > 0.75, base_score

def _fallback_similarity_check(user_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """Enhanced fallback when model is unavailable."""
    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()
    
    # Exact match
    if user_clean == correct_clean:
        return True, 1.0
    
    # Containment check
    if correct_clean in user_clean:
        return True, 0.9
    if user_clean in correct_clean:
        return True, 0.8
    
    # Word-based similarity
    user_words = set(user_clean.split())
    correct_words = set(correct_clean.split())
    
    if correct_words:
        overlap = len(user_words.intersection(correct_words))
        total_words = len(correct_words)
        similarity = overlap / total_words
        
        return similarity > 0.6, similarity
    
    return False, 0.0

def check_semantic_similarity(user_answer: str, correct_answer: str) -> Tuple[bool, float]:
    """Main interface for similarity checking with caching."""
    if not user_answer or not correct_answer:
        return False, 0.0
    
    # Use cache for repeated patterns
    return cached_similarity_check(user_answer.strip(), correct_answer.strip())

class AdaptiveDifficultySelector:
    """Improved difficulty selection with faster adaptation."""
    
    def __init__(self):
        self.min_attempts_for_stability = 2  # Reduced even more for faster response
        self.success_threshold_up = 0.75      # Move up if >75% success
        self.success_threshold_down = 0.5     # Move down if <50% success (was 0.4)
        self.confidence_boost = 0.1           # Boost for consecutive successes
        self.struggle_penalty = 0.2           # Penalty for consecutive failures
    
    def get_recent_performance(self, user_id: int, lesson_id: int, difficulty: int, limit: int = 7) -> Dict[str, Any]:
        """Get recent performance metrics for faster decision making using existing user_progress table."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get recent attempts for this specific difficulty using your existing schema
        # We'll need to join with questions table to get difficulty level
        cur.execute("""
            SELECT up.is_correct, up.answered_at 
            FROM user_progress up
            JOIN questions q ON up.question_id = q.id
            WHERE up.user_id = %s 
              AND q.lesson_id = %s 
              AND q.difficulty_level = %s 
            ORDER BY up.answered_at DESC 
            LIMIT %s
        """, (user_id, lesson_id, difficulty, limit))
        
        recent_attempts = cur.fetchall()
        cur.close()
        conn.close()
        
        if not recent_attempts:
            return {'recent_success_rate': 0, 'consecutive_correct': 0, 'consecutive_wrong': 0, 'total_attempts': 0}
        
        successes = sum(1 for attempt in recent_attempts if attempt['is_correct'])
        recent_success_rate = successes / len(recent_attempts)
        
        # Count consecutive results from most recent
        consecutive_correct = 0
        consecutive_wrong = 0
        
        for attempt in recent_attempts:
            if attempt['is_correct']:
                if consecutive_wrong == 0:
                    consecutive_correct += 1
                else:
                    break
            else:
                if consecutive_correct == 0:
                    consecutive_wrong += 1
                else:
                    break
        
        return {
            'recent_success_rate': recent_success_rate,
            'consecutive_correct': consecutive_correct,
            'consecutive_wrong': consecutive_wrong,
            'total_attempts': len(recent_attempts)
        }
    
    def select_difficulty(self, user_id: int, lesson_id: int) -> int:
        """Fast, adaptive difficulty selection."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get current bandit state
        cur.execute("""
            SELECT difficulty_level, times_selected, successful_outcomes 
            FROM bandit_state 
            WHERE user_id = %s AND lesson_id = %s
            ORDER BY difficulty_level
        """, (user_id, lesson_id))
        
        states = cur.fetchall()
        cur.close()
        conn.close()
        
        if not states:
            logging.info(f"New user {user_id} for lesson {lesson_id}, starting at level 1")
            return 1
        
        # Find current best performing difficulty
        current_best = self._find_current_best(states)
        
        # Get recent performance for the current best difficulty
        recent_perf = self.get_recent_performance(user_id, lesson_id, current_best)
        
        # Make fast adaptation decision
        new_difficulty = self._make_adaptation_decision(current_best, recent_perf, states)
        
        logging.info(f"User {user_id}: Current best {current_best}, Recent performance: {recent_perf['recent_success_rate']:.2f}, Selected: {new_difficulty}")
        
        return new_difficulty
    
    def _find_current_best(self, states) -> int:
        """Find the best performing difficulty level."""
        best_difficulty = 1
        best_score = -1
        
        state_dict = {s['difficulty_level']: s for s in states}
        
        for level in sorted(state_dict.keys()):
            state = state_dict[level]
            if state['times_selected'] == 0:
                continue
                
            success_rate = state['successful_outcomes'] / state['times_selected']
            
            # Prefer higher difficulties with similar success rates
            score = success_rate + (level - 1) * 0.1
            
            if score > best_score:
                best_score = score
                best_difficulty = level
        
        return best_difficulty
    
    def _make_adaptation_decision(self, current_difficulty: int, recent_perf: Dict[str, Any], states) -> int:
        """Make quick adaptation decisions based on recent performance."""
        success_rate = recent_perf['recent_success_rate']
        consecutive_correct = recent_perf['consecutive_correct']
        consecutive_wrong = recent_perf['consecutive_wrong']
        total_attempts = recent_perf['total_attempts']
        
        # AGGRESSIVE downward adjustment for struggling users
        if consecutive_wrong >= 2:
            # Drop more aggressively based on how many wrong answers
            if consecutive_wrong >= 4:
                # Drop by 2 levels for severe struggling
                new_level = max(current_difficulty - 2, 1)
                logging.info(f"SEVERE STRUGGLE: Dropping 2 levels due to {consecutive_wrong} consecutive wrong answers")
                return new_level
            elif consecutive_wrong >= 3:
                # Drop by 1-2 levels depending on current difficulty
                drop_amount = 2 if current_difficulty > 3 else 1
                new_level = max(current_difficulty - drop_amount, 1)
                logging.info(f"MAJOR STRUGGLE: Dropping {drop_amount} levels due to {consecutive_wrong} consecutive wrong answers")
                return new_level
            else:  # 2 consecutive wrong
                new_level = max(current_difficulty - 1, 1)
                logging.info(f"STRUGGLING: Dropping 1 level due to {consecutive_wrong} consecutive wrong answers")
                return new_level
        
        # Also check overall success rate for additional dropping
        if total_attempts >= 3 and success_rate <= 0.2:  # 20% or less success rate
            new_level = max(current_difficulty - 1, 1)
            logging.info(f"LOW SUCCESS RATE: Dropping due to {success_rate:.1%} success rate")
            return new_level
        
        # Check for moderate struggling (success rate between 20-40%)
        if total_attempts >= 4 and success_rate <= 0.4 and current_difficulty > 1:
            new_level = max(current_difficulty - 1, 1)
            logging.info(f"MODERATE STRUGGLE: Dropping due to {success_rate:.1%} success rate")
            return new_level
        
        # Fast upward progression for high performers
        if consecutive_correct >= 3 and success_rate >= self.success_threshold_up:
            new_level = min(current_difficulty + 1, 5)
            logging.info(f"PROMOTING: Due to {consecutive_correct} consecutive correct answers")
            return new_level
        
        # Gradual exploration for stable performance
        if total_attempts >= self.min_attempts_for_stability:
            if success_rate > 0.8 and current_difficulty < 5:
                # Try next level with high confidence
                logging.info(f"GRADUAL PROMOTION: High success rate {success_rate:.1%}")
                return current_difficulty + 1
            elif success_rate < 0.5 and current_difficulty > 1:
                # Step down for poor performance
                logging.info(f"GRADUAL DEMOTION: Low success rate {success_rate:.1%}")
                return current_difficulty - 1
        
        # Stay at current level if performance is stable
        logging.info(f"STAYING: Current level {current_difficulty}, success rate {success_rate:.1%}")
        return current_difficulty

# Global instance
difficulty_selector = AdaptiveDifficultySelector()

def select_difficulty_epsilon_greedy(user_id: int, lesson_id: int) -> int:
    """Improved difficulty selection with faster adaptation."""
    return difficulty_selector.select_difficulty(user_id, lesson_id)

def update_bandit_state(user_id: int, lesson_id: int, difficulty: int, was_correct: bool):
    """Enhanced bandit state update - now works with existing user_progress table."""
    conn = get_db_connection()
    cur = conn.cursor()
    reward = 1 if was_correct else 0

    # Update bandit state
    cur.execute("""
        INSERT INTO bandit_state (user_id, lesson_id, difficulty_level, times_selected, successful_outcomes)
        VALUES (%s, %s, %s, 1, %s) 
        ON CONFLICT (user_id, lesson_id, difficulty_level)
        DO UPDATE SET
            times_selected = bandit_state.times_selected + 1,
            successful_outcomes = bandit_state.successful_outcomes + %s
    """, (user_id, lesson_id, difficulty, reward, reward))

    # Note: Individual attempts are already tracked in your user_progress table
    # when you insert the user's answer to a specific question

    conn.commit()
    cur.close()
    conn.close()

def get_user_learning_stats(user_id: int, lesson_id: int) -> Dict[str, Any]:
    """Get comprehensive learning statistics using existing user_progress table."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get bandit state stats
    cur.execute("""
        SELECT 
            difficulty_level,
            times_selected,
            successful_outcomes,
            CASE WHEN times_selected > 0 THEN successful_outcomes::float / times_selected ELSE 0 END as success_rate
        FROM bandit_state 
        WHERE user_id = %s AND lesson_id = %s
        ORDER BY difficulty_level
    """, (user_id, lesson_id))
    
    bandit_stats = cur.fetchall()
    
    # Get recent activity from user_progress
    cur.execute("""
        SELECT 
            q.difficulty_level,
            COUNT(*) as attempts,
            SUM(CASE WHEN up.is_correct THEN 1 ELSE 0 END) as correct_answers,
            MAX(up.answered_at) as last_attempt
        FROM user_progress up
        JOIN questions q ON up.question_id = q.id
        WHERE up.user_id = %s AND q.lesson_id = %s
        GROUP BY q.difficulty_level
        ORDER BY q.difficulty_level
    """, (user_id, lesson_id))
    
    progress_stats = cur.fetchall()
    cur.close()
    conn.close()
    
    return {
        'bandit_stats': [dict(stat) for stat in bandit_stats],
        'progress_stats': [dict(stat) for stat in progress_stats],
        'total_attempts': sum(stat['times_selected'] for stat in bandit_stats),
        'overall_success_rate': sum(stat['successful_outcomes'] for stat in bandit_stats) / max(sum(stat['times_selected'] for stat in bandit_stats), 1)
    }

def reset_user_progress(user_id: int, lesson_id: int = None):
    """Reset user progress using existing tables."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if lesson_id:
        # Reset bandit state for specific lesson
        cur.execute("DELETE FROM bandit_state WHERE user_id = %s AND lesson_id = %s", (user_id, lesson_id))
        
        # Reset user progress for specific lesson
        cur.execute("""
            DELETE FROM user_progress 
            WHERE user_id = %s 
              AND question_id IN (SELECT id FROM questions WHERE lesson_id = %s)
        """, (user_id, lesson_id))
    else:
        # Reset all progress for user
        cur.execute("DELETE FROM bandit_state WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM user_progress WHERE user_id = %s", (user_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Reset progress for user {user_id}" + (f" lesson {lesson_id}" if lesson_id else " all lessons"))