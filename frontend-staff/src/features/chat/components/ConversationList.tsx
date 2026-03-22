import { useState, useCallback, type KeyboardEvent } from 'react';
import { formatDistanceToNow } from 'date-fns';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { MoreVertical } from 'lucide-react';
import type { Conversation } from '../types/chat';

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onRename,
  onDelete,
}: ConversationListProps) {
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const startRename = useCallback((conv: Conversation) => {
    setRenamingId(conv.id);
    setRenameValue(conv.title || '');
  }, []);

  const commitRename = useCallback(() => {
    if (renamingId && renameValue.trim()) {
      onRename(renamingId, renameValue.trim());
    }
    setRenamingId(null);
  }, [renamingId, renameValue, onRename]);

  const handleRenameKey = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') commitRename();
      if (e.key === 'Escape') setRenamingId(null);
    },
    [commitRename],
  );

  if (conversations.length === 0) {
    return (
      <p className="px-4 py-8 text-center text-sm text-muted-foreground">
        No conversations yet
      </p>
    );
  }

  return (
    <div role="listbox" aria-label="Conversations" className="flex flex-col gap-0.5">
      {conversations.map((conv) => {
        const isActive = conv.id === activeId;
        return (
          <div
            key={conv.id}
            role="option"
            aria-selected={isActive}
            onClick={() => onSelect(conv.id)}
            className={`group flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
              isActive
                ? 'border-l-[4px] border-primary bg-primary/10'
                : 'hover:bg-[hsl(217.2,32.6%,17.5%)]'
            }`}
          >
            {renamingId === conv.id ? (
              <input
                autoFocus
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onBlur={commitRename}
                onKeyDown={handleRenameKey}
                className="flex-1 rounded border border-border bg-background px-1 py-0.5 text-sm text-foreground outline-none"
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-sm text-foreground">
                  {conv.title || 'New conversation'}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
                </p>
              </div>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  onClick={(e) => e.stopPropagation()}
                  className="shrink-0 rounded p-1 opacity-0 hover:bg-muted group-hover:opacity-100"
                  aria-label="Conversation options"
                >
                  <MoreVertical className="h-3.5 w-3.5 text-muted-foreground" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => startRename(conv)}>
                  Rename
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="text-destructive"
                  onClick={() => setDeleteId(conv.id)}
                >
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        );
      })}

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete conversation</DialogTitle>
            <DialogDescription>
              Delete this conversation? Chat history will be permanently removed.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Keep Conversation
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (deleteId) onDelete(deleteId);
                setDeleteId(null);
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
