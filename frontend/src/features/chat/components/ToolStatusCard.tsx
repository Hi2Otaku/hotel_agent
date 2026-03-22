import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import type { ToolStatusState } from '../types/chat';

interface ToolStatusCardProps {
  status: ToolStatusState;
}

export function ToolStatusCard({ status }: ToolStatusCardProps) {
  return (
    <div className="my-2 rounded-lg border border-[#BBF7D0] bg-[#F0FDF4] p-4">
      <div className="flex items-center gap-2">
        {status.status === 'running' && (
          <Loader2 className="size-4 animate-spin text-[#0F766E]" />
        )}
        {status.status === 'success' && (
          <CheckCircle className="size-4 text-green-600" />
        )}
        {status.status === 'error' && (
          <XCircle className="size-4 text-red-600" />
        )}
        <span className="text-sm text-slate-700">{status.description}</span>
      </div>
    </div>
  );
}
