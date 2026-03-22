import { Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { formatDistanceToNow } from 'date-fns';
import { ToolStatusCard } from './ToolStatusCard';
import { ConfirmationCard } from './ConfirmationCard';
import { RoomCard } from './RoomCard';
import type { ChatMessage, ToolStatusState, RoomCardData } from '../types/chat';

interface MessageBubbleProps {
  message: ChatMessage;
  toolStatuses?: ToolStatusState[];
  onConfirm?: (messageId: string) => void;
  onDismiss?: () => void;
  onSend?: (text: string) => void;
}

function extractRoomCards(
  toolResults: Record<string, unknown> | null,
): RoomCardData[] {
  if (!toolResults) return [];
  const rooms: RoomCardData[] = [];
  // tool_results may contain room search data in various formats
  const data = toolResults.data ?? toolResults;
  if (Array.isArray(data)) {
    for (const item of data) {
      if (item && typeof item === 'object' && 'name' in item) {
        rooms.push(item as RoomCardData);
      }
    }
  }
  return rooms;
}

export function MessageBubble({
  message,
  toolStatuses = [],
  onConfirm,
  onDismiss,
  onSend,
}: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const roomCards = extractRoomCards(message.tool_results);
  const timestamp = formatDistanceToNow(new Date(message.created_at), {
    addSuffix: true,
  });

  return (
    <div
      className={`group flex w-full gap-2 px-4 py-2 ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Bot avatar */}
      {!isUser && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#F0FDFA]">
          <Bot className="size-4 text-[#0F766E]" />
        </div>
      )}

      <div
        className={`max-w-[75%] md:max-w-[75%] ${
          isUser ? 'max-w-[85%] md:max-w-[75%]' : ''
        }`}
      >
        {/* Message bubble */}
        <div
          className={`rounded-xl px-4 py-2.5 ${
            isUser
              ? 'bg-[#0F766E] text-white'
              : 'border border-[#E2E8F0] bg-[#F8FAFC] text-slate-900'
          }`}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none text-slate-900 prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content || ''}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Timestamp on hover */}
        <p
          className={`mt-1 text-xs text-[#64748B] opacity-0 transition-opacity group-hover:opacity-100 ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {timestamp}
        </p>

        {/* Tool status cards */}
        {toolStatuses.map((ts) => (
          <ToolStatusCard key={ts.tool_id} status={ts} />
        ))}

        {/* Room cards from tool results */}
        {roomCards.map((room) => (
          <RoomCard
            key={room.id}
            room={room}
            onBook={(name) => onSend?.(`Book ${name}`)}
          />
        ))}

        {/* Confirmation card */}
        {message.pending_confirmation && onConfirm && onDismiss && (
          <ConfirmationCard
            confirmation={message.pending_confirmation}
            onConfirm={onConfirm}
            onDismiss={onDismiss}
          />
        )}
      </div>
    </div>
  );
}
