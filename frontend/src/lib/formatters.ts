import { format, parseISO, differenceInDays } from 'date-fns';

/**
 * Format a number or string as USD currency.
 */
export function formatCurrency(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(num);
}

/**
 * Format an ISO date string as "Mar 21, 2026".
 */
export function formatDate(dateStr: string): string {
  return format(parseISO(dateStr), 'MMM d, yyyy');
}

/**
 * Format a date range as "Mar 21 - Mar 25, 2026".
 */
export function formatDateRange(checkIn: string, checkOut: string): string {
  const inDate = parseISO(checkIn);
  const outDate = parseISO(checkOut);
  const inStr = format(inDate, 'MMM d');
  const outStr = format(outDate, 'MMM d, yyyy');
  return `${inStr} - ${outStr}`;
}

/**
 * Calculate the number of nights between two ISO date strings.
 */
export function calculateNights(checkIn: string, checkOut: string): number {
  return differenceInDays(parseISO(checkOut), parseISO(checkIn));
}
