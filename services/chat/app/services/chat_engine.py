"""Chat engine orchestrator -- the brain of the chatbot.

Takes user messages, builds context, calls the LLM with tools,
handles the tool-use loop and confirmation flow, and streams
responses back via SSE events.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.base import LLMProvider, StreamChunk
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import SendMessageRequest
from app.schemas.sse_events import (
    ConfirmationRequiredEvent,
    DoneEvent,
    ErrorEvent,
    TextDeltaEvent,
    ToolResultEvent,
    ToolStartEvent,
)
from app.services.event_publisher import publish_chat_event
from app.services.prompt_builder import PromptBuilder
from app.services.title_generator import generate_title
from app.services.tool_executor import ToolExecutor
from app.services.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

# Maximum tool-use loop iterations to prevent runaway loops
MAX_TOOL_ITERATIONS = 5

# Soft limit on conversation length before suggesting a new one
CONVERSATION_SOFT_LIMIT = 50


def _tool_description(tool_name: str, args: dict) -> str:
    """Map tool names to human-readable status descriptions.

    Args:
        tool_name: The tool being called.
        args: The tool input arguments.

    Returns:
        A user-friendly description of what the tool is doing.
    """
    descriptions = {
        "search_rooms": "Searching rooms for {check_in} to {check_out}...".format_map(
            {**{"check_in": "your dates", "check_out": ""}, **args}
        ),
        "get_room_details": "Getting room details...",
        "check_booking_status": "Checking booking status...",
        "create_booking": "Creating your booking...",
        "cancel_booking": "Cancelling booking...",
        "modify_booking": "Modifying booking dates...",
        "check_in_guest": "Checking in guest...",
        "check_out_guest": "Checking out guest...",
        "update_room_status": "Updating room status...",
        "get_occupancy_report": "Generating occupancy report...",
        "get_revenue_report": "Generating revenue report...",
        "lookup_guest": "Looking up guest...",
    }
    return descriptions.get(tool_name, f"Executing {tool_name}...")


class ChatEngine:
    """Orchestrates the full chat message flow.

    Handles: load history -> call LLM -> tool-use loop (max 5 iterations) ->
    pause for write action confirmations -> stream SSE events.
    """

    def __init__(
        self,
        db: AsyncSession,
        user: dict,
        llm: LLMProvider,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
        prompt_builder: PromptBuilder,
        event_publisher=None,
    ) -> None:
        self.db = db
        self.user = user
        self.llm = llm
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor
        self.prompt_builder = prompt_builder
        self.event_publisher = event_publisher

    async def process_message(self, request: SendMessageRequest):
        """Process a user message and yield SSE event dicts.

        This is an async generator that yields dicts suitable for
        ServerSentEvent construction (with "event" and "data" keys).

        Args:
            request: The incoming send message request.

        Yields:
            Dicts with "event" (str) and "data" (JSON str) for SSE streaming.
        """
        try:
            async for event in self._process_message_inner(request):
                yield event
        except Exception as e:
            logger.exception("Error processing message")
            # Retry once
            try:
                await asyncio.sleep(1)
                async for event in self._process_message_inner(request):
                    yield event
            except Exception:
                logger.exception("Retry failed")
                yield {
                    "event": "error",
                    "data": ErrorEvent(
                        message="The assistant is temporarily unavailable. Please try again in a moment.",
                        retryable=False,
                    ).model_dump_json(),
                }

    async def _process_message_inner(self, request: SendMessageRequest):
        """Inner message processing logic."""
        conversation = None

        # a. Create or load conversation
        if request.conversation_id is None:
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=uuid.UUID(self.user["id"]),
                bot_type=request.bot_type,
            )
            self.db.add(conversation)
            await self.db.flush()

            # Publish conversation created event
            try:
                await publish_chat_event("chat.conversation.created", {
                    "conversation_id": str(conversation.id),
                    "user_id": self.user["id"],
                    "bot_type": request.bot_type,
                })
            except Exception:
                logger.warning("Failed to publish conversation.created event")
        else:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == uuid.UUID(self.user["id"]),
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation is None:
                yield {
                    "event": "error",
                    "data": ErrorEvent(
                        message="Conversation not found.",
                        retryable=False,
                    ).model_dump_json(),
                }
                return

        # b. Handle confirmation flow
        if request.confirmed_message_id:
            async for event in self._handle_confirmation(
                conversation, request.confirmed_message_id
            ):
                yield event
            return

        # c. Load conversation history (last 50 messages)
        history_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(50)
        )
        history_messages = list(reversed(history_result.scalars().all()))

        # Query total message count for soft limit check
        count_result = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation.id
            )
        )
        total_message_count = count_result.scalar() or 0

        # e. Save user message to DB
        user_message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="user",
            content=request.content,
        )
        self.db.add(user_message)
        await self.db.flush()

        # f. Build system prompt
        system_prompt = await self.prompt_builder.build_system_prompt(
            conversation.bot_type, self.db
        )

        # d. Soft limit check -- append note to system prompt
        if total_message_count >= CONVERSATION_SOFT_LIMIT:
            system_prompt += (
                "\n\nThis conversation has grown long. Gently suggest to the user "
                "that they might want to start a new conversation for better context "
                "and accuracy, but continue helping if they prefer to stay."
            )

        # g. Get tools
        tools = self.tool_registry.get_tools(
            conversation.bot_type, self.user.get("role")
        )

        # Build messages for LLM
        llm_messages = self._build_llm_messages(history_messages, request.content)

        # h. Tool-use loop (max 5 iterations)
        accumulated_text = []
        tool_calls_data = []
        tool_results_data = []
        assistant_message_id = uuid.uuid4()

        for iteration in range(MAX_TOOL_ITERATIONS):
            had_tool_call = False

            # Track current tool being built
            current_tool_name = None
            current_tool_id = None
            current_tool_input_parts = []

            async for chunk in self.llm.stream_message(
                llm_messages, system_prompt, tools
            ):
                if chunk.type == "text_delta":
                    yield {
                        "event": "text_delta",
                        "data": TextDeltaEvent(text=chunk.text).model_dump_json(),
                    }
                    if chunk.text:
                        accumulated_text.append(chunk.text)

                elif chunk.type == "tool_use_start":
                    current_tool_name = chunk.tool_name
                    current_tool_id = chunk.tool_id
                    current_tool_input_parts = []

                    yield {
                        "event": "tool_start",
                        "data": ToolStartEvent(
                            tool_name=chunk.tool_name,
                            tool_id=chunk.tool_id,
                            description=_tool_description(chunk.tool_name, {}),
                        ).model_dump_json(),
                    }

                elif chunk.type == "tool_use_input":
                    if chunk.text:
                        current_tool_input_parts.append(chunk.text)

                elif chunk.type == "tool_use_end":
                    had_tool_call = True
                    tool_input = chunk.tool_input or {}
                    tool_name = current_tool_name or chunk.tool_name or "unknown"
                    tool_id = current_tool_id or chunk.tool_id or str(uuid.uuid4())

                    tool_calls_data.append({
                        "name": tool_name,
                        "id": tool_id,
                        "input": tool_input,
                    })

                    # Check if tool requires confirmation
                    try:
                        tool_def = self.tool_registry.get_tool(tool_name)
                    except KeyError:
                        tool_def = {"requires_confirmation": False}

                    if tool_def.get("requires_confirmation"):
                        # Save pending confirmation to message
                        pending_msg = Message(
                            id=assistant_message_id,
                            conversation_id=conversation.id,
                            role="assistant",
                            content="".join(accumulated_text) if accumulated_text else None,
                            tool_calls=tool_calls_data,
                            pending_confirmation={
                                "tool_name": tool_name,
                                "tool_id": tool_id,
                                "tool_input": tool_input,
                            },
                        )
                        self.db.add(pending_msg)
                        await self.db.flush()
                        await self.db.commit()

                        yield {
                            "event": "confirmation_required",
                            "data": ConfirmationRequiredEvent(
                                message_id=str(assistant_message_id),
                                action=tool_name,
                                description=_tool_description(tool_name, tool_input),
                                details=tool_input,
                            ).model_dump_json(),
                        }
                        return
                    else:
                        # Execute tool immediately
                        result = await self.tool_executor.execute(tool_name, tool_input)
                        tool_results_data.append({
                            "tool_id": tool_id,
                            "result": result,
                        })

                        raw_data = result.get("data") or result.get("error") or {}
                        event_data = raw_data if isinstance(raw_data, dict) else {"message": str(raw_data)}

                        yield {
                            "event": "tool_result",
                            "data": ToolResultEvent(
                                tool_id=tool_id,
                                success=result["success"],
                                data=event_data,
                            ).model_dump_json(),
                        }

                        # Publish tool executed event
                        try:
                            await publish_chat_event("chat.tool.executed", {
                                "conversation_id": str(conversation.id),
                                "tool_name": tool_name,
                                "success": result["success"],
                            })
                        except Exception:
                            pass

                        # Append tool result to messages for next LLM call
                        llm_messages.append({
                            "role": "assistant",
                            "content": "".join(accumulated_text) if accumulated_text else None,
                            "tool_calls": [{"name": tool_name, "id": tool_id, "input": tool_input}],
                        })
                        llm_messages.append({
                            "role": "tool_result",
                            "tool_id": tool_id,
                            "content": json.dumps(result),
                        })
                        # Reset accumulated text for next iteration
                        accumulated_text = []

                elif chunk.type == "done":
                    break

            if not had_tool_call:
                break

        # i. After stream completes -- save assistant message
        try:
            usage = await self.llm.get_usage()
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
        except Exception:
            input_tokens = 0
            output_tokens = 0

        # Estimate cost (rough: $3/M input, $15/M output for Claude Sonnet)
        estimated_cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)

        assistant_msg = Message(
            id=assistant_message_id,
            conversation_id=conversation.id,
            role="assistant",
            content="".join(accumulated_text) if accumulated_text else None,
            tool_calls=tool_calls_data if tool_calls_data else None,
            tool_results=tool_results_data if tool_results_data else None,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=estimated_cost,
        )
        self.db.add(assistant_msg)

        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.commit()

        yield {
            "event": "done",
            "data": DoneEvent(
                message_id=str(assistant_message_id),
                conversation_id=str(conversation.id),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ).model_dump_json(),
        }

        # Publish message sent event
        try:
            await publish_chat_event("chat.message.sent", {
                "conversation_id": str(conversation.id),
                "message_id": str(assistant_message_id),
                "user_id": self.user["id"],
                "bot_type": conversation.bot_type,
            })
        except Exception:
            pass

        # If first exchange (2 messages: user + assistant), generate title
        total_after = total_message_count + 2  # user msg + assistant msg
        if total_after <= 2 and conversation.title is None:
            try:
                bot_response = "".join(accumulated_text) if accumulated_text else ""
                title = await generate_title(self.llm, request.content, bot_response)
                conversation.title = title
                await self.db.flush()
                await self.db.commit()
            except Exception:
                logger.warning("Failed to generate title for conversation %s", conversation.id)

    async def _handle_confirmation(self, conversation: Conversation, confirmed_message_id):
        """Handle a confirmed write action.

        Loads the pending confirmation from the message, executes the tool,
        yields the result, then continues to the LLM with the tool result.
        """
        msg_result = await self.db.execute(
            select(Message).where(
                Message.id == confirmed_message_id,
                Message.conversation_id == conversation.id,
            )
        )
        pending_msg = msg_result.scalar_one_or_none()

        if pending_msg is None or pending_msg.pending_confirmation is None:
            yield {
                "event": "error",
                "data": ErrorEvent(
                    message="No pending confirmation found.",
                    retryable=False,
                ).model_dump_json(),
            }
            return

        confirmation = pending_msg.pending_confirmation
        tool_name = confirmation["tool_name"]
        tool_id = confirmation["tool_id"]
        tool_input = confirmation["tool_input"]

        # Execute the confirmed tool
        result = await self.tool_executor.execute(tool_name, tool_input)

        # Clear pending confirmation
        pending_msg.pending_confirmation = None
        pending_msg.tool_results = [{"tool_id": tool_id, "result": result}]
        await self.db.flush()

        raw_confirm_data = result.get("data") or result.get("error") or {}
        confirm_event_data = raw_confirm_data if isinstance(raw_confirm_data, dict) else {"message": str(raw_confirm_data)}

        yield {
            "event": "tool_result",
            "data": ToolResultEvent(
                tool_id=tool_id,
                success=result["success"],
                data=confirm_event_data,
            ).model_dump_json(),
        }

        # Continue to LLM with tool result for natural language summary
        history_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(50)
        )
        history_messages = list(reversed(history_result.scalars().all()))

        system_prompt = await self.prompt_builder.build_system_prompt(
            conversation.bot_type, self.db
        )
        tools = self.tool_registry.get_tools(
            conversation.bot_type, self.user.get("role")
        )

        llm_messages = self._build_llm_messages_from_history(history_messages)
        # Append the tool result
        llm_messages.append({
            "role": "tool_result",
            "tool_id": tool_id,
            "content": json.dumps(result),
        })

        accumulated_text = []
        assistant_message_id = uuid.uuid4()

        async for chunk in self.llm.stream_message(llm_messages, system_prompt, tools):
            if chunk.type == "text_delta":
                yield {
                    "event": "text_delta",
                    "data": TextDeltaEvent(text=chunk.text).model_dump_json(),
                }
                if chunk.text:
                    accumulated_text.append(chunk.text)
            elif chunk.type == "done":
                break

        try:
            usage = await self.llm.get_usage()
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
        except Exception:
            input_tokens = 0
            output_tokens = 0

        estimated_cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)

        assistant_msg = Message(
            id=assistant_message_id,
            conversation_id=conversation.id,
            role="assistant",
            content="".join(accumulated_text) if accumulated_text else None,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=estimated_cost,
        )
        self.db.add(assistant_msg)
        conversation.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.commit()

        yield {
            "event": "done",
            "data": DoneEvent(
                message_id=str(assistant_message_id),
                conversation_id=str(conversation.id),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ).model_dump_json(),
        }

    def _build_llm_messages(
        self, history: list[Message], current_content: str
    ) -> list[dict]:
        """Build LLM message list from DB history + current user message."""
        messages = self._build_llm_messages_from_history(history)
        messages.append({"role": "user", "content": current_content})
        return messages

    def _build_llm_messages_from_history(self, history: list[Message]) -> list[dict]:
        """Build LLM message list from DB message history.

        Tool calls and results are stored together on the assistant message
        in JSONB fields. This method expands them into the separate messages
        the LLM API expects: assistant message with tool_calls, followed by
        individual tool_result messages for each call.
        """
        messages = []
        for msg in history:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                entry: dict = {"role": "assistant", "content": msg.content}
                if msg.tool_calls:
                    entry["tool_calls"] = msg.tool_calls
                messages.append(entry)

                # Expand tool results into separate messages after the assistant
                if msg.tool_calls and msg.tool_results:
                    results_by_id = {}
                    for tr in msg.tool_results:
                        if isinstance(tr, dict) and "tool_id" in tr:
                            results_by_id[tr["tool_id"]] = tr.get("result", {})

                    for tc in msg.tool_calls:
                        tc_id = tc.get("id", "")
                        result = results_by_id.get(tc_id, {})
                        messages.append({
                            "role": "tool_result",
                            "tool_id": tc_id,
                            "content": json.dumps(result) if isinstance(result, dict) else str(result),
                        })
            elif msg.role == "tool_result":
                messages.append({
                    "role": "tool_result",
                    "tool_id": getattr(msg, "tool_id", ""),
                    "content": msg.content,
                })
        return messages
