"""Tests for status board endpoint (RMGT-03)."""

import uuid

import pytest


def _unique_room_type(suffix: str) -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Board Type {suffix}-{uid}",
        "slug": f"board-type-{suffix}-{uid}",
        "description": "Test room type for board",
        "max_adults": 2,
        "max_children": 1,
        "bed_config": [{"type": "queen", "count": 1}],
        "amenities": {},
    }


async def test_status_board_returns_floors(client):
    """Status board should group rooms by floor."""
    rt_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("board"))
    room_type_id = rt_resp.json()["id"]

    # Create rooms on floor 1 and floor 2
    for floor, num in [(1, f"B1{uuid.uuid4().hex[:3]}"), (2, f"B2{uuid.uuid4().hex[:3]}")]:
        await client.post(
            "/api/v1/rooms/",
            json={"room_number": num, "floor": floor, "room_type_id": room_type_id},
        )

    resp = await client.get("/api/v1/rooms/board")
    assert resp.status_code == 200
    data = resp.json()
    assert "floors" in data
    assert "summary" in data
    floor_numbers = [f["floor"] for f in data["floors"]]
    assert 1 in floor_numbers or 2 in floor_numbers


async def test_status_board_summary_counts(client):
    """Summary should reflect status counts of created rooms."""
    rt_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("counts"))
    room_type_id = rt_resp.json()["id"]

    # Create 2 rooms (default status: available)
    for i in range(2):
        await client.post(
            "/api/v1/rooms/",
            json={
                "room_number": f"C{uuid.uuid4().hex[:4]}",
                "floor": 5,
                "room_type_id": room_type_id,
            },
        )

    resp = await client.get("/api/v1/rooms/board")
    assert resp.status_code == 200
    data = resp.json()
    summary = data["summary"]
    # At least 2 available rooms (may be more from other tests)
    assert summary.get("available", 0) >= 2
