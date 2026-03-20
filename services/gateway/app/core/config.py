"""Gateway service configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Gateway settings for routing requests to backend services."""

    AUTH_SERVICE_URL: str = "http://auth:8000"
    ROOM_SERVICE_URL: str = "http://room:8000"
    BOOKING_SERVICE_URL: str = "http://booking:8000"
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"

    model_config = {"env_file": ".env"}


settings = Settings()
