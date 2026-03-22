"""Chat SSE streaming endpoint and message history.

Provides the POST /send endpoint for sending messages with SSE streaming
responses, and GET /conversations/{id}/messages for message history.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from app.api.deps import get_current_user, get_db, rate_limiter
from app.core.config import settings
from app.llm import get_llm_provider
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import MessageResponse, SendMessageRequest
from app.services.chat_engine import ChatEngine
from app.services.prompt_builder import PromptBuilder
from app.services.tool_executor import ToolExecutor
from app.services.tool_registry import ToolRegistry

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Shared instances (stateless, safe to reuse)
_tool_registry = ToolRegistry()
_prompt_builder = PromptBuilder()


async def _sse_generator(engine: ChatEngine, request: SendMessageRequest):
    """Wrap ChatEngine output as ServerSentEvent objects for SSE streaming."""
    async for event_dict in engine.process_message(request):
        yield ServerSentEvent(
            data=event_dict["data"],
            event=event_dict["event"],
        )


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limiter),
):
    """Send a message and receive streaming SSE response.

    Creates a ChatEngine instance for this request and streams events
    including text_delta, tool_start, tool_result, confirmation_required,
    done, and error events.
    """
    llm = get_llm_provider(
        settings.CHAT_LLM_PROVIDER,
        settings.CHAT_LLM_API_KEY,
        settings.CHAT_LLM_MODEL,
    )
    tool_executor = ToolExecutor(auth_token=user["token"])

    engine = ChatEngine(
        db=db,
        user=user,
        llm=llm,
        tool_registry=_tool_registry,
        tool_executor=tool_executor,
        prompt_builder=_prompt_builder,
    )

    return EventSourceResponse(_sse_generator(engine, request))


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    before: str | None = Query(default=None, description="Cursor: ISO datetime to paginate before"),
):
    """Get messages for a conversation with cursor-based pagination.

    Returns messages ordered by created_at ascending. Use the `before`
    parameter with a message's created_at value for pagination.
    """
    # Verify user owns the conversation
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == uuid.UUID(user["id"]),
        )
    )
    if conv_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    if before:
        from datetime import datetime

        try:
            before_dt = datetime.fromisoformat(before)
            query = query.where(Message.created_at < before_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' datetime format")

    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))
    return messages
