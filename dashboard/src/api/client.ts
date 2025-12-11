/**
 * API Client for ABM Dashboard
 * Connects to Flask backend at /api/*
 */

import type { Account, Contact, AccountsResponse, AccountDetailResponse, PartnerRankingsResponse } from '../types';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

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

  // Partnerships
  async getPartnerships(): Promise<{ partnerships: any[]; total: number }> {
    return fetchJson<{ partnerships: any[]; total: number }>('/partnerships');
  },

  // Trigger Events
  async getTriggerEvents(accountId?: string): Promise<{ trigger_events: any[]; total: number }> {
    const query = accountId ? `?account_id=${accountId}` : '';
    return fetchJson<{ trigger_events: any[]; total: number }>(`/trigger-events${query}`);
  },

  // Create a new account (POST)
  async createAccount(data: {
    name: string;
    domain: string;
    industry?: string;
    employee_count?: number;
    business_model?: string;
    physical_infrastructure?: string;
  }): Promise<{
    success: boolean;
    id: string;
    notion_id: string;
    name: string;
    domain: string;
    message: string;
  }> {
    return fetchJson('/accounts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Run research pipeline for an account (POST)
  async runResearch(accountId: string, options?: {
    phases?: string[];
    force?: boolean;
  }): Promise<{
    status: string;
    account_id: string;
    phases_completed: string[];
    message: string;
  }> {
    return fetchJson(`/accounts/${accountId}/research`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    });
  },

  // Discover trigger events for an account (POST)
  async discoverEvents(accountId: string, options?: {
    event_types?: string[];
    lookback_days?: number;
    save_to_notion?: boolean;
  }): Promise<{
    status: string;
    account_name: string;
    total: number;
    saved_to_notion: number;
    event_type_counts: Record<string, number>;
    events: Array<{
      event_type: string;
      description: string;
      source_url: string;
      source_type: string;
      confidence_score: number;
      relevance_score: number;
      urgency_level: string;
      detected_date: string;
      event_date: string | null;
    }>;
  }> {
    return fetchJson(`/accounts/${accountId}/discover-events`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    });
  },

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return fetchJson<{ status: string; version: string }>('/health');
  },

  // Partner Rankings (strategic value scoring)
  async getPartnerRankings(): Promise<PartnerRankingsResponse> {
    return fetchJson<PartnerRankingsResponse>('/partner-rankings');
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

  const fetchData = useCallback(async () => {
    if (!accountId) {
      setData(null);
      return;
    }
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
  }, [accountId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

export function usePartnerships() {
  const [data, setData] = useState<{ partnerships: any[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getPartnerships();
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch partnerships'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { partnerships: data?.partnerships || [], total: data?.total || 0, loading, error, refetch: fetchData };
}

export function useTriggerEvents(accountId?: string) {
  const [data, setData] = useState<{ trigger_events: any[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getTriggerEvents(accountId);
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch trigger events'));
    } finally {
      setLoading(false);
    }
  }, [accountId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { events: data?.trigger_events || [], total: data?.total || 0, loading, error, refetch: fetchData };
}

export function usePartnerRankings() {
  const [data, setData] = useState<PartnerRankingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.getPartnerRankings();
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch partner rankings'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    rankings: data?.partner_rankings || [],
    total: data?.total || 0,
    totalAccounts: data?.total_accounts || 0,
    methodology: data?.scoring_methodology || null,
    loading,
    error,
    refetch: fetchData
  };
}

// Hook to get partners that can reach a specific account
export function usePartnersForAccount(accountId: string | null) {
  const { rankings, loading, error } = usePartnerRankings();

  const partnersForAccount = rankings
    .filter(partner =>
      partner.matched_accounts?.some(acc => acc.id === accountId)
    )
    .map(partner => ({
      ...partner,
      // Get the specific match reasons for this account
      matchInfo: partner.matched_accounts?.find(acc => acc.id === accountId)
    }))
    .sort((a, b) => b.partner_score - a.partner_score);

  return {
    partners: partnersForAccount,
    loading,
    error
  };
}
