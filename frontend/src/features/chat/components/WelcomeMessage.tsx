import { Bot } from 'lucide-react';
import { StarterChips } from './StarterChips';

interface WelcomeMessageProps {
  onSend: (message: string) => void;
}

export function WelcomeMessage({ onSend }: WelcomeMessageProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4">
      <div className="flex size-12 items-center justify-center rounded-full bg-[#F0FDFA]">
        <Bot className="size-6 text-[#0F766E]" />
      </div>
      <div className="text-center">
        <h2 className="text-xl font-semibold text-slate-900">
          Hi! I'm HotelBook Assistant
        </h2>
        <p className="mt-2 text-base text-[#64748B]">
          I can help you search rooms, make bookings, manage reservations, or
          answer questions about our hotel.
        </p>
      </div>
      <StarterChips onSend={onSend} />
    </div>
  );
}
