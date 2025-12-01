import { useState } from 'react';
import { api } from '../api/client';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onAccountCreated: (accountId: string, domain: string) => void;
}

type FormStatus = 'idle' | 'creating' | 'researching' | 'success' | 'error';

interface FormData {
  name: string;
  domain: string;
  industry: string;
  employee_count: string;
  business_model: string;
  physical_infrastructure: string;
}

const initialFormData: FormData = {
  name: '',
  domain: '',
  industry: '',
  employee_count: '',
  business_model: '',
  physical_infrastructure: '',
};

export function AddAccountModal({ isOpen, onClose, onAccountCreated }: Props) {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [status, setStatus] = useState<FormStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [autoResearch, setAutoResearch] = useState(true);
  const [progress, setProgress] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setStatus('creating');
    setProgress('Creating account in Notion...');

    try {
      // Prepare data for API
      const payload: Parameters<typeof api.createAccount>[0] = {
        name: formData.name.trim(),
        domain: formData.domain.trim(),
      };

      if (formData.industry) payload.industry = formData.industry;
      if (formData.employee_count) payload.employee_count = parseInt(formData.employee_count, 10);
      if (formData.business_model) payload.business_model = formData.business_model;
      if (formData.physical_infrastructure) payload.physical_infrastructure = formData.physical_infrastructure;

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
        }
      }

      setStatus('success');
      setProgress('');

      // Notify parent with the new account ID
      onAccountCreated(result.id, result.domain);

      // Reset form and close after brief success display
      setTimeout(() => {
        setFormData(initialFormData);
        setStatus('idle');
        onClose();
      }, 1500);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create account');
      setStatus('error');
      setProgress('');
    }
  };

  const handleClose = () => {
    if (status === 'creating' || status === 'researching') return; // Prevent close during operation
    setFormData(initialFormData);
    setStatus('idle');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  const isSubmitting = status === 'creating' || status === 'researching';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
      onClick={handleClose}
    >
      <div
        className="w-full max-w-lg mx-4 rounded-xl shadow-2xl animate-fade-in"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border-default)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
        >
          <div>
            <h2
              className="text-lg font-heading"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Add New Account
            </h2>
            <p
              className="text-sm"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Create a new account and run ABM research
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 rounded-lg transition-all"
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
              />
            </div>
          </div>

          {/* Optional Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Industry
              </label>
              <select
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                disabled={isSubmitting}
                className="input-field w-full"
              >
                <option value="">Select industry...</option>
                <option value="Technology">Technology</option>
                <option value="Cloud Infrastructure">Cloud Infrastructure</option>
                <option value="AI/ML">AI/ML</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Healthcare">Healthcare</option>
                <option value="E-commerce">E-commerce</option>
                <option value="Gaming">Gaming</option>
                <option value="Media & Entertainment">Media & Entertainment</option>
                <option value="Telecommunications">Telecommunications</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Employee Count
              </label>
              <input
                type="number"
                name="employee_count"
                value={formData.employee_count}
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="1000"
                min="1"
                className="input-field w-full"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Business Model
              </label>
              <select
                name="business_model"
                value={formData.business_model}
                onChange={handleChange}
                disabled={isSubmitting}
                className="input-field w-full"
              >
                <option value="">Select model...</option>
                <option value="SaaS">SaaS</option>
                <option value="Enterprise">Enterprise</option>
                <option value="B2B">B2B</option>
                <option value="B2C">B2C</option>
                <option value="Marketplace">Marketplace</option>
                <option value="Platform">Platform</option>
                <option value="Hardware">Hardware</option>
                <option value="Hybrid">Hybrid</option>
              </select>
            </div>
            <div>
              <label
                className="block text-sm font-medium mb-1.5"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Physical Infrastructure
              </label>
              <select
                name="physical_infrastructure"
                value={formData.physical_infrastructure}
                onChange={handleChange}
                disabled={isSubmitting}
                className="input-field w-full"
              >
                <option value="">Select type...</option>
                <option value="GPU Clusters">GPU Clusters</option>
                <option value="Data Centers">Data Centers</option>
                <option value="Cloud-Native">Cloud-Native</option>
                <option value="Hybrid Cloud">Hybrid Cloud</option>
                <option value="Edge Computing">Edge Computing</option>
                <option value="On-Premise">On-Premise</option>
                <option value="Unknown">Unknown</option>
              </select>
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

          {/* Success Message */}
          {status === 'success' && (
            <div
              className="p-3 rounded-lg animate-fade-in"
              style={{
                backgroundColor: 'var(--color-priority-high-bg)',
                border: '1px solid var(--color-priority-high-border)',
              }}
            >
              <div className="flex items-center gap-2">
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
                  Account created successfully!
                </p>
              </div>
            </div>
          )}

          {/* Actions */}
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
        </form>
      </div>
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
