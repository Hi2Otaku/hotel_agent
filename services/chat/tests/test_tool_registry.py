"""Tests for the tool registry with RBAC filtering and format conversion."""

import pytest

from app.services.tool_registry import ToolRegistry


@pytest.fixture
def registry():
    return ToolRegistry()


def test_guest_tools_count(registry):
    """Guest bot should have exactly 6 tools."""
    tools = registry.get_tools("guest")
    assert len(tools) == 6
    names = {t["name"] for t in tools}
    assert "search_rooms" in names
    assert "create_booking" in names
    assert "check_in_guest" not in names


def test_staff_tools_include_check_in(registry):
    """Staff bot (admin) should include check_in_guest and all guest tools."""
    tools = registry.get_tools("staff", "admin")
    names = {t["name"] for t in tools}
    assert "check_in_guest" in names
    assert "check_out_guest" in names
    assert "search_rooms" in names
    assert len(tools) == 12


def test_rbac_filters_by_role(registry):
    """Housekeeping role should get update_room_status but not check_in_guest."""
    tools = registry.get_tools("staff", "housekeeping")
    names = {t["name"] for t in tools}
    assert "update_room_status" in names
    assert "check_in_guest" not in names
    # Read-only staff tools (no role restriction) should still appear
    assert "get_occupancy_report" in names
    assert "lookup_guest" in names


def test_openai_format_wraps_in_function(registry):
    """OpenAI format should wrap tools in type/function structure."""
    tools = registry.get_tools("guest")
    openai_tools = registry.to_openai_format(tools)
    assert len(openai_tools) == len(tools)
    for t in openai_tools:
        assert t["type"] == "function"
        assert "function" in t
        assert "name" in t["function"]
        assert "description" in t["function"]
        assert "parameters" in t["function"]


def test_confirmation_required_on_write_tools(registry):
    """Write action tools must require confirmation."""
    tools = registry.get_tools("guest")
    write_tools = {"create_booking", "cancel_booking", "modify_booking"}
    for t in tools:
        if t["name"] in write_tools:
            assert t["requires_confirmation"] is True, f"{t['name']} should require confirmation"
        else:
            assert t["requires_confirmation"] is False, f"{t['name']} should not require confirmation"


def test_get_tool_by_name(registry):
    """get_tool should return a specific tool definition."""
    tool = registry.get_tool("search_rooms")
    assert tool["name"] == "search_rooms"
    assert "input_schema" in tool


def test_get_tool_unknown_raises(registry):
    """get_tool should raise KeyError for unknown tool names."""
    with pytest.raises(KeyError):
        registry.get_tool("nonexistent_tool")


def test_anthropic_format_strips_internal_keys(registry):
    """Anthropic format should only include name, description, input_schema."""
    tools = registry.get_tools("guest")
    anthropic_tools = registry.to_anthropic_format(tools)
    for t in anthropic_tools:
        assert set(t.keys()) == {"name", "description", "input_schema"}
