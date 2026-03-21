import { useQuery } from '@tanstack/react-query';
import { getRoomStatusBoard, getAvailableRooms } from '@/api/rooms';

export function useRoomStatusBoard() {
  return useQuery({
    queryKey: ['room-status'],
    queryFn: () => getRoomStatusBoard(),
    staleTime: 60000,
  });
}

export function useAvailableRooms(roomTypeId: string | null) {
  return useQuery({
    queryKey: ['available-rooms', roomTypeId],
    queryFn: () => getAvailableRooms(roomTypeId!),
    enabled: !!roomTypeId,
  });
}
