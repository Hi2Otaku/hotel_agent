import { useState } from 'react';
import { SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';

export interface FilterState {
  minPrice?: number;
  maxPrice?: number;
  amenities: string[];
  sort: string;
}

interface FilterDrawerProps {
  onFilter: (filters: FilterState) => void;
}

const AMENITY_OPTIONS = [
  'WiFi',
  'Pool',
  'Ocean View',
  'Balcony',
  'Kitchen',
  'AC',
];

function FilterControls({
  filters,
  setFilters,
  onApply,
  onClear,
}: {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  onApply: () => void;
  onClear: () => void;
}) {
  function toggleAmenity(amenity: string) {
    setFilters((prev) => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter((a) => a !== amenity)
        : [...prev.amenities, amenity],
    }));
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Price range */}
      <div>
        <h4 className="mb-2 text-sm font-semibold">Price Range</h4>
        <div className="flex items-center gap-2">
          <Input
            type="number"
            placeholder="Min"
            value={filters.minPrice ?? ''}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                minPrice: e.target.value ? Number(e.target.value) : undefined,
              }))
            }
            className="w-full"
          />
          <span className="text-sm text-[#64748B]">to</span>
          <Input
            type="number"
            placeholder="Max"
            value={filters.maxPrice ?? ''}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                maxPrice: e.target.value ? Number(e.target.value) : undefined,
              }))
            }
            className="w-full"
          />
        </div>
      </div>

      {/* Amenities */}
      <div>
        <h4 className="mb-2 text-sm font-semibold">Amenities</h4>
        <div className="flex flex-col gap-2">
          {AMENITY_OPTIONS.map((amenity) => (
            <label key={amenity} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={filters.amenities.includes(amenity)}
                onChange={() => toggleAmenity(amenity)}
                className="size-4 rounded border-slate-300"
              />
              {amenity}
            </label>
          ))}
        </div>
      </div>

      {/* Sort */}
      <div>
        <h4 className="mb-2 text-sm font-semibold">Sort</h4>
        <Select
          value={filters.sort}
          onValueChange={(val) =>
            setFilters((prev) => ({ ...prev, sort: val }))
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="recommended">Recommended</SelectItem>
            <SelectItem value="price_asc">Price: Low to High</SelectItem>
            <SelectItem value="price_desc">Price: High to Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          onClick={onApply}
          className="flex-1 bg-[#0F766E] text-white hover:bg-[#0D6660]"
        >
          Apply
        </Button>
        <Button onClick={onClear} variant="outline" className="flex-1">
          Clear
        </Button>
      </div>
    </div>
  );
}

const DEFAULT_FILTERS: FilterState = {
  amenities: [],
  sort: 'recommended',
};

export function FilterDrawer({ onFilter }: FilterDrawerProps) {
  const [filters, setFilters] = useState<FilterState>({ ...DEFAULT_FILTERS });

  function handleApply() {
    onFilter(filters);
  }

  function handleClear() {
    const cleared = { ...DEFAULT_FILTERS };
    setFilters(cleared);
    onFilter(cleared);
  }

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 lg:block">
        <h3 className="mb-4 text-lg font-semibold">Filters</h3>
        <FilterControls
          filters={filters}
          setFilters={setFilters}
          onApply={handleApply}
          onClear={handleClear}
        />
      </aside>

      {/* Mobile sheet */}
      <div className="lg:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" aria-label="Open filters">
              <SlidersHorizontal className="size-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right">
            <SheetHeader>
              <SheetTitle>Filters</SheetTitle>
            </SheetHeader>
            <div className="p-4">
              <FilterControls
                filters={filters}
                setFilters={setFilters}
                onApply={handleApply}
                onClear={handleClear}
              />
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}
