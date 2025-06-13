import psycopg2
import os
import sys
from urllib.parse import urlparse

# --- NEW: Path Correction ---
# This allows the script to find modules in the 'src' directory (like security.py)
# when run from the project's root directory (e.g., `python scripts/seed_db.py`).
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
    and then inserts fresh sample data, including a default admin user.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection_from_url()
        cur = conn.cursor()
        print("--- Database connection successful ---")

        print("Dropping existing tables...")
        cur.execute("DROP TABLE IF EXISTS bandit_state, user_progress, questions, users CASCADE;")

        print("Creating tables from schema.sql...")
        # Your schema.sql should already have the `is_admin` column added to the users table.
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())

        print("Tables created successfully.")

        print("Inserting sample data...")
        # Insert a regular test user
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s);",
            ('testuser', 'test@example.com', get_password_hash('testpass'))
        )
        
        # --- NEW: Insert a default admin user ---
        print("Creating default admin user...")
        admin_username = "admin"
        admin_email = "admin@learnbuddy.com"
        # IMPORTANT: In a real production environment, use a strong password
        # loaded from a secure source (like an environment variable), not hardcoded.
        admin_password = "adminpassword"
        admin_hashed_password = get_password_hash(admin_password)

        # Insert the admin user with the is_admin flag set to TRUE.
        # ON CONFLICT ensures this doesn't fail if the script is run multiple times.
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (username) DO NOTHING;
            """,
            (admin_username, admin_email, admin_hashed_password)
        )
        print(f"Admin user '{admin_username}' created or already exists.")
        # --- END OF NEW LOGIC ---

        sample_questions = [
            # lesson_id, content, difficulty_level, correct_answer_text
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
        insert_query = "INSERT INTO questions (lesson_id, content, difficulty_level, correct_answer_text) VALUES (%s, %s, %s, %s);"
        cur.executemany(insert_query, sample_questions)

        conn.commit()
        print(f"Seeded 1 regular user, 1 admin user, and {len(sample_questions)} questions.")
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