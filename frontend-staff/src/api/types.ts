// ---- Shared primitives ----

export interface BedConfigItem {
  type: string;
  count: number;
}

export interface NightlyRate {
  date: string;
  base_amount: string;
  seasonal_multiplier: string;
  weekend_multiplier: string;
  final_amount: string;
}

// ---- Booking ----

export interface BookingResponse {
  id: string;
  confirmation_number: string;
  user_id: string;
  room_type_id: string;
  room_id: string | null;
  check_in: string;
  check_out: string;
  guest_count: number;
  status: string;
  total_price: string | null;
  price_per_night: string | null;
  currency: string;
  nightly_breakdown: NightlyRate[] | null;
  guest_first_name: string | null;
  guest_last_name: string | null;
  guest_email: string | null;
  guest_phone: string | null;
  special_requests: string | null;
  expires_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  cancellation_fee: string | null;
  created_at: string;
  updated_at: string;
  // BFF enrichment fields
  room_type_name?: string;
  room_type_description?: string;
  room_type_photos?: string[];
  room_type_amenities?: string[];
}

export interface BookingListResponse {
  items: BookingResponse[];
  total: number;
}

// ---- Auth ----

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

// ---- Staff-specific types ----

export interface TodayOverview {
  arrivals_count: number;
  departures_count: number;
  occupancy_percent: number;
  rooms_to_clean: number;
  arrivals: BookingResponse[];
  departures: BookingResponse[];
}

export interface RoomStatusBoard {
  floors: { floor: number; rooms: RoomStatus[] }[];
  summary: {
    total: number;
    available: number;
    occupied: number;
    cleaning: number;
    maintenance: number;
  };
}

export interface RoomStatus {
  id: string;
  room_number: string;
  floor: number;
  status: string;
  room_type_id: string;
  room_type_name?: string;
}

export interface GuestProfile {
  user: UserResponse;
  bookings: BookingListResponse;
}

export interface UserListResponse {
  users: UserResponse[];
  total: number;
}

export interface CheckInRequest {
  room_id: string;
}

export interface StaffBookingParams {
  status?: string;
  skip?: number;
  limit?: number;
  search?: string;
  check_in_from?: string;
  check_in_to?: string;
}
