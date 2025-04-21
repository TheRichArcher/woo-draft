import logging
logging.info("Loading backend/app/routes/auth.py")
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import SessionLocal, get_db
from app.models.user import User
from app.schemas.user import UserInviteRequest, UserRegisterRequest, UserLoginRequest, UserResponse, CoachStatusResponse
from app.core.mail import send_invite_email
from app.core.config import settings
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
    stmt = select(User).where(User.invite_token == data.token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid invite token.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already registered.")
    
    user.name = data.name
    user.email = data.email
    user.password_hash = bcrypt.hash(data.password)
    user.is_verified = True
    user.invite_token = None
    
    # Temporary override for admin registration
    if data.email == "admin@woo-combine.com":
        logging.warning(f"Temporarily setting admin role for {data.email} during registration.")
        user.is_admin = True
    # else: # Optional: Ensure non-admins are explicitly set to False if needed
    #     user.is_admin = False
        
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    logging.info(f"Login attempt for email: {data.email}")
    try:
        logging.info("Querying user...")
        stmt = select(User).where(User.email == data.email)
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
