"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Optional, Any

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.settings import settings
from src.core.db import get_db
from src.models.user import User
from src.models.department import Department

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def require_admin_role(user: User = Depends(get_current_user)) -> User:
    """Require user to have admin role."""
    if user.role_type not in ["super_admin", "dept_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return user


def resolve_access_permission(
    user_department_id: int,
    user_role_type: str,
    user_level: int,
    document_department_id: int,
    document_min_level: int,
) -> tuple[bool, str]:
    """
    Determine if user has access to document.
    
    Returns: (has_access, reason)
    """
    # Super admin has full access
    if user_role_type == "super_admin":
        return True, "allowed"
    
    # Department admin - only documents in their department
    if user_role_type == "dept_admin":
        if user_department_id != document_department_id:
            return False, "access_denied"
        return True, "allowed"
    
    # Regular user - must match department and meet minimum level
    if user_department_id != document_department_id:
        return False, "access_denied"
    
    if user_level < document_min_level:
        return False, "access_denied"
    
    return True, "allowed"
