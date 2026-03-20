"""Password reset service: token generation, validation, and password update."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.token import PasswordResetToken
from app.models.user import User
from app.services.email import send_password_reset_email
from app.services.user import get_user_by_email

RESET_TOKEN_EXPIRE_MINUTES = 15


async def request_password_reset(db: AsyncSession, email: str) -> None:
    """Request a password reset. Always returns without error (no info leakage).

    Generates a secure random token, stores its SHA-256 hash in the database,
    and sends the plaintext token to the user's email via Mailpit.

    Args:
        db: The async database session.
        email: The email address to send the reset link to.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return  # Don't reveal whether email exists

    raw_token = secrets.token_urlsafe(32)
    token_hash = PasswordResetToken.hash_token(raw_token)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(reset_token)
    await db.commit()

    await send_password_reset_email(user.email, raw_token)


async def confirm_password_reset(
    db: AsyncSession, raw_token: str, new_password: str
) -> None:
    """Confirm a password reset using the token and set a new password.

    Validates the token hash, checks expiry and single-use, then updates
    the user's password.

    Args:
        db: The async database session.
        raw_token: The plaintext token from the reset URL.
        new_password: The new password to set.

    Raises:
        HTTPException: If the token is invalid, expired, or already used.
    """
    token_hash = PasswordResetToken.hash_token(raw_token)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False,  # noqa: E712
            PasswordResetToken.expires_at > datetime.now(timezone.utc),
        )
    )
    reset_token = result.scalar_one_or_none()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = await db.get(User, reset_token.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(new_password)
    reset_token.used = True
    await db.commit()
