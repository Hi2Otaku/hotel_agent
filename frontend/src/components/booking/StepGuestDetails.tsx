import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import { useAuthStore } from '@/stores/authStore';
import { useSubmitGuestDetails } from '@/hooks/queries/useBookings';

const guestDetailsSchema = z.object({
  guest_first_name: z.string().min(1, 'First name is required'),
  guest_last_name: z.string().min(1, 'Last name is required'),
  guest_email: z.string().email('Enter a valid email'),
  guest_phone: z.string().min(1, 'Phone number is required'),
  special_requests: z.string().optional(),
});

type GuestDetailsFormValues = z.infer<typeof guestDetailsSchema>;

export default function StepGuestDetails() {
  const bookingId = useBookingWizardStore((s) => s.bookingId);
  const guestDetails = useBookingWizardStore((s) => s.guestDetails);
  const setGuestDetails = useBookingWizardStore((s) => s.setGuestDetails);
  const setStep = useBookingWizardStore((s) => s.setStep);
  const user = useAuthStore((s) => s.user);

  const submitGuestDetails = useSubmitGuestDetails();

  const form = useForm<GuestDetailsFormValues>({
    resolver: zodResolver(guestDetailsSchema),
    defaultValues: {
      guest_first_name:
        (guestDetails?.guest_first_name as string) || user?.first_name || '',
      guest_last_name:
        (guestDetails?.guest_last_name as string) || user?.last_name || '',
      guest_email:
        (guestDetails?.guest_email as string) || user?.email || '',
      guest_phone: (guestDetails?.guest_phone as string) || '',
      special_requests: (guestDetails?.special_requests as string) || '',
    },
  });

  function onSubmit(values: GuestDetailsFormValues) {
    if (!bookingId) return;
    setGuestDetails(values);
    submitGuestDetails.mutate(
      {
        id: bookingId,
        data: {
          guest_first_name: values.guest_first_name,
          guest_last_name: values.guest_last_name,
          guest_email: values.guest_email,
          guest_phone: values.guest_phone,
          special_requests: values.special_requests,
        },
      },
      {
        onSuccess: () => {
          setStep(3);
        },
        onError: () => {
          toast.error('Something went wrong. Please try again in a moment.');
        },
      },
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-slate-900">Guest Details</h2>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="guest_first_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-normal">
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
              name="guest_last_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-normal">
                    Last Name
                  </FormLabel>
                  <FormControl>
                    <Input placeholder="Doe" {...field} />
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="guest_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-normal">
                    Email
                  </FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="john@example.com" {...field} />
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="guest_phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-normal">
                    Phone
                  </FormLabel>
                  <FormControl>
                    <Input type="tel" placeholder="+1 (555) 000-0000" {...field} />
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="special_requests"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-normal">
                  Special Requests{' '}
                  <span className="text-muted">(optional)</span>
                </FormLabel>
                <FormControl>
                  <textarea
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 outline-none disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Any special requests for your stay?"
                    {...field}
                  />
                </FormControl>
                <FormMessage className="text-destructive text-sm" />
              </FormItem>
            )}
          />

          <div className="flex justify-between pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep(1)}
              className="min-h-[44px]"
            >
              Back
            </Button>
            <Button
              type="submit"
              disabled={submitGuestDetails.isPending}
              className="min-h-[44px] bg-accent hover:bg-accent-hover text-white"
            >
              {submitGuestDetails.isPending ? (
                <Loader2 className="animate-spin" />
              ) : (
                'Continue'
              )}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
