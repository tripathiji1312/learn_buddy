import psycopg2
import psycopg2.extras  # Needed for dictionary cursors
import os
import random
from urllib.parse import urlparse # Import the URL parser

def get_db_connection():
    """
    Creates and returns a new database connection.
    UPDATED: It now intelligently reads the DATABASE_URL from the environment,
    which is provided by docker-compose.
    """
    db_url_str = os.getenv("DATABASE_URL")
    if not db_url_str:
        raise ValueError("DATABASE_URL environment variable is not set!")

    result = urlparse(db_url_str)
    conn = psycopg2.connect(
        host=result.hostname,
        database=result.path[1:], # The path has a leading '/', we strip it
        user=result.username,
        password=result.password
    )
    return conn


def select_question(difficulty: int, lesson_id: int):
    """
    Selects a random question from the database for a given difficulty and lesson.
    Returns a tuple of (question_id, question_content).
    """
    conn = get_db_connection()
    # A DictCursor returns rows as dictionaries, which is cleaner to work with.
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        "SELECT id, content FROM questions WHERE difficulty_level = %s AND lesson_id = %s;",
        (difficulty, lesson_id)
    )
    questions = cur.fetchall()
    cur.close()
    conn.close()

    if not questions:
        return None, None

    selected_question = random.choice(questions)
    return selected_question['id'], selected_question['content']