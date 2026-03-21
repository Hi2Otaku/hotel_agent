"""Gateway BFF booking aggregation endpoints.

Enriches booking data by combining responses from the Booking service
and Room service. These endpoints add value beyond the raw proxy by
merging room type details (name, photos, amenities) into booking responses.
"""

import httpx
from fastapi import APIRouter, Request, Response

from app.core.config import settings

router = APIRouter(tags=["bookings"])


@router.get("/api/v1/bookings/{booking_id}/details")
async def booking_with_room_details(booking_id: str, request: Request):
    """Get a single booking enriched with room type details.

    Forwards the booking request to the Booking service, then fetches
    room type information from the Room service and merges the two.
    """
    auth_header = request.headers.get("authorization", "")
    headers = {"authorization": auth_header} if auth_header else {}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Fetch booking from Booking service
        booking_resp = await client.get(
            f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/{booking_id}",
            headers=headers,
        )

        if booking_resp.status_code != 200:
            return Response(
                content=booking_resp.content,
                status_code=booking_resp.status_code,
                media_type="application/json",
            )

        booking_data = booking_resp.json()

        # Enrich with room type details if available
        room_type_id = booking_data.get("room_type_id")
        room_details = {}
        if room_type_id:
            try:
                room_resp = await client.get(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/{room_type_id}",
                )
                if room_resp.status_code == 200:
                    room_data = room_resp.json()
                    room_details = {
                        "room_type_name": room_data.get("name"),
                        "room_type_description": room_data.get("description"),
                        "room_type_photos": room_data.get("photo_urls", room_data.get("photos", [])),
                        "room_type_amenities": room_data.get("amenities", []),
                    }
            except httpx.HTTPError:
                pass  # Graceful degradation -- return booking without room details

        import json
        result = {**booking_data, **room_details}
        return Response(
            content=json.dumps(result),
            status_code=200,
            media_type="application/json",
        )


@router.get("/api/v1/bookings/summary")
async def booking_summary_with_room_info(request: Request):
    """Get a list of bookings enriched with room type names.

    Forwards the list request to the Booking service, then batch-fetches
    room type names from the Room service for all unique room_type_ids.
    """
    auth_header = request.headers.get("authorization", "")
    headers = {"authorization": auth_header} if auth_header else {}

    # Forward query params
    query_string = str(request.url.query)
    booking_url = f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/"
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

        # Batch fetch unique room type names
        room_type_ids = {b.get("room_type_id") for b in items if b.get("room_type_id")}
        room_names: dict[str, str] = {}

        for rt_id in room_type_ids:
            try:
                room_resp = await client.get(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/{rt_id}",
                )
                if room_resp.status_code == 200:
                    room_names[rt_id] = room_resp.json().get("name", "Unknown")
            except httpx.HTTPError:
                pass  # Graceful degradation

        # Enrich each booking with room type name
        for item in items:
            rt_id = item.get("room_type_id")
            if rt_id and rt_id in room_names:
                item["room_type_name"] = room_names[rt_id]

        import json
        result = {**booking_data, "items": items}
        return Response(
            content=json.dumps(result),
            status_code=200,
            media_type="application/json",
        )
