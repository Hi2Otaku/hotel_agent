import { useCallback } from 'react';
import { Menu } from 'lucide-react';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ConversationSidebar } from './components/ConversationSidebar';
import { ChatArea } from './components/ChatArea';
import { useChatStore } from './stores/chatStore';
import { useChat } from './hooks/useChat';
import {
  useConversations,
  useMessages,
  useRenameConversation,
  useDeleteConversation,
} from './hooks/useConversations';

export function ChatLayout() {
  const {
    currentConversationId,
    messages,
    isStreaming,
    toolStatuses,
    pendingConfirmation,
    setCurrentConversation,
    setMessages,
    clearChat,
    setPendingConfirmation,
  } = useChatStore();

  const { sendMessage, confirmAction } = useChat();
  const { data: conversations = [] } = useConversations();
  const { data: loadedMessages } = useMessages(currentConversationId);
  const renameMutation = useRenameConversation();
  const deleteMutation = useDeleteConversation();

  // Sync loaded messages when conversation changes
  const displayMessages =
    currentConversationId && loadedMessages && messages.length === 0
      ? loadedMessages
      : messages;

  const handleSelectConversation = useCallback(
    (id: string) => {
      setCurrentConversation(id);
      setMessages([]);
    },
    [setCurrentConversation, setMessages],
  );

  const handleNewChat = useCallback(() => {
    clearChat();
  }, [clearChat]);

  const handleRename = useCallback(
    (id: string, title: string) => {
      renameMutation.mutate({ id, title });
    },
    [renameMutation],
  );

  const handleDelete = useCallback(
    (id: string) => {
      deleteMutation.mutate(id);
      if (currentConversationId === id) {
        clearChat();
      }
    },
    [deleteMutation, currentConversationId, clearChat],
  );

  const handleDismiss = useCallback(() => {
    setPendingConfirmation(null);
  }, [setPendingConfirmation]);

  const sidebar = (
    <ConversationSidebar
      conversations={conversations}
      activeId={currentConversationId}
      onSelect={handleSelectConversation}
      onNewChat={handleNewChat}
      onRename={handleRename}
      onDelete={handleDelete}
    />
  );

  return (
    <div className="flex h-full">
      {/* Desktop sidebar */}
      <div className="hidden md:block">{sidebar}</div>

      {/* Mobile sidebar trigger + sheet */}
      <div className="flex flex-col md:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-2 top-2 z-10 md:hidden"
              aria-label="Open conversations"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[280px] p-0 bg-card border-border">
            {sidebar}
          </SheetContent>
        </Sheet>
      </div>

      {/* Chat area */}
      <ChatArea
        messages={displayMessages}
        isStreaming={isStreaming}
        toolStatuses={toolStatuses}
        pendingConfirmation={pendingConfirmation}
        onSendMessage={sendMessage}
        onConfirm={confirmAction}
        onDismiss={handleDismiss}
      />
    </div>
  );
}
