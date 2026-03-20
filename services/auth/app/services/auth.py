"""Auth service layer for registration and authentication."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.user import UserRole
from app.services.user import create_user, get_user_by_email


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> str:
    """Register a new guest user and return a JWT token.

    Args:
        db: The async database session.
        email: The user's email address.
        password: The plaintext password.
        first_name: The user's first name.
        last_name: The user's last name.

    Returns:
        A JWT access token string.

    Raises:
        HTTPException: 409 if the email is already registered.
    """
    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = await create_user(db, email, password, first_name, last_name)
    return create_access_token(str(user.id), user.role.value, user.email)


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> str:
    """Authenticate a user by email and password, return JWT token.

    Args:
        db: The async database session.
        email: The user's email address.
        password: The plaintext password to verify.

    Returns:
        A JWT access token string.

    Raises:
        HTTPException: 401 if credentials are invalid or account is deactivated.
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )
    return create_access_token(str(user.id), user.role.value, user.email)
