"""Auth service configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Auth service settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://auth_user:auth_pass@auth_db:5432/auth"

    # JWT
    JWT_PRIVATE_KEY_PATH: str = "/run/secrets/jwt_private_key"
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"
    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRE_HOURS: int = 24

    # Mail (Mailpit in development)
    MAIL_SERVER: str = "mailpit"
    MAIL_PORT: int = 1025
    MAIL_FROM: str = "noreply@hotelbook.local"
    MAIL_FROM_NAME: str = "HotelBook"
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_VALIDATE_CERTS: bool = False

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://hotel:hotel_pass@rabbitmq:5672/"

    # First admin seeding
    FIRST_ADMIN_EMAIL: str = "admin@hotel.local"
    FIRST_ADMIN_PASSWORD: str = "admin123"

    # Debug
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
