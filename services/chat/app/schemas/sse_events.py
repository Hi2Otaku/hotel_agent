"""Server-Sent Events (SSE) event models for streaming chat responses."""

from pydantic import BaseModel


class TextDeltaEvent(BaseModel):
    """Incremental text chunk from the LLM."""

    type: str = "text_delta"
    text: str


class ToolStartEvent(BaseModel):
    """LLM has started invoking a tool."""

    type: str = "tool_start"
    tool_name: str
    tool_id: str
    description: str


class ToolResultEvent(BaseModel):
    """Result from a tool execution."""

    type: str = "tool_result"
    tool_id: str
    success: bool
    data: dict


class ConfirmationRequiredEvent(BaseModel):
    """A destructive action requires user confirmation before proceeding."""

    type: str = "confirmation_required"
    message_id: str
    action: str
    description: str
    details: dict


class DoneEvent(BaseModel):
    """Stream is complete with token usage information."""

    type: str = "done"
    message_id: str
    input_tokens: int
    output_tokens: int


class ErrorEvent(BaseModel):
    """An error occurred during processing."""

    type: str = "error"
    message: str
    retryable: bool = False
