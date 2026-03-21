"""MinIO object storage client singleton."""

from minio import Minio
from app.core.config import settings


def get_minio_client() -> Minio:
    """Create and return a MinIO client instance.

    Returns:
        A configured Minio client for the hotelbook bucket.
    """
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
