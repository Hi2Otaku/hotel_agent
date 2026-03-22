import { useParams, useSearchParams, useNavigate } from 'react-router';
import { useRoomTypeDetail } from '@/hooks/queries/useSearch';
import { PhotoCarousel } from '@/components/common/PhotoCarousel';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { formatCurrency, calculateNights } from '@/lib/formatters';
import { useBookingWizardStore } from '@/stores/bookingWizardStore';
import type { RoomTypeDetail as RoomTypeDetailType } from '@/api/types';

function RoomDetailSkeleton() {
  return (
    <div>
      <Skeleton className="h-80 w-full bg-slate-200" />
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-8 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Skeleton className="h-8 w-2/3 bg-slate-200" />
          <Skeleton className="h-4 w-full bg-slate-200" />
          <Skeleton className="h-4 w-5/6 bg-slate-200" />
          <Skeleton className="h-4 w-3/4 bg-slate-200" />
        </div>
        <div>
          <Skeleton className="h-48 w-full rounded-lg bg-slate-200" />
        </div>
      </div>
    </div>
  );
}

function PriceCard({
  room,
  checkIn,
  checkOut,
  guests,
}: {
  room: RoomTypeDetailType;
  checkIn: string;
  checkOut: string;
  guests: number;
}) {
  const navigate = useNavigate();
  const setSelectedRoom = useBookingWizardStore((s) => s.setSelectedRoom);
  const setSearchParams = useBookingWizardStore((s) => s.setSearchParams);
  const nights = calculateNights(checkIn, checkOut);

  function handleBookNow() {
    setSelectedRoom({
      room_type_id: room.id,
      name: room.name,
      slug: room.slug,
      description: room.description,
      photo_url: room.photo_urls[0] ?? null,
      price_per_night: room.price_per_night,
      total_price: room.total_price,
      currency: room.currency,
      max_adults: room.max_adults,
      max_children: room.max_children,
      bed_config: room.bed_config,
      amenity_highlights: Object.values(room.amenities).flat().slice(0, 4),
      available_count: room.available_count,
      total_rooms: room.total_rooms,
    });
    setSearchParams(checkIn, checkOut, guests);
    navigate(
      `/book?roomTypeId=${room.id}&checkIn=${checkIn}&checkOut=${checkOut}&guests=${guests}`,
    );
  }

  return (
    <div className="rounded-lg border border-border bg-white p-6 shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
      <p className="text-2xl font-semibold text-accent">
        {formatCurrency(room.total_price)}
      </p>
      <p className="mb-4 text-sm text-muted">
        {nights} {nights === 1 ? 'night' : 'nights'} at{' '}
        {formatCurrency(room.price_per_night)}/night
      </p>

      {/* Nightly rate breakdown */}
      {room.nightly_rates.length > 0 && (
        <div className="mb-4">
          <h4 className="mb-2 text-sm font-semibold">Rate Breakdown</h4>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-muted">
                <th className="pb-1">Date</th>
                <th className="pb-1 text-right">Rate</th>
              </tr>
            </thead>
            <tbody>
              {room.nightly_rates.map((rate) => (
                <tr key={rate.date} className="border-b border-slate-100">
                  <td className="py-1">{rate.date}</td>
                  <td className="py-1 text-right">
                    {formatCurrency(rate.final_amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Button
        onClick={handleBookNow}
        className="min-h-[44px] w-full bg-accent text-white hover:bg-accent-hover"
      >
        Book Now
      </Button>
    </div>
  );
}

export default function RoomDetail() {
  const { roomTypeId } = useParams();
  const [searchParams] = useSearchParams();
  const checkIn = searchParams.get('checkIn') ?? '';
  const checkOut = searchParams.get('checkOut') ?? '';
  const guests = Number(searchParams.get('guests') ?? 2);

  const { data: room, isLoading } = useRoomTypeDetail(
    roomTypeId,
    checkIn,
    checkOut,
    guests,
  );

  if (isLoading || !room) {
    return <RoomDetailSkeleton />;
  }

  return (
    <div>
      {/* Photo carousel */}
      <div className="mx-auto max-h-[400px] overflow-hidden">
        <PhotoCarousel photos={room.photo_urls} altPrefix={room.name} />
      </div>

      {/* Content */}
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-8 md:px-8 lg:grid-cols-3">
        {/* Left content */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          <h1 className="text-2xl font-semibold">{room.name}</h1>
          <p className="text-base text-slate-700">{room.description}</p>

          {/* Capacity */}
          <p className="text-sm text-muted">
            Up to {room.max_adults} adults, {room.max_children} children
          </p>

          {/* Bed configuration */}
          <div>
            <h3 className="mb-2 text-lg font-semibold">Bed Configuration</h3>
            <div className="flex flex-wrap gap-2">
              {room.bed_config.map((bed, idx) => (
                <Badge key={idx} variant="outline">
                  {bed.count}x {bed.type}
                </Badge>
              ))}
            </div>
          </div>

          {/* Amenities grouped by category */}
          <div>
            <h3 className="mb-3 text-lg font-semibold">Amenities</h3>
            <div className="grid gap-4 sm:grid-cols-2">
              {Object.entries(room.amenities).map(([category, items]) => (
                <div key={category}>
                  <h4 className="mb-1 text-sm font-semibold capitalize">
                    {category}
                  </h4>
                  <ul className="list-inside list-disc text-sm text-slate-600">
                    {items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right sidebar - price card (sticky on desktop) */}
        <div className="lg:sticky lg:top-24">
          <PriceCard
            room={room}
            checkIn={checkIn}
            checkOut={checkOut}
            guests={guests}
          />
        </div>
      </div>

      {/* Mobile sticky Book Now footer */}
      <div className="fixed inset-x-0 bottom-0 border-t border-border bg-white p-4 shadow-lg lg:hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-lg font-semibold text-accent">
              {formatCurrency(room.total_price)}
            </p>
            <p className="text-xs text-muted">
              {calculateNights(checkIn, checkOut)} nights
            </p>
          </div>
          <Button
            onClick={() => {
              const setSelectedRoom = useBookingWizardStore.getState().setSelectedRoom;
              const setSearchParamsStore = useBookingWizardStore.getState().setSearchParams;
              setSelectedRoom({
                room_type_id: room.id,
                name: room.name,
                slug: room.slug,
                description: room.description,
                photo_url: room.photo_urls[0] ?? null,
                price_per_night: room.price_per_night,
                total_price: room.total_price,
                currency: room.currency,
                max_adults: room.max_adults,
                max_children: room.max_children,
                bed_config: room.bed_config,
                amenity_highlights: Object.values(room.amenities).flat().slice(0, 4),
                available_count: room.available_count,
                total_rooms: room.total_rooms,
              });
              setSearchParamsStore(checkIn, checkOut, guests);
              window.location.href = `/book?roomTypeId=${room.id}&checkIn=${checkIn}&checkOut=${checkOut}&guests=${guests}`;
            }}
            className="min-h-[44px] bg-accent text-white hover:bg-accent-hover"
          >
            Book Now
          </Button>
        </div>
      </div>
    </div>
  );
}
