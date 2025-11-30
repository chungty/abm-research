import { useState } from 'react';
import type { Account } from '../types';
import { API_BASE } from '../api/client';

interface Props {
  account: Account;
  onResearchComplete?: () => void;
}

type ResearchStatus = 'idle' | 'loading' | 'success' | 'error';

interface ResearchResult {
  status: string;
  message: string;
  account_id: string;
  account_data?: {
    name: string;
    employee_count?: number;
    business_model?: string;
    industry?: string;
    icp_fit_score?: number;
    account_score?: number;
    infrastructure_score?: number;
    buying_signals_score?: number;
    partnership_classification?: string;
  };
  research_summary?: {
    contacts_discovered: number;
    high_priority_contacts: number;
    trigger_events_found: number;
    partnerships_identified: number;
    research_duration_seconds: number;
  };
  notion_sync?: {
    account_saved: boolean;
    contacts_saved?: number;
    events_saved?: number;
    partnerships_saved?: number;
  };
}

export function ResearchButton({ account, onResearchComplete }: Props) {
  const [status, setStatus] = useState<ResearchStatus>('idle');
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');

  const handleRunResearch = async () => {
    setStatus('loading');
    setError(null);
    setResult(null);
    setProgress('Initializing research pipeline...');

    try {
      // Simulate progress updates
      const progressSteps = [
        'Phase 1: Gathering account intelligence...',
        'Phase 2: Discovering contacts...',
        'Phase 3: Enriching data...',
        'Phase 4: Analyzing engagement signals...',
        'Phase 5: Identifying partnership opportunities...',
        'Syncing to Notion...'
      ];

      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
          setProgress(progressSteps[stepIndex]);
          stepIndex++;
        }
      }, 2000);

      const response = await fetch(`${API_BASE}/accounts/${account.id}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force: false })
      });

      clearInterval(progressInterval);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Research failed');
      }

      setResult(data);
      setStatus('success');
      setProgress('');
      onResearchComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
      setProgress('');
    }
  };

  // Check if account has been researched by looking at reliable indicators:
  // 1. Has infrastructure breakdown with any detected items
  // 2. Has a meaningful account score (above baseline)
  // 3. Has business model populated
  const hasInfrastructureData = Boolean(
    account.infrastructure_breakdown?.breakdown &&
    Object.values(account.infrastructure_breakdown.breakdown).some(
      cat => cat?.detected?.length > 0
    )
  );
  const hasBeenResearched = Boolean(
    hasInfrastructureData ||
    account.account_score > 50 ||  // Above baseline score indicates research
    (account.business_model && account.business_model !== 'Unknown')
  );

  return (
    <div className="card-surface p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3
            className="text-base font-heading flex items-center gap-2"
            style={{ color: 'var(--color-text-primary)' }}
          >
            <ResearchIcon />
            Deep Research
          </h3>
          <p
            className="text-sm"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {hasBeenResearched
              ? 'Account has been researched — run again to refresh data'
              : 'Run comprehensive 5-phase ABM research'
            }
          </p>
        </div>

        <button
          onClick={handleRunResearch}
          disabled={status === 'loading'}
          className="px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
          style={{
            background: status === 'loading'
              ? 'var(--color-bg-card)'
              : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: status === 'loading'
              ? 'var(--color-text-muted)'
              : 'white',
            opacity: status === 'loading' ? 0.8 : 1,
            cursor: status === 'loading' ? 'not-allowed' : 'pointer',
            boxShadow: status === 'loading' ? 'none' : '0 2px 8px rgba(16, 185, 129, 0.3)'
          }}
        >
          {status === 'loading' ? (
            <>
              <LoadingSpinner />
              Researching...
            </>
          ) : (
            <>
              <SearchIcon />
              {hasBeenResearched ? 'Re-Research' : 'Run Research'}
            </>
          )}
        </button>
      </div>

      {/* Progress State */}
      {status === 'loading' && progress && (
        <div
          className="p-3 rounded-lg"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-default)'
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: 'var(--color-accent-primary)' }}
            />
            <p
              className="text-sm"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {progress}
            </p>
          </div>
          <ProgressBar />
        </div>
      )}

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
      {status === 'success' && result && (
        <div
          className="p-4 rounded-lg space-y-4 animate-fade-in"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-default)'
          }}
        >
          {/* Success Header */}
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
              {result.message}
            </span>
          </div>

          {/* Account Data Grid */}
          {(result.account_data || result.research_summary) && (
            <div className="grid grid-cols-2 gap-3">
              {/* Company Size */}
              <ResearchCard
                icon={<UsersIcon />}
                label="Company Size"
                value={result.account_data?.employee_count
                  ? `${result.account_data.employee_count.toLocaleString()} employees`
                  : 'Unknown'}
              />

              {/* Industry */}
              <ResearchCard
                icon={<GlobeIcon />}
                label="Industry"
                value={result.account_data?.industry || 'Unknown'}
              />

              {/* Business Model */}
              <ResearchCard
                icon={<BuildingIcon />}
                label="Business Model"
                value={result.account_data?.business_model || 'Unknown'}
              />

              {/* ICP Fit Score */}
              <ResearchCard
                icon={<ScoreIcon />}
                label="ICP Fit Score"
                value={result.account_data?.icp_fit_score?.toString() || 'N/A'}
              />
            </div>
          )}

          {/* Research Discovery Stats */}
          {result.research_summary && (
            <div>
              <p
                className="text-xs font-medium mb-2"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Research Discovery Summary
              </p>
              <div className="grid grid-cols-4 gap-2">
                <StatCard
                  label="Contacts"
                  value={result.research_summary.contacts_discovered}
                  highlight={result.research_summary.contacts_discovered > 0}
                />
                <StatCard
                  label="High Priority"
                  value={result.research_summary.high_priority_contacts}
                  highlight={result.research_summary.high_priority_contacts > 0}
                />
                <StatCard
                  label="Triggers"
                  value={result.research_summary.trigger_events_found}
                  highlight={result.research_summary.trigger_events_found > 0}
                />
                <StatCard
                  label="Partners"
                  value={result.research_summary.partnerships_identified}
                  highlight={result.research_summary.partnerships_identified > 0}
                />
              </div>
              {result.research_summary.research_duration_seconds && (
                <p
                  className="text-xs mt-2"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Completed in {result.research_summary.research_duration_seconds.toFixed(2)}s
                </p>
              )}
            </div>
          )}

          {/* Partnership Classification */}
          {result.account_data?.partnership_classification && (
            <div className="flex items-center gap-2">
              <span
                className="text-xs"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Partnership Classification:
              </span>
              <span
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  color: 'var(--color-priority-high)',
                  backgroundColor: 'var(--color-priority-high-bg)',
                  border: '1px solid var(--color-priority-high-border)'
                }}
              >
                {result.account_data.partnership_classification}
              </span>
            </div>
          )}

          {/* Notion Sync Summary */}
          {result.notion_sync && (
            <div
              className="pt-3 mt-3"
              style={{ borderTop: '1px solid var(--color-border-subtle)' }}
            >
              <p
                className="text-xs font-medium mb-2"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Synced to Notion
              </p>
              <div className="flex flex-wrap gap-3">
                {result.notion_sync.account_saved && (
                  <NotionSyncBadge label="Account Saved" />
                )}
                {(result.notion_sync.contacts_saved ?? 0) > 0 && (
                  <NotionSyncBadge label={`${result.notion_sync.contacts_saved} Contacts`} />
                )}
                {(result.notion_sync.events_saved ?? 0) > 0 && (
                  <NotionSyncBadge label={`${result.notion_sync.events_saved} Events`} />
                )}
                {(result.notion_sync.partnerships_saved ?? 0) > 0 && (
                  <NotionSyncBadge label={`${result.notion_sync.partnerships_saved} Partnerships`} />
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Sub-components

function ResearchCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div
      className="p-3 rounded-lg flex items-center gap-3"
      style={{ backgroundColor: 'var(--color-bg-card)' }}
    >
      <div style={{ color: 'var(--color-text-muted)' }}>
        {icon}
      </div>
      <div>
        <p
          className="text-xs"
          style={{ color: 'var(--color-text-muted)' }}
        >
          {label}
        </p>
        <p
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {value}
        </p>
      </div>
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: number; highlight: boolean }) {
  return (
    <div
      className="p-2 rounded-lg text-center"
      style={{
        backgroundColor: highlight ? 'var(--color-priority-high-bg)' : 'var(--color-bg-card)',
        border: highlight ? '1px solid var(--color-priority-high-border)' : '1px solid var(--color-border-subtle)'
      }}
    >
      <p
        className="text-lg font-data font-semibold"
        style={{ color: highlight ? 'var(--color-priority-high)' : 'var(--color-text-secondary)' }}
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

function NotionSyncBadge({ label }: { label: string }) {
  return (
    <span
      className="px-2 py-0.5 rounded text-xs flex items-center gap-1"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        color: 'var(--color-text-muted)'
      }}
    >
      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
        <path d="M4 4.5a.5.5 0 0 1 .5-.5H8a.5.5 0 0 1 0 1H4.5v14H18v-3.5a.5.5 0 0 1 1 0v4a.5.5 0 0 1-.5.5H4a.5.5 0 0 1-.5-.5v-15z"/>
        <path d="M19.354 4.354a.5.5 0 0 0-.708-.708L9.5 12.793V15.5h2.707l9.147-9.146z"/>
      </svg>
      {label}
    </span>
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

function ProgressBar() {
  return (
    <div className="mt-3 h-1.5 progress-bar-animated" />
  );
}

// Icons

function ResearchIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );
}

function GlobeIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function BuildingIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );
}

function ScoreIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}
