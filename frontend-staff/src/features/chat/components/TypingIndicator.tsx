import { Bot } from 'lucide-react';

interface TypingIndicatorProps {
  statusText?: string;
}

export function TypingIndicator({ statusText }: TypingIndicatorProps) {
  return (
    <div className="flex gap-2" aria-live="polite">
      <span className="sr-only">Assistant is typing</span>
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[hsl(217.2,32.6%,17.5%)] border border-[hsl(217.2,32.6%,29.4%)]">
        <Bot className="h-4 w-4 text-muted-foreground" />
      </div>
      <div>
        <div className="inline-flex items-center gap-1 rounded-xl bg-[hsl(217.2,32.6%,17.5%)] border border-[hsl(217.2,32.6%,29.4%)] px-4 py-3">
          <span className="h-2 w-2 rounded-full bg-muted-foreground motion-safe:animate-bounce" style={{ animationDelay: '0s' }} />
          <span className="h-2 w-2 rounded-full bg-muted-foreground motion-safe:animate-bounce" style={{ animationDelay: '0.2s' }} />
          <span className="h-2 w-2 rounded-full bg-muted-foreground motion-safe:animate-bounce" style={{ animationDelay: '0.4s' }} />
        </div>
        {statusText && (
          <p className="mt-1 text-sm italic text-muted-foreground">
            {statusText || 'Thinking...'}
          </p>
        )}
        {!statusText && (
          <p className="mt-1 text-sm italic text-muted-foreground">Thinking...</p>
        )}
      </div>
    </div>
  );
}
