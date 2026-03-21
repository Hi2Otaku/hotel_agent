import { describe, it, vi } from 'vitest';

// Mock Nivo calendar since jsdom cannot render SVG
vi.mock('@nivo/calendar', () => ({
  ResponsiveCalendar: vi.fn(() => null),
}));

describe('OccupancyHeatmap', () => {
  it.todo('renders without crashing when given valid occupancy data');
  it.todo('passes correct from/to props to ResponsiveCalendar');
  it.todo('calls onDayClick when a day is clicked');
  it.todo('adapts display mode based on date range length (<=14d, 15-90d, 91+d)');
});
