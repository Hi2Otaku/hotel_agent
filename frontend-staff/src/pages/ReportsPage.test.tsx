import { describe, it, expect, vi } from 'vitest';

// Mock all Nivo chart packages since jsdom cannot render SVG
vi.mock('@nivo/calendar', () => ({ ResponsiveCalendar: vi.fn(() => null) }));
vi.mock('@nivo/bar', () => ({ ResponsiveBar: vi.fn(() => null) }));
vi.mock('@nivo/line', () => ({ ResponsiveLine: vi.fn(() => null) }));

describe('ReportsPage', () => {
  it.todo('renders KPI cards section');
  it.todo('renders all three chart sections');
  it.todo('renders date range picker with default 30d selection');
  it.todo('updates all charts when date range changes');
  it.todo('shows loading skeletons while data is fetching');
  it.todo('shows empty states when no data returned');
});
