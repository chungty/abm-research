import { useState, useEffect } from 'react';

/**
 * Debounce hook for delaying value updates.
 * Useful for search inputs to avoid excessive re-renders.
 *
 * @param value - The value to debounce
 * @param delay - Delay in milliseconds (default: 200ms)
 * @returns The debounced value
 */
export function useDebounce<T>(value: T, delay: number = 200): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}
