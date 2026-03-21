import { StatusBadge } from '@/components/common/StatusBadge';
import type { BookingResponse } from '@/api/types';

interface DrillDownBookingRowProps {
  booking: BookingResponse;
}

function formatPrice(value: string | null): string {
  if (!value) return '-';
  const num = parseFloat(value);
  if (isNaN(num)) return '-';
  return `$${num.toFixed(2)}`;
}

function guestName(booking: BookingResponse): string {
  if (booking.guest_first_name || booking.guest_last_name) {
    return [booking.guest_first_name, booking.guest_last_name].filter(Boolean).join(' ');
  }
  return 'Guest';
}

export function DrillDownBookingRow({ booking }: DrillDownBookingRowProps) {
  return (
    <div className="flex items-start justify-between border-b border-[#334155] py-3">
      <div className="min-w-0 flex-1">
        <p className="font-mono text-sm text-[#F1F5F9]">
          {booking.confirmation_number}
        </p>
        <p className="text-xs text-[#94A3B8]">{guestName(booking)}</p>
        <p className="mt-0.5 text-xs text-[#94A3B8]">
          {booking.check_in} &mdash; {booking.check_out}
        </p>
      </div>
      <div className="flex flex-col items-end gap-1">
        <StatusBadge status={booking.status} />
        <span className="text-xs text-[#94A3B8]">{formatPrice(booking.total_price)}</span>
      </div>
    </div>
  );
}
