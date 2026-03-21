"""Initial room service models.

Revision ID: 001
Revises: None
Create Date: 2026-03-21

Creates all 6 tables for the room service:
- room_types
- rooms
- base_rates
- seasonal_rates
- weekend_surcharges
- room_status_changes
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Room status enum values
ROOM_STATUS_VALUES = (
    "available",
    "occupied",
    "cleaning",
    "inspected",
    "maintenance",
    "out_of_order",
    "reserved",
)


def upgrade() -> None:
    # Create the room_status enum type
    room_status_enum = ENUM(
        *ROOM_STATUS_VALUES, name="room_status", create_type=False
    )
    room_status_enum.create(op.get_bind(), checkfirst=True)

    # --- room_types ---
    op.create_table(
        "room_types",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("max_adults", sa.Integer, nullable=False),
        sa.Column("max_children", sa.Integer, nullable=False, server_default="0"),
        sa.Column("bed_config", JSONB, nullable=False, server_default="[]"),
        sa.Column("amenities", JSONB, nullable=False, server_default="{}"),
        sa.Column("photo_urls", JSONB, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
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

    # --- rooms ---
    op.create_table(
        "rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("room_number", sa.String(10), unique=True, nullable=False),
        sa.Column("floor", sa.Integer, nullable=False),
        sa.Column(
            "room_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("room_types.id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            room_status_enum,
            server_default="available",
            nullable=False,
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
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
    op.create_index("ix_rooms_room_type_id", "rooms", ["room_type_id"])
    op.create_index("ix_rooms_status", "rooms", ["status"])

    # --- base_rates ---
    op.create_table(
        "base_rates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "room_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("room_types.id"),
            nullable=False,
        ),
        sa.Column("min_occupancy", sa.Integer, nullable=False, server_default="1"),
        sa.Column("max_occupancy", sa.Integer, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "currency", sa.String(3), nullable=False, server_default="USD"
        ),
    )
    op.create_index("ix_base_rates_room_type_id", "base_rates", ["room_type_id"])

    # --- seasonal_rates ---
    op.create_table(
        "seasonal_rates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "room_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("room_types.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("multiplier", sa.Numeric(4, 2), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )
    op.create_index(
        "ix_seasonal_rates_room_type_id", "seasonal_rates", ["room_type_id"]
    )

    # --- weekend_surcharges ---
    op.create_table(
        "weekend_surcharges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "room_type_id",
            UUID(as_uuid=True),
            sa.ForeignKey("room_types.id"),
            nullable=False,
        ),
        sa.Column("multiplier", sa.Numeric(4, 2), nullable=False),
        sa.Column("days", JSONB, nullable=False, server_default="[4, 5]"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
    )
    op.create_index(
        "ix_weekend_surcharges_room_type_id",
        "weekend_surcharges",
        ["room_type_id"],
    )

    # --- room_status_changes ---
    op.create_table(
        "room_status_changes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "room_id",
            UUID(as_uuid=True),
            sa.ForeignKey("rooms.id"),
            nullable=False,
        ),
        sa.Column("from_status", room_status_enum, nullable=True),
        sa.Column("to_status", room_status_enum, nullable=False),
        sa.Column("changed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_room_status_changes_room_id", "room_status_changes", ["room_id"]
    )


def downgrade() -> None:
    op.drop_table("room_status_changes")
    op.drop_table("weekend_surcharges")
    op.drop_table("seasonal_rates")
    op.drop_table("base_rates")
    op.drop_table("rooms")
    op.drop_table("room_types")

    # Drop the enum type
    ENUM(name="room_status").drop(op.get_bind(), checkfirst=True)
