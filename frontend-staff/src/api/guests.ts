import { apiClient } from './client';
import type { UserResponse, GuestProfile } from './types';

export async function searchGuests(query: string): Promise<UserResponse[]> {
  const { data } = await apiClient.get<UserResponse[]>(
    '/api/v1/staff/guests/search',
    { params: { q: query } },
  );
  return data;
}

export async function getGuestProfile(userId: string): Promise<GuestProfile> {
  const { data } = await apiClient.get<GuestProfile>(
    `/api/v1/staff/guests/${userId}/profile`,
  );
  return data;
}
