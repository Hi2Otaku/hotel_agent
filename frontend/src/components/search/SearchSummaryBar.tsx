import { Link } from 'react-router';
import { formatDateRange } from '@/lib/formatters';

interface SearchSummaryBarProps {
  checkIn: string;
  checkOut: string;
  guests: number;
  total: number;
}

export function SearchSummaryBar({
  checkIn,
  checkOut,
  guests,
  total,
}: SearchSummaryBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#E2E8F0] bg-[#F8FAFC] px-4 py-4 md:px-8">
      <p className="text-sm text-slate-700">
        {checkIn && checkOut
          ? `${formatDateRange(checkIn, checkOut)} \u00B7 `
          : ''}
        {guests} {guests === 1 ? 'guest' : 'guests'} &middot;{' '}
        {total} {total === 1 ? 'room' : 'rooms'} found
      </p>
      <Link
        to="/"
        className="text-sm font-medium text-[#0F766E] hover:underline"
      >
        Modify Search
      </Link>
    </div>
  );
}
