import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine # Use sync create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
logging.info("Loading backend/app/core/db.py")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logging.error("DATABASE_URL not set in environment variables!")
    # raise ValueError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL) # Use sync create_engine

# Use sync Session for the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Sync dependency
def get_db(): 
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
