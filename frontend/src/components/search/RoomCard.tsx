import { useNavigate } from 'react-router';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/formatters';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import type { SearchResult } from '@/api/types';

interface RoomCardProps {
  room: SearchResult;
  checkIn: string;
  checkOut: string;
  guests: number;
}

export function RoomCard({ room, checkIn, checkOut, guests }: RoomCardProps) {
  const navigate = useNavigate();
  const setSelectedRoom = useBookingWizardStore((s) => s.setSelectedRoom);
  const setSearchParams = useBookingWizardStore((s) => s.setSearchParams);

  function handleBookNow() {
    setSelectedRoom(room);
    setSearchParams(checkIn, checkOut, guests);
    navigate(
      `/book?roomTypeId=${room.room_type_id}&checkIn=${checkIn}&checkOut=${checkOut}&guests=${guests}`,
    );
  }

  return (
    <div className="group overflow-hidden rounded-lg bg-white shadow-[0_1px_3px_rgba(0,0,0,0.08)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(0,0,0,0.12)]">
      {/* Photo */}
      {room.photo_url ? (
        <img
          src={room.photo_url}
          alt={`${room.name} - ${room.amenity_highlights.slice(0, 2).join(', ')}`}
          className="aspect-video w-full object-cover"
        />
      ) : (
        <div className="aspect-video w-full bg-gradient-to-br from-teal-100 to-teal-300" />
      )}

      {/* Content */}
      <div className="flex flex-col gap-3 p-4">
        <h3 className="text-2xl font-semibold leading-tight">{room.name}</h3>

        <p className="text-lg font-semibold text-[#0F766E]">
          {formatCurrency(room.price_per_night)}{' '}
          <span className="text-sm font-normal text-[#64748B]">/ night</span>
        </p>

        {/* Amenity badges */}
        <div className="flex flex-wrap gap-1.5">
          {room.amenity_highlights.slice(0, 4).map((amenity) => (
            <Badge key={amenity} variant="outline" className="text-sm">
              {amenity}
            </Badge>
          ))}
        </div>

        {/* Availability */}
        <p className="text-sm text-[#64748B]">
          {room.available_count} {room.available_count === 1 ? 'room' : 'rooms'}{' '}
          left
        </p>

        {/* Book Now */}
        <Button
          onClick={handleBookNow}
          className="min-h-[44px] w-full bg-[#0F766E] text-white hover:bg-[#0D6660]"
        >
          Book Now
        </Button>
      </div>
    </div>
  );
}
