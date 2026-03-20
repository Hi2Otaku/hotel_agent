"""Auth service security utilities.

Provides password hashing with Argon2 and JWT token creation/verification
using RS256 asymmetric keys.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """Hash a password using Argon2.

    Args:
        password: The plaintext password to hash.

    Returns:
        The Argon2 hash string.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hash.

    Args:
        plain_password: The plaintext password to check.
        hashed_password: The stored Argon2 hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


def _load_key(path: str) -> str:
    """Load a PEM key from the filesystem.

    Args:
        path: Path to the PEM key file.

    Returns:
        The key contents as a string.
    """
    return Path(path).read_text()


def create_access_token(user_id: str, role: str, email: str) -> str:
    """Create a JWT access token signed with the RS256 private key.

    Args:
        user_id: The user's UUID as a string.
        role: The user's role (guest, admin, manager, front_desk).
        email: The user's email address.

    Returns:
        The encoded JWT token string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token using the RS256 public key.

    Args:
        token: The JWT token string to verify.

    Returns:
        The decoded token payload as a dictionary.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    public_key = _load_key(settings.JWT_PUBLIC_KEY_PATH)
    return jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])


__all__ = ["hash_password", "verify_password", "create_access_token", "verify_token"]
