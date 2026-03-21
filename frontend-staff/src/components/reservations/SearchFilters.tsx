import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router';
import { Search } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface SearchFiltersProps {
  onSearch: (params: {
    search: string;
    status: string;
    dateFrom: string;
    dateTo: string;
  }) => void;
}

const STATUS_OPTIONS = [
  { value: 'all', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'checked_in', label: 'Checked In' },
  { value: 'checked_out', label: 'Checked Out' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'no_show', label: 'No Show' },
];

export function SearchFilters({ onSearch }: SearchFiltersProps) {
  const [searchParams, setSearchParams] = useSearchParams();

  const [search, setSearch] = useState(searchParams.get('search') ?? '');
  const [status, setStatus] = useState(searchParams.get('status') ?? 'all');
  const [dateFrom, setDateFrom] = useState(searchParams.get('dateFrom') ?? '');
  const [dateTo, setDateTo] = useState(searchParams.get('dateTo') ?? '');

  const emitSearch = useCallback(
    (s: string, st: string, df: string, dt: string) => {
      onSearch({ search: s, status: st === 'all' ? '' : st, dateFrom: df, dateTo: dt });
      const params = new URLSearchParams();
      if (s) params.set('search', s);
      if (st && st !== 'all') params.set('status', st);
      if (df) params.set('dateFrom', df);
      if (dt) params.set('dateTo', dt);
      setSearchParams(params, { replace: true });
    },
    [onSearch, setSearchParams],
  );

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      emitSearch(search, status, dateFrom, dateTo);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]); // eslint-disable-line react-hooks/exhaustive-deps

  // Immediate emit for non-search changes
  const handleStatusChange = (val: string) => {
    setStatus(val);
    emitSearch(search, val, dateFrom, dateTo);
  };

  const handleDateFromChange = (val: string) => {
    setDateFrom(val);
    emitSearch(search, status, val, dateTo);
  };

  const handleDateToChange = (val: string) => {
    setDateTo(val);
    emitSearch(search, status, dateFrom, val);
  };

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by guest name or confirmation number..."
          className="w-full rounded-md border border-[#334155] bg-[#1E293B] py-2.5 pl-10 pr-4 text-sm text-[#F1F5F9] placeholder-[#64748B] outline-none transition-shadow focus:border-[#0F766E] focus:ring-2 focus:ring-[rgba(15,118,110,0.3)]"
        />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Select value={status} onValueChange={handleStatusChange}>
          <SelectTrigger className="w-[180px] border-[#334155] bg-[#1E293B] text-[#F1F5F9]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent className="border-[#334155] bg-[#1E293B]">
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem
                key={opt.value}
                value={opt.value}
                className="text-[#F1F5F9] focus:bg-[#283548] focus:text-[#F1F5F9]"
              >
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[#94A3B8]">From</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => handleDateFromChange(e.target.value)}
            className="rounded-md border border-[#334155] bg-[#1E293B] px-3 py-2 text-sm text-[#F1F5F9] outline-none focus:border-[#0F766E] focus:ring-2 focus:ring-[rgba(15,118,110,0.3)]"
          />
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[#94A3B8]">To</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => handleDateToChange(e.target.value)}
            className="rounded-md border border-[#334155] bg-[#1E293B] px-3 py-2 text-sm text-[#F1F5F9] outline-none focus:border-[#0F766E] focus:ring-2 focus:ring-[rgba(15,118,110,0.3)]"
          />
        </div>
      </div>
    </div>
  );
}
