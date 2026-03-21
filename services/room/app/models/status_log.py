"""RoomStatusChange audit log model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.room import RoomStatus


class RoomStatusChange(Base):
    """Audit trail for room status transitions."""

    __tablename__ = "room_status_changes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id"),
        nullable=False,
    )
    from_status: Mapped[RoomStatus | None] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=False,
             values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    to_status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=False,
             values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    room = relationship("Room", back_populates="status_history")
