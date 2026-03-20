"""JWT verification using public key only.

This module is used by all services (Room, Booking, Gateway) to verify
tokens signed by the Auth service. Only the public key is needed.
"""

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def verify_token(token: str, public_key: str) -> dict:
    """Verify a JWT token using the RS256 public key.

    Args:
        token: The JWT token string to verify.
        public_key: The RSA public key in PEM format.

    Returns:
        The decoded token payload as a dictionary.

    Raises:
        ExpiredSignatureError: If the token has expired.
        InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(token, public_key, algorithms=["RS256"])


__all__ = ["verify_token", "ExpiredSignatureError", "InvalidTokenError"]
