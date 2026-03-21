import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useSearchParams, useNavigate } from 'react-router';
import { Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { useConfirmPasswordReset } from '@/hooks/queries/useAuth';
import { useState, useEffect } from 'react';
import { AxiosError } from 'axios';

const confirmSchema = z
  .object({
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type ConfirmFormValues = z.infer<typeof confirmSchema>;

export default function PasswordResetConfirm() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const confirmMutation = useConfirmPasswordReset();
  const [success, setSuccess] = useState(false);
  const [expiredError, setExpiredError] = useState(false);

  const form = useForm<ConfirmFormValues>({
    resolver: zodResolver(confirmSchema),
    defaultValues: { password: '', confirmPassword: '' },
  });

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        navigate('/login', { replace: true });
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [success, navigate]);

  if (!token) {
    return (
      <div className="min-h-[calc(100vh-64px-200px)] flex items-center justify-center bg-[#F8FAFC] px-4">
        <Card className="w-full max-w-[400px] bg-white shadow-md">
          <CardContent className="pt-8 pb-8 text-center">
            <p className="text-[#DC2626] text-sm mb-4">
              Invalid or missing reset token.
            </p>
            <Link
              to="/password-reset"
              className="text-[#0F766E] hover:underline font-medium text-sm"
            >
              Request a new reset link
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const onSubmit = (values: ConfirmFormValues) => {
    setExpiredError(false);
    confirmMutation.mutate(
      { token, newPassword: values.password },
      {
        onSuccess: () => {
          setSuccess(true);
        },
        onError: (error) => {
          if (error instanceof AxiosError && error.response?.status === 400) {
            setExpiredError(true);
          }
        },
      },
    );
  };

  return (
    <div className="min-h-[calc(100vh-64px-200px)] flex items-center justify-center bg-[#F8FAFC] px-4">
      <Card className="w-full max-w-[400px] bg-white shadow-md">
        <CardContent className="pt-8 pb-8">
          <div className="text-center mb-6">
            <span className="text-[24px] font-semibold text-[#0F766E]">
              HotelBook
            </span>
          </div>

          <h1 className="text-[24px] font-semibold text-center mb-6">
            Set New Password
          </h1>

          {success ? (
            <div className="text-center">
              <p className="text-[#16A34A] text-sm mb-2">
                Password reset successfully.
              </p>
              <p className="text-sm text-[#64748B]">
                Redirecting to login...
              </p>
            </div>
          ) : (
            <>
              {expiredError && (
                <div className="text-center mb-4">
                  <p className="text-[#DC2626] text-sm mb-1">
                    Reset link has expired. Please request a new one.
                  </p>
                  <Link
                    to="/password-reset"
                    className="text-[#0F766E] hover:underline font-medium text-sm"
                  >
                    Request new reset link
                  </Link>
                </div>
              )}

              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4"
                >
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-[14px] font-normal">
                          New Password
                        </FormLabel>
                        <FormControl>
                          <Input type="password" {...field} />
                        </FormControl>
                        <FormMessage className="text-[#DC2626] text-sm" />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-[14px] font-normal">
                          Confirm Password
                        </FormLabel>
                        <FormControl>
                          <Input type="password" {...field} />
                        </FormControl>
                        <FormMessage className="text-[#DC2626] text-sm" />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    disabled={confirmMutation.isPending}
                    className="w-full min-h-[44px] bg-[#0F766E] hover:bg-[#0D6660] text-white"
                  >
                    {confirmMutation.isPending ? (
                      <Loader2 className="animate-spin" />
                    ) : (
                      'Reset Password'
                    )}
                  </Button>
                </form>
              </Form>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
