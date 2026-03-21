import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock Nivo chart packages
vi.mock('@nivo/calendar', () => ({ ResponsiveCalendar: vi.fn(() => null) }));
vi.mock('@nivo/bar', () => ({ ResponsiveBar: vi.fn(() => null) }));
vi.mock('@nivo/line', () => ({ ResponsiveLine: vi.fn(() => null) }));

// Mock the useReportData hook
vi.mock('@/hooks/queries/useReports', () => ({
  useReportData: vi.fn(),
}));

// Mock the export functions
vi.mock('@/lib/export', () => ({
  downloadCSV: vi.fn(),
  exportDashboardPDF: vi.fn(),
}));

// Mock DrillDownPanel (uses portal)
vi.mock('@/components/reports/DrillDownPanel', () => ({
  DrillDownPanel: () => null,
}));

import ReportsPage from './ReportsPage';
import { useReportData } from '@/hooks/queries/useReports';

const mockedUseReportData = vi.mocked(useReportData);

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ReportsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ReportsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders KPI cards when data is available', () => {
    mockedUseReportData.mockReturnValue({
      data: {
        kpis: {
          total_revenue: '45000',
          total_bookings: 120,
          avg_daily_rate: '185',
        },
        occupancy: {
          daily: [{ day: '2026-03-01', value: 85 }],
          total_rooms: 50,
          avg_occupancy: 78.5,
        },
        revenue: {
          data: [{ room_type_id: 'rt-1', period: '2026-03-01', revenue: '1500', count: 3 }],
          group_by: 'day' as const,
        },
        trends: {
          data: [{ day: '2026-03-01', value: 12 }],
        },
      },
      isLoading: false,
    } as any);

    renderPage();
    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('Avg Occupancy')).toBeInTheDocument();
    expect(screen.getByText('Total Bookings')).toBeInTheDocument();
    expect(screen.getByText('Avg Daily Rate')).toBeInTheDocument();
  });

  it('renders all three chart section titles', () => {
    mockedUseReportData.mockReturnValue({
      data: {
        kpis: { total_revenue: '0', total_bookings: 0, avg_daily_rate: '0' },
        occupancy: { daily: [{ day: '2026-03-01', value: 0 }], total_rooms: 50, avg_occupancy: 0 },
        revenue: { data: [{ room_type_id: 'rt-1', period: '2026-03-01', revenue: '0', count: 0 }], group_by: 'day' as const },
        trends: { data: [{ day: '2026-03-01', value: 0 }] },
      },
      isLoading: false,
    } as any);

    renderPage();
    expect(screen.getByText('Occupancy Rate')).toBeInTheDocument();
    expect(screen.getByText('Revenue by Room Type')).toBeInTheDocument();
    expect(screen.getByText('Booking Trends')).toBeInTheDocument();
  });

  it('renders Export PDF button', () => {
    mockedUseReportData.mockReturnValue({
      data: null,
      isLoading: false,
    } as any);

    renderPage();
    expect(screen.getByText('Export PDF')).toBeInTheDocument();
  });

  it('renders date range picker with preset buttons', () => {
    mockedUseReportData.mockReturnValue({
      data: null,
      isLoading: false,
    } as any);

    renderPage();
    expect(screen.getByText('7d')).toBeInTheDocument();
    expect(screen.getByText('30d')).toBeInTheDocument();
  });
});
