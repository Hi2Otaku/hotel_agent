import { Bed, Users, MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface RoomResult {
  name: string;
  photo_url?: string;
  price_per_night: string;
  total_price?: string;
  description?: string;
  available_count?: number;
  max_adults?: number;
  bed_config?: Array<{ type: string; count: number }>;
  amenity_highlights?: string[];
}

interface RoomCardProps {
  room: RoomResult;
  onBook: (roomName: string) => void;
}

function formatBedConfig(beds: Array<{ type: string; count: number }>): string {
  return beds
    .map((b) => `${b.count} ${b.type}${b.count > 1 ? 's' : ''}`)
    .join(', ');
}

export function RoomCard({ room, onBook }: RoomCardProps) {
  return (
    <div className="my-2 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      <div className="flex flex-col sm:flex-row">
        {/* Photo */}
        {room.photo_url && (
          <div className="h-[140px] w-full shrink-0 sm:h-auto sm:w-[180px]">
            <img
              src={room.photo_url}
              alt={room.name}
              className="size-full object-cover"
            />
          </div>
        )}

        {/* Content */}
        <div className="flex flex-1 flex-col justify-between p-4">
          <div>
            <h4 className="text-base font-semibold text-slate-900">
              {room.name}
            </h4>
            {room.description && (
              <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                {room.description}
              </p>
            )}

            {/* Details row */}
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-600">
              {room.bed_config && room.bed_config.length > 0 && (
                <span className="flex items-center gap-1">
                  <Bed className="size-3.5" />
                  {formatBedConfig(room.bed_config)}
                </span>
              )}
              {room.max_adults && (
                <span className="flex items-center gap-1">
                  <Users className="size-3.5" />
                  Up to {room.max_adults} guests
                </span>
              )}
              {room.available_count !== undefined && (
                <span className="flex items-center gap-1">
                  <MapPin className="size-3.5" />
                  {room.available_count} available
                </span>
              )}
            </div>

            {/* Amenities */}
            {room.amenity_highlights && room.amenity_highlights.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {room.amenity_highlights.map((a) => (
                  <Badge
                    key={a}
                    variant="secondary"
                    className="rounded-full px-2 py-0.5 text-[10px] font-normal"
                  >
                    {a}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Price + Book */}
          <div className="mt-3 flex items-end justify-between">
            <div>
              <span className="text-lg font-bold text-[#0F766E]">
                ${room.price_per_night}
              </span>
              <span className="text-xs text-slate-500">/night</span>
              {room.total_price && (
                <p className="text-[11px] text-slate-400">
                  ${room.total_price} total
                </p>
              )}
            </div>
            <Button
              size="sm"
              className="bg-[#0F766E] text-white hover:bg-[#0D6660]"
              onClick={() => onBook(room.name)}
            >
              Book this
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
