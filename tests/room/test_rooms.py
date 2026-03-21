"""Tests for room CRUD endpoints (RMGT-02)."""

import uuid

import pytest

from tests.room.conftest import make_mock_user, ROOM_TEST_DB_URL

SAMPLE_ROOM_TYPE = {
    "name": "Standard Double",
    "slug": "standard-double",
    "description": "Standard room with double bed",
    "max_adults": 2,
    "max_children": 1,
    "bed_config": [{"type": "double", "count": 1}],
    "amenities": {"Comfort": ["AC"]},
}


def _unique_room_type(suffix: str) -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        **SAMPLE_ROOM_TYPE,
        "name": f"Room Type {suffix}-{uid}",
        "slug": f"room-type-{suffix}-{uid}",
    }


async def _create_room_type(client) -> str:
    """Helper: create a room type and return its ID."""
    resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("rooms"))
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_room(client):
    room_type_id = await _create_room_type(client)
    room_number = f"R{uuid.uuid4().hex[:4]}"
    resp = await client.post(
        "/api/v1/rooms/",
        json={"room_number": room_number, "floor": 1, "room_type_id": room_type_id},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["room_number"] == room_number
    assert data["floor"] == 1
    assert data["status"] == "available"


async def test_create_room_duplicate_number(client):
    room_type_id = await _create_room_type(client)
    room_number = f"D{uuid.uuid4().hex[:4]}"
    resp1 = await client.post(
        "/api/v1/rooms/",
        json={"room_number": room_number, "floor": 1, "room_type_id": room_type_id},
    )
    assert resp1.status_code == 201
    resp2 = await client.post(
        "/api/v1/rooms/",
        json={"room_number": room_number, "floor": 2, "room_type_id": room_type_id},
    )
    assert resp2.status_code == 409


async def test_list_rooms(client):
    room_type_id = await _create_room_type(client)
    for i in range(2):
        await client.post(
            "/api/v1/rooms/",
            json={
                "room_number": f"L{uuid.uuid4().hex[:4]}",
                "floor": 1,
                "room_type_id": room_type_id,
            },
        )
    resp = await client.get("/api/v1/rooms/list")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


async def test_list_rooms_filter_by_floor(client):
    room_type_id = await _create_room_type(client)
    # Create rooms on different floors
    await client.post(
        "/api/v1/rooms/",
        json={
            "room_number": f"F{uuid.uuid4().hex[:4]}",
            "floor": 10,
            "room_type_id": room_type_id,
        },
    )
    resp = await client.get("/api/v1/rooms/list?floor=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(r["floor"] == 10 for r in data["items"])


async def test_get_room_by_id(client):
    room_type_id = await _create_room_type(client)
    create_resp = await client.post(
        "/api/v1/rooms/",
        json={
            "room_number": f"G{uuid.uuid4().hex[:4]}",
            "floor": 1,
            "room_type_id": room_type_id,
        },
    )
    room_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/rooms/{room_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == room_id


async def test_update_room(client):
    room_type_id = await _create_room_type(client)
    create_resp = await client.post(
        "/api/v1/rooms/",
        json={
            "room_number": f"U{uuid.uuid4().hex[:4]}",
            "floor": 1,
            "room_type_id": room_type_id,
        },
    )
    room_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/rooms/{room_id}",
        json={"notes": "Renovated 2024"},
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Renovated 2024"


async def test_delete_room(client):
    room_type_id = await _create_room_type(client)
    create_resp = await client.post(
        "/api/v1/rooms/",
        json={
            "room_number": f"X{uuid.uuid4().hex[:4]}",
            "floor": 1,
            "room_type_id": room_type_id,
        },
    )
    room_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/rooms/{room_id}")
    assert resp.status_code == 204
