"""Auth API routes: registration, login, password reset, and current user."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth import authenticate_user, register_user
from app.services.password_reset import confirm_password_reset, request_password_reset

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new guest account and return a JWT token."""
    access_token = await register_user(
        db,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email (username) and password, return JWT token.

    Uses OAuth2PasswordRequestForm for Swagger UI compatibility.
    The 'username' field is treated as the email address.
    """
    access_token = await authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    return TokenResponse(access_token=access_token)


@router.post("/password-reset/request", response_model=MessageResponse)
async def password_reset_request(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email. Always returns 200 (no info leakage)."""
    await request_password_reset(db, payload.email)
    return MessageResponse(
        message="If that email exists, a reset link has been sent"
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def password_reset_confirm(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Confirm password reset with token and new password."""
    await confirm_password_reset(db, payload.token, payload.new_password)
    return MessageResponse(message="Password reset successful")


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated user's profile."""
    return current_user
