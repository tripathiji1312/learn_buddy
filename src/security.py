import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# --- Configuration ---
# This creates a context for hashing passwords. bcrypt is a strong algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This should be a real, long, random secret key stored securely, not here!
# For the hackathon, this is okay. We load it from an environment variable if it exists.
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_for_your_hackathon")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This creates a "scheme" that tells FastAPI where to look for the token.
# It will look for an "Authorization: Bearer <token>" header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Core Security Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain text password matches a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain text password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt