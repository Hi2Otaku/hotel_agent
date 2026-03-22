import { WelcomeMessage } from './WelcomeMessage';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import type { ChatMessage, ToolStatusState, PendingConfirmation } from '../types/chat';

interface ChatAreaProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  toolStatuses: ToolStatusState[];
  pendingConfirmation: PendingConfirmation | null;
  onSendMessage: (message: string) => void;
  onConfirm: (messageId: string) => void;
  onDismiss: () => void;
}

export function ChatArea({
  messages,
  isStreaming,
  toolStatuses,
  pendingConfirmation,
  onSendMessage,
  onConfirm,
  onDismiss,
}: ChatAreaProps) {
  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-1 flex-col bg-background">
      {hasMessages ? (
        <MessageList
          messages={messages}
          isStreaming={isStreaming}
          toolStatuses={toolStatuses}
          pendingConfirmation={pendingConfirmation}
          onConfirm={onConfirm}
          onDismiss={onDismiss}
        />
      ) : (
        <WelcomeMessage onSendMessage={onSendMessage} />
      )}
      <MessageInput onSend={onSendMessage} disabled={isStreaming} />
    </div>
  );
}
