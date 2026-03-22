"""Search tools for querying room availability and details."""

import httpx
import os

ROOM_SERVICE = os.getenv("ROOM_SERVICE_URL", "http://room:8000")


def register_search_tools(mcp):
    """Register room search tools on the MCP server."""

    @mcp.tool()
    async def search_rooms(check_in: str, check_out: str, guests: int) -> str:
        """Search available hotel rooms for given dates and guest count. Returns room types with prices and availability."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{ROOM_SERVICE}/api/v1/search/availability",
                params={
                    "check_in": check_in,
                    "check_out": check_out,
                    "guests": guests,
                },
            )
            return resp.text

    @mcp.tool()
    async def get_room_types() -> str:
        """List all room types with amenities, capacity, and base prices."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{ROOM_SERVICE}/api/v1/rooms/types")
            return resp.text

    @mcp.tool()
    async def get_room_details(room_type_id: str) -> str:
        """Get detailed information about a specific room type including photos and amenities."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{ROOM_SERVICE}/api/v1/rooms/types/{room_type_id}"
            )
            return resp.text
