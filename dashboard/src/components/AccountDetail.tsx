import type { Account, Contact } from '../types';
import { ScoreBadge } from './ScoreBadge';
import { InfrastructureBreakdown } from './InfrastructureBreakdown';
import { ContactList } from './ContactCard';

interface Props {
  account: Account;
  contacts: Contact[];
  onClose?: () => void;
}

export function AccountDetail({ account, contacts, onClose }: Props) {
  const hasGpu = account.infrastructure_breakdown?.breakdown?.gpu_infrastructure?.detected?.length > 0;

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold text-gray-900">{account.name}</h2>
              {hasGpu && (
                <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm font-medium">
                  🎯 TARGET ICP
                </span>
              )}
            </div>
            <p className="text-gray-500">{account.domain}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <ScoreBadge
              score={account.account_score}
              priorityLevel={account.account_priority_level}
              size="lg"
            />
            {onClose && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-sm"
              >
                ✕ Close
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Score Overview */}
        <div className="grid grid-cols-4 gap-4">
          <ScoreCard
            label="Account Score"
            score={account.account_score}
            subtitle={account.account_priority_level}
            primary
          />
          <ScoreCard
            label="Infrastructure"
            score={account.infrastructure_score}
            subtitle="35% weight"
          />
          <ScoreCard
            label="Business Fit"
            score={account.business_fit_score}
            subtitle="35% weight"
          />
          <ScoreCard
            label="Buying Signals"
            score={account.buying_signals_score}
            subtitle="30% weight"
          />
        </div>

        {/* Infrastructure Breakdown */}
        {account.infrastructure_breakdown && (
          <InfrastructureBreakdown breakdown={account.infrastructure_breakdown} />
        )}

        {/* Business Fit Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Business Fit</h3>
          <div className="grid grid-cols-3 gap-4">
            <BusinessFitItem
              label="Industry"
              value={account.business_model || 'Unknown'}
              score={account.account_score_breakdown?.business_fit?.breakdown?.industry_fit?.score}
            />
            <BusinessFitItem
              label="Company Size"
              value={`${account.employee_count?.toLocaleString() || '?'} employees`}
              score={account.account_score_breakdown?.business_fit?.breakdown?.company_size_fit?.score}
            />
            <BusinessFitItem
              label="Geography"
              value={account.account_score_breakdown?.business_fit?.breakdown?.geographic_fit?.priority || 'Unknown'}
              score={account.account_score_breakdown?.business_fit?.breakdown?.geographic_fit?.score}
            />
          </div>
        </div>

        {/* Buying Signals */}
        {account.account_score_breakdown?.buying_signals && (
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Buying Signals</h3>
            <div className="space-y-3">
              <SignalSection
                label="Trigger Events"
                items={account.account_score_breakdown.buying_signals.breakdown?.trigger_events?.high_value_triggers || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.trigger_events?.score}
              />
              <SignalSection
                label="Expansion Signals"
                items={account.account_score_breakdown.buying_signals.breakdown?.expansion_signals?.detected || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.expansion_signals?.score}
              />
              <SignalSection
                label="Hiring Signals"
                items={account.account_score_breakdown.buying_signals.breakdown?.hiring_signals?.detected || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.hiring_signals?.score}
              />
            </div>
          </div>
        )}

        {/* Partnership Classification */}
        {account.partnership_classification && (
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Partnership Classification</h3>
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                {account.partnership_classification}
              </span>
              <span className="text-sm text-gray-500">
                {account.classification_confidence?.toFixed(0)}% confidence
              </span>
            </div>
          </div>
        )}

        {/* Contacts */}
        <ContactList contacts={contacts} title={`Contacts at ${account.name}`} />
      </div>
    </div>
  );
}

function ScoreCard({
  label,
  score,
  subtitle,
  primary = false,
}: {
  label: string;
  score: number;
  subtitle: string;
  primary?: boolean;
}) {
  const getColor = (s: number) => {
    if (s >= 80) return 'text-emerald-600';
    if (s >= 60) return 'text-blue-600';
    if (s >= 40) return 'text-amber-600';
    return 'text-gray-500';
  };

  return (
    <div
      className={`rounded-lg p-4 ${
        primary ? 'bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200' : 'bg-gray-50'
      }`}
    >
      <div className={`text-3xl font-bold ${getColor(score)}`}>{Math.round(score)}</div>
      <div className="text-sm font-medium text-gray-900">{label}</div>
      <div className="text-xs text-gray-500">{subtitle}</div>
    </div>
  );
}

function BusinessFitItem({
  label,
  value,
  score,
}: {
  label: string;
  value: string;
  score?: number;
}) {
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className="font-medium text-gray-900">{value}</div>
      {score !== undefined && (
        <div className="text-xs text-gray-500 mt-1">Score: {Math.round(score)}</div>
      )}
    </div>
  );
}

function SignalSection({
  label,
  items,
  score,
}: {
  label: string;
  items: string[];
  score?: number;
}) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="text-sm font-medium text-gray-700">{label}</div>
        {items.length > 0 ? (
          <div className="flex flex-wrap gap-1 mt-1">
            {items.map((item, i) => (
              <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
                {item}
              </span>
            ))}
          </div>
        ) : (
          <span className="text-xs text-gray-400">None detected</span>
        )}
      </div>
      {score !== undefined && (
        <span className="text-sm font-medium text-gray-600">{Math.round(score)}</span>
      )}
    </div>
  );
}
