from uuid import UUID
from dotenv import load_dotenv
from fastapi import Depends, status, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os
from src.auth.models import PasswordResetToken, Users
from src.database import get_db

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a JWT access token with an expiry time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))  # ✅ Use timezone-aware datetime
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Extract user info
    except JWTError:
        return None  # Invalid token


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

oauth2_scheme = HTTPBearer()

from sqlalchemy.future import select  # Ensure correct import

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Extract user from token for authentication."""
    token = credentials.credentials  # Extract the actual token
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")  # Extract user email
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    print(token)
    stmt = select(Users).where(Users.email == user_email)
    result = await db.execute(stmt)  # ✅ Corrected: Execute the statement
    user = result.scalars().first()  # ✅ Extract the first user

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    return user


async def verify_user_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify the user's email and activate their account."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

async def delete_reset_token(user_id: int, db: AsyncSession):
    stmt = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
    await db.execute(stmt)  # ✅ Await query execution
    await db.commit()       # ✅ Await commit

async def is_valid_uuid(uuid, version=4):
    """Check if uuid is a valid UUID."""

    try:
        uuid_obj = UUID(uuid, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid

def is_valid_email(email: str) -> bool:

    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# atom

from datetime import datetime, timedelta, timezone
import re
from typing import Dict
from uuid import UUID

import bcrypt
from fastapi_mail import MessageSchema, MessageType
import jwt

# from src.auth.config import config
# from src.auth.exceptions import JwtTokenExpiredException
# from src.auth.models import User
# from src.auth.schemas import TokenData, TokenType, UserRole
# from src.mail import send_email


def is_valid_email(email: str) -> bool:
    """
    Check if the given string is a valid email address.

    An email is considered valid if it contains at least one character before '@',
    followed by a domain name with a '.' and at least one character after it.
    """

    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def is_valid_phone(phone: str) -> bool:

    return bool(re.match(r"^\d{10}$", phone))


def is_password_complex(password: str) -> bool:

    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True



def is_valid_uuid(uuid, version=4):

    try:
        uuid_obj = UUID(uuid, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid


# def create_access_token(user_id, role: UserRole) -> str:
#     current_time = datetime.now(timezone.utc)
#     expiry_time = current_time + timedelta(minutes=config.JWT_ACCESS_EXPIRY_MINUTES)
#     payload = {
#         "sub": str(user_id),
#         "role": role.value,
#         "iat": current_time,
#         "exp": expiry_time,
#         "aud": config.JWT_AUDIENCE,
#         "iss": config.JWT_ISSUER,
#         "type": TokenType.ACCESS.value,
#     }
#     return jwt.encode(payload, config.JWT_ACCESS_SECRET, algorithm="HS256")

