"""Conversation CRUD endpoints.

Provides listing, renaming, and deleting conversations.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ConversationRenameRequest, ConversationResponse

router = APIRouter(prefix="/api/v1/chat/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user, ordered by most recent.

    Includes a message_count subquery for each conversation.
    """
    message_count_subq = (
        select(func.count(Message.id))
        .where(Message.conversation_id == Conversation.id)
        .correlate(Conversation)
        .scalar_subquery()
    )

    result = await db.execute(
        select(
            Conversation,
            message_count_subq.label("message_count"),
        )
        .where(Conversation.user_id == uuid.UUID(user["id"]))
        .order_by(Conversation.updated_at.desc())
    )

    conversations = []
    for row in result.all():
        conv = row[0]
        count = row[1] or 0
        conversations.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                bot_type=conv.bot_type,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=count,
            )
        )
    return conversations


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: uuid.UUID,
    body: ConversationRenameRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rename a conversation. Only the owner can rename."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == uuid.UUID(user["id"]),
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.title = body.title
    await db.flush()
    await db.commit()

    # Get message count
    count_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
    )
    msg_count = count_result.scalar() or 0

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        bot_type=conv.bot_type,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=msg_count,
    )


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages. Only the owner can delete."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == uuid.UUID(user["id"]),
        )
    )
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conv)
    await db.commit()
