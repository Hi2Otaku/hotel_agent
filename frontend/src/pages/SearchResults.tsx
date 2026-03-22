import { useSearchParams } from 'react-router';
import { toast } from 'sonner';
import { useEffect } from 'react';
import { useSearchAvailability } from '@/hooks/queries/useSearch';
import { SearchSummaryBar } from '@/components/search/SearchSummaryBar';
import { RoomCard } from '@/components/search/RoomCard';
import { FilterDrawer, type FilterState } from '@/components/search/FilterDrawer';
import { EmptyState } from '@/components/common/EmptyState';
import { Skeleton } from '@/components/ui/skeleton';

function SearchResultsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="overflow-hidden rounded-lg bg-white shadow-sm">
          <Skeleton className="h-48 w-full bg-slate-200" />
          <div className="flex flex-col gap-3 p-4">
            <Skeleton className="h-4 w-3/4 bg-slate-200" />
            <Skeleton className="h-4 w-1/2 bg-slate-200" />
            <Skeleton className="h-4 w-2/3 bg-slate-200" />
            <Skeleton className="h-10 w-full bg-slate-200" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams();
  const checkIn = searchParams.get('checkIn') ?? '';
  const checkOut = searchParams.get('checkOut') ?? '';
  const guests = Number(searchParams.get('guests') ?? 2);
  const minPrice = searchParams.get('minPrice')
    ? Number(searchParams.get('minPrice'))
    : undefined;
  const maxPrice = searchParams.get('maxPrice')
    ? Number(searchParams.get('maxPrice'))
    : undefined;
  const amenities = searchParams.get('amenities') ?? undefined;
  const sort = searchParams.get('sort') ?? undefined;

  const { data, isLoading, isError } = useSearchAvailability({
    checkIn,
    checkOut,
    guests,
    minPrice,
    maxPrice,
    amenities,
    sort,
  });

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong. Please try again in a moment.');
    }
  }, [isError]);

  function handleFilter(filters: FilterState) {
    const params = new URLSearchParams(searchParams);
    // Update filter params
    if (filters.minPrice !== undefined) {
      params.set('minPrice', String(filters.minPrice));
    } else {
      params.delete('minPrice');
    }
    if (filters.maxPrice !== undefined) {
      params.set('maxPrice', String(filters.maxPrice));
    } else {
      params.delete('maxPrice');
    }
    if (filters.amenities.length > 0) {
      params.set('amenities', filters.amenities.join(','));
    } else {
      params.delete('amenities');
    }
    if (filters.sort && filters.sort !== 'recommended') {
      params.set('sort', filters.sort);
    } else {
      params.delete('sort');
    }
    setSearchParams(params);
  }

  return (
    <div>
      {/* Summary bar */}
      <SearchSummaryBar
        checkIn={checkIn}
        checkOut={checkOut}
        guests={guests}
        total={data?.total ?? 0}
      />

      {/* Main content */}
      <div className="flex gap-8 px-4 py-6 md:px-8">
        {/* Filter sidebar / mobile button */}
        <FilterDrawer onFilter={handleFilter} />

        {/* Results area */}
        <div className="flex-1">
          {/* Mobile filter button row */}
          <div className="mb-4 flex items-center justify-between lg:hidden">
            <p className="text-sm text-muted">
              {data?.total ?? 0} results
            </p>
          </div>

          {isLoading && <SearchResultsSkeleton />}

          {!isLoading && data && data.results.length === 0 && (
            <EmptyState
              heading="No rooms available"
              body="Try adjusting your dates or guest count to find available rooms."
              actionLabel="Search Rooms"
              actionHref="/"
            />
          )}

          {!isLoading && data && data.results.length > 0 && (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {data.results.map((room) => (
                <RoomCard
                  key={room.room_type_id}
                  room={room}
                  checkIn={checkIn}
                  checkOut={checkOut}
                  guests={guests}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
