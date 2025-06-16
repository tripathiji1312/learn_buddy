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
    Selects a random question from the database.
    FIXED: Uses a single query with a smart fallback and always returns three values.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute(
        """
        SELECT id, content, difficulty_level 
        FROM questions 
        WHERE lesson_id = %s AND difficulty_level <= %s
        ORDER BY difficulty_level DESC, RANDOM()
        LIMIT 1;
        """,
        (lesson_id, difficulty)
    )
    question = cur.fetchone()
    cur.close()
    conn.close()
    
    if question:
        return question['id'], question['content'], question['difficulty_level']
    else:
        # Always return three values, even on failure
        return None, None, None