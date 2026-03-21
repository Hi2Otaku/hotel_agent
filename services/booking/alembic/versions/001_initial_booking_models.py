"""Initial booking and payment tables.

Revision ID: 001
Revises: None
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

# Enum values matching BookingStatus
BOOKING_STATUSES = ("pending", "confirmed", "checked_in", "checked_out", "cancelled", "no_show")


def upgrade() -> None:
    """Create booking_status enum, bookings table, and payment_transactions table."""

    # Create the enum type
    booking_status_enum = ENUM(
        *BOOKING_STATUSES, name="booking_status", create_type=False
    )
    booking_status_enum.create(op.get_bind(), checkfirst=True)

    # Create bookings table
    op.create_table(
        "bookings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("confirmation_number", sa.String(20), unique=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("room_type_id", UUID(as_uuid=True), nullable=False),
        sa.Column("room_id", UUID(as_uuid=True), nullable=True),
        sa.Column("check_in", sa.Date, nullable=False),
        sa.Column("check_out", sa.Date, nullable=False),
        sa.Column("guest_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "status",
            booking_status_enum,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_per_night", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("nightly_breakdown", JSONB, nullable=True),
        sa.Column("guest_first_name", sa.String(100), nullable=True),
        sa.Column("guest_last_name", sa.String(100), nullable=True),
        sa.Column("guest_email", sa.String(255), nullable=True),
        sa.Column("guest_phone", sa.String(50), nullable=True),
        sa.Column("guest_address", sa.Text, nullable=True),
        sa.Column("special_requests", sa.Text, nullable=True),
        sa.Column("id_document", sa.String(100), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String(50), nullable=True),
        sa.Column("cancellation_fee", sa.Numeric(10, 2), nullable=True),
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

    # Indexes for bookings
    op.create_index("ix_bookings_confirmation_number", "bookings", ["confirmation_number"], unique=True)
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])

    # Create payment_transactions table
    op.create_table(
        "payment_transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", sa.String(50), unique=True, nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("card_last_four", sa.String(4), nullable=False),
        sa.Column("card_brand", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("decline_reason", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Indexes for payment_transactions
    op.create_index("ix_payment_transactions_booking_id", "payment_transactions", ["booking_id"])
    op.create_index("ix_payment_transactions_transaction_id", "payment_transactions", ["transaction_id"], unique=True)


def downgrade() -> None:
    """Drop payment_transactions, bookings, and booking_status enum."""
    op.drop_table("payment_transactions")
    op.drop_table("bookings")
    ENUM(name="booking_status").drop(op.get_bind(), checkfirst=True)
