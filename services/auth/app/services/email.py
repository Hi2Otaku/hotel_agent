"""Email sending service via fastapi-mail and Mailpit."""

from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings

_conf: ConnectionConfig | None = None


def _get_mail_config() -> ConnectionConfig:
    """Lazily build the mail configuration.

    Uses model_construct to bypass pydantic email validation on MAIL_FROM,
    which rejects .local domains used in development with Mailpit.
    """
    global _conf
    if _conf is not None:
        return _conf

    _conf = ConnectionConfig.model_construct(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
        TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email",
        SUPPRESS_SEND=0,
    )
    return _conf


async def send_password_reset_email(email: str, reset_token: str) -> None:
    """Send a password reset email with a reset link.

    Args:
        email: The recipient's email address.
        reset_token: The plaintext reset token for the URL.
    """
    reset_url = f"http://localhost:8000/reset-password?token={reset_token}"
    message = MessageSchema(
        subject="Reset Your Password - HotelBook",
        recipients=[email],
        template_body={"reset_url": reset_url, "token": reset_token},
        subtype=MessageType.html,
    )
    fm = FastMail(_get_mail_config())
    await fm.send_message(message, template_name="password_reset.html")


async def send_invite_email(email: str, invite_token: str, role: str) -> None:
    """Send a staff invitation email with an invite link.

    Args:
        email: The recipient's email address.
        invite_token: The plaintext invite token for the URL.
        role: The target role for the invited staff member.
    """
    invite_url = f"http://localhost:8000/invite/accept?token={invite_token}"
    message = MessageSchema(
        subject=f"You're Invited to Join HotelBook as {role.replace('_', ' ').title()}",
        recipients=[email],
        template_body={"invite_url": invite_url, "role": role, "token": invite_token},
        subtype=MessageType.html,
    )
    fm = FastMail(_get_mail_config())
    await fm.send_message(message, template_name="staff_invite.html")
