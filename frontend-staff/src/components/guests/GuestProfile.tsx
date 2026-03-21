import { useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import { toast } from 'sonner';
import { useGuestProfile } from '@/hooks/queries/useGuests';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface GuestProfileProps {
  userId: string;
}

export function GuestProfile({ userId }: GuestProfileProps) {
  const { data, isLoading, isError } = useGuestProfile(userId);

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong. Please try again.');
    }
  }, [isError]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48 bg-[#1E293B]" />
        <Skeleton className="h-5 w-64 bg-[#1E293B]" />
        <Skeleton className="h-5 w-40 bg-[#1E293B]" />
        <Skeleton className="mt-6 h-8 w-40 bg-[#1E293B]" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full bg-[#1E293B]" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const { user, bookings } = data;

  return (
    <div>
      {/* Guest info */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-[#F1F5F9]">
          {user.first_name} {user.last_name}
        </h2>
        <p className="mt-1 text-sm text-[#94A3B8]">{user.email}</p>
      </div>

      {/* Booking history */}
      <h3 className="mb-4 text-xl font-semibold text-[#F1F5F9]">
        Booking History
      </h3>

      {bookings.items.length === 0 ? (
        <p className="text-sm text-[#94A3B8]">No bookings found.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[#334155]">
          <Table>
            <TableHeader>
              <TableRow className="border-[#334155] bg-[#0F172A] hover:bg-[#0F172A]">
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Confirmation #
                </TableHead>
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Room Type
                </TableHead>
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Check-in
                </TableHead>
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Check-out
                </TableHead>
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Status
                </TableHead>
                <TableHead
                  scope="col"
                  className="text-xs uppercase text-[#94A3B8]"
                >
                  Total
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bookings.items.map((booking, idx) => (
                <TableRow
                  key={booking.id}
                  className={`border-[#334155] transition-colors hover:bg-[#283548] ${
                    idx % 2 === 0 ? 'bg-[#1E293B]' : 'bg-[#172033]'
                  }`}
                >
                  <TableCell className="px-3 py-2 font-mono text-sm text-[#94A3B8]">
                    {booking.confirmation_number}
                  </TableCell>
                  <TableCell className="px-3 py-2 text-sm text-[#F1F5F9]">
                    {booking.room_type_name ?? 'Room'}
                  </TableCell>
                  <TableCell className="px-3 py-2 text-sm text-[#F1F5F9]">
                    {format(parseISO(booking.check_in), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell className="px-3 py-2 text-sm text-[#F1F5F9]">
                    {format(parseISO(booking.check_out), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell className="px-3 py-2">
                    <StatusBadge status={booking.status} />
                  </TableCell>
                  <TableCell className="px-3 py-2 text-sm text-[#F1F5F9]">
                    {booking.total_price
                      ? `${booking.currency === 'USD' ? '$' : booking.currency}${booking.total_price}`
                      : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
