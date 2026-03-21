import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import { CalendarIcon, Loader2 } from 'lucide-react';
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
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useModifyBooking } from '@/hooks/queries/useBookings';
import { formatCurrency } from '@/lib/formatters';
import type { BookingResponse, BookingModifyRequest } from '@/api/types';
import { cn } from '@/lib/utils';

interface ModifyDialogProps {
  booking: BookingResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function ModifyDialog({
  booking,
  open,
  onOpenChange,
  onSuccess,
}: ModifyDialogProps) {
  const [checkIn, setCheckIn] = useState<Date>(parseISO(booking.check_in));
  const [checkOut, setCheckOut] = useState<Date>(parseISO(booking.check_out));
  const [guestCount, setGuestCount] = useState<number>(booking.guest_count);
  const [conflictError, setConflictError] = useState<string | null>(null);

  const modifyMutation = useModifyBooking();

  const handleSubmit = () => {
    setConflictError(null);

    const changes: BookingModifyRequest = {};
    const newCheckIn = format(checkIn, 'yyyy-MM-dd');
    const newCheckOut = format(checkOut, 'yyyy-MM-dd');

    if (newCheckIn !== booking.check_in) changes.check_in = newCheckIn;
    if (newCheckOut !== booking.check_out) changes.check_out = newCheckOut;
    if (guestCount !== booking.guest_count) changes.guest_count = guestCount;

    if (Object.keys(changes).length === 0) {
      onOpenChange(false);
      return;
    }

    modifyMutation.mutate(
      { id: booking.id, data: changes },
      {
        onSuccess: (result) => {
          const oldTotal = result.old_total ?? booking.total_price ?? '0';
          const newTotal = result.new_total ?? oldTotal;
          const price_difference = result.price_difference ?? '0';
          const diff = parseFloat(price_difference);
          const diffStr =
            diff >= 0
              ? `+${formatCurrency(diff)}`
              : formatCurrency(diff);

          toast.success(
            `Booking modified. Price changed from ${formatCurrency(oldTotal)} to ${formatCurrency(newTotal)} (${diffStr}).`
          );
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          if (
            error &&
            typeof error === 'object' &&
            'response' in error &&
            (error as { response?: { status?: number } }).response?.status === 409
          ) {
            setConflictError(
              'This room is no longer available for the new dates.'
            );
          } else {
            toast.error('Something went wrong. Please try again in a moment.');
          }
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Modify Booking</DialogTitle>
          <DialogDescription>
            Update your booking dates or guest count.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-2">
          {/* Check-in date */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">New Check-in Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'min-h-[44px] w-full justify-start text-left font-normal',
                    !checkIn && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {checkIn ? format(checkIn, 'PPP') : 'Select date'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={checkIn}
                  onSelect={(date) => date && setCheckIn(date)}
                  disabled={(date) => date < new Date()}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Check-out date */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">New Check-out Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'min-h-[44px] w-full justify-start text-left font-normal',
                    !checkOut && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {checkOut ? format(checkOut, 'PPP') : 'Select date'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={checkOut}
                  onSelect={(date) => date && setCheckOut(date)}
                  disabled={(date) => date <= checkIn}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Guest count */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Guests</label>
            <Select
              value={String(guestCount)}
              onValueChange={(val) => setGuestCount(Number(val))}
            >
              <SelectTrigger className="min-h-[44px] w-full">
                <SelectValue placeholder="Select guest count" />
              </SelectTrigger>
              <SelectContent>
                {[1, 2, 3, 4, 5, 6].map((n) => (
                  <SelectItem key={n} value={String(n)}>
                    {n} {n === 1 ? 'Guest' : 'Guests'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {conflictError && (
            <p className="text-sm font-medium text-red-600">{conflictError}</p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            className="bg-[#0F766E] text-white hover:bg-[#0D6660]"
            onClick={handleSubmit}
            disabled={modifyMutation.isPending}
          >
            {modifyMutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
