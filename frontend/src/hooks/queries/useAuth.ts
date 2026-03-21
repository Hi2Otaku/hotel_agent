import { useMutation, useQuery } from '@tanstack/react-query';
import {
  loginUser,
  registerUser,
  getCurrentUser,
  requestPasswordReset,
  confirmPasswordReset,
} from '@/api/auth';
import { useAuthStore } from '@/stores/authStore';
import type { RegisterRequest } from '@/api/types';

export function useLogin() {
  const login = useAuthStore((s) => s.login);
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginUser(email, password),
    onSuccess: async (data) => {
      login(data.access_token);
      try {
        const user = await getCurrentUser();
        setUser(user);
      } catch {
        // Token stored, user fetch can retry later
      }
    },
  });
}

export function useRegister() {
  const login = useAuthStore((s) => s.login);
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: (data: RegisterRequest) => registerUser(data),
    onSuccess: async (data) => {
      login(data.access_token);
      try {
        const user = await getCurrentUser();
        setUser(user);
      } catch {
        // Token stored, user fetch can retry later
      }
    },
  });
}

export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: (email: string) => requestPasswordReset(email),
  });
}

export function useConfirmPasswordReset() {
  return useMutation({
    mutationFn: ({
      token,
      newPassword,
    }: {
      token: string;
      newPassword: string;
    }) => confirmPasswordReset(token, newPassword),
  });
}

export function useCurrentUser() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const setUser = useAuthStore((s) => s.setUser);

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const user = await getCurrentUser();
      setUser(user);
      return user;
    },
    enabled: isAuthenticated,
    staleTime: 300_000,
  });
}
