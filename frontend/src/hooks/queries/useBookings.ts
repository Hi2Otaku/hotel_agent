import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createBooking,
  submitGuestDetails,
  submitPayment,
  getBookings,
  getBookingDetails,
  getCancellationPolicy,
  cancelBooking,
  modifyBooking,
} from '@/api/booking';
import type {
  BookingCreate,
  GuestDetailsSubmit,
  PaymentSubmit,
  BookingModifyRequest,
} from '@/api/types';

export function useCreateBooking() {
  return useMutation({
    mutationFn: (data: BookingCreate) => createBooking(data),
  });
}

export function useSubmitGuestDetails() {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: GuestDetailsSubmit }) =>
      submitGuestDetails(id, data),
  });
}

export function useSubmitPayment() {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PaymentSubmit }) =>
      submitPayment(id, data),
  });
}

export function useBookingDetails(id: string | null) {
  return useQuery({
    queryKey: ['booking', id],
    queryFn: () => getBookingDetails(id!),
    enabled: !!id,
  });
}

export function useBookingList(params?: {
  status?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['bookings', params],
    queryFn: () => getBookings(params),
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cancelBooking(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
    },
  });
}

export function useModifyBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: BookingModifyRequest }) =>
      modifyBooking(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] });
    },
  });
}

export function useCancellationPolicy(id: string | null) {
  return useQuery({
    queryKey: ['cancellation-policy', id],
    queryFn: () => getCancellationPolicy(id!),
    enabled: !!id,
  });
}
