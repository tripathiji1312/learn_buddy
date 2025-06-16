import psycopg2
import os
import sys
from urllib.parse import urlparse

# --- Path Correction ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.security import get_password_hash


def get_db_connection_from_url():
    """
    Connects to the database using the DATABASE_URL environment variable.
    """
    db_url_str = os.getenv("DATABASE_URL")
    if not db_url_str:
        raise ValueError("DATABASE_URL environment variable is not set!")

    result = urlparse(db_url_str)
    conn = psycopg2.connect(
        host=result.hostname,
        database=result.path[1:],
        user=result.username,
        password=result.password
    )
    return conn


def seed_database():
    """
    Wipes the database, runs the schema.sql file to create tables,
    and then inserts fresh sample data.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection_from_url()
        cur = conn.cursor()
        print("--- Database connection successful ---")

        print("Dropping existing tables...")
        # MODIFIED: Add new tables to the drop list
        cur.execute("DROP TABLE IF EXISTS user_quests, quests, bandit_state, user_progress, questions, users CASCADE;")

        print("Creating tables from schema.sql...")
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())

        print("Tables created successfully.")

        print("Inserting sample data...")
        # Insert users (unchanged)
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s);",
            ('testuser', 'test@example.com', get_password_hash('testpass'))
        )
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, TRUE) ON CONFLICT (username) DO NOTHING;
            """,
            ("admin", "admin@learnbuddy.com", get_password_hash("adminpassword"))
        )

        # Insert questions (unchanged)
        sample_questions = [
            (1, 'What is two plus two?', 1, '4'),
            (1, 'What is five plus seven?', 1, '12'),
            (1, 'What is ten minus the number three?', 1, '7'),
            (1, 'What is eight multiplied by two?', 2, '16'),
            (1, 'What is twelve times three?', 2, '36'),
            (1, 'What is fifteen divided by five?', 2, '3'),
            (1, 'What is one hundred divided by four?', 3, '25'),
            (1, 'What is the square root of eighty one?', 3, '9'),
            (1, 'What is 7 squared?', 3, '49'),
            (1, 'If a train travels at 100 km/h, how long does it take to travel 250 km?', 4, '2.5 hours'),
            (1, 'What is 3 to the power of 4?', 4, '81'),
            (1, 'Solve for x: 4x + 7 = 35', 4, '7'),
            (1, 'What is the area of a circle with a radius of 10 units?', 5, '314.16'),
            (1, 'If a box has a volume of 125 cubic meters, what is the length of one side?', 5, '5 meters')
        ]
        insert_query_q = "INSERT INTO questions (lesson_id, content, difficulty_level, correct_answer_text) VALUES (%s, %s, %s, %s);"
        cur.executemany(insert_query_q, sample_questions)

        # --- NEW: Insert sample quests ---
        print("Inserting sample quests...")
        sample_quests = [
            # title, description, quest_type, completion_target, xp_reward
            ('First Steps', 'Answer 3 questions to complete your first quest!', 'TOTAL_ANSWERS', 3, 25),
            ('Sharp Shooter', 'Get 5 answers correct.', 'CORRECT_ANSWERS', 5, 50),
            ('Quick Learner', 'Complete a quest in under 5 minutes.', 'TIME_BASED', 300, 75)
        ]
        insert_query_quests = "INSERT INTO quests (title, description, quest_type, completion_target, xp_reward) VALUES (%s, %s, %s, %s, %s);"
        cur.executemany(insert_query_quests, sample_quests)
        print(f"Seeded {len(sample_quests)} quests.")
        # --- END OF NEW LOGIC ---

        conn.commit()
        print(f"Seeded users, {len(sample_questions)} questions, and quests.")
        print("--- Database Seed Successful ---")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    seed_database()