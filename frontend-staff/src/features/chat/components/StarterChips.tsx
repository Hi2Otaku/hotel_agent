interface StarterChipsProps {
  onSendMessage: (message: string) => void;
}

const STAFF_CHIPS = [
  "Today's check-ins",
  'Room status',
  'Find guest',
  'Occupancy report',
];

export function StarterChips({ onSendMessage }: StarterChipsProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {STAFF_CHIPS.map((chip) => (
        <button
          key={chip}
          onClick={() => onSendMessage(chip)}
          className="h-9 rounded-full border border-primary px-4 text-sm text-primary transition-all hover:bg-primary hover:text-primary-foreground active:scale-[0.98] motion-safe:hover:scale-[1.02]"
        >
          {chip}
        </button>
      ))}
    </div>
  );
}
