import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  heading: string;
  body: string;
}

export function EmptyState({ heading, body }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Inbox className="mb-4 h-12 w-12 text-[#94A3B8]" />
      <h2 className="mb-2 text-xl font-semibold text-[#F1F5F9]">{heading}</h2>
      <p className="max-w-md text-sm text-[#94A3B8]">{body}</p>
    </div>
  );
}
