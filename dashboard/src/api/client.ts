/**
 * API Client for ABM Dashboard
 * Connects to Flask backend at /api/*
 */

import type { Account, Contact, AccountsResponse, AccountDetailResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Accounts
  async getAccounts(params?: {
    page?: number;
    per_page?: number;
    sort_by?: string;
    sort_dir?: 'asc' | 'desc';
    priority?: string[];
    gpu_only?: boolean;
    search?: string;
  }): Promise<AccountsResponse> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.per_page) searchParams.set('per_page', String(params.per_page));
    if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params?.sort_dir) searchParams.set('sort_dir', params.sort_dir);
    if (params?.priority?.length) searchParams.set('priority', params.priority.join(','));
    if (params?.gpu_only) searchParams.set('gpu_only', 'true');
    if (params?.search) searchParams.set('search', params.search);

    const query = searchParams.toString();
    return fetchJson<AccountsResponse>(`/accounts${query ? `?${query}` : ''}`);
  },

  async getAccount(id: string): Promise<AccountDetailResponse> {
    return fetchJson<AccountDetailResponse>(`/accounts/${id}`);
  },

  // Contacts
  async getContacts(accountId: string): Promise<{ contacts: Contact[] }> {
    return fetchJson<{ contacts: Contact[] }>(`/accounts/${accountId}/contacts`);
  },

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return fetchJson<{ status: string; version: string }>('/health');
  },
};

// React hooks for data fetching
import { useState, useEffect, useCallback } from 'react';

export function useAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getAccounts({ per_page: 100 });
      setAccounts(response.accounts);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch accounts'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  return { accounts, loading, error, refetch: fetchAccounts };
}

export function useAccountDetail(accountId: string | null) {
  const [data, setData] = useState<AccountDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!accountId) {
      setData(null);
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getAccount(accountId);
        setData(response);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch account'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [accountId]);

  return { data, loading, error };
}
