import { useState, useCallback } from 'react';

/**
 * Hook to persist state in sessionStorage.
 * State persists across page reloads but clears on browser/tab close.
 *
 * @param key - The sessionStorage key
 * @param initialValue - Default value if no stored value exists
 * @returns [value, setValue] tuple similar to useState
 */
export function useSessionStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Get initial value from sessionStorage or use provided default
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      // If sessionStorage is unavailable or parsing fails, use initial value
      console.warn(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Setter that updates both state and sessionStorage
  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      try {
        // Support functional updates like useState
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        sessionStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.warn(`Error writing to sessionStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
}
