import { useState } from 'react';
import type { Account } from '../types';
import { API_BASE } from '../api/client';

interface Props {
  account: Account;
  contactsCount: number;
  onEnrichmentComplete?: () => void;
}

type EnrichmentStatus = 'idle' | 'loading' | 'success' | 'error';

interface EnrichmentResult {
  status: string;
  message: string;
  discovered?: number;
  saved?: number;
  contacts?: Array<{
    name: string;
    title: string;
    role_tier: string;
    champion_potential_level: string;
    lead_score: number;
  }>;
  summary?: {
    entry_points: number;
    middle_deciders: number;
    economic_buyers: number;
  };
}

export function EnrichmentButton({ account, contactsCount, onEnrichmentComplete }: Props) {
  const [status, setStatus] = useState<EnrichmentStatus>('idle');
  const [result, setResult] = useState<EnrichmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const hasContacts = contactsCount > 0;

  const handleEnrich = async () => {
    setStatus('loading');
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/accounts/${account.id}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force: false })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Enrichment failed');
      }

      setResult(data);
      setStatus('success');
      onEnrichmentComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  const handleRescore = async () => {
    setStatus('loading');
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/accounts/${account.id}/rescore`, {
        method: 'POST'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Rescoring failed');
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
            Contact Intelligence
          </h3>
          <p
            className="text-sm"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {hasContacts
              ? `${contactsCount} contacts found`
              : 'No contacts discovered yet'}
          </p>
        </div>

        <div className="flex gap-2">
          {!hasContacts && (
            <button
              onClick={handleEnrich}
              disabled={status === 'loading'}
              className="px-4 py-2 rounded-lg font-medium text-sm transition-all"
              style={{
                backgroundColor: status === 'loading'
                  ? 'var(--color-bg-card)'
                  : 'var(--color-accent-primary)',
                color: status === 'loading'
                  ? 'var(--color-text-muted)'
                  : 'white',
                opacity: status === 'loading' ? 0.7 : 1,
                cursor: status === 'loading' ? 'not-allowed' : 'pointer'
              }}
            >
              {status === 'loading' ? (
                <span className="flex items-center gap-2">
                  <LoadingSpinner />
                  Discovering...
                </span>
              ) : (
                'Discover Contacts'
              )}
            </button>
          )}

          {hasContacts && (
            <button
              onClick={handleRescore}
              disabled={status === 'loading'}
              className="px-4 py-2 rounded-lg font-medium text-sm transition-all"
              style={{
                backgroundColor: 'transparent',
                color: 'var(--color-accent-primary)',
                border: '1px solid var(--color-accent-primary)',
                opacity: status === 'loading' ? 0.7 : 1,
                cursor: status === 'loading' ? 'not-allowed' : 'pointer'
              }}
            >
              {status === 'loading' ? (
                <span className="flex items-center gap-2">
                  <LoadingSpinner />
                  Rescoring...
                </span>
              ) : (
                'Rescore MEDDIC'
              )}
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
      {status === 'success' && result && (
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
              {result.message}
            </span>
          </div>

          {/* MEDDIC Summary */}
          {result.summary && (
            <div className="grid grid-cols-3 gap-3">
              <MeddicTierCard
                label="Entry Points"
                count={result.summary.entry_points}
                tier="entry_point"
              />
              <MeddicTierCard
                label="Middle Deciders"
                count={result.summary.middle_deciders}
                tier="middle_decider"
              />
              <MeddicTierCard
                label="Economic Buyers"
                count={result.summary.economic_buyers}
                tier="economic_buyer"
              />
            </div>
          )}

          {/* Discovered Contacts Preview */}
          {result.contacts && result.contacts.length > 0 && (
            <div className="space-y-2">
              <p
                className="text-xs font-medium"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Top contacts discovered:
              </p>
              {result.contacts.slice(0, 5).map((contact, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded"
                  style={{ backgroundColor: 'var(--color-bg-card)' }}
                >
                  <div>
                    <p
                      className="text-sm font-medium"
                      style={{ color: 'var(--color-text-primary)' }}
                    >
                      {contact.name}
                    </p>
                    <p
                      className="text-xs"
                      style={{ color: 'var(--color-text-muted)' }}
                    >
                      {contact.title}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <RoleTierBadge tier={contact.role_tier} />
                    <ChampionBadge level={contact.champion_potential_level} />
                  </div>
                </div>
              ))}
            </div>
          )}
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

function MeddicTierCard({ label, count, tier }: { label: string; count: number; tier: string }) {
  const colors = {
    entry_point: 'var(--color-priority-high)',
    middle_decider: 'var(--color-priority-medium)',
    economic_buyer: 'var(--color-accent-primary)'
  };

  const color = colors[tier as keyof typeof colors] || 'var(--color-text-secondary)';

  return (
    <div
      className="p-3 rounded-lg text-center"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: `1px solid ${color}20`
      }}
    >
      <p
        className="text-2xl font-data font-semibold"
        style={{ color }}
      >
        {count}
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

function RoleTierBadge({ tier }: { tier: string }) {
  const config = {
    entry_point: { label: 'Entry', color: 'var(--color-priority-high)' },
    middle_decider: { label: 'Decider', color: 'var(--color-priority-medium)' },
    economic_buyer: { label: 'Buyer', color: 'var(--color-accent-primary)' }
  };

  const { label, color } = config[tier as keyof typeof config] || { label: tier, color: 'var(--color-text-muted)' };

  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-medium"
      style={{
        backgroundColor: `${color}15`,
        color,
        border: `1px solid ${color}30`
      }}
    >
      {label}
    </span>
  );
}

function ChampionBadge({ level }: { level: string }) {
  const config: Record<string, { bg: string; color: string }> = {
    'Very High': { bg: 'var(--color-priority-very-high-bg)', color: 'var(--color-priority-very-high)' },
    'High': { bg: 'var(--color-priority-high-bg)', color: 'var(--color-priority-high)' },
    'Medium': { bg: 'var(--color-priority-medium-bg)', color: 'var(--color-priority-medium)' },
    'Low': { bg: 'var(--color-priority-low-bg)', color: 'var(--color-priority-low)' }
  };

  const style = config[level] || { bg: 'var(--color-bg-card)', color: 'var(--color-text-muted)' };

  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-medium"
      style={{
        backgroundColor: style.bg,
        color: style.color
      }}
    >
      {level || 'N/A'}
    </span>
  );
}
