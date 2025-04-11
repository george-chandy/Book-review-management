from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://georgechandy:6452@localhost:5432/bookreview"

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,   # Debugging purposes (set to False in production)
    pool_pre_ping=True  # Helps handle stale connections
)

SessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    autoflush=False,  # Helps avoid unexpected commits
    autocommit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session  # No need to manually close it