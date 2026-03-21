import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  useRoomStatusBoard,
  useTransitionRoomStatus,
} from '@/hooks/queries/useRooms';
import { RoomStatusBoard } from '@/components/rooms/RoomStatusBoard';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import type { RoomStatus } from '@/api/types';

const STATUS_ACTIONS: Record<string, string[]> = {
  available: ['occupied', 'maintenance'],
  occupied: ['cleaning', 'available'],
  cleaning: ['inspected', 'available', 'maintenance'],
  inspected: ['available'],
  maintenance: ['available'],
};

const STATUS_LABELS: Record<string, string> = {
  available: 'Mark Available',
  occupied: 'Mark Occupied',
  cleaning: 'Mark Cleaning',
  inspected: 'Mark Inspected',
  maintenance: 'Mark Maintenance',
};

export default function RoomStatusPage() {
  const { data, isLoading, isError } = useRoomStatusBoard();
  const transitionMutation = useTransitionRoomStatus();
  const [selectedRoom, setSelectedRoom] = useState<RoomStatus | null>(null);
  const [popoverOpen, setPopoverOpen] = useState(false);

  useEffect(() => {
    if (isError) {
      toast.error('Something went wrong. Please try again.');
    }
  }, [isError]);

  const handleStatusChange = async (roomId: string, newStatus: string) => {
    try {
      await transitionMutation.mutateAsync({ roomId, newStatus });
      toast.success(`Room status updated to ${STATUS_LABELS[newStatus]?.replace('Mark ', '') ?? newStatus}`);
      setPopoverOpen(false);
      setSelectedRoom(null);
    } catch {
      toast.error('Something went wrong. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-wrap gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-32 rounded-lg bg-[#1E293B]" />
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton
              key={i}
              className="h-20 w-[120px] rounded-lg bg-[#1E293B]"
            />
          ))}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { summary, floors } = data;

  const summaryItems = [
    { label: 'Total', value: summary.total, color: '#F1F5F9' },
    { label: 'Available', value: summary.available, color: '#16A34A' },
    { label: 'Occupied', value: summary.occupied, color: '#0F766E' },
    { label: 'Cleaning', value: summary.cleaning, color: '#D97706' },
    { label: 'Maintenance', value: summary.maintenance, color: '#DC2626' },
  ];

  const validActions = selectedRoom
    ? STATUS_ACTIONS[selectedRoom.status] ?? []
    : [];

  return (
    <div className="space-y-6">
      {/* Summary row */}
      <div className="flex flex-wrap gap-4">
        {summaryItems.map((item) => (
          <div
            key={item.label}
            className="rounded-lg border border-[#334155] bg-[#1E293B] px-5 py-3"
          >
            <div
              className="text-xl font-semibold"
              style={{ color: item.color }}
            >
              {item.value}
            </div>
            <div className="text-xs text-[#94A3B8]">{item.label}</div>
          </div>
        ))}
      </div>

      {/* Room board with popover trigger */}
      <Popover open={popoverOpen} onOpenChange={setPopoverOpen}>
        <PopoverTrigger asChild>
          <div>
            <RoomStatusBoard
              floors={floors}
              onRoomClick={(room) => {
                setSelectedRoom(room);
                setPopoverOpen(true);
              }}
            />
          </div>
        </PopoverTrigger>

        {selectedRoom && (
          <PopoverContent
            className="w-64 border-[#334155] bg-[#1E293B] p-4"
            side="right"
            align="start"
          >
            <div className="space-y-3">
              <div>
                <div className="text-sm font-semibold text-[#F1F5F9]">
                  Room {selectedRoom.room_number}
                </div>
                <div className="text-xs text-[#94A3B8]">
                  {selectedRoom.room_type_name ?? 'Room'} &middot;{' '}
                  {selectedRoom.status.charAt(0).toUpperCase() +
                    selectedRoom.status.slice(1)}
                </div>
              </div>

              {validActions.length > 0 && (
                <div className="space-y-1.5">
                  {validActions.map((action) => (
                    <Button
                      key={action}
                      size="sm"
                      variant="outline"
                      className="w-full justify-start border-[#334155] text-[#CBD5E1] hover:bg-[#283548]"
                      disabled={transitionMutation.isPending}
                      onClick={() =>
                        handleStatusChange(selectedRoom.id, action)
                      }
                    >
                      {STATUS_LABELS[action] ?? action}
                    </Button>
                  ))}
                </div>
              )}
            </div>
          </PopoverContent>
        )}
      </Popover>
    </div>
  );
}
