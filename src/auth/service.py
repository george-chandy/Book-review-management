from datetime import datetime, timezone
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from src.auth.models import EmailVerificationToken, PasswordResetToken, Users
from src.auth.schemas import RegisterRequest
from src.mail import send_email
from src.auth.models import EmailVerificationToken
from src.auth.utils import create_access_token, delete_reset_token
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import uuid
from src.mail import send_email
from sqlalchemy import delete, text
from src.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user_data, db: AsyncSession):

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
    



async def get_user_by_email(email: str, db: AsyncSession):
    query = select(Users).where(Users.email == email)
    result = await db.execute(query)
    return result.scalars().first()

async def deactivate_user(user: Users, db: AsyncSession) -> None:
    user.is_active = False
    user.deactivated_at = datetime.utcnow()
    await db.commit()

async def activate_user(user: Users, db: AsyncSession):
    user.is_active = True
    user.deactivated_at = None
    await db.commit()
    

async def verify_user_email(token: str, db: AsyncSession):
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