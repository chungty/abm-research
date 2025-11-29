import type { Account } from '../types';
import { ScoreBadge, InfraChip } from './ScoreBadge';

interface Props {
  account: Account;
  onClick?: () => void;
  selected?: boolean;
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

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md
        ${selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'}
        ${hasGpu ? 'ring-1 ring-red-200' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {account.name}
            </h3>
            {hasGpu && (
              <span className="text-xs px-1.5 py-0.5 bg-red-100 text-red-700 rounded font-medium">
                🎯 TARGET ICP
              </span>
            )}
          </div>
          <p className="text-sm text-gray-500 truncate">{account.domain}</p>
        </div>
        <ScoreBadge
          score={account.account_score}
          priorityLevel={account.account_priority_level}
        />
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <ScoreItem label="Infrastructure" score={account.infrastructure_score} />
        <ScoreItem label="Business Fit" score={account.business_fit_score} />
        <ScoreItem label="Buying Signals" score={account.buying_signals_score} />
      </div>

      {/* Infrastructure Chips */}
      {detectedInfra.length > 0 && (
        <div className="flex flex-wrap mb-3">
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

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-gray-500 pt-2 border-t border-gray-100">
        <div className="flex items-center gap-4">
          <span>{account.employee_count?.toLocaleString() || '?'} employees</span>
          <span>{account.contacts_count || 0} contacts</span>
        </div>
        <span className="text-xs">{account.business_model}</span>
      </div>
    </div>
  );
}

function ScoreItem({ label, score }: { label: string; score: number }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'text-emerald-600';
    if (s >= 60) return 'text-blue-600';
    if (s >= 40) return 'text-amber-600';
    return 'text-gray-500';
  };

  return (
    <div className="text-center">
      <div className={`text-lg font-bold ${getColor(score)}`}>
        {Math.round(score)}
      </div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}
