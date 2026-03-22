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
import { useCancelBooking } from '@/hooks/queries/useStaffBookings';
import type { BookingResponse } from '@/api/types';

interface CancelBookingDialogProps {
  booking: BookingResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CancelBookingDialog({
  booking,
  open,
  onOpenChange,
  onSuccess,
}: CancelBookingDialogProps) {
  const cancelBooking = useCancelBooking();

  const guestName = `${booking.guest_first_name} ${booking.guest_last_name}`;

  const handleConfirm = async () => {
    try {
      await cancelBooking.mutateAsync(booking.id);
      toast.success(`${guestName}'s reservation has been cancelled.`);
      onOpenChange(false);
      onSuccess?.();
    } catch {
      toast.error('Failed to cancel reservation. Please try again.');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="border-[#334155] bg-[#1E293B] text-[#F1F5F9]">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-[#F1F5F9]">
            Cancel reservation for {guestName}?
          </DialogTitle>
          <DialogDescription className="text-sm text-[#94A3B8]">
            Confirmation #{booking.confirmation_number} will be cancelled. This
            cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="border-[#334155] text-[#CBD5E1] hover:bg-[#283548]"
          >
            Keep Reservation
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={cancelBooking.isPending}
            className="bg-[#DC2626] text-white hover:bg-[#EF4444] disabled:opacity-30"
          >
            {cancelBooking.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Yes, Cancel Reservation'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
