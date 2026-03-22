import { Bot } from 'lucide-react';
import { StarterChips } from './StarterChips';

interface WelcomeMessageProps {
  onSendMessage: (message: string) => void;
}

export function WelcomeMessage({ onSendMessage }: WelcomeMessageProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
        <Bot className="h-6 w-6 text-primary" />
      </div>
      <div className="text-center">
        <h2 className="text-xl font-semibold text-foreground">
          Hi! I'm HB Ops
        </h2>
        <p className="mt-2 text-base text-muted-foreground">
          I can help you with check-ins, room status, guest lookups, reports, and daily operations.
        </p>
      </div>
      <StarterChips onSendMessage={onSendMessage} />
    </div>
  );
}
