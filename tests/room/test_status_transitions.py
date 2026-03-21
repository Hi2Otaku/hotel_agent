"""Tests for role-based status transitions and audit logging (RMGT-04)."""

import uuid

import pytest

from app.api.deps import get_current_user
from app.main import app
from tests.room.conftest import make_mock_user


def _unique_room_type(suffix: str) -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Trans Type {suffix}-{uid}",
        "slug": f"trans-type-{suffix}-{uid}",
        "description": "Test room type for transitions",
        "max_adults": 2,
        "max_children": 0,
        "bed_config": [{"type": "king", "count": 1}],
        "amenities": {},
    }


async def _create_room(client, floor: int = 1) -> tuple[str, str]:
    """Helper: create room type + room, return (room_id, room_type_id)."""
    rt_resp = await client.post("/api/v1/rooms/types", json=_unique_room_type("trans"))
    room_type_id = rt_resp.json()["id"]
    room_resp = await client.post(
        "/api/v1/rooms/",
        json={
            "room_number": f"T{uuid.uuid4().hex[:5]}",
            "floor": floor,
            "room_type_id": room_type_id,
        },
    )
    assert room_resp.status_code == 201
    return room_resp.json()["id"], room_type_id


async def test_front_desk_can_transition_available_to_occupied(client):
    """Front desk can transition available -> occupied."""
    room_id, _ = await _create_room(client)
    # Override to front_desk user
    fd_user = make_mock_user("front_desk")
    app.dependency_overrides[get_current_user] = lambda: fd_user

    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "occupied", "reason": "Guest check-in"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "occupied"


async def test_front_desk_cannot_transition_cleaning_to_available(client):
    """Front desk cannot transition cleaning -> available (not in their allowed set)."""
    room_id, _ = await _create_room(client)

    # First, admin sets room to cleaning
    admin_user = make_mock_user("admin")
    app.dependency_overrides[get_current_user] = lambda: admin_user
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "cleaning"},
    )
    assert resp.status_code == 200

    # Now front_desk tries cleaning -> available
    fd_user = make_mock_user("front_desk")
    app.dependency_overrides[get_current_user] = lambda: fd_user
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "available"},
    )
    assert resp.status_code == 403


async def test_housekeeping_can_transition_cleaning_to_inspected(client):
    """Housekeeping can transition cleaning -> inspected."""
    room_id, _ = await _create_room(client)

    # Admin sets room to cleaning first
    admin_user = make_mock_user("admin")
    app.dependency_overrides[get_current_user] = lambda: admin_user
    await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "cleaning"},
    )

    # Housekeeping transitions cleaning -> inspected
    hk_user = make_mock_user("housekeeping")
    app.dependency_overrides[get_current_user] = lambda: hk_user
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "inspected", "reason": "Room cleaned and checked"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "inspected"


async def test_admin_can_do_any_transition(client):
    """Admin can transition between any statuses."""
    room_id, _ = await _create_room(client)
    admin_user = make_mock_user("admin")
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # available -> maintenance (not in front_desk or housekeeping sets)
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "maintenance", "reason": "AC repair"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "maintenance"

    # maintenance -> available
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "available", "reason": "Repair complete"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "available"


async def test_manager_override_any_transition(client):
    """Manager can do any transition (manager has None = all allowed)."""
    room_id, _ = await _create_room(client)
    mgr_user = make_mock_user("manager")
    app.dependency_overrides[get_current_user] = lambda: mgr_user

    # available -> out_of_order
    resp = await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "out_of_order", "reason": "Flood damage"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "out_of_order"


async def test_status_change_logged(client):
    """Status transitions should be recorded in the audit log."""
    room_id, _ = await _create_room(client)
    admin_user = make_mock_user("admin")
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Transition: available -> occupied
    await client.post(
        f"/api/v1/rooms/{room_id}/status",
        json={"new_status": "occupied", "reason": "VIP check-in"},
    )

    # Check history
    resp = await client.get(f"/api/v1/rooms/{room_id}/status-history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 1
    entry = history[0]
    assert entry["from_status"] == "available"
    assert entry["to_status"] == "occupied"
    assert entry["changed_by"] == admin_user["sub"]
    assert entry["reason"] == "VIP check-in"
