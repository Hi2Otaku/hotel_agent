import { useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { ScrollToBottom } from './ScrollToBottom';
import { useAutoScroll } from '../hooks/useAutoScroll';
import type { ChatMessage, ToolStatusState, PendingConfirmation } from '../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  toolStatuses: ToolStatusState[];
  pendingConfirmation: PendingConfirmation | null;
  onConfirm: (messageId: string) => void;
  onDismiss: () => void;
}

export function MessageList({
  messages,
  isStreaming,
  toolStatuses,
  pendingConfirmation,
  onConfirm,
  onDismiss,
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { isAtBottom, scrollToBottom } = useAutoScroll(containerRef, [messages, isStreaming]);

  return (
    <div className="relative flex-1">
      <div
        ref={containerRef}
        role="log"
        aria-live="polite"
        className="absolute inset-0 overflow-y-auto px-6 py-4"
      >
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {messages.map((msg, i) => {
            const isLastAssistant =
              msg.role === 'assistant' && i === messages.length - 1;
            return (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <MessageBubble
                  message={msg}
                  toolStatuses={isLastAssistant ? toolStatuses : undefined}
                  pendingConfirmation={
                    isLastAssistant ? pendingConfirmation : undefined
                  }
                  onConfirm={onConfirm}
                  onDismiss={onDismiss}
                />
              </div>
            );
          })}
          {isStreaming && messages[messages.length - 1]?.content === '' && (
            <TypingIndicator
              statusText={
                toolStatuses.find((t) => t.status === 'running')?.description
              }
            />
          )}
        </div>
      </div>
      <ScrollToBottom visible={!isAtBottom} onClick={scrollToBottom} />
    </div>
  );
}
