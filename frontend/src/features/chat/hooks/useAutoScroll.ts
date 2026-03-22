import { useCallback, useEffect, useRef, useState, type RefObject } from 'react';

const BOTTOM_THRESHOLD = 50;

export function useAutoScroll(
  ref: RefObject<HTMLElement | null>,
  deps: unknown[],
) {
  const [isAtBottom, setIsAtBottom] = useState(true);
  const shouldAutoScroll = useRef(true);

  const checkBottom = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    const atBottom =
      el.scrollTop + el.clientHeight >= el.scrollHeight - BOTTOM_THRESHOLD;
    setIsAtBottom(atBottom);
    shouldAutoScroll.current = atBottom;
  }, [ref]);

  const scrollToBottom = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    shouldAutoScroll.current = true;
    setIsAtBottom(true);
  }, [ref]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.addEventListener('scroll', checkBottom, { passive: true });
    return () => el.removeEventListener('scroll', checkBottom);
  }, [ref, checkBottom]);

  // Auto-scroll on dependency change if user is at bottom
  useEffect(() => {
    if (shouldAutoScroll.current) {
      const el = ref.current;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { isAtBottom, scrollToBottom };
}
