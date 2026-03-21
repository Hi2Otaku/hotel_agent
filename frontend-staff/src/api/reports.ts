import { apiClient } from './client';
import type { ReportResponse, DateRange } from './types';

export async function getReportData(dateRange: DateRange): Promise<ReportResponse> {
  const { data } = await apiClient.get<ReportResponse>('/api/v1/staff/reports', {
    params: { start_date: dateRange.from, end_date: dateRange.to },
  });
  return data;
}
