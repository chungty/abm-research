import { useState } from 'react';
import { AccountList, AccountDetail } from './components';
import { useAccounts, useAccountDetail } from './api/client';
import type { Account } from './types';
import './App.css';

function App() {
  const { accounts, loading: accountsLoading, error: accountsError } = useAccounts();
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const { data: accountDetail, loading: detailLoading } = useAccountDetail(
    selectedAccount?.id || null
  );

  return (
    <div className="h-screen flex flex-col" style={{ backgroundColor: 'var(--color-bg-base)' }}>
      {/* Header */}
      <header
        className="px-6 py-4"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          borderBottom: '1px solid var(--color-border-subtle)'
        }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1
              className="text-2xl font-semibold tracking-tight"
              style={{ color: 'var(--color-text-primary)' }}
            >
              <span className="text-gradient-accent">Verdigris</span>
              <span className="ml-2 font-light" style={{ color: 'var(--color-text-secondary)' }}>
                Signal Intelligence
              </span>
            </h1>
            <p
              className="text-sm mt-0.5"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Account-First Scoring with Infrastructure & MEDDIC Analysis
            </p>
          </div>
          <div className="flex items-center gap-6">
            <div
              className="font-data text-sm tabular-nums"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              <span className="font-semibold" style={{ color: 'var(--color-accent-primary)' }}>
                {accounts.length}
              </span>
              <span className="ml-1.5">accounts</span>
            </div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm transition-colors"
              style={{ color: 'var(--color-text-tertiary)' }}
              onMouseEnter={(e) => e.currentTarget.style.color = 'var(--color-accent-primary)'}
              onMouseLeave={(e) => e.currentTarget.style.color = 'var(--color-text-tertiary)'}
            >
              Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Account List - Left Panel */}
        <div
          className="w-[420px] flex flex-col"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            borderRight: '1px solid var(--color-border-subtle)'
          }}
        >
          {accountsError ? (
            <div className="p-4" style={{ color: 'var(--color-target-hot)' }}>
              <p className="font-medium">Error loading accounts</p>
              <p className="text-sm opacity-80">{accountsError.message}</p>
              <p
                className="text-xs mt-2"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Make sure the Flask API is running at http://localhost:5001
              </p>
            </div>
          ) : (
            <AccountList
              accounts={accounts}
              selectedAccountId={selectedAccount?.id}
              onSelectAccount={setSelectedAccount}
              loading={accountsLoading}
            />
          )}
        </div>

        {/* Account Detail - Right Panel */}
        <div
          className="flex-1 overflow-hidden"
          style={{ backgroundColor: 'var(--color-bg-base)' }}
        >
          {selectedAccount ? (
            detailLoading ? (
              <div className="flex items-center justify-center h-full">
                <div
                  className="animate-spin rounded-full h-8 w-8 border-2"
                  style={{
                    borderColor: 'var(--color-border-default)',
                    borderTopColor: 'var(--color-accent-primary)'
                  }}
                />
              </div>
            ) : accountDetail ? (
              <AccountDetail
                account={accountDetail.account}
                contacts={accountDetail.contacts}
                onClose={() => setSelectedAccount(null)}
              />
            ) : (
              <AccountDetail
                account={selectedAccount}
                contacts={[]}
                onClose={() => setSelectedAccount(null)}
              />
            )
          ) : (
            <EmptyState />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer
        className="px-6 py-2.5 text-xs"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          borderTop: '1px solid var(--color-border-subtle)',
          color: 'var(--color-text-muted)'
        }}
      >
        <div className="flex items-center justify-between">
          <span className="font-medium" style={{ color: 'var(--color-text-tertiary)' }}>
            Verdigris ABM Intelligence System
          </span>
          <span className="font-data tabular-nums">
            Scoring: Infrastructure (35%) + Business Fit (35%) + Buying Signals (30%)
          </span>
        </div>
      </footer>
    </div>
  );
}

function EmptyState() {
  return (
    <div
      className="flex flex-col items-center justify-center h-full"
      style={{ color: 'var(--color-text-tertiary)' }}
    >
      {/* Signal Icon */}
      <div
        className="w-16 h-16 rounded-xl flex items-center justify-center mb-6"
        style={{
          backgroundColor: 'var(--color-bg-card)',
          border: '1px solid var(--color-border-default)'
        }}
      >
        <svg
          className="w-8 h-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ color: 'var(--color-accent-primary)' }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      </div>

      <h2
        className="text-xl font-medium mb-2"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        Select an Account
      </h2>
      <p
        className="text-sm mb-10 max-w-xs text-center"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        Choose an account from the list to view detailed scoring breakdown and contact intelligence
      </p>

      {/* MEDDIC Role Cards */}
      <div className="grid grid-cols-3 gap-4 text-center">
        <RoleCard
          icon="entry"
          label="Entry Points"
          sublabel="Technical Believers"
          color="var(--color-infra-vendor)"
        />
        <RoleCard
          icon="middle"
          label="Middle Deciders"
          sublabel="Tooling Decisions"
          color="var(--color-priority-medium)"
        />
        <RoleCard
          icon="economic"
          label="Economic Buyers"
          sublabel="Budget Authority"
          color="var(--color-infra-cooling)"
        />
      </div>
    </div>
  );
}

function RoleCard({
  icon,
  label,
  sublabel,
  color
}: {
  icon: 'entry' | 'middle' | 'economic';
  label: string;
  sublabel: string;
  color: string;
}) {
  const icons = {
    entry: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
      />
    ),
    middle: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
      />
    ),
    economic: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    ),
  };

  return (
    <div
      className="p-4 rounded-lg transition-all"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: '1px solid var(--color-border-default)'
      }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-2"
        style={{ backgroundColor: `${color}15` }}
      >
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ color }}
        >
          {icons[icon]}
        </svg>
      </div>
      <div
        className="font-medium text-sm"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {label}
      </div>
      <div
        className="text-xs mt-0.5"
        style={{ color: 'var(--color-text-muted)' }}
      >
        {sublabel}
      </div>
    </div>
  );
}

export default App;
