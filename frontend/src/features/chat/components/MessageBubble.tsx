import { Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { formatDistanceToNow } from 'date-fns';
import { ToolStatusCard } from './ToolStatusCard';
import { ConfirmationCard } from './ConfirmationCard';
import { RoomCard } from './RoomCard';
import type { ChatMessage, ToolStatusState } from '../types/chat';

interface MessageBubbleProps {
  message: ChatMessage;
  toolStatuses?: ToolStatusState[];
  onConfirm?: (messageId: string) => void;
  onDismiss?: () => void;
  onSend?: (text: string) => void;
}

interface RoomResult {
  name: string;
  photo_url?: string;
  price_per_night: string;
  total_price?: string;
  description?: string;
  available_count?: number;
  max_adults?: number;
  bed_config?: Array<{ type: string; count: number }>;
  amenity_highlights?: string[];
}

function extractRoomCards(
  toolResults: unknown,
): RoomResult[] {
  if (!toolResults) return [];
  const rooms: RoomResult[] = [];

  // tool_results is stored as an array of {tool_id, result: {data: {...}, success}}
  const results = Array.isArray(toolResults) ? toolResults : [toolResults];
  for (const entry of results) {
    const data = entry?.result?.data;
    if (data && Array.isArray(data.results)) {
      for (const room of data.results) {
        if (room && typeof room === 'object' && 'name' in room) {
          rooms.push(room as RoomResult);
        }
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
