import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatDateRange, calculateNights } from '@/lib/formatters';
import type { SearchResult, BookingResponse } from '@/api/types';

interface BookingSummaryPanelProps {
  room: SearchResult | null;
  checkIn: string | null;
  checkOut: string | null;
  guests: number;
  booking: BookingResponse | null;
}

export default function BookingSummaryPanel({
  room,
  checkIn,
  checkOut,
  guests,
  booking,
}: BookingSummaryPanelProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const roomName = booking?.room_type_name || room?.name;
  const photoUrl = booking?.room_type_photos?.[0] || room?.photo_url;
  const pricePerNight = booking?.price_per_night || room?.price_per_night;
  const totalPrice = booking?.total_price || room?.total_price;
  const nights = checkIn && checkOut ? calculateNights(checkIn, checkOut) : 0;
  const dateRange = checkIn && checkOut ? formatDateRange(checkIn, checkOut) : null;

  const summaryContent = (
    <div className="space-y-3">
      {photoUrl && (
        <img
          src={photoUrl}
          alt={roomName ? `${roomName} room` : 'Room photo'}
          className="w-full h-24 object-cover rounded-md"
        />
      )}
      {roomName && (
        <p className="text-lg font-semibold text-slate-900">{roomName}</p>
      )}
      {dateRange && (
        <div className="text-sm text-slate-600">{dateRange}</div>
      )}
      {nights > 0 && (
        <div className="text-sm text-slate-600">{nights} night{nights !== 1 ? 's' : ''}</div>
      )}
      <div className="text-sm text-slate-600">
        {guests} guest{guests !== 1 ? 's' : ''}
      </div>
      <Separator />
      {pricePerNight && nights > 0 && (
        <div className="text-sm text-slate-600">
          {formatCurrency(pricePerNight)} x {nights} night{nights !== 1 ? 's' : ''}
        </div>
      )}
      {totalPrice && (
        <div className="text-xl font-semibold text-[#0F766E]">
          {formatCurrency(totalPrice)}
        </div>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop panel */}
      <Card className="hidden md:block">
        <CardContent className="pt-4">
          <p className="text-sm font-medium text-slate-500 mb-3">Booking Summary</p>
          {summaryContent}
        </CardContent>
      </Card>

      {/* Mobile collapsible */}
      <div className="md:hidden border-b border-[#E2E8F0] bg-white">
        <Button
          variant="ghost"
          className="w-full flex items-center justify-between px-4 py-3 h-auto"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          <span className="text-sm font-medium text-slate-500">Booking Summary</span>
          <div className="flex items-center gap-2">
            {totalPrice && (
              <span className="text-sm font-semibold text-[#0F766E]">
                {formatCurrency(totalPrice)}
              </span>
            )}
            {mobileOpen ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
          </div>
        </Button>
        {mobileOpen && (
          <div className="px-4 pb-4">
            {summaryContent}
          </div>
        )}
      </div>
    </>
  );
}
