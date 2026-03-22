import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { Loader2 } from 'lucide-react';
import { AxiosError } from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import { useCreateBooking } from '@/hooks/queries/useBookings';
import { formatCurrency, formatDateRange } from '@/lib/formatters';

export default function StepRoomSelection() {
  const navigate = useNavigate();
  const [conflictOpen, setConflictOpen] = useState(false);

  const selectedRoom = useBookingWizardStore((s) => s.selectedRoom);
  const checkIn = useBookingWizardStore((s) => s.checkIn);
  const checkOut = useBookingWizardStore((s) => s.checkOut);
  const guests = useBookingWizardStore((s) => s.guests);
  const setBookingId = useBookingWizardStore((s) => s.setBookingId);
  const setStep = useBookingWizardStore((s) => s.setStep);

  const createBooking = useCreateBooking();

  if (!selectedRoom || !checkIn || !checkOut) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-600 mb-4">Please search for a room first</p>
        <Link
          to="/search"
          className="text-accent hover:underline font-medium"
        >
          Search Rooms
        </Link>
      </div>
    );
  }

  function handleContinue() {
    if (!selectedRoom || !checkIn || !checkOut) return;
    createBooking.mutate(
      {
        room_type_id: selectedRoom.room_type_id,
        check_in: checkIn,
        check_out: checkOut,
        guest_count: guests,
      },
      {
        onSuccess: (booking) => {
          setBookingId(booking.id);
          setStep(2);
        },
        onError: (error) => {
          if (error instanceof AxiosError && error.response?.status === 409) {
            setConflictOpen(true);
          }
        },
      },
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-slate-900">Select Room</h2>

      <Card>
        <CardContent className="pt-4">
          {selectedRoom.photo_url && (
            <img
              src={selectedRoom.photo_url}
              alt={`${selectedRoom.name} room`}
              className="w-full aspect-video object-cover rounded-md mb-4"
            />
          )}
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            {selectedRoom.name}
          </h3>
          <div className="text-sm text-slate-600 space-y-1">
            <p>{formatDateRange(checkIn, checkOut)}</p>
            <p>{guests} guest{guests !== 1 ? 's' : ''}</p>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-lg font-semibold text-accent">
              {formatCurrency(selectedRoom.price_per_night)}
            </span>
            <span className="text-sm text-slate-500">/ night</span>
          </div>
          <div className="mt-1 text-sm text-slate-600">
            Total: {formatCurrency(selectedRoom.total_price)}
          </div>
        </CardContent>
      </Card>

      <p className="text-sm text-muted">
        Free cancellation up to 24 hours before check-in. Late cancellations are
        subject to a one-night charge.
      </p>

      <Button
        onClick={handleContinue}
        disabled={createBooking.isPending}
        className="w-full min-h-[44px] bg-accent hover:bg-accent-hover text-white"
      >
        {createBooking.isPending ? (
          <Loader2 className="animate-spin" />
        ) : (
          'Continue'
        )}
      </Button>

      <Dialog open={conflictOpen} onOpenChange={setConflictOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Room Unavailable</DialogTitle>
            <DialogDescription>
              This room is no longer available for your selected dates. Please
              choose another room.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              onClick={() => {
                setConflictOpen(false);
                navigate('/search');
              }}
              className="bg-accent hover:bg-accent-hover text-white"
            >
              Search Again
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
