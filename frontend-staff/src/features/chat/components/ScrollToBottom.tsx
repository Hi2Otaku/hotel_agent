import { ChevronDown } from 'lucide-react';

interface ScrollToBottomProps {
  visible: boolean;
  onClick: () => void;
}

export function ScrollToBottom({ visible, onClick }: ScrollToBottomProps) {
  if (!visible) return null;

  return (
    <button
      onClick={onClick}
      aria-label="Scroll to latest messages"
      className="absolute bottom-20 right-4 flex h-10 w-10 items-center justify-center rounded-full border border-border bg-card shadow-md transition-opacity duration-200 hover:bg-muted"
    >
      <ChevronDown className="h-5 w-5 text-muted-foreground" />
    </button>
  );
}
