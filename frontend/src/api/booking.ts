import { apiClient } from './client';
import type {
  BookingCreate,
  BookingResponse,
  BookingListResponse,
  GuestDetailsSubmit,
  PaymentSubmit,
  PaymentResponse,
  CancellationPolicyResponse,
  BookingModifyRequest,
} from './types';

export async function createBooking(
  data: BookingCreate,
): Promise<BookingResponse> {
  const { data: result } = await apiClient.post<BookingResponse>(
    '/api/v1/bookings/',
    data,
  );
  return result;
}

export async function submitGuestDetails(
  id: string,
  data: GuestDetailsSubmit,
): Promise<BookingResponse> {
  const { data: result } = await apiClient.put<BookingResponse>(
    `/api/v1/bookings/${id}/guest-details`,
    data,
  );
  return result;
}

export async function submitPayment(
  id: string,
  data: PaymentSubmit,
): Promise<{ booking: BookingResponse; payment: PaymentResponse }> {
  const { data: result } = await apiClient.post<{
    booking: BookingResponse;
    payment: PaymentResponse;
  }>(`/api/v1/bookings/${id}/payment`, data);
  return result;
}

export async function getBookings(params?: {
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<BookingListResponse> {
  const { data } = await apiClient.get<BookingListResponse>(
    '/api/v1/bookings/summary',
    { params },
  );
  return data;
}

export async function getBookingDetails(
  id: string,
): Promise<BookingResponse> {
  const { data } = await apiClient.get<BookingResponse>(
    `/api/v1/bookings/${id}/details`,
  );
  return data;
}

export async function getCancellationPolicy(
  id: string,
): Promise<CancellationPolicyResponse> {
  const { data } = await apiClient.get<CancellationPolicyResponse>(
    `/api/v1/bookings/${id}/cancellation-policy`,
  );
  return data;
}

export async function cancelBooking(
  id: string,
): Promise<BookingResponse> {
  const { data } = await apiClient.post<BookingResponse>(
    `/api/v1/bookings/${id}/cancel`,
  );
  return data;
}

export async function modifyBooking(
  id: string,
  data: BookingModifyRequest,
): Promise<{
  booking: BookingResponse;
  old_total: string;
  new_total: string;
  price_difference: string;
  currency: string;
}> {
  const { data: result } = await apiClient.put<{
    booking: BookingResponse;
    old_total: string;
    new_total: string;
    price_difference: string;
    currency: string;
  }>(`/api/v1/bookings/${id}/modify`, data);
  return result;
}
