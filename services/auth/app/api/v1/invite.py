"""Invite API routes: staff invite creation and acceptance."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    StaffInviteAccept,
    StaffInviteRequest,
    TokenResponse,
)
from app.services.invite import accept_invite, create_invite

router = APIRouter(prefix="/api/v1/invite", tags=["invite"])


@router.post("/create", response_model=MessageResponse)
async def create_invite_endpoint(
    request: StaffInviteRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create a staff invite link. Requires admin role."""
    token = await create_invite(
        db, admin, request.target_role, getattr(request, "email", None)
    )
    return MessageResponse(message=f"Invite created. Token: {token}")


@router.post(
    "/accept",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_invite_endpoint(
    request: StaffInviteAccept,
    db: AsyncSession = Depends(get_db),
):
    """Accept a staff invite and create an account."""
    access_token = await accept_invite(
        db,
        request.token,
        request.email,
        request.password,
        request.first_name,
        request.last_name,
    )
    return TokenResponse(access_token=access_token, token_type="bearer")
