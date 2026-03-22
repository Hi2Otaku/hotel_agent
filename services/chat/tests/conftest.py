"""Shared test fixtures for chat service tests."""

import uuid
from typing import AsyncIterator

import pytest

from app.llm.base import LLMProvider, StreamChunk, TokenUsage


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that yields canned responses for testing.

    Yields a single text_delta chunk with "Hello" followed by a done chunk.
    """

    def __init__(self) -> None:
        self._usage = TokenUsage(input_tokens=10, output_tokens=5)

    async def stream_message(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamChunk]:
        """Yield canned streaming response chunks."""
        yield StreamChunk(type="text_delta", text="Hello")
        yield StreamChunk(type="done")

    async def get_usage(self) -> TokenUsage:
        """Return fixed test usage."""
        return self._usage


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    """Provide a mock LLM provider for testing."""
    return MockLLMProvider()


@pytest.fixture
def test_user_claims() -> dict:
    """Provide test user JWT claims."""
    return {
        "id": str(uuid.uuid4()),
        "role": "guest",
        "email": "test@example.com",
    }
