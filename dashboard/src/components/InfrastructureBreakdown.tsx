import type { InfrastructureBreakdown as InfraBreakdownType } from '../types';
import { InfraChip } from './ScoreBadge';

interface Props {
  breakdown: InfraBreakdownType;
  compact?: boolean;
}

const categoryOrder = [
  'gpu_infrastructure',
  'dc_rectifier_systems',
  'target_vendors',
  'power_systems',
  'cooling_systems',
  'dcim_software',
] as const;

const categoryDescriptions: Record<string, string> = {
  gpu_infrastructure: 'GPU/AI Infrastructure - TARGET ICP (neocloud datacenter)',
  dc_rectifier_systems: 'DC Rectifier/Power - TARGET ICP (48V/380V DC infrastructure)',
  target_vendors: 'Target Vendor (competitive displacement opportunity)',
  power_systems: 'Power infrastructure detected',
  cooling_systems: 'Cooling infrastructure (critical for GPU density)',
  dcim_software: 'DCIM software detected',
};

export function InfrastructureBreakdown({ breakdown, compact = false }: Props) {
  const { score, breakdown: categories } = breakdown;

  // Get detected categories
  const detectedCategories = categoryOrder.filter(
    cat => categories[cat]?.detected?.length > 0
  );

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-1">
        <span
          className="text-sm font-medium mr-2"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          Infra: {Math.round(score)}
        </span>
        {detectedCategories.map(cat => (
          <InfraChip
            key={cat}
            category={cat}
            detected={categories[cat].detected}
            points={categories[cat].points}
            maxPoints={categories[cat].max_points}
          />
        ))}
        {detectedCategories.length === 0 && (
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-muted)' }}
          >
            No infrastructure detected
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="card-surface p-4">
      <div className="flex items-center justify-between mb-4">
        <h3
          className="text-base font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Infrastructure Breakdown
        </h3>
        <div className="flex items-center">
          <span
            className="score-value text-2xl"
            style={{ color: 'var(--color-priority-very-high)' }}
          >
            {Math.round(score)}
          </span>
          <span
            className="text-sm ml-1"
            style={{ color: 'var(--color-text-muted)' }}
          >
            /100
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div
        className="w-full rounded-full h-2 mb-4"
        style={{ backgroundColor: 'var(--color-bg-elevated)' }}
      >
        <div
          className="h-2 rounded-full transition-all"
          style={{
            width: `${Math.min(score, 100)}%`,
            background: 'linear-gradient(90deg, var(--color-priority-very-high), var(--color-accent-primary))'
          }}
        />
      </div>

      {/* Category breakdown */}
      <div className="space-y-4">
        {categoryOrder.map(cat => {
          const data = categories[cat];
          if (!data) return null;

          const isDetected = data.detected?.length > 0;
          const percentage = (data.points / data.max_points) * 100;

          return (
            <div
              key={cat}
              className="transition-opacity"
              style={{ opacity: isDetected ? 1 : 0.4 }}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <InfraChip
                    category={cat}
                    detected={data.detected || []}
                    points={data.points}
                    maxPoints={data.max_points}
                  />
                  {!isDetected && (
                    <span
                      className="text-xs"
                      style={{ color: 'var(--color-text-muted)' }}
                    >
                      {categoryDescriptions[cat]?.split(' - ')[0] || cat}
                    </span>
                  )}
                </div>
                <span
                  className="text-sm font-data font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  {data.points}/{data.max_points}
                </span>
              </div>

              {/* Mini progress bar */}
              <div
                className="w-full rounded-full h-1"
                style={{ backgroundColor: 'var(--color-bg-elevated)' }}
              >
                <div
                  className="h-1 rounded-full transition-all"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: isDetected ? 'var(--color-priority-very-high)' : 'var(--color-border-strong)'
                  }}
                />
              </div>

              {/* Detected keywords */}
              {isDetected && data.detected.length > 0 && (
                <div
                  className="mt-1.5 text-xs"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Detected: {data.detected.slice(0, 5).join(', ')}
                  {data.detected.length > 5 && ` +${data.detected.length - 5} more`}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* GPU Infrastructure highlight */}
      {categories.gpu_infrastructure?.detected?.length > 0 && (
        <div
          className="mt-4 p-3 rounded-lg"
          style={{
            backgroundColor: 'var(--color-target-hot-bg)',
            border: '1px solid var(--color-target-hot-border)'
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)' }}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                style={{ color: 'var(--color-target-hot)' }}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div>
              <p
                className="text-sm font-semibold"
                style={{ color: 'var(--color-target-hot)' }}
              >
                TARGET ICP: GPU Infrastructure Detected
              </p>
              <p
                className="text-xs"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Neocloud datacenter - highest priority account type
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
