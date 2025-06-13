import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware  # <-- THE FIX IS HERE
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import psycopg2.extras
from datetime import timedelta
from jose import jwt, JWTError

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

# Define the list of origins that are allowed to make requests to your API
origins = [
    "http://localhost",
    "http://localhost:5500",  # The origin of your VS Code Live Server
    "http://127.0.0.1:5500", # Sometimes the browser uses this address as well
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


# --- Dependency for getting the current user ---
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
    cur.execute("SELECT id, username, email, xp FROM users WHERE username = %s", (username,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if user_data is None:
        raise credentials_exception

    return User.model_validate(dict(user_data))


# --- AUTHENTICATION ENDPOINTS ---
@app.post("/signup", summary="Create a new user", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Creates a new user account."""
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
    """Authenticates a user and returns a JWT access token."""
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


# --- PROTECTED LEARNING ENDPOINTS ---
@app.post("/next_question", summary="Get the next AI-selected question (Protected)")
def get_next_question(req: NextQuestionRequest, current_user: User = Depends(get_current_user)):
    """
    Uses a more user-friendly Epsilon-Greedy AI to select optimal difficulty.
    """
    logging.info(f"Request for next question for user {current_user.id}, lesson {req.lesson_id}")

    optimal_difficulty = select_difficulty_epsilon_greedy(current_user.id, req.lesson_id)
    question_id, question_text = select_question(optimal_difficulty, req.lesson_id)

    if question_id is None:
        raise HTTPException(status_code=404, detail="No questions found for this difficulty.")

    return {"difficulty_level": optimal_difficulty, "question_id": question_id, "question_text": question_text}


@app.post("/submit_answer", summary="Submit an answer (Protected)")
def submit_answer(submission: AnswerSubmission, current_user: User = Depends(get_current_user)):
    """
    Uses NLP to check answer, updates RL model. Requires authentication.
    """
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