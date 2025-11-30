import { useState, type ReactNode } from 'react';

interface Props {
  title: string;
  defaultOpen?: boolean;
  badge?: string | number;
  badgeColor?: string;
  children: ReactNode;
}

export function CollapsibleSection({
  title,
  defaultOpen = true,
  badge,
  badgeColor = 'var(--color-accent-primary)',
  children
}: Props) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="card-surface overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between transition-colors"
        style={{ backgroundColor: isOpen ? 'transparent' : 'var(--color-bg-card)' }}
      >
        <div className="flex items-center gap-3">
          <svg
            className="w-4 h-4 transition-transform"
            style={{
              color: 'var(--color-text-tertiary)',
              transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)'
            }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
          <h3
            className="text-base font-semibold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {title}
          </h3>
          {badge !== undefined && (
            <span
              className="px-2 py-0.5 rounded-full text-xs font-data font-medium"
              style={{
                backgroundColor: `${badgeColor}20`,
                color: badgeColor,
              }}
            >
              {badge}
            </span>
          )}
        </div>
        <span
          className="text-xs"
          style={{ color: 'var(--color-text-muted)' }}
        >
          {isOpen ? 'Collapse' : 'Expand'}
        </span>
      </button>

      <div
        className="overflow-hidden transition-all"
        style={{
          maxHeight: isOpen ? '2000px' : '0',
          opacity: isOpen ? 1 : 0,
        }}
      >
        <div className="p-4 pt-0">
          {children}
        </div>
      </div>
    </div>
  );
}
