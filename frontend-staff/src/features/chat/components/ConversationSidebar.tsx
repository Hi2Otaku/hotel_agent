import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ConversationList } from './ConversationList';
import type { Conversation } from '../types/chat';

interface ConversationSidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}

export function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  onRename,
  onDelete,
}: ConversationSidebarProps) {
  return (
    <div className="flex h-full w-[280px] flex-col border-r border-border bg-card">
      <div className="p-3">
        <Button
          variant="outline"
          className="w-full border-primary text-primary hover:bg-primary hover:text-primary-foreground"
          onClick={onNewChat}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-2 pb-2">
          <ConversationList
            conversations={conversations}
            activeId={activeId}
            onSelect={onSelect}
            onRename={onRename}
            onDelete={onDelete}
          />
        </div>
      </ScrollArea>
    </div>
  );
}
