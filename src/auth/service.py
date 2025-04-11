from datetime import datetime, timezone
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from src.auth.models import EmailVerificationToken, PasswordResetToken, Users
from src.auth.schemas import RegisterRequest, User
from src.mail import send_email
from src.auth.models import EmailVerificationToken
from src.auth.utils import create_access_token, delete_reset_token, hash_password, is_password_complex
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import uuid
from src.mail import send_email
from sqlalchemy import delete, text
from src.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user_data, db: AsyncSession):
    # ✅ Check if email already exists

    hashed_password = pwd_context.hash(user_data.password)
    user = Users(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        password=hashed_password,
        gender=user_data.gender,
        dob=user_data.dob,
        is_email_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # ✅ Create verification token and send email
    await create_verification_token(user, db)
    return user

async def create_verification_token(user, db: AsyncSession):
    token = str(uuid.uuid4())

    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(days=1)

    verification_entry = EmailVerificationToken(
        user_id=user.id,
        token=token,
        created_at=created_at,
        expires_at=expires_at
    )

    db.add(verification_entry)
    await db.commit()
    await db.refresh(verification_entry)

    # verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    # await send_email(user.email, "Verify Your Email", f"Click here to verify: {verification_link}")
    
async def get_user_by_id(db: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession):
    query = select(Users).where(Users.email == email)
    result = await db.execute(query)
    return result.scalars().first()

async def deactivate_user(user: Users, db: AsyncSession) -> None:
    user.is_active = False
    user.deactivated_at = datetime.now(timezone.utc)
    await db.commit()

async def activate_user(user: Users, db: AsyncSession):
    user.is_active = True
    await db.commit()
    

async def verify_the_email(token: str, db: AsyncSession):
    """Verify email using token."""
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.token == token)
    result = await db.execute(stmt)
    email_verification = result.scalars().first()

    if not email_verification:
        return {"error": "Invalid token"}

    # ✅ Get user and update status
    stmt = select(Users).where(Users.id == email_verification.user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        return {"error": "User not found"}

    user.is_email_verified = True

    # ✅ Remove the token after successful verification
    await db.delete(email_verification)
    await db.commit()

    return {"message": "Email verified successfully"}

async def create_reset_token(email: str, db: AsyncSession):
    
    user = await get_user_by_email(email, db)
    stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    result = await db.execute(stmt)
    existing_token = result.scalars().first()

    if existing_token:
        await delete_reset_token(user.id, db)
    
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    db.add(reset_token)
    await db.commit()  # ✅ Await commit after add

    return token


async def delete_email_token(user_id: int, db: AsyncSession):
   stmt = select(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id)
   result = await db.execute(stmt)
   token_entry = result.scalars().first()


   if token_entry:
       await db.delete(token_entry)
       await db.commit()
       
       
# async def get_user_id_by_password_token(db: AsyncSession, token: str):
#     """Retrieves the user ID from a password reset token."""
#     stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
#     result = await db.execute(stmt)
#     db_token = result.scalar_one_or_none()

#     if not db_token:
#         return None
    
#     current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Convert to offset-aware
#     if current_time > db_token.expires_at:

#         return db_token.user_id


async def get_user_id_by_password_token(db: AsyncSession, token: str):
    """Retrieves the user ID from a password reset token."""
    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token:
        return None

    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Ensure UTC timezone

    # Ensure expires_at is also timezone-aware
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if current_time > expires_at:
        return None  # Token is expired, return None

    return db_token.user_id  


async def update_user_password(db: AsyncSession, user_id: int, hashed_password: str):
    """Updates the user's password in the database."""
    stmt = select(Users).where(Users.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # if not user:
    #     raise 

    user.password = hashed_password
    await db.commit()


async def mark_email_verified(db: AsyncSession, user_id: int):
    """Marks a user's email as verified."""
    stmt = select(Users).where(Users.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.is_email_verified = True
        await db.commit()


async def delete_email_tokens(db: AsyncSession, user_id: int):
    """Deletes email verification tokens for the user."""
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id)
    result = await db.execute(stmt)
    tokens = result.scalars().all()

    for token in tokens:
        await db.delete(token)

    await db.commit()


async def delete_password_tokens(db: AsyncSession, user_id: int):
    """Deletes password reset tokens for the user."""
    stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
    result = await db.execute(stmt)
    tokens = result.scalars().all()

    for token in tokens:
        await db.delete(token)

    await db.commit()




