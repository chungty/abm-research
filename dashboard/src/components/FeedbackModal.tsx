import { useState, useCallback } from 'react';
import { FocusTrap } from './shared';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: string, category: string) => Promise<void>;
}

type FeedbackStatus = 'idle' | 'submitting' | 'success' | 'error';

const FEEDBACK_CATEGORIES = [
  { value: 'feature', label: 'Feature Request' },
  { value: 'bug', label: 'Bug Report' },
  { value: 'improvement', label: 'Improvement' },
  { value: 'other', label: 'Other' },
];

export function FeedbackModal({ isOpen, onClose, onSubmit }: Props) {
  const [feedback, setFeedback] = useState('');
  const [category, setCategory] = useState('feature');
  const [status, setStatus] = useState<FeedbackStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const handleClose = useCallback(() => {
    if (status === 'submitting') return;
    setFeedback('');
    setCategory('feature');
    setStatus('idle');
    setError(null);
    onClose();
  }, [status, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedback.trim()) return;

    setStatus('submitting');
    setError(null);

    try {
      await onSubmit(feedback.trim(), category);
      setStatus('success');
      // Auto-close after success
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
      setStatus('error');
    }
  };

  if (!isOpen) return null;

  const isSubmitting = status === 'submitting';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
      onClick={handleClose}
      role="presentation"
    >
      <FocusTrap active={isOpen && !isSubmitting} onEscape={handleClose}>
        <div
          className="w-full max-w-md mx-4 rounded-xl shadow-2xl animate-fade-in"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-default)',
          }}
          onClick={e => e.stopPropagation()}
          aria-labelledby="feedback-title"
        >
          {/* Header */}
          <div
            className="px-6 py-4 flex items-center justify-between"
            style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
          >
            <div>
              <h2
                id="feedback-title"
                className="text-lg font-heading"
                style={{ color: 'var(--color-text-primary)' }}
              >
                Submit Feedback
              </h2>
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Help us improve the product
              </p>
            </div>
            <button
              onClick={handleClose}
              disabled={isSubmitting}
              aria-label="Close dialog"
              className="p-2 rounded-lg transition-all focus:outline-none focus-visible:ring-2"
              style={{
                color: 'var(--color-text-muted)',
                backgroundColor: 'transparent',
                opacity: isSubmitting ? 0.5 : 1,
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
              }}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Category Selection */}
            <div>
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Category
              </label>
              <div className="flex flex-wrap gap-2">
                {FEEDBACK_CATEGORIES.map(cat => (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setCategory(cat.value)}
                    disabled={isSubmitting}
                    className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
                    style={{
                      backgroundColor: category === cat.value
                        ? 'var(--color-accent-primary-muted)'
                        : 'var(--color-bg-card)',
                      color: category === cat.value
                        ? 'var(--color-accent-primary)'
                        : 'var(--color-text-secondary)',
                      border: category === cat.value
                        ? '1px solid var(--color-accent-primary)'
                        : '1px solid var(--color-border-default)',
                    }}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Feedback Text */}
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Your Feedback
              </label>
              <textarea
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
                disabled={isSubmitting}
                placeholder="Describe your suggestion, bug, or feedback..."
                rows={4}
                className="input-field w-full resize-none"
                style={{ minHeight: '100px' }}
              />
              <p
                className="text-xs mt-1"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Your feedback will be sent to the product team
              </p>
            </div>

            {/* Error Message */}
            {status === 'error' && error && (
              <div
                className="p-3 rounded-lg"
                style={{
                  backgroundColor: 'var(--color-priority-low-bg)',
                  border: '1px solid var(--color-priority-low-border)',
                }}
              >
                <p
                  className="text-sm"
                  style={{ color: 'var(--color-priority-low)' }}
                >
                  {error}
                </p>
              </div>
            )}

            {/* Success Message */}
            {status === 'success' && (
              <div
                className="p-3 rounded-lg flex items-center gap-2"
                style={{
                  backgroundColor: 'var(--color-priority-high-bg)',
                  border: '1px solid var(--color-priority-high-border)',
                }}
              >
                <svg
                  className="w-5 h-5"
                  style={{ color: 'var(--color-priority-high)' }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <p
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-priority-high)' }}
                >
                  Thanks for your feedback!
                </p>
              </div>
            )}

            {/* Actions */}
            {status !== 'success' && (
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-lg font-medium text-sm transition-all"
                  style={{
                    backgroundColor: 'transparent',
                    color: 'var(--color-text-secondary)',
                    border: '1px solid var(--color-border-default)',
                    opacity: isSubmitting ? 0.5 : 1,
                    cursor: isSubmitting ? 'not-allowed' : 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !feedback.trim()}
                  className="px-5 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
                  style={{
                    background: isSubmitting || !feedback.trim()
                      ? 'var(--color-bg-card)'
                      : 'linear-gradient(135deg, var(--color-accent-primary) 0%, #2563eb 100%)',
                    color: isSubmitting || !feedback.trim()
                      ? 'var(--color-text-muted)'
                      : 'white',
                    cursor: isSubmitting || !feedback.trim()
                      ? 'not-allowed'
                      : 'pointer',
                    boxShadow: isSubmitting || !feedback.trim()
                      ? 'none'
                      : '0 2px 8px rgba(59, 130, 246, 0.3)',
                  }}
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <SendIcon />
                      Submit Feedback
                    </>
                  )}
                </button>
              </div>
            )}
          </form>
        </div>
      </FocusTrap>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <svg
      className="animate-spin w-4 h-4"
      fill="none"
      viewBox="0 0 24 24"
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
  );
}

function SendIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  );
}
