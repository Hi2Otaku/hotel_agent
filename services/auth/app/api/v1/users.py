"""User management API routes (admin/staff only)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, require_staff
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse
from app.services.user import get_all_users

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_admin),
):
    """List all users (admin only)."""
    users, total = await get_all_users(db, skip=skip, limit=limit)
    return UserListResponse(users=users, total=total)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_staff),
):
    """Get a specific user by ID (staff only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
