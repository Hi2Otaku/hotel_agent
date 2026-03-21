import type { LucideIcon } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface MetricCardProps {
  icon: LucideIcon;
  value: number | string;
  label: string;
  accentColor?: string;
  loading?: boolean;
}

export function MetricCard({
  icon: Icon,
  value,
  label,
  accentColor = '#0F766E',
  loading = false,
}: MetricCardProps) {
  if (loading) {
    return (
      <div className="rounded-lg border border-[#334155] bg-[#1E293B] p-4">
        <Skeleton className="mb-3 h-5 w-5 bg-[#1E293B]" />
        <Skeleton className="mb-2 h-8 w-16 bg-[#1E293B]" />
        <Skeleton className="h-3 w-24 bg-[#1E293B]" />
      </div>
    );
  }

  return (
    <div
      className="rounded-lg border border-[#334155] bg-[#1E293B] p-4"
      aria-label={`${label}: ${value}`}
    >
      <Icon className="mb-3 h-5 w-5" style={{ color: accentColor }} />
      <div className="text-[32px] font-semibold leading-tight text-[#F1F5F9]">
        {value}
      </div>
      <div className="mt-1 text-xs text-[#94A3B8]">{label}</div>
    </div>
  );
}
