import { useState } from 'react';
import { Link } from 'react-router';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';
import { useBookingList } from '@/hooks/queries/useBookings';
import { StatusBadge } from '@/components/booking/StatusBadge';
import { CancelDialog } from '@/components/booking/CancelDialog';
import { ModifyDialog } from '@/components/booking/ModifyDialog';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDateRange, formatCurrency } from '@/lib/formatters';
import type { BookingResponse } from '@/api/types';

export default function MyBookings() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useBookingList();

  const [cancelBookingId, setCancelBookingId] = useState<string | null>(null);
  const [modifyBooking, setModifyBooking] = useState<BookingResponse | null>(null);

  if (isError) {
    toast.error('Something went wrong. Please try again in a moment.');
  }

  const canManage = (status: string) =>
    status === 'pending' || status === 'confirmed';

  const handleSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['bookings'] });
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-8">
      <h1 className="mb-6 text-2xl font-semibold">My Bookings</h1>

      {isLoading && (
        <div className="flex flex-col gap-4">
          {[1, 2].map((i) => (
            <Card key={i} className="p-4">
              <div className="flex gap-4">
                <Skeleton className="h-20 w-20 rounded-lg bg-slate-200" />
                <div className="flex flex-1 flex-col gap-2">
                  <Skeleton className="h-4 w-40 bg-slate-200" />
                  <Skeleton className="h-4 w-28 bg-slate-200" />
                  <Skeleton className="h-4 w-20 bg-slate-200" />
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <Skeleton className="h-10 w-28 bg-slate-200" />
                <Skeleton className="h-10 w-20 bg-slate-200" />
              </div>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && data && data.items.length === 0 && (
        <EmptyState
          heading="No bookings yet"
          body="Ready to plan your stay? Find the perfect room."
          actionLabel="Search Rooms"
          actionHref="/"
        />
      )}

      {!isLoading && data && data.items.length > 0 && (
        <div className="flex flex-col gap-4">
          {data.items.map((booking) => (
            <Card key={booking.id} className="p-4">
              <div className="flex gap-4">
                {/* Room photo thumbnail */}
                <div className="h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-slate-100">
                  {booking.room_type_photos?.[0] ? (
                    <img
                      src={booking.room_type_photos[0]}
                      alt={booking.room_type_name ?? 'Room'}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
                      No photo
                    </div>
                  )}
                </div>

                {/* Booking info */}
                <div className="flex flex-1 flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    {booking.room_type_name && (
                      <p className="text-base font-medium text-slate-900">
                        {booking.room_type_name}
                      </p>
                    )}
                    <p className="text-sm text-slate-600">
                      {formatDateRange(booking.check_in, booking.check_out)}
                    </p>
                  </div>
                  <div className="flex flex-col items-start gap-1 sm:items-end">
                    <StatusBadge status={booking.status} />
                    <p className="text-xs text-muted">
                      {booking.confirmation_number}
                    </p>
                    {booking.total_price && (
                      <p className="text-sm font-semibold text-slate-900">
                        {formatCurrency(booking.total_price)}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Action buttons */}
              <div className="mt-4 flex flex-wrap gap-2">
                <Link to={`/my-bookings/${booking.id}`}>
                  <Button variant="outline" className="min-h-[44px]">
                    View Details
                  </Button>
                </Link>
                {canManage(booking.status) && (
                  <>
                    <Button
                      variant="outline"
                      className="min-h-[44px]"
                      onClick={() => setModifyBooking(booking)}
                    >
                      Modify
                    </Button>
                    <Button
                      variant="outline"
                      className="min-h-[44px] border-destructive/30 text-destructive hover:bg-red-50"
                      onClick={() => setCancelBookingId(booking.id)}
                    >
                      Cancel
                    </Button>
                  </>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Cancel dialog */}
      {cancelBookingId && (
        <CancelDialog
          bookingId={cancelBookingId}
          open={!!cancelBookingId}
          onOpenChange={(open) => {
            if (!open) setCancelBookingId(null);
          }}
          onSuccess={handleSuccess}
        />
      )}

      {/* Modify dialog */}
      {modifyBooking && (
        <ModifyDialog
          booking={modifyBooking}
          open={!!modifyBooking}
          onOpenChange={(open) => {
            if (!open) setModifyBooking(null);
          }}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  );
}
