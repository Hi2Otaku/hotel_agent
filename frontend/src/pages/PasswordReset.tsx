import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router';
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
import { useRequestPasswordReset } from '@/hooks/queries/useAuth';
import { useState } from 'react';

const resetSchema = z.object({
  email: z.string().email('Enter a valid email'),
});

type ResetFormValues = z.infer<typeof resetSchema>;

export default function PasswordReset() {
  const resetMutation = useRequestPasswordReset();
  const [submitted, setSubmitted] = useState(false);

  const form = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    defaultValues: { email: '' },
  });

  const onSubmit = (values: ResetFormValues) => {
    resetMutation.mutate(values.email, {
      onSuccess: () => {
        setSubmitted(true);
      },
      onError: () => {
        toast.error('Something went wrong. Please try again in a moment.');
      },
    });
  };

  return (
    <div className="min-h-[calc(100vh-64px-200px)] flex items-center justify-center bg-surface px-4">
      <Card className="w-full max-w-[400px] bg-white shadow-md">
        <CardContent className="pt-8 pb-8">
          <div className="text-center mb-6">
            <span className="text-2xl font-semibold text-accent">
              HotelBook
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-center mb-2">
            Reset Password
          </h1>

          {submitted ? (
            <div className="text-center" aria-live="polite">
              <p className="text-success text-sm mb-4">
                If an account exists with that email, you&apos;ll receive a
                reset link.
              </p>
              <p className="text-sm">
                Back to{' '}
                <Link
                  to="/login"
                  className="text-accent hover:underline font-medium"
                >
                  Log In
                </Link>
              </p>
            </div>
          ) : (
            <>
              <p className="text-base text-muted text-center mb-6">
                Enter your email and we&apos;ll send you a reset link.
              </p>

              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-4"
                >
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-normal">
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

                  <Button
                    type="submit"
                    disabled={resetMutation.isPending}
                    className="w-full min-h-[44px] bg-accent hover:bg-accent-hover text-white"
                  >
                    {resetMutation.isPending ? (
                      <Loader2 className="animate-spin" />
                    ) : (
                      'Send Reset Link'
                    )}
                  </Button>
                </form>
              </Form>

              <p className="text-center text-sm mt-4">
                Back to{' '}
                <Link
                  to="/login"
                  className="text-accent hover:underline font-medium"
                >
                  Log In
                </Link>
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
