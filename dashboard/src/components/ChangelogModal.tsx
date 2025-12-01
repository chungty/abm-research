import { useState } from 'react';
import { changelog, CURRENT_VERSION, getCategoryInfo, type ChangelogEntry } from '../data/changelog';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function ChangelogModal({ isOpen, onClose }: Props) {
  const [expandedVersion, setExpandedVersion] = useState<string | null>(changelog[0]?.version || null);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="w-full max-w-2xl max-h-[80vh] flex flex-col rounded-xl overflow-hidden animate-fade-in"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border-default)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
        }}
      >
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            borderBottom: '1px solid var(--color-border-subtle)'
          }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-priority-high) 100%)'
              }}
            >
              <SparklesIcon />
            </div>
            <div>
              <h2
                className="text-lg font-heading"
                style={{ color: 'var(--color-text-primary)' }}
              >
                What's New
              </h2>
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Version history and release notes
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-all"
            style={{
              color: 'var(--color-text-muted)',
              backgroundColor: 'transparent'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--color-text-primary)';
              e.currentTarget.style.backgroundColor = 'var(--color-bg-elevated)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--color-text-muted)';
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {changelog.map((entry) => (
            <ChangelogEntryCard
              key={entry.version}
              entry={entry}
              isExpanded={expandedVersion === entry.version}
              isLatest={entry.version === CURRENT_VERSION}
              onToggle={() => setExpandedVersion(
                expandedVersion === entry.version ? null : entry.version
              )}
            />
          ))}
        </div>

        {/* Footer */}
        <div
          className="px-6 py-3 text-xs"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            borderTop: '1px solid var(--color-border-subtle)',
            color: 'var(--color-text-muted)'
          }}
        >
          <div className="flex items-center justify-between">
            <span>Verdigris Signal Intelligence</span>
            <span className="font-data">{CURRENT_VERSION}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChangelogEntryCard({
  entry,
  isExpanded,
  isLatest,
  onToggle
}: {
  entry: ChangelogEntry;
  isExpanded: boolean;
  isLatest: boolean;
  onToggle: () => void;
}) {
  return (
    <div
      className="rounded-lg overflow-hidden transition-all"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: isLatest
          ? '1px solid var(--color-accent-primary)'
          : '1px solid var(--color-border-default)'
      }}
    >
      {/* Collapsed Header */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between text-left transition-all"
        style={{
          backgroundColor: isExpanded ? 'var(--color-bg-elevated)' : 'transparent'
        }}
      >
        <div className="flex items-center gap-3">
          <span
            className="px-2 py-0.5 rounded text-xs font-data font-medium"
            style={{
              backgroundColor: isLatest
                ? 'var(--color-accent-primary-muted)'
                : 'var(--color-bg-elevated)',
              color: isLatest
                ? 'var(--color-accent-primary)'
                : 'var(--color-text-secondary)',
              border: isLatest
                ? '1px solid var(--color-accent-primary)'
                : '1px solid var(--color-border-subtle)'
            }}
          >
            {entry.version}
          </span>
          <span
            className="font-medium"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {entry.title}
          </span>
          {isLatest && (
            <span
              className="px-1.5 py-0.5 rounded text-xs font-medium"
              style={{
                backgroundColor: 'var(--color-priority-high-bg)',
                color: 'var(--color-priority-high)'
              }}
            >
              Latest
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span
            className="text-xs font-data"
            style={{ color: 'var(--color-text-muted)' }}
          >
            {entry.date}
          </span>
          <svg
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            style={{ color: 'var(--color-text-tertiary)' }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div
          className="px-4 pb-4 space-y-4 animate-fade-in"
          style={{ borderTop: '1px solid var(--color-border-subtle)' }}
        >
          {/* Highlights */}
          <div className="pt-4">
            <h4
              className="text-xs font-medium uppercase tracking-wide mb-2"
              style={{ color: 'var(--color-text-muted)' }}
            >
              Highlights
            </h4>
            <div className="flex flex-wrap gap-2">
              {entry.highlights.map((highlight, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: 'var(--color-priority-high-bg)',
                    color: 'var(--color-priority-high)',
                    border: '1px solid var(--color-priority-high-border)'
                  }}
                >
                  {highlight}
                </span>
              ))}
            </div>
          </div>

          {/* Features by Category */}
          {entry.features.map((featureGroup, idx) => {
            const categoryInfo = getCategoryInfo(featureGroup.category);
            return (
              <div key={idx}>
                <h4
                  className="text-xs font-medium mb-2 flex items-center gap-2"
                  style={{ color: categoryInfo.color }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: categoryInfo.color }}
                  />
                  {categoryInfo.name}
                </h4>
                <ul className="space-y-1.5 pl-3">
                  {featureGroup.items.map((item, itemIdx) => (
                    <li
                      key={itemIdx}
                      className="text-sm flex items-start gap-2"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      <span
                        className="mt-1.5 w-1 h-1 rounded-full flex-shrink-0"
                        style={{ backgroundColor: 'var(--color-text-muted)' }}
                      />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function SparklesIcon() {
  return (
    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
      />
    </svg>
  );
}
