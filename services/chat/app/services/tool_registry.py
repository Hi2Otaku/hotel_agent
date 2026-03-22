"""Tool registry for guest and staff chatbot tool definitions.

Defines available tools with RBAC filtering and provider format conversion.
Tools are stored in a provider-agnostic format; each LLM provider converts
format internally. The to_anthropic_format/to_openai_format methods are
utility helpers for testing or direct API usage outside the ChatEngine.
"""

from copy import deepcopy


# ---------- Tool definitions ----------

_GUEST_TOOLS: list[dict] = [
    {
        "name": "search_rooms",
        "description": "Search available rooms by date range and guest count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                "guests": {"type": "integer", "description": "Number of guests"},
            },
            "required": ["check_in", "check_out", "guests"],
        },
        "requires_confirmation": False,
        "staff_only": False,
        "allowed_roles": None,
    },
    {
        "name": "get_room_details",
        "description": "Get detailed information for a specific room type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_type_id": {"type": "string", "description": "Room type UUID"},
            },
            "required": ["room_type_id"],
        },
        "requires_confirmation": False,
        "staff_only": False,
        "allowed_roles": None,
    },
    {
        "name": "check_booking_status",
        "description": "Check the status of a booking by confirmation number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "confirmation_number": {"type": "string", "description": "Booking confirmation number (e.g. HB-XXXXXX)"},
            },
            "required": ["confirmation_number"],
        },
        "requires_confirmation": False,
        "staff_only": False,
        "allowed_roles": None,
    },
    {
        "name": "create_booking",
        "description": "Create a new room booking. Requires confirmation before execution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_type_id": {"type": "string", "description": "Room type UUID"},
                "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                "guests": {"type": "integer", "description": "Number of guests"},
                "guest_name": {"type": "string", "description": "Guest full name"},
                "guest_email": {"type": "string", "description": "Guest email address"},
            },
            "required": ["room_type_id", "check_in", "check_out", "guests", "guest_name", "guest_email"],
        },
        "requires_confirmation": True,
        "staff_only": False,
        "allowed_roles": None,
    },
    {
        "name": "cancel_booking",
        "description": "Cancel an existing booking. Requires confirmation before execution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking UUID"},
            },
            "required": ["booking_id"],
        },
        "requires_confirmation": True,
        "staff_only": False,
        "allowed_roles": None,
    },
    {
        "name": "modify_booking",
        "description": "Modify booking dates. Requires confirmation before execution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking UUID"},
                "new_check_in": {"type": "string", "description": "New check-in date (YYYY-MM-DD)"},
                "new_check_out": {"type": "string", "description": "New check-out date (YYYY-MM-DD)"},
            },
            "required": ["booking_id", "new_check_in", "new_check_out"],
        },
        "requires_confirmation": True,
        "staff_only": False,
        "allowed_roles": None,
    },
]


_STAFF_ONLY_TOOLS: list[dict] = [
    {
        "name": "check_in_guest",
        "description": "Check in a guest by booking ID and room ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking UUID"},
                "room_id": {"type": "string", "description": "Room UUID to assign"},
            },
            "required": ["booking_id", "room_id"],
        },
        "requires_confirmation": True,
        "staff_only": True,
        "allowed_roles": ["admin", "manager", "front_desk"],
    },
    {
        "name": "check_out_guest",
        "description": "Check out a guest by booking ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "Booking UUID"},
            },
            "required": ["booking_id"],
        },
        "requires_confirmation": True,
        "staff_only": True,
        "allowed_roles": ["admin", "manager", "front_desk"],
    },
    {
        "name": "update_room_status",
        "description": "Update a room's status (e.g. cleaning, maintenance, available).",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string", "description": "Room UUID"},
                "new_status": {"type": "string", "description": "New status value"},
            },
            "required": ["room_id", "new_status"],
        },
        "requires_confirmation": True,
        "staff_only": True,
        "allowed_roles": ["admin", "manager", "front_desk", "housekeeping"],
    },
    {
        "name": "get_occupancy_report",
        "description": "Get occupancy report for a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            },
            "required": ["date_from", "date_to"],
        },
        "requires_confirmation": False,
        "staff_only": True,
        "allowed_roles": None,
    },
    {
        "name": "get_revenue_report",
        "description": "Get revenue report for a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            },
            "required": ["date_from", "date_to"],
        },
        "requires_confirmation": False,
        "staff_only": True,
        "allowed_roles": None,
    },
    {
        "name": "lookup_guest",
        "description": "Search for a guest by email or name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Guest email to search"},
                "name": {"type": "string", "description": "Guest name to search"},
            },
            "required": [],
        },
        "requires_confirmation": False,
        "staff_only": True,
        "allowed_roles": None,
    },
]


class ToolRegistry:
    """Registry of available tools for guest and staff chatbots.

    Tools are stored in a provider-agnostic format. The get_tools method
    filters by bot_type and RBAC role.
    """

    def __init__(self) -> None:
        self._tools: dict[str, dict] = {}
        for tool in _GUEST_TOOLS + _STAFF_ONLY_TOOLS:
            self._tools[tool["name"]] = tool

    def get_tools(self, bot_type: str, user_role: str | None = None) -> list[dict]:
        """Return tool list filtered by bot_type and user RBAC role.

        Args:
            bot_type: "guest" or "staff".
            user_role: The user's role (e.g. "admin", "front_desk").
                       Required for staff bot to filter role-gated tools.

        Returns:
            List of tool definitions the user is allowed to use.
        """
        tools = []
        for tool in self._tools.values():
            if bot_type == "guest" and tool["staff_only"]:
                continue
            if tool["staff_only"] and tool["allowed_roles"] is not None:
                if user_role not in tool["allowed_roles"]:
                    continue
            tools.append(deepcopy(tool))
        return tools

    def get_tool(self, name: str) -> dict:
        """Return a single tool definition by name.

        Args:
            name: Tool name.

        Returns:
            The tool definition dict.

        Raises:
            KeyError: If the tool name is not registered.
        """
        return self._tools[name]

    def to_anthropic_format(self, tools: list[dict]) -> list[dict]:
        """Convert tools to Anthropic API format (native, no-op).

        Anthropic uses name/description/input_schema natively, so this
        returns the tools as-is (stripping internal-only keys).
        """
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["input_schema"],
            }
            for t in tools
        ]

    def to_openai_format(self, tools: list[dict]) -> list[dict]:
        """Convert tools to OpenAI function-calling format.

        Wraps each tool in {"type":"function","function":{...}} structure.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]
