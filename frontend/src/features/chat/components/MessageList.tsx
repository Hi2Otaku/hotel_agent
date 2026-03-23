import { useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { ScrollToBottom } from './ScrollToBottom';
import { useAutoScroll } from '../hooks/useAutoScroll';
import { useChatStore } from '../stores/chatStore';
import type { ChatMessage } from '../types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onConfirm: (messageId: string) => void;
  onDismiss: () => void;
  onSend: (text: string) => void;
}

export function MessageList({
  messages,
  isStreaming,
  onConfirm,
  onDismiss,
  onSend,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const toolStatuses = useChatStore((s) => s.toolStatuses);
  const { isAtBottom, scrollToBottom } = useAutoScroll(scrollRef, [
    messages,
    isStreaming,
  ]);

  return (
    <div className="relative flex-1 overflow-hidden">
      <div
        ref={scrollRef}
        role="log"
        aria-live="polite"
        className="h-full overflow-y-auto py-4"
      >
        {messages.map((msg, idx) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            toolStatuses={
              msg.role === 'assistant' &&
              msg.isStreaming &&
              idx === messages.length - 1
                ? toolStatuses
                : []
            }
            onConfirm={onConfirm}
            onDismiss={onDismiss}
            onSend={onSend}
          />
        ))}
        {isStreaming && messages[messages.length - 1]?.content === '' && (
          <TypingIndicator />
        )}
      </div>
      <ScrollToBottom visible={!isAtBottom} onClick={scrollToBottom} />
    </div>
  );
}
