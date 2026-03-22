import { useState, useCallback, useRef } from 'react';
import { subDays, format } from 'date-fns';
import { DollarSign, Percent, CalendarCheck, TrendingUp, Download } from 'lucide-react';
import { useReportData } from '@/hooks/queries/useReports';
import { DateRangePicker } from '@/components/reports/DateRangePicker';
import { ChartContainer } from '@/components/reports/ChartContainer';
import { OccupancyHeatmap } from '@/components/reports/OccupancyHeatmap';
import { RevenueChart } from '@/components/reports/RevenueChart';
import { BookingTrendsChart } from '@/components/reports/BookingTrendsChart';
import { DrillDownPanel } from '@/components/reports/DrillDownPanel';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { Button } from '@/components/ui/button';
import { downloadCSV, exportDashboardPDF } from '@/lib/export';
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
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);

  const { data, isLoading, isError, refetch } = useReportData(dateRange);

  const handleRetry = useCallback(() => {
    refetch();
  }, [refetch]);

  const handleDayClick = useCallback((day: string) => {
    setSelectedDay(day);
  }, []);

  const handleBarClick = useCallback((period: string, _roomType: string) => {
    setSelectedDay(period);
  }, []);

  const handlePointClick = useCallback((day: string) => {
    setSelectedDay(day);
  }, []);

  const handleExportPDF = useCallback(() => {
    if (dashboardRef.current) {
      exportDashboardPDF(dashboardRef.current, dateRange);
    }
  }, [dateRange]);

  return (
    <div className="space-y-6">
      {/* Top row: date range picker + export PDF */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <DateRangePicker dateRange={dateRange} onChange={setDateRange} />
        <Button
          variant="ghost"
          onClick={handleExportPDF}
          disabled={isLoading || isError || !data}
          className="text-[#94A3B8] hover:text-[#F1F5F9]"
        >
          <Download className="mr-1 h-4 w-4" />
          Export PDF
        </Button>
      </div>

      {/* Dashboard capture area for PDF export */}
      <div ref={dashboardRef}>
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
        <div className="mt-8 space-y-8">
          <ChartContainer
            title="Occupancy Rate"
            loading={isLoading}
            error={isError}
            onRetry={handleRetry}
            empty={!data || data.occupancy.daily.length === 0}
            onExportCSV={() =>
              data &&
              downloadCSV(
                data.occupancy.daily.map((d) => ({ Date: d.day, 'Occupancy %': d.value })),
                `hotelbook-occupancy-${dateRange.from}-${dateRange.to}.csv`,
              )
            }
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
            error={isError}
            onRetry={handleRetry}
            empty={!data || data.revenue.data.length === 0}
            onExportCSV={() =>
              data &&
              downloadCSV(
                data.revenue.data.map((r) => ({
                  Period: r.period,
                  'Room Type': r.room_type_id,
                  Revenue: r.revenue,
                  Bookings: r.count,
                })),
                `hotelbook-revenue-${dateRange.from}-${dateRange.to}.csv`,
              )
            }
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
            error={isError}
            onRetry={handleRetry}
            empty={!data || data.trends.data.length === 0}
            onExportCSV={() =>
              data &&
              downloadCSV(
                data.trends.data.map((d) => ({ Date: d.day, Bookings: d.value })),
                `hotelbook-trends-${dateRange.from}-${dateRange.to}.csv`,
              )
            }
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

      {/* Drill-down panel (renders via portal) */}
      <DrillDownPanel selectedDay={selectedDay} onClose={() => setSelectedDay(null)} />
    </div>
  );
}
