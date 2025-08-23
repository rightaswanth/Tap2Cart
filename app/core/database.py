## === app/db/database.py ===
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    settings.database_url, 
    pool_size = int(os.getenv("DATABASE_POOL_SIZE", 5)),
    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", 10)),
    pool_pre_ping=True,
    pool_recycle=3600
    # connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
AsyncSessionLocal = sessionmaker(engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False
                                 )

Base = declarative_base()
 
async def get_db():
    async with AsyncSessionLocal() as session: 
        try: 
            yield session 
        finally: 
            await session.close() 
