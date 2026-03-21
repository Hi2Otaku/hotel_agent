import { useEffect, useMemo, lazy, Suspense } from 'react';
import { useSearchParams, useNavigate } from 'react-router';
import { Loader2 } from 'lucide-react';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import { useAuthStore } from '@/stores/authStore';
import { useBookingDetails } from '@/hooks/queries/useBookings';
import WizardSidebar from '@/components/booking/WizardSidebar';
import BookingSummaryPanel from '@/components/booking/BookingSummaryPanel';

const StepRoomSelection = lazy(() => import('@/components/booking/StepRoomSelection'));
const StepGuestDetails = lazy(() => import('@/components/booking/StepGuestDetails'));
const StepPayment = lazy(() => import('@/components/booking/StepPayment'));
const StepConfirmation = lazy(() => import('@/components/booking/StepConfirmation'));

export default function BookingWizard() {
  const [urlParams] = useSearchParams();
  const navigate = useNavigate();

  const step = useBookingWizardStore((s) => s.step);
  const setStep = useBookingWizardStore((s) => s.setStep);
  const bookingId = useBookingWizardStore((s) => s.bookingId);
  const selectedRoom = useBookingWizardStore((s) => s.selectedRoom);
  const checkIn = useBookingWizardStore((s) => s.checkIn);
  const checkOut = useBookingWizardStore((s) => s.checkOut);
  const guests = useBookingWizardStore((s) => s.guests);
  const setSearchParams = useBookingWizardStore((s) => s.setSearchParams);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  const { data: booking, isLoading: bookingLoading } = useBookingDetails(bookingId);

  // Populate store from URL params on mount
  useEffect(() => {
    const ci = urlParams.get('checkIn');
    const co = urlParams.get('checkOut');
    const g = urlParams.get('guests');

    if (ci && co && g && !bookingId) {
      setSearchParams(ci, co, parseInt(g, 10));
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Restore step from booking status on refresh
  useEffect(() => {
    if (!booking) return;
    if (booking.status === 'confirmed' || booking.status === 'checked_in' || booking.status === 'checked_out') {
      setStep(4);
    } else if (booking.status === 'pending' && booking.guest_first_name) {
      setStep(3);
    } else if (booking.status === 'pending' && !booking.guest_first_name) {
      setStep(2);
    }
  }, [booking, setStep]);

  // Auth gate: step > 1 requires authentication
  useEffect(() => {
    if (step > 1 && !isAuthenticated) {
      const returnUrl = window.location.pathname + window.location.search;
      navigate(`/login?from=${encodeURIComponent(returnUrl)}`, { replace: true });
    }
  }, [step, isAuthenticated, navigate]);

  const completedSteps = useMemo(() => {
    const completed: number[] = [];
    if (bookingId) completed.push(1);
    if (booking?.guest_first_name) completed.push(2);
    if (booking?.status === 'confirmed' || booking?.status === 'checked_in' || booking?.status === 'checked_out') {
      completed.push(3, 4);
    }
    return completed;
  }, [bookingId, booking]);

  function handleStepClick(targetStep: number) {
    if (targetStep === 4 && !completedSteps.includes(4)) return;
    if (targetStep <= Math.max(...completedSteps, 0) + 1) {
      setStep(targetStep);
    }
  }

  if (bookingLoading && bookingId) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="size-6 animate-spin text-[#0F766E]" />
        <span className="ml-2 text-slate-500">Loading...</span>
      </div>
    );
  }

  const stepFallback = (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="size-5 animate-spin text-[#0F766E]" />
    </div>
  );

  return (
    <div className="min-h-[calc(100vh-64px)]">
      {/* Mobile steps + summary */}
      <WizardSidebar
        currentStep={step}
        onStepClick={handleStepClick}
        completedSteps={completedSteps}
      />
      <BookingSummaryPanel
        room={selectedRoom}
        checkIn={checkIn}
        checkOut={checkOut}
        guests={guests}
        booking={booking ?? null}
      />

      {/* Desktop layout */}
      <div className="hidden md:grid grid-cols-[240px_1fr] xl:grid-cols-[240px_1fr_300px] min-h-[calc(100vh-64px)]">
        {/* Desktop sidebar is already rendered above via WizardSidebar (hidden on mobile) */}
        {/* Re-render sidebar for desktop grid position */}
        <WizardSidebar
          currentStep={step}
          onStepClick={handleStepClick}
          completedSteps={completedSteps}
        />

        {/* Main content */}
        <main className="p-6 lg:p-8 max-w-2xl">
          <Suspense fallback={stepFallback}>
            {step === 1 && <StepRoomSelection />}
            {step === 2 && <StepGuestDetails />}
            {step === 3 && <StepPayment />}
            {step === 4 && <StepConfirmation />}
          </Suspense>
        </main>

        {/* Desktop summary sidebar (xl only) */}
        <aside className="hidden xl:block p-6 border-l border-[#E2E8F0] bg-[#F8FAFC]">
          <BookingSummaryPanel
            room={selectedRoom}
            checkIn={checkIn}
            checkOut={checkOut}
            guests={guests}
            booking={booking ?? null}
          />
        </aside>
      </div>

      {/* Mobile content */}
      <main className="md:hidden p-4">
        <Suspense fallback={stepFallback}>
          {step === 1 && <StepRoomSelection />}
          {step === 2 && <StepGuestDetails />}
          {step === 3 && <StepPayment />}
          {step === 4 && <StepConfirmation />}
        </Suspense>
      </main>
    </div>
  );
}
