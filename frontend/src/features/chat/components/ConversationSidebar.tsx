import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ConversationList } from './ConversationList';
import {
  useConversations,
  useRenameConversation,
  useDeleteConversation,
} from '../hooks/useConversations';
import { useChatStore } from '../stores/chatStore';

export function ConversationSidebar() {
  const { data: conversations = [] } = useConversations();
  const renameMutation = useRenameConversation();
  const deleteMutation = useDeleteConversation();
  const { currentConversationId, setCurrentConversation, clearChat } =
    useChatStore();

  const handleNewChat = () => {
    clearChat();
  };

  const handleSelect = (id: string) => {
    setCurrentConversation(id);
  };

  const handleRename = (id: string, title: string) => {
    renameMutation.mutate({ id, title });
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
    if (currentConversationId === id) {
      clearChat();
    }
  };

  return (
    <div className="flex h-full w-[280px] flex-col border-r bg-[#F8FAFC]">
      <div className="p-3">
        <Button
          variant="outline"
          className="w-full border-[#0F766E] text-[#0F766E] hover:bg-[#0F766E]/5"
          onClick={handleNewChat}
        >
          <Plus className="mr-2 size-4" />
          New Chat
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <ConversationList
          conversations={conversations}
          activeId={currentConversationId}
          onSelect={handleSelect}
          onRename={handleRename}
          onDelete={handleDelete}
        />
      </ScrollArea>
    </div>
  );
}
