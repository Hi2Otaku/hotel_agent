"""Add reservation_projections table and overbooking_pct column.

Revision ID: 002
Revises: 001
Create Date: 2026-03-21

Creates:
- reservation_projections table (booking event projection for availability queries)
- overbooking_pct column on room_types
- Composite index ix_reservation_proj_availability
- Partial index ix_reservation_proj_room_dates
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- reservation_projections ---
    op.create_table(
        "reservation_projections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column(
            "room_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("room_types.id"),
            nullable=False,
        ),
        sa.Column(
            "room_id",
            UUID(as_uuid=True),
            sa.ForeignKey("rooms.id"),
            nullable=True,
        ),
        sa.Column("check_in", sa.Date, nullable=False),
        sa.Column("check_out", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("guest_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Index on booking_id for fast lookup by booking
    op.create_index(
        "ix_reservation_projections_booking_id",
        "reservation_projections",
        ["booking_id"],
        unique=True,
    )

    # Composite index for availability queries: (room_type_id, check_in, check_out, status)
    op.create_index(
        "ix_reservation_proj_availability",
        "reservation_projections",
        ["room_type_id", "check_in", "check_out", "status"],
    )

    # Partial index for room-level date overlap (only when room_id assigned)
    op.execute(
        """
        CREATE INDEX ix_reservation_proj_room_dates
        ON reservation_projections (room_id, check_in, check_out)
        WHERE room_id IS NOT NULL
        """
    )

    # Add overbooking percentage to room_types
    op.add_column(
        "room_types",
        sa.Column(
            "overbooking_pct",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="0.00",
        ),
    )


def downgrade() -> None:
    op.drop_column("room_types", "overbooking_pct")
    op.drop_table("reservation_projections")
