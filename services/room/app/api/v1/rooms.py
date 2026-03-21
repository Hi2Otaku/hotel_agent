"""Room CRUD + status transition + status board API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, require_manager_or_above, require_staff
from app.models.room import RoomStatus
from app.schemas.room import (
    RoomCreate,
    RoomDetailResponse,
    RoomListResponse,
    RoomResponse,
    RoomUpdate,
    StatusBoardResponse,
    StatusChangeResponse,
    StatusTransitionRequest,
)
from app.services.room import (
    create_room,
    delete_room,
    get_room,
    get_rooms,
    get_status_board,
    get_status_history,
    transition_status,
    update_room,
)

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room_endpoint(
    payload: RoomCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Create a new room."""
    return await create_room(db, payload)


@router.get("/list", response_model=RoomListResponse)
async def list_rooms_endpoint(
    skip: int = 0,
    limit: int = 50,
    floor: int | None = None,
    room_status: str | None = None,
    room_type_id: UUID | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """List rooms with optional filters and pagination."""
    # Convert string status to enum if provided
    status_enum = None
    if room_status is not None:
        try:
            status_enum = RoomStatus(room_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid room status: {room_status}",
            )

    items, total = await get_rooms(
        db,
        skip=skip,
        limit=limit,
        floor=floor,
        room_status=status_enum,
        room_type_id=room_type_id,
        active_only=active_only,
    )
    return RoomListResponse(items=items, total=total)


@router.get("/board", response_model=StatusBoardResponse)
async def status_board_endpoint(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Get the room status board grouped by floor."""
    return await get_status_board(db)


@router.get("/{room_id}", response_model=RoomDetailResponse)
async def get_room_endpoint(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Get a room by ID with room type details."""
    room = await get_room(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return room


@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room_endpoint(
    room_id: UUID,
    payload: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_manager_or_above),
):
    """Update a room."""
    return await update_room(db, room_id, payload)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_endpoint(
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Soft-delete a room."""
    await delete_room(db, room_id)
    return None


@router.post("/{room_id}/status", response_model=RoomResponse)
async def transition_status_endpoint(
    room_id: UUID,
    payload: StatusTransitionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Transition a room's status. Role-based validation in service layer."""
    try:
        new_status = RoomStatus(payload.new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {payload.new_status}",
        )

    return await transition_status(
        db,
        room_id=room_id,
        new_status=new_status,
        user_role=user["role"],
        user_id=UUID(user["sub"]),
        reason=payload.reason,
    )


@router.get("/{room_id}/status-history", response_model=list[StatusChangeResponse])
async def get_status_history_endpoint(
    room_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Get the status change history for a room."""
    return await get_status_history(db, room_id, limit=limit)
