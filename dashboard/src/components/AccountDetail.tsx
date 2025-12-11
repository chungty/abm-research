import { useState } from 'react';
import type { Account, Contact, TriggerEvent } from '../types';
import { ScoreBadge } from './ScoreBadge';
import { InfrastructureBreakdown } from './InfrastructureBreakdown';
import { ContactList } from './ContactCard';
import { EnrichmentButton } from './EnrichmentButton';
import { ResearchButton } from './ResearchButton';
import { VendorDiscoveryButton } from './VendorDiscoveryButton';
import { AccountFieldEnrichmentButton } from './AccountFieldEnrichmentButton';
import { TriggerEventsSection } from './TriggerEventsSection';
import { api } from '../api/client';

interface Props {
  account: Account;
  contacts: Contact[];
  triggerEvents?: TriggerEvent[];
  onClose?: () => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export function AccountDetail({ account, contacts, triggerEvents = [], onClose, onRefresh, isLoading = false }: Props) {
  const hasGpu = account.infrastructure_breakdown?.breakdown?.gpu_infrastructure?.detected?.length > 0;
  const [isRefreshingEvents, setIsRefreshingEvents] = useState(false);
  const [discoveredEvents, setDiscoveredEvents] = useState<TriggerEvent[]>([]);
  const [showAccountActions, setShowAccountActions] = useState(true);

  // Combine existing events with newly discovered ones
  const allEvents = [...triggerEvents, ...discoveredEvents];

  // Check if account needs enrichment (missing key data)
  const needsEnrichment = !account.employee_count || account.employee_count === 0 ||
    account.business_model === 'Unknown' || !account.business_model;

  const handleRefreshEvents = async () => {
    setIsRefreshingEvents(true);
    try {
      const result = await api.discoverEvents(account.id, {
        lookback_days: 90,
        save_to_notion: true,
      });
      // Transform API response to TriggerEvent format
      const newEvents: TriggerEvent[] = result.events.map((e, idx) => ({
        id: `discovered_${idx}_${Date.now()}`,
        description: e.description,
        event_type: e.event_type,
        relevance_score: e.relevance_score,
        source_url: e.source_url,
        detected_date: e.detected_date,
      }));
      setDiscoveredEvents(newEvents);
      // Also trigger parent refresh to update from Notion
      onRefresh?.();
    } catch (error) {
      console.error('Failed to discover events:', error);
    } finally {
      setIsRefreshingEvents(false);
    }
  };

  return (
    <div
      className="h-full flex flex-col"
      style={{ backgroundColor: 'var(--color-bg-base)' }}
    >
      {/* Header */}
      <div
        className="p-5"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          borderBottom: '1px solid var(--color-border-subtle)'
        }}
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2
                className="text-2xl font-heading"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {account.name}
              </h2>
              {hasGpu && (
                <span className="badge badge-target">TARGET ICP</span>
              )}
            </div>
            <p style={{ color: 'var(--color-text-tertiary)' }}>{account.domain}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <ScoreBadge
              score={account.account_score}
              priorityLevel={account.account_priority_level}
              size="lg"
            />
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 rounded-lg transition-all"
                style={{
                  color: 'var(--color-text-muted)',
                  backgroundColor: 'transparent'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--color-text-primary)';
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-card)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--color-text-muted)';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
                title="Close panel"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6 animate-fade-in">
        {/* Loading State - Show skeleton while fetching detailed data */}
        {isLoading && (
          <div className="space-y-4 animate-pulse">
            {/* Score cards skeleton */}
            <div className="grid grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="h-24 rounded-lg"
                  style={{ backgroundColor: 'var(--color-bg-card)' }}
                />
              ))}
            </div>
            {/* Content skeleton */}
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-32 rounded-lg"
                style={{ backgroundColor: 'var(--color-bg-card)' }}
              />
            ))}
            <div className="flex items-center justify-center pt-4">
              <span
                className="text-sm"
                style={{ color: 'var(--color-text-muted)' }}
              >
                Loading account details...
              </span>
            </div>
          </div>
        )}

        {/* Actual content - only show when not loading */}
        {!isLoading && (
          <>
        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 1: ACCOUNT ACTIONS
            Purpose: Account-level enrichment and research tools
            ═══════════════════════════════════════════════════════════════════ */}
        <div className="space-y-3">
          <button
            onClick={() => setShowAccountActions(!showAccountActions)}
            className="flex items-center gap-2 w-full text-left group"
          >
            <span
              className="section-header uppercase tracking-wider"
              style={{ color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}
            >
              Account Actions
            </span>
            <span
              className="text-xs transition-colors"
              style={{ color: 'var(--color-text-muted)' }}
            >
              — Enrich account data and run research
            </span>
            <svg
              className={`w-4 h-4 ml-auto transition-transform ${showAccountActions ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              style={{ color: 'var(--color-text-muted)' }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAccountActions && (
            <div className="space-y-3 animate-fade-in">
              {/* Enrichment hint when data is missing */}
              {needsEnrichment && (
                <div
                  className="p-3 rounded-lg flex items-start gap-3"
                  style={{
                    backgroundColor: 'var(--color-priority-medium-bg)',
                    border: '1px solid var(--color-priority-medium-border)'
                  }}
                >
                  <svg
                    className="w-5 h-5 flex-shrink-0 mt-0.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    style={{ color: 'var(--color-priority-medium)' }}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p
                      className="text-sm font-medium"
                      style={{ color: 'var(--color-priority-medium)' }}
                    >
                      Account data incomplete
                    </p>
                    <p
                      className="text-xs mt-0.5"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      Run "Account Field Enrichment" to populate company size, industry, and infrastructure data.
                    </p>
                  </div>
                </div>
              )}

              {/* Account Field Enrichment */}
              <AccountFieldEnrichmentButton
                account={account}
                onEnrichmentComplete={onRefresh}
              />

              {/* Deep Research */}
              <ResearchButton
                account={account}
                onResearchComplete={onRefresh}
              />
            </div>
          )}
        </div>

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 2: SCORE OVERVIEW
            Purpose: Quick view of account scoring components
            ═══════════════════════════════════════════════════════════════════ */}
        <div className="grid grid-cols-4 gap-3">
          <ScoreCard
            label="Account Score"
            score={account.account_score}
            subtitle={account.account_priority_level}
            primary
          />
          <ScoreCard
            label="Infrastructure"
            score={account.infrastructure_score}
            subtitle="35% weight"
          />
          <ScoreCard
            label="Business Fit"
            score={account.business_fit_score}
            subtitle="35% weight"
          />
          <ScoreCard
            label="Buying Signals"
            score={account.buying_signals_score}
            subtitle="30% weight"
          />
        </div>

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 3: INFRASTRUCTURE BREAKDOWN
            Purpose: Detailed infrastructure scoring (expandable)
            ═══════════════════════════════════════════════════════════════════ */}
        {account.infrastructure_breakdown && (
          <InfrastructureBreakdown breakdown={account.infrastructure_breakdown} />
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 4: BUSINESS FIT
            Purpose: Company profile and fit assessment
            ═══════════════════════════════════════════════════════════════════ */}
        <div className="card-surface p-4">
          <div className="flex items-center justify-between mb-4">
            <h3
              className="text-base font-heading"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Business Fit
            </h3>
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-muted)' }}
            >
              Company profile and ICP alignment
            </span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <BusinessFitItem
              label="Industry"
              value={account.business_model || 'Unknown'}
              score={account.account_score_breakdown?.business_fit?.breakdown?.industry_fit?.score}
              needsData={!account.business_model || account.business_model === 'Unknown'}
            />
            <BusinessFitItem
              label="Company Size"
              value={account.employee_count && account.employee_count > 0
                ? `${account.employee_count.toLocaleString()} employees`
                : 'Unknown'}
              score={account.account_score_breakdown?.business_fit?.breakdown?.company_size_fit?.score}
              needsData={!account.employee_count || account.employee_count === 0}
            />
            <BusinessFitItem
              label="Geography"
              value={account.account_score_breakdown?.business_fit?.breakdown?.geographic_fit?.priority || 'Unknown'}
              score={account.account_score_breakdown?.business_fit?.breakdown?.geographic_fit?.score}
            />
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 5: PARTNERSHIP APPROACH (if applicable)
            Purpose: How to engage based on partner relationship type
            ═══════════════════════════════════════════════════════════════════ */}
        {account.partnership_classification && (
          <div className="card-surface p-4">
            <div className="flex items-center justify-between mb-3">
              <h3
                className="text-base font-heading"
                style={{ color: 'var(--color-text-primary)' }}
              >
                Partnership Approach
              </h3>
              <span
                className="text-xs"
                style={{ color: 'var(--color-text-muted)' }}
              >
                How to engage based on partner type
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span
                className="px-3 py-1 rounded-full font-medium text-sm"
                style={{
                  color: 'var(--color-priority-high)',
                  backgroundColor: 'var(--color-priority-high-bg)',
                  border: '1px solid var(--color-priority-high-border)'
                }}
              >
                {account.partnership_classification}
              </span>
              <span
                className="text-sm font-data"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {account.classification_confidence?.toFixed(0)}% confidence
              </span>
            </div>
            <p
              className="text-xs mt-3"
              style={{ color: 'var(--color-text-muted)' }}
            >
              This classification suggests the most effective engagement strategy for this account based on their partner ecosystem role.
            </p>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 6: BUYING SIGNALS (Scoring Context)
            Purpose: Shows how trigger events contribute to buying signal score
            ═══════════════════════════════════════════════════════════════════ */}
        {account.account_score_breakdown?.buying_signals && (
          <div className="card-surface p-4">
            <div className="flex items-center justify-between mb-4">
              <h3
                className="text-base font-heading"
                style={{ color: 'var(--color-text-primary)' }}
              >
                Buying Signal Scoring
              </h3>
              <span
                className="text-xs"
                style={{ color: 'var(--color-text-muted)' }}
              >
                How triggers contribute to the 30% buying signals score
              </span>
            </div>
            <div className="space-y-4">
              <SignalSection
                label="High-Value Triggers"
                items={account.account_score_breakdown.buying_signals.breakdown?.trigger_events?.high_value_triggers || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.trigger_events?.score}
              />
              <SignalSection
                label="Expansion Signals"
                items={account.account_score_breakdown.buying_signals.breakdown?.expansion_signals?.detected || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.expansion_signals?.score}
              />
              <SignalSection
                label="Hiring Signals"
                items={account.account_score_breakdown.buying_signals.breakdown?.hiring_signals?.detected || []}
                score={account.account_score_breakdown.buying_signals.breakdown?.hiring_signals?.score}
              />
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 7: TRIGGER EVENTS (Detailed Intelligence)
            Purpose: Actionable event details with sources and dates
            ═══════════════════════════════════════════════════════════════════ */}
        <TriggerEventsSection
          events={allEvents}
          onRefresh={handleRefreshEvents}
          isRefreshing={isRefreshingEvents}
        />

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 8: CONTACT INTELLIGENCE
            Purpose: Contact discovery, enrichment, and MEDDIC scoring
            ═══════════════════════════════════════════════════════════════════ */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span
              className="section-header uppercase tracking-wider"
              style={{ color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}
            >
              Contact Intelligence
            </span>
            <span
              className="text-xs"
              style={{ color: 'var(--color-text-muted)' }}
            >
              — Discover and score contacts for outreach
            </span>
          </div>

          {/* Contact Discovery & MEDDIC Scoring */}
          <EnrichmentButton
            account={account}
            contactsCount={contacts.length}
            onEnrichmentComplete={onRefresh}
          />

          {/* Vendor Discovery */}
          <VendorDiscoveryButton
            account={account}
            onDiscoveryComplete={onRefresh}
          />
        </div>

        {/* ═══════════════════════════════════════════════════════════════════
            SECTION 9: CONTACTS LIST
            Purpose: Display discovered contacts grouped by MEDDIC role tier
            ═══════════════════════════════════════════════════════════════════ */}
        <ContactList contacts={contacts} account={account} title={`Contacts at ${account.name}`} />
          </>
        )}
      </div>
    </div>
  );
}

function ScoreCard({
  label,
  score,
  subtitle,
  primary = false,
}: {
  label: string;
  score: number;
  subtitle: string;
  primary?: boolean;
}) {
  const getColor = (s: number) => {
    if (s >= 80) return 'var(--color-priority-very-high)';
    if (s >= 60) return 'var(--color-priority-high)';
    if (s >= 40) return 'var(--color-priority-medium)';
    return 'var(--color-text-tertiary)';
  };

  return (
    <div
      className="rounded-lg p-4"
      style={{
        backgroundColor: primary ? 'var(--color-accent-primary-muted)' : 'var(--color-bg-card)',
        border: primary
          ? '1px solid var(--color-accent-primary)'
          : '1px solid var(--color-border-default)'
      }}
    >
      <div
        className="score-value text-2xl animate-count"
        style={{ color: getColor(score) }}
      >
        {Math.round(score)}
      </div>
      <div
        className="text-sm font-medium"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {label}
      </div>
      <div
        className="text-xs"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {subtitle}
      </div>
    </div>
  );
}

function BusinessFitItem({
  label,
  value,
  score,
  needsData = false,
}: {
  label: string;
  value: string;
  score?: number;
  needsData?: boolean;
}) {
  return (
    <div
      className="p-3 rounded-md relative"
      style={{
        backgroundColor: 'var(--color-bg-elevated)',
        border: needsData ? '1px dashed var(--color-priority-medium-border)' : 'none'
      }}
    >
      {needsData && (
        <div
          className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center"
          style={{
            backgroundColor: 'var(--color-priority-medium-bg)',
            border: '1px solid var(--color-priority-medium-border)'
          }}
          title="Run Account Field Enrichment to populate this data"
        >
          <span
            className="text-xs font-bold"
            style={{ color: 'var(--color-priority-medium)' }}
          >
            ?
          </span>
        </div>
      )}
      <div className="score-label mb-1">{label}</div>
      <div
        className="font-medium text-sm"
        style={{ color: needsData ? 'var(--color-text-muted)' : 'var(--color-text-primary)' }}
      >
        {value}
      </div>
      {score !== undefined && (
        <div
          className="text-xs font-data mt-1"
          style={{ color: 'var(--color-text-muted)' }}
        >
          Score: {Math.round(score)}
        </div>
      )}
    </div>
  );
}

function SignalSection({
  label,
  items,
  score,
}: {
  label: string;
  items: string[];
  score?: number;
}) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <div
          className="text-sm font-medium mb-1"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {label}
        </div>
        {items.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {items.map((item, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  color: 'var(--color-priority-high)',
                  backgroundColor: 'var(--color-priority-high-bg)',
                  border: '1px solid var(--color-priority-high-border)'
                }}
              >
                {item}
              </span>
            ))}
          </div>
        ) : (
          <span
            className="text-xs"
            style={{ color: 'var(--color-text-muted)' }}
          >
            None detected
          </span>
        )}
      </div>
      {score !== undefined && (
        <span
          className="font-data font-medium text-sm"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {Math.round(score)}
        </span>
      )}
    </div>
  );
}
