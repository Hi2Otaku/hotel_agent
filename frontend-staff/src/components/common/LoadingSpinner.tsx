import { Loader2 } from 'lucide-react';

export function LoadingSpinner() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center">
      <Loader2 className="mb-3 h-10 w-10 animate-spin text-[#0F766E]" />
      <p className="text-sm text-[#94A3B8]">Loading...</p>
    </div>
  );
}
