"""FastAPI dependency chain for authentication and RBAC."""

from collections.abc import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import verify_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async for session in get_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token.

    Args:
        token: The Bearer token from the Authorization header.
        db: The database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: If the token is expired, invalid, or the user is not found/inactive.
    """
    try:
        payload = verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_role(*roles: UserRole):
    """Dependency factory for role-based access control.

    Args:
        roles: One or more UserRole values that are allowed.

    Returns:
        A FastAPI dependency that checks the user's role.
    """

    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return check_role


# Convenience dependencies for common role combinations
require_admin = require_role(UserRole.ADMIN)
require_manager_or_above = require_role(UserRole.ADMIN, UserRole.MANAGER)
require_staff = require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.FRONT_DESK)
