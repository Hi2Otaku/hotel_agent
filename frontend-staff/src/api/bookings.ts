import { apiClient } from './client';
import type {
  BookingListResponse,
  BookingResponse,
  TodayOverview,
  StaffBookingParams,
} from './types';

export async function getStaffBookings(
  params?: StaffBookingParams,
): Promise<BookingListResponse> {
  const { data } = await apiClient.get<BookingListResponse>(
    '/api/v1/bookings/staff/',
    { params },
  );
  return data;
}

export async function getTodayOverview(): Promise<TodayOverview> {
  const { data } = await apiClient.get<TodayOverview>(
    '/api/v1/staff/overview',
  );
  return data;
}

export async function checkInGuest(
  bookingId: string,
  roomId: string,
): Promise<BookingResponse> {
  const { data } = await apiClient.post<BookingResponse>(
    `/api/v1/staff/check-in/${bookingId}`,
    { room_id: roomId },
  );
  return data;
}

export async function checkOutGuest(
  bookingId: string,
): Promise<BookingResponse> {
  const { data } = await apiClient.post<BookingResponse>(
    `/api/v1/staff/check-out/${bookingId}`,
  );
  return data;
}

export async function cancelBooking(
  bookingId: string,
): Promise<BookingResponse> {
  const { data } = await apiClient.post<BookingResponse>(
    `/api/v1/bookings/staff/${bookingId}/cancel`,
  );
  return data;
}

export async function getBookingsByUser(
  userId: string,
): Promise<BookingListResponse> {
  const { data } = await apiClient.get<BookingListResponse>(
    `/api/v1/bookings/staff/by-user/${userId}`,
  );
  return data;
}
