import numpy as np
import logging
import random
import re
import os
from sentence_transformers import SentenceTransformer, util
from .adaptive_engine import get_db_connection
import psycopg2.extras


# --- NLP MODEL INITIALIZATION WITH ERROR HANDLING ---
def load_similarity_model():
    """Load the similarity model with proper error handling and caching."""
    model_name = 'all-MiniLM-L6-v2'
    cache_dir = os.environ.get('TRANSFORMERS_CACHE', './model_cache')

    try:
        logging.info("Loading Semantic Similarity model...")

        # Try to load with local cache first
        model = SentenceTransformer(model_name, cache_folder=cache_dir)
        logging.info("Semantic Similarity model loaded successfully.")
        return model

    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {str(e)}")

        # Fallback: Try a different approach or use a backup model
        try:
            logging.info("Attempting to load model with offline mode...")
            model = SentenceTransformer(model_name, cache_folder=cache_dir, use_auth_token=False)
            return model
        except Exception as e2:
            logging.error(f"Fallback loading also failed: {str(e2)}")

            # Final fallback: Return None and handle gracefully
            logging.warning("Using fallback similarity checking without transformer model")
            return None


# Initialize model
similarity_model = load_similarity_model()


def _extract_number(text: str) -> str:
    """Finds the first number in a string."""
    match = re.search(r'\d+', text)
    if match:
        return match.group(0)
    return None


def check_semantic_similarity(user_answer: str, correct_answer: str) -> tuple[bool, float]:
    """
    Checks if a user's free-text answer is close enough to the correct answer.
    It now correctly uses a numeric matching shortcut before falling back to the AI model.
    """
    # --- Stage 1: Attempt Numeric Shortcut ---
    # First, check if the correct answer is purely a number.
    if correct_answer.isdigit():
        extracted_number = _extract_number(user_answer)
        # If we found a number and it's a perfect match, we are done. Return immediately.
        if extracted_number and extracted_number == correct_answer:
            logging.info("Numeric shortcut successful.")
            return True, 1.0

    # --- Stage 2: Attempt AI Model Similarity (if numeric shortcut failed) ---
    if similarity_model is not None:
        try:
            logging.info("Using AI model for similarity check.")
            embedding1 = similarity_model.encode(user_answer, convert_to_tensor=True)
            embedding2 = similarity_model.encode(correct_answer, convert_to_tensor=True)
            similarity_score = util.cos_sim(embedding1, embedding2).item()
            is_correct = similarity_score > 0.6
            return is_correct, similarity_score # Return the AI's result immediately.
        except Exception as e:
            logging.error(f"Error during AI similarity check, proceeding to fallback: {e}")
            # If the AI fails for any reason, we don't stop. We fall through to the final basic check.

    # --- Stage 3: Final Fallback (if numeric shortcut failed AND AI failed or is unavailable) ---
    logging.warning("Falling back to basic string comparison.")
    user_answer_clean = user_answer.lower().strip()
    correct_answer_clean = correct_answer.lower().strip()

    if correct_answer_clean in user_answer_clean:
        return True, 0.8  # A high score for a simple "contains" check

    return False, 0.0 # If all checks fail, it's incorrect.

def select_difficulty_epsilon_greedy(user_id: int, lesson_id: int) -> int:
    """
    Selects the best difficulty using an improved Epsilon-Greedy strategy.
    It handles failure more gracefully and encourages exploration after success.
    """
    EPSILON = 0.2  # 20% chance to explore randomly

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT difficulty_level, times_selected, successful_outcomes FROM bandit_state WHERE user_id = %s AND lesson_id = %s;",
        (user_id, lesson_id)
    )
    states = cur.fetchall()
    cur.close()
    conn.close()

    # If the user has no history for this lesson, always start at level 1.
    if not states:
        logging.info(f"AI: New user/lesson for user {user_id}. Starting at level 1.")
        return 1

    # --- The "Greedy" Part: Find the best-performing level ---
    best_difficulty = 1
    max_avg_reward = -1.0

    state_map = {s['difficulty_level']: s for s in states}
    for level in sorted(state_map.keys()):  # Check in order from easiest to hardest
        state = state_map[level]
        avg_reward = state['successful_outcomes'] / state['times_selected']
        if avg_reward >= max_avg_reward:  # Use >= to prefer higher difficulties with same score
            max_avg_reward = avg_reward
            best_difficulty = level

    # --- The "Epsilon" or "Smart Exploration" Part ---

    # Case 1: The user is struggling (best success rate is 0%).
    if max_avg_reward == 0:
        logging.info(f"AI: User {user_id} is struggling. Resetting to level 1 for encouragement.")
        return 1  # Always drop back to the easiest level to rebuild confidence.

    # Case 2: The user is doing well. Let's decide whether to explore or exploit.
    if random.random() < EPSILON:
        logging.info(f"AI: User {user_id} is succeeding. Exploring a new level.")
        # Let's be smart about exploring. Try a level that is one harder.
        possible_next_level = best_difficulty + 1
        if possible_next_level > 5:  # Don't go past the max difficulty
            possible_next_level = 5
        return possible_next_level
    else:
        # Exploit: Stick with the level that's working best.
        logging.info(f"AI: User {user_id} is succeeding. Exploiting best level: {best_difficulty}.")
        return best_difficulty


def update_bandit_state(user_id: int, lesson_id: int, difficulty: int, was_correct: bool):
    """
    Updates the bandit's memory after a user answers a question.
    This function remains the same as it correctly supports any learning model.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    reward = 1 if was_correct else 0

    cur.execute(
        """
        INSERT INTO bandit_state (user_id, lesson_id, difficulty_level, times_selected, successful_outcomes)
        VALUES (%s, %s, %s, 1, %s) ON CONFLICT (user_id, lesson_id, difficulty_level)
        DO
        UPDATE SET
            times_selected = bandit_state.times_selected + 1,
            successful_outcomes = bandit_state.successful_outcomes + %s;
        """,
        (user_id, lesson_id, difficulty, reward, reward)
    )

    conn.commit()
    cur.close()
    conn.close()