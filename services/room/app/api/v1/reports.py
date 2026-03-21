"""Room service reporting endpoints -- occupancy aggregation.

Uses the reservation_projections table (synced via RabbitMQ events)
to compute daily occupancy without calling the booking service at runtime.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.models.reservation import ReservationProjection
from app.models.room import Room

router = APIRouter(prefix="/api/v1/rooms/reports", tags=["room-reports"])

require_staff = require_role("admin", "manager", "front_desk")

# Statuses that count as occupying a room
_ACTIVE_STATUSES = ["confirmed", "checked_in", "checked_out"]


@router.get("/occupancy")
async def occupancy_report(
    start_date: date = Query(..., description="Inclusive start date"),
    end_date: date = Query(..., description="Inclusive end date"),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Daily occupancy percentages for the given date range.

    A reservation overlaps day D if check_in <= D AND check_out > D.
    Occupancy = overlapping reservations / total rooms * 100.

    Returns:
        daily: list of {day: YYYY-MM-DD, value: float} for Nivo charts.
        total_rooms: int total room count.
        avg_occupancy: float average occupancy across the range.
    """
    # Total room count
    total_rooms_result = await db.execute(select(func.count()).select_from(Room))
    total_rooms = total_rooms_result.scalar() or 0

    if total_rooms == 0:
        return {"daily": [], "total_rooms": 0, "avg_occupancy": 0.0}

    # Iterate days in range and count overlapping reservations
    daily = []
    current = start_date
    while current <= end_date:
        overlap_stmt = select(func.count()).select_from(ReservationProjection).where(
            and_(
                ReservationProjection.check_in <= current,
                ReservationProjection.check_out > current,
                ReservationProjection.status.in_(_ACTIVE_STATUSES),
            )
        )
        overlap_result = await db.execute(overlap_stmt)
        overlap_count = overlap_result.scalar() or 0

        pct = round(overlap_count / total_rooms * 100, 1)
        daily.append({
            "day": current.strftime("%Y-%m-%d"),
            "value": pct,
        })
        current += timedelta(days=1)

    avg_occupancy = round(
        sum(d["value"] for d in daily) / len(daily), 1
    ) if daily else 0.0

    return {
        "daily": daily,
        "total_rooms": total_rooms,
        "avg_occupancy": avg_occupancy,
    }
