import { describe, it, expect, vi } from 'vitest';

// Mock Nivo bar since jsdom cannot render SVG
vi.mock('@nivo/bar', () => ({
  ResponsiveBar: vi.fn(() => null),
}));

describe('RevenueChart', () => {
  it.todo('renders without crashing when given revenue data');
  it.todo('transforms RevenueRow[] into Nivo bar data format');
  it.todo('calls onBarClick when a bar segment is clicked');
  it.todo('displays room type names in legend');
});
