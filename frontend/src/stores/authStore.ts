import { create } from 'zustand';
import type { UserResponse } from '@/api/types';

interface AuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  login: (token: string) => {
    localStorage.setItem('access_token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  setUser: (user: UserResponse) => set({ user }),
}));
