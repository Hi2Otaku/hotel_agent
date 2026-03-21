import { useQuery } from '@tanstack/react-query';
import { searchGuests, getGuestProfile } from '@/api/guests';

export function useGuestSearch(query: string) {
  return useQuery({
    queryKey: ['guest-search', query],
    queryFn: () => searchGuests(query),
    enabled: query.length >= 2,
  });
}

export function useGuestProfile(userId: string | null) {
  return useQuery({
    queryKey: ['guest-profile', userId],
    queryFn: () => getGuestProfile(userId!),
    enabled: !!userId,
  });
}
