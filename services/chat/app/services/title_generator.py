"""Conversation title generator using the LLM.

Generates a concise 3-6 word title from the first user/bot exchange.
Falls back to truncated user message on LLM failure.
"""

import logging

from app.llm.base import LLMProvider, StreamChunk

logger = logging.getLogger(__name__)


async def generate_title(llm: LLMProvider, first_user_msg: str, first_bot_msg: str) -> str:
    """Generate a concise 3-6 word title for a conversation.

    Sends a short prompt to the LLM and collects the full non-streaming
    response. Falls back to the first 50 characters of the user message
    if the LLM call fails.

    Args:
        llm: An LLMProvider instance.
        first_user_msg: The first message from the user.
        first_bot_msg: The first response from the bot.

    Returns:
        A short conversation title string.
    """
    prompt = (
        f"Generate a concise 3-6 word title for this conversation. "
        f"First message: {first_user_msg}. "
        f"Response: {first_bot_msg}. "
        f"Title only, no quotes."
    )

    try:
        collected = []
        async for chunk in llm.stream_message(
            messages=[{"role": "user", "content": prompt}],
            system="You generate short conversation titles. Respond with only the title.",
            tools=[],
            max_tokens=50,
        ):
            if chunk.type == "text_delta" and chunk.text:
                collected.append(chunk.text)
            elif chunk.type == "done":
                break

        title = "".join(collected).strip().strip('"').strip("'")
        if title:
            return title
    except Exception:
        logger.exception("Failed to generate conversation title")

    # Fallback: first 50 chars of user message
    fallback = first_user_msg[:50].strip()
    if len(first_user_msg) > 50:
        fallback += "..."
    return fallback
