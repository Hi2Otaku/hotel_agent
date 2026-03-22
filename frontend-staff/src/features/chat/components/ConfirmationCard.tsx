import { Button } from '@/components/ui/button';
import type { PendingConfirmation } from '../types/chat';

interface ConfirmationCardProps {
  confirmation: PendingConfirmation;
  onConfirm: (messageId: string) => void;
  onDismiss: () => void;
}

function getButtonLabels(action: string): { confirm: string; dismiss: string } {
  switch (action) {
    case 'check_in':
      return { confirm: 'Confirm Check-in', dismiss: "Don't Check In" };
    case 'check_out':
      return { confirm: 'Confirm Check-out', dismiss: "Don't Check Out" };
    case 'book':
      return { confirm: 'Confirm Booking', dismiss: 'Keep Shopping' };
    case 'cancel':
      return { confirm: 'Yes, Cancel', dismiss: 'Keep Booking' };
    case 'modify':
      return { confirm: 'Confirm Changes', dismiss: 'Keep Original Dates' };
    default:
      return { confirm: 'Confirm', dismiss: 'Cancel' };
  }
}

export function ConfirmationCard({
  confirmation,
  onConfirm,
  onDismiss,
}: ConfirmationCardProps) {
  const labels = getButtonLabels(confirmation.action);

  return (
    <div className="rounded-lg border bg-amber-900/20 border-amber-700/30 p-4">
      <p className="mb-3 text-sm text-foreground">{confirmation.description}</p>
      <div className="flex gap-2">
        <Button
          size="sm"
          onClick={() => onConfirm(confirmation.message_id)}
        >
          {labels.confirm}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onDismiss}
        >
          {labels.dismiss}
        </Button>
      </div>
    </div>
  );
}
