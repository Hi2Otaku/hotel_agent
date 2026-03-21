"""FastAPI dependency chain for JWT verification and RBAC.

Unlike the auth service, the room service does NOT look up users in a database.
It trusts the JWT claims (sub, role, email) directly.
"""

from collections.abc import AsyncGenerator

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from shared.jwt import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_public_key: str | None = None


def _get_public_key() -> str:
    """Lazily load the JWT public key from disk."""
    global _public_key
    if _public_key is None:
        with open(settings.JWT_PUBLIC_KEY_PATH) as f:
            _public_key = f.read()
    return _public_key


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async for session in get_session():
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and validate the current user from the JWT token.

    Returns the decoded payload dict (not a User ORM object).
    Keys: sub (UUID), role (str), email (str).
    """
    try:
        payload = verify_token(token, _get_public_key())
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload  # {"sub": uuid, "role": "admin", "email": "..."}


def require_role(*roles: str):
    """Dependency factory for role-based access control.

    Args:
        roles: One or more role strings that are allowed.

    Returns:
        A FastAPI dependency that checks the user's role claim.
    """

    async def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return checker


# Convenience dependencies for common role combinations
require_admin = require_role("admin")
require_manager_or_above = require_role("admin", "manager")
require_staff = require_role("admin", "manager", "front_desk")
require_any_staff = require_role("admin", "manager", "front_desk")
