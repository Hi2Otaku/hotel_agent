import { apiClient } from './client';
import type { SearchResponse, RoomTypeDetail, CalendarResponse } from './types';

export interface SearchParams {
  checkIn: string;
  checkOut: string;
  guests: number;
  roomTypeId?: string;
  minPrice?: number;
  maxPrice?: number;
  amenities?: string;
  sort?: string;
}

export async function searchAvailability(
  params: SearchParams,
): Promise<SearchResponse> {
  const query: Record<string, string | number> = {
    check_in: params.checkIn,
    check_out: params.checkOut,
    guests: params.guests,
  };
  if (params.roomTypeId) query.room_type_id = params.roomTypeId;
  if (params.minPrice !== undefined) query.min_price = params.minPrice;
  if (params.maxPrice !== undefined) query.max_price = params.maxPrice;
  if (params.amenities) query.amenities = params.amenities;
  if (params.sort) query.sort = params.sort;

  const { data } = await apiClient.get<SearchResponse>(
    '/api/v1/search/availability',
    { params: query },
  );
  return data;
}

export async function getRoomTypeDetail(
  id: string,
  checkIn: string,
  checkOut: string,
  guests?: number,
): Promise<RoomTypeDetail> {
  const query: Record<string, string | number> = {
    check_in: checkIn,
    check_out: checkOut,
  };
  if (guests !== undefined) query.guests = guests;

  const { data } = await apiClient.get<RoomTypeDetail>(
    `/api/v1/search/room-types/${id}`,
    { params: query },
  );
  return data;
}

export async function getPricingCalendar(
  roomTypeId?: string,
  guests?: number,
  months?: number,
): Promise<CalendarResponse> {
  const query: Record<string, string | number> = {};
  if (roomTypeId) query.room_type_id = roomTypeId;
  if (guests !== undefined) query.guests = guests;
  if (months !== undefined) query.months = months;

  const { data } = await apiClient.get<CalendarResponse>(
    '/api/v1/search/calendar',
    { params: query },
  );
  return data;
}
