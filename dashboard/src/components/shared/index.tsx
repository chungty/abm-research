/**
 * Shared UI Components
 *
 * Reusable components for consistent UX across the dashboard:
 * - LoadingSpinner: Consistent loading indicators
 * - ErrorBanner: User-friendly error messages with actionable guidance
 * - EmptyState: Consistent empty states with context and actions
 * - DataQualityBanner: Warnings about template/mock/stale data
 * - FocusTrap: Accessibility helper for modal dialogs
 */

import { useEffect, useRef, type ReactNode } from 'react';

// =============================================================================
// Loading Spinner
// =============================================================================

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export function LoadingSpinner({ size = 'md', message, className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg
        className={`animate-spin ${sizeClasses[size]}`}
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {message && (
        <span style={{ color: 'var(--color-text-secondary)' }}>{message}</span>
      )}
    </div>
  );
}

// =============================================================================
// Error Banner
// =============================================================================

type ErrorType = 'api' | 'config' | 'validation' | 'permission' | 'unknown';

interface ErrorBannerProps {
  error: Error | string;
  type?: ErrorType;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

const ERROR_GUIDANCE: Record<ErrorType, { title: string; guidance: string }> = {
  api: {
    title: 'Connection Error',
    guidance: 'Check that the Flask API is running at http://localhost:5001',
  },
  config: {
    title: 'Configuration Error',
    guidance: 'Check your Notion API token and database IDs in .env file',
  },
  validation: {
    title: 'Invalid Input',
    guidance: 'Please check your input and try again',
  },
  permission: {
    title: 'Permission Denied',
    guidance: 'You may not have access to this resource',
  },
  unknown: {
    title: 'Something went wrong',
    guidance: 'Please try again or contact support if the issue persists',
  },
};

export function ErrorBanner({ error, type = 'unknown', onRetry, onDismiss, className = '' }: ErrorBannerProps) {
  const errorMessage = typeof error === 'string' ? error : error.message;

  // Auto-detect error type from message if not specified
  const detectedType = type === 'unknown' ? detectErrorType(errorMessage) : type;
  const { title, guidance } = ERROR_GUIDANCE[detectedType];

  return (
    <div
      className={`p-4 rounded-lg ${className}`}
      style={{
        backgroundColor: 'var(--color-priority-low-bg)',
        border: '1px solid var(--color-priority-low-border)',
      }}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <svg
          className="w-5 h-5 flex-shrink-0 mt-0.5"
          style={{ color: 'var(--color-priority-low)' }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div className="flex-1 min-w-0">
          <p
            className="font-medium"
            style={{ color: 'var(--color-priority-low)' }}
          >
            {title}
          </p>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {errorMessage}
          </p>
          <p
            className="text-xs mt-2"
            style={{ color: 'var(--color-text-muted)' }}
          >
            💡 {guidance}
          </p>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-3 py-1 rounded text-xs font-medium transition-colors"
              style={{
                backgroundColor: 'var(--color-bg-elevated)',
                color: 'var(--color-text-secondary)',
                border: '1px solid var(--color-border-default)',
              }}
            >
              Retry
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-1 rounded transition-colors"
              style={{ color: 'var(--color-text-muted)' }}
              aria-label="Dismiss error"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function detectErrorType(message: string): ErrorType {
  const lowerMessage = message.toLowerCase();
  if (lowerMessage.includes('fetch') || lowerMessage.includes('network') || lowerMessage.includes('connection') || lowerMessage.includes('api')) {
    return 'api';
  }
  if (lowerMessage.includes('notion') || lowerMessage.includes('config') || lowerMessage.includes('token')) {
    return 'config';
  }
  if (lowerMessage.includes('invalid') || lowerMessage.includes('required') || lowerMessage.includes('format')) {
    return 'validation';
  }
  if (lowerMessage.includes('permission') || lowerMessage.includes('unauthorized') || lowerMessage.includes('forbidden')) {
    return 'permission';
  }
  return 'unknown';
}

// =============================================================================
// Empty State
// =============================================================================

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    href?: string;
    onClick?: () => void;
  };
  className?: string;
}

export function EmptyState({ icon, title, description, action, secondaryAction, className = '' }: EmptyStateProps) {
  return (
    <div
      className={`text-center py-8 ${className}`}
      style={{ color: 'var(--color-text-muted)' }}
    >
      {icon && (
        <div
          className="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            border: '1px solid var(--color-border-default)',
          }}
        >
          {icon}
        </div>
      )}
      <p
        className="font-medium"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {title}
      </p>
      <p className="text-sm mt-1 max-w-sm mx-auto">
        {description}
      </p>
      {(action || secondaryAction) && (
        <div className="mt-4 flex items-center justify-center gap-3">
          {action && (
            <button
              onClick={action.onClick}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                backgroundColor: 'var(--color-accent-primary)',
                color: 'white',
              }}
            >
              {action.label}
            </button>
          )}
          {secondaryAction && (
            secondaryAction.href ? (
              <a
                href={secondaryAction.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm underline"
                style={{ color: 'var(--color-accent-primary)' }}
              >
                {secondaryAction.label}
              </a>
            ) : (
              <button
                onClick={secondaryAction.onClick}
                className="text-sm underline"
                style={{ color: 'var(--color-accent-primary)' }}
              >
                {secondaryAction.label}
              </button>
            )
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Data Quality Banner
// =============================================================================

type DataSourceType = 'ai' | 'template' | 'mock' | 'cached' | 'partial';

interface DataQualityBannerProps {
  source: DataSourceType;
  lastUpdated?: Date | string;
  onRefresh?: () => void;
  details?: string;
  className?: string;
}

const DATA_SOURCE_CONFIG: Record<DataSourceType, {
  icon: string;
  label: string;
  color: string;
  bgColor: string;
  guidance: string;
}> = {
  ai: {
    icon: '✨',
    label: 'AI-Generated',
    color: 'var(--color-priority-very-high)',
    bgColor: 'var(--color-priority-very-high-bg)',
    guidance: 'This content was generated by AI based on available data',
  },
  template: {
    icon: '📝',
    label: 'Template Data',
    color: 'var(--color-priority-medium)',
    bgColor: 'var(--color-priority-medium-bg)',
    guidance: 'Using template fallback. Click "Generate with AI" for personalized content',
  },
  mock: {
    icon: '🔧',
    label: 'Demo Data',
    color: 'var(--color-priority-low)',
    bgColor: 'var(--color-priority-low-bg)',
    guidance: 'Showing demo data. Connect Notion to see real accounts',
  },
  cached: {
    icon: '⏱️',
    label: 'Cached Data',
    color: 'var(--color-text-tertiary)',
    bgColor: 'var(--color-bg-card)',
    guidance: 'Data may be stale. Click refresh for latest information',
  },
  partial: {
    icon: '⚠️',
    label: 'Incomplete Data',
    color: 'var(--color-priority-medium)',
    bgColor: 'var(--color-priority-medium-bg)',
    guidance: 'Some fields are missing. Run "Deep Research" to populate all fields',
  },
};

export function DataQualityBanner({ source, lastUpdated, onRefresh, details, className = '' }: DataQualityBannerProps) {
  const config = DATA_SOURCE_CONFIG[source];

  const formattedDate = lastUpdated
    ? typeof lastUpdated === 'string'
      ? lastUpdated
      : formatRelativeTime(lastUpdated)
    : null;

  return (
    <div
      className={`px-3 py-2 rounded-lg flex items-center gap-2 text-xs ${className}`}
      style={{
        backgroundColor: config.bgColor,
        border: `1px solid ${config.color}30`,
      }}
      role="status"
    >
      <span>{config.icon}</span>
      <span style={{ color: config.color }} className="font-medium">
        {config.label}
      </span>
      <span style={{ color: 'var(--color-text-muted)' }}>—</span>
      <span style={{ color: 'var(--color-text-secondary)' }}>
        {details || config.guidance}
      </span>
      {formattedDate && (
        <>
          <span style={{ color: 'var(--color-text-muted)' }}>•</span>
          <span style={{ color: 'var(--color-text-muted)' }}>
            Updated {formattedDate}
          </span>
        </>
      )}
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="ml-auto px-2 py-0.5 rounded transition-colors"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            color: 'var(--color-text-secondary)',
          }}
        >
          Refresh
        </button>
      )}
    </div>
  );
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

// =============================================================================
// Focus Trap (for modals)
// =============================================================================

interface FocusTrapProps {
  children: ReactNode;
  active?: boolean;
  onEscape?: () => void;
}

export function FocusTrap({ children, active = true, onEscape }: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active) return;

    const container = containerRef.current;
    if (!container) return;

    // Get all focusable elements
    const focusableSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const focusableElements = container.querySelectorAll<HTMLElement>(focusableSelector);
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first input/textarea element on mount (better UX for forms)
    // Falls back to first focusable element if no inputs exist
    const firstInputSelector = 'input:not([type="hidden"]):not([disabled]), textarea:not([disabled])';
    const firstInput = container.querySelector<HTMLElement>(firstInputSelector);
    (firstInput || firstElement)?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && onEscape) {
        e.preventDefault();
        onEscape();
        return;
      }

      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift+Tab: if on first element, go to last
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab: if on last element, go to first
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [active, onEscape]);

  return (
    <div ref={containerRef} role="dialog" aria-modal="true">
      {children}
    </div>
  );
}

// =============================================================================
// Accessible Button
// =============================================================================

interface IconButtonProps {
  onClick: () => void;
  ariaLabel: string;
  icon: ReactNode;
  disabled?: boolean;
  className?: string;
  title?: string;
}

export function IconButton({ onClick, ariaLabel, icon, disabled, className = '', title }: IconButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      title={title || ariaLabel}
      className={`p-2 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${className}`}
      style={{
        color: 'var(--color-text-muted)',
        backgroundColor: 'transparent',
      }}
    >
      {icon}
    </button>
  );
}

// =============================================================================
// Configuration Constants (replacing hardcoded values)
// =============================================================================

/**
 * Application configuration constants
 * These values were previously hardcoded throughout the app.
 * Now centralized for easy modification and documentation.
 */
export const APP_CONFIG = {
  /** Minimum lead score required to show "Reveal Email" button */
  LEAD_SCORE_THRESHOLD: 60,

  /** Maximum events to show before "Show more" */
  MAX_EVENTS_DISPLAY: 10,

  /** Maximum "Why Prioritize" reasons to show collapsed */
  MAX_COLLAPSED_REASONS: 2,

  /** Delay after account creation before selection (ms) */
  ACCOUNT_CREATION_DELAY: 500,

  /** LinkedIn message character limit */
  LINKEDIN_CHAR_LIMIT: 300,

  /** API endpoints */
  API: {
    BASE_URL: 'http://localhost:5001',
  },

  /** Score thresholds for color coding */
  SCORE_THRESHOLDS: {
    VERY_HIGH: 80,
    HIGH: 60,
    MEDIUM: 40,
  },
} as const;

/**
 * Get score level label based on value
 */
export function getScoreLevel(score: number): 'Very High' | 'High' | 'Medium' | 'Low' {
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.VERY_HIGH) return 'Very High';
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.HIGH) return 'High';
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.MEDIUM) return 'Medium';
  return 'Low';
}

/**
 * Get score color based on value
 */
export function getScoreColor(score: number): string {
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.VERY_HIGH) return 'var(--color-priority-very-high)';
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.HIGH) return 'var(--color-priority-high)';
  if (score >= APP_CONFIG.SCORE_THRESHOLDS.MEDIUM) return 'var(--color-priority-medium)';
  return 'var(--color-text-tertiary)';
}
