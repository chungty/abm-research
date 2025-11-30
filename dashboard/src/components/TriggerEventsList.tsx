import { useTriggerEvents } from '../api/client';

interface TriggerEvent {
  id: string;
  event_type: string;
  description: string;
  source_url?: string;
  confidence?: string;
  urgency_level?: string;
  detected_date?: string;
  account_name?: string;
}

export function TriggerEventsList() {
  const { events, total, loading, error } = useTriggerEvents();

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
        <p className="font-medium">Error loading trigger events</p>
        <p className="text-sm opacity-80">{error.message}</p>
      </div>
    );
  }

  const eventTypeColors: Record<string, string> = {
    'expansion': 'var(--color-priority-very-high)',
    'funding': 'var(--color-priority-high)',
    'ai_workload': 'var(--color-accent-primary)',
    'partnership': 'var(--color-priority-medium)',
    'hiring': 'var(--color-infra-vendor)',
    'leadership': 'var(--color-infra-cooling)',
    'incident': 'var(--color-target-hot)',
  };

  const urgencyColors: Record<string, string> = {
    'High': 'var(--color-priority-very-high)',
    'Medium': 'var(--color-priority-medium)',
    'Low': 'var(--color-text-tertiary)',
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2
          className="text-lg font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Trigger Events
          <span
            className="ml-2 text-sm font-normal font-data"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            ({total})
          </span>
        </h2>
      </div>

      {events.length === 0 ? (
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
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <p>No trigger events found</p>
          <p className="text-sm mt-1">Run research on accounts to discover trigger events</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {events.map((event: TriggerEvent) => (
            <TriggerEventCard
              key={event.id}
              event={event}
              typeColors={eventTypeColors}
              urgencyColors={urgencyColors}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TriggerEventCard({
  event,
  typeColors,
  urgencyColors
}: {
  event: TriggerEvent;
  typeColors: Record<string, string>;
  urgencyColors: Record<string, string>;
}) {
  const typeColor = typeColors[event.event_type?.toLowerCase()] || 'var(--color-text-secondary)';
  const urgencyColor = urgencyColors[event.urgency_level || 'Low'] || 'var(--color-text-muted)';

  return (
    <div
      className="p-4 rounded-lg transition-all"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border-default)'
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className="px-2 py-0.5 rounded text-xs font-medium"
              style={{
                backgroundColor: `${typeColor}15`,
                color: typeColor,
                border: `1px solid ${typeColor}30`
              }}
            >
              {event.event_type?.replace('_', ' ') || 'Unknown'}
            </span>
            {event.urgency_level && (
              <span
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  backgroundColor: `${urgencyColor}15`,
                  color: urgencyColor,
                }}
              >
                {event.urgency_level} Urgency
              </span>
            )}
          </div>
          <p
            className="text-sm"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {event.description}
          </p>
          {event.account_name && (
            <p
              className="text-xs mt-1"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Account: {event.account_name}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-1">
          {event.confidence && (
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {event.confidence} confidence
            </span>
          )}
          {event.detected_date && (
            <span
              className="text-xs font-data"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {new Date(event.detected_date).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
      {event.source_url && (
        <div className="mt-2 pt-2" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <a
            href={event.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs transition-colors"
            style={{ color: 'var(--color-accent-primary)' }}
          >
            View Source →
          </a>
        </div>
      )}
    </div>
  );
}
