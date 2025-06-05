-- This table will store user login info and their experience points (XP).
CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- Gives each user a unique, auto-incrementing number.
    username VARCHAR(50) UNIQUE NOT NULL, -- User's name, must be unique.
    email VARCHAR(255) UNIQUE NOT NULL, -- User's email, must be unique.
    password_hash VARCHAR(255) NOT NULL, -- IMPORTANT: We never store raw passwords.
    xp INT DEFAULT 0, -- User's experience points, starts at 0.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- This table will store questions for the lessons.
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL, -- Which lesson this question belongs to.
    content TEXT NOT NULL, -- The text of the question (e.g., "What is 2+2?").
    difficulty_level INT NOT NULL -- A number, e.g., 1=easy, 5=hard.
);

-- This table is CRITICAL. It tracks every answer a user gives.
-- This data will power your AI engine later.
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    -- 'FOREIGN KEY' creates a link to the 'users' table.
    -- If a user is deleted, their progress can be handled automatically.
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    -- This links to the specific question that was answered.
    question_id INT REFERENCES questions(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL, -- Did the user get it right? (True/False)
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);