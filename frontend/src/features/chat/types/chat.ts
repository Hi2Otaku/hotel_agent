export interface Conversation {
  id: string;
  title: string | null;
  bot_type: 'guest' | 'staff';
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool_result';
  content: string | null;
  tool_calls: Record<string, unknown> | null;
  tool_results: Record<string, unknown> | null;
  pending_confirmation: PendingConfirmation | null;
  created_at: string;
  isStreaming?: boolean;
}

export interface PendingConfirmation {
  message_id: string;
  action: string;
  description: string;
  details: Record<string, unknown>;
}

export interface SSETextDelta {
  type: 'text_delta';
  text: string;
}
export interface SSEToolStart {
  type: 'tool_start';
  tool_name: string;
  tool_id: string;
  description: string;
}
export interface SSEToolResult {
  type: 'tool_result';
  tool_id: string;
  success: boolean;
  data: Record<string, unknown>;
}
export interface SSEConfirmationRequired {
  type: 'confirmation_required';
  message_id: string;
  action: string;
  description: string;
  details: Record<string, unknown>;
}
export interface SSEDone {
  type: 'done';
  message_id: string;
  input_tokens: number;
  output_tokens: number;
}
export interface SSEError {
  type: 'error';
  message: string;
  retryable: boolean;
}

export type SSEEvent =
  | SSETextDelta
  | SSEToolStart
  | SSEToolResult
  | SSEConfirmationRequired
  | SSEDone
  | SSEError;

export interface ToolStatusState {
  tool_id: string;
  tool_name: string;
  description: string;
  status: 'running' | 'success' | 'error';
  data?: Record<string, unknown>;
}

export interface RoomCardData {
  id: string;
  name: string;
  photo_url: string;
  price_per_night: number;
  capacity: number;
  amenities: string[];
}
