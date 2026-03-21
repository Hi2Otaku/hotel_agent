import { useQuery } from '@tanstack/react-query';
import { getReportData } from '@/api/reports';
import type { DateRange } from '@/api/types';

export function useReportData(dateRange: DateRange) {
  return useQuery({
    queryKey: ['reports', dateRange.from, dateRange.to],
    queryFn: () => getReportData(dateRange),
    staleTime: 5 * 60 * 1000,  // 5 min -- report data doesn't change fast
    enabled: !!dateRange.from && !!dateRange.to,
  });
}
