-- This table stores user login info and their experience points (XP).
-- MODIFIED to include an admin flag.
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    xp INT DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE, -- NEW: Flag for admin users
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- This table stores questions for the lessons.
-- It is MODIFIED to include a text-based answer for our NLP model.
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL,
    content TEXT NOT NULL,
    difficulty_level INT NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    correct_answer_text VARCHAR(255) NOT NULL
);

-- This table tracks every answer a user gives.
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    question_id INT REFERENCES questions(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- NEW TABLE: Stores the state of our Reinforcement Learning model.
-- This is the "memory" for the AI to learn about each user.
CREATE TABLE bandit_state (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INT NOT NULL,
    difficulty_level INT NOT NULL,
    times_selected INT DEFAULT 1,
    successful_outcomes INT DEFAULT 0,
    PRIMARY KEY (user_id, lesson_id, difficulty_level)
);