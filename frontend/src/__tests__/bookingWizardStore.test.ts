import { describe, it, expect, beforeEach } from 'vitest';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';

describe('bookingWizardStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useBookingWizardStore.getState().reset();
  });

  it('initial state has step 1 and null selections', () => {
    const state = useBookingWizardStore.getState();
    expect(state.step).toBe(1);
    expect(state.selectedRoom).toBeNull();
    expect(state.guestDetails).toBeNull();
    expect(state.bookingId).toBeNull();
    expect(state.guests).toBe(2);
  });

  it('setStep advances step number', () => {
    useBookingWizardStore.getState().setStep(3);
    expect(useBookingWizardStore.getState().step).toBe(3);
  });

  it('setSearchParams stores check-in, check-out, and guests', () => {
    useBookingWizardStore.getState().setSearchParams('2026-04-01', '2026-04-05', 3);

    const state = useBookingWizardStore.getState();
    expect(state.checkIn).toBe('2026-04-01');
    expect(state.checkOut).toBe('2026-04-05');
    expect(state.guests).toBe(3);
  });

  it('setSelectedRoom stores room data and room type id', () => {
    const mockRoom = {
      room_type_id: 'rt-001',
      name: 'Deluxe Suite',
      slug: 'deluxe-suite',
      description: 'A deluxe suite',
      photo_url: null,
      price_per_night: '150.00',
      total_price: '600.00',
      currency: 'USD',
      max_adults: 2,
      max_children: 1,
      bed_config: [{ type: 'king', count: 1 }],
      amenity_highlights: ['WiFi', 'Pool'],
      available_count: 3,
      total_rooms: 5,
    };

    useBookingWizardStore.getState().setSelectedRoom(mockRoom);

    const state = useBookingWizardStore.getState();
    expect(state.selectedRoom).toEqual(mockRoom);
    expect(state.roomTypeId).toBe('rt-001');
  });

  it('setGuestDetails stores guest info', () => {
    const details = {
      guest_first_name: 'John',
      guest_last_name: 'Smith',
      guest_email: 'john@example.com',
      guest_phone: '+1234567890',
    };

    useBookingWizardStore.getState().setGuestDetails(details);
    expect(useBookingWizardStore.getState().guestDetails).toEqual(details);
  });

  it('reset clears all wizard state back to initial', () => {
    // Set some state first
    useBookingWizardStore.getState().setStep(3);
    useBookingWizardStore.getState().setSearchParams('2026-04-01', '2026-04-05', 4);
    useBookingWizardStore.getState().setBookingId('booking-123');

    useBookingWizardStore.getState().reset();

    const state = useBookingWizardStore.getState();
    expect(state.step).toBe(1);
    expect(state.bookingId).toBeNull();
    expect(state.checkIn).toBeNull();
    expect(state.checkOut).toBeNull();
    expect(state.guests).toBe(2);
    expect(state.selectedRoom).toBeNull();
    expect(state.guestDetails).toBeNull();
  });
});
