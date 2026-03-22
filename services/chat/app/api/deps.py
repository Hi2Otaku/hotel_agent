"""FastAPI dependency chain for chat service authentication."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import verify_token


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async for session in get_session():
        yield session


async def get_current_user(
    authorization: str = Header(...),
) -> dict:
    """Extract and validate the current user from the JWT Bearer token.

    Args:
        authorization: The Authorization header value (Bearer <token>).

    Returns:
        A dict with id (from sub), role, and email claims.

    Raises:
        HTTPException: If the header is missing/malformed or the token is invalid.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = authorization[len("Bearer "):]
    claims = verify_token(token)
    return {
        "id": claims["sub"],
        "role": claims["role"],
        "email": claims["email"],
    }


async def rate_limiter() -> None:
    """Placeholder rate limiter dependency.

    Will be implemented in Plan 02 with actual rate limiting logic.
    """
    pass
