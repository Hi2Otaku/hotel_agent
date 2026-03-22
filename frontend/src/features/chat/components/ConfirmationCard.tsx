import { Button } from '@/components/ui/button';
import type { PendingConfirmation } from '../types/chat';

interface ConfirmationCardProps {
  confirmation: PendingConfirmation;
  onConfirm: (messageId: string) => void;
  onDismiss: () => void;
}

const ACTION_LABELS: Record<string, string> = {
  book: 'Confirm Booking',
  cancel: 'Confirm Cancellation',
  modify: 'Confirm Changes',
};

export function ConfirmationCard({
  confirmation,
  onConfirm,
  onDismiss,
}: ConfirmationCardProps) {
  const confirmLabel =
    ACTION_LABELS[confirmation.action] || 'Confirm';

  return (
    <div className="my-2 rounded-lg border border-[#FDE68A] bg-[#FEF3C7] p-4">
      <p className="mb-3 text-sm text-slate-700">
        {confirmation.description}
      </p>
      <div className="flex gap-2">
        <Button
          size="sm"
          className="bg-[#0F766E] text-white hover:bg-[#0F766E]/90"
          onClick={() => onConfirm(confirmation.message_id)}
        >
          {confirmLabel}
        </Button>
        <Button size="sm" variant="outline" onClick={onDismiss}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
