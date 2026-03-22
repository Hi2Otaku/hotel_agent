import { Bot } from 'lucide-react';

interface TypingIndicatorProps {
  statusText?: string;
}

export function TypingIndicator({ statusText }: TypingIndicatorProps) {
  return (
    <div className="flex items-start gap-2 px-4 py-2">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#F0FDFA]">
        <Bot className="size-4 text-[#0F766E]" />
      </div>
      <div>
        <div className="inline-flex items-center gap-1 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] px-4 py-3">
          <span
            className="size-2 rounded-full bg-slate-400 motion-safe:animate-bounce"
            style={{ animationDelay: '0s' }}
          />
          <span
            className="size-2 rounded-full bg-slate-400 motion-safe:animate-bounce"
            style={{ animationDelay: '0.2s' }}
          />
          <span
            className="size-2 rounded-full bg-slate-400 motion-safe:animate-bounce"
            style={{ animationDelay: '0.4s' }}
          />
        </div>
        <p className="mt-1 text-sm italic text-[#64748B]" aria-live="polite">
          {statusText || 'Thinking...'}
        </p>
        <span className="sr-only">Assistant is typing</span>
      </div>
    </div>
  );
}
