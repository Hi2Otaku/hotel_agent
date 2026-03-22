import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

const STEPS = [
  { number: 1, label: 'Select Room' },
  { number: 2, label: 'Guest Details' },
  { number: 3, label: 'Payment' },
  { number: 4, label: 'Confirmation' },
];

interface WizardSidebarProps {
  currentStep: number;
  onStepClick: (step: number) => void;
  completedSteps: number[];
}

export default function WizardSidebar({
  currentStep,
  onStepClick,
  completedSteps,
}: WizardSidebarProps) {
  const maxCompleted = completedSteps.length > 0 ? Math.max(...completedSteps) : 0;

  function isClickable(stepNumber: number) {
    if (stepNumber === 4) return completedSteps.includes(4);
    return stepNumber <= maxCompleted + 1;
  }

  return (
    <>
      {/* Desktop sidebar */}
      <nav
        className="hidden md:flex flex-col gap-4 w-[240px] bg-surface p-6 border-r border-border min-h-full"
        aria-label="Booking steps"
      >
        {STEPS.map((step) => {
          const isActive = step.number === currentStep;
          const isCompleted = completedSteps.includes(step.number);
          const clickable = isClickable(step.number);

          return (
            <button
              key={step.number}
              type="button"
              onClick={() => clickable && onStepClick(step.number)}
              disabled={!clickable}
              className={cn(
                'flex items-center gap-3 text-left transition-colors',
                clickable ? 'cursor-pointer' : 'cursor-default',
              )}
              aria-current={isActive ? 'step' : undefined}
            >
              <span
                className={cn(
                  'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium shrink-0 transition-colors',
                  isActive && 'bg-accent text-white',
                  isCompleted && !isActive && 'bg-accent text-white',
                  !isActive && !isCompleted && 'border border-border bg-white text-muted',
                )}
              >
                {isCompleted && !isActive ? (
                  <Check className="size-4" />
                ) : (
                  step.number
                )}
              </span>
              <span
                className={cn(
                  'text-sm',
                  isActive && 'font-semibold text-slate-900',
                  isCompleted && !isActive && 'text-slate-700',
                  !isActive && !isCompleted && 'text-muted',
                )}
              >
                {step.number}. {step.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Mobile horizontal steps */}
      <nav
        className="flex md:hidden items-center justify-center gap-2 px-4 py-3 bg-surface border-b border-border"
        aria-label="Booking steps"
      >
        {STEPS.map((step, index) => {
          const isActive = step.number === currentStep;
          const isCompleted = completedSteps.includes(step.number);
          const clickable = isClickable(step.number);

          return (
            <div key={step.number} className="flex items-center">
              <button
                type="button"
                onClick={() => clickable && onStepClick(step.number)}
                disabled={!clickable}
                className={cn(
                  'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium shrink-0 transition-colors',
                  isActive && 'bg-accent text-white',
                  isCompleted && !isActive && 'bg-accent text-white',
                  !isActive && !isCompleted && 'border border-border bg-white text-muted',
                  clickable ? 'cursor-pointer' : 'cursor-default',
                )}
                aria-current={isActive ? 'step' : undefined}
                aria-label={`${step.number}. ${step.label}`}
              >
                {isCompleted && !isActive ? (
                  <Check className="size-4" />
                ) : (
                  step.number
                )}
              </button>
              {index < STEPS.length - 1 && (
                <div
                  className={cn(
                    'w-6 h-px mx-1',
                    step.number < currentStep ? 'bg-accent' : 'bg-border',
                  )}
                />
              )}
            </div>
          );
        })}
      </nav>
    </>
  );
}
