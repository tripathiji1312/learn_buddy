-- This table stores user login info and their experience points (XP).
-- MODIFIED to include an admin flag AND streak-tracking columns.
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    xp INT DEFAULT 0,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- NEW: Columns for tracking daily streaks
    last_login_date DATE,
    streak_count INT DEFAULT 0
);

-- This table stores questions for the lessons.
-- (No changes here)
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL,
    content TEXT NOT NULL,
    difficulty_level INT NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    correct_answer_text VARCHAR(255) NOT NULL
);

-- This table tracks every answer a user gives.
-- (No changes here)
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    question_id INT REFERENCES questions(id) ON DELETE CASCADE,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- This table stores the state of our Reinforcement Learning model.
-- (No changes here)
CREATE TABLE bandit_state (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INT NOT NULL,
    difficulty_level INT NOT NULL,
    times_selected INT DEFAULT 1,
    successful_outcomes INT DEFAULT 0,
    PRIMARY KEY (user_id, lesson_id, difficulty_level)
);

-- NEW TABLE: Stores the definitions for all possible quests.
CREATE TABLE quests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    quest_type VARCHAR(50) NOT NULL, -- e.g., 'CORRECT_ANSWERS', 'TOTAL_ANSWERS'
    completion_target INT NOT NULL, -- e.g., 5 for "Answer 5 questions correctly"
    xp_reward INT NOT NULL
);

-- NEW TABLE: Tracks the active quest for each user for the current day.
CREATE TABLE user_quests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    quest_id INT REFERENCES quests(id) ON DELETE CASCADE,
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    current_progress INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, assigned_date) -- Ensures a user only gets one quest per day
);
-- (Keep all the existing tables: users, questions, user_progress, etc.)

-- NEW TABLE: Stores the definitions for all possible achievements.
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon_class VARCHAR(50) NOT NULL, -- e.g., 'fas fa-brain', 'fas fa-fire'
    criteria_type VARCHAR(50) NOT NULL, -- e.g., 'CORRECT_ANSWERS_TOTAL', 'STREAK'
    criteria_value INT NOT NULL,
    xp_reward INT NOT NULL
);

-- NEW TABLE: Links users to the achievements they have unlocked.
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INT REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id) -- A user can only earn each achievement once
);