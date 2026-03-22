import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useCancelBooking, useCancellationPolicy } from '@/hooks/queries/useBookings';
import { formatCurrency } from '@/lib/formatters';

interface CancelDialogProps {
  bookingId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CancelDialog({
  bookingId,
  open,
  onOpenChange,
  onSuccess,
}: CancelDialogProps) {
  const { data: policy } = useCancellationPolicy(open ? bookingId : null);
  const cancelMutation = useCancelBooking();

  const isFreeCancel =
    policy?.free_cancellation_before &&
    new Date(policy.free_cancellation_before) > new Date();

  const handleCancel = () => {
    cancelMutation.mutate(bookingId, {
      onSuccess: () => {
        toast.success('Booking cancelled successfully');
        onOpenChange(false);
        onSuccess();
      },
      onError: () => {
        toast.error('Something went wrong. Please try again in a moment.');
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Cancel Booking</DialogTitle>
          <DialogDescription>
            Are you sure you want to cancel this booking? This action cannot be
            undone.
          </DialogDescription>
        </DialogHeader>

        {policy && (
          <div className="text-sm">
            {isFreeCancel ? (
              <p className="text-green-600 font-medium">
                Free cancellation available.
              </p>
            ) : policy.cancellation_fee ? (
              <p className="text-amber-600 font-medium">
                A cancellation fee of {formatCurrency(policy.cancellation_fee)}{' '}
                will apply.
              </p>
            ) : (
              <p className="text-muted-foreground">{policy.policy_text}</p>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Keep Booking
          </Button>
          <Button
            className="bg-destructive text-white hover:bg-destructive-hover"
            onClick={handleCancel}
            disabled={cancelMutation.isPending}
          >
            {cancelMutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Yes, Cancel Booking
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
