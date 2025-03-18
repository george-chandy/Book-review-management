# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from typing import AsyncGenerator

# from src.config import config
# engine = create_async_engine(config.DATABASE_URL, future=True, echo=True, pool_pre_ping=True)
# # engine = create_async_engine(config.DATABASE_URL)
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)




from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://georgechandy:6452@localhost:5432/bookreview"

engine = create_async_engine(
    DATABASE_URL, 
    future=True, 
    echo=True
)

SessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
        await session.close()
