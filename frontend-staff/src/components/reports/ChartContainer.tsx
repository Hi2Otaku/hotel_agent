import type { ReactNode } from 'react';
import { Download } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

interface ChartContainerProps {
  title: string;
  loading: boolean;
  empty: boolean;
  children: ReactNode;
  onExportCSV?: () => void;
  chartHeight?: string;
}

export function ChartContainer({
  title,
  loading,
  empty,
  children,
  onExportCSV,
  chartHeight,
}: ChartContainerProps) {
  const heightClass = chartHeight ?? 'h-[220px] md:h-[260px] lg:h-[300px]';

  return (
    <Card className="bg-[#1E293B] border-[#334155] p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[20px] font-semibold leading-[1.2] text-[#F1F5F9]">
          {title}
        </h3>
        {onExportCSV && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onExportCSV}
            className="text-[#94A3B8] hover:text-[#F1F5F9]"
          >
            <Download className="mr-1 h-4 w-4" />
            Export CSV
          </Button>
        )}
      </div>

      <div className={heightClass}>
        {loading ? (
          <Skeleton className="h-full w-full bg-[#0F172A]" />
        ) : empty ? (
          <div className="flex h-full flex-col items-center justify-center">
            <p className="text-sm text-[#94A3B8]">No data for this period</p>
            <p className="mt-1 text-xs text-[#64748B]">
              Try selecting a different date range to view reporting data.
            </p>
          </div>
        ) : (
          children
        )}
      </div>
    </Card>
  );
}
