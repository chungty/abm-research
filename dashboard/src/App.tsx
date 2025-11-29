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
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">ABM Intelligence Dashboard</h1>
            <p className="text-sm text-gray-500">
              Account-First Scoring with Infrastructure & MEDDIC Analysis
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              {accounts.length} accounts
            </div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Docs →
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Account List - Left Panel */}
        <div className="w-[400px] border-r border-gray-200 bg-white flex flex-col">
          {accountsError ? (
            <div className="p-4 text-red-600">
              <p className="font-medium">Error loading accounts</p>
              <p className="text-sm">{accountsError.message}</p>
              <p className="text-xs mt-2 text-gray-500">
                Make sure the Flask API is running at http://localhost:5000
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
        <div className="flex-1 overflow-hidden">
          {selectedAccount ? (
            detailLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
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
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-xl font-medium text-gray-600">Select an Account</h2>
              <p className="text-sm mt-2">
                Choose an account from the list to see detailed scoring breakdown
              </p>
              <div className="mt-8 grid grid-cols-3 gap-4 text-center text-sm">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">🔧</div>
                  <div className="font-medium text-gray-700">Entry Points</div>
                  <div className="text-xs text-gray-500">Technical Believers</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">📊</div>
                  <div className="font-medium text-gray-700">Middle Deciders</div>
                  <div className="text-xs text-gray-500">Tooling Decisions</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">💰</div>
                  <div className="font-medium text-gray-700">Economic Buyers</div>
                  <div className="text-xs text-gray-500">Budget Authority</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-2 text-xs text-gray-500">
        <div className="flex items-center justify-between">
          <span>Verdigris ABM Intelligence System</span>
          <span>
            Scoring: Infrastructure (35%) + Business Fit (35%) + Buying Signals (30%)
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
