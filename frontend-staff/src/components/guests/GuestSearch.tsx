import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { useGuestSearch } from '@/hooks/queries/useGuests';
import { EmptyState } from '@/components/common/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import type { UserResponse } from '@/api/types';

interface GuestSearchProps {
  onSelect: (userId: string) => void;
}

export function GuestSearch({ onSelect }: GuestSearchProps) {
  const [inputValue, setInputValue] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(inputValue);
    }, 300);
    return () => clearTimeout(timer);
  }, [inputValue]);

  const { data: results, isLoading } = useGuestSearch(debouncedQuery);

  const hasSearched = debouncedQuery.length >= 2;

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#64748B]" />
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Search by guest name or email..."
          className="w-full rounded-md border border-[#334155] bg-[#1E293B] py-2.5 pl-10 pr-4 text-sm text-[#F1F5F9] placeholder-[#64748B] outline-none transition-shadow focus:border-[#0F766E] focus:ring-2 focus:ring-[rgba(15,118,110,0.3)]"
        />
      </div>

      {isLoading && hasSearched && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full rounded-md bg-[#1E293B]" />
          ))}
        </div>
      )}

      {!hasSearched && (
        <EmptyState
          heading="Search for a guest"
          body="Enter a guest name or email to view their profile and booking history."
        />
      )}

      {hasSearched && !isLoading && results && results.length === 0 && (
        <EmptyState
          heading="No guests found"
          body="No guests match your search. Try a different name or email."
        />
      )}

      {hasSearched && !isLoading && results && results.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-[#334155]">
          {results.map((guest: UserResponse, idx: number) => (
            <button
              key={guest.id}
              type="button"
              onClick={() => onSelect(guest.id)}
              className={`flex w-full items-center justify-between bg-[#1E293B] px-4 py-3 text-left transition-colors duration-150 hover:bg-[#283548] ${
                idx < results.length - 1 ? 'border-b border-[#334155]' : ''
              }`}
            >
              <div>
                <div className="text-sm font-semibold text-[#F1F5F9]">
                  {guest.first_name} {guest.last_name}
                </div>
                <div className="text-xs text-[#94A3B8]">{guest.email}</div>
              </div>
              <span className="rounded-md bg-[rgba(15,118,110,0.15)] px-2 py-0.5 text-xs text-[#0F766E]">
                {guest.role}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
