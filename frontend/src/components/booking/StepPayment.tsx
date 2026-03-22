import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { AxiosError } from 'axios';
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
import { useSubmitPayment } from '@/hooks/queries/useBookings';

const paymentSchema = z.object({
  card_number: z
    .string()
    .min(13, 'Card number must be 13-19 digits')
    .max(19),
  expiry_month: z.string().min(1, 'Required'),
  expiry_year: z.string().min(1, 'Required'),
  cvc: z.string().min(3, 'CVC must be 3-4 digits').max(4),
  cardholder_name: z.string().min(1, 'Cardholder name is required'),
});

type PaymentFormValues = z.infer<typeof paymentSchema>;

export default function StepPayment() {
  const bookingId = useBookingWizardStore((s) => s.bookingId);
  const setStep = useBookingWizardStore((s) => s.setStep);

  const submitPayment = useSubmitPayment();

  const form = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      card_number: '',
      expiry_month: '',
      expiry_year: '',
      cvc: '',
      cardholder_name: '',
    },
  });

  function onSubmit(values: PaymentFormValues) {
    if (!bookingId) return;
    submitPayment.mutate(
      {
        id: bookingId,
        data: {
          card_number: values.card_number,
          expiry_month: Number(values.expiry_month),
          expiry_year: Number(values.expiry_year),
          cvc: values.cvc,
          cardholder_name: values.cardholder_name,
        },
      },
      {
        onSuccess: () => {
          setStep(4);
        },
        onError: (error) => {
          if (
            error instanceof AxiosError &&
            error.response?.data?.detail?.includes?.('declined')
          ) {
            form.setError('card_number', {
              message:
                'Payment was declined. Please try another card.',
            });
          } else {
            toast.error(
              'Something went wrong. Please try again in a moment.',
            );
          }
        },
      },
    );
  }

  const months = Array.from({ length: 12 }, (_, i) =>
    String(i + 1).padStart(2, '0'),
  );
  const years = Array.from({ length: 5 }, (_, i) => String(2026 + i));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-slate-900">Payment</h2>

      {/* Demo disclaimer */}
      <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-md">
        <AlertTriangle className="size-5 text-amber-600 shrink-0 mt-0.5" />
        <p className="text-sm text-amber-800">
          This is a demo application. No real charges will be made.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="cardholder_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-[14px] font-normal">
                  Cardholder Name
                </FormLabel>
                <FormControl>
                  <Input placeholder="John Doe" {...field} />
                </FormControl>
                <FormMessage className="text-destructive text-sm" />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="card_number"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-[14px] font-normal">
                  Card Number
                </FormLabel>
                <FormControl>
                  <Input placeholder="4242 4242 4242 4242" {...field} />
                </FormControl>
                <FormMessage className="text-destructive text-sm" />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-[1fr_1fr_auto] gap-4">
            <FormField
              control={form.control}
              name="expiry_month"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[14px] font-normal">
                    Month
                  </FormLabel>
                  <FormControl>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                      value={field.value || ''}
                      onChange={(e) =>
                        field.onChange(
                          e.target.value,
                        )
                      }
                    >
                      <option value="">MM</option>
                      {months.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="expiry_year"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[14px] font-normal">
                    Year
                  </FormLabel>
                  <FormControl>
                    <select
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                      value={field.value || ''}
                      onChange={(e) =>
                        field.onChange(
                          e.target.value,
                        )
                      }
                    >
                      <option value="">YYYY</option>
                      {years.map((y) => (
                        <option key={y} value={y}>
                          {y}
                        </option>
                      ))}
                    </select>
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="cvc"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[14px] font-normal">
                    CVC
                  </FormLabel>
                  <FormControl>
                    <Input
                      className="w-24"
                      placeholder="123"
                      maxLength={4}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-destructive text-sm" />
                </FormItem>
              )}
            />
          </div>

          <div className="flex justify-between pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep(2)}
              className="min-h-[44px]"
            >
              Back
            </Button>
            <Button
              type="submit"
              disabled={submitPayment.isPending}
              className="min-h-[44px] bg-accent hover:bg-accent-hover text-white"
            >
              {submitPayment.isPending ? (
                <>
                  <Loader2 className="animate-spin" />
                  Processing...
                </>
              ) : (
                'Confirm & Pay'
              )}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
