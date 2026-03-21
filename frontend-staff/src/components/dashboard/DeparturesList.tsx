import { Link } from 'react-router';
import { toast } from 'sonner';
import type { BookingResponse } from '@/api/types';
import { EmptyState } from '@/components/common/EmptyState';

interface DeparturesListProps {
  departures: BookingResponse[];
}

export function DeparturesList({ departures }: DeparturesListProps) {
  if (departures.length === 0) {
    return (
      <div>
        <h2 className="mb-4 text-xl font-semibold text-[#F1F5F9]">
          Today's Departures
        </h2>
        <EmptyState
          heading="No departures today"
          body="No guests checking out today."
        />
      </div>
    );
  }

  const displayed = departures.slice(0, 5);

  return (
    <div>
      <h2 className="mb-4 text-xl font-semibold text-[#F1F5F9]">
        Today's Departures
      </h2>
      <div className="overflow-hidden rounded-lg border border-[#334155]">
        {displayed.map((booking, idx) => (
          <div
            key={booking.id}
            className={`flex items-center justify-between bg-[#1E293B] px-4 py-4 transition-colors duration-150 hover:bg-[#283548] ${
              idx < displayed.length - 1 ? 'border-b border-[#334155]' : ''
            }`}
          >
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold text-[#F1F5F9]">
                {booking.guest_first_name} {booking.guest_last_name}
              </div>
              <div className="mt-1 text-xs text-[#94A3B8]">
                {booking.room_id ? `Room ${booking.room_id}` : (booking.room_type_name ?? 'Room')}{' '}
                &middot;{' '}
                <span className="font-mono">
                  {booking.confirmation_number}
                </span>
              </div>
            </div>
            <button
              onClick={() => toast('Check-out dialog coming soon')}
              className="ml-4 shrink-0 rounded-md bg-[#0F766E] px-4 py-2 text-sm text-white transition-colors hover:bg-[#0D9488]"
              style={{ minHeight: 44 }}
            >
              Check Out
            </button>
          </div>
        ))}
      </div>
      {departures.length > 5 && (
        <Link
          to="/check-in-out"
          className="mt-3 inline-block text-sm text-[#0F766E] hover:text-[#0D9488]"
        >
          View All
        </Link>
      )}
    </div>
  );
}
