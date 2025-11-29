import { useState, useMemo } from 'react';
import type { Account, PriorityLevel, SortField, SortDirection } from '../types';
import { AccountCard } from './AccountCard';

interface Props {
  accounts: Account[];
  selectedAccountId?: string;
  onSelectAccount: (account: Account) => void;
  loading?: boolean;
}

export function AccountList({
  accounts,
  selectedAccountId,
  onSelectAccount,
  loading = false,
}: Props) {
  const [sortField, setSortField] = useState<SortField>('account_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filterPriority, setFilterPriority] = useState<PriorityLevel[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showGpuOnly, setShowGpuOnly] = useState(false);

  const sortedAccounts = useMemo(() => {
    let filtered = [...accounts];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        a =>
          a.name.toLowerCase().includes(query) ||
          a.domain.toLowerCase().includes(query) ||
          a.business_model?.toLowerCase().includes(query)
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
  }, [accounts, sortField, sortDirection, filterPriority, searchQuery, showGpuOnly]);

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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header & Filters */}
      <div className="bg-white border-b border-gray-200 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            Accounts
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({sortedAccounts.length})
            </span>
          </h2>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showGpuOnly}
              onChange={e => setShowGpuOnly(e.target.checked)}
              className="rounded border-gray-300 text-red-600 focus:ring-red-500"
            />
            <span className="text-red-700 font-medium">🎯 GPU Only</span>
          </label>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search accounts..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {/* Sort & Filter */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-gray-500">Sort:</span>
          <SortButton
            label="Score"
            active={sortField === 'account_score'}
            direction={sortField === 'account_score' ? sortDirection : undefined}
            onClick={() => handleSort('account_score')}
          />
          <SortButton
            label="Infrastructure"
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

          <span className="text-xs text-gray-500 ml-2">Filter:</span>
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
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        {sortedAccounts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
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
      className={`px-2 py-1 text-xs rounded transition-colors ${
        active
          ? 'bg-blue-100 text-blue-700 font-medium'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      {label}
      {active && direction && (
        <span className="ml-1">{direction === 'asc' ? '↑' : '↓'}</span>
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
  const colors: Record<string, string> = {
    'Very High': 'bg-emerald-100 text-emerald-700 border-emerald-200',
    High: 'bg-blue-100 text-blue-700 border-blue-200',
    Medium: 'bg-amber-100 text-amber-700 border-amber-200',
    Low: 'bg-gray-100 text-gray-600 border-gray-200',
  };

  return (
    <button
      onClick={onClick}
      className={`px-2 py-0.5 text-xs rounded-full border transition-all ${
        active ? colors[label] + ' ring-2 ring-offset-1' : 'bg-white text-gray-500 border-gray-200'
      }`}
    >
      {label}
    </button>
  );
}
