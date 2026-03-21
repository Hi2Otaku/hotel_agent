import { format, parseISO } from 'date-fns';
import { Loader2 } from 'lucide-react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { useDrillDownBookings } from '@/hooks/queries/useReports';
import { DrillDownBookingRow } from './DrillDownBookingRow';

interface DrillDownPanelProps {
  selectedDay: string | null;
  onClose: () => void;
}

function formatDayLabel(day: string): string {
  try {
    return format(parseISO(day), 'MMMM d, yyyy');
  } catch {
    return day;
  }
}

export function DrillDownPanel({ selectedDay, onClose }: DrillDownPanelProps) {
  const { data, isLoading, isError } = useDrillDownBookings(selectedDay);

  return (
    <Sheet open={!!selectedDay} onOpenChange={(open) => !open && onClose()}>
      <SheetContent
        side="right"
        className="w-full sm:w-[400px] bg-[#1E293B] border-[#334155]"
      >
        <SheetHeader>
          <SheetTitle className="text-[#F1F5F9]">
            Bookings for {selectedDay ? formatDayLabel(selectedDay) : ''}
          </SheetTitle>
          <SheetDescription className="text-[#94A3B8]">
            Reservations active on this date
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-[#0F766E]" />
            </div>
          )}

          {isError && (
            <p className="py-8 text-center text-sm text-[#DC2626]">
              Failed to load booking details.
            </p>
          )}

          {!isLoading && !isError && data && data.length === 0 && (
            <p className="py-8 text-center text-sm text-[#94A3B8]">
              No bookings found for this date. Try selecting a different date on the chart.
            </p>
          )}

          {!isLoading && !isError && data && data.length > 0 && (
            <div>
              {data.map((booking) => (
                <DrillDownBookingRow key={booking.id} booking={booking} />
              ))}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
