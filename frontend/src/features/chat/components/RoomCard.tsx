import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { RoomCardData } from '../types/chat';

interface RoomCardProps {
  room: RoomCardData;
  onBook: (roomName: string) => void;
}

export function RoomCard({ room, onBook }: RoomCardProps) {
  return (
    <div className="my-2 rounded-lg border p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        {room.photo_url && (
          <img
            src={room.photo_url}
            alt={room.name}
            className="h-[60px] w-[80px] rounded-md object-cover"
          />
        )}
        <div className="flex flex-1 flex-col gap-1">
          <span className="font-semibold text-slate-900">{room.name}</span>
          <span className="text-sm font-semibold text-[#0F766E]">
            ${room.price_per_night}/night
          </span>
          <div className="flex flex-wrap gap-1">
            {room.amenities.slice(0, 3).map((amenity) => (
              <Badge key={amenity} variant="secondary" className="text-xs">
                {amenity}
              </Badge>
            ))}
          </div>
        </div>
        <Button
          size="sm"
          className="bg-[#0F766E] text-white hover:bg-[#0F766E]/90"
          onClick={() => onBook(room.name)}
        >
          Book this
        </Button>
      </div>
    </div>
  );
}
