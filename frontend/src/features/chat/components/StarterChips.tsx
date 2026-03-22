const GUEST_CHIPS = [
  'Search rooms',
  'Check my booking',
  'Hotel info',
  'Cancellation policy',
];

interface StarterChipsProps {
  onSend: (message: string) => void;
}

export function StarterChips({ onSend }: StarterChipsProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {GUEST_CHIPS.map((chip) => (
        <button
          key={chip}
          type="button"
          onClick={() => onSend(chip)}
          className="h-9 rounded-full border border-[#0F766E] px-4 text-sm text-[#0F766E] transition-colors hover:bg-[#0F766E] hover:text-white motion-safe:hover:scale-[1.02] motion-safe:active:scale-[0.98]"
        >
          {chip}
        </button>
      ))}
    </div>
  );
}
