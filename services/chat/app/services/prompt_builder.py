"""Dynamic system prompt builder for guest and staff chatbots.

Fetches live hotel data (room types, prices, amenities) and constructs
context-rich system prompts with hotel policies and bot personality.
"""

import logging
import time
from datetime import datetime, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache TTL: 1 hour
_CACHE_TTL = 3600


class PromptBuilder:
    """Builds system prompts with live hotel data and bot personality.

    Caches prompts per bot_type for 1 hour to avoid repeated room-service calls.
    """

    def __init__(self) -> None:
        self._cache: dict[str, tuple[str, float]] = {}

    async def build_system_prompt(self, bot_type: str, db=None) -> str:
        """Build the system prompt for the given bot type.

        Args:
            bot_type: Either "guest" or "staff".
            db: Database session (unused, reserved for future context queries).

        Returns:
            The complete system prompt string.
        """
        now = time.time()
        cached = self._cache.get(bot_type)
        if cached and (now - cached[1]) < _CACHE_TTL:
            return cached[0]

        room_types_section = await self._fetch_room_types()
        current_dt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        if bot_type == "staff":
            prompt = self._build_staff_prompt(room_types_section, current_dt)
        else:
            prompt = self._build_guest_prompt(room_types_section, current_dt)

        self._cache[bot_type] = (prompt, now)
        return prompt

    async def _fetch_room_types(self) -> str:
        """Fetch room types from room service and format as prompt section."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types"
                )
                resp.raise_for_status()
                room_types = resp.json()

            lines = []
            for rt in room_types:
                name = rt.get("name", "Unknown")
                price = rt.get("price_per_night", "N/A")
                capacity = rt.get("max_guests", "N/A")
                amenities = ", ".join(rt.get("amenities", [])[:5])
                lines.append(
                    f"- {name}: ${price}/night, up to {capacity} guests. "
                    f"Amenities: {amenities}"
                )
            return "\n".join(lines) if lines else "Room information temporarily unavailable."
        except Exception:
            logger.exception("Failed to fetch room types for prompt")
            return "Room information temporarily unavailable."

    def _build_guest_prompt(self, room_types: str, current_dt: str) -> str:
        """Build the guest bot system prompt."""
        return f"""You are HotelBook Assistant, a friendly and helpful hotel concierge. You help guests search rooms, make bookings, manage reservations, and answer questions. Always be warm and professional. When presenting room options, include key details like price, capacity, and top amenities. For write actions (booking, cancellation, modification), always ask for confirmation before proceeding. Respond in the same language the user writes in.

Current date and time: {current_dt}

Hotel Information:
- Hotel: HotelBook
- Check-in time: 3:00 PM
- Check-out time: 11:00 AM
- Amenities: Free WiFi, swimming pool, fitness gym, on-site restaurant

Room Types:
{room_types}

Cancellation Policy:
- Free cancellation up to 24 hours before check-in
- Late cancellation (within 24 hours) charges the first night's rate"""

    def _build_staff_prompt(self, room_types: str, current_dt: str) -> str:
        """Build the staff bot system prompt."""
        return f"""You are HB Ops, a professional hotel operations assistant. You help staff with check-ins, check-outs, room status management, guest lookups, and reports. Be concise and efficient. Respect the user's role permissions when suggesting actions. Respond in the same language the user writes in.

Current date and time: {current_dt}

Hotel Information:
- Hotel: HotelBook
- Check-in time: 3:00 PM
- Check-out time: 11:00 AM
- Amenities: Free WiFi, swimming pool, fitness gym, on-site restaurant

Room Types:
{room_types}

Cancellation Policy:
- Free cancellation up to 24 hours before check-in
- Late cancellation (within 24 hours) charges the first night's rate"""
