"""Tests for LLM provider abstraction layer."""

import pytest

from app.llm import get_llm_provider
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.base import StreamChunk, TokenUsage


def test_get_llm_provider_anthropic():
    """Factory returns an AnthropicProvider instance."""
    provider = get_llm_provider("anthropic", "test-key", "claude-sonnet-4-6-20250514")
    assert isinstance(provider, AnthropicProvider)


def test_get_llm_provider_openai():
    """Factory returns an OpenAIProvider instance."""
    provider = get_llm_provider("openai", "test-key", "gpt-4o")
    assert isinstance(provider, OpenAIProvider)


def test_get_llm_provider_unknown_raises():
    """Factory raises ValueError for unknown provider."""
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm_provider("unknown", "key", "model")


@pytest.mark.asyncio
async def test_mock_provider_streams_text(mock_llm_provider):
    """MockLLMProvider yields text_delta chunks."""
    chunks = []
    async for chunk in mock_llm_provider.stream_message(
        messages=[{"role": "user", "content": "Hi"}],
        system="You are a helpful assistant.",
        tools=[],
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].type == "text_delta"
    assert chunks[0].text == "Hello"
    assert chunks[1].type == "done"


@pytest.mark.asyncio
async def test_mock_provider_usage(mock_llm_provider):
    """MockLLMProvider returns fixed token usage."""
    usage = await mock_llm_provider.get_usage()
    assert isinstance(usage, TokenUsage)
    assert usage.input_tokens == 10
    assert usage.output_tokens == 5
