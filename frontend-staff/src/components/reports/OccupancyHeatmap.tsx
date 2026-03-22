import { useMemo } from 'react';
import { ResponsiveCalendar } from '@nivo/calendar';
import { differenceInDays } from 'date-fns';
import { nivoTheme, HEATMAP_EMPTY, HEATMAP_COLORS } from '@/lib/chartTheme';
import type { OccupancyDay } from '@/api/types';

interface OccupancyHeatmapProps {
  data: OccupancyDay[];
  from: string;
  to: string;
  onDayClick: (day: string) => void;
}

export function OccupancyHeatmap({ data, from, to, onDayClick }: OccupancyHeatmapProps) {
  const dayCount = useMemo(() => {
    try {
      return differenceInDays(new Date(to), new Date(from));
    } catch {
      return 30;
    }
  }, [from, to]);

  const calendarConfig = useMemo(() => {
    if (dayCount <= 14) {
      // Daily grid: horizontal layout, default cell size
      return { direction: 'horizontal' as const, cellSize: undefined };
    }
    if (dayCount > 90) {
      // Compact mode: horizontal layout, reduced cell size
      return { direction: 'horizontal' as const, cellSize: 11 };
    }
    // Monthly calendar (15-90 days): vertical Nivo default layout
    return { direction: 'vertical' as const, cellSize: undefined };
  }, [dayCount]);

  return (
    <div role="img" aria-label="Occupancy rate calendar heatmap" className="h-full">
      <ResponsiveCalendar
        data={data}
        from={from}
        to={to}
        emptyColor={HEATMAP_EMPTY}
        colors={HEATMAP_COLORS}
        margin={{ top: 20, right: 32, bottom: 40, left: 48 }}
        yearSpacing={40}
        monthBorderColor="#334155"
        dayBorderWidth={2}
        dayBorderColor="#0F172A"
        direction={calendarConfig.direction}
        {...(calendarConfig.cellSize ? { daySpacing: 1, monthSpacing: 12 } : {})}
        theme={nivoTheme}
        onClick={(datum) => onDayClick(datum.day)}
        tooltip={({ day, value }) => (
          <div
            style={{
              background: '#1E293B',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '8px 12px',
              color: '#F1F5F9',
              fontSize: '12px',
            }}
          >
            <strong>{day}</strong>
            <br />
            Occupancy: {value ?? 0}%
          </div>
        )}
      />
    </div>
  );
}
