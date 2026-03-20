"""Auth request and response schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Guest registration request."""

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """Password reset request -- sends email with reset link."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with new password."""

    token: str
    new_password: str = Field(min_length=8)


class StaffInviteRequest(BaseModel):
    """Staff invite request -- admin creates invite link."""

    target_role: str = Field(
        pattern="^(admin|manager|front_desk)$",
        description="Must be admin, manager, or front_desk",
    )
    email: str | None = Field(
        default=None, description="Optional email hint for the invite"
    )


class StaffInviteAccept(BaseModel):
    """Staff invite acceptance -- creates staff account."""

    token: str
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
