import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { useTodayOverview } from '@/hooks/queries/useStaffBookings';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { CheckInDialog } from '@/components/checkin/CheckInDialog';
import { CheckOutDialog } from '@/components/checkin/CheckOutDialog';
import type { BookingResponse } from '@/api/types';

type DialogType = 'check-in' | 'check-out' | null;

export default function CheckInOutPage() {
  const { data, isLoading, isError } = useTodayOverview();
  const [selectedBooking, setSelectedBooking] =
    useState<BookingResponse | null>(null);
  const [dialogType, setDialogType] = useState<DialogType>(null);

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong. Please try again.');
    }
  }, [isError]);

  const openCheckIn = (booking: BookingResponse) => {
    setSelectedBooking(booking);
    setDialogType('check-in');
  };

  const openCheckOut = (booking: BookingResponse) => {
    setSelectedBooking(booking);
    setDialogType('check-out');
  };

  const closeDialog = () => {
    setDialogType(null);
    setSelectedBooking(null);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64 bg-[#1E293B]" />
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full bg-[#1E293B]" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div>
      <Tabs defaultValue="arrivals" className="w-full">
        <TabsList className="mb-6 bg-[#1E293B]">
          <TabsTrigger
            value="arrivals"
            className="text-[#94A3B8] data-[state=active]:bg-[#0F172A] data-[state=active]:text-[#F1F5F9]"
          >
            Arrivals
          </TabsTrigger>
          <TabsTrigger
            value="departures"
            className="text-[#94A3B8] data-[state=active]:bg-[#0F172A] data-[state=active]:text-[#F1F5F9]"
          >
            Departures
          </TabsTrigger>
        </TabsList>

        <TabsContent value="arrivals">
          {data.arrivals.length === 0 ? (
            <EmptyState
              heading="No arrivals today"
              body="All quiet on the front desk. No guests expected today."
            />
          ) : (
            <div className="overflow-hidden rounded-lg border border-[#334155]">
              {data.arrivals.map((booking, idx) => (
                <div
                  key={booking.id}
                  className={`flex items-center justify-between bg-[#1E293B] px-4 py-4 transition-colors duration-150 hover:bg-[#283548] ${
                    idx < data.arrivals.length - 1
                      ? 'border-b border-[#334155]'
                      : ''
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold text-[#F1F5F9]">
                      {booking.guest_first_name} {booking.guest_last_name}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[#94A3B8]">
                      <span>{booking.room_type_name ?? 'Room'}</span>
                      <span>&middot;</span>
                      <span className="font-mono text-[#94A3B8]">
                        {booking.confirmation_number}
                      </span>
                      {booking.special_requests && (
                        <>
                          <span>&middot;</span>
                          <span className="max-w-[200px] truncate">
                            {booking.special_requests}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => openCheckIn(booking)}
                    className="ml-4 shrink-0 rounded-md bg-[#0F766E] px-4 py-2 text-sm text-white transition-colors hover:bg-[#0D9488]"
                    style={{ minHeight: 44 }}
                  >
                    Check In
                  </button>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="departures">
          {data.departures.length === 0 ? (
            <EmptyState
              heading="No departures today"
              body="No guests checking out today."
            />
          ) : (
            <div className="overflow-hidden rounded-lg border border-[#334155]">
              {data.departures.map((booking, idx) => (
                <div
                  key={booking.id}
                  className={`flex items-center justify-between bg-[#1E293B] px-4 py-4 transition-colors duration-150 hover:bg-[#283548] ${
                    idx < data.departures.length - 1
                      ? 'border-b border-[#334155]'
                      : ''
                  }`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold text-[#F1F5F9]">
                      {booking.guest_first_name} {booking.guest_last_name}
                    </div>
                    <div className="mt-1 text-xs text-[#94A3B8]">
                      {booking.room_number
                        ? `Room ${booking.room_number}`
                        : booking.room_id
                          ? `Room ${booking.room_id}`
                          : (booking.room_type_name ?? 'Room')}{' '}
                      &middot;{' '}
                      <span className="font-mono">
                        {booking.confirmation_number}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => openCheckOut(booking)}
                    className="ml-4 shrink-0 rounded-md bg-[#0F766E] px-4 py-2 text-sm text-white transition-colors hover:bg-[#0D9488]"
                    style={{ minHeight: 44 }}
                  >
                    Check Out
                  </button>
                </div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {selectedBooking && dialogType === 'check-in' && (
        <CheckInDialog
          booking={selectedBooking}
          open
          onOpenChange={(open) => {
            if (!open) closeDialog();
          }}
        />
      )}

      {selectedBooking && dialogType === 'check-out' && (
        <CheckOutDialog
          booking={selectedBooking}
          open
          onOpenChange={(open) => {
            if (!open) closeDialog();
          }}
        />
      )}
    </div>
  );
}
