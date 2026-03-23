"""Tests for room type CRUD endpoints (RMGT-01)."""

import uuid

import pytest

from app.api.deps import get_current_user
from app.main import app
from .conftest import make_mock_user

SAMPLE_ROOM_TYPE = {
    "name": "Ocean View Suite",
    "slug": "ocean-view-suite",
    "description": "Spacious suite with ocean panorama",
    "max_adults": 2,
    "max_children": 2,
    "bed_config": [{"type": "king", "count": 1}],
    "amenities": {"Comfort": ["AC", "Mini Bar"], "Tech": ["WiFi", "Smart TV"]},
}


def _unique_room_type(suffix: str | None = None) -> dict:
    """Generate a unique room type payload."""
    uid = suffix or uuid.uuid4().hex[:8]
    return {
        **SAMPLE_ROOM_TYPE,
        "name": f"Test Room Type {uid}",
        "slug": f"test-room-type-{uid}",
    }


async def test_create_room_type(client):
    payload = _unique_room_type("create")
    resp = await client.post("/api/v1/rooms/types", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["slug"] == payload["slug"]
    assert data["amenities"] == payload["amenities"]
    assert data["bed_config"] == payload["bed_config"]
    assert data["is_active"] is True


async def test_create_room_type_duplicate_name(client):
    payload = _unique_room_type("dup")
    resp1 = await client.post("/api/v1/rooms/types", json=payload)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/rooms/types", json=payload)
    assert resp2.status_code == 409


async def test_list_room_types(client):
    await client.post("/api/v1/rooms/types", json=_unique_room_type("list1"))
    await client.post("/api/v1/rooms/types", json=_unique_room_type("list2"))
    resp = await client.get("/api/v1/rooms/types")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


async def test_get_room_type_by_id(client):
    create_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("getid"))
    room_type_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/rooms/types/{room_type_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == room_type_id


async def test_update_room_type(client):
    create_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("upd"))
    room_type_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/rooms/types/{room_type_id}",
        json={"name": f"Updated Name {uuid.uuid4().hex[:6]}"},
    )
    assert resp.status_code == 200
    assert "Updated Name" in resp.json()["name"]


async def test_delete_room_type(client):
    create_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("del"))
    room_type_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/rooms/types/{room_type_id}")
    assert resp.status_code == 204

    # Verify it's gone from active list (get by id should still work but inactive)
    get_resp = await client.get(f"/api/v1/rooms/types/{room_type_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


async def test_create_room_type_requires_manager(client):
    """Front desk staff should not be able to create room types."""
    app.dependency_overrides[get_current_user] = lambda: make_mock_user("front_desk")
    payload = _unique_room_type("rbac")
    resp = await client.post("/api/v1/rooms/types", json=payload)
    assert resp.status_code == 403
