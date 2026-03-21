import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getStaffBookings,
  getTodayOverview,
  checkInGuest,
  checkOutGuest,
  cancelBooking,
} from '@/api/bookings';
import type { StaffBookingParams } from '@/api/types';

export function useStaffBookings(params?: StaffBookingParams) {
  return useQuery({
    queryKey: ['staff-bookings', params],
    queryFn: () => getStaffBookings(params),
  });
}

export function useTodayOverview() {
  return useQuery({
    queryKey: ['today-overview'],
    queryFn: () => getTodayOverview(),
    staleTime: 30000,
  });
}

export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookingId, roomId }: { bookingId: string; roomId: string }) =>
      checkInGuest(bookingId, roomId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['room-status'] });
      queryClient.invalidateQueries({ queryKey: ['today-overview'] });
    },
  });
}

export function useCheckOut() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (bookingId: string) => checkOutGuest(bookingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['room-status'] });
      queryClient.invalidateQueries({ queryKey: ['today-overview'] });
    },
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (bookingId: string) => cancelBooking(bookingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['today-overview'] });
    },
  });
}
