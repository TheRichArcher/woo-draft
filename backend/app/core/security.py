from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
import logging
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logging.warning("Token validation failed: 'sub' (user_id) missing in payload.")
            raise credentials_exception
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
             logging.warning(f"Token validation failed: 'sub' field '{user_id_str}' is not a valid UUID.")
             raise credentials_exception

    except JWTError as e:
        logging.warning(f"Token validation failed: JWTError - {e}")
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        logging.warning(f"Token validation failed: User with id {user_id} not found.")
        raise credentials_exception
    if not user.is_verified:
        logging.warning(f"Token validation failed: User {user.email} is not verified.")
        raise HTTPException(status_code=403, detail="User not verified")

    logging.info(f"Token validated successfully for user: {user.email} (ID: {user.id})")
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        logging.warning(f"Admin access denied for user: {current_user.email}")
        raise HTTPException(status_code=403, detail="Not enough privileges")
    logging.info(f"Admin access granted for user: {current_user.email}")
    return current_user 