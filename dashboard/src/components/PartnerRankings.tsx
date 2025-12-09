import { useState } from 'react';
import { usePartnerRankings } from '../api/client';
import type { RankedPartner, PartnerMatchedAccount, ScoringMethodology } from '../types';

export function PartnerRankings() {
  const { rankings, total, totalAccounts, methodology, loading, error } = usePartnerRankings();
  const [expandedPartner, setExpandedPartner] = useState<string | null>(null);
  const [showMethodology, setShowMethodology] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div
          className="animate-spin rounded-full h-8 w-8 border-2"
          style={{
            borderColor: 'var(--color-border-default)',
            borderTopColor: 'var(--color-accent-primary)'
          }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6" style={{ color: 'var(--color-target-hot)' }}>
        <p className="font-medium">Error loading partner rankings</p>
        <p className="text-sm opacity-80">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2
            className="text-lg font-semibold flex items-center gap-2"
            style={{ color: 'var(--color-text-primary)' }}
          >
            <TrophyIcon />
            Partner Rankings
            <span
              className="text-sm font-normal font-data"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              ({total} partners)
            </span>
          </h2>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--color-text-muted)' }}
          >
            Strategic partners ranked by potential to unlock ICP accounts ({totalAccounts} accounts analyzed)
          </p>
        </div>
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="text-xs px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5"
          style={{
            backgroundColor: showMethodology ? 'var(--color-accent-primary-muted)' : 'var(--color-bg-card)',
            color: showMethodology ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
            border: `1px solid ${showMethodology ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}`
          }}
        >
          <InfoIcon />
          Scoring
        </button>
      </div>

      {/* Methodology Panel */}
      {showMethodology && methodology && (
        <MethodologyPanel methodology={methodology} />
      )}

      {/* Rankings List */}
      {rankings.length === 0 ? (
        <EmptyRankings />
      ) : (
        <div className="space-y-3">
          {rankings.map((partner, index) => (
            <PartnerRankCard
              key={partner.partner_id}
              partner={partner}
              rank={index + 1}
              expanded={expandedPartner === partner.partner_id}
              onToggle={() => setExpandedPartner(
                expandedPartner === partner.partner_id ? null : partner.partner_id
              )}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function MethodologyPanel({ methodology }: { methodology: ScoringMethodology }) {
  const dimensions = [
    { key: 'account_reach', label: 'Account Reach', icon: <NetworkIcon />, color: 'var(--color-priority-very-high)' },
    { key: 'icp_alignment', label: 'ICP Alignment', icon: <TargetIcon />, color: 'var(--color-priority-high)' },
    { key: 'entry_point_quality', label: 'Entry Point', icon: <DoorIcon />, color: 'var(--color-priority-medium)' },
    { key: 'trust_evidence', label: 'Trust Evidence', icon: <ShieldIcon />, color: 'var(--color-infra-power)' },
  ];

  return (
    <div
      className="p-4 rounded-lg animate-fade-in"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border-default)'
      }}
    >
      <h3
        className="text-sm font-medium mb-3"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        Partner Scoring Methodology
      </h3>
      <div className="grid grid-cols-2 gap-3">
        {dimensions.map(dim => {
          const data = methodology[dim.key as keyof ScoringMethodology];
          return (
            <div
              key={dim.key}
              className="p-3 rounded-lg"
              style={{
                backgroundColor: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border-subtle)'
              }}
            >
              <div className="flex items-center gap-2 mb-1">
                <span style={{ color: dim.color }}>{dim.icon}</span>
                <span
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {dim.label}
                </span>
                <span
                  className="ml-auto text-xs font-data px-1.5 py-0.5 rounded"
                  style={{
                    backgroundColor: `${dim.color}15`,
                    color: dim.color
                  }}
                >
                  {data.weight}
                </span>
              </div>
              <p
                className="text-xs leading-relaxed"
                style={{ color: 'var(--color-text-muted)' }}
              >
                {data.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PartnerRankCard({
  partner,
  rank,
  expanded,
  onToggle
}: {
  partner: RankedPartner;
  rank: number;
  expanded: boolean;
  onToggle: () => void;
}) {
  const scoreColor = getScoreColor(partner.partner_score);
  const breakdown = partner.score_breakdown;

  return (
    <div
      className="rounded-lg overflow-hidden transition-all"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: `1px solid ${expanded ? 'var(--color-accent-primary)' : 'var(--color-border-default)'}`
      }}
    >
      {/* Main Card */}
      <button
        className="w-full p-4 cursor-pointer hover:bg-opacity-50 transition-colors text-left"
        onClick={onToggle}
        aria-expanded={expanded}
        aria-label={`${partner.partner_name} - Score ${partner.partner_score.toFixed(1)}. Click to ${expanded ? 'collapse' : 'expand'} details.`}
        style={{
          backgroundColor: expanded ? 'var(--color-accent-primary-muted)' : 'transparent'
        }}
      >
        <div className="flex items-start gap-4">
          {/* Rank Badge */}
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center font-heading text-lg flex-shrink-0"
            style={{
              backgroundColor: rank <= 3 ? `${scoreColor}15` : 'var(--color-bg-elevated)',
              color: rank <= 3 ? scoreColor : 'var(--color-text-muted)',
              border: `1px solid ${rank <= 3 ? `${scoreColor}30` : 'var(--color-border-subtle)'}`
            }}
          >
            #{rank}
          </div>

          {/* Partner Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <h3
                  className="font-medium"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {partner.partner_name}
                </h3>
                <div className="flex items-center gap-2 mt-0.5">
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: 'var(--color-bg-elevated)',
                      color: 'var(--color-text-tertiary)',
                      border: '1px solid var(--color-border-subtle)'
                    }}
                  >
                    {partner.partnership_type || 'Unknown Type'}
                  </span>
                  {partner.account_coverage > 0 && (
                    <span
                      className="text-xs"
                      style={{ color: 'var(--color-text-muted)' }}
                    >
                      {partner.account_coverage} reachable accounts
                    </span>
                  )}
                </div>
              </div>

              {/* Score */}
              <div className="text-right flex-shrink-0">
                <div
                  className="text-2xl font-heading tabular-nums"
                  style={{ color: scoreColor }}
                >
                  {partner.partner_score.toFixed(1)}
                </div>
                <div
                  className="text-xs"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Partner Score
                </div>
              </div>
            </div>

            {/* Score Breakdown Bar */}
            <div className="mt-3">
              <ScoreBreakdownBar breakdown={breakdown} />
            </div>
          </div>

          {/* Expand Arrow */}
          <div
            className="w-6 h-6 flex items-center justify-center flex-shrink-0 transition-transform"
            style={{
              color: 'var(--color-text-muted)',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)'
            }}
            aria-hidden="true"
          >
            <ChevronDownIcon />
          </div>
        </div>
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div
          className="px-4 pb-4 pt-2 animate-fade-in"
          style={{ borderTop: '1px solid var(--color-border-subtle)' }}
        >
          {/* Score Detail Grid */}
          <div className="grid grid-cols-4 gap-3 mb-4">
            <ScoreDimensionCard
              label="Account Reach"
              score={breakdown.account_reach.score}
              contribution={breakdown.account_reach.contribution}
              details={`${breakdown.account_reach.matched_count} matched (${(breakdown.account_reach.icp_account_ratio * 100).toFixed(0)}% of ICP)`}
              color="var(--color-priority-very-high)"
            />
            <ScoreDimensionCard
              label="ICP Alignment"
              score={breakdown.icp_alignment.score}
              contribution={breakdown.icp_alignment.contribution}
              details={breakdown.icp_alignment.tech_category || 'No category'}
              color="var(--color-priority-high)"
            />
            <ScoreDimensionCard
              label="Entry Point"
              score={breakdown.entry_point_quality.score}
              contribution={breakdown.entry_point_quality.contribution}
              details={breakdown.entry_point_quality.effectiveness_tier || 'Unknown'}
              color="var(--color-priority-medium)"
            />
            <ScoreDimensionCard
              label="Trust Evidence"
              score={breakdown.trust_evidence.score}
              contribution={breakdown.trust_evidence.contribution}
              details={`${breakdown.trust_evidence.signals_detected?.length || 0} signals`}
              color="var(--color-infra-power)"
            />
          </div>

          {/* Matched Accounts */}
          {partner.matched_accounts && partner.matched_accounts.length > 0 && (
            <MatchedAccountsList accounts={partner.matched_accounts} />
          )}

          {/* Partnership Context */}
          {partner.partnership_data?.context && (
            <div
              className="mt-3 p-3 rounded-lg"
              style={{
                backgroundColor: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border-subtle)'
              }}
            >
              <div
                className="text-xs font-medium mb-1"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Partnership Context
              </div>
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {partner.partnership_data.context}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ScoreBreakdownBar({ breakdown }: { breakdown: RankedPartner['score_breakdown'] }) {
  const segments = [
    { value: breakdown.account_reach.contribution, color: 'var(--color-priority-very-high)', label: 'Reach' },
    { value: breakdown.icp_alignment.contribution, color: 'var(--color-priority-high)', label: 'ICP' },
    { value: breakdown.entry_point_quality.contribution, color: 'var(--color-priority-medium)', label: 'Entry' },
    { value: breakdown.trust_evidence.contribution, color: 'var(--color-infra-power)', label: 'Trust' },
  ];

  const total = segments.reduce((sum, s) => sum + s.value, 0) || 1;

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 rounded-full overflow-hidden flex" style={{ backgroundColor: 'var(--color-bg-elevated)' }}>
        {segments.map((segment, i) => (
          <div
            key={i}
            className="h-full transition-all"
            style={{
              width: `${(segment.value / total) * 100}%`,
              backgroundColor: segment.color,
              opacity: segment.value > 0 ? 1 : 0.3
            }}
            title={`${segment.label}: ${segment.value.toFixed(1)}`}
          />
        ))}
      </div>
      <div className="flex gap-1.5">
        {segments.map((segment, i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: segment.color, opacity: segment.value > 0 ? 1 : 0.3 }}
            title={segment.label}
          />
        ))}
      </div>
    </div>
  );
}

function ScoreDimensionCard({
  label,
  score,
  contribution,
  details,
  color
}: {
  label: string;
  score: number;
  contribution: number;
  details: string;
  color: string;
}) {
  const isZero = score === 0;
  const isMissingData = details === 'No category' || details === 'Unknown' || details === '0 signals';

  return (
    <div
      className="p-2 rounded-lg text-center relative"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        border: `1px solid ${isMissingData ? 'var(--color-priority-medium-border)' : 'var(--color-border-subtle)'}`
      }}
      title={isMissingData ? `${label}: Score may be low due to missing data. Add more context in Notion.` : undefined}
    >
      {isMissingData && (
        <div
          className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center"
          style={{
            backgroundColor: 'var(--color-priority-medium-bg)',
            color: 'var(--color-priority-medium)',
            fontSize: '10px',
            border: '1px solid var(--color-priority-medium-border)',
          }}
          title="Missing data - score may be inaccurate"
        >
          !
        </div>
      )}
      <div
        className="text-lg font-heading tabular-nums"
        style={{ color: isZero ? 'var(--color-text-muted)' : color }}
      >
        {isZero ? '—' : score.toFixed(0)}
      </div>
      <div
        className="text-xs font-medium"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {label}
      </div>
      <div
        className="text-xs mt-0.5"
        style={{ color: 'var(--color-text-muted)' }}
      >
        +{contribution.toFixed(1)} pts
      </div>
      <div
        className="text-xs mt-1 truncate"
        style={{ color: isMissingData ? 'var(--color-priority-medium)' : 'var(--color-text-tertiary)' }}
        title={details}
      >
        {isMissingData ? '⚠️ ' : ''}{details}
      </div>
    </div>
  );
}

function MatchedAccountsList({ accounts }: { accounts: PartnerMatchedAccount[] }) {
  const [showAll, setShowAll] = useState(false);
  const displayedAccounts = showAll ? accounts : accounts.slice(0, 3);

  return (
    <div>
      <div
        className="text-xs font-medium mb-2"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        Reachable ICP Accounts ({accounts.length})
      </div>
      <div className="space-y-2">
        {displayedAccounts.map(account => (
          <div
            key={account.id}
            className="flex items-center justify-between p-2 rounded-lg"
            style={{
              backgroundColor: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border-subtle)'
            }}
          >
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: getPriorityColor(account.priority_level) }}
              />
              <span
                className="text-sm font-medium"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {account.name}
              </span>
              <span
                className="text-xs px-1.5 py-0.5 rounded"
                style={{
                  backgroundColor: 'var(--color-bg-card)',
                  color: 'var(--color-text-muted)'
                }}
              >
                Score: {account.account_score}
              </span>
            </div>
            <div className="flex flex-wrap gap-1 justify-end">
              {account.match_reasons.slice(0, 2).map((reason, i) => (
                <span
                  key={i}
                  className="text-xs px-1.5 py-0.5 rounded"
                  style={{
                    backgroundColor: 'var(--color-accent-primary-muted)',
                    color: 'var(--color-accent-primary)'
                  }}
                >
                  {reason}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      {accounts.length > 3 && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="mt-2 text-xs transition-colors"
          style={{ color: 'var(--color-accent-primary)' }}
        >
          {showAll ? 'Show less' : `Show ${accounts.length - 3} more`}
        </button>
      )}
    </div>
  );
}

function EmptyRankings() {
  return (
    <div
      className="text-center py-12"
      style={{ color: 'var(--color-text-muted)' }}
    >
      <div
        className="w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4"
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border-default)'
        }}
      >
        <TrophyIcon />
      </div>
      <p className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>
        No partner rankings available
      </p>
      <p className="text-sm mt-1 max-w-md mx-auto">
        Partnerships are discovered automatically when you run <strong>"Discover Vendors"</strong> on an account.
      </p>
      <div
        className="mt-4 p-4 rounded-lg text-left max-w-md mx-auto"
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border-default)'
        }}
      >
        <p className="text-xs font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>
          How to discover partnerships:
        </p>
        <ol className="text-xs space-y-1" style={{ color: 'var(--color-text-muted)' }}>
          <li>1. Select an account from the Accounts tab</li>
          <li>2. Click <strong>"Discover Vendors"</strong> button</li>
          <li>3. AI will find vendor relationships and save them as partnerships</li>
          <li>4. Return here to see ranked partners by ICP account coverage</li>
        </ol>
      </div>
    </div>
  );
}

// Helper functions
function getScoreColor(score: number): string {
  if (score >= 70) return 'var(--color-priority-very-high)';
  if (score >= 50) return 'var(--color-priority-high)';
  if (score >= 30) return 'var(--color-priority-medium)';
  return 'var(--color-priority-low)';
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'Very High': return 'var(--color-priority-very-high)';
    case 'High': return 'var(--color-priority-high)';
    case 'Medium': return 'var(--color-priority-medium)';
    default: return 'var(--color-priority-low)';
  }
}

// Icons
function TrophyIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-4.5A3.75 3.75 0 0012.75 10.5H12m4.5 8.25V10.5a3.75 3.75 0 00-3.75-3.75H12m0 0V3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V3.75m-6 0h6M5.25 6H4.125c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125h1.5c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H5.25zM18.75 6h1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125h-1.5c-.621 0-1.125-.504-1.125-1.125v-1.5c0-.621.504-1.125 1.125-1.125h.375z" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function NetworkIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
    </svg>
  );
}

function TargetIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function DoorIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  );
}

function ChevronDownIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
    </svg>
  );
}
