import { format } from 'date-fns';
import type { BookingResponse } from '@/api/types';
import { StatusBadge } from '@/components/common/StatusBadge';

interface ReservationCardProps {
  booking: BookingResponse;
  onCheckIn?: (booking: BookingResponse) => void;
  onCheckOut?: (booking: BookingResponse) => void;
  onCancel?: (booking: BookingResponse) => void;
  onView?: (booking: BookingResponse) => void;
}

export function ReservationCard({
  booking,
  onCheckIn,
  onCheckOut,
  onCancel,
  onView,
}: ReservationCardProps) {
  const checkIn = new Date(booking.check_in);
  const checkOut = new Date(booking.check_out);
  const dateRange = `${format(checkIn, 'MMM d')} - ${format(checkOut, 'MMM d')}`;

  return (
    <div className="rounded-lg border border-[#334155] bg-[#1E293B] p-4 transition-colors duration-150 hover:bg-[#283548]">
      {/* Top row */}
      <div className="mb-3 flex items-start justify-between">
        <span className="text-sm font-semibold text-[#F1F5F9]">
          {booking.guest_first_name} {booking.guest_last_name}
        </span>
        <StatusBadge status={booking.status} />
      </div>

      {/* Middle */}
      <div className="mb-4 space-y-1">
        <div className="font-mono text-xs text-[#94A3B8]">
          {booking.confirmation_number}
        </div>
        <div className="text-sm text-[#CBD5E1]">
          {booking.room_type_name ?? 'Room'}
        </div>
        <div className="text-sm text-[#CBD5E1]">{dateRange}</div>
      </div>

      {/* Bottom: contextual action buttons */}
      <div className="flex flex-wrap gap-2">
        {booking.status === 'confirmed' && (
          <>
            <button
              onClick={() => onCheckIn?.(booking)}
              className="rounded-md bg-[#0F766E] px-4 py-2 text-sm text-white transition-colors hover:bg-[#0D9488]"
              style={{ minHeight: 44 }}
            >
              Check In
            </button>
            <button
              onClick={() => onCancel?.(booking)}
              className="rounded-md border border-[#DC2626] bg-transparent px-4 py-2 text-sm text-[#DC2626] transition-colors hover:bg-[rgba(220,38,38,0.15)]"
              style={{ minHeight: 44 }}
            >
              Cancel Booking
            </button>
          </>
        )}
        {booking.status === 'checked_in' && (
          <>
            <button
              onClick={() => onCheckOut?.(booking)}
              className="rounded-md bg-[#0F766E] px-4 py-2 text-sm text-white transition-colors hover:bg-[#0D9488]"
              style={{ minHeight: 44 }}
            >
              Check Out
            </button>
            <button
              onClick={() => onView?.(booking)}
              className="rounded-md border border-[#334155] bg-transparent px-4 py-2 text-sm text-[#CBD5E1] transition-colors hover:bg-[#283548]"
              style={{ minHeight: 44 }}
            >
              View
            </button>
          </>
        )}
        {booking.status !== 'confirmed' && booking.status !== 'checked_in' && (
          <button
            onClick={() => onView?.(booking)}
            className="rounded-md border border-[#334155] bg-transparent px-4 py-2 text-sm text-[#CBD5E1] transition-colors hover:bg-[#283548]"
            style={{ minHeight: 44 }}
          >
            View
          </button>
        )}
      </div>
    </div>
  );
}
