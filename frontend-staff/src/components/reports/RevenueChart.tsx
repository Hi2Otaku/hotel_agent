import { useMemo } from 'react';
import { ResponsiveBar } from '@nivo/bar';
import { nivoTheme, CHART_COLORS, chartAnimate } from '@/lib/chartTheme';
import type { RevenueRow } from '@/api/types';

interface RevenueChartProps {
  data: RevenueRow[];
  groupBy: string;
  onBarClick: (period: string, roomType: string) => void;
}

export function RevenueChart({ data, groupBy: _groupBy, onBarClick }: RevenueChartProps) {
  const { barData, roomTypeKeys } = useMemo(() => {
    const periodMap = new Map<string, Record<string, number>>();
    const roomTypes = new Set<string>();

    for (const row of data) {
      const displayName = row.room_type_name || row.room_type_id.substring(0, 8);
      roomTypes.add(displayName);

      if (!periodMap.has(row.period)) {
        periodMap.set(row.period, { period: 0 });
      }
      const entry = periodMap.get(row.period)!;
      entry[displayName] = (entry[displayName] ?? 0) + Number(row.revenue);
    }

    const keys = Array.from(roomTypes);
    const barEntries = Array.from(periodMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([period, values]) => ({
        period,
        ...values,
      }));

    return { barData: barEntries, roomTypeKeys: keys };
  }, [data]);

  return (
    <div role="img" aria-label="Revenue by room type bar chart" className="h-full">
      <ResponsiveBar
        data={barData}
        keys={roomTypeKeys}
        indexBy="period"
        margin={{ top: 20, right: 130, bottom: 40, left: 60 }}
        padding={0.3}
        borderRadius={2}
        colors={CHART_COLORS}
        animate={chartAnimate}
        theme={nivoTheme}
        axisLeft={{
          format: (v) => '$' + (Number(v) / 1000).toFixed(0) + 'k',
        }}
        axisBottom={{
          tickRotation: -45,
        }}
        enableLabel={false}
        legends={[
          {
            dataFrom: 'keys',
            anchor: 'bottom-right',
            direction: 'column',
            translateX: 120,
            itemWidth: 100,
            itemHeight: 20,
            itemsSpacing: 2,
            symbolSize: 12,
            itemTextColor: '#94A3B8',
          },
        ]}
        onClick={(datum) =>
          onBarClick(String(datum.indexValue), String(datum.id))
        }
      />
    </div>
  );
}
