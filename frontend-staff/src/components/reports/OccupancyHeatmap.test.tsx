import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@nivo/calendar', () => ({
  ResponsiveCalendar: vi.fn(() => null),
}));

import { ResponsiveCalendar } from '@nivo/calendar';
import { OccupancyHeatmap } from './OccupancyHeatmap';

const mockResponsiveCalendar = vi.mocked(ResponsiveCalendar);

const mockData = [
  { day: '2026-03-01', value: 85 },
  { day: '2026-03-02', value: 92 },
  { day: '2026-03-03', value: 70 },
];

describe('OccupancyHeatmap', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing when given valid occupancy data', () => {
    render(
      <OccupancyHeatmap
        data={mockData}
        from="2026-03-01"
        to="2026-03-31"
        onDayClick={vi.fn()}
      />,
    );
    expect(screen.getByRole('img')).toBeInTheDocument();
  });

  it('passes correct from and to props to ResponsiveCalendar', () => {
    render(
      <OccupancyHeatmap
        data={mockData}
        from="2026-03-01"
        to="2026-03-31"
        onDayClick={vi.fn()}
      />,
    );
    expect(mockResponsiveCalendar).toHaveBeenCalled();
    const calendarProps = mockResponsiveCalendar.mock.calls[0][0];
    expect(calendarProps.from).toBe('2026-03-01');
    expect(calendarProps.to).toBe('2026-03-31');
  });

  it('passes data to ResponsiveCalendar', () => {
    render(
      <OccupancyHeatmap
        data={mockData}
        from="2026-03-01"
        to="2026-03-31"
        onDayClick={vi.fn()}
      />,
    );
    const calendarProps = mockResponsiveCalendar.mock.calls[0][0];
    expect(calendarProps.data).toEqual(mockData);
  });

  it('has aria-label for accessibility', () => {
    render(
      <OccupancyHeatmap
        data={mockData}
        from="2026-03-01"
        to="2026-03-31"
        onDayClick={vi.fn()}
      />,
    );
    expect(screen.getByLabelText('Occupancy rate calendar heatmap')).toBeInTheDocument();
  });
});
