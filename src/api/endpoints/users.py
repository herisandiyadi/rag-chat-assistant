"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core import security
from src.schemas import UserOut, UserCreate, UserUpdate, UserList
from src.services.user import UserService

router = APIRouter()


@router.get("/", response_model=UserList)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """List users with pagination."""
    return await UserService.list_users(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Create a new user (admin only)."""
    return await UserService.create_user(
        db=db,
        current_user=current_user,
        user_create=user,
    )


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Update user information."""
    return await UserService.update_user(
        db=db,
        current_user=current_user,
        user_id=user_id,
        user_update=user,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Delete a user (admin only)."""
    return await UserService.delete_user(
        db=db,
        current_user=current_user,
        user_id=user_id,
    )
