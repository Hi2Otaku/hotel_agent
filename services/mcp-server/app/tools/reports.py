"""Reporting tools for hotel occupancy and revenue data."""

import httpx
import os

BOOKING_SERVICE = os.getenv("BOOKING_SERVICE_URL", "http://booking:8000")


def register_report_tools(mcp):
    """Register reporting tools on the MCP server."""

    @mcp.tool()
    async def get_occupancy_report(date_from: str, date_to: str) -> str:
        """Get hotel occupancy rates for a date range. Returns daily occupancy percentages."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BOOKING_SERVICE}/api/v1/reports/occupancy",
                params={"date_from": date_from, "date_to": date_to},
            )
            return resp.text

    @mcp.tool()
    async def get_revenue_report(date_from: str, date_to: str) -> str:
        """Get hotel revenue summary for a date range."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BOOKING_SERVICE}/api/v1/reports/revenue",
                params={"date_from": date_from, "date_to": date_to},
            )
            return resp.text
