"""Booking tools for checking reservation status."""

import httpx
import os

BOOKING_SERVICE = os.getenv("BOOKING_SERVICE_URL", "http://booking:8000")


def register_booking_tools(mcp):
    """Register booking lookup tools on the MCP server."""

    @mcp.tool()
    async def check_booking_status(confirmation_number: str) -> str:
        """Look up a booking by its confirmation number (e.g., HB-XXXXXX)."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BOOKING_SERVICE}/api/v1/bookings/confirm/{confirmation_number}"
            )
            return resp.text
