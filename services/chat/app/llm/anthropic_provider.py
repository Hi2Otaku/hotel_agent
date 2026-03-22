"""Anthropic (Claude) LLM provider implementation."""

import json
from typing import AsyncIterator

import anthropic

from app.llm.base import LLMProvider, StreamChunk, TokenUsage


class AnthropicProvider(LLMProvider):
    """LLM provider using Anthropic's Claude API with streaming.

    Args:
        api_key: Anthropic API key.
        model: Model identifier (e.g., "claude-sonnet-4-6-20250514").
    """

    def __init__(self, api_key: str, model: str) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self._usage: TokenUsage = TokenUsage(input_tokens=0, output_tokens=0)

    async def stream_message(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a message response from Anthropic's API.

        Anthropic tools use the native format: name, description, input_schema.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Tool definitions with name, description, input_schema.
            max_tokens: Maximum tokens to generate.

        Yields:
            StreamChunk objects for text deltas, tool use events, and done.
        """
        # Track active tool blocks for accumulating input
        current_tool_id: str | None = None
        current_tool_input_json = ""

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        async with self.client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if hasattr(block, "name"):
                        # Tool use block starting
                        current_tool_id = block.id
                        current_tool_input_json = ""
                        yield StreamChunk(
                            type="tool_use_start",
                            tool_name=block.name,
                            tool_id=block.id,
                        )

                elif event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "text"):
                        yield StreamChunk(type="text_delta", text=delta.text)
                    elif hasattr(delta, "partial_json"):
                        current_tool_input_json += delta.partial_json
                        yield StreamChunk(
                            type="tool_use_input", text=delta.partial_json
                        )

                elif event.type == "content_block_stop":
                    if current_tool_id is not None:
                        # Parse accumulated JSON input
                        try:
                            tool_input = json.loads(current_tool_input_json) if current_tool_input_json else {}
                        except json.JSONDecodeError:
                            tool_input = {}
                        yield StreamChunk(
                            type="tool_use_end",
                            tool_id=current_tool_id,
                            tool_input=tool_input,
                        )
                        current_tool_id = None
                        current_tool_input_json = ""

            # Get final message for usage
            final = await stream.get_final_message()
            self._usage = TokenUsage(
                input_tokens=final.usage.input_tokens,
                output_tokens=final.usage.output_tokens,
            )

        yield StreamChunk(type="done")

    async def get_usage(self) -> TokenUsage:
        """Return token usage from the most recent stream."""
        return self._usage
