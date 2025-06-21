import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
import psycopg2.extras
from datetime import timedelta, date, datetime
import random
from jose import jwt, JWTError
from typing import List, Optional
import os
from fastapi.responses import JSONResponse

# --- Import our custom modules ---
# MODIFIED: Import the new, advanced functions
from .learning_models import (
    select_difficulty_ultra_responsive,
    update_bandit_state_enhanced
)
from .adaptive_engine import get_db_connection, select_question
from . import security
from .db_models import User

# MODIFIED: Add SentenceTransformer imports directly, as it's no longer in learning_models.py
from sentence_transformers import SentenceTransformer, util

# --- Basic App Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(title="LearnBuddy AI Engine", version="1.0.0")

origins = [ "http://localhost", "http://localhost:5500", "http://127.0.0.1:5500" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
similarity_model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    cache_folder=os.environ.get('TRANSFORMERS_CACHE', './model_cache')
)

# --- Pydantic Models for API Data (Unchanged) ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserInDB(User):
    is_admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class NextQuestionRequest(BaseModel):
    lesson_id: int

class AnswerSubmission(BaseModel):
    lesson_id: int
    question_id: int
    difficulty_answered: int
    user_answer: str

class QuestResponse(BaseModel):
    title: str
    description: str
    current_progress: int
    completion_target: int
    xp_reward: int
    is_completed: bool

class UserStatsResponse(BaseModel):
    xp: int
    streak_count: int
    last_login_date: datetime

class AchievementResponse(BaseModel):
    name: str
    description: str
    icon_class: str
    unlocked_at: datetime
    
# Admin Models (Unchanged)
class UserAdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    xp: int = 0
    is_admin: bool = False

class UserAdminUpdate(BaseModel):
    username: str
    email: EmailStr
    xp: int
    is_admin: bool
    password: Optional[str] = Field(None, min_length=8)

class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    xp: int
    is_admin: bool

class QuestionAdmin(BaseModel):
    id: int
    lesson_id: int
    question_text: str
    difficulty_level: int

class QuestionCreateUpdate(BaseModel):
    lesson_id: int
    question_text: str
    difficulty_level: int
    correct_answer_text: str

class AdminStats(BaseModel):
    total_users: int
    total_questions: int
    total_answers_submitted: int
    questions_by_difficulty: dict

# --- Load Similarity Model on Startup ---
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')


# --- Achievement Helper Function (Unchanged) ---
def check_and_award_achievements(user_id: int, conn, cur):
    cur.execute("SELECT id, name, criteria_type, criteria_value, xp_reward FROM achievements WHERE id NOT IN (SELECT achievement_id FROM user_achievements WHERE user_id = %s)", (user_id,))
    unearned_achievements = cur.fetchall()
    if not unearned_achievements: return
    cur.execute("SELECT streak_count FROM users WHERE id = %s", (user_id,))
    user_stats = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM user_progress WHERE user_id = %s", (user_id,))
    total_answers = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) FROM user_progress WHERE user_id = %s AND is_correct = TRUE", (user_id,))
    total_correct_answers = cur.fetchone()['count']
    xp_to_add = 0
    for achievement in unearned_achievements:
        unlocked = False
        if achievement['criteria_type'] == 'STREAK' and user_stats['streak_count'] >= achievement['criteria_value']: unlocked = True
        elif achievement['criteria_type'] == 'ANSWERS_TOTAL' and total_answers >= achievement['criteria_value']: unlocked = True
        elif achievement['criteria_type'] == 'CORRECT_ANSWERS_TOTAL' and total_correct_answers >= achievement['criteria_value']: unlocked = True
        if unlocked:
            cur.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (%s, %s)", (user_id, achievement['id']))
            xp_to_add += achievement['xp_reward']
            logging.info(f"User {user_id} unlocked achievement '{achievement['name']}'!")
    if xp_to_add > 0: cur.execute("UPDATE users SET xp = xp + %s WHERE id = %s", (xp_to_add, user_id))


# --- Security & Dependencies (Unchanged) ---
def get_current_user(token: str = Depends(security.oauth2_scheme)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError: raise credentials_exception
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, username, email, xp, is_admin FROM users WHERE username = %s", (username,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data is None: raise credentials_exception
    return UserInDB.model_validate(dict(user_data))

def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return current_user


# --- Learner Endpoints ---
@app.post("/signup", summary="Create a new user", status_code=status.HTTP_201_CREATED)
def create_user_learner(user: UserCreate):
    # This function is unchanged
    hashed_password = security.get_password_hash(user.password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id;", (user.username, user.email, hashed_password))
        new_user_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    finally:
        cur.close()
        conn.close()
    return {"id": new_user_id, "username": user.username, "email": user.email}

@app.post("/token", response_model=Token, summary="User login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # This function is unchanged
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    if not user or not security.verify_password(form_data.password, user['password_hash']):
        cur.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    today = date.today()
    last_login = user['last_login_date']
    new_streak = user['streak_count']
    if last_login is None: new_streak = 1
    elif last_login < today:
        if last_login == today - timedelta(days=1): new_streak += 1
        else: new_streak = 1
    cur.execute("UPDATE users SET streak_count = %s, last_login_date = %s WHERE id = %s", (new_streak, today, user['id']))
    check_and_award_achievements(user['id'], conn, cur)
    conn.commit()
    cur.close()
    conn.close()
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/next_question", summary="Get the next AI-selected question (Protected)", tags=["Learner"])
def get_next_question(req: NextQuestionRequest, current_user: User = Depends(get_current_user)):
    # The AI decides the IDEAL difficulty
    optimal_difficulty = select_difficulty_ultra_responsive(current_user.id, req.lesson_id)
    
    # Unpack the THREE values from the new select_question function
    question_id, question_text, actual_difficulty = select_question(optimal_difficulty, req.lesson_id)
    
    if question_id is None:
        raise HTTPException(status_code=404, detail="No questions found for this lesson.")
        
    # Return the ACTUAL difficulty of the question served
    return {"difficulty_level": actual_difficulty, "question_id": question_id, "question_text": question_text}

@app.post("/submit_answer", summary="Submit an answer (Protected)", tags=["Learner"])
def submit_answer(submission: AnswerSubmission, current_user: User = Depends(get_current_user)):
    # MODIFIED: Logic updated to use new functions
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT correct_answer_text FROM questions WHERE id = %s;", (submission.question_id,))
        result = cur.fetchone()
        if not result: raise HTTPException(status_code=404, detail="Question ID not found.")
        
        correct_answer = result['correct_answer_text']
        
        # Perform similarity check directly in the endpoint
        embedding1 = similarity_model.encode(submission.user_answer.lower().strip(), convert_to_tensor=True)
        embedding2 = similarity_model.encode(correct_answer.lower().strip(), convert_to_tensor=True)
        similarity_score = util.cos_sim(embedding1, embedding2).item()
        is_correct = similarity_score > 0.8
        
        # Call the new, enhanced update function
        update_bandit_state_enhanced(
            user_id=current_user.id, 
            lesson_id=submission.lesson_id, 
            difficulty=submission.difficulty_answered, 
            was_correct=is_correct
        )
        
        cur.execute("INSERT INTO user_progress (user_id, question_id, is_correct) VALUES (%s, %s, %s);", (current_user.id, submission.question_id, is_correct))
        
        xp_gain = 10 if is_correct else 0
        quest_completed_this_turn = False
        
        cur.execute("SELECT uq.id, uq.current_progress, q.quest_type, q.completion_target, q.xp_reward FROM user_quests uq JOIN quests q ON uq.quest_id = q.id WHERE uq.user_id = %s AND uq.assigned_date = CURRENT_DATE AND uq.is_completed = FALSE;", (current_user.id,))
        active_quest = cur.fetchone()
        if active_quest:
            quest_progress_updated = (active_quest['quest_type'] == 'TOTAL_ANSWERS') or (active_quest['quest_type'] == 'CORRECT_ANSWERS' and is_correct)
            if quest_progress_updated:
                new_progress = active_quest['current_progress'] + 1
                cur.execute("UPDATE user_quests SET current_progress = %s WHERE id = %s", (new_progress, active_quest['id']))
                if new_progress >= active_quest['completion_target']:
                    cur.execute("UPDATE user_quests SET is_completed = TRUE WHERE id = %s", (active_quest['id'],))
                    xp_gain += active_quest['xp_reward']
                    quest_completed_this_turn = True
        
        if xp_gain > 0: cur.execute("UPDATE users SET xp = xp + %s WHERE id = %s;", (xp_gain, current_user.id))
        
        check_and_award_achievements(current_user.id, conn, cur)
        conn.commit()

        return {"status": "Answer processed", "is_correct": is_correct, "similarity_score": round(similarity_score, 2), "quest_completed": quest_completed_this_turn}
    finally:
        cur.close()
        conn.close()

@app.get("/users/me/stats", response_model=UserStatsResponse, summary="Get current user's stats (Protected)", tags=["Learner"])
def get_user_stats(current_user: User = Depends(get_current_user)):
    # This function is unchanged
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT xp, streak_count, last_login_date FROM users WHERE id = %s", (current_user.id,))
    stats = cur.fetchone()
    cur.close()
    conn.close()
    if not stats: raise HTTPException(status_code=404, detail="User not found.")
    return UserStatsResponse(xp=stats['xp'], streak_count=stats['streak_count'], last_login_date=stats['last_login_date'])

@app.get("/quests/today", response_model=QuestResponse, summary="Get today's quest (Protected)", tags=["Learner"])
def get_daily_quest(current_user: User = Depends(get_current_user)):
    # This function is unchanged
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT q.title, q.description, uq.current_progress, q.completion_target, q.xp_reward, uq.is_completed FROM user_quests uq JOIN quests q ON uq.quest_id = q.id WHERE uq.user_id = %s AND uq.assigned_date = CURRENT_DATE;", (current_user.id,))
    quest_data = cur.fetchone()
    if not quest_data:
        cur.execute("SELECT id FROM quests WHERE quest_type != 'TIME_BASED' ORDER BY RANDOM() LIMIT 1")
        random_quest = cur.fetchone()
        if not random_quest:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="No available quests to assign.")
        cur.execute("INSERT INTO user_quests (user_id, quest_id) VALUES (%s, %s) RETURNING id;", (current_user.id, random_quest['id']))
        conn.commit()
        cur.execute("SELECT q.title, q.description, uq.current_progress, q.completion_target, q.xp_reward, uq.is_completed FROM user_quests uq JOIN quests q ON uq.quest_id = q.id WHERE uq.user_id = %s AND uq.assigned_date = CURRENT_DATE;", (current_user.id,))
        quest_data = cur.fetchone()
    cur.close()
    conn.close()
    return QuestResponse(**quest_data)

@app.get("/achievements", response_model=List[AchievementResponse], summary="Get user's unlocked achievements", tags=["Learner"])
def get_user_achievements(current_user: User = Depends(get_current_user)):
    # This function is unchanged
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT a.name, a.description, a.icon_class, ua.unlocked_at FROM user_achievements ua JOIN achievements a ON ua.achievement_id = a.id WHERE ua.user_id = %s ORDER BY ua.unlocked_at DESC;", (current_user.id,))
    achievements = cur.fetchall()
    cur.close()
    conn.close()
    return [AchievementResponse(**ach) for ach in achievements]


# ===================================================================
# ===================== ADMIN PANEL ENDPOINTS =======================
# ===================================================================

@app.post("/admin/token", response_model=Token, summary="Admin user login", tags=["Admin"])
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not user['is_admin'] or not security.verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password, or not an admin.")
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/stats", response_model=AdminStats, summary="Get dashboard statistics", tags=["Admin"])
def get_admin_stats(admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT count(*) FROM users;")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM questions;")
    total_questions = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM user_progress;")
    total_answers = cur.fetchone()[0]
    cur.execute("SELECT difficulty_level, count(*) FROM questions GROUP BY difficulty_level;")
    difficulty_counts = {str(row['difficulty_level']): row['count'] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return {"total_users": total_users, "total_questions": total_questions, "total_answers_submitted": total_answers, "questions_by_difficulty": difficulty_counts}

@app.get("/admin/users", response_model=List[UserAdminResponse], summary="Get all users", tags=["Admin"])
def get_all_users(admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, username, email, xp, is_admin FROM users ORDER BY id ASC;")
    users = [UserAdminResponse.model_validate(dict(row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return users

@app.get("/admin/users/{user_id}", response_model=UserAdminResponse, summary="Get a single user by ID", tags=["Admin"])
def get_user_by_id(user_id: int, admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, username, email, xp, is_admin FROM users WHERE id = %s;", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user: raise HTTPException(status_code=404, detail="User not found.")
    return UserAdminResponse.model_validate(dict(user))

@app.post("/admin/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user as Admin", tags=["Admin"])
def create_user_admin(user: UserAdminCreate, admin: UserInDB = Depends(get_current_admin_user)):
    hashed_password = security.get_password_hash(user.password)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("INSERT INTO users (username, email, password_hash, xp, is_admin) VALUES (%s, %s, %s, %s, %s) RETURNING id;", (user.username, user.email, hashed_password, user.xp, user.is_admin))
        new_user_id = cur.fetchone()['id']
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username or email already in use.")
    finally:
        cur.close()
        conn.close()
    return UserAdminResponse(id=new_user_id, **user.model_dump())

@app.put("/admin/users/{user_id}", response_model=UserAdminResponse, summary="Update a user as Admin", tags=["Admin"])
def update_user_admin(user_id: int, user_update: UserAdminUpdate, admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if user_update.password:
        hashed_password = security.get_password_hash(user_update.password)
        cur.execute("UPDATE users SET username=%s, email=%s, xp=%s, is_admin=%s, password_hash=%s WHERE id=%s RETURNING id;", (user_update.username, user_update.email, user_update.xp, user_update.is_admin, hashed_password, user_id))
    else:
        cur.execute("UPDATE users SET username=%s, email=%s, xp=%s, is_admin=%s WHERE id=%s RETURNING id;", (user_update.username, user_update.email, user_update.xp, user_update.is_admin, user_id))
    
    updated_user = cur.fetchone()
    if updated_user is None: raise HTTPException(status_code=404, detail="User not found.")
    conn.commit()
    cur.close()
    conn.close()
    return UserAdminResponse(id=user_id, **user_update.model_dump())

@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user", tags=["Admin"])
def delete_user(user_id: int, admin: UserInDB = Depends(get_current_admin_user)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account.")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    if cur.fetchone() is None: raise HTTPException(status_code=404, detail="User not found.")
    conn.commit()
    cur.close()
    conn.close()
    return

@app.get("/admin/questions", response_model=List[QuestionAdmin], summary="Get all questions", tags=["Admin"])
def get_all_questions(admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, lesson_id, content as question_text, difficulty_level FROM questions ORDER BY id DESC;")
    questions = [QuestionAdmin.model_validate(dict(row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return questions

@app.post("/admin/questions", response_model=QuestionAdmin, status_code=status.HTTP_201_CREATED, summary="Create a new question", tags=["Admin"])
def create_question(question: QuestionCreateUpdate, admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO questions (lesson_id, content, difficulty_level, correct_answer_text) VALUES (%s, %s, %s, %s) RETURNING id;", (question.lesson_id, question.question_text, question.difficulty_level, question.correct_answer_text))
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return {**question.model_dump(exclude={"correct_answer_text"}), "id": new_id, "question_text": question.question_text}

@app.put("/admin/questions/{question_id}", response_model=QuestionAdmin, summary="Update a question", tags=["Admin"])
def update_question(question_id: int, question: QuestionCreateUpdate, admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("UPDATE questions SET lesson_id=%s, content=%s, difficulty_level=%s, correct_answer_text=%s WHERE id=%s RETURNING id;", (question.lesson_id, question.question_text, question.difficulty_level, question.correct_answer_text, question_id))
    if cur.fetchone() is None: raise HTTPException(status_code=404, detail="Question not found.")
    conn.commit()
    cur.close()
    conn.close()
    return {**question.model_dump(exclude={"correct_answer_text"}), "id": question_id, "question_text": question.question_text}

@app.delete("/admin/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a question", tags=["Admin"])
def delete_question(question_id: int, admin: UserInDB = Depends(get_current_admin_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id = %s RETURNING id;", (question_id,))
    if cur.fetchone() is None: raise HTTPException(status_code=404, detail="Question not found.")
    conn.commit()
    cur.close()
    conn.close()
    return

@app.get("/users/me", summary="Get current user's profile info", tags=["Learner"])
def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    return JSONResponse(content={
        "username": current_user.username,
        "email": current_user.email
    })