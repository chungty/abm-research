import type { Account } from '../types';
import { ScoreBadge, InfraChip } from './ScoreBadge';

interface Props {
  account: Account;
  onClick?: () => void;
  selected?: boolean;
}

// Account urgency status based on buying signals
export type AccountStatus = 'hot' | 'warming' | 'quiet';

export interface AccountStatusInfo {
  status: AccountStatus;
  label: string;
  reason: string | null;
  color: string;
  bgColor: string;
  borderColor: string;
}

export function getAccountStatus(account: Account): AccountStatusInfo {
  const signalScore = account.buying_signals_score || 0;

  // Extract a reason from the buying signals breakdown if available
  const buyingSignals = account.account_score_breakdown?.buying_signals?.breakdown;
  let reason: string | null = null;

  if (buyingSignals) {
    // Check for high-value triggers first
    const triggers = buyingSignals.trigger_events?.high_value_triggers;
    if (triggers && triggers.length > 0) {
      reason = triggers[0];
    }
    // Then check expansion signals
    else if (buyingSignals.expansion_signals?.detected?.length > 0) {
      reason = buyingSignals.expansion_signals.detected[0];
    }
    // Then hiring signals
    else if (buyingSignals.hiring_signals?.detected?.length > 0) {
      reason = buyingSignals.hiring_signals.detected[0];
    }
  }

  if (signalScore >= 50) {
    return {
      status: 'hot',
      label: 'Hot',
      reason,
      color: 'var(--color-priority-very-high)',
      bgColor: 'var(--color-priority-very-high-bg)',
      borderColor: 'var(--color-priority-very-high-border)'
    };
  }

  if (signalScore >= 20) {
    return {
      status: 'warming',
      label: 'Warming',
      reason,
      color: 'var(--color-priority-medium)',
      bgColor: 'var(--color-priority-medium-bg)',
      borderColor: 'var(--color-priority-medium-border)'
    };
  }

  return {
    status: 'quiet',
    label: 'Quiet',
    reason: null,
    color: 'var(--color-text-muted)',
    bgColor: 'var(--color-bg-elevated)',
    borderColor: 'var(--color-border-subtle)'
  };
}

export function AccountCard({ account, onClick, selected = false }: Props) {
  const infraBreakdown = account.infrastructure_breakdown?.breakdown;

  // Get detected infrastructure categories
  const detectedInfra = infraBreakdown
    ? Object.entries(infraBreakdown)
        .filter(([_, data]) => data.detected?.length > 0)
        .map(([cat, data]) => ({ category: cat, ...data }))
    : [];

  const hasGpu = infraBreakdown?.gpu_infrastructure?.detected?.length > 0;

  // Compute account urgency status
  const statusInfo = getAccountStatus(account);

  return (
    <div
      onClick={onClick}
      className={`card-surface p-4 cursor-pointer ${selected ? 'selected' : ''} ${hasGpu ? 'target-icp' : ''}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3
              className="text-base font-semibold truncate"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {account.name}
            </h3>
            {hasGpu && (
              <span className="badge badge-target text-xs px-1.5 py-0.5">
                TARGET
              </span>
            )}
          </div>
          <p
            className="text-sm truncate"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {account.domain}
          </p>
        </div>
        <ScoreBadge
          score={account.account_score}
          priorityLevel={account.account_priority_level}
        />
      </div>

      {/* Score Breakdown */}
      <div
        className="grid grid-cols-3 gap-3 mb-3 py-2 px-3 rounded-md"
        style={{ backgroundColor: 'var(--color-bg-elevated)' }}
      >
        <ScoreItem label="Infra" score={account.infrastructure_score} />
        <ScoreItem label="Business" score={account.business_fit_score} />
        <ScoreItem label="Signals" score={account.buying_signals_score} />
      </div>

      {/* Infrastructure Chips */}
      {detectedInfra.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {detectedInfra.map(({ category, detected, points, max_points }) => (
            <InfraChip
              key={category}
              category={category}
              detected={detected}
              points={points}
              maxPoints={max_points}
            />
          ))}
        </div>
      )}

      {/* Status + Metrics Row */}
      <div
        className="flex items-center gap-2 mb-3"
      >
        {/* Status Badge */}
        <div
          className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium"
          style={{
            backgroundColor: statusInfo.bgColor,
            color: statusInfo.color,
            border: `1px solid ${statusInfo.borderColor}`
          }}
        >
          <StatusDot status={statusInfo.status} />
          {statusInfo.label}
        </div>

        {/* Quick metrics */}
        <span
          className="text-xs"
          style={{ color: 'var(--color-text-muted)' }}
        >
          {account.contacts_count || 0} contacts
        </span>
      </div>

      {/* Status Reason - only show if there's a meaningful reason */}
      {statusInfo.reason && (
        <div
          className="text-xs mb-3 px-2 py-1.5 rounded"
          style={{
            backgroundColor: statusInfo.bgColor,
            color: statusInfo.color,
            borderLeft: `2px solid ${statusInfo.color}`
          }}
        >
          {statusInfo.reason}
        </div>
      )}

      {/* Footer */}
      <div
        className="flex items-center justify-between text-xs pt-2"
        style={{
          borderTop: '1px solid var(--color-border-subtle)',
          color: 'var(--color-text-muted)'
        }}
      >
        <div className="flex items-center gap-3">
          <span className="font-data">{account.employee_count?.toLocaleString() || '—'} employees</span>
        </div>
        <span
          className="px-1.5 py-0.5 rounded text-xs"
          style={{
            backgroundColor: 'var(--color-bg-hover)',
            color: 'var(--color-text-tertiary)'
          }}
        >
          {account.business_model || 'Unknown'}
        </span>
      </div>
    </div>
  );
}

function StatusDot({ status }: { status: AccountStatus }) {
  return (
    <span
      className="w-2 h-2 rounded-full"
      style={{
        backgroundColor: status === 'hot'
          ? 'var(--color-priority-very-high)'
          : status === 'warming'
            ? 'var(--color-priority-medium)'
            : 'var(--color-text-muted)'
      }}
    />
  );
}

function ScoreItem({ label, score }: { label: string; score: number }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'var(--color-priority-very-high)';
    if (s >= 60) return 'var(--color-priority-high)';
    if (s >= 40) return 'var(--color-priority-medium)';
    return 'var(--color-text-tertiary)';
  };

  return (
    <div className="text-center">
      <div
        className="score-value text-lg"
        style={{ color: getColor(score) }}
      >
        {Math.round(score)}
      </div>
      <div className="score-label">{label}</div>
    </div>
  );
}
