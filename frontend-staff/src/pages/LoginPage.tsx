import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useForm } from 'react-hook-form';
import { z } from 'zod/v4';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { apiClient } from '@/api/client';
import { useAuthStore, STAFF_ROLES } from '@/stores/authStore';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { TokenResponse } from '@/api/types';

const loginSchema = z.object({
  email: z.email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

function decodeJwtPayload(token: string): Record<string, unknown> {
  const base64 = token.split('.')[1];
  const json = atob(base64);
  return JSON.parse(json) as Record<string, unknown>;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, setUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      // OAuth2 form data format
      const formData = new URLSearchParams();
      formData.append('username', data.email);
      formData.append('password', data.password);

      const response = await apiClient.post<TokenResponse>(
        '/api/v1/auth/login',
        formData,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
      );

      const token = response.data.access_token;

      // Decode JWT to check role
      const payload = decodeJwtPayload(token);
      const role = payload.role as string;

      if (!(STAFF_ROLES as readonly string[]).includes(role)) {
        toast.error('You do not have permission to access this page.');
        setIsLoading(false);
        return;
      }

      // Store token and load user
      login(token);
      setUser({
        id: payload.sub as string,
        email: data.email,
        first_name: (payload.first_name as string) ?? '',
        last_name: (payload.last_name as string) ?? '',
        role,
        is_active: true,
        created_at: '',
      });

      navigate('/', { replace: true });
    } catch {
      toast.error('Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0F172A] px-4">
      <Card className="w-full max-w-sm bg-[#1E293B] border-[#334155]">
        <CardHeader className="space-y-1 text-center">
          <h1 className="text-xl font-semibold text-[#F1F5F9]">Staff Login</h1>
          <p className="text-sm text-[#94A3B8]">
            Access the hotel management dashboard
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[#F1F5F9]">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="staff@hotelbook.com"
                className="bg-[#1E293B] border-[#334155] text-[#F1F5F9] placeholder:text-[#64748B]"
                {...register('email')}
              />
              {errors.email && (
                <p className="text-xs text-[#DC2626]">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-[#F1F5F9]">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                className="bg-[#1E293B] border-[#334155] text-[#F1F5F9] placeholder:text-[#64748B]"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-xs text-[#DC2626]">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#0F766E] hover:bg-[#0D6B63] text-white"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
