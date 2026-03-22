import { useState, useMemo } from 'react';
import { subDays, startOfMonth, startOfYear, format, parseISO } from 'date-fns';
import { CalendarIcon } from 'lucide-react';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import type { DateRange } from '@/api/types';

interface DateRangePickerProps {
  dateRange: DateRange;
  onChange: (range: DateRange) => void;
}

type PresetKey = '7d' | '30d' | '90d' | 'month' | 'year';

interface Preset {
  key: PresetKey;
  label: string;
  getRange: () => { from: Date; to: Date };
}

const today = () => new Date();

const presets: Preset[] = [
  { key: '7d', label: '7 days', getRange: () => ({ from: subDays(today(), 7), to: today() }) },
  { key: '30d', label: '30 days', getRange: () => ({ from: subDays(today(), 30), to: today() }) },
  { key: '90d', label: '90 days', getRange: () => ({ from: subDays(today(), 90), to: today() }) },
  { key: 'month', label: 'This Month', getRange: () => ({ from: startOfMonth(today()), to: today() }) },
  { key: 'year', label: 'This Year', getRange: () => ({ from: startOfYear(today()), to: today() }) },
];

function formatDate(d: Date): string {
  return format(d, 'yyyy-MM-dd');
}

export function DateRangePicker({ dateRange, onChange }: DateRangePickerProps) {
  const [customOpen, setCustomOpen] = useState(false);

  const activePreset = useMemo(() => {
    for (const p of presets) {
      const r = p.getRange();
      if (formatDate(r.from) === dateRange.from && formatDate(r.to) === dateRange.to) {
        return p.key;
      }
    }
    return '';
  }, [dateRange]);

  function handlePreset(value: string) {
    if (!value) return;
    const preset = presets.find((p) => p.key === value);
    if (preset) {
      const range = preset.getRange();
      onChange({ from: formatDate(range.from), to: formatDate(range.to) });
    }
  }

  function handleCustomRange(range: { from?: Date; to?: Date } | undefined) {
    if (range?.from && range?.to) {
      onChange({ from: formatDate(range.from), to: formatDate(range.to) });
      setCustomOpen(false);
    }
  }

  const calendarSelected = useMemo(() => {
    try {
      return {
        from: parseISO(dateRange.from),
        to: parseISO(dateRange.to),
      };
    } catch {
      return undefined;
    }
  }, [dateRange]);

  const displayLabel = useMemo(() => {
    const preset = presets.find((p) => p.key === activePreset);
    if (preset) {
      return `Last ${preset.label}`;
    }
    return `${dateRange.from} - ${dateRange.to}`;
  }, [activePreset, dateRange]);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <ToggleGroup
        type="single"
        value={activePreset}
        onValueChange={handlePreset}
        className="flex-wrap"
      >
        {presets.map((p) => (
          <ToggleGroupItem
            key={p.key}
            value={p.key}
            className={
              activePreset === p.key
                ? 'bg-[rgba(15,118,110,0.15)] text-[#0F766E] data-[state=on]:bg-[rgba(15,118,110,0.15)] data-[state=on]:text-[#0F766E]'
                : 'text-[#94A3B8]'
            }
            size="sm"
          >
            {p.label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>

      <Popover open={customOpen} onOpenChange={setCustomOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="border-[#334155] text-[#94A3B8] hover:text-[#F1F5F9]"
          >
            <CalendarIcon className="mr-1 h-4 w-4" />
            {!activePreset ? displayLabel : 'Custom'}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto bg-[#1E293B] border-[#334155] p-0" align="start">
          <Calendar
            mode="range"
            selected={calendarSelected}
            onSelect={handleCustomRange}
            numberOfMonths={2}
            disabled={{ after: today() }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
