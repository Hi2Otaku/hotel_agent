import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
}

const statusConfig: Record<string, { className: string; label: string }> = {
  pending: {
    className: 'bg-[rgba(217,119,6,0.15)] text-[#D97706] border-[#D97706]/20',
    label: 'Pending',
  },
  confirmed: {
    className: 'bg-[rgba(15,118,110,0.15)] text-[#0F766E] border-[#0F766E]/20',
    label: 'Confirmed',
  },
  checked_in: {
    className: 'bg-[rgba(22,163,74,0.15)] text-[#16A34A] border-[#16A34A]/20',
    label: 'Checked In',
  },
  checked_out: {
    className: 'bg-[rgba(148,163,184,0.15)] text-[#94A3B8] border-[#94A3B8]/20',
    label: 'Checked Out',
  },
  cancelled: {
    className: 'bg-[rgba(220,38,38,0.15)] text-[#DC2626] border-[#DC2626]/20',
    label: 'Cancelled',
  },
  no_show: {
    className: 'bg-[rgba(220,38,38,0.15)] text-[#DC2626] border-[#DC2626]/20',
    label: 'No Show',
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] ?? {
    className: 'bg-[rgba(148,163,184,0.15)] text-[#94A3B8] border-[#94A3B8]/20',
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
