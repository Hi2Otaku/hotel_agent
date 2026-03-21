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

// ---- Search / Room types ----

export interface SearchResult {
  room_type_id: string;
  name: string;
  slug: string;
  description: string;
  photo_url: string | null;
  price_per_night: string;
  total_price: string;
  currency: string;
  max_adults: number;
  max_children: number;
  bed_config: BedConfigItem[];
  amenity_highlights: string[];
  available_count: number;
  total_rooms: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  check_in: string;
  check_out: string;
  guests: number;
}

export interface RoomTypeDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  max_adults: number;
  max_children: number;
  bed_config: BedConfigItem[];
  amenities: Record<string, string[]>;
  photo_urls: string[];
  available_count: number;
  total_rooms: number;
  price_per_night: string;
  total_price: string;
  currency: string;
  nightly_rates: NightlyRate[];
}

export interface CalendarDay {
  date: string;
  rate: string;
  base_amount: string;
  seasonal_multiplier: string;
  weekend_multiplier: string;
  available_count: number;
  total_rooms: number;
  availability_indicator: 'green' | 'yellow' | 'red';
}

export interface CalendarResponse {
  room_type_id: string | null;
  room_type_name: string | null;
  start_date: string;
  end_date: string;
  days: CalendarDay[];
}

// ---- Booking ----

export interface BookingCreate {
  room_type_id: string;
  check_in: string;
  check_out: string;
  guest_count: number;
}

export interface GuestDetailsSubmit {
  guest_first_name: string;
  guest_last_name: string;
  guest_email: string;
  guest_phone: string;
  guest_address?: string;
  special_requests?: string;
  id_document?: string;
}

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

export interface BookingModifyRequest {
  check_in?: string;
  check_out?: string;
  room_type_id?: string;
  guest_count?: number;
  guest_first_name?: string;
  guest_last_name?: string;
  guest_phone?: string;
  guest_address?: string;
  special_requests?: string;
}

export interface CancellationPolicyResponse {
  free_cancellation_before: string | null;
  cancellation_fee: string | null;
  policy_text: string;
}

// ---- Payment ----

export interface PaymentSubmit {
  card_number: string;
  expiry_month: number;
  expiry_year: number;
  cvc: string;
  cardholder_name: string;
  billing_address?: string;
}

export interface PaymentResponse {
  transaction_id: string;
  status: string;
  amount: string;
  currency: string;
  card_last_four: string;
  card_brand: string;
  decline_reason?: string;
}

// ---- Auth ----

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

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
