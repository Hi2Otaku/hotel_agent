"""Tool executor that routes chatbot tool calls to internal service APIs.

Each tool maps to a specific internal API endpoint on the room, booking,
or auth service. The user's JWT is forwarded for downstream authorization.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Request timeout for internal API calls
_TIMEOUT = 10.0


class ToolExecutor:
    """Executes tool calls by routing them to internal microservice APIs.

    Args:
        auth_token: The user's JWT bearer token, forwarded to downstream services.
    """

    def __init__(self, auth_token: str) -> None:
        self._auth_token = auth_token
        self._headers = {"Authorization": f"Bearer {auth_token}"}

    async def execute(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool by calling the corresponding internal API.

        Args:
            tool_name: Name of the tool to execute.
            tool_input: Dict of tool input parameters.

        Returns:
            Dict with "success" (bool) and either "data" or "error".
        """
        try:
            handler = getattr(self, f"_execute_{tool_name}", None)
            if handler is None:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
            return await handler(tool_input)
        except httpx.TimeoutException:
            logger.warning("Timeout executing tool %s", tool_name)
            return {"success": False, "error": f"Request timed out while executing {tool_name}"}
        except Exception as e:
            logger.exception("Error executing tool %s", tool_name)
            return {"success": False, "error": str(e)}

    async def _execute_search_rooms(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.ROOM_SERVICE_URL}/api/v1/search/availability",
                params={
                    "check_in": inp["check_in"],
                    "check_out": inp["check_out"],
                    "guests": inp["guests"],
                },
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_get_room_details(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/{inp['room_type_id']}",
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_check_booking_status(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/confirm/{inp['confirmation_number']}",
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_create_booking(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/",
                json={
                    "room_type_id": inp["room_type_id"],
                    "check_in": inp["check_in"],
                    "check_out": inp["check_out"],
                    "guests": inp["guests"],
                    "guest_name": inp["guest_name"],
                    "guest_email": inp["guest_email"],
                },
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_cancel_booking(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/{inp['booking_id']}/cancel",
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_modify_booking(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.put(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/{inp['booking_id']}",
                json={
                    "new_check_in": inp["new_check_in"],
                    "new_check_out": inp["new_check_out"],
                },
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_check_in_guest(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/staff/bookings/{inp['booking_id']}/check-in",
                json={"room_id": inp["room_id"]},
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_check_out_guest(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/staff/bookings/{inp['booking_id']}/check-out",
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_update_room_status(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.patch(
                f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/{inp['room_id']}/status",
                json={"status": inp["new_status"]},
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_get_occupancy_report(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/reports/occupancy",
                params={"date_from": inp["date_from"], "date_to": inp["date_to"]},
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_get_revenue_report(self, inp: dict) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.BOOKING_SERVICE_URL}/api/v1/reports/revenue",
                params={"date_from": inp["date_from"], "date_to": inp["date_to"]},
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}

    async def _execute_lookup_guest(self, inp: dict) -> dict:
        params = {}
        if inp.get("email"):
            params["q"] = inp["email"]
        elif inp.get("name"):
            params["q"] = inp["name"]
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/users/search",
                params=params,
                headers=self._headers,
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
