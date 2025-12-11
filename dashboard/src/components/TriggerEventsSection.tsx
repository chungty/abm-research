import { useState } from 'react';
import type { TriggerEvent } from '../types';

interface Props {
  events: TriggerEvent[];
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

/**
 * Generate a headline from description if not provided
 * Takes first sentence or truncates at reasonable length
 */
function generateHeadline(description: string, maxLength: number = 80): string {
  // Try to get first sentence
  const firstSentence = description.split(/[.!?]/)[0];
  if (firstSentence && firstSentence.length <= maxLength) {
    return firstSentence.trim();
  }
  // Otherwise truncate at word boundary
  if (description.length <= maxLength) return description;
  const truncated = description.substring(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');
  return (lastSpace > 0 ? truncated.substring(0, lastSpace) : truncated) + '...';
}

/**
 * TriggerEventsSection - Displays trigger events within the AccountDetail view
 * Shows event cards with type badges, descriptions, and metadata
 * Collapsible with headline-first view for quick scanning
 */
export function TriggerEventsSection({ events, onRefresh, isRefreshing }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);
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
      {/* Header - Clickable to expand/collapse */}
      <button
        onClick={() => events.length > 0 && setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full mb-4 text-left"
        disabled={events.length === 0}
      >
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
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-muted)' }}
          >
            — Actionable intelligence with sources
          </span>
        </div>

        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={(e) => { e.stopPropagation(); onRefresh(); }}
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
              {isRefreshing ? 'Discovering...' : 'Discover'}
            </button>
          )}
          {events.length > 0 && (
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style={{ color: 'var(--color-text-muted)' }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
      </button>

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
          {onRefresh && (
            <p className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
              Click "Discover" above to find recent company events.
            </p>
          )}
        </div>
      ) : (
        <>
          {/* Collapsed view - Headlines only */}
          {!isExpanded && (
            <div className="space-y-2">
              {events.slice(0, 5).map((event) => (
                <div
                  key={event.id}
                  className="flex items-center gap-2 p-2 rounded-md transition-colors cursor-pointer hover:bg-[rgba(255,255,255,0.02)]"
                  onClick={() => setIsExpanded(true)}
                >
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: getEventColor(event.event_type) }}
                  />
                  <span
                    className="text-xs font-medium px-1.5 py-0.5 rounded"
                    style={{
                      backgroundColor: `${getEventColor(event.event_type)}15`,
                      color: getEventColor(event.event_type),
                    }}
                  >
                    {event.event_type}
                  </span>
                  <span
                    className="text-sm flex-1 truncate"
                    style={{ color: 'var(--color-text-secondary)' }}
                  >
                    {event.headline || generateHeadline(event.description)}
                  </span>
                  {event.source_url && (
                    <a
                      href={event.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs hover:underline flex-shrink-0"
                      style={{ color: 'var(--color-accent-primary)' }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      Source
                    </a>
                  )}
                </div>
              ))}
              {events.length > 5 && (
                <p
                  className="text-center text-xs pt-1"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  + {events.length - 5} more — click to expand
                </p>
              )}
            </div>
          )}

          {/* Expanded view - Full details */}
          {isExpanded && (
            <div className="space-y-3 animate-fade-in">
              {events.slice(0, 10).map((event) => {
                const isEventExpanded = expandedEventId === event.id;
                const headline = event.headline || generateHeadline(event.description);

                return (
                  <div
                    key={event.id}
                    className="p-3 rounded-lg transition-colors"
                    style={{
                      backgroundColor: 'var(--color-bg-elevated)',
                      border: `1px solid ${isEventExpanded ? 'var(--color-accent-primary)' : 'var(--color-border-subtle)'}`
                    }}
                  >
                    {/* Clickable headline row */}
                    <button
                      onClick={() => setExpandedEventId(isEventExpanded ? null : event.id)}
                      className="flex items-start justify-between gap-3 w-full text-left"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {/* Event Type Badge */}
                          <span
                            className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                            style={{
                              backgroundColor: `${getEventColor(event.event_type)}15`,
                              color: getEventColor(event.event_type),
                            }}
                          >
                            {event.event_type}
                          </span>
                          {event.detected_date && (
                            <span
                              className="text-xs"
                              style={{ color: 'var(--color-text-muted)' }}
                            >
                              {new Date(event.detected_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>

                        {/* Headline */}
                        <p
                          className="text-sm font-medium"
                          style={{ color: 'var(--color-text-primary)' }}
                        >
                          {headline}
                        </p>
                      </div>

                      {/* Relevance Score + Expand indicator */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {event.relevance_score > 0 && (
                          <span
                            className="text-sm font-data"
                            style={{ color: 'var(--color-text-secondary)' }}
                          >
                            {event.relevance_score}%
                          </span>
                        )}
                        <svg
                          className={`w-4 h-4 transition-transform ${isEventExpanded ? 'rotate-180' : ''}`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          style={{ color: 'var(--color-text-muted)' }}
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </button>

                    {/* Expanded details */}
                    {isEventExpanded && (
                      <div className="mt-3 pt-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
                        {/* Full description */}
                        <p
                          className="text-sm mb-2"
                          style={{ color: 'var(--color-text-secondary)' }}
                        >
                          {event.description}
                        </p>

                        {/* Source link */}
                        {event.source_url && (
                          <a
                            href={event.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs hover:underline"
                            style={{ color: 'var(--color-accent-primary)' }}
                          >
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            View original source
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

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
        </>
      )}
    </div>
  );
}
