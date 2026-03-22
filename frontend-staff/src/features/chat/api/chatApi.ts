import { apiClient } from '@/api/client';
import { useAuthStore } from '@/stores/authStore';
import type { Conversation, ChatMessage } from '../types/chat';

const API_BASE = import.meta.env.VITE_API_URL || '';

export async function getConversations(): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>('/api/v1/chat/conversations');
  return data;
}

export async function getMessages(
  conversationId: string,
  limit?: number,
  before?: string,
): Promise<ChatMessage[]> {
  const params: Record<string, string | number> = {};
  if (limit) params.limit = limit;
  if (before) params.before = before;
  const { data } = await apiClient.get<ChatMessage[]>(
    `/api/v1/chat/conversations/${conversationId}/messages`,
    { params },
  );
  return data;
}

export async function renameConversation(id: string, title: string): Promise<void> {
  await apiClient.patch(`/api/v1/chat/conversations/${id}`, { title });
}

export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/chat/conversations/${id}`);
}

export function sendMessageStream(
  content: string,
  botType: string,
  conversationId?: string,
  confirmedMessageId?: string,
): { response: Promise<Response>; abort: () => void } {
  const controller = new AbortController();
  const token = useAuthStore.getState().token;

  const body: Record<string, unknown> = {
    content,
    bot_type: botType,
  };
  if (conversationId) body.conversation_id = conversationId;
  if (confirmedMessageId) body.confirmed_message_id = confirmedMessageId;

  const response = fetch(`${API_BASE}/api/v1/chat/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
    signal: controller.signal,
  });

  return { response, abort: () => controller.abort() };
}
