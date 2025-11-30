import type { PriorityLevel, ChampionPotentialLevel } from '../types';

interface ScoreBadgeProps {
  score: number;
  priorityLevel?: PriorityLevel | ChampionPotentialLevel;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export function ScoreBadge({
  score,
  priorityLevel,
  size = 'md',
  showScore = true
}: ScoreBadgeProps) {
  const level = priorityLevel || getPriorityFromScore(score);
  const badgeClass = getBadgeClass(level);

  return (
    <span className={`badge ${badgeClass} ${sizeClasses[size]}`}>
      {showScore && <span className="font-bold mr-1">{Math.round(score)}</span>}
      <span>{level}</span>
    </span>
  );
}

function getPriorityFromScore(score: number): PriorityLevel {
  if (score >= 80) return 'Very High';
  if (score >= 65) return 'High';
  if (score >= 50) return 'Medium';
  return 'Low';
}

function getBadgeClass(level: string): string {
  switch (level) {
    case 'Very High':
      return 'badge-very-high';
    case 'High':
      return 'badge-high';
    case 'Medium':
      return 'badge-medium';
    default:
      return 'badge-low';
  }
}

// Role tier badge for MEDDIC contacts
interface RoleTierBadgeProps {
  tier: 'entry_point' | 'middle_decider' | 'economic_buyer';
  classification: string;
}

const tierConfig = {
  entry_point: {
    label: 'Entry Point',
    color: 'var(--color-infra-vendor)',
    bgColor: 'rgba(217, 70, 239, 0.12)',
    borderColor: 'rgba(217, 70, 239, 0.25)',
    description: 'Technical Believer - feels the pain',
  },
  middle_decider: {
    label: 'Middle Decider',
    color: 'var(--color-priority-medium)',
    bgColor: 'var(--color-priority-medium-bg)',
    borderColor: 'var(--color-priority-medium-border)',
    description: 'Tooling decision maker',
  },
  economic_buyer: {
    label: 'Economic Buyer',
    color: 'var(--color-infra-cooling)',
    bgColor: 'rgba(6, 182, 212, 0.12)',
    borderColor: 'rgba(6, 182, 212, 0.25)',
    description: 'Budget authority - engage via champion',
  },
};

export function RoleTierBadge({ tier, classification }: RoleTierBadgeProps) {
  const config = tierConfig[tier];

  return (
    <div className="flex flex-col gap-1">
      <span
        className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold"
        style={{
          color: config.color,
          backgroundColor: config.bgColor,
          border: `1px solid ${config.borderColor}`
        }}
      >
        {config.label}
      </span>
      <span
        className="text-xs"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {classification}
      </span>
    </div>
  );
}

// Infrastructure category chip
interface InfraChipProps {
  category: string;
  detected: string[];
  points: number;
  maxPoints: number;
}

const infraConfig: Record<string, { label: string; className: string }> = {
  gpu_infrastructure: { label: 'GPU/AI', className: 'gpu' },
  target_vendors: { label: 'Vendor', className: 'vendor' },
  power_systems: { label: 'Power', className: 'power' },
  cooling_systems: { label: 'Cooling', className: 'cooling' },
  dcim_software: { label: 'DCIM', className: 'dcim' },
};

export function InfraChip({ category, detected, points }: InfraChipProps) {
  const config = infraConfig[category] || { label: category, className: '' };
  const isDetected = detected.length > 0;

  if (!isDetected) return null;

  return (
    <span
      className={`infra-chip ${config.className}`}
      title={`Detected: ${detected.join(', ')}`}
    >
      {config.label}
      <span style={{ opacity: 0.7 }}>+{points}</span>
    </span>
  );
}
