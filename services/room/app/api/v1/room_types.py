"""Room type CRUD + photo upload/delete API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, require_manager_or_above, require_staff
from app.core.config import settings
from app.core.storage import get_minio_client
from app.schemas.room_type import (
    RoomTypeCreate,
    RoomTypeListResponse,
    RoomTypeResponse,
    RoomTypeUpdate,
)
from app.services.room_type import (
    add_photo_url,
    create_room_type,
    delete_room_type,
    get_room_type,
    get_room_types,
    remove_photo_url,
    update_room_type,
)
from app.services.storage import delete_photo, upload_photo

router = APIRouter(prefix="/api/v1/rooms/types", tags=["room-types"])


@router.post("", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type_endpoint(
    payload: RoomTypeCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_manager_or_above),
):
    """Create a new room type."""
    return await create_room_type(db, payload)


@router.get("", response_model=RoomTypeListResponse)
async def list_room_types_endpoint(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """List room types with pagination."""
    items, total = await get_room_types(db, skip=skip, limit=limit, active_only=active_only)
    return RoomTypeListResponse(items=items, total=total)


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
async def get_room_type_endpoint(
    room_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Get a room type by ID."""
    room_type = await get_room_type(db, room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    return room_type


@router.patch("/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type_endpoint(
    room_type_id: UUID,
    payload: RoomTypeUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_manager_or_above),
):
    """Update a room type."""
    return await update_room_type(db, room_type_id, payload)


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type_endpoint(
    room_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Soft-delete a room type."""
    await delete_room_type(db, room_type_id)
    return None


@router.post("/{room_type_id}/photos", response_model=RoomTypeResponse)
async def upload_photo_endpoint(
    room_type_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_manager_or_above),
):
    """Upload a photo for a room type."""
    client = get_minio_client()
    object_name = await upload_photo(client, settings.MINIO_BUCKET, file)
    # Build the URL for retrieval
    photo_url = f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_name}"
    return await add_photo_url(db, room_type_id, photo_url)


@router.delete("/{room_type_id}/photos", response_model=RoomTypeResponse)
async def delete_photo_endpoint(
    room_type_id: UUID,
    photo_url: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_manager_or_above),
):
    """Remove a photo from a room type."""
    # Extract object name from URL for MinIO deletion
    try:
        client = get_minio_client()
        # URL format: http://endpoint/bucket/room-photos/uuid.ext
        object_name = photo_url.split(f"/{settings.MINIO_BUCKET}/", 1)[1]
        await delete_photo(client, settings.MINIO_BUCKET, object_name)
    except Exception:
        pass  # Photo may already be deleted from storage; still remove URL
    return await remove_photo_url(db, room_type_id, photo_url)
