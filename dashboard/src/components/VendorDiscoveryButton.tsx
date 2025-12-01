import { useState } from 'react';
import type { Account } from '../types';
import { API_BASE } from '../api/client';

interface Props {
  account: Account;
  onDiscoveryComplete?: () => void;
}

type DiscoveryStatus = 'idle' | 'loading' | 'success' | 'error';

interface DiscoveredVendor {
  vendor_name: string;
  category: string;
  confidence: number;
  mention_count: number;
  relationship_type: string;
  strategic_purpose: string;
  evidence_snippets: string[];
  is_new: boolean;
}

interface DiscoveryResult {
  status: string;
  account_name: string;
  workflow: string;
  new_vendors_count: number;
  saved_to_notion: number;
  known_vendors_found: number;
  known_vendors_detail: string[];
  search_results_analyzed: number;
  cost_estimate: string;
  category_summary: Record<string, number>;
  discovered_vendors: DiscoveredVendor[];
}

export function VendorDiscoveryButton({ account, onDiscoveryComplete }: Props) {
  const [status, setStatus] = useState<DiscoveryStatus>('idle');
  const [result, setResult] = useState<DiscoveryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');

  const handleDiscoverVendors = async () => {
    setStatus('loading');
    setError(null);
    setResult(null);
    setProgress('Searching for vendors...');

    try {
      // Simulate progress updates
      const progressSteps = [
        'Searching news and web for vendor mentions...',
        'Analyzing partnerships and collaborations...',
        'Extracting vendor names with AI...',
        'Categorizing discovered vendors...',
        'Saving to Notion...'
      ];

      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
          setProgress(progressSteps[stepIndex]);
          stepIndex++;
        }
      }, 3000);

      const response = await fetch(`${API_BASE}/accounts/${account.id}/discover-unknown-vendors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          save_to_notion: true,
          min_confidence: 0.6
        })
      });

      clearInterval(progressInterval);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Vendor discovery failed');
      }

      setResult(data);
      setStatus('success');
      setProgress('');
      onDiscoveryComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
      setProgress('');
    }
  };

  // Category badge colors
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'competitor':
        return { color: 'var(--color-priority-low)', bg: 'var(--color-priority-low-bg)' };
      case 'complementary_compute':
      case 'complementary_networking':
        return { color: 'var(--color-priority-high)', bg: 'var(--color-priority-high-bg)' };
      case 'channel':
        return { color: 'var(--color-priority-very-high)', bg: 'var(--color-priority-very-high-bg)' };
      default:
        return { color: 'var(--color-text-secondary)', bg: 'var(--color-bg-card)' };
    }
  };

  return (
    <div className="card-surface p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3
            className="text-base font-heading flex items-center gap-2"
            style={{ color: 'var(--color-text-primary)' }}
          >
            <VendorIcon />
            Vendor Discovery
          </h3>
          <p
            className="text-sm"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            Find new vendor relationships using AI-powered search
          </p>
        </div>

        <button
          onClick={handleDiscoverVendors}
          disabled={status === 'loading'}
          className="px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
          style={{
            background: status === 'loading'
              ? 'var(--color-bg-card)'
              : 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
            color: status === 'loading'
              ? 'var(--color-text-muted)'
              : 'white',
            opacity: status === 'loading' ? 0.8 : 1,
            cursor: status === 'loading' ? 'not-allowed' : 'pointer',
            boxShadow: status === 'loading' ? 'none' : '0 2px 8px rgba(139, 92, 246, 0.3)'
          }}
        >
          {status === 'loading' ? (
            <>
              <LoadingSpinner />
              Discovering...
            </>
          ) : (
            <>
              <SearchIcon />
              Discover Vendors
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
              style={{ backgroundColor: '#8b5cf6' }}
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
              Discovered {result.new_vendors_count} new vendors
            </span>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-2">
            <StatCard
              label="New Vendors"
              value={result.new_vendors_count}
              highlight={result.new_vendors_count > 0}
            />
            <StatCard
              label="Saved to Notion"
              value={result.saved_to_notion}
              highlight={result.saved_to_notion > 0}
            />
            <StatCard
              label="Known Found"
              value={result.known_vendors_found}
              highlight={false}
            />
            <StatCard
              label="Analyzed"
              value={result.search_results_analyzed}
              highlight={false}
            />
          </div>

          {/* Category Breakdown */}
          {result.category_summary && Object.keys(result.category_summary).length > 0 && (
            <div>
              <p
                className="text-xs font-medium mb-2"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Categories
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(result.category_summary).map(([cat, count]) => (
                  count > 0 && (
                    <span
                      key={cat}
                      className="px-2 py-0.5 rounded text-xs font-medium"
                      style={{
                        color: getCategoryColor(cat).color,
                        backgroundColor: getCategoryColor(cat).bg,
                      }}
                    >
                      {cat.replace(/_/g, ' ')}: {count}
                    </span>
                  )
                ))}
              </div>
            </div>
          )}

          {/* Top Discovered Vendors */}
          {result.discovered_vendors && result.discovered_vendors.length > 0 && (
            <div>
              <p
                className="text-xs font-medium mb-2"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Top Vendors Discovered
              </p>
              <div className="space-y-2">
                {result.discovered_vendors.slice(0, 5).map((vendor, idx) => (
                  <VendorCard key={idx} vendor={vendor} getCategoryColor={getCategoryColor} />
                ))}
              </div>
            </div>
          )}

          {/* Cost Estimate */}
          {result.cost_estimate && (
            <p
              className="text-xs"
              style={{ color: 'var(--color-text-muted)' }}
            >
              API Cost: {result.cost_estimate}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// Sub-components

function VendorCard({
  vendor,
  getCategoryColor,
}: {
  vendor: DiscoveredVendor;
  getCategoryColor: (cat: string) => { color: string; bg: string };
}) {
  const colors = getCategoryColor(vendor.category);

  return (
    <div
      className="p-2 rounded-lg flex items-center justify-between"
      style={{ backgroundColor: 'var(--color-bg-card)' }}
    >
      <div className="flex items-center gap-2">
        <span
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: colors.color }}
        />
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {vendor.vendor_name}
        </span>
        <span
          className="px-1.5 py-0.5 rounded text-xs"
          style={{
            color: colors.color,
            backgroundColor: colors.bg,
          }}
        >
          {vendor.category.replace(/_/g, ' ')}
        </span>
      </div>
      <span
        className="text-xs font-data"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {Math.round(vendor.confidence * 100)}% conf
      </span>
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: number; highlight: boolean }) {
  return (
    <div
      className="p-2 rounded-lg text-center"
      style={{
        backgroundColor: highlight ? 'rgba(139, 92, 246, 0.1)' : 'var(--color-bg-card)',
        border: highlight ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid var(--color-border-subtle)'
      }}
    >
      <p
        className="text-lg font-data font-semibold"
        style={{ color: highlight ? '#8b5cf6' : 'var(--color-text-secondary)' }}
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
    <div
      className="mt-3 h-1.5 rounded-full overflow-hidden"
      style={{ backgroundColor: 'var(--color-bg-card)' }}
    >
      <div
        className="h-full animate-pulse"
        style={{
          width: '60%',
          background: 'linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%)',
          animation: 'progress-indeterminate 1.5s infinite ease-in-out'
        }}
      />
    </div>
  );
}

// Icons

function VendorIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
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
