import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router';
import { useQueryClient } from '@tanstack/react-query';
import { AlertTriangle } from 'lucide-react';
import { useBookingDetails } from '@/hooks/queries/useBookings';
import { StatusBadge } from '@/components/booking/StatusBadge';
import { StatusTimeline } from '@/components/booking/StatusTimeline';
import { CancelDialog } from '@/components/booking/CancelDialog';
import { ModifyDialog } from '@/components/booking/ModifyDialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import {
  formatCurrency,
  formatDateRange,
  formatDate,
  calculateNights,
} from '@/lib/formatters';

export default function BookingDetail() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: booking, isLoading } = useBookingDetails(bookingId ?? null);

  const [cancelOpen, setCancelOpen] = useState(false);
  const [modifyOpen, setModifyOpen] = useState(false);

  const canManage =
    booking?.status === 'pending' || booking?.status === 'confirmed';

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-8">
        <div className="flex items-center gap-3">
          <Skeleton className="h-9 w-48 bg-slate-200" />
          <Skeleton className="h-6 w-20 bg-slate-200" />
        </div>
        <Skeleton className="mt-6 h-12 w-full bg-slate-200" />
        <div className="mt-8 grid gap-8 lg:grid-cols-3">
          <div className="flex flex-col gap-4 lg:col-span-2">
            <Skeleton className="h-4 w-32 bg-slate-200" />
            <Skeleton className="h-4 w-48 bg-slate-200" />
            <Skeleton className="h-4 w-40 bg-slate-200" />
            <Skeleton className="h-4 w-36 bg-slate-200" />
          </div>
          <Skeleton className="h-48 w-full rounded-lg bg-slate-200" />
        </div>
        <div className="mt-6 flex gap-3">
          <Skeleton className="h-10 w-36 bg-slate-200" />
          <Skeleton className="h-10 w-36 bg-slate-200" />
        </div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <p className="text-lg text-slate-600">Booking not found.</p>
        <Link to="/my-bookings" className="mt-4 text-sm text-muted hover:underline">
          Back to My Bookings
        </Link>
      </div>
    );
  }

  const nights = calculateNights(booking.check_in, booking.check_out);
  const roomPhoto = booking.room_type_photos?.[0];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-8">
      {/* Top: confirmation + badge */}
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-4xl font-semibold">
          {booking.confirmation_number}
        </h1>
        <StatusBadge status={booking.status} />
      </div>

      {/* Status timeline */}
      <div className="mt-6">
        <StatusTimeline status={booking.status} />
      </div>

      {/* Main content: 2-col on desktop */}
      <div className="mt-8 grid gap-8 lg:grid-cols-3">
        {/* Left: details */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          {/* Guest info */}
          <div>
            <h2 className="mb-3 text-lg font-semibold">Guest Information</h2>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
              {(booking.guest_first_name || booking.guest_last_name) && (
                <>
                  <dt className="text-muted">Name</dt>
                  <dd>
                    {[booking.guest_first_name, booking.guest_last_name]
                      .filter(Boolean)
                      .join(' ')}
                  </dd>
                </>
              )}
              {booking.guest_email && (
                <>
                  <dt className="text-muted">Email</dt>
                  <dd>{booking.guest_email}</dd>
                </>
              )}
              {booking.guest_phone && (
                <>
                  <dt className="text-muted">Phone</dt>
                  <dd>{booking.guest_phone}</dd>
                </>
              )}
              {booking.special_requests && (
                <>
                  <dt className="text-muted">Special Requests</dt>
                  <dd>{booking.special_requests}</dd>
                </>
              )}
            </dl>
          </div>

          <Separator />

          {/* Stay details */}
          <div>
            <h2 className="mb-3 text-lg font-semibold">Stay Details</h2>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
              <dt className="text-muted">Dates</dt>
              <dd>{formatDateRange(booking.check_in, booking.check_out)}</dd>
              <dt className="text-muted">Nights</dt>
              <dd>{nights}</dd>
              <dt className="text-muted">Guests</dt>
              <dd>{booking.guest_count}</dd>
              {booking.room_type_name && (
                <>
                  <dt className="text-muted">Room Type</dt>
                  <dd>{booking.room_type_name}</dd>
                </>
              )}
            </dl>
          </div>

          <Separator />

          {/* Price breakdown */}
          <div>
            <h2 className="mb-3 text-lg font-semibold">Price Breakdown</h2>
            {booking.nightly_breakdown && booking.nightly_breakdown.length > 0 ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted">
                    <th className="pb-2 font-medium">Date</th>
                    <th className="pb-2 text-right font-medium">Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {booking.nightly_breakdown.map((night) => (
                    <tr key={night.date} className="border-b border-slate-100">
                      <td className="py-2">{formatDate(night.date)}</td>
                      <td className="py-2 text-right">
                        {formatCurrency(night.final_amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-sm text-muted">
                {booking.price_per_night
                  ? `${formatCurrency(booking.price_per_night)} per night`
                  : 'Price details unavailable'}
              </p>
            )}

            {booking.total_price && (
              <p className="mt-3 text-xl font-semibold text-accent">
                Total: {formatCurrency(booking.total_price)}
              </p>
            )}

            {booking.cancellation_fee && (
              <p className="mt-2 text-sm font-medium text-red-600">
                Cancellation fee: {formatCurrency(booking.cancellation_fee)}
              </p>
            )}
          </div>
        </div>

        {/* Right: room photo */}
        <div>
          {roomPhoto ? (
            <img
              src={roomPhoto}
              alt={booking.room_type_name ?? 'Room'}
              className="w-full rounded-lg object-cover"
            />
          ) : (
            <div className="flex h-48 w-full items-center justify-center rounded-lg bg-slate-100 text-sm text-slate-400">
              No photo available
            </div>
          )}
        </div>
      </div>

      {/* Cancellation policy callout */}
      {canManage && (
        <Card className="mt-8 border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-600" />
            <p className="text-sm text-amber-800">
              Free cancellation up to 24 hours before check-in. Late
              cancellations are subject to a one-night charge.
            </p>
          </div>
        </Card>
      )}

      {/* Action buttons */}
      <div className="mt-8 flex flex-wrap items-center gap-3">
        {canManage && (
          <>
            <Button
              className="min-h-[44px] bg-destructive text-white hover:bg-destructive-hover"
              onClick={() => setCancelOpen(true)}
            >
              Cancel Booking
            </Button>
            <Button
              variant="outline"
              className="min-h-[44px]"
              onClick={() => setModifyOpen(true)}
            >
              Modify Booking
            </Button>
          </>
        )}
        <Link
          to="/my-bookings"
          className="text-sm text-muted hover:underline"
        >
          Back to My Bookings
        </Link>
      </div>

      {/* Dialogs */}
      {canManage && (
        <>
          <CancelDialog
            bookingId={booking.id}
            open={cancelOpen}
            onOpenChange={setCancelOpen}
            onSuccess={() => navigate('/my-bookings')}
          />
          <ModifyDialog
            booking={booking}
            open={modifyOpen}
            onOpenChange={setModifyOpen}
            onSuccess={() =>
              queryClient.invalidateQueries({
                queryKey: ['booking', bookingId],
              })
            }
          />
        </>
      )}
    </div>
  );
}
