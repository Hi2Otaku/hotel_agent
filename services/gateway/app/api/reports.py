"""Gateway BFF reports endpoint.

Orchestrates parallel fetches from booking and room services to build
a unified report payload for the staff dashboard.
"""

import asyncio
import json
import logging

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reports-bff"])


def _auth_headers(request: Request) -> dict[str, str]:
    """Extract authorization header from incoming request."""
    auth_header = request.headers.get("authorization", "")
    return {"authorization": auth_header} if auth_header else {}


@router.get("/api/v1/staff/reports")
async def staff_reports(request: Request):
    """Aggregate all report data from backend services.

    Fetches occupancy, revenue, trends, and KPIs in parallel.
    Returns merged JSON with graceful degradation per sub-call.

    Query params forwarded as-is: start_date, end_date.
    """
    headers = _auth_headers(request)
    query_string = str(request.url.query)

    async with httpx.AsyncClient(timeout=30.0) as client:

        async def fetch_occupancy() -> dict:
            try:
                url = f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/reports/occupancy"
                if query_string:
                    url += f"?{query_string}"
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
            except httpx.HTTPError:
                logger.warning("Failed to fetch occupancy report")
            return {"daily": [], "total_rooms": 0, "avg_occupancy": 0.0}

        async def fetch_revenue() -> dict:
            try:
                url = f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/reports/revenue"
                if query_string:
                    url += f"?{query_string}"
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
            except httpx.HTTPError:
                logger.warning("Failed to fetch revenue report")
            return {"data": [], "group_by": "day"}

        async def fetch_trends() -> dict:
            try:
                url = f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/reports/trends"
                if query_string:
                    url += f"?{query_string}"
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
            except httpx.HTTPError:
                logger.warning("Failed to fetch trends report")
            return {"data": []}

        async def fetch_kpis() -> dict:
            try:
                url = f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/reports/kpis"
                if query_string:
                    url += f"?{query_string}"
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
            except httpx.HTTPError:
                logger.warning("Failed to fetch KPI report")
            return {"total_revenue": "0.00", "total_bookings": 0, "avg_daily_rate": "0.00"}

        occupancy, revenue, trends, kpis = await asyncio.gather(
            fetch_occupancy(),
            fetch_revenue(),
            fetch_trends(),
            fetch_kpis(),
        )

    result = {
        "occupancy": occupancy,
        "revenue": revenue,
        "trends": trends,
        "kpis": kpis,
    }

    return Response(
        content=json.dumps(result),
        status_code=200,
        media_type="application/json",
    )
