import type { InfrastructureBreakdown as InfraBreakdownType } from '../types';
import { InfraChip } from './ScoreBadge';

interface Props {
  breakdown: InfraBreakdownType;
  compact?: boolean;
}

const categoryOrder = [
  'gpu_infrastructure',
  'target_vendors',
  'power_systems',
  'cooling_systems',
  'dcim_software',
] as const;

const categoryDescriptions: Record<string, string> = {
  gpu_infrastructure: 'GPU/AI Infrastructure - TARGET ICP (neocloud datacenter)',
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
        <span className="text-sm font-medium text-gray-700 mr-2">
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
          <span className="text-xs text-gray-400">No infrastructure detected</span>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Infrastructure Breakdown</h3>
        <div className="flex items-center">
          <span className="text-2xl font-bold text-gray-900">{Math.round(score)}</span>
          <span className="text-sm text-gray-500 ml-1">/100</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div
          className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all"
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>

      {/* Category breakdown */}
      <div className="space-y-3">
        {categoryOrder.map(cat => {
          const data = categories[cat];
          if (!data) return null;

          const isDetected = data.detected?.length > 0;
          const percentage = (data.points / data.max_points) * 100;

          return (
            <div key={cat} className={`${isDetected ? '' : 'opacity-50'}`}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <InfraChip
                    category={cat}
                    detected={data.detected || []}
                    points={data.points}
                    maxPoints={data.max_points}
                  />
                  {!isDetected && (
                    <span className="text-xs text-gray-400">
                      {categoryDescriptions[cat]?.split(' - ')[0] || cat}
                    </span>
                  )}
                </div>
                <span className="text-sm font-medium">
                  {data.points}/{data.max_points}
                </span>
              </div>

              {/* Mini progress bar */}
              <div className="w-full bg-gray-100 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all ${
                    isDetected ? 'bg-emerald-500' : 'bg-gray-300'
                  }`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              {/* Detected keywords */}
              {isDetected && data.detected.length > 0 && (
                <div className="mt-1 text-xs text-gray-500">
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
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-lg">🎯</span>
            <div>
              <p className="text-sm font-semibold text-red-800">TARGET ICP: GPU Infrastructure Detected</p>
              <p className="text-xs text-red-600">
                Neocloud datacenter - highest priority account type
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
