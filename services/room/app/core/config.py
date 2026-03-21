"""Room service configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Room service settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://room_user:room_pass@room_db:5432/rooms"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://hotel:hotel_pass@rabbitmq:5672/"

    # JWT (public key only -- room service verifies, never signs)
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"

    # MinIO object storage
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "hotelbook"
    MINIO_SECURE: bool = False

    # Startup behaviour
    SEED_ON_STARTUP: bool = True

    # Debug
    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
