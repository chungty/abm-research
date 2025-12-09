import { useState } from 'react';
import type { Contact, Account, RoleTier, ChampionPotentialLevel } from '../types';
import { ScoreBadge, RoleTierBadge } from './ScoreBadge';
import { OutreachPanel } from './OutreachPanel';
import { API_BASE } from '../api/client';
import { APP_CONFIG, getScoreColor } from './shared';

interface Props {
  contact: Contact;
  account?: Account;
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const tierConfig: Record<RoleTier, {
  color: string;
  bgColor: string;
  borderColor: string;
  glowColor: string;
}> = {
  entry_point: {
    color: 'var(--color-infra-vendor)',
    bgColor: 'rgba(217, 70, 239, 0.08)',
    borderColor: 'rgba(217, 70, 239, 0.2)',
    glowColor: 'rgba(217, 70, 239, 0.1)',
  },
  middle_decider: {
    color: 'var(--color-priority-medium)',
    bgColor: 'var(--color-priority-medium-bg)',
    borderColor: 'var(--color-priority-medium-border)',
    glowColor: 'rgba(245, 158, 11, 0.1)',
  },
  economic_buyer: {
    color: 'var(--color-infra-cooling)',
    bgColor: 'rgba(6, 182, 212, 0.08)',
    borderColor: 'rgba(6, 182, 212, 0.2)',
    glowColor: 'rgba(6, 182, 212, 0.1)',
  },
};

const championColors: Record<ChampionPotentialLevel, string> = {
  'Very High': 'var(--color-priority-very-high)',
  High: 'var(--color-priority-high)',
  Medium: 'var(--color-priority-medium)',
  Low: 'var(--color-text-tertiary)',
};

// Use centralized config for threshold
const LEAD_SCORE_THRESHOLD = APP_CONFIG.LEAD_SCORE_THRESHOLD;

export function ContactCard({ contact, account, expanded = false, onToggleExpand }: Props) {
  const [showOutreach, setShowOutreach] = useState(false);
  const [isRevealing, setIsRevealing] = useState(false);
  const [revealedEmail, setRevealedEmail] = useState<string | null>(null);
  const [revealError, setRevealError] = useState<string | null>(null);

  const config = tierConfig[contact.role_tier] || tierConfig.entry_point;
  const isHighChampion = ['Very High', 'High'].includes(contact.champion_potential_level);

  // Determine current email (revealed or from contact)
  const currentEmail = revealedEmail || contact.email;
  const hasValidEmail = currentEmail && currentEmail.trim() !== '' && !currentEmail.includes('@unknown');
  const canRevealEmail = !hasValidEmail && contact.lead_score >= LEAD_SCORE_THRESHOLD;

  const handleRevealEmail = async () => {
    if (isRevealing || !contact.id) return;

    setIsRevealing(true);
    setRevealError(null);

    try {
      const response = await fetch(`${API_BASE}/contacts/${contact.id}/reveal-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to reveal email');
      }

      if (data.email) {
        setRevealedEmail(data.email);
      } else {
        setRevealError('No email found');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      // Provide user-friendly error messages
      if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
        setRevealError('Connection failed. Check that the API is running.');
      } else if (errorMsg.includes('not found') || errorMsg.includes('404')) {
        setRevealError('Contact not found in enrichment sources.');
      } else {
        setRevealError('Could not reveal email. Try again later.');
      }
    } finally {
      setIsRevealing(false);
    }
  };

  return (
    <>
      <div
        className="rounded-lg p-4 transition-all"
        style={{
          backgroundColor: config.bgColor,
          border: `1px solid ${config.borderColor}`,
          boxShadow: isHighChampion ? `0 0 12px ${config.glowColor}` : 'none'
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h4
                className="font-semibold truncate"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {contact.name}
              </h4>
              {isHighChampion && (
                <span
                  className="text-xs px-1.5 py-0.5 rounded font-medium"
                  style={{
                    color: 'var(--color-infra-vendor)',
                    backgroundColor: 'rgba(217, 70, 239, 0.15)',
                    border: '1px solid rgba(217, 70, 239, 0.25)'
                  }}
                >
                  Champion
                </span>
              )}
            </div>
            <p
              className="text-sm truncate"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {contact.title}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <ScoreBadge score={contact.lead_score} size="sm" />
            <span
              className="text-xs font-medium"
              style={{ color: championColors[contact.champion_potential_level] }}
            >
              {contact.champion_potential_level} Champion
            </span>
          </div>
        </div>

        {/* Role Tier */}
        <div className="mb-3">
          <RoleTierBadge tier={contact.role_tier} classification={contact.role_classification} />
        </div>

        {/* Score Breakdown */}
        <div
          className="grid grid-cols-3 gap-2 mb-3 text-center p-2 rounded-md"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.04)' }}
        >
          <MiniScore
            label="Champion"
            score={contact.champion_potential_score}
            weight="45%"
          />
          <MiniScore
            label="Role Fit"
            score={contact.meddic_score_breakdown?.role_fit?.score || 0}
            weight="30%"
          />
          <MiniScore
            label="Engagement"
            score={contact.meddic_score_breakdown?.engagement_potential?.score || 0}
            weight="25%"
          />
        </div>

        {/* Why Prioritize */}
        {contact.why_prioritize && contact.why_prioritize.length > 0 && (
          <div
            className="mb-3 p-2 rounded"
            style={{ backgroundColor: 'rgba(255, 255, 255, 0.04)' }}
          >
            <p
              className="text-xs font-medium mb-1"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Why Prioritize:
            </p>
            <ul className="text-xs space-y-0.5" style={{ color: 'var(--color-text-tertiary)' }}>
              {contact.why_prioritize.slice(0, expanded ? undefined : 2).map((reason, i) => (
                <li key={i} className="flex items-start gap-1">
                  <span style={{ color: 'var(--color-priority-very-high)' }}>✓</span>
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Approach */}
        <div
          className="p-2 rounded text-xs"
          style={{
            backgroundColor: 'var(--color-priority-high-bg)',
            border: '1px solid var(--color-priority-high-border)'
          }}
        >
          <span
            className="font-medium"
            style={{ color: 'var(--color-priority-high)' }}
          >
            Approach:{' '}
          </span>
          <span style={{ color: 'var(--color-text-secondary)' }}>
            {contact.recommended_approach}
          </span>
        </div>

        {/* Contact Info & Actions */}
        <div
          className="mt-3 pt-3 flex items-center justify-between"
          style={{ borderTop: '1px solid var(--color-border-subtle)' }}
        >
          <div className="flex items-center gap-3 text-xs">
            {/* Email - show link if available, or Reveal button if eligible */}
            {hasValidEmail ? (
              <a
                href={`mailto:${currentEmail}`}
                className="truncate max-w-[120px] transition-colors"
                style={{ color: 'var(--color-text-tertiary)' }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-accent-primary)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-tertiary)'}
                onClick={e => e.stopPropagation()}
              >
                {currentEmail}
                {revealedEmail && (
                  <span
                    className="ml-1 text-xs"
                    style={{ color: 'var(--color-priority-high)' }}
                  >
                    ✓
                  </span>
                )}
              </a>
            ) : canRevealEmail ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRevealEmail();
                }}
                disabled={isRevealing}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-all"
                style={{
                  backgroundColor: isRevealing ? 'var(--color-bg-card)' : 'var(--color-priority-high-bg)',
                  color: isRevealing ? 'var(--color-text-muted)' : 'var(--color-priority-high)',
                  border: `1px solid ${isRevealing ? 'var(--color-border-default)' : 'var(--color-priority-high-border)'}`,
                  cursor: isRevealing ? 'wait' : 'pointer'
                }}
              >
                {isRevealing ? (
                  <>
                    <LoadingSpinner />
                    Revealing...
                  </>
                ) : (
                  <>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Reveal Email
                  </>
                )}
              </button>
            ) : revealError ? (
              <span
                className="text-xs"
                style={{ color: 'var(--color-priority-low)' }}
              >
                {revealError}
              </span>
            ) : (
              <span
                className="text-xs"
                style={{ color: 'var(--color-text-muted)' }}
              >
                No email
              </span>
            )}
            {contact.linkedin_url && (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="transition-colors"
                style={{ color: 'var(--color-priority-high)' }}
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-accent-primary)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-priority-high)'}
                onClick={e => e.stopPropagation()}
              >
                LinkedIn
              </a>
            )}
          </div>

          {/* Outreach Button */}
          {account && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowOutreach(true);
              }}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all"
              style={{
                backgroundColor: 'var(--color-accent-primary-muted)',
                color: 'var(--color-accent-primary)',
                border: '1px solid var(--color-accent-primary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-accent-primary)';
                e.currentTarget.style.color = 'var(--color-bg-base)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-accent-primary-muted)';
                e.currentTarget.style.color = 'var(--color-accent-primary)';
              }}
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Generate Outreach
            </button>
          )}
        </div>

        {/* Expand/Collapse */}
        {onToggleExpand && (
          <button
            onClick={onToggleExpand}
            aria-expanded={expanded}
            aria-label={expanded ? 'Show less contact details' : 'Show more contact details'}
            className="w-full mt-2 text-xs transition-colors py-1 rounded hover:bg-[rgba(255,255,255,0.05)] focus:outline-none focus-visible:ring-2"
            style={{ color: 'var(--color-text-muted)' }}
          >
            {expanded ? '▲ Less' : '▼ More'}
          </button>
        )}
      </div>

      {/* Outreach Panel Modal */}
      {showOutreach && account && (
        <OutreachPanel
          contact={contact}
          account={account}
          onClose={() => setShowOutreach(false)}
        />
      )}
    </>
  );
}

function LoadingSpinner() {
  return (
    <svg
      className="animate-spin w-3 h-3"
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

function MiniScore({ label, score, weight }: { label: string; score: number; weight: string }) {
  const isZero = score === 0;
  const color = getScoreColor(score);

  return (
    <div
      className="rounded p-1.5 relative"
      style={{ backgroundColor: 'rgba(255, 255, 255, 0.04)' }}
      title={isZero ? `${label}: No data. Run "Rescore MEDDIC" to calculate.` : `${label}: ${Math.round(score)} (${weight} of total)`}
    >
      {isZero && (
        <div
          className="absolute -top-1 -right-1 w-3 h-3 rounded-full flex items-center justify-center text-xs"
          style={{
            backgroundColor: 'var(--color-priority-medium-bg)',
            color: 'var(--color-priority-medium)',
            fontSize: '8px',
          }}
          title="Missing data - run Rescore MEDDIC"
        >
          ?
        </div>
      )}
      <div
        className="score-value text-sm font-semibold"
        style={{ color: isZero ? 'var(--color-text-muted)' : color }}
      >
        {isZero ? '—' : Math.round(score)}
      </div>
      <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
        {label}
      </div>
      <div
        className="text-xs font-medium"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        {weight}
      </div>
    </div>
  );
}

// Contact List component
interface ContactListProps {
  contacts: Contact[];
  account?: Account;
  title?: string;
}

export function ContactList({ contacts, account, title = 'Contacts' }: ContactListProps) {
  // Group contacts by role tier
  const groupedContacts = {
    entry_point: contacts.filter(c => c.role_tier === 'entry_point'),
    middle_decider: contacts.filter(c => c.role_tier === 'middle_decider'),
    economic_buyer: contacts.filter(c => c.role_tier === 'economic_buyer'),
  };

  // Sort each group by score
  Object.values(groupedContacts).forEach(group => {
    group.sort((a, b) => b.lead_score - a.lead_score);
  });

  const tierSections = [
    {
      key: 'entry_point' as const,
      label: 'Entry Points',
      sublabel: 'Technical Believers - Start Here',
      color: 'var(--color-infra-vendor)',
    },
    {
      key: 'middle_decider' as const,
      label: 'Middle Deciders',
      sublabel: 'Tooling Decision Makers',
      color: 'var(--color-priority-medium)',
    },
    {
      key: 'economic_buyer' as const,
      label: 'Economic Buyers',
      sublabel: 'Budget Authority - Engage via Champion',
      color: 'var(--color-infra-cooling)',
    },
  ];

  return (
    <div className="space-y-6">
      <h3 style={{ color: 'var(--color-text-primary)' }} className="text-lg font-semibold">
        {title}
        <span
          className="ml-2 text-sm font-normal font-data"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          ({contacts.length})
        </span>
      </h3>

      {tierSections.map(({ key, label, sublabel, color }) => (
        groupedContacts[key].length > 0 && (
          <div key={key}>
            <div className="flex items-center gap-2 mb-3">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: color }}
              />
              <h4 className="font-medium" style={{ color }}>
                {label}
                <span
                  className="ml-1 text-xs font-normal"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  ({sublabel})
                </span>
              </h4>
            </div>
            <div className="grid gap-3">
              {groupedContacts[key].map(contact => (
                <ContactCard key={contact.id} contact={contact} account={account} />
              ))}
            </div>
          </div>
        )
      ))}

      {contacts.length === 0 && (
        <div
          className="text-center py-8"
          style={{ color: 'var(--color-text-muted)' }}
        >
          <svg
            className="w-10 h-10 mx-auto mb-3 opacity-50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <p className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>
            No contacts found
          </p>
          <p className="text-sm mt-1">
            Run <strong>"Contact Intelligence"</strong> enrichment to discover contacts for this account.
          </p>
          <p className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
            💡 Look for the "Rescore MEDDIC" button in the account actions.
          </p>
        </div>
      )}
    </div>
  );
}
