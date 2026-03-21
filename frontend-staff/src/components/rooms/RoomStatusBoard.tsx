import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { RoomCard } from './RoomCard';
import type { RoomStatus } from '@/api/types';

interface Floor {
  floor: number;
  rooms: RoomStatus[];
}

interface RoomStatusBoardProps {
  floors: Floor[];
  onRoomClick?: (room: RoomStatus) => void;
}

export function RoomStatusBoard({ floors, onRoomClick }: RoomStatusBoardProps) {
  const [collapsed, setCollapsed] = useState<Record<number, boolean>>({});

  const toggleFloor = (floor: number) => {
    setCollapsed((prev) => ({ ...prev, [floor]: !prev[floor] }));
  };

  return (
    <div className="space-y-4">
      {floors.map(({ floor, rooms }) => {
        const isCollapsed = collapsed[floor] ?? false;

        return (
          <div key={floor}>
            <button
              type="button"
              onClick={() => toggleFloor(floor)}
              className="mb-2 flex w-full items-center gap-2 text-left text-sm font-semibold text-[#F1F5F9] hover:text-[#CBD5E1]"
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
              Floor {floor}
            </button>

            {!isCollapsed && (
              <div className="flex flex-wrap gap-2">
                {rooms.map((room) => (
                  <RoomCard
                    key={room.id}
                    room={room}
                    onClick={onRoomClick}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
