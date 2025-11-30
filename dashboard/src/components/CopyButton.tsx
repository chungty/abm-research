import { useState } from 'react';

interface Props {
  text: string;
  label?: string;
  size?: 'sm' | 'md';
  variant?: 'icon' | 'full';
}

export function CopyButton({
  text,
  label = 'Copy',
  size = 'md',
  variant = 'full'
}: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
  };

  if (variant === 'icon') {
    return (
      <button
        onClick={handleCopy}
        className="p-1.5 rounded transition-all"
        style={{
          backgroundColor: copied ? 'var(--color-priority-very-high-bg)' : 'var(--color-bg-hover)',
          color: copied ? 'var(--color-priority-very-high)' : 'var(--color-text-tertiary)',
        }}
        title={copied ? 'Copied!' : 'Copy to clipboard'}
      >
        {copied ? (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
        )}
      </button>
    );
  }

  return (
    <button
      onClick={handleCopy}
      className={`rounded font-medium transition-all flex items-center gap-1.5 ${sizeClasses[size]}`}
      style={{
        backgroundColor: copied ? 'var(--color-priority-very-high-bg)' : 'var(--color-accent-primary-muted)',
        color: copied ? 'var(--color-priority-very-high)' : 'var(--color-accent-primary)',
        border: `1px solid ${copied ? 'var(--color-priority-very-high-border)' : 'var(--color-accent-primary)'}`,
      }}
    >
      {copied ? (
        <>
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Copied!
        </>
      ) : (
        <>
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          {label}
        </>
      )}
    </button>
  );
}
