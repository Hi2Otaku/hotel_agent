import { useQuery } from '@tanstack/react-query';
import {
  searchAvailability,
  getRoomTypeDetail,
  getPricingCalendar,
  type SearchParams,
} from '@/api/search';

export function useSearchAvailability(params: Partial<SearchParams>) {
  return useQuery({
    queryKey: ['search', params],
    queryFn: () =>
      searchAvailability({
        checkIn: params.checkIn!,
        checkOut: params.checkOut!,
        guests: params.guests!,
        roomTypeId: params.roomTypeId,
        minPrice: params.minPrice,
        maxPrice: params.maxPrice,
        amenities: params.amenities,
        sort: params.sort,
      }),
    enabled: Boolean(params.checkIn && params.checkOut),
    staleTime: 30_000,
  });
}

export function useRoomTypeDetail(
  id: string | undefined,
  checkIn: string | undefined,
  checkOut: string | undefined,
  guests?: number,
) {
  return useQuery({
    queryKey: ['room-type', id, checkIn, checkOut],
    queryFn: () => getRoomTypeDetail(id!, checkIn!, checkOut!, guests),
    enabled: Boolean(id && checkIn && checkOut),
  });
}

export function usePricingCalendar(
  roomTypeId?: string,
  guests?: number,
  months?: number,
) {
  return useQuery({
    queryKey: ['calendar', roomTypeId, guests, months],
    queryFn: () => getPricingCalendar(roomTypeId, guests, months),
    staleTime: 60_000,
  });
}
