import { useEffect } from 'react';
import { CalendarCheck, LogOut, BedDouble, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import { useTodayOverview } from '@/hooks/queries/useStaffBookings';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { ArrivalsList } from '@/components/dashboard/ArrivalsList';
import { DeparturesList } from '@/components/dashboard/DeparturesList';
import { Skeleton } from '@/components/ui/skeleton';

export default function OverviewPage() {
  const { data, isLoading, isError } = useTodayOverview();

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong. Please try again.');
    }
  }, [isError]);

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <MetricCard
              key={i}
              icon={CalendarCheck}
              value={0}
              label=""
              loading
            />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <Skeleton className="mb-4 h-6 w-40 bg-[#1E293B]" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="mb-2 h-16 w-full bg-[#1E293B]" />
            ))}
          </div>
          <div>
            <Skeleton className="mb-4 h-6 w-44 bg-[#1E293B]" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="mb-2 h-16 w-full bg-[#1E293B]" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={CalendarCheck}
          value={data.arrivals_count}
          label="Today's Check-ins"
        />
        <MetricCard
          icon={LogOut}
          value={data.departures_count}
          label="Today's Check-outs"
        />
        <MetricCard
          icon={BedDouble}
          value={`${data.occupancy_percent}%`}
          label="Occupancy"
        />
        <MetricCard
          icon={Sparkles}
          value={data.rooms_to_clean}
          label="Rooms to Clean"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <ArrivalsList arrivals={data.arrivals} />
        <DeparturesList departures={data.departures} />
      </div>
    </div>
  );
}
