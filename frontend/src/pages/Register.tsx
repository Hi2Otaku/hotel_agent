import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
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
import { useRegister } from '@/hooks/queries/useAuth';
import { useState } from 'react';
import { AxiosError } from 'axios';

const registerSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function Register() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const [duplicateEmail, setDuplicateEmail] = useState(false);

  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { first_name: '', last_name: '', email: '', password: '' },
  });

  const onSubmit = (values: RegisterFormValues) => {
    setDuplicateEmail(false);
    registerMutation.mutate(values, {
      onSuccess: () => {
        navigate('/', { replace: true });
      },
      onError: (error) => {
        if (error instanceof AxiosError && error.response?.status === 409) {
          setDuplicateEmail(true);
        } else {
          toast.error('Something went wrong. Please try again in a moment.');
        }
      },
    });
  };

  return (
    <div className="min-h-[calc(100vh-64px-200px)] flex items-center justify-center bg-surface px-4">
      <Card className="w-full max-w-[400px] bg-white shadow-md">
        <CardContent className="pt-8 pb-8">
          <div className="text-center mb-6">
            <span className="text-[24px] font-semibold text-accent">
              HotelBook
            </span>
          </div>

          {duplicateEmail && (
            <p className="text-destructive text-sm text-center mb-4">
              An account with this email already exists.
            </p>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px] font-normal">
                      First Name
                    </FormLabel>
                    <FormControl>
                      <Input placeholder="John" {...field} />
                    </FormControl>
                    <FormMessage className="text-destructive text-sm" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[14px] font-normal">
                      Last Name
                    </FormLabel>
                    <FormControl>
                      <Input placeholder="Doe" {...field} />
                    </FormControl>
                    <FormMessage className="text-destructive text-sm" />
                  </FormItem>
                )}
              />

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
                    <FormMessage className="text-destructive text-sm" />
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
                    <FormMessage className="text-destructive text-sm" />
                  </FormItem>
                )}
              />

              <Button
                type="submit"
                disabled={registerMutation.isPending}
                className="w-full min-h-[44px] bg-accent hover:bg-accent-hover text-white"
              >
                {registerMutation.isPending ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  'Create Account'
                )}
              </Button>
            </form>
          </Form>

          <p className="text-center text-sm mt-4">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-accent hover:underline font-medium"
            >
              Log In
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
