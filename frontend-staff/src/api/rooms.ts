import { apiClient } from './client';
import type { RoomStatusBoard, RoomStatus } from './types';

export async function getRoomStatusBoard(): Promise<RoomStatusBoard> {
  const { data } = await apiClient.get<RoomStatusBoard>('/api/v1/rooms/board');
  return data;
}

export async function getAvailableRooms(
  roomTypeId: string,
): Promise<RoomStatus[]> {
  const { data } = await apiClient.get<{ items: RoomStatus[]; total: number }>(
    '/api/v1/rooms/list',
    {
      params: {
        room_type_id: roomTypeId,
        room_status: 'available',
        limit: 50,
      },
    },
  );
  return data.items;
}

export async function transitionRoomStatus(
  roomId: string,
  newStatus: string,
): Promise<RoomStatus> {
  const { data } = await apiClient.post<RoomStatus>(
    `/api/v1/rooms/${roomId}/status`,
    { status: newStatus },
  );
  return data;
}
