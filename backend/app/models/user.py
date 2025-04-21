import logging
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.db import Base

logging.info("Loading backend/app/models/user.py")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)  # null if not yet signed up
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    invite_token = Column(String, nullable=True)  # for invite link
    created_at = Column(DateTime, default=datetime.utcnow)
