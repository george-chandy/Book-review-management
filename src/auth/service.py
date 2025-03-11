from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from src.auth.models import Users
from src.auth.schemas import RegisterRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user_data: RegisterRequest, db: AsyncSession):
    hashed_password = pwd_context.hash(user_data.password)
    db_user = Users(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        gender=user_data.gender,
        dob=user_data.dob,
        password=hashed_password,  # Store hashed password
        email=user_data.email,
        is_email_verified=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

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
    