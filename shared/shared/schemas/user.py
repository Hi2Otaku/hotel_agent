"""Shared Pydantic schemas for JWT token payload.

Used by all services to parse and validate JWT token contents.
"""

from datetime import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Schema representing the decoded JWT token payload."""

    sub: str
    role: str
    email: str
    iat: datetime
    exp: datetime
