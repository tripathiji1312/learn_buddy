import numpy as np
import logging
import random
import math
from typing import Dict, Any, List, Tuple
from collections import deque
import time
from dataclasses import dataclass
# ADD THIS IMPORT AT THE TOP OF THE FILE
from .adaptive_engine import get_db_connection
import psycopg2.extras # Often needed with DictCursor

@dataclass
class PerformanceMetrics:
    """Lightweight performance tracking structure."""
    success_rate: float = 0.0
    consecutive_correct: int = 0
    consecutive_wrong: int = 0
    recent_attempts: int = 0
    avg_response_time: float = 0.0
    difficulty_stability: float = 0.0
    learning_velocity: float = 0.0

class EnhancedAdaptiveDifficultySelector:
    """
    Ultra-responsive difficulty selector with multiple adaptation strategies.
    Features:
    - Immediate response to performance changes
    - Multiple learning rate strategies
    - Confidence-based exploration
    - Fast recovery mechanisms
    - Performance momentum tracking
    """
    
    def __init__(self):
        # Core thresholds - more aggressive
        self.immediate_promotion_threshold = 0.8    # Promote immediately at 80% success
        self.immediate_demotion_threshold = 0.3     # Demote immediately below 30%
        self.exploration_confidence = 0.75          # Explore higher levels at 75% confidence
        
        # Response speeds
        self.min_attempts_fast_track = 2            # Fast decisions after just 2 attempts
        self.min_attempts_stable = 5                # Stable decisions after 5 attempts
        self.consecutive_threshold_up = 2           # Promote after 2 consecutive correct
        self.consecutive_threshold_down = 2         # Demote after 2 consecutive wrong
        
        # Learning dynamics
        self.momentum_weight = 0.3                  # Weight for learning momentum
        self.recency_weight = 0.7                   # Weight recent performance more heavily
        self.difficulty_change_cooldown = 0         # No cooldown for immediate response
        
        # Multi-armed bandit parameters
        self.exploration_rate = 0.15                # Higher exploration
        self.confidence_decay = 0.95                # Confidence decay per wrong answer
        self.confidence_boost = 1.1                 # Confidence boost per correct answer
        
        # Performance windows
        self.short_window = 3                       # Immediate reaction window
        self.medium_window = 6                      # Trend analysis window
        self.long_window = 12                       # Stability analysis window
        
        # User state tracking (in-memory for speed)
        self.user_states = {}
        
    def _get_user_state(self, user_id: int, lesson_id: int) -> Dict:
        """Get or create user state for fast access."""
        key = f"{user_id}_{lesson_id}"
        if key not in self.user_states:
            self.user_states[key] = {
                'current_difficulty': 1,
                'confidence_scores': [0.5] * 5,  # Confidence for each difficulty level
                'recent_performance': deque(maxlen=self.long_window),
                'difficulty_history': deque(maxlen=20),
                'learning_momentum': 0.0,
                'last_update': time.time(),
                'streak_counter': 0,
                'struggle_counter': 0,
                'exploration_debt': 0,  # Track when we should explore
            }
        return self.user_states[key]
    
    def get_enhanced_performance_metrics(self, user_id: int, lesson_id: int, limit: int = 12) -> PerformanceMetrics:
        """Get comprehensive performance metrics with better analysis."""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get recent attempts with timing data
        cur.execute("""
            SELECT 
                up.is_correct,
                up.answered_at,
                q.difficulty_level,
                EXTRACT(EPOCH FROM (up.answered_at - LAG(up.answered_at) OVER (ORDER BY up.answered_at))) as response_time
            FROM user_progress up
            JOIN questions q ON up.question_id = q.id
            WHERE up.user_id = %s AND q.lesson_id = %s
            ORDER BY up.answered_at DESC
            LIMIT %s
        """, (user_id, lesson_id, limit))
        
        attempts = cur.fetchall()
        cur.close()
        conn.close()
        
        if not attempts:
            return PerformanceMetrics()
        
        # Calculate metrics
        correct_count = sum(1 for a in attempts if a['is_correct'])
        success_rate = correct_count / len(attempts)
        
        # Calculate consecutive streaks
        consecutive_correct = consecutive_wrong = 0
        for attempt in attempts:
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
        
        # Calculate learning velocity (improvement over time)
        if len(attempts) >= 6:
            recent_half = attempts[:len(attempts)//2]
            older_half = attempts[len(attempts)//2:]
            recent_success = sum(1 for a in recent_half if a['is_correct']) / len(recent_half)
            older_success = sum(1 for a in older_half if a['is_correct']) / len(older_half)
            learning_velocity = recent_success - older_success
        else:
            learning_velocity = 0.0
        
        # Calculate response time average
        response_times = [a['response_time'] for a in attempts if a['response_time'] is not None]
        avg_response_time = np.mean(response_times) if response_times else 0.0
        
        return PerformanceMetrics(
            success_rate=success_rate,
            consecutive_correct=consecutive_correct,
            consecutive_wrong=consecutive_wrong,
            recent_attempts=len(attempts),
            avg_response_time=avg_response_time,
            learning_velocity=learning_velocity,
            difficulty_stability=self._calculate_difficulty_stability(attempts)
        )
    
    def _calculate_difficulty_stability(self, attempts: List) -> float:
        """Calculate how stable the user is at their current difficulty."""
        if len(attempts) < 4:
            return 0.0
        
        # Group by difficulty level and calculate stability
        difficulty_performance = {}
        for attempt in attempts:
            diff = attempt['difficulty_level']
            if diff not in difficulty_performance:
                difficulty_performance[diff] = []
            difficulty_performance[diff].append(attempt['is_correct'])
        
        # Calculate variance in performance across difficulties
        stabilities = []
        for diff, results in difficulty_performance.items():
            if len(results) >= 2:
                success_rate = sum(results) / len(results)
                variance = np.var([1 if r else 0 for r in results])
                stability = success_rate * (1 - variance)  # High success, low variance = stable
                stabilities.append(stability)
        
        return np.mean(stabilities) if stabilities else 0.0
    
    def select_difficulty_ultra_responsive(self, user_id: int, lesson_id: int) -> int:
        """Ultra-responsive difficulty selection with multiple decision paths."""
        try:
            # Get user state and performance metrics
            user_state = self._get_user_state(user_id, lesson_id)
            metrics = self.get_enhanced_performance_metrics(user_id, lesson_id)
            
            current_difficulty = user_state['current_difficulty']
            
            # Update user state with recent performance
            if metrics.recent_attempts > 0:
                user_state['recent_performance'].extend([metrics.success_rate])
                user_state['learning_momentum'] = (
                    user_state['learning_momentum'] * 0.7 + 
                    metrics.learning_velocity * 0.3
                )
            
            # IMMEDIATE RESPONSE PATHS
            
            # 1. Crisis intervention - user is really struggling
            if metrics.consecutive_wrong >= 3 or (metrics.recent_attempts >= 3 and metrics.success_rate <= 0.2):
                new_difficulty = max(1, current_difficulty - 2)
                user_state['struggle_counter'] = 0  # Reset struggle counter
                logging.info(f"CRISIS INTERVENTION: Dropping to level {new_difficulty} (was {current_difficulty})")
                return self._update_and_return(user_state, new_difficulty, "crisis_intervention")
            
            # 2. Hot streak - user is performing excellently
            if metrics.consecutive_correct >= 3 or (metrics.recent_attempts >= 3 and metrics.success_rate >= 0.9):
                if current_difficulty < 5:
                    new_difficulty = min(5, current_difficulty + 1)
                    logging.info(f"HOT STREAK: Promoting to level {new_difficulty} (was {current_difficulty})")
                    return self._update_and_return(user_state, new_difficulty, "hot_streak")
            
            # 3. Fast track decisions (after minimal attempts)
            if metrics.recent_attempts >= self.min_attempts_fast_track:
                decision = self._fast_track_decision(user_state, metrics, current_difficulty)
                if decision != current_difficulty:
                    return self._update_and_return(user_state, decision, "fast_track")
            
            # 4. Confidence-based exploration
            if self._should_explore(user_state, metrics):
                exploration_level = self._get_exploration_level(user_state, metrics, current_difficulty)
                if exploration_level != current_difficulty:
                    logging.info(f"EXPLORATION: Trying level {exploration_level} (confidence-based)")
                    return self._update_and_return(user_state, exploration_level, "exploration")
            
            # 5. Momentum-based adjustment
            if abs(user_state['learning_momentum']) > 0.2:
                momentum_decision = self._momentum_based_decision(user_state, metrics, current_difficulty)
                if momentum_decision != current_difficulty:
                    return self._update_and_return(user_state, momentum_decision, "momentum")
            
            # 6. Stability-based fine-tuning
            if metrics.recent_attempts >= self.min_attempts_stable:
                stable_decision = self._stability_based_decision(user_state, metrics, current_difficulty)
                if stable_decision != current_difficulty:
                    return self._update_and_return(user_state, stable_decision, "stability")
            
            # Default: stay at current level but update confidence
            self._update_confidence_scores(user_state, metrics, current_difficulty)
            logging.info(f"MAINTAINING: Level {current_difficulty} (SR: {metrics.success_rate:.2f})")
            return current_difficulty
            
        except Exception as e:
            logging.error(f"Error in ultra-responsive difficulty selection: {e}")
            return 1  # Safe fallback
    
    def _fast_track_decision(self, user_state: Dict, metrics: PerformanceMetrics, current_difficulty: int) -> int:
        """Make fast decisions after minimal attempts."""
        
        # Immediate promotion conditions
        if (metrics.consecutive_correct >= self.consecutive_threshold_up and 
            metrics.success_rate >= self.immediate_promotion_threshold and 
            current_difficulty < 5):
            return min(5, current_difficulty + 1)
        
        # Immediate demotion conditions
        if (metrics.consecutive_wrong >= self.consecutive_threshold_down or 
            metrics.success_rate <= self.immediate_demotion_threshold) and current_difficulty > 1:
            return max(1, current_difficulty - 1)
        
        return current_difficulty
    
    def _should_explore(self, user_state: Dict, metrics: PerformanceMetrics) -> bool:
        """Determine if we should explore a different difficulty level."""
        
        # Don't explore if user is struggling
        if metrics.success_rate < 0.6 or metrics.consecutive_wrong >= 2:
            return False
        
        # Explore if user is doing well and we haven't explored recently
        if (metrics.success_rate >= self.exploration_confidence and 
            user_state['exploration_debt'] <= 0 and
            random.random() < self.exploration_rate):
            user_state['exploration_debt'] = 3  # Explore, then wait 3 decisions
            return True
        
        # Decay exploration debt
        if user_state['exploration_debt'] > 0:
            user_state['exploration_debt'] -= 1
        
        return False
    
    def _get_exploration_level(self, user_state: Dict, metrics: PerformanceMetrics, current_difficulty: int) -> int:
        """Choose exploration level based on confidence and performance."""
        
        confidence_scores = user_state['confidence_scores']
        
        # Try one level up if doing very well
        if (current_difficulty < 5 and 
            metrics.success_rate >= 0.8 and 
            confidence_scores[current_difficulty] > 0.7):
            return current_difficulty + 1
        
        # Try one level down if confidence is low at current level
        if (current_difficulty > 1 and 
            confidence_scores[current_difficulty-1] < 0.4):
            return current_difficulty - 1
        
        return current_difficulty
    
    def _momentum_based_decision(self, user_state: Dict, metrics: PerformanceMetrics, current_difficulty: int) -> int:
        """Make decisions based on learning momentum."""
        
        momentum = user_state['learning_momentum']
        
        # Strong positive momentum - try harder content
        if momentum > 0.3 and current_difficulty < 5 and metrics.success_rate >= 0.65:
            return min(5, current_difficulty + 1)
        
        # Strong negative momentum - provide easier content
        if momentum < -0.3 and current_difficulty > 1:
            return max(1, current_difficulty - 1)
        
        return current_difficulty
    
    def _stability_based_decision(self, user_state: Dict, metrics: PerformanceMetrics, current_difficulty: int) -> int:
        """Make decisions based on performance stability."""
        
        # If user is stable and successful, promote
        if (metrics.difficulty_stability > 0.7 and 
            metrics.success_rate >= 0.75 and 
            current_difficulty < 5):
            return current_difficulty + 1
        
        # If user is unstable or unsuccessful, demote
        if (metrics.difficulty_stability < 0.3 or 
            metrics.success_rate < 0.4) and current_difficulty > 1:
            return current_difficulty - 1
        
        return current_difficulty
    
    def _update_confidence_scores(self, user_state: Dict, metrics: PerformanceMetrics, difficulty: int):
        """Update confidence scores for all difficulty levels."""
        
        # Update confidence for current difficulty
        if metrics.recent_attempts > 0:
            current_confidence = user_state['confidence_scores'][difficulty-1]
            
            # Weighted update based on recent performance
            new_confidence = (
                current_confidence * (1 - self.recency_weight) + 
                metrics.success_rate * self.recency_weight
            )
            
            user_state['confidence_scores'][difficulty-1] = max(0.0, min(1.0, new_confidence))
        
    def _update_and_return(self, user_state: Dict, new_difficulty: int, reason: str) -> int:
        """Update user state and return new difficulty."""
        
        old_difficulty = user_state['current_difficulty']
        user_state['current_difficulty'] = new_difficulty
        user_state['difficulty_history'].append((new_difficulty, time.time(), reason))
        user_state['last_update'] = time.time()
        
        # Reset counters on difficulty change
        if new_difficulty != old_difficulty:
            user_state['streak_counter'] = 0
            user_state['struggle_counter'] = 0
        
        return new_difficulty
    
    def update_bandit_state_enhanced(self, user_id: int, lesson_id: int, difficulty: int, 
                                   was_correct: bool, response_time: float = None):
        """Enhanced bandit state update with additional metrics."""
        
        # Update database (existing functionality)
        conn = get_db_connection()
        cur = conn.cursor()
        reward = 1 if was_correct else 0

        cur.execute("""
            INSERT INTO bandit_state (user_id, lesson_id, difficulty_level, times_selected, successful_outcomes)
            VALUES (%s, %s, %s, 1, %s) 
            ON CONFLICT (user_id, lesson_id, difficulty_level)
            DO UPDATE SET
                times_selected = bandit_state.times_selected + 1,
                successful_outcomes = bandit_state.successful_outcomes + %s
        """, (user_id, lesson_id, difficulty, reward, reward))

        conn.commit()
        cur.close()
        conn.close()
        
        # Update in-memory user state for immediate response
        user_state = self._get_user_state(user_id, lesson_id)
        
        # Update counters
        if was_correct:
            user_state['streak_counter'] = user_state['streak_counter'] + 1
            user_state['struggle_counter'] = 0
            # Boost confidence
            current_conf = user_state['confidence_scores'][difficulty-1]
            user_state['confidence_scores'][difficulty-1] = min(1.0, current_conf * self.confidence_boost)
        else:
            user_state['struggle_counter'] = user_state['struggle_counter'] + 1
            user_state['streak_counter'] = 0
            # Decay confidence
            current_conf = user_state['confidence_scores'][difficulty-1]
            user_state['confidence_scores'][difficulty-1] = max(0.0, current_conf * self.confidence_decay)
        
        # Add performance data point
        user_state['recent_performance'].append({
            'correct': was_correct,
            'difficulty': difficulty,
            'timestamp': time.time(),
            'response_time': response_time
        })
        
        logging.info(f"Updated state for user {user_id}: streak={user_state['streak_counter']}, "
                    f"struggle={user_state['struggle_counter']}, confidence={user_state['confidence_scores'][difficulty-1]:.2f}")
    
    def get_user_insights(self, user_id: int, lesson_id: int) -> Dict[str, Any]:
        """Get comprehensive user learning insights."""
        
        user_state = self._get_user_state(user_id, lesson_id)
        metrics = self.get_enhanced_performance_metrics(user_id, lesson_id)
        
        return {
            'current_difficulty': user_state['current_difficulty'],
            'confidence_scores': user_state['confidence_scores'],
            'learning_momentum': user_state['learning_momentum'],
            'streak_counter': user_state['streak_counter'],
            'struggle_counter': user_state['struggle_counter'],
            'success_rate': metrics.success_rate,
            'consecutive_correct': metrics.consecutive_correct,
            'consecutive_wrong': metrics.consecutive_wrong,
            'difficulty_stability': metrics.difficulty_stability,
            'learning_velocity': metrics.learning_velocity,
            'recent_attempts': metrics.recent_attempts,
            'difficulty_history': list(user_state['difficulty_history'])[-5:],  # Last 5 changes
            'recommendation': self._get_learning_recommendation(user_state, metrics)
        }
    
    def _get_learning_recommendation(self, user_state: Dict, metrics: PerformanceMetrics) -> str:
        """Provide learning recommendations based on current state."""
        
        if metrics.consecutive_wrong >= 3:
            return "Take a break and review easier concepts"
        elif metrics.consecutive_correct >= 4:
            return "You're on fire! Ready for more challenging content"
        elif metrics.success_rate < 0.4:
            return "Focus on mastering current level before advancing"
        elif metrics.success_rate > 0.8 and metrics.difficulty_stability > 0.6:
            return "Excellent progress! Time to level up"
        elif user_state['learning_momentum'] > 0.3:
            return "Great improvement trend - keep building on this progress"
        elif user_state['learning_momentum'] < -0.3:
            return "Consider reviewing fundamentals to build stronger foundation"
        else:
            return "Steady progress - maintain current practice routine"


# Global enhanced instance
enhanced_difficulty_selector = EnhancedAdaptiveDifficultySelector()

def select_difficulty_ultra_responsive(user_id: int, lesson_id: int) -> int:
    """Main interface for ultra-responsive difficulty selection."""
    return enhanced_difficulty_selector.select_difficulty_ultra_responsive(user_id, lesson_id)

def update_bandit_state_enhanced(user_id: int, lesson_id: int, difficulty: int, 
                               was_correct: bool, response_time: float = None):
    """Enhanced bandit state update with immediate response capabilities."""
    enhanced_difficulty_selector.update_bandit_state_enhanced(
        user_id, lesson_id, difficulty, was_correct, response_time
    )

def get_user_learning_insights(user_id: int, lesson_id: int) -> Dict[str, Any]:
    """Get comprehensive user learning insights."""
    return enhanced_difficulty_selector.get_user_insights(user_id, lesson_id)