"""MinIO photo upload/delete operations for room type images."""

import asyncio
import json
import uuid as uuid_mod

from fastapi import UploadFile
from minio import Minio


async def upload_photo(client: Minio, bucket: str, file: UploadFile) -> str:
    """Upload photo to MinIO, return object path. Runs sync client in executor."""
    ext = (
        file.filename.rsplit(".", 1)[-1]
        if file.filename and "." in file.filename
        else "jpg"
    )
    object_name = f"room-photos/{uuid_mod.uuid4()}.{ext}"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: client.put_object(
            bucket,
            object_name,
            file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type or "image/jpeg",
        ),
    )
    return object_name


async def delete_photo(client: Minio, bucket: str, object_name: str) -> None:
    """Delete photo from MinIO."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: client.remove_object(bucket, object_name)
    )


def ensure_bucket(client: Minio, bucket: str) -> None:
    """Create bucket if it doesn't exist. Called on startup."""
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        # Set public read policy for demo
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
        client.set_bucket_policy(bucket, json.dumps(policy))
