import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { useStaffBookings } from '@/hooks/queries/useStaffBookings';
import { SearchFilters } from '@/components/reservations/SearchFilters';
import { ReservationCard } from '@/components/reservations/ReservationCard';
import { EmptyState } from '@/components/common/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from '@/components/ui/pagination';

const PAGE_SIZE = 12;

export default function ReservationsPage() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useStaffBookings({
    search: search || undefined,
    status: status || undefined,
    check_in_from: dateFrom || undefined,
    check_in_to: dateTo || undefined,
    skip: (page - 1) * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const handleSearch = useCallback(
    (params: { search: string; status: string; dateFrom: string; dateTo: string }) => {
      setSearch(params.search);
      setStatus(params.status);
      setDateFrom(params.dateFrom);
      setDateTo(params.dateTo);
      setPage(1);
    },
    [],
  );

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  const handlePlaceholderAction = (action: string) => {
    toast(`${action} - Feature coming soon.`);
  };

  // Build page numbers to display
  const getPageNumbers = () => {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    const end = Math.min(totalPages, start + maxVisible - 1);
    start = Math.max(1, end - maxVisible + 1);
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  return (
    <div className="space-y-6">
      <SearchFilters onSearch={handleSearch} />

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg bg-[#1E293B]" />
          ))}
        </div>
      )}

      {!isLoading && data && data.items.length === 0 && (
        <EmptyState
          heading="No reservations found"
          body="Try adjusting your search or filters."
        />
      )}

      {!isLoading && data && data.items.length > 0 && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.items.map((booking) => (
              <ReservationCard
                key={booking.id}
                booking={booking}
                onCheckIn={() => handlePlaceholderAction('Check In')}
                onCheckOut={() => handlePlaceholderAction('Check Out')}
                onCancel={() => handlePlaceholderAction('Cancel Booking')}
                onView={() => handlePlaceholderAction('View Booking')}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <Pagination className="mt-6">
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className={
                      page === 1
                        ? 'pointer-events-none opacity-50'
                        : 'cursor-pointer text-[#CBD5E1] hover:bg-[#283548]'
                    }
                  />
                </PaginationItem>

                {getPageNumbers().map((p) => (
                  <PaginationItem key={p}>
                    <PaginationLink
                      onClick={() => setPage(p)}
                      isActive={p === page}
                      className={
                        p === page
                          ? 'cursor-pointer border-[#0F766E] bg-[#0F766E] text-white hover:bg-[#0D9488]'
                          : 'cursor-pointer bg-[#1E293B] text-[#CBD5E1] hover:bg-[#283548]'
                      }
                    >
                      {p}
                    </PaginationLink>
                  </PaginationItem>
                ))}

                <PaginationItem>
                  <PaginationNext
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className={
                      page === totalPages
                        ? 'pointer-events-none opacity-50'
                        : 'cursor-pointer text-[#CBD5E1] hover:bg-[#283548]'
                    }
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          )}
        </>
      )}
    </div>
  );
}
