import { ChevronDown } from 'lucide-react';

interface ScrollToBottomProps {
  visible: boolean;
  onClick: () => void;
}

export function ScrollToBottom({ visible, onClick }: ScrollToBottomProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Scroll to latest messages"
      className={`absolute bottom-20 right-4 flex size-10 items-center justify-center rounded-full border bg-white shadow-md transition-opacity duration-200 ${
        visible ? 'opacity-100' : 'pointer-events-none opacity-0'
      }`}
    >
      <ChevronDown className="size-5 text-slate-600" />
    </button>
  );
}
