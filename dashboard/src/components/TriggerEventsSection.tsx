import type { TriggerEvent } from '../types';

interface Props {
  events: TriggerEvent[];
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

/**
 * TriggerEventsSection - Displays trigger events within the AccountDetail view
 * Shows event cards with type badges, descriptions, and metadata
 */
export function TriggerEventsSection({ events, onRefresh, isRefreshing }: Props) {
  // Aggregate events by type with count
  const eventsByType = events.reduce((acc, event) => {
    const type = event.event_type || 'Unknown';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(event);
    return acc;
  }, {} as Record<string, TriggerEvent[]>);

  const eventTypeColors: Record<string, string> = {
    expansion: 'var(--color-priority-very-high)',
    hiring: 'var(--color-infra-vendor)',
    funding: 'var(--color-infra-gpu)',
    partnership: 'var(--color-accent-primary)',
    ai_workload: 'var(--color-infra-cooling)',
    leadership: 'var(--color-priority-medium)',
    incident: 'var(--color-target-hot)',
  };

  const getEventColor = (type: string): string => {
    const normalizedType = type.toLowerCase().replace(/\s+/g, '_');
    return eventTypeColors[normalizedType] || 'var(--color-text-muted)';
  };

  return (
    <div
      className="rounded-lg p-4"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border-default)'
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: 'var(--color-accent-primary)' }}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h3
            className="font-semibold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Trigger Events
          </h3>
          <span
            className="px-2 py-0.5 rounded text-xs font-data"
            style={{
              backgroundColor: 'var(--color-bg-elevated)',
              color: 'var(--color-text-secondary)'
            }}
          >
            {events.length}
          </span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5"
            style={{
              backgroundColor: 'var(--color-bg-elevated)',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border-default)',
              opacity: isRefreshing ? 0.6 : 1,
            }}
          >
            <svg
              className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {isRefreshing ? 'Discovering...' : 'Refresh'}
          </button>
        )}
      </div>

      {/* Event Type Summary */}
      {events.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {Object.entries(eventsByType).map(([type, typeEvents]) => (
            <span
              key={type}
              className="px-2.5 py-1 rounded-full text-xs font-medium"
              style={{
                backgroundColor: `${getEventColor(type)}15`,
                color: getEventColor(type),
                border: `1px solid ${getEventColor(type)}30`,
              }}
            >
              {type} ({typeEvents.length})
            </span>
          ))}
        </div>
      )}

      {/* Event Cards */}
      {events.length === 0 ? (
        <div
          className="text-center py-8"
          style={{ color: 'var(--color-text-muted)' }}
        >
          <svg className="w-10 h-10 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <p className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>
            No trigger events detected
          </p>
          <p className="text-sm mt-1">
            Trigger events include: expansion, hiring, funding, leadership changes, and incidents.
          </p>
          {onRefresh ? (
            <button
              onClick={onRefresh}
              className="mt-3 px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                backgroundColor: 'var(--color-accent-primary)',
                color: 'white',
              }}
            >
              Discover Events
            </button>
          ) : (
            <p className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
              💡 Click "Refresh" in the account actions to run event discovery.
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {events.slice(0, 10).map((event) => (
            <div
              key={event.id}
              className="p-3 rounded-lg"
              style={{
                backgroundColor: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border-subtle)'
              }}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  {/* Event Type Badge */}
                  <span
                    className="inline-block px-2 py-0.5 rounded text-xs font-medium mb-2"
                    style={{
                      backgroundColor: `${getEventColor(event.event_type)}15`,
                      color: getEventColor(event.event_type),
                    }}
                  >
                    {event.event_type}
                  </span>

                  {/* Description */}
                  <p
                    className="text-sm"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    {event.description}
                  </p>

                  {/* Metadata Row */}
                  <div className="flex items-center gap-4 mt-2 text-xs" style={{ color: 'var(--color-text-muted)' }}>
                    {event.detected_date && (
                      <span>{new Date(event.detected_date).toLocaleDateString()}</span>
                    )}
                    {event.source_url && (
                      <a
                        href={event.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                        style={{ color: 'var(--color-accent-primary)' }}
                      >
                        View source
                      </a>
                    )}
                  </div>
                </div>

                {/* Relevance Score */}
                {event.relevance_score > 0 && (
                  <div
                    className="text-right flex-shrink-0"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    <div
                      className="text-sm font-data font-medium"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      {event.relevance_score}%
                    </div>
                    <div className="text-xs">relevance</div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {events.length > 10 && (
            <p
              className="text-center text-xs pt-2"
              style={{ color: 'var(--color-text-muted)' }}
            >
              + {events.length - 10} more events
            </p>
          )}
        </div>
      )}
    </div>
  );
}
