import { useState, useRef, useCallback, type KeyboardEvent } from 'react';
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
import { MoreVertical, Pencil, Trash2 } from 'lucide-react';
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
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);

  const handleRenameSubmit = useCallback(
    (id: string) => {
      const value = renameInputRef.current?.value.trim();
      if (value) {
        onRename(id, value);
      }
      setRenamingId(null);
    },
    [onRename],
  );

  const handleRenameKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>, id: string) => {
      if (e.key === 'Enter') {
        handleRenameSubmit(id);
      } else if (e.key === 'Escape') {
        setRenamingId(null);
      }
    },
    [handleRenameSubmit],
  );

  if (conversations.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center px-4">
        <p className="text-sm text-slate-400">No conversations yet</p>
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col gap-0.5">
        {conversations.map((conv) => {
          const isActive = conv.id === activeId;
          return (
            <div
              key={conv.id}
              role="button"
              tabIndex={0}
              onClick={() => onSelect(conv.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelect(conv.id);
              }}
              className={`group flex cursor-pointer items-center justify-between px-3 py-2.5 transition-colors hover:bg-slate-100 ${
                isActive
                  ? 'border-l-4 border-[#0F766E] bg-teal-50/50'
                  : 'border-l-4 border-transparent'
              }`}
            >
              <div className="min-w-0 flex-1">
                {renamingId === conv.id ? (
                  <input
                    ref={renameInputRef}
                    defaultValue={conv.title || ''}
                    autoFocus
                    className="w-full rounded border px-1 py-0.5 text-sm"
                    onBlur={() => handleRenameSubmit(conv.id)}
                    onKeyDown={(e) => handleRenameKeyDown(e, conv.id)}
                  />
                ) : (
                  <>
                    <p className="truncate text-sm font-medium text-slate-700">
                      {conv.title || 'New conversation'}
                    </p>
                    <p className="text-xs text-slate-400">
                      {formatDistanceToNow(new Date(conv.updated_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </>
                )}
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="ml-1 rounded p-1 opacity-0 hover:bg-slate-200 group-hover:opacity-100"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <MoreVertical className="size-4 text-slate-400" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                      setRenamingId(conv.id);
                    }}
                  >
                    <Pencil className="mr-2 size-4" />
                    Rename
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteId(conv.id);
                    }}
                    className="text-red-600 focus:text-red-600"
                  >
                    <Trash2 className="mr-2 size-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          );
        })}
      </div>

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete this conversation?</DialogTitle>
            <DialogDescription>
              Chat history will be permanently removed.
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
    </>
  );
}
