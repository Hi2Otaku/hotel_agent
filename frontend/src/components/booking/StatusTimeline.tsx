import { Check, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatusTimelineProps {
  status: string;
}

const steps = [
  { key: 'pending', label: 'Booked', shortLabel: 'Booked' },
  { key: 'confirmed', label: 'Confirmed', shortLabel: 'Conf.' },
  { key: 'checked_in', label: 'Checked In', shortLabel: 'In' },
  { key: 'checked_out', label: 'Checked Out', shortLabel: 'Out' },
];

const statusToStep: Record<string, number> = {
  pending: 0,
  confirmed: 1,
  checked_in: 2,
  checked_out: 3,
};

export function StatusTimeline({ status }: StatusTimelineProps) {
  const isCancelled = status === 'cancelled' || status === 'no_show';
  const currentStep = statusToStep[status] ?? -1;

  return (
    <div className="w-full" role="group" aria-label="Booking status timeline">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = !isCancelled && index < currentStep;
          const isCurrent = !isCancelled && index === currentStep;
          const isFuture = isCancelled || index > currentStep;

          return (
            <div key={step.key} className="flex flex-1 items-center">
              {/* Dot + label */}
              <div
                className="flex flex-col items-center"
                aria-current={isCurrent ? 'step' : undefined}
              >
                <div
                  className={cn(
                    'flex h-3 w-3 items-center justify-center rounded-full',
                    isCompleted && 'bg-[#0F766E]',
                    isCurrent && 'bg-[#0F766E]',
                    isFuture && 'border-2 border-[#E2E8F0] bg-white',
                    isCancelled && 'border-2 border-[#E2E8F0] bg-white'
                  )}
                >
                  {isCompleted && <Check className="h-2 w-2 text-white" />}
                </div>
                <span
                  className={cn(
                    'mt-1.5 text-[14px]',
                    isCurrent && 'font-semibold text-slate-900',
                    isCompleted && 'text-[#0F766E]',
                    isFuture && 'text-[#64748B]',
                    isCancelled && 'text-[#64748B]'
                  )}
                >
                  <span className="hidden sm:inline">{step.label}</span>
                  <span className="sm:hidden">{step.shortLabel}</span>
                </span>
              </div>

              {/* Connecting line */}
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'mx-1 h-0.5 flex-1 sm:mx-2',
                    !isCancelled && index < currentStep
                      ? 'bg-[#0F766E]'
                      : 'bg-slate-200'
                  )}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Cancelled label */}
      {isCancelled && (
        <div className="mt-3 flex items-center gap-1.5">
          <XCircle className="h-4 w-4 text-red-600" />
          <span className="text-sm font-medium text-red-600">
            {status === 'no_show' ? 'No Show' : 'Cancelled'}
          </span>
        </div>
      )}
    </div>
  );
}
