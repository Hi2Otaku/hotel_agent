"""Room type CRUD business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate


async def create_room_type(db: AsyncSession, data: RoomTypeCreate) -> RoomType:
    """Create a new room type. Raises 409 if name or slug already exists."""
    # Check uniqueness
    existing = await db.execute(
        select(RoomType).where(
            (RoomType.name == data.name) | (RoomType.slug == data.slug)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room type with this name or slug already exists",
        )

    room_type = RoomType(
        name=data.name,
        slug=data.slug,
        description=data.description,
        max_adults=data.max_adults,
        max_children=data.max_children,
        bed_config=[bc.model_dump() for bc in data.bed_config],
        amenities=data.amenities,
    )
    db.add(room_type)
    await db.commit()
    await db.refresh(room_type)
    return room_type


async def get_room_type(
    db: AsyncSession, room_type_id: uuid.UUID
) -> RoomType | None:
    """Get a room type by ID."""
    return await db.get(RoomType, room_type_id)


async def get_room_types(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
) -> tuple[list[RoomType], int]:
    """List room types with pagination. Returns (items, total_count)."""
    query = select(RoomType)
    count_query = select(func.count()).select_from(RoomType)

    if active_only:
        query = query.where(RoomType.is_active == True)  # noqa: E712
        count_query = count_query.where(RoomType.is_active == True)  # noqa: E712

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return items, total


async def update_room_type(
    db: AsyncSession, room_type_id: uuid.UUID, data: RoomTypeUpdate
) -> RoomType:
    """Update a room type. Raises 404 if not found, 409 if unique constraint violated."""
    room_type = await db.get(RoomType, room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check uniqueness for name/slug changes
    if "name" in update_data or "slug" in update_data:
        conditions = []
        if "name" in update_data:
            conditions.append(RoomType.name == update_data["name"])
        if "slug" in update_data:
            conditions.append(RoomType.slug == update_data["slug"])

        from sqlalchemy import or_

        existing = await db.execute(
            select(RoomType).where(
                or_(*conditions), RoomType.id != room_type_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room type with this name or slug already exists",
            )

    # Convert bed_config if present
    if "bed_config" in update_data and update_data["bed_config"] is not None:
        update_data["bed_config"] = [
            bc.model_dump() if hasattr(bc, "model_dump") else bc
            for bc in update_data["bed_config"]
        ]

    for field, value in update_data.items():
        setattr(room_type, field, value)

    await db.commit()
    await db.refresh(room_type)
    return room_type


async def delete_room_type(db: AsyncSession, room_type_id: uuid.UUID) -> None:
    """Soft-delete a room type. Raises 404 if not found."""
    room_type = await db.get(RoomType, room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    room_type.is_active = False
    await db.commit()


async def add_photo_url(
    db: AsyncSession, room_type_id: uuid.UUID, url: str
) -> RoomType:
    """Append a photo URL to the room type's photo_urls list."""
    room_type = await db.get(RoomType, room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    # JSONB list mutation: create new list to trigger change detection
    current_urls = list(room_type.photo_urls or [])
    current_urls.append(url)
    room_type.photo_urls = current_urls
    await db.commit()
    await db.refresh(room_type)
    return room_type


async def remove_photo_url(
    db: AsyncSession, room_type_id: uuid.UUID, url: str
) -> RoomType:
    """Remove a photo URL from the room type's photo_urls list."""
    room_type = await db.get(RoomType, room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    current_urls = list(room_type.photo_urls or [])
    if url in current_urls:
        current_urls.remove(url)
    room_type.photo_urls = current_urls
    await db.commit()
    await db.refresh(room_type)
    return room_type
