"""Gateway BFF staff endpoints.

Orchestrates check-in/check-out across booking + room services,
provides overview aggregation, guest search, and guest profile endpoints.
"""

import asyncio
import json
import logging

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["staff-bff"])


def _auth_headers(request: Request) -> dict[str, str]:
    """Extract authorization header from incoming request."""
    auth_header = request.headers.get("authorization", "")
    return {"authorization": auth_header} if auth_header else {}


@router.post("/api/v1/staff/check-in/{booking_id}")
async def staff_check_in(booking_id: str, request: Request):
    """Orchestrate guest check-in across booking and room services.

    Step 1: Check in the booking (assign room, transition to checked_in).
    Step 2: Update room status to 'occupied' (graceful degradation if fails).
    """
    headers = _auth_headers(request)
    body = await request.json()
    room_id = body.get("room_id")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Check in via booking service
        booking_resp = await client.post(
            f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/{booking_id}/check-in",
            json={"room_id": room_id},
            headers=headers,
        )

        if booking_resp.status_code != 200:
            return Response(
                content=booking_resp.content,
                status_code=booking_resp.status_code,
                media_type="application/json",
            )

        # Step 2: Update room status to occupied (graceful degradation)
        if room_id:
            try:
                await client.post(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/{room_id}/status",
                    json={"new_status": "occupied"},
                    headers=headers,
                )
            except httpx.HTTPError:
                logger.warning("Failed to update room %s status to occupied", room_id)

        return Response(
            content=booking_resp.content,
            status_code=200,
            media_type="application/json",
        )


@router.post("/api/v1/staff/check-out/{booking_id}")
async def staff_check_out(booking_id: str, request: Request):
    """Orchestrate guest check-out across booking and room services.

    Step 1: Check out the booking (transition to checked_out).
    Step 2: Update room status to 'cleaning' (graceful degradation if fails).
    """
    headers = _auth_headers(request)

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Check out via booking service
        booking_resp = await client.post(
            f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/{booking_id}/check-out",
            headers=headers,
        )

        if booking_resp.status_code != 200:
            return Response(
                content=booking_resp.content,
                status_code=booking_resp.status_code,
                media_type="application/json",
            )

        # Step 2: Update room status to cleaning (graceful degradation)
        booking_data = booking_resp.json()
        room_id = booking_data.get("room_id")

        if room_id:
            try:
                await client.post(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/{room_id}/status",
                    json={"new_status": "cleaning"},
                    headers=headers,
                )
            except httpx.HTTPError:
                logger.warning("Failed to update room %s status to cleaning", room_id)

        return Response(
            content=booking_resp.content,
            status_code=200,
            media_type="application/json",
        )


@router.get("/api/v1/staff/overview")
async def staff_overview(request: Request):
    """Aggregate staff overview with today's bookings and room status.

    Fetches today's bookings and room board in parallel, then computes
    arrival/departure counts and occupancy metrics.
    """
    headers = _auth_headers(request)

    async with httpx.AsyncClient(timeout=15.0) as client:

        async def fetch_today():
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/today",
                headers=headers,
            )
            return resp.json() if resp.status_code == 200 else {"arrivals": [], "departures": []}

        async def fetch_rooms():
            resp = await client.get(
                f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/",
                headers=headers,
            )
            return resp.json() if resp.status_code == 200 else []

        today_data, rooms_data = await asyncio.gather(fetch_today(), fetch_rooms())

    arrivals = today_data.get("arrivals", [])
    departures = today_data.get("departures", [])

    # Build room_id -> room_number lookup from rooms data
    rooms_list = rooms_data if isinstance(rooms_data, list) else rooms_data.get("items", [])
    room_number_map: dict[str, str] = {}
    for r in rooms_list:
        rid = r.get("id")
        rnum = r.get("room_number")
        if rid and rnum:
            room_number_map[str(rid)] = rnum

    # Enrich bookings with room_number
    for booking in arrivals + departures:
        room_id = booking.get("room_id")
        if room_id and str(room_id) in room_number_map:
            booking["room_number"] = room_number_map[str(room_id)]

    # Room metrics
    total_rooms = len(rooms_list)
    occupied_rooms = sum(1 for r in rooms_list if r.get("status") == "occupied")
    rooms_to_clean = sum(1 for r in rooms_list if r.get("status") == "cleaning")
    occupancy_percent = round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 1)

    result = {
        "arrivals_count": len(arrivals),
        "departures_count": len(departures),
        "occupancy_percent": occupancy_percent,
        "rooms_to_clean": rooms_to_clean,
        "arrivals": arrivals,
        "departures": departures,
    }

    return Response(
        content=json.dumps(result),
        status_code=200,
        media_type="application/json",
    )


@router.get("/api/v1/staff/guests/search")
async def staff_guest_search(request: Request):
    """Forward guest search to auth service."""
    headers = _auth_headers(request)
    query_string = str(request.url.query)

    async with httpx.AsyncClient(timeout=15.0) as client:
        url = f"{settings.AUTH_SERVICE_URL}/api/v1/users/search"
        if query_string:
            url += f"?{query_string}"

        resp = await client.get(url, headers=headers)

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type="application/json",
        )


@router.get("/api/v1/staff/guests/{user_id}/profile")
async def staff_guest_profile(user_id: str, request: Request):
    """Aggregate guest profile from auth service and booking history.

    Fetches user details and booking history in parallel, merging into
    a single response. Gracefully degrades if booking service is unavailable.
    """
    headers = _auth_headers(request)

    async with httpx.AsyncClient(timeout=15.0) as client:

        async def fetch_user():
            resp = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/users/{user_id}",
                headers=headers,
            )
            if resp.status_code == 200:
                return resp.json()
            return None

        async def fetch_bookings():
            try:
                resp = await client.get(
                    f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/by-user/{user_id}",
                    headers=headers,
                )
                if resp.status_code == 200:
                    return resp.json()
            except httpx.HTTPError:
                logger.warning("Failed to fetch bookings for user %s", user_id)
            return {"items": [], "total": 0}

        user_data, bookings_data = await asyncio.gather(fetch_user(), fetch_bookings())

    if user_data is None:
        return Response(
            content=json.dumps({"detail": "User not found"}),
            status_code=404,
            media_type="application/json",
        )

    result = {
        "user": user_data,
        "bookings": bookings_data,
    }

    return Response(
        content=json.dumps(result),
        status_code=200,
        media_type="application/json",
    )


@router.get("/api/v1/bookings/staff/")
async def staff_bookings_enriched(request: Request):
    """Forward staff bookings list and enrich with room_number from room service.

    Fetches the booking list from the Booking service, then batch-fetches
    room details for bookings that have a room_id to add human-readable
    room_number to the response.
    """
    headers = _auth_headers(request)
    query_string = str(request.url.query)

    booking_url = f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/"
    if query_string:
        booking_url += f"?{query_string}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        booking_resp = await client.get(booking_url, headers=headers)

        if booking_resp.status_code != 200:
            return Response(
                content=booking_resp.content,
                status_code=booking_resp.status_code,
                media_type="application/json",
            )

        booking_data = booking_resp.json()
        items = booking_data.get("items", [])

        # Collect unique room_ids that need room_number lookup
        room_ids = {
            b.get("room_id") for b in items
            if b.get("room_id")
        }

        # Also enrich with room_type_name
        room_type_ids = {
            b.get("room_type_id") for b in items
            if b.get("room_type_id")
        }

        room_number_map: dict[str, str] = {}
        room_type_names: dict[str, str] = {}

        # Batch fetch room details for room_number
        for rid in room_ids:
            try:
                resp = await client.get(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/{rid}",
                    headers=headers,
                )
                if resp.status_code == 200:
                    room_data = resp.json()
                    room_number_map[rid] = room_data.get("room_number", "")
            except httpx.HTTPError:
                pass

        # Batch fetch room type names
        for rt_id in room_type_ids:
            try:
                resp = await client.get(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/{rt_id}",
                )
                if resp.status_code == 200:
                    room_type_names[rt_id] = resp.json().get("name", "Unknown")
            except httpx.HTTPError:
                pass

        # Enrich items
        for item in items:
            rid = item.get("room_id")
            if rid and rid in room_number_map:
                item["room_number"] = room_number_map[rid]
            rt_id = item.get("room_type_id")
            if rt_id and rt_id in room_type_names:
                item["room_type_name"] = room_type_names[rt_id]

    return Response(
        content=json.dumps({**booking_data, "items": items}),
        status_code=200,
        media_type="application/json",
    )
