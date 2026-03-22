import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { ToolStatusCard } from './ToolStatusCard';
import { ConfirmationCard } from './ConfirmationCard';
import type { ChatMessage, ToolStatusState, PendingConfirmation } from '../types/chat';

interface MessageBubbleProps {
  message: ChatMessage;
  toolStatuses?: ToolStatusState[];
  pendingConfirmation?: PendingConfirmation | null;
  onConfirm?: (messageId: string) => void;
  onDismiss?: () => void;
}

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function MessageBubble({
  message,
  toolStatuses,
  pendingConfirmation,
  onConfirm,
  onDismiss,
}: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'} max-w-[75%] md:max-w-[75%] max-[768px]:max-w-[85%]`}
    >
      {/* Bot avatar */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[hsl(217.2,32.6%,17.5%)] border border-[hsl(217.2,32.6%,29.4%)]">
          <Bot className="h-4 w-4 text-muted-foreground" />
        </div>
      )}

      <div className="flex flex-col gap-1">
        <Tooltip>
          <TooltipTrigger asChild>
            <div
              className={`rounded-xl px-3 py-2 text-base ${
                isUser
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-[hsl(217.2,32.6%,17.5%)] border border-[hsl(217.2,32.6%,29.4%)] text-foreground'
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-invert prose-sm max-w-none [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_li]:my-0 [&_code]:bg-background/50 [&_code]:px-1 [&_code]:rounded [&_pre]:bg-background/50 [&_pre]:p-2 [&_pre]:rounded-md [&_a]:text-primary [&_a]:underline">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content || ''}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="text-xs text-muted-foreground">
            {formatTime(message.created_at)}
          </TooltipContent>
        </Tooltip>

        {/* Tool statuses */}
        {toolStatuses && toolStatuses.length > 0 && (
          <div className="mt-1 flex flex-col gap-1">
            {toolStatuses.map((ts) => (
              <ToolStatusCard key={ts.tool_id} status={ts} />
            ))}
          </div>
        )}

        {/* Confirmation card */}
        {pendingConfirmation && onConfirm && onDismiss && (
          <div className="mt-1">
            <ConfirmationCard
              confirmation={pendingConfirmation}
              onConfirm={onConfirm}
              onDismiss={onDismiss}
            />
          </div>
        )}
      </div>
    </div>
  );
}
