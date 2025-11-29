import type { Contact, RoleTier, ChampionPotentialLevel } from '../types';
import { ScoreBadge, RoleTierBadge } from './ScoreBadge';

interface Props {
  contact: Contact;
  expanded?: boolean;
  onToggleExpand?: () => void;
}

const tierConfig: Record<RoleTier, { emoji: string; bgColor: string; borderColor: string }> = {
  entry_point: {
    emoji: '🔧',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
  },
  middle_decider: {
    emoji: '📊',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
  },
  economic_buyer: {
    emoji: '💰',
    bgColor: 'bg-cyan-50',
    borderColor: 'border-cyan-200',
  },
};

const championColors: Record<ChampionPotentialLevel, string> = {
  'Very High': 'text-emerald-600',
  High: 'text-blue-600',
  Medium: 'text-amber-600',
  Low: 'text-gray-500',
};

export function ContactCard({ contact, expanded = false, onToggleExpand }: Props) {
  const config = tierConfig[contact.role_tier] || tierConfig.entry_point;
  const isHighChampion = ['Very High', 'High'].includes(contact.champion_potential_level);

  return (
    <div
      className={`rounded-lg border p-4 transition-all ${config.bgColor} ${config.borderColor} ${
        isHighChampion ? 'ring-2 ring-purple-300' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-lg">{config.emoji}</span>
            <h4 className="font-semibold text-gray-900 truncate">{contact.name}</h4>
            {isHighChampion && (
              <span className="text-xs px-1.5 py-0.5 bg-purple-200 text-purple-800 rounded font-medium">
                🏆 Champion
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 truncate">{contact.title}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <ScoreBadge score={contact.lead_score} size="sm" />
          <span className={`text-xs font-medium ${championColors[contact.champion_potential_level]}`}>
            {contact.champion_potential_level} Champion
          </span>
        </div>
      </div>

      {/* Role Tier */}
      <div className="mb-3">
        <RoleTierBadge tier={contact.role_tier} classification={contact.role_classification} />
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
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
        <div className="mb-3 p-2 bg-white/50 rounded">
          <p className="text-xs font-medium text-gray-700 mb-1">Why Prioritize:</p>
          <ul className="text-xs text-gray-600 space-y-0.5">
            {contact.why_prioritize.slice(0, expanded ? undefined : 2).map((reason, i) => (
              <li key={i} className="flex items-start gap-1">
                <span className="text-emerald-500">✓</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Approach */}
      <div className="p-2 bg-blue-50 border border-blue-100 rounded text-xs">
        <span className="font-medium text-blue-800">Approach: </span>
        <span className="text-blue-700">{contact.recommended_approach}</span>
      </div>

      {/* Contact Info */}
      <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
        <a
          href={`mailto:${contact.email}`}
          className="hover:text-blue-600 truncate max-w-[60%]"
          onClick={e => e.stopPropagation()}
        >
          {contact.email}
        </a>
        {contact.linkedin_url && (
          <a
            href={contact.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800"
            onClick={e => e.stopPropagation()}
          >
            LinkedIn →
          </a>
        )}
      </div>

      {/* Expand/Collapse */}
      {onToggleExpand && (
        <button
          onClick={onToggleExpand}
          className="w-full mt-2 text-xs text-gray-500 hover:text-gray-700"
        >
          {expanded ? '▲ Less' : '▼ More'}
        </button>
      )}
    </div>
  );
}

function MiniScore({ label, score, weight }: { label: string; score: number; weight: string }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'text-emerald-600';
    if (s >= 60) return 'text-blue-600';
    if (s >= 40) return 'text-amber-600';
    return 'text-gray-500';
  };

  return (
    <div className="bg-white/50 rounded p-1">
      <div className={`text-sm font-bold ${getColor(score)}`}>{Math.round(score)}</div>
      <div className="text-xs text-gray-500">
        {label}
        <span className="opacity-50 ml-0.5">({weight})</span>
      </div>
    </div>
  );
}

// Contact List component
interface ContactListProps {
  contacts: Contact[];
  title?: string;
}

export function ContactList({ contacts, title = 'Contacts' }: ContactListProps) {
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

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">
        {title}
        <span className="ml-2 text-sm font-normal text-gray-500">({contacts.length})</span>
      </h3>

      {/* Entry Points - Primary targets */}
      {groupedContacts.entry_point.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🔧</span>
            <h4 className="font-medium text-purple-800">
              Entry Points
              <span className="ml-1 text-xs font-normal text-purple-600">
                (Technical Believers - Start Here)
              </span>
            </h4>
          </div>
          <div className="grid gap-3">
            {groupedContacts.entry_point.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Middle Deciders */}
      {groupedContacts.middle_decider.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">📊</span>
            <h4 className="font-medium text-orange-800">
              Middle Deciders
              <span className="ml-1 text-xs font-normal text-orange-600">
                (Tooling Decision Makers)
              </span>
            </h4>
          </div>
          <div className="grid gap-3">
            {groupedContacts.middle_decider.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {/* Economic Buyers */}
      {groupedContacts.economic_buyer.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">💰</span>
            <h4 className="font-medium text-cyan-800">
              Economic Buyers
              <span className="ml-1 text-xs font-normal text-cyan-600">
                (Budget Authority - Engage via Champion)
              </span>
            </h4>
          </div>
          <div className="grid gap-3">
            {groupedContacts.economic_buyer.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        </div>
      )}

      {contacts.length === 0 && (
        <div className="text-center py-8 text-gray-500">No contacts found</div>
      )}
    </div>
  );
}
