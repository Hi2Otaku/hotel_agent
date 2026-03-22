"""MCP server exposing read-only hotel tools via Streamable HTTP transport."""

from mcp.server.fastmcp import FastMCP

from app.tools.search import register_search_tools
from app.tools.booking import register_booking_tools
from app.tools.reports import register_report_tools

mcp = FastMCP("hotelbook", instructions="HotelBook hotel management read-only tools")

register_search_tools(mcp)
register_booking_tools(mcp)
register_report_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
