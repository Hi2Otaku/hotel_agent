import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('@/hooks/queries/useSearch', () => ({
  useSearchAvailability: vi.fn(),
}));

import SearchResults from '@/pages/SearchResults';
import { useSearchAvailability } from '@/hooks/queries/useSearch';

const mockedUseSearch = vi.mocked(useSearchAvailability);

function renderWithProviders(initialEntries: string[] = ['/search?checkIn=2026-04-01&checkOut=2026-04-05&guests=2']) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <SearchResults />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('SearchResults', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading skeleton when data is loading', () => {
    mockedUseSearch.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as any);

    renderWithProviders();
    // Skeleton uses rounded-lg bg-white shadow-sm class pattern
    const skeletons = document.querySelectorAll('.rounded-lg');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders room cards when data is available', () => {
    mockedUseSearch.mockReturnValue({
      data: {
        results: [
          {
            room_type_id: 'rt-1',
            name: 'Standard Room',
            slug: 'standard-room',
            description: 'A standard room',
            photo_url: null,
            price_per_night: '100.00',
            total_price: '400.00',
            currency: 'USD',
            max_adults: 2,
            max_children: 1,
            bed_config: [{ type: 'queen', count: 1 }],
            amenity_highlights: ['WiFi'],
            available_count: 5,
            total_rooms: 10,
          },
          {
            room_type_id: 'rt-2',
            name: 'Deluxe Suite',
            slug: 'deluxe-suite',
            description: 'A deluxe suite',
            photo_url: null,
            price_per_night: '250.00',
            total_price: '1000.00',
            currency: 'USD',
            max_adults: 3,
            max_children: 2,
            bed_config: [{ type: 'king', count: 1 }],
            amenity_highlights: ['WiFi', 'Pool'],
            available_count: 2,
            total_rooms: 4,
          },
        ],
        total: 2,
        check_in: '2026-04-01',
        check_out: '2026-04-05',
        guests: 2,
      },
      isLoading: false,
      isError: false,
    } as any);

    renderWithProviders();
    expect(screen.getByText('Standard Room')).toBeInTheDocument();
    expect(screen.getByText('Deluxe Suite')).toBeInTheDocument();
  });

  it('renders empty state when no rooms are available', () => {
    mockedUseSearch.mockReturnValue({
      data: {
        results: [],
        total: 0,
        check_in: '2026-04-01',
        check_out: '2026-04-05',
        guests: 2,
      },
      isLoading: false,
      isError: false,
    } as any);

    renderWithProviders();
    expect(screen.getByText('No rooms available')).toBeInTheDocument();
  });

  it('displays total result count', () => {
    mockedUseSearch.mockReturnValue({
      data: {
        results: [
          {
            room_type_id: 'rt-1',
            name: 'Standard Room',
            slug: 'standard-room',
            description: 'A standard room',
            photo_url: null,
            price_per_night: '100.00',
            total_price: '400.00',
            currency: 'USD',
            max_adults: 2,
            max_children: 1,
            bed_config: [],
            amenity_highlights: [],
            available_count: 5,
            total_rooms: 10,
          },
        ],
        total: 1,
        check_in: '2026-04-01',
        check_out: '2026-04-05',
        guests: 2,
      },
      isLoading: false,
      isError: false,
    } as any);

    renderWithProviders();
    // The mobile result count text shows "1 results"
    expect(screen.getByText('1 results')).toBeInTheDocument();
  });
});
