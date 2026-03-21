import { useState, useMemo } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { useCheckIn } from '@/hooks/queries/useStaffBookings';
import { useAvailableRooms } from '@/hooks/queries/useRooms';
import type { BookingResponse } from '@/api/types';

interface CheckInDialogProps {
  booking: BookingResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CheckInDialog({
  booking,
  open,
  onOpenChange,
  onSuccess,
}: CheckInDialogProps) {
  const [showRoomSelect, setShowRoomSelect] = useState(false);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);

  const { data: availableRooms, isLoading: roomsLoading } = useAvailableRooms(
    open ? booking.room_type_id : null,
  );

  const checkIn = useCheckIn();

  const sortedRooms = useMemo(() => {
    if (!availableRooms) return [];
    return [...availableRooms].sort((a, b) => {
      if (a.floor !== b.floor) return a.floor - b.floor;
      return a.room_number.localeCompare(b.room_number, undefined, {
        numeric: true,
      });
    });
  }, [availableRooms]);

  const autoAssignedRoom = sortedRooms[0] ?? null;

  const selectedRoom = selectedRoomId
    ? sortedRooms.find((r) => r.id === selectedRoomId) ?? autoAssignedRoom
    : autoAssignedRoom;

  const guestName = `${booking.guest_first_name} ${booking.guest_last_name}`;

  const handleConfirm = async () => {
    if (!selectedRoom) return;
    try {
      await checkIn.mutateAsync({
        bookingId: booking.id,
        roomId: selectedRoom.id,
      });
      toast.success(
        `${guestName} checked in to Room ${selectedRoom.room_number}`,
      );
      onOpenChange(false);
      setShowRoomSelect(false);
      setSelectedRoomId(null);
      onSuccess?.();
    } catch {
      toast.error('Something went wrong. Please try again.');
    }
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setShowRoomSelect(false);
      setSelectedRoomId(null);
    }
    onOpenChange(nextOpen);
  };

  const noRoomsAvailable =
    !roomsLoading && sortedRooms.length === 0 && open;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="border-[#334155] bg-[#1E293B] text-[#F1F5F9]">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-[#F1F5F9]">
            Check in {guestName}
          </DialogTitle>
          <DialogDescription className="text-sm text-[#94A3B8]">
            {booking.room_type_name ?? 'Room'} &middot;{' '}
            <span className="font-mono">{booking.confirmation_number}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {roomsLoading && (
            <div className="flex items-center gap-2 text-sm text-[#94A3B8]">
              <Loader2 className="h-4 w-4 animate-spin" />
              Finding available rooms...
            </div>
          )}

          {noRoomsAvailable && (
            <p className="text-sm text-[#DC2626]">
              No available rooms of this type. Please assign manually or change
              room type.
            </p>
          )}

          {selectedRoom && !showRoomSelect && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-[#F1F5F9]">
                Room {selectedRoom.room_number} ({selectedRoom.floor}F)
              </span>
              <button
                type="button"
                onClick={() => setShowRoomSelect(true)}
                className="text-sm text-[#0F766E] hover:text-[#0D9488] hover:underline"
              >
                Change
              </button>
            </div>
          )}

          {showRoomSelect && sortedRooms.length > 0 && (
            <Select
              value={selectedRoom?.id ?? ''}
              onValueChange={(value) => setSelectedRoomId(value)}
            >
              <SelectTrigger className="w-full border-[#334155] bg-[#1E293B] text-[#F1F5F9]">
                <SelectValue placeholder="Select a room" />
              </SelectTrigger>
              <SelectContent className="border-[#334155] bg-[#1E293B]">
                {sortedRooms.map((room) => (
                  <SelectItem
                    key={room.id}
                    value={room.id}
                    className="text-[#F1F5F9] focus:bg-[#283548] focus:text-[#F1F5F9]"
                  >
                    Room {room.room_number} ({room.floor}F)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            className="border-[#334155] text-[#CBD5E1] hover:bg-[#283548]"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selectedRoom || checkIn.isPending}
            className="bg-[#0F766E] text-white hover:bg-[#0D9488] disabled:opacity-30"
          >
            {checkIn.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              `Check In to Room ${selectedRoom?.room_number ?? '...'}`
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
