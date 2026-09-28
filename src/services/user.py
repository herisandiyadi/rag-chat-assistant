"""User service for authentication and management."""

import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.db import get_db
from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.models.department import Department
from src.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management."""
    
    @staticmethod
    async def authenticate(
        db: AsyncSession,
        username: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with username and password."""
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if user and verify_password(password, user.password_hash):
            return user
        return None
    
    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str,
    ) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        current_user: User,
        user_create: UserCreate,
    ) -> User:
        """Create a new user (admin only)."""
        # Check if current user has permission
        if current_user.role_type not in ["super_admin", "dept_admin"]:
            raise PermissionError("Not authorized to create users")
        
        # Check if username already exists
        existing = await UserService.get_user_by_username(db, user_create.username)
        if existing:
            raise ValueError("Username already exists")
        
        # Create new user
        user = User(
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
            department_id=user_create.department_id,
            role_type=user_create.role_type,
            level=user_create.level,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def list_users(
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """List users with pagination (admin only)."""
        if current_user.role_type not in ["super_admin", "dept_admin"]:
            raise PermissionError("Not authorized to list users")
        
        # Build query based on role
        query = select(User).offset(skip).limit(limit)
        
        if current_user.role_type == "dept_admin":
            query = query.where(User.department_id == current_user.department_id)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Get total count
        count_query = select(User)
        if current_user.role_type == "dept_admin":
            count_query = count_query.where(User.department_id == current_user.department_id)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        return {
            "total": total,
            "users": users,
        }
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        current_user: User,
        user_id: str,
        user_update: UserUpdate,
    ) -> Optional[User]:
        """Update user information."""
        user = await db.get(User, user_id)
        if not user:
            return None
        
        # Check permission
        if current_user.role_type == "dept_admin":
            if user.department_id != current_user.department_id:
                raise PermissionError("Not authorized to update this user")
        
        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                setattr(user, "password_hash", get_password_hash(value))
            else:
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(
        db: AsyncSession,
        current_user: User,
        user_id: str,
    ) -> bool:
        """Delete a user (admin only)."""
        user = await db.get(User, user_id)
        if not user:
            return False
        
        # Check permission
        if current_user.role_type == "dept_admin":
            if user.department_id != current_user.department_id:
                raise PermissionError("Not authorized to delete this user")
        
        await db.delete(user)
        await db.commit()
        return True


def get_user_service() -> UserService:
    """Get user service instance."""
    return UserService()
