import { Inbox } from 'lucide-react';
import { Link } from 'react-router';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  heading: string;
  body: string;
  actionLabel?: string;
  actionHref?: string;
}

export function EmptyState({
  heading,
  body,
  actionLabel,
  actionHref,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Inbox className="mb-4 h-12 w-12 text-muted" />
      <h2 className="mb-2 text-2xl font-semibold text-slate-900">{heading}</h2>
      <p className="mb-6 max-w-md text-base text-muted">{body}</p>
      {actionLabel && actionHref && (
        <Link to={actionHref}>
          <Button className="bg-accent hover:bg-accent-hover">{actionLabel}</Button>
        </Link>
      )}
    </div>
  );
}
