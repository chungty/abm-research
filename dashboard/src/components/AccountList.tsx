import { useState, useMemo } from 'react';
import type { Account, PriorityLevel, SortField, SortDirection } from '../types';
import { AccountCard, getAccountStatus, type AccountStatus } from './AccountCard';
import { useDebounce } from '../hooks/useDebounce';

interface Props {
  accounts: Account[];
  selectedAccountId?: string;
  onSelectAccount: (account: Account) => void;
  onAddAccount?: () => void;
  loading?: boolean;
}

export function AccountList({
  accounts,
  selectedAccountId,
  onSelectAccount,
  onAddAccount,
  loading = false,
}: Props) {
  const [sortField, setSortField] = useState<SortField>('account_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filterPriority, setFilterPriority] = useState<PriorityLevel[]>([]);
  const [filterStatus, setFilterStatus] = useState<AccountStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showGpuOnly, setShowGpuOnly] = useState(false);

  // Debounce search for smoother filtering (200ms delay)
  const debouncedSearch = useDebounce(searchQuery, 200);

  // Compute status counts for all accounts
  const statusCounts = useMemo(() => {
    const counts = { hot: 0, warming: 0, quiet: 0 };
    accounts.forEach(account => {
      const status = getAccountStatus(account).status;
      counts[status]++;
    });
    return counts;
  }, [accounts]);

  const sortedAccounts = useMemo(() => {
    let filtered = [...accounts];

    // Search filter (using debounced value for performance)
    if (debouncedSearch) {
      const query = debouncedSearch.toLowerCase();
      filtered = filtered.filter(
        a =>
          a.name.toLowerCase().includes(query) ||
          a.domain.toLowerCase().includes(query)
      );
    }

    // Priority filter
    if (filterPriority.length > 0) {
      filtered = filtered.filter(a => filterPriority.includes(a.account_priority_level));
    }

    // GPU filter
    if (showGpuOnly) {
      filtered = filtered.filter(
        a => a.infrastructure_breakdown?.breakdown?.gpu_infrastructure?.detected?.length > 0
      );
    }

    // Status filter
    if (filterStatus) {
      filtered = filtered.filter(a => getAccountStatus(a).status === filterStatus);
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal: number | string;
      let bVal: number | string;

      switch (sortField) {
        case 'account_score':
          aVal = a.account_score;
          bVal = b.account_score;
          break;
        case 'infrastructure_score':
          aVal = a.infrastructure_score;
          bVal = b.infrastructure_score;
          break;
        case 'name':
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case 'contacts_count':
          aVal = a.contacts_count || 0;
          bVal = b.contacts_count || 0;
          break;
        default:
          aVal = a.account_score;
          bVal = b.account_score;
      }

      if (typeof aVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal);
      }

      return sortDirection === 'asc' ? aVal - (bVal as number) : (bVal as number) - aVal;
    });

    return filtered;
  }, [accounts, sortField, sortDirection, filterPriority, debouncedSearch, showGpuOnly, filterStatus]);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(d => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const togglePriority = (priority: PriorityLevel) => {
    setFilterPriority(prev =>
      prev.includes(priority) ? prev.filter(p => p !== priority) : [...prev, priority]
    );
  };

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

  return (
    <div className="flex flex-col h-full">
      {/* Header & Filters */}
      <div
        className="p-4 space-y-3"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          borderBottom: '1px solid var(--color-border-subtle)'
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2
              className="text-lg font-semibold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Accounts
              <span
                className="ml-2 text-sm font-normal font-data"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                ({sortedAccounts.length})
              </span>
            </h2>
            {onAddAccount && (
              <button
                onClick={onAddAccount}
                className="p-1.5 rounded-lg transition-all"
                style={{
                  backgroundColor: 'var(--color-accent-primary)',
                  color: 'white',
                }}
                title="Add new account"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            )}
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer group">
            <input
              type="checkbox"
              checked={showGpuOnly}
              onChange={e => setShowGpuOnly(e.target.checked)}
              className="sr-only"
            />
            <div
              className="w-4 h-4 rounded flex items-center justify-center transition-all"
              style={{
                backgroundColor: showGpuOnly ? 'var(--color-target-hot-bg)' : 'var(--color-bg-card)',
                border: `1px solid ${showGpuOnly ? 'var(--color-target-hot-border)' : 'var(--color-border-default)'}`
              }}
            >
              {showGpuOnly && (
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20" style={{ color: 'var(--color-target-hot)' }}>
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <span
              className="font-medium transition-colors"
              style={{ color: showGpuOnly ? 'var(--color-target-hot)' : 'var(--color-text-tertiary)' }}
            >
              GPU/AI Only
            </span>
          </label>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search accounts..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="input-field"
        />

        {/* Status Quick Filters */}
        <div className="flex items-center gap-2">
          <StatusFilterButton
            label="Hot"
            count={statusCounts.hot}
            active={filterStatus === 'hot'}
            onClick={() => setFilterStatus(filterStatus === 'hot' ? null : 'hot')}
            status="hot"
          />
          <StatusFilterButton
            label="Warming"
            count={statusCounts.warming}
            active={filterStatus === 'warming'}
            onClick={() => setFilterStatus(filterStatus === 'warming' ? null : 'warming')}
            status="warming"
          />
          <StatusFilterButton
            label="Quiet"
            count={statusCounts.quiet}
            active={filterStatus === 'quiet'}
            onClick={() => setFilterStatus(filterStatus === 'quiet' ? null : 'quiet')}
            status="quiet"
          />
          {filterStatus && (
            <button
              onClick={() => setFilterStatus(null)}
              className="text-xs px-2 py-1 rounded transition-colors"
              style={{ color: 'var(--color-text-muted)' }}
            >
              Clear
            </button>
          )}
        </div>

        {/* Sort & Filter */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="section-header">Sort</span>
          <SortButton
            label="Score"
            active={sortField === 'account_score'}
            direction={sortField === 'account_score' ? sortDirection : undefined}
            onClick={() => handleSort('account_score')}
          />
          <SortButton
            label="Infra"
            active={sortField === 'infrastructure_score'}
            direction={sortField === 'infrastructure_score' ? sortDirection : undefined}
            onClick={() => handleSort('infrastructure_score')}
          />
          <SortButton
            label="Name"
            active={sortField === 'name'}
            direction={sortField === 'name' ? sortDirection : undefined}
            onClick={() => handleSort('name')}
          />

          <div className="w-px h-4 mx-1" style={{ backgroundColor: 'var(--color-border-default)' }} />

          <span className="section-header">Filter</span>
          {(['Very High', 'High', 'Medium', 'Low'] as PriorityLevel[]).map(priority => (
            <FilterChip
              key={priority}
              label={priority}
              active={filterPriority.includes(priority)}
              onClick={() => togglePriority(priority)}
            />
          ))}
        </div>
      </div>

      {/* Account List */}
      <div
        className="flex-1 overflow-y-auto p-3 space-y-2"
        style={{ backgroundColor: 'var(--color-bg-base)' }}
      >
        {sortedAccounts.length === 0 ? (
          <div
            className="text-center py-8"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            No accounts match your filters
          </div>
        ) : (
          sortedAccounts.map(account => (
            <AccountCard
              key={account.id}
              account={account}
              selected={account.id === selectedAccountId}
              onClick={() => onSelectAccount(account)}
            />
          ))
        )}
      </div>
    </div>
  );
}

function SortButton({
  label,
  active,
  direction,
  onClick,
}: {
  label: string;
  active: boolean;
  direction?: SortDirection;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`btn ${active ? 'btn-subtle active' : 'btn-ghost'}`}
      style={{
        fontSize: 'var(--text-xs)',
        padding: '0.25rem 0.5rem'
      }}
    >
      {label}
      {active && direction && (
        <span className="ml-1 opacity-70">{direction === 'asc' ? '↑' : '↓'}</span>
      )}
    </button>
  );
}

function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  const getColor = (priority: string) => {
    switch (priority) {
      case 'Very High':
        return active
          ? { color: 'var(--color-priority-very-high)', bg: 'var(--color-priority-very-high-bg)', border: 'var(--color-priority-very-high-border)' }
          : { color: 'var(--color-text-tertiary)', bg: 'transparent', border: 'var(--color-border-default)' };
      case 'High':
        return active
          ? { color: 'var(--color-priority-high)', bg: 'var(--color-priority-high-bg)', border: 'var(--color-priority-high-border)' }
          : { color: 'var(--color-text-tertiary)', bg: 'transparent', border: 'var(--color-border-default)' };
      case 'Medium':
        return active
          ? { color: 'var(--color-priority-medium)', bg: 'var(--color-priority-medium-bg)', border: 'var(--color-priority-medium-border)' }
          : { color: 'var(--color-text-tertiary)', bg: 'transparent', border: 'var(--color-border-default)' };
      default:
        return active
          ? { color: 'var(--color-priority-low)', bg: 'var(--color-priority-low-bg)', border: 'var(--color-priority-low-border)' }
          : { color: 'var(--color-text-tertiary)', bg: 'transparent', border: 'var(--color-border-default)' };
    }
  };

  const colors = getColor(label);

  return (
    <button
      onClick={onClick}
      className="transition-all"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.125rem 0.5rem',
        fontSize: 'var(--text-xs)',
        fontWeight: 500,
        borderRadius: 'var(--radius-full)',
        border: `1px solid ${colors.border}`,
        backgroundColor: colors.bg,
        color: colors.color,
        cursor: 'pointer'
      }}
    >
      {label}
    </button>
  );
}

function StatusFilterButton({
  label,
  count,
  active,
  onClick,
  status
}: {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
  status: AccountStatus;
}) {
  const getStatusColors = (s: AccountStatus, isActive: boolean) => {
    if (s === 'hot') {
      return isActive
        ? { color: '#fff', bg: 'var(--color-priority-very-high)', border: 'var(--color-priority-very-high)' }
        : { color: 'var(--color-priority-very-high)', bg: 'var(--color-priority-very-high-bg)', border: 'var(--color-priority-very-high-border)' };
    }
    if (s === 'warming') {
      return isActive
        ? { color: '#fff', bg: 'var(--color-priority-medium)', border: 'var(--color-priority-medium)' }
        : { color: 'var(--color-priority-medium)', bg: 'var(--color-priority-medium-bg)', border: 'var(--color-priority-medium-border)' };
    }
    return isActive
      ? { color: '#fff', bg: 'var(--color-text-muted)', border: 'var(--color-text-muted)' }
      : { color: 'var(--color-text-muted)', bg: 'var(--color-bg-elevated)', border: 'var(--color-border-subtle)' };
  };

  const colors = getStatusColors(status, active);

  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all"
      style={{
        backgroundColor: colors.bg,
        color: colors.color,
        border: `1px solid ${colors.border}`
      }}
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{
          backgroundColor: status === 'hot'
            ? active ? '#fff' : 'var(--color-priority-very-high)'
            : status === 'warming'
              ? active ? '#fff' : 'var(--color-priority-medium)'
              : active ? '#fff' : 'var(--color-text-muted)'
        }}
      />
      {label}
      <span
        className="px-1 py-0.5 rounded text-xs"
        style={{
          backgroundColor: active ? 'rgba(255,255,255,0.2)' : 'var(--color-bg-card)',
          color: active ? '#fff' : 'var(--color-text-muted)'
        }}
      >
        {count}
      </span>
    </button>
  );
}
