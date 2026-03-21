import { useState, useCallback } from 'react';
import { subDays, format } from 'date-fns';
import { DollarSign, Percent, CalendarCheck, TrendingUp, FileText } from 'lucide-react';
import { useReportData } from '@/hooks/queries/useReports';
import { DateRangePicker } from '@/components/reports/DateRangePicker';
import { ChartContainer } from '@/components/reports/ChartContainer';
import { OccupancyHeatmap } from '@/components/reports/OccupancyHeatmap';
import { RevenueChart } from '@/components/reports/RevenueChart';
import { BookingTrendsChart } from '@/components/reports/BookingTrendsChart';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { Button } from '@/components/ui/button';
import type { DateRange } from '@/api/types';

function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '$0';
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function defaultDateRange(): DateRange {
  const now = new Date();
  return {
    from: format(subDays(now, 30), 'yyyy-MM-dd'),
    to: format(now, 'yyyy-MM-dd'),
  };
}

export default function ReportsPage() {
  const [dateRange, setDateRange] = useState<DateRange>(defaultDateRange);

  const { data, isLoading } = useReportData(dateRange);

  const handleDayClick = useCallback((_day: string) => {
    // Drill-down wired in plan 03
  }, []);

  const handleBarClick = useCallback((_period: string, _roomType: string) => {
    // Drill-down wired in plan 03
  }, []);

  const handlePointClick = useCallback((_day: string) => {
    // Drill-down wired in plan 03
  }, []);

  const noopExport = useCallback(() => {
    // CSV export wired in plan 03
  }, []);

  return (
    <div className="space-y-6">
      {/* Top row: date range picker + export PDF */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <DateRangePicker dateRange={dateRange} onChange={setDateRange} />
        <Button disabled className="text-[#94A3B8]">
          <FileText className="mr-1 h-4 w-4" />
          Export PDF
        </Button>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={DollarSign}
          value={data ? formatCurrency(data.kpis.total_revenue) : '-'}
          label="Total Revenue"
          loading={isLoading}
        />
        <MetricCard
          icon={Percent}
          value={data ? `${data.occupancy.avg_occupancy.toFixed(1)}%` : '-'}
          label="Avg Occupancy"
          loading={isLoading}
        />
        <MetricCard
          icon={CalendarCheck}
          value={data ? data.kpis.total_bookings : '-'}
          label="Total Bookings"
          loading={isLoading}
        />
        <MetricCard
          icon={TrendingUp}
          value={data ? formatCurrency(data.kpis.avg_daily_rate) : '-'}
          label="Avg Daily Rate"
          loading={isLoading}
        />
      </div>

      {/* Charts */}
      <div className="space-y-8">
        <ChartContainer
          title="Occupancy Rate"
          loading={isLoading}
          empty={!data || data.occupancy.daily.length === 0}
          onExportCSV={noopExport}
        >
          {data && (
            <OccupancyHeatmap
              data={data.occupancy.daily}
              from={dateRange.from}
              to={dateRange.to}
              onDayClick={handleDayClick}
            />
          )}
        </ChartContainer>

        <ChartContainer
          title="Revenue by Room Type"
          loading={isLoading}
          empty={!data || data.revenue.data.length === 0}
          onExportCSV={noopExport}
        >
          {data && (
            <RevenueChart
              data={data.revenue.data}
              groupBy={data.revenue.group_by}
              onBarClick={handleBarClick}
            />
          )}
        </ChartContainer>

        <ChartContainer
          title="Booking Trends"
          loading={isLoading}
          empty={!data || data.trends.data.length === 0}
          onExportCSV={noopExport}
        >
          {data && (
            <BookingTrendsChart
              data={data.trends.data}
              onPointClick={handlePointClick}
            />
          )}
        </ChartContainer>
      </div>
    </div>
  );
}
