"""Test stubs for chat service database models."""

import uuid
from datetime import datetime, timezone


def test_conversation_create():
    """Test that a Conversation can be instantiated with required fields."""
    from app.models.conversation import Conversation

    conv = Conversation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        bot_type="guest",
        title="Test Conversation",
    )
    assert conv.bot_type == "guest"
    assert conv.title == "Test Conversation"
    assert conv.user_id is not None


def test_message_create():
    """Test that a Message can be instantiated with JSONB tool_calls."""
    from app.models.message import Message

    msg = Message(
        id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        role="assistant",
        content="Hello, how can I help?",
        tool_calls={"name": "search_rooms", "input": {"check_in": "2026-04-01"}},
        pending_confirmation={"action": "create_booking", "details": {}},
        input_tokens=100,
        output_tokens=50,
    )
    assert msg.role == "assistant"
    assert msg.tool_calls is not None
    assert msg.tool_calls["name"] == "search_rooms"
    assert msg.pending_confirmation is not None


def test_conversation_message_relationship():
    """Test that Conversation has messages relationship attribute."""
    from app.models.conversation import Conversation

    conv = Conversation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        bot_type="staff",
    )
    # The relationship exists as an attribute (not populated without DB)
    assert hasattr(conv, "messages")
