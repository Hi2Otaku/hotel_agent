import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@nivo/line', () => ({
  ResponsiveLine: vi.fn(() => null),
}));

import { ResponsiveLine } from '@nivo/line';
import { BookingTrendsChart } from './BookingTrendsChart';

const mockResponsiveLine = vi.mocked(ResponsiveLine);

const mockData = [
  { day: '2026-03-01', value: 12 },
  { day: '2026-03-02', value: 8 },
  { day: '2026-03-03', value: 15 },
];

describe('BookingTrendsChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing when given trend data', () => {
    render(
      <BookingTrendsChart data={mockData} onPointClick={vi.fn()} />,
    );
    expect(screen.getByRole('img')).toBeInTheDocument();
  });

  it('transforms TrendDay array into Nivo line data format', () => {
    render(
      <BookingTrendsChart data={mockData} onPointClick={vi.fn()} />,
    );
    expect(mockResponsiveLine).toHaveBeenCalled();
    const lineProps = mockResponsiveLine.mock.calls[0][0];
    expect(lineProps.data).toHaveLength(1);
    expect(lineProps.data[0].id).toBe('Bookings');
    expect(lineProps.data[0].data).toHaveLength(3);
    expect(lineProps.data[0].data[0]).toEqual({ x: '2026-03-01', y: 12 });
  });

  it('uses monotoneX curve interpolation', () => {
    render(
      <BookingTrendsChart data={mockData} onPointClick={vi.fn()} />,
    );
    const lineProps = mockResponsiveLine.mock.calls[0][0];
    expect(lineProps.curve).toBe('monotoneX');
  });

  it('has aria-label for accessibility', () => {
    render(
      <BookingTrendsChart data={mockData} onPointClick={vi.fn()} />,
    );
    expect(screen.getByLabelText('Booking trends line chart')).toBeInTheDocument();
  });
});
