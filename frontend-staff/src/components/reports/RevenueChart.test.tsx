import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@nivo/bar', () => ({
  ResponsiveBar: vi.fn(() => null),
}));

import { ResponsiveBar } from '@nivo/bar';
import { RevenueChart } from './RevenueChart';

const mockResponsiveBar = vi.mocked(ResponsiveBar);

const mockData = [
  { room_type_id: 'rt-aaa11111', period: '2026-03-01', revenue: '1500.00', count: 3 },
  { room_type_id: 'rt-bbb22222', period: '2026-03-01', revenue: '2200.00', count: 5 },
  { room_type_id: 'rt-aaa11111', period: '2026-03-08', revenue: '1800.00', count: 4 },
];

describe('RevenueChart', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing when given revenue data', () => {
    render(
      <RevenueChart data={mockData} groupBy="week" onBarClick={vi.fn()} />,
    );
    expect(screen.getByRole('img')).toBeInTheDocument();
  });

  it('passes transformed data to ResponsiveBar', () => {
    render(
      <RevenueChart data={mockData} groupBy="week" onBarClick={vi.fn()} />,
    );
    expect(mockResponsiveBar).toHaveBeenCalled();
    const barProps = mockResponsiveBar.mock.calls[0][0];
    expect(barProps.data.length).toBeGreaterThan(0);
    expect(barProps.indexBy).toBe('period');
  });

  it('extracts room type keys from data', () => {
    render(
      <RevenueChart data={mockData} groupBy="week" onBarClick={vi.fn()} />,
    );
    const barProps = mockResponsiveBar.mock.calls[0][0];
    expect(barProps.keys.length).toBeGreaterThan(0);
  });

  it('has aria-label for accessibility', () => {
    render(
      <RevenueChart data={mockData} groupBy="week" onBarClick={vi.fn()} />,
    );
    expect(screen.getByLabelText('Revenue by room type bar chart')).toBeInTheDocument();
  });
});
