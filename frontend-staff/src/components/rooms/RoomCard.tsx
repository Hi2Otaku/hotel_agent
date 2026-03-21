import type { RoomStatus } from '@/api/types';

interface RoomCardProps {
  room: RoomStatus;
  onClick?: (room: RoomStatus) => void;
}

const statusColors: Record<string, { dot: string; label: string }> = {
  available: { dot: '#16A34A', label: 'Available' },
  occupied: { dot: '#0F766E', label: 'Occupied' },
  cleaning: { dot: '#D97706', label: 'Cleaning' },
  maintenance: { dot: '#DC2626', label: 'Maintenance' },
  inspected: { dot: '#3B82F6', label: 'Inspected' },
};

export function RoomCard({ room, onClick }: RoomCardProps) {
  const config = statusColors[room.status] ?? {
    dot: '#94A3B8',
    label: room.status.charAt(0).toUpperCase() + room.status.slice(1),
  };

  return (
    <button
      type="button"
      onClick={() => onClick?.(room)}
      aria-label={`Room ${room.room_number}, ${config.label}, ${room.room_type_name ?? 'Room'}`}
      className="flex h-20 w-[120px] cursor-pointer flex-col items-center justify-center rounded-lg border border-[#334155] bg-[#1E293B] p-2 transition-colors duration-150 hover:bg-[#283548]"
    >
      <span className="text-sm font-semibold text-[#F1F5F9]">
        {room.room_number}
      </span>
      <div className="mt-1 flex items-center gap-1.5">
        <span
          className="inline-block h-2 w-2 rounded-full"
          style={{ backgroundColor: config.dot }}
        />
        <span className="text-xs text-[#94A3B8]">{config.label}</span>
      </div>
      {room.room_type_name && (
        <span className="mt-0.5 max-w-full truncate text-xs text-[#94A3B8]">
          {room.room_type_name}
        </span>
      )}
    </button>
  );
}
