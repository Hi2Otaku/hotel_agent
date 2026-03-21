import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router';
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
import { useLogin } from '@/hooks/queries/useAuth';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const loginMutation = useLogin();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = (values: LoginFormValues) => {
    loginMutation.mutate(
      { email: values.email, password: values.password },
      {
        onSuccess: () => {
          const from =
            (location.state as { from?: string } | null)?.from || '/';
          navigate(from, { replace: true });
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

          {loginMutation.isError && (
            <p className="text-[#DC2626] text-sm text-center mb-4">
              Invalid email or password. Please try again.
            </p>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px] font-normal">
                      Email
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="your@email.com"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage className="text-[#DC2626] text-sm" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px] font-normal">
                      Password
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
                disabled={loginMutation.isPending}
                className="w-full min-h-[44px] bg-[#0F766E] hover:bg-[#0D6660] text-white"
              >
                {loginMutation.isPending ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  'Log In'
                )}
              </Button>
            </form>
          </Form>

          <p className="text-center text-sm mt-4">
            Don&apos;t have an account?{' '}
            <Link
              to="/register"
              className="text-[#0F766E] hover:underline font-medium"
            >
              Register
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
