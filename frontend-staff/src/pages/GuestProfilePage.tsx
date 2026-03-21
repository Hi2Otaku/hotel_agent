import { useState } from 'react';
import { GuestSearch } from '@/components/guests/GuestSearch';
import { GuestProfile } from '@/components/guests/GuestProfile';

export default function GuestProfilePage() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      {/* Search sidebar */}
      <div className="w-full shrink-0 lg:w-80">
        <GuestSearch onSelect={setSelectedUserId} />
      </div>

      {/* Profile area */}
      <div className="min-w-0 flex-1">
        {selectedUserId ? (
          <GuestProfile userId={selectedUserId} />
        ) : (
          <div className="flex items-center justify-center py-16 text-sm text-[#94A3B8]">
            Select a guest to view their profile
          </div>
        )}
      </div>
    </div>
  );
}
