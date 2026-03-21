import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
}

const statusConfig: Record<string, { className: string; label: string }> = {
  confirmed: {
    className: 'bg-[#0F766E]/10 text-[#0F766E] border-[#0F766E]/20',
    label: 'Confirmed',
  },
  pending: {
    className: 'bg-amber-100 text-amber-700 border-amber-200',
    label: 'Pending',
  },
  cancelled: {
    className: 'bg-red-100 text-red-700 border-red-200',
    label: 'Cancelled',
  },
  checked_in: {
    className: 'bg-green-100 text-green-700 border-green-200',
    label: 'Checked In',
  },
  checked_out: {
    className: 'bg-slate-100 text-slate-500 border-slate-200',
    label: 'Checked Out',
  },
  no_show: {
    className: 'bg-red-100 text-red-700 border-red-200',
    label: 'No Show',
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] ?? {
    className: 'bg-slate-100 text-slate-500 border-slate-200',
    label: status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
  };

  return (
    <Badge
      variant="outline"
      className={cn('border text-xs font-medium', config.className)}
    >
      {config.label}
    </Badge>
  );
}
