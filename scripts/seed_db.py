import psycopg2
import os
from urllib.parse import urlparse  # Import the URL parser


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
        database=result.path[1:],  # The path has a leading '/', we strip it
        user=result.username,
        password=result.password
    )
    return conn


def seed_database():
    """
    Wipes the database, runs the schema.sql file to create tables,
    and then inserts fresh sample data.
    """
    try:
        # UPDATED: This now reads the single DATABASE_URL from the environment,
        # which correctly identifies the database host as 'db'.
        conn = get_db_connection_from_url()
        cur = conn.cursor()
        print("--- Database connection successful ---")

        # The rest of the logic remains exactly the same...
        print("Dropping existing tables...")
        cur.execute("DROP TABLE IF EXISTS bandit_state, user_progress, questions, users CASCADE;")

        print("Creating tables from schema.sql...")
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())

        print("Tables created successfully.")

        print("Inserting sample data...")
        cur.execute(
            "INSERT INTO users (id, username, email, password_hash) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
            (1, 'testuser', 'test@example.com', 'some_secure_hash')
        )

        sample_questions = [
            # lesson_id, content, difficulty_level, correct_answer_text
            # --- Difficulty 1 ---
            (1, 'What is two plus two?', 1, '4'),
            (1, 'What is five plus seven?', 1, '12'),
            (1, 'What is ten minus the number three?', 1, '7'),

            # --- Difficulty 2 ---
            (1, 'What is eight multiplied by two?', 2, '16'),
            (1, 'What is twelve times three?', 2, '36'),
            (1, 'What is fifteen divided by five?', 2, '3'),

            # --- Difficulty 3 ---
            (1, 'What is one hundred divided by four?', 3, '25'),
            (1, 'What is the square root of eighty one?', 3, '9'),
            (1, 'What is 7 squared?', 3, '49'),

            # --- Difficulty 4 (NEW CONTENT) ---
            (1, 'If a train travels at 100 km/h, how long does it take to travel 250 km?', 4, '2.5 hours'),
            (1, 'What is 3 to the power of 4?', 4, '81'),
            (1, 'Solve for x: 4x + 7 = 35', 4, '7'),

            # --- Difficulty 5 (NEW CONTENT) ---
            (1, 'What is the area of a circle with a radius of 10 units?', 5, '314.16'),
            (1, 'If a box has a volume of 125 cubic meters, what is the length of one side?', 5, '5 meters')
        ]
        insert_query = "INSERT INTO questions (lesson_id, content, difficulty_level, correct_answer_text) VALUES (%s, %s, %s, %s);"
        cur.executemany(insert_query, sample_questions)

        conn.commit()
        print(f"Seeded 1 user and {len(sample_questions)} questions.")
        print("--- Database Seed Successful ---")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    seed_database()