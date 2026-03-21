import { create } from 'zustand';
import { apiClient } from '@/api/client';
import type { UserResponse } from '@/api/types';

const STAFF_ROLES = ['admin', 'manager', 'front_desk', 'housekeeping'] as const;

function getStoredToken(): string | null {
  try {
    return localStorage.getItem('staff_access_token');
  } catch {
    return null;
  }
}

interface AuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
  fetchUser: () => Promise<void>;
  isStaff: () => boolean;
}

export { STAFF_ROLES };

export const useAuthStore = create<AuthState>((set, get) => ({
  token: getStoredToken(),
  user: null,
  isAuthenticated: !!getStoredToken(),
  login: (token: string) => {
    localStorage.setItem('staff_access_token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('staff_access_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  setUser: (user: UserResponse) => set({ user }),
  fetchUser: async () => {
    try {
      const { data } = await apiClient.get<UserResponse>('/api/v1/auth/me');
      set({ user: data });
    } catch {
      get().logout();
    }
  },
  isStaff: () => {
    const { user } = get();
    if (!user) return false;
    return (STAFF_ROLES as readonly string[]).includes(user.role);
  },
}));
