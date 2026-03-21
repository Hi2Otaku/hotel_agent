import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { format, differenceInDays, parseISO } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useCheckOut } from '@/hooks/queries/useStaffBookings';
import type { BookingResponse } from '@/api/types';

interface CheckOutDialogProps {
  booking: BookingResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CheckOutDialog({
  booking,
  open,
  onOpenChange,
  onSuccess,
}: CheckOutDialogProps) {
  const checkOut = useCheckOut();

  const guestName = `${booking.guest_first_name} ${booking.guest_last_name}`;
  const roomLabel = booking.room_id
    ? `Room ${booking.room_id}`
    : null;

  const checkInDate = parseISO(booking.check_in);
  const checkOutDate = parseISO(booking.check_out);
  const nights = differenceInDays(checkOutDate, checkInDate);

  const handleConfirm = async () => {
    try {
      await checkOut.mutateAsync(booking.id);
      const roomMsg = roomLabel ? ` Room ${booking.room_id} marked for cleaning.` : '';
      toast.success(`${guestName} checked out.${roomMsg}`);
      onOpenChange(false);
      onSuccess?.();
    } catch {
      toast.error('Something went wrong. Please try again.');
    }
  };

  const title = roomLabel
    ? `Check out ${guestName} from ${roomLabel}`
    : `Check out ${guestName}`;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="border-[#334155] bg-[#1E293B] text-[#F1F5F9]">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-[#F1F5F9]">
            {title}
          </DialogTitle>
          <DialogDescription className="text-sm text-[#94A3B8]">
            <span className="font-mono">{booking.confirmation_number}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <h3 className="text-sm font-semibold text-[#F1F5F9]">
            Stay Summary
          </h3>
          <div className="space-y-2 rounded-lg border border-[#334155] bg-[#0F172A] p-4">
            <div className="flex justify-between text-sm">
              <span className="text-[#94A3B8]">Check-in</span>
              <span className="text-[#F1F5F9]">
                {format(checkInDate, 'MMM d, yyyy')}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#94A3B8]">Check-out</span>
              <span className="text-[#F1F5F9]">
                {format(checkOutDate, 'MMM d, yyyy')}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#94A3B8]">Nights</span>
              <span className="text-[#F1F5F9]">{nights}</span>
            </div>
            {booking.total_price && (
              <div className="flex justify-between border-t border-[#334155] pt-2 text-sm font-semibold">
                <span className="text-[#94A3B8]">Total</span>
                <span className="text-[#F1F5F9]">
                  {booking.currency === 'USD' ? '$' : booking.currency}
                  {booking.total_price}
                </span>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="border-[#334155] text-[#CBD5E1] hover:bg-[#283548]"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={checkOut.isPending}
            className="bg-[#0F766E] text-white hover:bg-[#0D9488] disabled:opacity-30"
          >
            {checkOut.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Confirm Check-out'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
