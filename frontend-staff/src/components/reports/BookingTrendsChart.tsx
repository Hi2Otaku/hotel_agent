import { useMemo } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { nivoTheme, chartAnimate } from '@/lib/chartTheme';
import type { TrendDay } from '@/api/types';

interface BookingTrendsChartProps {
  data: TrendDay[];
  onPointClick: (day: string) => void;
}

export function BookingTrendsChart({ data, onPointClick }: BookingTrendsChartProps) {
  const lineData = useMemo(
    () => [
      {
        id: 'Bookings',
        data: data.map((d) => ({ x: d.day, y: d.value })),
      },
    ],
    [data],
  );

  return (
    <div role="img" aria-label="Booking trends line chart" className="h-full">
      <ResponsiveLine
        data={lineData}
        margin={{ top: 20, right: 32, bottom: 40, left: 48 }}
        xScale={{ type: 'time', format: '%Y-%m-%d', precision: 'day' }}
        xFormat="time:%b %d"
        yScale={{ type: 'linear', min: 0, max: 'auto' }}
        curve="monotoneX"
        colors={['#0F766E']}
        pointSize={6}
        pointColor="#0F172A"
        pointBorderWidth={2}
        pointBorderColor="#0F766E"
        enableCrosshair={true}
        crosshairType="x"
        useMesh={true}
        animate={chartAnimate}
        theme={nivoTheme}
        axisBottom={{
          format: '%b %d',
          tickRotation: -45,
        }}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onClick={(point: any) => onPointClick(String(point.data.x))}
      />
    </div>
  );
}
