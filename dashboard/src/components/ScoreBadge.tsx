import type { PriorityLevel, ChampionPotentialLevel } from '../types';

interface ScoreBadgeProps {
  score: number;
  priorityLevel?: PriorityLevel | ChampionPotentialLevel;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

const priorityColors: Record<string, string> = {
  'Very High': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'High': 'bg-blue-100 text-blue-800 border-blue-200',
  'Medium': 'bg-amber-100 text-amber-800 border-amber-200',
  'Low': 'bg-gray-100 text-gray-600 border-gray-200',
};

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
  const colorClass = priorityColors[level] || priorityColors['Low'];

  return (
    <span className={`inline-flex items-center rounded-full font-medium border ${colorClass} ${sizeClasses[size]}`}>
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

// Role tier badge for MEDDIC contacts
interface RoleTierBadgeProps {
  tier: 'entry_point' | 'middle_decider' | 'economic_buyer';
  classification: string;
}

const tierConfig = {
  entry_point: {
    label: 'Entry Point',
    emoji: '🔧',
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    description: 'Technical Believer - feels the pain',
  },
  middle_decider: {
    label: 'Middle Decider',
    emoji: '📊',
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    description: 'Tooling decision maker',
  },
  economic_buyer: {
    label: 'Economic Buyer',
    emoji: '💰',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-200',
    description: 'Budget authority - engage via champion',
  },
};

export function RoleTierBadge({ tier, classification }: RoleTierBadgeProps) {
  const config = tierConfig[tier];

  return (
    <div className="flex flex-col gap-1">
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold border ${config.color}`}>
        <span className="mr-1">{config.emoji}</span>
        {config.label}
      </span>
      <span className="text-xs text-gray-500">{classification}</span>
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

const infraColors: Record<string, string> = {
  gpu_infrastructure: 'bg-red-100 text-red-700 border-red-200',
  target_vendors: 'bg-pink-100 text-pink-700 border-pink-200',
  power_systems: 'bg-amber-100 text-amber-700 border-amber-200',
  cooling_systems: 'bg-blue-100 text-blue-700 border-blue-200',
  dcim_software: 'bg-green-100 text-green-700 border-green-200',
};

const infraLabels: Record<string, string> = {
  gpu_infrastructure: '🎮 GPU/AI',
  target_vendors: '🎯 Target Vendor',
  power_systems: '⚡ Power',
  cooling_systems: '❄️ Cooling',
  dcim_software: '📊 DCIM',
};

export function InfraChip({ category, detected, points }: InfraChipProps) {
  const colorClass = infraColors[category] || 'bg-gray-100 text-gray-700';
  const label = infraLabels[category] || category;
  const isDetected = detected.length > 0;

  if (!isDetected) return null;

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${colorClass} mr-1 mb-1`}
      title={`Detected: ${detected.join(', ')}`}
    >
      {label}
      <span className="ml-1 opacity-70">+{points}</span>
    </span>
  );
}
