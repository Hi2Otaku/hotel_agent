"""Chat request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""

    conversation_id: UUID | None = None
    content: str
    bot_type: str = "guest"
    confirmed_message_id: UUID | None = None


class ConversationResponse(BaseModel):
    """Response representing a conversation."""

    id: UUID
    title: str | None
    bot_type: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Response representing a single message."""

    id: UUID
    role: str
    content: str | None
    tool_calls: dict | None
    tool_results: dict | None
    pending_confirmation: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRenameRequest(BaseModel):
    """Request to rename a conversation."""

    title: str
