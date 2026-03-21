import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getRoomStatusBoard,
  getAvailableRooms,
  transitionRoomStatus,
} from '@/api/rooms';

export function useRoomStatusBoard() {
  return useQuery({
    queryKey: ['room-status'],
    queryFn: () => getRoomStatusBoard(),
    staleTime: 60000,
  });
}

export function useTransitionRoomStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ roomId, newStatus }: { roomId: string; newStatus: string }) =>
      transitionRoomStatus(roomId, newStatus),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['room-status'] });
    },
  });
}

export function useAvailableRooms(roomTypeId: string | null) {
  return useQuery({
    queryKey: ['available-rooms', roomTypeId],
    queryFn: () => getAvailableRooms(roomTypeId!),
    enabled: !!roomTypeId,
  });
}
