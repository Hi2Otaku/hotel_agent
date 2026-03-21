import { describe, it, vi } from 'vitest';

// Mock Nivo line since jsdom cannot render SVG
vi.mock('@nivo/line', () => ({
  ResponsiveLine: vi.fn(() => null),
}));

describe('BookingTrendsChart', () => {
  it.todo('renders without crashing when given trend data');
  it.todo('transforms TrendDay[] into Nivo line data format');
  it.todo('calls onPointClick when a point is clicked');
  it.todo('uses monotoneX curve interpolation');
});
