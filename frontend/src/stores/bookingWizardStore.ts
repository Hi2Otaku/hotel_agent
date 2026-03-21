import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SearchResult, GuestDetailsSubmit } from '@/api/types';

interface BookingWizardState {
  step: number;
  bookingId: string | null;
  roomTypeId: string | null;
  checkIn: string | null;
  checkOut: string | null;
  guests: number;
  selectedRoom: SearchResult | null;
  guestDetails: Partial<GuestDetailsSubmit> | null;
  setStep: (step: number) => void;
  setBookingId: (id: string) => void;
  setSearchParams: (checkIn: string, checkOut: string, guests: number) => void;
  setSelectedRoom: (room: SearchResult) => void;
  setGuestDetails: (details: Partial<GuestDetailsSubmit>) => void;
  reset: () => void;
}

const initialState = {
  step: 1,
  bookingId: null,
  roomTypeId: null,
  checkIn: null,
  checkOut: null,
  guests: 2,
  selectedRoom: null,
  guestDetails: null,
};

export const useBookingWizardStore = create<BookingWizardState>()(
  persist(
    (set) => ({
      ...initialState,
      setStep: (step: number) => set({ step }),
      setBookingId: (id: string) => set({ bookingId: id }),
      setSearchParams: (checkIn: string, checkOut: string, guests: number) =>
        set({ checkIn, checkOut, guests }),
      setSelectedRoom: (room: SearchResult) =>
        set({ selectedRoom: room, roomTypeId: room.room_type_id }),
      setGuestDetails: (details: Partial<GuestDetailsSubmit>) =>
        set({ guestDetails: details }),
      reset: () => set(initialState),
    }),
    { name: 'booking-wizard' },
  ),
);
