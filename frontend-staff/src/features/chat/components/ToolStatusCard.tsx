import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import type { ToolStatusState } from '../types/chat';

interface ToolStatusCardProps {
  status: ToolStatusState;
}

export function ToolStatusCard({ status }: ToolStatusCardProps) {
  return (
    <div className="flex items-center gap-2 rounded-lg border bg-green-900/20 border-green-700/30 p-3 text-sm">
      {status.status === 'running' && (
        <Loader2 className="h-4 w-4 animate-spin text-green-400" />
      )}
      {status.status === 'success' && (
        <CheckCircle className="h-4 w-4 text-green-400" />
      )}
      {status.status === 'error' && (
        <XCircle className="h-4 w-4 text-red-400" />
      )}
      <span className="text-muted-foreground">{status.description}</span>
    </div>
  );
}
