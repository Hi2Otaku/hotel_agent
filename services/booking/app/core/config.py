"""Booking service configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Booking service settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://booking_user:booking_pass@booking_db:5432/bookings"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://hotel:hotel_pass@rabbitmq:5672/"

    # JWT (public key only -- booking service verifies, never signs)
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"

    # Inter-service communication
    ROOM_SERVICE_URL: str = "http://room:8000"
    AUTH_SERVICE_URL: str = "http://auth:8000"

    # Mail (Mailpit)
    MAIL_SERVER: str = "mailpit"
    MAIL_PORT: int = 1025
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "bookings@hotel.local"
    MAIL_FROM_NAME: str = "HotelBook"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_VALIDATE_CERTS: bool = False

    # Business rules
    CANCELLATION_POLICY_DAYS: int = 3
    PENDING_EXPIRY_MINUTES: int = 15
    EXPIRY_CHECK_INTERVAL_SECONDS: int = 300

    # Debug
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
