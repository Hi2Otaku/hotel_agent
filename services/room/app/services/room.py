"""Room CRUD + role-based status state machine with audit logging."""

import uuid
from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.models.status_log import RoomStatusChange
from app.schemas.room import RoomCreate, RoomUpdate


# ---------------------------------------------------------------------------
# Status transition rules
# ---------------------------------------------------------------------------

ROLE_TRANSITIONS: dict[str, set[tuple[RoomStatus, RoomStatus]] | None] = {
    "front_desk": {
        (RoomStatus.AVAILABLE, RoomStatus.OCCUPIED),
        (RoomStatus.OCCUPIED, RoomStatus.AVAILABLE),
        (RoomStatus.RESERVED, RoomStatus.OCCUPIED),
    },
    "housekeeping": {
        (RoomStatus.CLEANING, RoomStatus.INSPECTED),
    },
    "manager": None,  # None = all transitions allowed
    "admin": None,
}

AUTO_TRANSITIONS = {
    "checkout": (RoomStatus.OCCUPIED, RoomStatus.CLEANING),
    "inspection_complete": (RoomStatus.INSPECTED, RoomStatus.AVAILABLE),
    "booking_assigned": (RoomStatus.AVAILABLE, RoomStatus.RESERVED),
}


# ---------------------------------------------------------------------------
# Room CRUD
# ---------------------------------------------------------------------------


async def create_room(db: AsyncSession, data: RoomCreate) -> Room:
    """Create a new room. Validates room_type_id exists and room_number uniqueness."""
    # Validate room type exists
    room_type = await db.get(RoomType, data.room_type_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # Check unique room number
    existing = await db.execute(
        select(Room).where(Room.room_number == data.room_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists",
        )

    room = Room(
        room_number=data.room_number,
        floor=data.floor,
        room_type_id=data.room_type_id,
        notes=data.notes,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_room(db: AsyncSession, room_id: uuid.UUID) -> Room | None:
    """Get a room by ID with room_type eagerly loaded."""
    result = await db.execute(
        select(Room)
        .where(Room.id == room_id)
        .options(selectinload(Room.room_type))
    )
    return result.scalar_one_or_none()


async def get_rooms(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    floor: int | None = None,
    room_status: RoomStatus | None = None,
    room_type_id: uuid.UUID | None = None,
    active_only: bool = True,
) -> tuple[list[Room], int]:
    """List rooms with optional filters and pagination."""
    query = select(Room)
    count_query = select(func.count()).select_from(Room)

    if active_only:
        query = query.where(Room.is_active == True)  # noqa: E712
        count_query = count_query.where(Room.is_active == True)  # noqa: E712
    if floor is not None:
        query = query.where(Room.floor == floor)
        count_query = count_query.where(Room.floor == floor)
    if room_status is not None:
        query = query.where(Room.status == room_status)
        count_query = count_query.where(Room.status == room_status)
    if room_type_id is not None:
        query = query.where(Room.room_type_id == room_type_id)
        count_query = count_query.where(Room.room_type_id == room_type_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.offset(skip).limit(limit))
    items = list(result.scalars().all())

    return items, total


async def update_room(
    db: AsyncSession, room_id: uuid.UUID, data: RoomUpdate
) -> Room:
    """Update a room. Raises 404 if not found."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # If changing room_number, check uniqueness
    if "room_number" in update_data:
        existing = await db.execute(
            select(Room).where(
                Room.room_number == update_data["room_number"],
                Room.id != room_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists",
            )

    for field, value in update_data.items():
        setattr(room, field, value)

    await db.commit()
    await db.refresh(room)
    return room


async def delete_room(db: AsyncSession, room_id: uuid.UUID) -> None:
    """Soft-delete a room. Raises 404 if not found."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    room.is_active = False
    await db.commit()


# ---------------------------------------------------------------------------
# Status machine
# ---------------------------------------------------------------------------


async def transition_status(
    db: AsyncSession,
    room_id: uuid.UUID,
    new_status: RoomStatus,
    user_role: str,
    user_id: uuid.UUID,
    reason: str | None = None,
) -> Room:
    """Transition a room's status with role-based validation and audit logging.

    Args:
        db: Async database session.
        room_id: The room to transition.
        new_status: Target status.
        user_role: The role of the user performing the transition.
        user_id: The UUID of the user performing the transition.
        reason: Optional reason for the transition.

    Returns:
        The updated room.

    Raises:
        HTTPException 404: Room not found.
        HTTPException 403: Transition not allowed for this role.
    """
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # No-op if already at target status
    if room.status == new_status:
        return room

    # Check role permissions
    allowed = ROLE_TRANSITIONS.get(user_role)
    if allowed is not None:
        # Role has a restricted set of transitions
        if (room.status, new_status) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Transition not allowed for your role",
            )

    # Create audit log entry
    change = RoomStatusChange(
        room_id=room.id,
        from_status=room.status,
        to_status=new_status,
        changed_by=user_id,
        reason=reason,
    )
    db.add(change)

    # Apply transition
    room.status = new_status
    await db.commit()
    await db.refresh(room)
    return room


# ---------------------------------------------------------------------------
# Status board
# ---------------------------------------------------------------------------


async def get_status_board(db: AsyncSession) -> dict:
    """Build the status board: rooms grouped by floor with summary counts.

    Returns:
        Dict with 'floors' (list of floor groups) and 'summary' (status counts).
    """
    result = await db.execute(
        select(Room)
        .where(Room.is_active == True)  # noqa: E712
        .options(selectinload(Room.room_type))
        .order_by(Room.floor, Room.room_number)
    )
    rooms = result.scalars().all()

    # Group by floor
    floor_map: dict[int, list[dict]] = defaultdict(list)
    summary: dict[str, int] = defaultdict(int)

    for room in rooms:
        floor_map[room.floor].append(
            {
                "id": room.id,
                "room_number": room.room_number,
                "status": room.status.value,
                "room_type_name": room.room_type.name if room.room_type else "Unknown",
            }
        )
        summary[room.status.value] += 1

    floors = [
        {"floor": floor_num, "rooms": floor_rooms}
        for floor_num, floor_rooms in sorted(floor_map.items())
    ]

    return {"floors": floors, "summary": dict(summary)}


# ---------------------------------------------------------------------------
# Status history
# ---------------------------------------------------------------------------


async def get_status_history(
    db: AsyncSession, room_id: uuid.UUID, limit: int = 50
) -> list[RoomStatusChange]:
    """Return recent status changes for a room."""
    result = await db.execute(
        select(RoomStatusChange)
        .where(RoomStatusChange.room_id == room_id)
        .order_by(RoomStatusChange.changed_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
