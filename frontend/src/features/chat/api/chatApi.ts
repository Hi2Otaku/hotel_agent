import { apiClient } from '@/api/client';
import type { Conversation, ChatMessage } from '../types/chat';

export async function getConversations(): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>(
    '/api/v1/chat/conversations',
  );
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

  // Sort messages chronologically, user before assistant for same timestamp
  const roleOrder: Record<string, number> = { system: 0, user: 1, assistant: 2 };
  data.sort((a, b) => {
    const timeA = new Date(a.created_at).getTime();
    const timeB = new Date(b.created_at).getTime();
    if (timeA !== timeB) return timeA - timeB;
    return (roleOrder[a.role] ?? 3) - (roleOrder[b.role] ?? 3);
  });
  return data;
}

export async function renameConversation(
  id: string,
  title: string,
): Promise<void> {
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

  const baseURL =
    (import.meta.env.VITE_API_URL as string | undefined) || '';
  const token = localStorage.getItem('access_token');

  const response = fetch(`${baseURL}/api/v1/chat/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      content,
      bot_type: botType,
      conversation_id: conversationId || undefined,
      confirmed_message_id: confirmedMessageId || undefined,
    }),
    signal: controller.signal,
  });

  return {
    response,
    abort: () => controller.abort(),
  };
}
