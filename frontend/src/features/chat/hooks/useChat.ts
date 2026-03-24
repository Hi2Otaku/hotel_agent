import { useCallback, useRef, useState } from 'react';
import { createParser, type EventSourceMessage } from 'eventsource-parser';
import { toast } from 'sonner';
import { useChatStore } from '../stores/chatStore';
import { sendMessageStream } from '../api/chatApi';
import type { SSEEvent, ChatMessage } from '../types/chat';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';

const STAFF_ROLES = new Set(['admin', 'manager', 'front_desk', 'housekeeping']);

export function useChat() {
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<(() => void) | null>(null);
  const queryClient = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const botType = user?.role && STAFF_ROLES.has(user.role) ? 'staff' : 'guest';

  const {
    currentConversationId,
    isStreaming,
    addMessage,
    appendToLastMessage,
    setStreaming,
    addToolStatus,
    updateToolStatus,
    appendToolResult,
    clearToolStatuses,
    setPendingConfirmation,
    setCurrentConversation,
  } = useChatStore();

  const processSSEEvent = useCallback(
    (event: SSEEvent, assistantMsgRef: { id: string }) => {
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
          appendToolResult(event.tool_id, '', event.data, event.success);
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
          assistantMsgRef.id = event.message_id;
          if (event.conversation_id) {
            setCurrentConversation(event.conversation_id);
          }
          clearToolStatuses();
          setStreaming(false);
          queryClient.invalidateQueries({ queryKey: ['conversations'] });
          break;
        case 'error':
          toast.error(event.message);
          setStreaming(false);
          setError(event.message);
          break;
      }
    },
    [
      appendToLastMessage,
      addToolStatus,
      updateToolStatus,
      appendToolResult,
      clearToolStatuses,
      setPendingConfirmation,
      setStreaming,
      queryClient,
    ],
  );

  const handleStream = useCallback(
    async (
      response: Response,
      assistantMsgRef: { id: string },
    ) => {
      if (!response.ok) {
        const text = await response.text();
        toast.error(text || `Error: ${response.status}`);
        setStreaming(false);
        return;
      }

      const body = response.body;
      if (!body) {
        setStreaming(false);
        return;
      }

      const parser = createParser({
        onEvent: (event: EventSourceMessage) => {
          try {
            const data = JSON.parse(event.data) as SSEEvent;
            processSSEEvent(data, assistantMsgRef);
          } catch {
            // ignore malformed events
          }
        },
      });

      const reader = body.getReader();
      const decoder = new TextDecoder();

      try {
        let done = false;
        while (!done) {
          const result = await reader.read();
          done = result.done;
          if (result.value) {
            parser.feed(decoder.decode(result.value, { stream: true }));
          }
        }
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          toast.error('Connection lost. Please try again.');
          setStreaming(false);
        }
      }
    },
    [processSSEEvent, setStreaming],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (isStreaming) return;
      setError(null);

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        tool_calls: null,
        tool_results: null,
        pending_confirmation: null,
        created_at: new Date().toISOString(),
      };
      addMessage(userMsg);
      setStreaming(true);

      const { response, abort } = sendMessageStream(
        content,
        botType,
        currentConversationId ?? undefined,
      );
      abortRef.current = abort;

      try {
        const res = await response;

        // Add empty assistant message only after response starts
        const assistantMsgRef = { id: crypto.randomUUID() };
        const assistantMsg: ChatMessage = {
          id: assistantMsgRef.id,
          role: 'assistant',
          content: '',
          tool_calls: null,
          tool_results: null,
          pending_confirmation: null,
          created_at: new Date().toISOString(),
          isStreaming: true,
        };
        addMessage(assistantMsg);

        await handleStream(res, assistantMsgRef);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          toast.error('Failed to send message. Please try again.');
          setStreaming(false);
        }
      }
    },
    [
      isStreaming,
      currentConversationId,
      botType,
      addMessage,
      setStreaming,
      handleStream,
      setCurrentConversation,
    ],
  );

  const confirmAction = useCallback(
    async (messageId: string) => {
      if (isStreaming) return;
      setError(null);
      setPendingConfirmation(null);
      setStreaming(true);

      const { response, abort } = sendMessageStream(
        '',
        botType,
        currentConversationId ?? undefined,
        messageId,
      );
      abortRef.current = abort;

      try {
        const res = await response;

        const assistantMsgRef = { id: crypto.randomUUID() };
        const assistantMsg: ChatMessage = {
          id: assistantMsgRef.id,
          role: 'assistant',
          content: '',
          tool_calls: null,
          tool_results: null,
          pending_confirmation: null,
          created_at: new Date().toISOString(),
          isStreaming: true,
        };
        addMessage(assistantMsg);

        await handleStream(res, assistantMsgRef);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          toast.error('Failed to confirm action. Please try again.');
          setStreaming(false);
        }
      }
    },
    [
      isStreaming,
      currentConversationId,
      botType,
      addMessage,
      setStreaming,
      handleStream,
      setPendingConfirmation,
    ],
  );

  return { sendMessage, confirmAction, isStreaming, error };
}
