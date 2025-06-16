import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
import psycopg2.extras
from datetime import timedelta, date # MODIFIED: Add 'date'
import random # NEW: Add 'random'
from jose import jwt, JWTError
from typing import List, Optional

# --- Import our custom modules ---
from .learning_models import (
    select_difficulty_epsilon_greedy,
    update_bandit_state,
    check_semantic_similarity
)
from .adaptive_engine import get_db_connection, select_question
from . import security
from .db_models import User

# --- Basic App Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(title="LearnBuddy AI Engine", version="1.0.0")

origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Data ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserInDB(User):
    is_admin: bool = False

# Token Model (No Changes Here)
class Token(BaseModel):
    access_token: str
    token_type: str

# Learning Models (No Changes Here)
class NextQuestionRequest(BaseModel):
    lesson_id: int

class AnswerSubmission(BaseModel):
    lesson_id: int
    question_id: int
    difficulty_answered: int
    user_answer: str

# --- NEW: Gamification Models ---
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

# --- NEW Admin Panel User Management Models ---
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
    password: Optional[str] = Field(None, min_length=8) # Optional: only update if provided

class UserAdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    xp: int
    is_admin: bool

# Admin Panel Question Models
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


# --- Security & Dependencies (No Changes) ---
def get_current_user(token: str = Depends(security.oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, username, email, xp, is_admin FROM users WHERE username = %s", (username,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if user_data is None:
        raise credentials_exception

    user = UserInDB.model_validate(dict(user_data))
    return user

def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return current_user

# --- Learner Endpoints (No Changes) ---
@app.post("/signup", summary="Create a new user", status_code=status.HTTP_201_CREATED)
def create_user_learner(user: UserCreate):
    # ... (code is unchanged)
    hashed_password = security.get_password_hash(user.password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
            (user.username, user.email, hashed_password)
        )
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
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not security.verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/next_question", summary="Get the next AI-selected question (Protected)")
def get_next_question(req: NextQuestionRequest, current_user: User = Depends(get_current_user)):
    # ... (code is unchanged)
    logging.info(f"Request for next question for user {current_user.id}, lesson {req.lesson_id}")
    optimal_difficulty = select_difficulty_epsilon_greedy(current_user.id, req.lesson_id)
    question_id, question_text = select_question(optimal_difficulty, req.lesson_id)
    if question_id is None:
        raise HTTPException(status_code=404, detail="No questions found for this difficulty.")
    return {"difficulty_level": optimal_difficulty, "question_id": question_id, "question_text": question_text}


@app.post("/submit_answer", summary="Submit an answer (Protected)")
def submit_answer(submission: AnswerSubmission, current_user: User = Depends(get_current_user)):
    # ... (code is unchanged)
    logging.info(f"Answer submission from user {current_user.id} for question {submission.question_id}")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("SELECT correct_answer_text FROM questions WHERE id = %s;", (submission.question_id,))
        result = cur.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Question ID not found.")
        correct_answer = result['correct_answer_text']
        is_correct, score = check_semantic_similarity(submission.user_answer, correct_answer)
        update_bandit_state(current_user.id, submission.lesson_id, submission.difficulty_answered, is_correct)
        cur.execute(
            "INSERT INTO user_progress (user_id, question_id, is_correct) VALUES (%s, %s, %s);",
            (current_user.id, submission.question_id, is_correct)
        )
        if is_correct:
            cur.execute("UPDATE users SET xp = xp + 10 WHERE id = %s;", (current_user.id,))
        conn.commit()
        return {"status": "Answer processed", "is_correct": is_correct, "similarity_score": round(score, 2)}
    finally:
        cur.close()
        conn.close()

# ===================================================================
# ===================== ADMIN PANEL ENDPOINTS =======================
# ===================================================================

@app.post("/admin/token", response_model=Token, summary="Admin user login", tags=["Admin"])
def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not user['is_admin'] or not security.verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, or not an admin.",
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/stats", response_model=AdminStats, summary="Get dashboard statistics", tags=["Admin"])
def get_admin_stats(admin: UserInDB = Depends(get_current_admin_user)):
    # ... (code is unchanged)
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

# --- UPDATED & NEW USER MANAGEMENT ENDPOINTS ---

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
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserAdminResponse.model_validate(dict(user))

@app.post("/admin/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user as Admin", tags=["Admin"])
def create_user_admin(user: UserAdminCreate, admin: UserInDB = Depends(get_current_admin_user)):
    hashed_password = security.get_password_hash(user.password)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, xp, is_admin) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (user.username, user.email, hashed_password, user.xp, user.is_admin)
        )
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
        # If a new password is provided, hash it and update it
        hashed_password = security.get_password_hash(user_update.password)
        cur.execute(
            """
            UPDATE users SET username=%s, email=%s, xp=%s, is_admin=%s, password_hash=%s
            WHERE id=%s RETURNING id;
            """,
            (user_update.username, user_update.email, user_update.xp, user_update.is_admin, hashed_password, user_id)
        )
    else:
        # If no password is provided, update everything else
        cur.execute(
            "UPDATE users SET username=%s, email=%s, xp=%s, is_admin=%s WHERE id=%s RETURNING id;",
            (user_update.username, user_update.email, user_update.xp, user_update.is_admin, user_id)
        )
    
    updated_user = cur.fetchone()
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
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
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found.")
    conn.commit()
    cur.close()
    conn.close()
    return

# --- Question Management Endpoints (No changes, just for completeness) ---

@app.get("/admin/questions", response_model=List[QuestionAdmin], summary="Get all questions", tags=["Admin"])
def get_all_questions(admin: UserInDB = Depends(get_current_admin_user)):
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, lesson_id, content as question_text, difficulty_level FROM questions ORDER BY id DESC;")
    questions = [QuestionAdmin.model_validate(dict(row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return questions

@app.post("/admin/questions", response_model=QuestionAdmin, status_code=status.HTTP_201_CREATED, summary="Create a new question", tags=["Admin"])
def create_question(question: QuestionCreateUpdate, admin: UserInDB = Depends(get_current_admin_user)):
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "INSERT INTO questions (lesson_id, content, difficulty_level, correct_answer_text) VALUES (%s, %s, %s, %s) RETURNING id;",
        (question.lesson_id, question.question_text, question.difficulty_level, question.correct_answer_text)
    )
    new_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return {**question.model_dump(exclude={"correct_answer_text"}), "id": new_id, "question_text": question.question_text}

@app.put("/admin/questions/{question_id}", response_model=QuestionAdmin, summary="Update a question", tags=["Admin"])
def update_question(question_id: int, question: QuestionCreateUpdate, admin: UserInDB = Depends(get_current_admin_user)):
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "UPDATE questions SET lesson_id=%s, content=%s, difficulty_level=%s, correct_answer_text=%s WHERE id=%s RETURNING id;",
        (question.lesson_id, question.question_text, question.difficulty_level, question.correct_answer_text, question_id)
    )
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    conn.commit()
    cur.close()
    conn.close()
    return {**question.model_dump(exclude={"correct_answer_text"}), "id": question_id, "question_text": question.question_text}

@app.delete("/admin/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a question", tags=["Admin"])
def delete_question(question_id: int, admin: UserInDB = Depends(get_current_admin_user)):
    # ... (code is unchanged)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id = %s RETURNING id;", (question_id,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    conn.commit()
    cur.close()
    conn.close()
    return