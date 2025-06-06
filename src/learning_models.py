import numpy as np
import logging
import random
import re
import os
from sentence_transformers import SentenceTransformer, util
from .adaptive_engine import get_db_connection
import psycopg2.extras

# --- NLP MODEL INITIALIZATION ---
# This section remains the same, loading the model robustly.
def load_similarity_model():
    """Load the similarity model with proper error handling and caching."""
    # Using a direct path is the most reliable offline strategy
    local_model_path = './model_cache/sentence-transformers_all-MiniLM-L6-v2'
    logging.info(f"Attempting to load model from local path: {local_model_path}...")
    
    try:
        if os.path.exists(local_model_path):
            model = SentenceTransformer(local_model_path)
            logging.info("Semantic Similarity model loaded successfully from local files.")
            return model
        else:
            logging.warning(f"Local model path not found: {local_model_path}. Attempting to download.")
            # Fallback to downloading if the local cache isn't present
            model_name = 'all-MiniLM-L6-v2'
            model = SentenceTransformer(model_name)
            logging.info("Model downloaded and loaded successfully.")
            return model
            
    except Exception as e:
        logging.error(f"FATAL: Could not load or download the model: {e}")
        logging.warning("Continuing without AI-powered similarity checking.")
        return None

# Initialize model at startup
similarity_model = load_similarity_model()


# --- CORRECTED HELPER AND MAIN CHECKING FUNCTION ---

def _find_all_numbers(text: str) -> list[str]:
    """
    Finds all numbers in a string and returns them as a list of strings.
    This is more robust than finding only the first one.
    """
    # re.findall returns a list of all non-overlapping matches in the string.
    return re.findall(r'\d+', text)


def check_semantic_similarity(user_answer: str, correct_answer: str) -> tuple[bool, float]:
    """
    Checks if a user's free-text answer is close enough to the correct answer.
    It now correctly uses a numeric matching shortcut before falling back to the AI model.
    """
    # --- Stage 1: Attempt Numeric Shortcut ---
    # First, check if the correct answer is purely a number.
    if correct_answer.isdigit():
        # Get ALL numbers from the user's answer using the corrected helper.
        numbers_in_answer = _find_all_numbers(user_answer)
        # Check if the correct answer exists anywhere in the list of found numbers.
        if correct_answer in numbers_in_answer:
            logging.info(f"Numeric shortcut successful. Found '{correct_answer}' in numbers: {numbers_in_answer}")
            return True, 1.0

    # --- Stage 2: Attempt AI Model Similarity (if numeric shortcut failed) ---
    if similarity_model is not None:
        try:
            logging.info("Using AI model for similarity check.")
            embedding1 = similarity_model.encode(user_answer, convert_to_tensor=True)
            embedding2 = similarity_model.encode(correct_answer, convert_to_tensor=True)
            similarity_score = util.cos_sim(embedding1, embedding2).item()
            is_correct = similarity_score > 0.6
            return is_correct, similarity_score
        except Exception as e:
            logging.error(f"Error during AI similarity check, proceeding to fallback: {e}")
            # If the AI fails for any reason, we don't stop. We fall through to the final basic check.

    # --- Stage 3: Final Fallback (if numeric shortcut failed AND AI failed or is unavailable) ---
    logging.warning("Falling back to basic string comparison.")
    user_answer_clean = user_answer.lower().strip()
    correct_answer_clean = correct_answer.lower().strip()

    if correct_answer_clean in user_answer_clean:
        return True, 0.8  # A high score for a simple "contains" check

    return False, 0.0


# --- REINFORCEMENT LEARNING MODEL ---
# This is your final, approved Epsilon-Greedy logic which works correctly.
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

    if not states:
        logging.info(f"AI: New user/lesson for user {user_id}. Starting at level 1.")
        return 1

    best_difficulty = 1
    max_avg_reward = -1.0
    state_map = {s['difficulty_level']: s for s in states}

    for level in sorted(state_map.keys()):
        state = state_map[level]
        avg_reward = state['successful_outcomes'] / state['times_selected']
        if avg_reward >= max_avg_reward:
            max_avg_reward = avg_reward
            best_difficulty = level

    if max_avg_reward == 0:
        logging.info(f"AI: User {user_id} is struggling. Resetting to level 1 for encouragement.")
        return 1

    if random.random() < EPSILON:
        logging.info(f"AI: User {user_id} is succeeding. Exploring a new level.")
        possible_next_level = best_difficulty + 1
        return min(possible_next_level, 5)
    else:
        logging.info(f"AI: User {user_id} is succeeding. Exploiting best level: {best_difficulty}.")
        return best_difficulty


def update_bandit_state(user_id: int, lesson_id: int, difficulty: int, was_correct: bool):
    """
    Updates the bandit's memory after a user answers a question.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    reward = 1 if was_correct else 0
    cur.execute(
        """
        INSERT INTO bandit_state (user_id, lesson_id, difficulty_level, times_selected, successful_outcomes)
        VALUES (%s, %s, %s, 1, %s) ON CONFLICT (user_id, lesson_id, difficulty_level)
        DO UPDATE SET
            times_selected = bandit_state.times_selected + 1,
            successful_outcomes = bandit_state.successful_outcomes + %s;
        """,
        (user_id, lesson_id, difficulty, reward, reward)
    )
    conn.commit()
    cur.close()
    conn.close()