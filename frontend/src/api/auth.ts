import { apiClient } from './client';
import type { RegisterRequest, TokenResponse, UserResponse } from './types';

export async function registerUser(data: RegisterRequest): Promise<TokenResponse> {
  const { data: result } = await apiClient.post<TokenResponse>(
    '/api/v1/auth/register',
    data,
  );
  return result;
}

export async function loginUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const { data } = await apiClient.post<TokenResponse>(
    '/api/v1/auth/login',
    params,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    },
  );
  return data;
}

export async function getCurrentUser(): Promise<UserResponse> {
  const { data } = await apiClient.get<UserResponse>('/api/v1/auth/me');
  return data;
}

export async function requestPasswordReset(
  email: string,
): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>(
    '/api/v1/auth/password-reset/request',
    { email },
  );
  return data;
}

export async function confirmPasswordReset(
  token: string,
  newPassword: string,
): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>(
    '/api/v1/auth/password-reset/confirm',
    { token, new_password: newPassword },
  );
  return data;
}
