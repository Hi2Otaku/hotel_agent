"""FastAPI dependency chain for chat service authentication and rate limiting."""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import verify_token
from app.models.conversation import Conversation
from app.models.message import Message

# Rate limiting configuration
RATE_LIMIT_MESSAGES = 20
RATE_LIMIT_WINDOW = timedelta(minutes=1)


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
        A dict with id (from sub), role, and email claims, plus raw token.

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
        "token": token,
    }


async def rate_limiter(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Enforce per-user rate limit of 20 messages per minute.

    Counts user messages sent within the rate limit window. Raises
    HTTP 429 if the limit is exceeded.
    """
    since = datetime.now(timezone.utc) - RATE_LIMIT_WINDOW
    result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == uuid.UUID(user["id"]))
        .where(Message.role == "user")
        .where(Message.created_at >= since)
    )
    count = result.scalar() or 0
    if count >= RATE_LIMIT_MESSAGES:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before sending more messages.",
        )
