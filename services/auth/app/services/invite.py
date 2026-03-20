"""Staff invite service: token creation and invite acceptance."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.token import PasswordResetToken, StaffInviteToken
from app.models.user import User, UserRole
from app.services.email import send_invite_email
from app.services.user import create_user, get_user_by_email

INVITE_TOKEN_EXPIRE_HOURS = 48


async def create_invite(
    db: AsyncSession,
    admin_user: User,
    target_role: str,
    email: str | None = None,
) -> str:
    """Create a staff invite link. Returns the raw token.

    Args:
        db: The async database session.
        admin_user: The admin creating the invite.
        target_role: The role to assign (admin, manager, front_desk).
        email: Optional email to send the invite to.

    Returns:
        The plaintext invite token.

    Raises:
        HTTPException: If the target role is invalid.
    """
    if target_role not in ("admin", "manager", "front_desk"):
        raise HTTPException(status_code=400, detail="Invalid target role")

    raw_token = secrets.token_urlsafe(32)
    token_hash = PasswordResetToken.hash_token(raw_token)  # reuse SHA-256 hashing
    invite = StaffInviteToken(
        token_hash=token_hash,
        target_role=UserRole(target_role),
        created_by=admin_user.id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(hours=INVITE_TOKEN_EXPIRE_HOURS),
    )
    db.add(invite)
    await db.commit()

    if email:
        await send_invite_email(email, raw_token, target_role)

    return raw_token


async def accept_invite(
    db: AsyncSession,
    raw_token: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> str:
    """Accept an invite and create a staff account. Returns a JWT access token.

    Args:
        db: The async database session.
        raw_token: The plaintext invite token.
        email: The new staff member's email.
        password: The new staff member's password.
        first_name: The new staff member's first name.
        last_name: The new staff member's last name.

    Returns:
        A JWT access token for the newly created user.

    Raises:
        HTTPException: If the invite is invalid, expired, used, or email is taken.
    """
    token_hash = PasswordResetToken.hash_token(raw_token)
    result = await db.execute(
        select(StaffInviteToken).where(
            StaffInviteToken.token_hash == token_hash,
            StaffInviteToken.used_at == None,  # noqa: E711
            StaffInviteToken.expires_at > datetime.now(timezone.utc),
        )
    )
    invite = result.scalar_one_or_none()
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite token")

    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await create_user(db, email, password, first_name, last_name, invite.target_role)
    invite.used_at = datetime.now(timezone.utc)
    invite.used_by = user.id
    await db.commit()

    return create_access_token(str(user.id), user.role.value, user.email)
