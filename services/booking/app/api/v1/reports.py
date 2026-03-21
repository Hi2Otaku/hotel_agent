"""Staff-only reporting endpoints for the booking service.

Provides revenue breakdown, booking trends, and KPI summaries.
All data is pre-aggregated server-side -- no raw bookings are returned.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.services.reports import (
    get_booking_trends,
    get_kpi_summary,
    get_revenue_by_room_type,
)

router = APIRouter(prefix="/api/v1/bookings/staff/reports", tags=["staff-reports"])

require_staff = require_role("admin", "manager", "front_desk")


@router.get("/revenue")
async def revenue_report(
    start_date: date = Query(..., description="Inclusive start date"),
    end_date: date = Query(..., description="Exclusive end date"),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Revenue breakdown by room type and time period.

    Grouping is auto-computed from range length:
    - < 30 days: group by day
    - 30-90 days: group by week
    - > 90 days: group by month
    """
    range_days = (end_date - start_date).days
    if range_days < 30:
        group_by = "day"
    elif range_days <= 90:
        group_by = "week"
    else:
        group_by = "month"

    data = await get_revenue_by_room_type(db, start_date, end_date, group_by)
    return {"data": data, "group_by": group_by}


@router.get("/trends")
async def trends_report(
    start_date: date = Query(..., description="Inclusive start date"),
    end_date: date = Query(..., description="Inclusive end date"),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Daily booking creation counts for trend charts."""
    data = await get_booking_trends(db, start_date, end_date)
    return {"data": data}


@router.get("/kpis")
async def kpis_report(
    start_date: date = Query(..., description="Inclusive start date"),
    end_date: date = Query(..., description="Exclusive end date"),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """KPI summary: total revenue, total bookings, average daily rate."""
    data = await get_kpi_summary(db, start_date, end_date)
    return data
