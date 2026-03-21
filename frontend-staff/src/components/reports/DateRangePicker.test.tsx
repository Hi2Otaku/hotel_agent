import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DateRangePicker } from './DateRangePicker';

describe('DateRangePicker', () => {
  const mockOnChange = vi.fn();
  const defaultRange = { from: '2026-02-20', to: '2026-03-22' };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders preset buttons (7d, 30d, 90d, This Month, This Year)', () => {
    render(<DateRangePicker dateRange={defaultRange} onChange={mockOnChange} />);
    expect(screen.getByText('7d')).toBeInTheDocument();
    expect(screen.getByText('30d')).toBeInTheDocument();
    expect(screen.getByText('90d')).toBeInTheDocument();
    expect(screen.getByText('This Month')).toBeInTheDocument();
    expect(screen.getByText('This Year')).toBeInTheDocument();
  });

  it('renders Custom button for calendar popover', () => {
    render(<DateRangePicker dateRange={defaultRange} onChange={mockOnChange} />);
    expect(screen.getByText('Custom')).toBeInTheDocument();
  });

  it('calls onChange when a preset button is clicked', async () => {
    const user = userEvent.setup();
    render(<DateRangePicker dateRange={defaultRange} onChange={mockOnChange} />);

    await user.click(screen.getByText('7d'));

    expect(mockOnChange).toHaveBeenCalledTimes(1);
    const range = mockOnChange.mock.calls[0][0];
    expect(range).toHaveProperty('from');
    expect(range).toHaveProperty('to');
  });

  it('renders all five preset toggle items', () => {
    render(<DateRangePicker dateRange={defaultRange} onChange={mockOnChange} />);
    const presetLabels = ['7d', '30d', '90d', 'This Month', 'This Year'];
    for (const label of presetLabels) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });
});
