"""Abstract LLM provider interface for chat service."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class StreamChunk:
    """A single chunk from an LLM streaming response.

    Attributes:
        type: One of "text_delta", "tool_use_start", "tool_use_input",
              "tool_use_end", "done", "error".
        text: Text content for text_delta and tool_use_input chunks.
        tool_name: Tool name for tool_use_start chunks.
        tool_id: Tool identifier for tool_use_start and tool_use_end chunks.
        tool_input: Parsed tool input dict for tool_use_end chunks.
    """

    type: str  # "text_delta" | "tool_use_start" | "tool_use_input" | "tool_use_end" | "done" | "error"
    text: str | None = None
    tool_name: str | None = None
    tool_id: str | None = None
    tool_input: dict | None = None


@dataclass
class TokenUsage:
    """Token usage information from an LLM response.

    Attributes:
        input_tokens: Number of input (prompt) tokens consumed.
        output_tokens: Number of output (completion) tokens generated.
    """

    input_tokens: int
    output_tokens: int


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Implementations must provide streaming message generation and
    token usage tracking.
    """

    @abstractmethod
    async def stream_message(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a message response from the LLM.

        Args:
            messages: Conversation history as a list of role/content dicts.
            system: System prompt string.
            tools: List of tool definitions (name, description, input_schema).
            max_tokens: Maximum tokens to generate.

        Yields:
            StreamChunk objects representing incremental response data.
        """
        ...

    @abstractmethod
    async def get_usage(self) -> TokenUsage:
        """Get token usage from the most recent stream_message call.

        Returns:
            TokenUsage with input and output token counts.
        """
        ...


__all__ = ["LLMProvider", "StreamChunk", "TokenUsage"]
