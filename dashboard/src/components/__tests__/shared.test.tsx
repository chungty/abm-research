/**
 * Tests for shared UI components
 *
 * Tests the reusable components in shared/index.tsx:
 * - LoadingSpinner: Size variants, message display
 * - ErrorBanner: Error type detection, retry/dismiss actions
 * - EmptyState: Action buttons, secondary actions
 * - DataQualityBanner: Source types, refresh callbacks
 * - FocusTrap: Focus cycling, escape key handling
 * - Helper functions: getScoreLevel, getScoreColor
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  LoadingSpinner,
  ErrorBanner,
  EmptyState,
  DataQualityBanner,
  FocusTrap,
  IconButton,
  getScoreLevel,
  getScoreColor,
  APP_CONFIG,
} from '../shared';

// =============================================================================
// LoadingSpinner Tests
// =============================================================================

describe('LoadingSpinner', () => {
  it('renders without message by default', () => {
    render(<LoadingSpinner />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('displays message when provided', () => {
    render(<LoadingSpinner message="Loading accounts..." />);
    expect(screen.getByText('Loading accounts...')).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />);
    let spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('w-4', 'h-4');

    rerender(<LoadingSpinner size="lg" />);
    spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('w-8', 'h-8');
  });
});

// =============================================================================
// ErrorBanner Tests
// =============================================================================

describe('ErrorBanner', () => {
  it('displays error message', () => {
    render(<ErrorBanner error="A specific error occurred" />);
    expect(screen.getByText('A specific error occurred')).toBeInTheDocument();
  });

  it('displays Error object message', () => {
    render(<ErrorBanner error={new Error('Network failure')} />);
    expect(screen.getByText('Network failure')).toBeInTheDocument();
  });

  it('shows retry button when onRetry provided', () => {
    const onRetry = vi.fn();
    render(<ErrorBanner error="Error" onRetry={onRetry} />);

    const retryButton = screen.getByText('Retry');
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('shows dismiss button when onDismiss provided', () => {
    const onDismiss = vi.fn();
    render(<ErrorBanner error="Error" onDismiss={onDismiss} />);

    const dismissButton = screen.getByLabelText('Dismiss error');
    expect(dismissButton).toBeInTheDocument();

    fireEvent.click(dismissButton);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('auto-detects API error type from message', () => {
    render(<ErrorBanner error="Failed to fetch data from API" />);
    expect(screen.getByText('Connection Error')).toBeInTheDocument();
    expect(screen.getByText(/Flask API/)).toBeInTheDocument();
  });

  it('auto-detects config error type from message', () => {
    // "token" keyword triggers config error type (avoid "api" which triggers api type first)
    render(<ErrorBanner error="Token not found in configuration" />);
    expect(screen.getByText('Configuration Error')).toBeInTheDocument();
    expect(screen.getByText(/.env file/)).toBeInTheDocument();
  });

  it('auto-detects validation error type from message', () => {
    render(<ErrorBanner error="Invalid email format required" />);
    expect(screen.getByText('Invalid Input')).toBeInTheDocument();
  });

  it('has alert role for accessibility', () => {
    render(<ErrorBanner error="Error" />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });
});

// =============================================================================
// EmptyState Tests
// =============================================================================

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(
      <EmptyState
        title="No contacts found"
        description="Try adding contacts from LinkedIn"
      />
    );

    expect(screen.getByText('No contacts found')).toBeInTheDocument();
    expect(screen.getByText('Try adding contacts from LinkedIn')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No data"
        description="Get started"
        action={{ label: 'Add Account', onClick }}
      />
    );

    const button = screen.getByText('Add Account');
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders secondary link when href provided', () => {
    render(
      <EmptyState
        title="No data"
        description="Get started"
        secondaryAction={{ label: 'Learn more', href: 'https://example.com' }}
      />
    );

    const link = screen.getByText('Learn more');
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('renders secondary button when onClick provided', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No data"
        description="Get started"
        secondaryAction={{ label: 'Try again', onClick }}
      />
    );

    const button = screen.getByText('Try again');
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders icon when provided', () => {
    render(
      <EmptyState
        title="No data"
        description="Test"
        icon={<span data-testid="custom-icon">Icon</span>}
      />
    );

    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });
});

// =============================================================================
// DataQualityBanner Tests
// =============================================================================

describe('DataQualityBanner', () => {
  it('displays AI source label', () => {
    render(<DataQualityBanner source="ai" />);
    expect(screen.getByText('AI-Generated')).toBeInTheDocument();
  });

  it('displays template source with guidance', () => {
    render(<DataQualityBanner source="template" />);
    expect(screen.getByText('Template Data')).toBeInTheDocument();
    expect(screen.getByText(/Generate with AI/)).toBeInTheDocument();
  });

  it('displays custom details when provided', () => {
    render(<DataQualityBanner source="ai" details="Custom AI message" />);
    expect(screen.getByText('Custom AI message')).toBeInTheDocument();
  });

  it('shows refresh button when onRefresh provided', () => {
    const onRefresh = vi.fn();
    render(<DataQualityBanner source="cached" onRefresh={onRefresh} />);

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);
    expect(onRefresh).toHaveBeenCalledTimes(1);
  });

  it('displays formatted last updated time', () => {
    render(<DataQualityBanner source="cached" lastUpdated="2h ago" />);
    expect(screen.getByText('Updated 2h ago')).toBeInTheDocument();
  });

  it('has status role for accessibility', () => {
    render(<DataQualityBanner source="ai" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays all source types correctly', () => {
    const sources = ['ai', 'template', 'mock', 'cached', 'partial'] as const;
    const labels = ['AI-Generated', 'Template Data', 'Demo Data', 'Cached Data', 'Incomplete Data'];

    sources.forEach((source, index) => {
      const { unmount } = render(<DataQualityBanner source={source} />);
      expect(screen.getByText(labels[index])).toBeInTheDocument();
      unmount();
    });
  });
});

// =============================================================================
// FocusTrap Tests
// =============================================================================

describe('FocusTrap', () => {
  it('renders children', () => {
    render(
      <FocusTrap>
        <button>Click me</button>
      </FocusTrap>
    );

    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('has dialog role', () => {
    render(
      <FocusTrap>
        <button>Click me</button>
      </FocusTrap>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('calls onEscape when Escape key pressed', async () => {
    const onEscape = vi.fn();
    render(
      <FocusTrap onEscape={onEscape}>
        <button>Click me</button>
      </FocusTrap>
    );

    await userEvent.keyboard('{Escape}');
    expect(onEscape).toHaveBeenCalledTimes(1);
  });

  it('does not trap focus when active is false', () => {
    const onEscape = vi.fn();
    render(
      <FocusTrap active={false} onEscape={onEscape}>
        <button>Click me</button>
      </FocusTrap>
    );

    // Should not call onEscape when inactive
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onEscape).not.toHaveBeenCalled();
  });
});

// =============================================================================
// IconButton Tests
// =============================================================================

describe('IconButton', () => {
  it('renders with aria-label', () => {
    render(
      <IconButton
        onClick={() => {}}
        ariaLabel="Close dialog"
        icon={<span>X</span>}
      />
    );

    expect(screen.getByLabelText('Close dialog')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(
      <IconButton
        onClick={onClick}
        ariaLabel="Action"
        icon={<span>Icon</span>}
      />
    );

    fireEvent.click(screen.getByLabelText('Action'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('can be disabled', () => {
    const onClick = vi.fn();
    render(
      <IconButton
        onClick={onClick}
        ariaLabel="Action"
        icon={<span>Icon</span>}
        disabled
      />
    );

    const button = screen.getByLabelText('Action');
    expect(button).toBeDisabled();

    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('displays title when provided', () => {
    render(
      <IconButton
        onClick={() => {}}
        ariaLabel="Action"
        icon={<span>Icon</span>}
        title="Custom tooltip"
      />
    );

    expect(screen.getByTitle('Custom tooltip')).toBeInTheDocument();
  });
});

// =============================================================================
// Helper Function Tests
// =============================================================================

describe('getScoreLevel', () => {
  it('returns "Very High" for scores >= 80', () => {
    expect(getScoreLevel(80)).toBe('Very High');
    expect(getScoreLevel(100)).toBe('Very High');
    expect(getScoreLevel(95)).toBe('Very High');
  });

  it('returns "High" for scores >= 60 and < 80', () => {
    expect(getScoreLevel(60)).toBe('High');
    expect(getScoreLevel(79)).toBe('High');
    expect(getScoreLevel(70)).toBe('High');
  });

  it('returns "Medium" for scores >= 40 and < 60', () => {
    expect(getScoreLevel(40)).toBe('Medium');
    expect(getScoreLevel(59)).toBe('Medium');
    expect(getScoreLevel(50)).toBe('Medium');
  });

  it('returns "Low" for scores < 40', () => {
    expect(getScoreLevel(39)).toBe('Low');
    expect(getScoreLevel(0)).toBe('Low');
    expect(getScoreLevel(20)).toBe('Low');
  });
});

describe('getScoreColor', () => {
  it('returns very high color for scores >= 80', () => {
    expect(getScoreColor(80)).toBe('var(--color-priority-very-high)');
  });

  it('returns high color for scores >= 60', () => {
    expect(getScoreColor(60)).toBe('var(--color-priority-high)');
  });

  it('returns medium color for scores >= 40', () => {
    expect(getScoreColor(40)).toBe('var(--color-priority-medium)');
  });

  it('returns tertiary color for low scores', () => {
    expect(getScoreColor(20)).toBe('var(--color-text-tertiary)');
  });
});

describe('APP_CONFIG', () => {
  it('has expected score thresholds', () => {
    expect(APP_CONFIG.SCORE_THRESHOLDS.VERY_HIGH).toBe(80);
    expect(APP_CONFIG.SCORE_THRESHOLDS.HIGH).toBe(60);
    expect(APP_CONFIG.SCORE_THRESHOLDS.MEDIUM).toBe(40);
  });

  it('has expected lead score threshold', () => {
    expect(APP_CONFIG.LEAD_SCORE_THRESHOLD).toBe(60);
  });

  it('has API base URL configured', () => {
    expect(APP_CONFIG.API.BASE_URL).toBe('http://localhost:5001');
  });
});
