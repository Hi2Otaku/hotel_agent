"""Chat service configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Chat service settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://chat_user:chat_pass@chat_db:5432/chat"

    # JWT (public key only -- chat service verifies, never signs)
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://hotel:hotel_pass@rabbitmq:5672/"

    # LLM configuration
    CHAT_LLM_PROVIDER: str = "anthropic"  # "anthropic" or "openai"
    CHAT_LLM_MODEL: str = "claude-sonnet-4-6-20250514"
    CHAT_LLM_API_KEY: str = "sk-placeholder"

    # Inter-service communication
    AUTH_SERVICE_URL: str = "http://auth:8000"
    ROOM_SERVICE_URL: str = "http://room:8000"
    BOOKING_SERVICE_URL: str = "http://booking:8000"

    # Debug
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
