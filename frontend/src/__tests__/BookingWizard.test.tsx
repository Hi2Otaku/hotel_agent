import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the lazy-loaded step components
vi.mock('@/components/booking/StepRoomSelection', () => ({
  default: () => <div data-testid="step-room-selection">Room Selection Step</div>,
}));
vi.mock('@/components/booking/StepGuestDetails', () => ({
  default: () => <div data-testid="step-guest-details">Guest Details Step</div>,
}));
vi.mock('@/components/booking/StepPayment', () => ({
  default: () => <div data-testid="step-payment">Payment Step</div>,
}));
vi.mock('@/components/booking/StepConfirmation', () => ({
  default: () => <div data-testid="step-confirmation">Confirmation Step</div>,
}));

// Mock the sidebar and summary panel
vi.mock('@/components/booking/WizardSidebar', () => ({
  default: ({ currentStep }: { currentStep: number }) => (
    <div data-testid="wizard-sidebar">Step {currentStep}</div>
  ),
}));
vi.mock('@/components/booking/BookingSummaryPanel', () => ({
  default: () => <div data-testid="booking-summary">Summary</div>,
}));

vi.mock('@/hooks/queries/useBookings', () => ({
  useBookingDetails: vi.fn().mockReturnValue({
    data: null,
    isLoading: false,
  }),
}));

import BookingWizard from '@/pages/BookingWizard';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import { useAuthStore } from '@/stores/authStore';

function renderWizard(initialEntries: string[] = ['/book?checkIn=2026-04-01&checkOut=2026-04-05&guests=2']) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <BookingWizard />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('BookingWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    useBookingWizardStore.getState().reset();
    useAuthStore.setState({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  });

  it('renders first step (room selection) initially', async () => {
    renderWizard();
    await waitFor(() => {
      expect(screen.getAllByText('Room Selection Step').length).toBeGreaterThan(0);
    });
  });

  it('renders wizard sidebar with current step', async () => {
    renderWizard();
    await waitFor(() => {
      const sidebars = screen.getAllByTestId('wizard-sidebar');
      expect(sidebars.length).toBeGreaterThan(0);
      expect(sidebars[0].textContent).toContain('Step 1');
    });
  });

  it('renders booking summary panel', async () => {
    renderWizard();
    await waitFor(() => {
      const summaries = screen.getAllByTestId('booking-summary');
      expect(summaries.length).toBeGreaterThan(0);
    });
  });

  it('shows step 2 when store step is 2 and user is authenticated', async () => {
    useAuthStore.setState({
      token: 'test-token',
      isAuthenticated: true,
      user: null,
    });
    useBookingWizardStore.setState({ step: 2 });

    renderWizard();
    await waitFor(() => {
      expect(screen.getAllByText('Guest Details Step').length).toBeGreaterThan(0);
    });
  });
});
