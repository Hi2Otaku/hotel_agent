import { Link } from 'react-router';
import { CheckCircle2, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import { useBookingDetails } from '@/hooks/queries/useBookings';
import { formatCurrency, formatDateRange } from '@/lib/formatters';

export default function StepConfirmation() {
  const bookingId = useBookingWizardStore((s) => s.bookingId);
  const reset = useBookingWizardStore((s) => s.reset);

  const { data: booking, isLoading } = useBookingDetails(bookingId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="size-6 animate-spin text-accent" />
        <span className="ml-2 text-slate-500">Loading...</span>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-600">Booking not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-center">
      <CheckCircle2 className="mx-auto text-success" style={{ width: 64, height: 64 }} />

      <h2 className="text-2xl font-semibold text-slate-900">
        Your booking is confirmed!
      </h2>

      <p className="text-4xl font-semibold text-accent">
        {booking.confirmation_number}
      </p>

      <Card className="text-left">
        <CardContent className="pt-4 space-y-2">
          {booking.room_type_name && (
            <p className="text-lg font-semibold text-slate-900">
              {booking.room_type_name}
            </p>
          )}
          <p className="text-sm text-slate-600">
            {formatDateRange(booking.check_in, booking.check_out)}
          </p>
          <p className="text-sm text-slate-600">
            {booking.guest_count} guest{booking.guest_count !== 1 ? 's' : ''}
          </p>
          {booking.total_price && (
            <p className="text-lg font-semibold text-accent">
              Total: {formatCurrency(booking.total_price)}
            </p>
          )}
        </CardContent>
      </Card>

      <Button
        asChild
        className="w-full min-h-[44px] bg-accent hover:bg-accent-hover text-white"
      >
        <Link to="/my-bookings">View My Bookings</Link>
      </Button>

      <Link
        to="/"
        onClick={reset}
        className="block text-sm text-muted hover:text-accent hover:underline"
      >
        Book Another Room
      </Link>
    </div>
  );
}
