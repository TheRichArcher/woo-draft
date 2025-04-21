import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # Use async imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator # Import AsyncGenerator
# import os # No longer needed here
# from dotenv import load_dotenv # No longer needed here
from app.core.config import settings # Import settings

# load_dotenv() # Remove local load_dotenv
logging.info("Loading backend/app/core/db.py")

# DATABASE_URL = os.getenv("DATABASE_URL") # Remove local getenv

# Use settings.DATABASE_URL from config.py
# if not settings.DATABASE_URL: # Check is now done in config.py
#     logging.error("DATABASE_URL not set in environment variables!")
    # raise ValueError("DATABASE_URL not set")

# Use create_async_engine with settings.DATABASE_URL
engine = create_async_engine(settings.DATABASE_URL, echo=True) # echo=True for debugging SQL

# Use AsyncSession for the sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession, # Use AsyncSession
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

Base = declarative_base()

# Async dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]: # Fix type hint
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit() # Optional: commit at end of request
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
