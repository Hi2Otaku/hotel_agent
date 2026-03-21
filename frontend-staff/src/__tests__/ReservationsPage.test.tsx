import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the staff bookings hook
vi.mock('@/hooks/queries/useStaffBookings', () => ({
  useStaffBookings: vi.fn(),
}));

// Mock CheckInDialog/CheckOutDialog (they use complex portal/dialog components)
vi.mock('@/components/checkin/CheckInDialog', () => ({
  CheckInDialog: () => null,
}));
vi.mock('@/components/checkin/CheckOutDialog', () => ({
  CheckOutDialog: () => null,
}));

import ReservationsPage from '@/pages/ReservationsPage';
import { useStaffBookings } from '@/hooks/queries/useStaffBookings';

const mockedUseStaffBookings = vi.mocked(useStaffBookings);

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ReservationsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ReservationsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders search and filter controls', () => {
    mockedUseStaffBookings.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
    } as any);

    renderPage();
    // SearchFilters component should render search input
    const searchInputs = document.querySelectorAll('input');
    expect(searchInputs.length).toBeGreaterThan(0);
  });

  it('shows empty state when no bookings exist', () => {
    mockedUseStaffBookings.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
    } as any);

    renderPage();
    // EmptyState should render
    expect(screen.getByText(/no.*reservation/i)).toBeInTheDocument();
  });

  it('renders reservation cards when bookings exist', () => {
    mockedUseStaffBookings.mockReturnValue({
      data: {
        items: [
          {
            id: 'b-001',
            confirmation_number: 'HB-ABC123',
            guest_first_name: 'John',
            guest_last_name: 'Doe',
            guest_email: 'john@example.com',
            check_in: '2026-04-01',
            check_out: '2026-04-05',
            status: 'confirmed',
            total_price: '600.00',
            room_type_id: 'rt-1',
            room_number: null,
          },
        ],
        total: 1,
      },
      isLoading: false,
    } as any);

    renderPage();
    expect(screen.getByText('HB-ABC123')).toBeInTheDocument();
  });

  it('renders loading skeletons while fetching', () => {
    mockedUseStaffBookings.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    renderPage();
    const skeletons = document.querySelectorAll('[class*="animate-pulse"], [class*="skeleton"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
