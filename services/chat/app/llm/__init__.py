"""LLM provider abstraction layer.

Provides a factory function to instantiate the configured LLM provider.
"""

from app.llm.base import LLMProvider, StreamChunk, TokenUsage


def get_llm_provider(provider: str, api_key: str, model: str) -> LLMProvider:
    """Create an LLM provider instance by name.

    Args:
        provider: Provider name ("anthropic" or "openai").
        api_key: API key for the provider.
        model: Model identifier string.

    Returns:
        An LLMProvider implementation instance.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    if provider == "anthropic":
        from app.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=api_key, model=model)
    elif provider == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = ["LLMProvider", "StreamChunk", "TokenUsage", "get_llm_provider"]
