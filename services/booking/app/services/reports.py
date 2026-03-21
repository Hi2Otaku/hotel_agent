"""Booking report aggregation queries.

Server-side aggregation for revenue, booking trends, and KPI summaries.
All monetary values returned as string-encoded Decimals (never float).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import case, cast, func, select, Date, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus

# Statuses that count as "real" bookings for revenue/occupancy
_ACTIVE_STATUSES = [
    BookingStatus.CONFIRMED,
    BookingStatus.CHECKED_IN,
    BookingStatus.CHECKED_OUT,
]


async def get_revenue_by_room_type(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    group_by: str = "day",
) -> list[dict]:
    """Aggregate revenue by room type and time period.

    Args:
        db: Async database session.
        start_date: Inclusive start date.
        end_date: Exclusive end date.
        group_by: Grouping granularity -- "day", "week", or "month".

    Returns:
        List of dicts with room_type_id, period, revenue (str), count.
    """
    period_expr = func.date_trunc(group_by, Booking.check_in)

    stmt = (
        select(
            cast(Booking.room_type_id, String).label("room_type_id"),
            period_expr.label("period"),
            func.sum(Booking.total_price).label("revenue"),
            func.count().label("count"),
        )
        .where(
            Booking.check_in >= start_date,
            Booking.check_in < end_date,
            Booking.status.in_(_ACTIVE_STATUSES),
        )
        .group_by(Booking.room_type_id, period_expr)
        .order_by(period_expr)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "room_type_id": row.room_type_id,
            "period": row.period.strftime("%Y-%m-%d") if row.period else None,
            "revenue": str(row.revenue) if row.revenue else "0.00",
            "count": row.count,
        }
        for row in rows
    ]


async def get_booking_trends(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> list[dict]:
    """Daily booking creation counts for trend charts.

    Args:
        db: Async database session.
        start_date: Inclusive start date.
        end_date: Inclusive end date.

    Returns:
        List of dicts with day (YYYY-MM-DD string) and value (int).
    """
    day_expr = cast(Booking.created_at, Date)

    stmt = (
        select(
            day_expr.label("day"),
            func.count().label("count"),
        )
        .where(
            day_expr >= start_date,
            day_expr <= end_date,
        )
        .group_by(day_expr)
        .order_by(day_expr)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "day": row.day.strftime("%Y-%m-%d") if row.day else None,
            "value": row.count,
        }
        for row in rows
    ]


async def get_kpi_summary(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> dict:
    """Compute KPI summary: total revenue, total bookings, average daily rate.

    All monetary values are string-encoded Decimals.
    """
    # Revenue and ADR from active bookings by check_in date
    revenue_stmt = select(
        func.coalesce(func.sum(Booking.total_price), Decimal("0.00")).label(
            "total_revenue"
        ),
        func.coalesce(func.avg(Booking.price_per_night), Decimal("0.00")).label(
            "avg_daily_rate"
        ),
    ).where(
        Booking.check_in >= start_date,
        Booking.check_in < end_date,
        Booking.status.in_(_ACTIVE_STATUSES),
    )

    # Total bookings by creation date
    bookings_stmt = select(func.count().label("total_bookings")).where(
        cast(Booking.created_at, Date) >= start_date,
        cast(Booking.created_at, Date) <= end_date,
    )

    rev_result = await db.execute(revenue_stmt)
    rev_row = rev_result.one()

    book_result = await db.execute(bookings_stmt)
    book_row = book_result.one()

    return {
        "total_revenue": str(rev_row.total_revenue),
        "total_bookings": book_row.total_bookings,
        "avg_daily_rate": str(
            round(Decimal(str(rev_row.avg_daily_rate)), 2)
        ),
    }
