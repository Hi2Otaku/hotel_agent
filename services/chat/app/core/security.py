"""Chat service JWT verification.

Verifies RS256 JWT tokens using the public key only.
The chat service never signs tokens -- only the auth service does.
"""

from pathlib import Path

import jwt
from fastapi import HTTPException, status

from app.core.config import settings


def _load_public_key() -> str:
    """Load the RS256 public key from the filesystem.

    Returns:
        The public key contents as a string.
    """
    return Path(settings.JWT_PUBLIC_KEY_PATH).read_text()


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token using the RS256 public key.

    Args:
        token: The JWT token string to verify.

    Returns:
        The decoded token payload with sub, role, and email claims.

    Raises:
        HTTPException: If the token is expired or invalid (401).
    """
    try:
        public_key = _load_public_key()
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
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


__all__ = ["verify_token"]
