import { useMemo } from 'react';
import { useNavigate } from 'react-router';
import { format, addDays, parseISO } from 'date-fns';
import { usePricingCalendar } from '@/hooks/queries/useSearch';
import { Skeleton } from '@/components/ui/skeleton';
import { formatCurrency } from '@/lib/formatters';
import type { CalendarDay } from '@/api/types';

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const INDICATOR_STYLES: Record<
  CalendarDay['availability_indicator'],
  string
> = {
  green: 'bg-green-50 border-green-200 hover:bg-green-100',
  yellow: 'bg-amber-50 border-amber-200 hover:bg-amber-100',
  red: 'bg-red-50 border-red-200 hover:bg-red-100',
};

interface MonthGroup {
  label: string;
  days: (CalendarDay | null)[];
}

function groupByMonth(days: CalendarDay[]): MonthGroup[] {
  const months = new Map<string, CalendarDay[]>();

  for (const day of days) {
    const date = parseISO(day.date);
    const key = format(date, 'yyyy-MM');
    if (!months.has(key)) {
      months.set(key, []);
    }
    months.get(key)!.push(day);
  }

  const result: MonthGroup[] = [];
  for (const [, monthDays] of months) {
    if (monthDays.length === 0) continue;
    const firstDate = parseISO(monthDays[0].date);
    const label = format(firstDate, 'MMMM yyyy');

    // Pad start with nulls for alignment
    const startDow = firstDate.getDay();
    const padded: (CalendarDay | null)[] = Array(startDow).fill(null);
    padded.push(...monthDays);

    result.push({ label, days: padded });
  }

  return result;
}

function CalendarSkeleton() {
  return (
    <div className="grid grid-cols-7 gap-1">
      {Array.from({ length: 35 }).map((_, i) => (
        <Skeleton key={i} className="h-16 w-full bg-slate-200" />
      ))}
    </div>
  );
}

export default function PricingCalendar() {
  const navigate = useNavigate();
  const { data, isLoading } = usePricingCalendar(undefined, undefined, 3);

  const months = useMemo(() => {
    if (!data?.days) return [];
    return groupByMonth(data.days);
  }, [data]);

  function handleDayClick(day: CalendarDay) {
    const nextDay = format(addDays(parseISO(day.date), 1), 'yyyy-MM-dd');
    navigate(`/search?checkIn=${day.date}&checkOut=${nextDay}&guests=2`);
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 md:px-8">
      <h1 className="mb-2 text-2xl font-semibold">Pricing Calendar</h1>
      <p className="mb-6 text-base text-[#64748B]">
        View rates and availability. Click a date to search.
      </p>

      {isLoading && <CalendarSkeleton />}

      {!isLoading && months.length > 0 && (
        <div className="flex flex-col gap-10">
          {months.map((month) => (
            <div key={month.label}>
              <h2 className="mb-3 text-lg font-semibold">{month.label}</h2>

              {/* Weekday headers */}
              <div className="mb-1 grid grid-cols-7 gap-1">
                {WEEKDAYS.map((wd) => (
                  <div
                    key={wd}
                    className="py-1 text-center text-xs font-medium text-[#64748B]"
                  >
                    {wd}
                  </div>
                ))}
              </div>

              {/* Day cells */}
              <div className="grid grid-cols-7 gap-1">
                {month.days.map((day, idx) => {
                  if (!day) {
                    return <div key={`empty-${idx}`} />;
                  }

                  const date = parseISO(day.date);
                  const indicatorClass =
                    INDICATOR_STYLES[day.availability_indicator];

                  return (
                    <button
                      key={day.date}
                      onClick={() => handleDayClick(day)}
                      className={`flex min-h-[44px] flex-col items-center justify-center rounded border p-1 transition-colors ${indicatorClass}`}
                    >
                      <span className="hidden text-xs sm:block">
                        {format(date, 'd')}
                      </span>
                      <span className="text-xs font-medium sm:text-sm">
                        {formatCurrency(day.rate)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Legend */}
          <div className="flex flex-wrap items-center gap-4 border-t border-[#E2E8F0] pt-4">
            <div className="flex items-center gap-1.5">
              <span className="inline-block size-3 rounded-full bg-green-400" />
              <span className="text-sm text-[#64748B]">Available</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block size-3 rounded-full bg-amber-400" />
              <span className="text-sm text-[#64748B]">Limited</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block size-3 rounded-full bg-red-400" />
              <span className="text-sm text-[#64748B]">Almost Full</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
