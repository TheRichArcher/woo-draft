import logging
logging.info("Loading backend/app/routes/auth.py")
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.db import SessionLocal, get_db
from app.models.user import User
from app.schemas.user import UserInviteRequest, UserRegisterRequest, UserLoginRequest, UserResponse, CoachStatusResponse
from app.core.mail import send_invite_email
from app.core.config import settings
from app.core.security import get_current_user
from passlib.hash import bcrypt
from jose import jwt
import uuid
from datetime import datetime, timedelta
import anyio

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Helper: create JWT
def create_jwt(user: User):
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

@router.post("/invite", status_code=201)
async def invite_coach(data: UserInviteRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: User = Depends(lambda: None)):
    # TODO: Replace with real admin auth check
    # For now, allow all
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already invited or registered.")
    
    invite_token = str(uuid.uuid4())
    user = User(
        name=data.name,
        email=data.email,
        is_admin=False,
        is_verified=False,
        invite_token=invite_token
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    background_tasks.add_task(send_invite_email, data.name, data.email, invite_token)
    return {"message": "Invitation sent."}

@router.post("/register", response_model=UserResponse)
async def register_coach(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # TEMPORARY BYPASS: Check if user already exists before creating
    stmt_exist = select(User).where(func.lower(User.email) == data.email.lower())
    result_exist = await db.execute(stmt_exist)
    existing_user = result_exist.scalar_one_or_none()

    if existing_user:
        # If user exists and is verified, maybe just return them? Or raise error?
        # Let's raise an error as per the user's prompt suggestion to prevent duplicates clearly.
        raise HTTPException(status_code=400, detail="User already registered.")

    # If user doesn't exist, create them directly without invite token
    logging.warning(f"TEMPORARY BYPASS: Creating user {data.email} without invite token check.")
    user = User(
        name=data.name,
        email=data.email, # Store email as provided, comparison is case-insensitive
        password_hash=bcrypt.hash(data.password),
        is_verified=True, # Auto-verify
        is_admin=True, # Auto-set as admin
        invite_token=None # No token needed/used
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # The previous conditional admin logic based on email is removed,
    # as we are directly setting is_admin=True for this temporary bypass.

    return user

@router.post("/login")
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    logging.info(f"Login attempt for email: {data.email}")
    try:
        logging.info("Querying user...")
        stmt = select(User).where(func.lower(User.email) == data.email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logging.warning(f"Login failed: User {data.email} not found.")
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        
        if not user.password_hash:
            logging.warning(f"Login failed: User {data.email} has no password hash set.")
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        logging.info(f"Verifying password for user {data.email}...")
        # bcrypt is cpu-bound, run in threadpool
        password_match = await anyio.to_thread.run_sync(bcrypt.verify, data.password, user.password_hash)
        
        if not password_match:
            logging.warning(f"Login failed: Password mismatch for user {data.email}.")
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        logging.info(f"Password verified for {data.email}. Creating JWT...")
        token = create_jwt(user)
        logging.info(f"JWT created successfully for {data.email}.")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logging.exception(f"Login failed unexpectedly for {data.email}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/coaches", response_model=list[CoachStatusResponse])
async def get_coaches(db: AsyncSession = Depends(get_db), current_user: User = Depends(lambda: None)):
    # TODO: Replace with real admin auth check
    # For now, allow all
    stmt = select(User).where(User.is_admin == False)
    result = await db.execute(stmt)
    coaches = result.scalars().all()
    
    result_list = []
    for coach in coaches:
        if coach.is_verified:
            status = "Verified"
        elif coach.password_hash:
            status = "Signed Up"
        else:
            status = "Invited"
        result_list.append(CoachStatusResponse(
            id=coach.id,
            name=coach.name,
            email=coach.email,
            status=status,
            is_verified=coach.is_verified,
            created_at=coach.created_at
        ))
    return result_list

# New route to verify token
@router.post("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    # If get_current_user dependency runs without error, the token is valid.
    # The dependency also ensures the user exists and is verified.
    # Return specific fields as requested
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_verified": current_user.is_verified
    }
