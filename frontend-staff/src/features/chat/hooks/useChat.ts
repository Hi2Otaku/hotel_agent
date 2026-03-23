import { useCallback, useRef } from 'react';
import { createParser, type EventSourceMessage } from 'eventsource-parser';
import { toast } from 'sonner';
import { useChatStore } from '../stores/chatStore';
import { sendMessageStream } from '../api/chatApi';
import type { SSEEvent } from '../types/chat';

export function useChat() {
  const abortRef = useRef<(() => void) | null>(null);
  const {
    currentConversationId,
    isStreaming,
    addMessage,
    appendToLastMessage,
    setStreaming,
    addToolStatus,
    updateToolStatus,
    setPendingConfirmation,
    setCurrentConversation,
  } = useChatStore();

  const handleSSEEvent = useCallback(
    (event: SSEEvent) => {
      switch (event.type) {
        case 'text_delta':
          appendToLastMessage(event.text);
          break;
        case 'tool_start':
          addToolStatus({
            tool_id: event.tool_id,
            tool_name: event.tool_name,
            description: event.description,
            status: 'running',
          });
          break;
        case 'tool_result':
          updateToolStatus(event.tool_id, {
            status: event.success ? 'success' : 'error',
            data: event.data,
          });
          break;
        case 'confirmation_required':
          setPendingConfirmation({
            message_id: event.message_id,
            action: event.action,
            description: event.description,
            details: event.details,
          });
          break;
        case 'done':
          setStreaming(false);
          break;
        case 'error':
          toast.error(event.message);
          setStreaming(false);
          break;
      }
    },
    [appendToLastMessage, addToolStatus, updateToolStatus, setPendingConfirmation, setStreaming],
  );

  const processStream = useCallback(
    async (response: Response) => {
      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      const parser = createParser({
        onEvent: (event: EventSourceMessage) => {
          try {
            const data = JSON.parse(event.data) as SSEEvent;
            handleSSEEvent(data);

            // Extract conversation_id from done event if starting new conversation
            if (data.type === 'done' && 'conversation_id' in data && !currentConversationId) {
              setCurrentConversation((data as SSEEvent & { conversation_id: string }).conversation_id);
            }
          } catch {
            // Ignore malformed SSE data
          }
        },
      });

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          parser.feed(decoder.decode(value, { stream: true }));
        }
      } finally {
        reader.releaseLock();
      }
    },
    [handleSSEEvent, currentConversationId, setCurrentConversation],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (isStreaming || !content.trim()) return;

      // Add user message
      addMessage({
        id: crypto.randomUUID(),
        role: 'user',
        content,
        tool_calls: null,
        tool_results: null,
        pending_confirmation: null,
        created_at: new Date().toISOString(),
      });

      setStreaming(true);

      const { response, abort } = sendMessageStream(
        content,
        'staff',
        currentConversationId ?? undefined,
      );
      abortRef.current = abort;

      try {
        const res = await response;
        if (!res.ok) {
          const errorText = await res.text();
          toast.error(errorText || 'Failed to send message');
          setStreaming(false);
          return;
        }

        // Add empty assistant message only after response starts
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: '',
          tool_calls: null,
          tool_results: null,
          pending_confirmation: null,
          created_at: new Date().toISOString(),
          isStreaming: true,
        });

        await processStream(res);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          toast.error('Unable to connect. Check your connection and try again.');
          setStreaming(false);
        }
      }
    },
    [isStreaming, addMessage, setStreaming, currentConversationId, processStream],
  );

  const confirmAction = useCallback(
    async (messageId: string) => {
      if (isStreaming) return;

      setStreaming(true);
      setPendingConfirmation(null);

      const { response, abort } = sendMessageStream(
        '',
        'staff',
        currentConversationId ?? undefined,
        messageId,
      );
      abortRef.current = abort;

      try {
        const res = await response;
        if (!res.ok) {
          toast.error('Failed to confirm action');
          setStreaming(false);
          return;
        }

        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: '',
          tool_calls: null,
          tool_results: null,
          pending_confirmation: null,
          created_at: new Date().toISOString(),
          isStreaming: true,
        });

        await processStream(res);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          toast.error('Unable to connect. Check your connection and try again.');
          setStreaming(false);
        }
      }
    },
    [isStreaming, addMessage, setStreaming, setPendingConfirmation, currentConversationId, processStream],
  );

  return { sendMessage, confirmAction, isStreaming };
}
