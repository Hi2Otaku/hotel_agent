import { useCallback, useEffect, useRef, useState, type RefObject } from 'react';

export function useAutoScroll(ref: RefObject<HTMLElement | null>, deps: unknown[]) {
  const [isAtBottom, setIsAtBottom] = useState(true);
  const userScrolledUp = useRef(false);

  const checkIsAtBottom = useCallback(() => {
    const el = ref.current;
    if (!el) return true;
    return el.scrollTop + el.clientHeight >= el.scrollHeight - 50;
  }, [ref]);

  const scrollToBottom = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    userScrolledUp.current = false;
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    setIsAtBottom(true);
  }, [ref]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handleScroll = () => {
      const atBottom = checkIsAtBottom();
      setIsAtBottom(atBottom);
      if (!atBottom) {
        userScrolledUp.current = true;
      } else {
        userScrolledUp.current = false;
      }
    };

    el.addEventListener('scroll', handleScroll, { passive: true });
    return () => el.removeEventListener('scroll', handleScroll);
  }, [ref, checkIsAtBottom]);

  // Auto-scroll on new content if user hasn't scrolled up
  useEffect(() => {
    if (!userScrolledUp.current) {
      const el = ref.current;
      if (el) {
        el.scrollTop = el.scrollHeight;
        setIsAtBottom(true);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { isAtBottom, scrollToBottom };
}
