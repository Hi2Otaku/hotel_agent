import { useEffect } from 'react';
import { WelcomeMessage } from './WelcomeMessage';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '../hooks/useChat';
import { useMessages } from '../hooks/useConversations';
import { useChatStore } from '../stores/chatStore';

export function ChatArea() {
  const { sendMessage, confirmAction, isStreaming } = useChat();
  const {
    currentConversationId,
    messages,
    pendingConfirmation,
    setMessages,
    setPendingConfirmation,
  } = useChatStore();

  // Load messages when conversation changes
  const { data: historicMessages } = useMessages(currentConversationId);

  useEffect(() => {
    if (historicMessages) {
      setMessages(historicMessages);
    }
  }, [historicMessages, setMessages]);

  const showWelcome = !currentConversationId && messages.length === 0;

  const handleDismissConfirmation = () => {
    setPendingConfirmation(null);
    sendMessage('Never mind, cancel that.');
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {showWelcome ? (
        <WelcomeMessage onSend={sendMessage} />
      ) : (
        <>
          <MessageList
            messages={messages}
            isStreaming={isStreaming}
            onConfirm={confirmAction}
            onDismiss={handleDismissConfirmation}
            onSend={sendMessage}
          />
          {pendingConfirmation && null /* handled inline in MessageBubble */}
        </>
      )}
      <MessageInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
