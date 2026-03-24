"""OpenAI LLM provider implementation."""

import json
from typing import AsyncIterator

import openai

from app.llm.base import LLMProvider, StreamChunk, TokenUsage


class OpenAIProvider(LLMProvider):
    """LLM provider using OpenAI's API with streaming.

    Args:
        api_key: OpenAI API key.
        model: Model identifier (e.g., "gpt-4o").
    """

    def __init__(self, api_key: str, model: str) -> None:
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self._usage: TokenUsage = TokenUsage(input_tokens=0, output_tokens=0)

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert provider-agnostic tool format to OpenAI function calling format.

        Args:
            tools: List of dicts with name, description, input_schema.

        Returns:
            List of OpenAI-format tool definitions.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                },
            }
            for tool in tools
        ]

    async def stream_message(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a message response from OpenAI's API.

        Converts tool definitions to OpenAI function calling format and
        handles incremental tool call argument streaming.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Tool definitions with name, description, input_schema.
            max_tokens: Maximum tokens to generate.

        Yields:
            StreamChunk objects for text deltas, tool use events, and done.
        """
        # Convert provider-agnostic messages to OpenAI format
        openai_messages = [{"role": "system", "content": system}]
        for msg in messages:
            if msg.get("role") == "tool_result":
                # Convert tool_result -> tool with tool_call_id
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.get("tool_id", ""),
                    "content": msg.get("content", ""),
                })
            elif msg.get("role") == "assistant" and msg.get("tool_calls"):
                # Ensure tool_calls have type: "function" and proper structure
                converted_calls = []
                for tc in msg["tool_calls"]:
                    converted_calls.append({
                        "id": tc.get("id", ""),
                        "type": "function",
                        "function": {
                            "name": tc.get("name", ""),
                            "arguments": json.dumps(tc.get("input", {})) if isinstance(tc.get("input"), dict) else tc.get("arguments", "{}"),
                        },
                    })
                entry: dict = {
                    "role": "assistant",
                    "tool_calls": converted_calls,
                }
                if msg.get("content"):
                    entry["content"] = msg["content"]
                openai_messages.append(entry)
            else:
                # Ensure content is never null for OpenAI
                cleaned = {**msg}
                if cleaned.get("content") is None:
                    cleaned["content"] = ""
                openai_messages.append(cleaned)

        # Final sanitization: ensure no message has null content
        for m in openai_messages:
            if "content" in m and m["content"] is None:
                if m.get("tool_calls"):
                    # Assistant messages with tool_calls: remove content entirely
                    del m["content"]
                else:
                    m["content"] = ""

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": openai_messages,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        # Track tool call accumulation
        tool_calls_acc: dict[int, dict] = {}  # index -> {id, name, arguments}

        stream = await self.client.chat.completions.create(**kwargs)

        async for chunk in stream:
            # Handle usage from final chunk
            if chunk.usage is not None:
                self._usage = TokenUsage(
                    input_tokens=chunk.usage.prompt_tokens,
                    output_tokens=chunk.usage.completion_tokens,
                )

            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            # Text content
            if delta and delta.content:
                yield StreamChunk(type="text_delta", text=delta.content)

            # Tool calls (streamed incrementally)
            if delta and delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {
                            "id": tc.id or "",
                            "name": "",
                            "arguments": "",
                        }

                    if tc.id:
                        tool_calls_acc[idx]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_acc[idx]["name"] = tc.function.name
                        yield StreamChunk(
                            type="tool_use_start",
                            tool_name=tc.function.name,
                            tool_id=tool_calls_acc[idx]["id"],
                        )
                    if tc.function and tc.function.arguments:
                        tool_calls_acc[idx]["arguments"] += tc.function.arguments
                        yield StreamChunk(
                            type="tool_use_input",
                            text=tc.function.arguments,
                        )

            # Check for finish
            if choice.finish_reason in ("stop", "tool_calls"):
                # Emit tool_use_end for any accumulated tool calls
                for idx, tc_data in tool_calls_acc.items():
                    try:
                        tool_input = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                    except json.JSONDecodeError:
                        tool_input = {}
                    yield StreamChunk(
                        type="tool_use_end",
                        tool_id=tc_data["id"],
                        tool_input=tool_input,
                    )
                tool_calls_acc.clear()

        yield StreamChunk(type="done")

    async def get_usage(self) -> TokenUsage:
        """Return token usage from the most recent stream."""
        return self._usage
