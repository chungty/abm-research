import { usePartnerships } from '../api/client';

interface Partnership {
  id: string;
  partner_name: string;
  partner_type: string;
  status: string;
  classification?: string;
  account_name?: string;
  notes?: string;
}

export function PartnershipsList() {
  const { partnerships, total, loading, error } = usePartnerships();

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
        <p className="font-medium">Error loading partnerships</p>
        <p className="text-sm opacity-80">{error.message}</p>
      </div>
    );
  }

  const partnershipTypeColors: Record<string, string> = {
    'strategic_partner': 'var(--color-priority-very-high)',
    'direct_icp': 'var(--color-priority-high)',
    'referral_partner': 'var(--color-priority-medium)',
    'competitive': 'var(--color-priority-low)',
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-lg font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Partnerships
          <span
            className="ml-2 text-sm font-normal font-data"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            ({total})
          </span>
        </h2>
      </div>

      {partnerships.length === 0 ? (
        <div
          className="text-center py-12"
          style={{ color: 'var(--color-text-muted)' }}
        >
          <svg
            className="w-12 h-12 mx-auto mb-4 opacity-50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <p>No partnerships found</p>
          <p className="text-sm mt-1">Run research on accounts to discover partnerships</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {partnerships.map((partnership: Partnership) => (
            <PartnershipCard key={partnership.id} partnership={partnership} colors={partnershipTypeColors} />
          ))}
        </div>
      )}
    </div>
  );
}

function PartnershipCard({
  partnership,
  colors
}: {
  partnership: Partnership;
  colors: Record<string, string>;
}) {
  const typeColor = colors[partnership.classification || 'direct_icp'] || 'var(--color-text-secondary)';

  return (
    <div
      className="p-4 rounded-lg transition-all"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border-default)'
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {partnership.partner_name}
          </h3>
          {partnership.account_name && (
            <p
              className="text-sm"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Account: {partnership.account_name}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-1">
          {partnership.classification && (
            <span
              className="px-2 py-0.5 rounded text-xs font-medium"
              style={{
                backgroundColor: `${typeColor}15`,
                color: typeColor,
                border: `1px solid ${typeColor}30`
              }}
            >
              {partnership.classification.replace('_', ' ')}
            </span>
          )}
          {partnership.status && (
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {partnership.status}
            </span>
          )}
        </div>
      </div>
      {partnership.partner_type && (
        <div className="mt-2 flex items-center gap-2">
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-muted)' }}
          >
            Type:
          </span>
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {partnership.partner_type}
          </span>
        </div>
      )}
      {partnership.notes && (
        <p
          className="mt-2 text-sm"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          {partnership.notes}
        </p>
      )}
    </div>
  );
}
