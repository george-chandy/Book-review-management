from uuid import UUID
from dotenv import load_dotenv
from fastapi import Depends, status, HTTPException
from jose import JWTError
from sqlalchemy import delete
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
# from jose import JWTError, jwt
import os
from src.auth.models import PasswordResetToken, Users
from src.auth.config import config
from src.database import get_db
from src.mail import send_email
from src.auth.schemas import TokenData,TokenType
from src.auth.exceptions import JwtTokenExpiredException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.future import select 

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
    

oauth2_scheme = HTTPBearer()


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
from typing import Dict, Optional
from uuid import UUID

import bcrypt
from fastapi_mail import MessageSchema, MessageType
import jwt


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


async def send_verification_email(user_id: int, session: AsyncSession):
    """Fetch user details from the database and send a verification email."""
    
    result = await session.execute(select(Users).where(Users.id == user_id))
    user = result.scalars().first()

    if not user:
        return {"error": "User not found"}

    verification_token = user.verification_token  

    subject = "Verify Your Email Address with book review app"
    body = f"""
    Dear {user.first_name} {user.last_name},

    Thank you for joining the Book Review App! We're thrilled to have you in our community of book lovers. 

    To complete your registration and start exploring book reviews, please verify your email address by clicking the link below:

    {config.HOST_ADDRESS}/verify-email?token={verification_token}


    {config.HOST_ADDRESS}/verify-email?token={verification_token}
    """

    message = MessageSchema(
        recipients=[user.email], subject=subject, body=body, subtype=MessageType.plain
    )

    await send_email(message=message)

    return {"message": "Verification email sent successfully"}


def create_refresh_token(user_id: str) -> str:
    """Generate a refresh token with a longer expiration time."""
    payload = {
        "sub": user_id,  # User ID as subject
        "exp": datetime.utcnow() + timedelta(days=config.JWT_REFRESH_EXPIRY_DAYS),
        "iat": datetime.utcnow(),
        "iss": config.JWT_ISSUER,
        "aud": config.JWT_AUDIENCE,
        "type": "refresh"
    }
    
    return jwt.encode(payload, config.JWT_REFRESH_SECRET, algorithm="HS256")



def create_access_token(user_id) -> str:
    current_time = datetime.now(timezone.utc)
    expiry_time = current_time + timedelta(minutes=config.JWT_ACCESS_EXPIRY_MINUTES)
    payload = {
        "sub": str(user_id),
        "iat": current_time,
        "exp": expiry_time,
        "aud": config.JWT_AUDIENCE,
        "iss": config.JWT_ISSUER,
        "type": TokenType.ACCESS.value,
    }
    return jwt.encode(payload, config.JWT_ACCESS_SECRET, algorithm="HS256")


def validate_and_decode_token(token: str, token_type: TokenType) -> TokenData | None:
    """
    Returns: token data if token is valid else return None.
    Exception: JwtTokenExpiredException <- if token is expired
    """

    secrets = {
        TokenType.ACCESS: config.JWT_ACCESS_SECRET,
        TokenType.REFRESH: config.JWT_REFRESH_SECRET,
    }

    try:
        payload: Dict = jwt.decode(
            token,
            secrets[token_type],
            ["HS256"],
            audience=config.JWT_AUDIENCE,
            issuer=config.JWT_ISSUER,
        )

        user_id = payload.get("sub") 
        if not user_id:
            return None  

        return TokenData(user_id=int(user_id))  
    except jwt.exceptions.ExpiredSignatureError:
        raise JwtTokenExpiredException()
    except jwt.exceptions.InvalidTokenError:
        return None
    except Exception:
        return None