import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '@/stores/authStore';

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  });

  it('login sets token and isAuthenticated', () => {
    const { login } = useAuthStore.getState();
    login('test-jwt-token');

    const state = useAuthStore.getState();
    expect(state.token).toBe('test-jwt-token');
    expect(state.isAuthenticated).toBe(true);
  });

  it('login persists token to localStorage', () => {
    const { login } = useAuthStore.getState();
    login('persisted-token');

    expect(localStorage.getItem('access_token')).toBe('persisted-token');
  });

  it('logout clears token, user, and localStorage', () => {
    // Setup: login first
    useAuthStore.setState({
      token: 'some-token',
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        role: 'guest',
        is_active: true,
        created_at: '2026-01-01',
      },
      isAuthenticated: true,
    });
    localStorage.setItem('access_token', 'some-token');

    const { logout } = useAuthStore.getState();
    logout();

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('setUser stores user data', () => {
    const mockUser = {
      id: '42',
      email: 'user@example.com',
      first_name: 'Jane',
      last_name: 'Doe',
      role: 'guest',
      is_active: true,
      created_at: '2026-01-01',
    };

    const { setUser } = useAuthStore.getState();
    setUser(mockUser);

    expect(useAuthStore.getState().user).toEqual(mockUser);
  });

  it('isAuthenticated reflects token presence', () => {
    expect(useAuthStore.getState().isAuthenticated).toBe(false);

    useAuthStore.getState().login('token-123');
    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    useAuthStore.getState().logout();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
