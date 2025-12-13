import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';
import { FocusTrap, ErrorBanner } from './shared';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onAccountCreated: (accountId: string, domain: string, viewAccount?: boolean) => void;
}

type FormStatus = 'idle' | 'creating' | 'researching' | 'success' | 'error';

interface FormData {
  name: string;
  domain: string;
}

const initialFormData: FormData = {
  name: '',
  domain: '',
};

export function AddAccountModal({ isOpen, onClose, onAccountCreated }: Props) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [status, setStatus] = useState<FormStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [autoResearch, setAutoResearch] = useState(true);
  const [progress, setProgress] = useState<string>('');
  const [createdAccountId, setCreatedAccountId] = useState<string | null>(null);
  const [createdAccountName, setCreatedAccountName] = useState<string>('');
  const [researchFailed, setResearchFailed] = useState(false);
  const [domainError, setDomainError] = useState<string | null>(null);

  // Domain validation helper
  const validateDomain = useCallback((domain: string): string | null => {
    if (!domain) return null; // Empty is handled by required attribute
    const trimmed = domain.trim().toLowerCase();
    // Remove protocol if present for validation
    const cleaned = trimmed.replace(/^https?:\/\//, '').replace(/\/$/, '');
    // Must contain at least one dot and no spaces
    if (!cleaned.includes('.')) {
      return 'Domain must include a TLD (e.g., company.com)';
    }
    if (cleaned.includes(' ')) {
      return 'Domain cannot contain spaces';
    }
    // Check for valid domain characters
    if (!/^[a-z0-9.-]+$/.test(cleaned)) {
      return 'Domain contains invalid characters';
    }
    return null;
  }, []);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData(initialFormData);
      setStatus('idle');
      setError(null);
      setCreatedAccountId(null);
      setCreatedAccountName('');
      setResearchFailed(false);
      setDomainError(null);
    }
  }, [isOpen]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear domain error when user edits domain field
    if (name === 'domain') {
      setDomainError(null);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResearchFailed(false);

    // Validate domain before submitting
    const domainValidationError = validateDomain(formData.domain);
    if (domainValidationError) {
      setDomainError(domainValidationError);
      return;
    }

    setStatus('creating');
    setProgress('Creating account in Notion...');

    try {
      // Prepare data for API - only name and domain required
      // Other fields (Industry, Infrastructure, etc.) are populated by Deep Research
      const payload: Parameters<typeof api.createAccount>[0] = {
        name: formData.name.trim(),
        domain: formData.domain.trim(),
      };

      // Create the account
      const result = await api.createAccount(payload);

      if (!result.success) {
        throw new Error('Account creation failed');
      }

      // If auto-research is enabled, run the research pipeline
      if (autoResearch) {
        setStatus('researching');
        setProgress('Running deep research pipeline...');

        try {
          await api.runResearch(result.id, { force: false });
        } catch (researchErr) {
          // Research failure shouldn't block success - account was created
          console.warn('Research pipeline failed:', researchErr);
          setResearchFailed(true);
        }
      }

      setStatus('success');
      setProgress('');
      setCreatedAccountId(result.id);
      setCreatedAccountName(formData.name);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create account');
      setStatus('error');
      setProgress('');
    }
  };

  const handleClose = useCallback(() => {
    if (status === 'creating' || status === 'researching') return; // Prevent close during operation
    setFormData(initialFormData);
    setStatus('idle');
    setError(null);
    setCreatedAccountId(null);
    setCreatedAccountName('');
    setResearchFailed(false);
    setDomainError(null);
    onClose();
  }, [status, onClose]);

  const handleViewAccount = useCallback(() => {
    if (createdAccountId) {
      onAccountCreated(createdAccountId, formData.domain, true);
    }
    handleClose();
  }, [createdAccountId, formData.domain, onAccountCreated, handleClose]);

  const handleAddAnother = useCallback(() => {
    // Notify parent about the created account (without viewing)
    if (createdAccountId) {
      onAccountCreated(createdAccountId, formData.domain, false);
    }
    // Reset form for new entry
    setFormData(initialFormData);
    setStatus('idle');
    setCreatedAccountId(null);
    setCreatedAccountName('');
    setResearchFailed(false);
  }, [createdAccountId, formData.domain, onAccountCreated]);

  if (!isOpen) return null;

  const isSubmitting = status === 'creating' || status === 'researching';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
      onClick={handleClose}
      role="presentation"
    >
      <FocusTrap active={isOpen && !isSubmitting} onEscape={handleClose}>
        <div
          className="w-full max-w-lg mx-4 rounded-xl shadow-2xl animate-fade-in"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-default)',
          }}
          onClick={e => e.stopPropagation()}
          aria-labelledby="add-account-title"
        >
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
        >
          <div>
            <h2
              id="add-account-title"
              className="text-lg font-heading"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Add New Account
            </h2>
            <p
              className="text-sm"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Deep Research will auto-populate Industry, Infrastructure & ICP Score
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
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Required Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Company Name <span style={{ color: 'var(--color-target-hot)' }}>*</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                disabled={isSubmitting}
                placeholder="Acme Corporation"
                className="input-field w-full"
              />
            </div>
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Domain <span style={{ color: 'var(--color-target-hot)' }}>*</span>
              </label>
              <input
                type="text"
                name="domain"
                value={formData.domain}
                onChange={handleChange}
                required
                disabled={isSubmitting}
                placeholder="acme.com"
                className="input-field w-full"
                style={domainError ? { borderColor: 'var(--color-target-hot)' } : undefined}
              />
              {domainError && (
                <p
                  className="text-xs mt-1"
                  style={{ color: 'var(--color-target-hot)' }}
                >
                  {domainError}
                </p>
              )}
            </div>
          </div>

          {/* Auto-Research Toggle */}
          <div
            className="p-3 rounded-lg"
            style={{
              backgroundColor: 'var(--color-bg-card)',
              border: '1px solid var(--color-border-subtle)',
            }}
          >
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoResearch}
                onChange={e => setAutoResearch(e.target.checked)}
                disabled={isSubmitting}
                className="mt-1"
              />
              <div>
                <span
                  className="text-sm font-medium block"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  Auto-run Deep Research
                </span>
                <span
                  className="text-xs"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Automatically run 5-phase ABM research pipeline after creation
                </span>
              </div>
            </label>
          </div>

          {/* Error Message */}
          {status === 'error' && error && (
            <ErrorBanner
              error={error}
              onRetry={() => {
                setError(null);
                setStatus('idle');
              }}
            />
          )}

          {/* Progress Message */}
          {isSubmitting && progress && (
            <div
              className="p-3 rounded-lg"
              style={{
                backgroundColor: 'var(--color-bg-card)',
                border: '1px solid var(--color-border-default)',
              }}
            >
              <div className="flex items-center gap-3">
                <LoadingSpinner />
                <p
                  className="text-sm"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  {progress}
                </p>
              </div>
            </div>
          )}

          {/* Success State - Show action buttons */}
          {status === 'success' && (
            <div
              className="p-4 rounded-lg animate-fade-in"
              style={{
                backgroundColor: 'var(--color-priority-high-bg)',
                border: '1px solid var(--color-priority-high-border)',
              }}
            >
              <div className="flex items-center gap-2 mb-2">
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
                  {createdAccountName} created successfully!
                </p>
              </div>
              {researchFailed && (
                <p
                  className="text-xs mb-3 pl-7"
                  style={{ color: 'var(--color-priority-medium)' }}
                >
                  Note: Deep Research couldn't complete. You can run it manually from the account detail view.
                </p>
              )}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleViewAccount}
                  className="flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2"
                  style={{
                    background: 'linear-gradient(135deg, var(--color-accent-primary) 0%, #2563eb 100%)',
                    color: 'white',
                    boxShadow: '0 2px 8px rgba(59, 130, 246, 0.3)',
                  }}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  View Account
                </button>
                <button
                  type="button"
                  onClick={handleAddAnother}
                  className="px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
                  style={{
                    backgroundColor: 'var(--color-bg-card)',
                    color: 'var(--color-text-secondary)',
                    border: '1px solid var(--color-border-default)',
                  }}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Add Another
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 rounded-lg font-medium text-sm transition-all"
                  style={{
                    backgroundColor: 'transparent',
                    color: 'var(--color-text-muted)',
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          )}

          {/* Actions - Only show when not in success state */}
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
              disabled={isSubmitting || !formData.name || !formData.domain}
              className="px-5 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
              style={{
                background: isSubmitting || !formData.name || !formData.domain
                  ? 'var(--color-bg-card)'
                  : 'linear-gradient(135deg, var(--color-accent-primary) 0%, #2563eb 100%)',
                color: isSubmitting || !formData.name || !formData.domain
                  ? 'var(--color-text-muted)'
                  : 'white',
                cursor: isSubmitting || !formData.name || !formData.domain
                  ? 'not-allowed'
                  : 'pointer',
                boxShadow: isSubmitting || !formData.name || !formData.domain
                  ? 'none'
                  : '0 2px 8px rgba(59, 130, 246, 0.3)',
              }}
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner />
                  {status === 'creating' ? 'Creating...' : 'Researching...'}
                </>
              ) : (
                <>
                  <PlusIcon />
                  Create Account
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

function PlusIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
    </svg>
  );
}
