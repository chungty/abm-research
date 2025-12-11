import { usePartnersForAccount } from '../api/client';
import type { RankedPartner, PartnerMatchedAccount } from '../types';

interface PartnerWithMatch extends RankedPartner {
  matchInfo?: PartnerMatchedAccount;
}

interface Props {
  accountId: string;
  accountName: string;
}

export function PartnerPaths({ accountId, accountName }: Props) {
  const { partners, loading, error } = usePartnersForAccount(accountId);

  if (loading) {
    return (
      <div
        className="card-surface p-4 animate-pulse"
      >
        <div className="h-5 w-32 rounded" style={{ backgroundColor: 'var(--color-bg-elevated)' }} />
        <div className="h-16 w-full rounded mt-3" style={{ backgroundColor: 'var(--color-bg-elevated)' }} />
      </div>
    );
  }

  if (error) {
    return null; // Silently fail - partner paths are supplementary
  }

  if (partners.length === 0) {
    return (
      <div
        className="card-surface p-4"
      >
        <div className="flex items-center justify-between mb-3">
          <h3
            className="text-base font-heading flex items-center gap-2"
            style={{ color: 'var(--color-text-primary)' }}
          >
            <PathIcon />
            Partner Paths
          </h3>
        </div>
        <div
          className="text-sm p-3 rounded-lg text-center"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            color: 'var(--color-text-muted)'
          }}
        >
          <p>No known partner paths to {accountName}</p>
          <p className="text-xs mt-1">
            Run "Discover Vendors" on accounts to find partnership connections
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card-surface p-4">
      <div className="flex items-center justify-between mb-3">
        <h3
          className="text-base font-heading flex items-center gap-2"
          style={{ color: 'var(--color-text-primary)' }}
        >
          <PathIcon />
          Partner Paths to {accountName}
        </h3>
        <span
          className="text-xs px-2 py-0.5 rounded-full"
          style={{
            backgroundColor: 'var(--color-priority-very-high)',
            color: '#fff'
          }}
        >
          {partners.length} path{partners.length !== 1 ? 's' : ''}
        </span>
      </div>

      <p
        className="text-xs mb-3"
        style={{ color: 'var(--color-text-muted)' }}
      >
        These partners have relationships that could help you reach this account
      </p>

      <div className="space-y-2">
        {partners.map((partner: PartnerWithMatch) => (
          <PartnerPathCard key={partner.partner_id} partner={partner} />
        ))}
      </div>
    </div>
  );
}

function PartnerPathCard({ partner }: { partner: PartnerWithMatch }) {
  const scoreColor = getScoreColor(partner.partner_score);

  return (
    <div
      className="p-3 rounded-lg"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border-subtle)'
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="font-medium text-sm"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {partner.partner_name}
            </span>
            <span
              className="text-xs px-1.5 py-0.5 rounded"
              style={{
                backgroundColor: 'var(--color-bg-card)',
                color: 'var(--color-text-tertiary)'
              }}
            >
              {partner.partnership_type || 'Partner'}
            </span>
          </div>

          {/* Match reasons - why this partner can help */}
          {partner.matchInfo?.match_reasons && partner.matchInfo.match_reasons.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {partner.matchInfo.match_reasons.map((reason, i) => (
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
          )}

          {/* Partnership context if available */}
          {partner.partnership_data?.context && (
            <p
              className="text-xs mt-2 line-clamp-2"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {partner.partnership_data.context}
            </p>
          )}
        </div>

        {/* Score */}
        <div className="flex flex-col items-end ml-3">
          <div
            className="text-lg font-heading tabular-nums"
            style={{ color: scoreColor }}
          >
            {partner.partner_score.toFixed(0)}
          </div>
          <div
            className="text-xs"
            style={{ color: 'var(--color-text-muted)' }}
          >
            score
          </div>
        </div>
      </div>

      {/* Trust signals */}
      {partner.score_breakdown?.trust_evidence?.signals_detected &&
        partner.score_breakdown.trust_evidence.signals_detected.length > 0 && (
          <div
            className="mt-2 pt-2 flex items-center gap-2"
            style={{ borderTop: '1px solid var(--color-border-subtle)' }}
          >
            <ShieldIcon />
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Trust signals: {partner.score_breakdown.trust_evidence.signals_detected.slice(0, 3).join(', ')}
            </span>
          </div>
        )}
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 70) return 'var(--color-priority-very-high)';
  if (score >= 50) return 'var(--color-priority-high)';
  if (score >= 30) return 'var(--color-priority-medium)';
  return 'var(--color-priority-low)';
}

function PathIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} style={{ color: 'var(--color-infra-power)' }}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  );
}
