import { useState } from 'react';
import type { Account } from '../types';
import { API_BASE } from '../api/client';

interface Props {
  account: Account;
  onEnrichmentComplete?: () => void;
}

type EnrichmentStatus = 'idle' | 'loading' | 'success' | 'error';

interface EnrichmentResult {
  status: string;
  account_name: string;
  enrichment_results?: {
    industry: string;
    physical_infrastructure: string;
    icp_fit_score: number;
    reasoning: string;
  };
  search_results_analyzed: number;
  duration_seconds: number;
  notion_updated: boolean;
  error?: string;
}

export function AccountFieldEnrichmentButton({ account, onEnrichmentComplete }: Props) {
  const [status, setStatus] = useState<EnrichmentStatus>('idle');
  const [result, setResult] = useState<EnrichmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check if account already has enriched fields
  const hasIndustry = account.industry && account.industry !== 'Unknown';
  const hasIcpScore = account.icp_fit_score && account.icp_fit_score > 0;
  const isEnriched = hasIndustry && hasIcpScore;

  const handleEnrich = async (force: boolean = false) => {
    setStatus('loading');
    setError(null);
    setResult(null);

    try {
      // Use notion_id if available, otherwise fall back to id
      const accountId = account.notion_id || account.id;

      const response = await fetch(`${API_BASE}/accounts/${accountId}/enrich-fields`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Enrichment failed');
      }

      setResult(data);
      setStatus('success');
      onEnrichmentComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  return (
    <div className="card-surface p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3
            className="text-base font-heading"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Account Field Enrichment
          </h3>
          <p
            className="text-sm"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {isEnriched
              ? `Industry: ${account.industry} | ICP Score: ${account.icp_fit_score}`
              : 'Populate Industry, Infrastructure & ICP Score'}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => handleEnrich(false)}
            disabled={status === 'loading'}
            className="px-4 py-2 rounded-lg font-medium text-sm transition-all"
            style={{
              backgroundColor: status === 'loading'
                ? 'var(--color-bg-card)'
                : isEnriched
                  ? 'transparent'
                  : 'var(--color-accent-primary)',
              color: status === 'loading'
                ? 'var(--color-text-muted)'
                : isEnriched
                  ? 'var(--color-accent-primary)'
                  : 'white',
              border: isEnriched ? '1px solid var(--color-accent-primary)' : 'none',
              opacity: status === 'loading' ? 0.7 : 1,
              cursor: status === 'loading' ? 'not-allowed' : 'pointer'
            }}
          >
            {status === 'loading' ? (
              <span className="flex items-center gap-2">
                <LoadingSpinner />
                Enriching...
              </span>
            ) : isEnriched ? (
              'Re-enrich Fields'
            ) : (
              'Enrich Account Fields'
            )}
          </button>

          {isEnriched && (
            <button
              onClick={() => handleEnrich(true)}
              disabled={status === 'loading'}
              className="px-3 py-2 rounded-lg font-medium text-xs transition-all"
              style={{
                backgroundColor: 'transparent',
                color: 'var(--color-text-muted)',
                border: '1px solid var(--color-border-default)',
                opacity: status === 'loading' ? 0.5 : 1,
                cursor: status === 'loading' ? 'not-allowed' : 'pointer'
              }}
              title="Force refresh even if recently enriched"
            >
              Force Refresh
            </button>
          )}
        </div>
      </div>

      {/* Error State */}
      {status === 'error' && error && (
        <div
          className="p-3 rounded-lg"
          style={{
            backgroundColor: 'var(--color-priority-low-bg)',
            border: '1px solid var(--color-priority-low-border)'
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

      {/* Success Result */}
      {status === 'success' && result && result.enrichment_results && (
        <div
          className="p-4 rounded-lg space-y-3 animate-fade-in"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-default)'
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
            <span
              className="text-sm font-medium"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Enrichment Complete
            </span>
          </div>

          {/* Enrichment Results */}
          <div className="grid grid-cols-3 gap-3">
            <EnrichmentCard
              label="Industry"
              value={result.enrichment_results.industry}
              icon="building"
            />
            <EnrichmentCard
              label="ICP Fit Score"
              value={result.enrichment_results.icp_fit_score.toString()}
              icon="chart"
              highlight={result.enrichment_results.icp_fit_score >= 75}
            />
            <EnrichmentCard
              label="Sources Analyzed"
              value={result.search_results_analyzed.toString()}
              icon="search"
            />
          </div>

          {/* Infrastructure Summary */}
          {result.enrichment_results.physical_infrastructure && (
            <div
              className="p-3 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-card)' }}
            >
              <p
                className="text-xs font-medium mb-1"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Physical Infrastructure
              </p>
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {result.enrichment_results.physical_infrastructure.length > 200
                  ? result.enrichment_results.physical_infrastructure.substring(0, 200) + '...'
                  : result.enrichment_results.physical_infrastructure}
              </p>
            </div>
          )}

          {/* Reasoning */}
          {result.enrichment_results.reasoning && (
            <div
              className="p-3 rounded-lg"
              style={{ backgroundColor: 'var(--color-bg-card)' }}
            >
              <p
                className="text-xs font-medium mb-1"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                ICP Score Reasoning
              </p>
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-muted)' }}
              >
                {result.enrichment_results.reasoning}
              </p>
            </div>
          )}

          {/* Meta info */}
          <div className="flex items-center justify-between text-xs" style={{ color: 'var(--color-text-muted)' }}>
            <span>Duration: {result.duration_seconds.toFixed(1)}s</span>
            <span>{result.notion_updated ? 'Saved to Notion' : 'Preview only'}</span>
          </div>
        </div>
      )}
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

function EnrichmentCard({
  label,
  value,
  icon,
  highlight = false
}: {
  label: string;
  value: string;
  icon: 'building' | 'chart' | 'search';
  highlight?: boolean;
}) {
  const iconPaths = {
    building: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    chart: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
  };

  return (
    <div
      className="p-3 rounded-lg text-center"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: highlight ? '1px solid var(--color-priority-high)' : '1px solid var(--color-border-subtle)'
      }}
    >
      <svg
        className="w-5 h-5 mx-auto mb-1"
        style={{ color: highlight ? 'var(--color-priority-high)' : 'var(--color-text-muted)' }}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d={iconPaths[icon]} />
      </svg>
      <p
        className="text-lg font-data font-semibold"
        style={{ color: highlight ? 'var(--color-priority-high)' : 'var(--color-text-primary)' }}
      >
        {value}
      </p>
      <p
        className="text-xs"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {label}
      </p>
    </div>
  );
}
