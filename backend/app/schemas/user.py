from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserInviteRequest(BaseModel):
    name: str
    email: EmailStr

class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    token: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    is_verified: bool
    is_admin: bool
    invite_token: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class CoachStatusResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    status: str  # Invited, Signed Up, Verified
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True 