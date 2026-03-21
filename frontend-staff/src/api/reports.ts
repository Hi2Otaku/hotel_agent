import { apiClient } from './client';
import type { ReportResponse, DateRange, BookingResponse, BookingListResponse } from './types';

export async function getReportData(dateRange: DateRange): Promise<ReportResponse> {
  const { data } = await apiClient.get<ReportResponse>('/api/v1/staff/reports', {
    params: { start_date: dateRange.from, end_date: dateRange.to },
  });
  return data;
}

export async function getDrillDownBookings(day: string): Promise<BookingResponse[]> {
  const { data } = await apiClient.get<BookingListResponse>(
    '/api/v1/bookings/staff/',
    { params: { date_from: day, date_to: day, limit: 50 } },
  );
  return data.items;
}
