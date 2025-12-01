/**
 * ABM Dashboard TypeScript Types
 * Aligned with backend AccountScorer and MEDDICContactScorer
 */

// ============================================================================
// Infrastructure Types
// ============================================================================

export interface InfrastructureCategory {
  detected: string[];
  points: number;
  max_points: number;
  description: string;
}

export interface InfrastructureBreakdown {
  score: number;
  breakdown: {
    gpu_infrastructure: InfrastructureCategory;
    target_vendors: InfrastructureCategory;
    power_systems: InfrastructureCategory;
    cooling_systems: InfrastructureCategory;
    dcim_software: InfrastructureCategory;
  };
  raw_text: string;
}

// ============================================================================
// Account Types
// ============================================================================

export type PriorityLevel = 'Very High' | 'High' | 'Medium' | 'Low';

export interface AccountScoreBreakdown {
  total_score: number;
  infrastructure_fit: {
    score: number;
    weight: string;
    breakdown: InfrastructureBreakdown['breakdown'];
  };
  business_fit: {
    score: number;
    weight: string;
    breakdown: {
      industry_fit: { detected: string; score: number; business_model: string };
      company_size_fit: { employee_count: number; size_category: string; score: number };
      geographic_fit: { us_locations: string[]; priority: string; score: number };
    };
  };
  buying_signals: {
    score: number;
    weight: string;
    breakdown: {
      trigger_events: { high_value_triggers: string[]; total_triggers: number; score: number };
      expansion_signals: { detected: string[]; score: number };
      hiring_signals: { detected: string[]; score: number };
    };
  };
  priority_level: PriorityLevel;
}

export interface Account {
  id: string;
  name: string;
  domain: string;
  employee_count: number;
  industry: string;
  business_model: string;

  // Account-First Scores
  account_score: number;
  infrastructure_score: number;
  business_fit_score: number;
  buying_signals_score: number;
  account_priority_level: PriorityLevel;

  // Breakdowns for dashboard display
  infrastructure_breakdown: InfrastructureBreakdown;
  account_score_breakdown: AccountScoreBreakdown;

  // Partnership classification
  partnership_classification?: string;
  classification_confidence?: number;

  // Legacy fields
  icp_fit_score: number;

  // Metadata
  last_updated: string;
  contacts_count: number;
}

// ============================================================================
// Contact Types (MEDDIC)
// ============================================================================

export type RoleTier = 'entry_point' | 'middle_decider' | 'economic_buyer';
export type ChampionPotentialLevel = 'Very High' | 'High' | 'Medium' | 'Low';

export interface MEDDICScoreBreakdown {
  total_score: number;
  champion_potential: {
    score: number;
    weight: string;
    level: ChampionPotentialLevel;
  };
  role_fit: {
    score: number;
    weight: string;
    tier: RoleTier;
    classification: string;
  };
  engagement_potential: {
    score: number;
    weight: string;
  };
  why_prioritize: string[];
  recommended_approach: string;
}

export interface Contact {
  id: string;
  name: string;
  title: string;
  email: string;
  company: string;
  linkedin_url?: string;

  // MEDDIC Scores
  lead_score: number;
  champion_potential_score: number;
  role_tier: RoleTier;
  role_classification: string;
  champion_potential_level: ChampionPotentialLevel;
  recommended_approach: string;
  why_prioritize: string[];
  meddic_score_breakdown: MEDDICScoreBreakdown;

  // Enrichment data
  enrichment_status: 'enriched' | 'pending' | 'failed' | 'skipped_low_score';
  linkedin_activity_level?: string;
  content_themes?: string[];

  // Metadata
  account_id: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface AccountsResponse {
  accounts: Account[];
  total: number;
  page: number;
  per_page: number;
}

export interface AccountDetailResponse {
  account: Account;
  contacts: Contact[];
  trigger_events: TriggerEvent[];
}

export interface TriggerEvent {
  id: string;
  description: string;
  event_type: string;
  relevance_score: number;
  source_url: string;
  detected_date: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export type SortField = 'account_score' | 'infrastructure_score' | 'name' | 'contacts_count';
export type SortDirection = 'asc' | 'desc';

export interface FilterState {
  priorityLevels: PriorityLevel[];
  minScore: number;
  hasGpuInfrastructure: boolean;
  searchQuery: string;
}

// ============================================================================
// Partner Rankings Types
// ============================================================================

export interface PartnerScoreBreakdown {
  account_reach: {
    score: number;
    weight: string;
    contribution: number;
    matched_count: number;
    icp_account_ratio: number;
  };
  icp_alignment: {
    score: number;
    weight: string;
    contribution: number;
    keyword_matches: string[];
    tech_category: string;
  };
  entry_point_quality: {
    score: number;
    weight: string;
    contribution: number;
    partnership_type: string;
    effectiveness_tier: string;
  };
  trust_evidence: {
    score: number;
    weight: string;
    contribution: number;
    signals_detected: string[];
  };
}

export interface PartnerMatchedAccount {
  id: string;
  name: string;
  account_score: number;
  priority_level: PriorityLevel;
  match_reasons: string[];
}

export interface RankedPartner {
  partner_name: string;
  partner_id: string;
  partnership_type: string;
  partner_score: number;
  account_coverage: number;
  score_breakdown: PartnerScoreBreakdown;
  matched_accounts: PartnerMatchedAccount[];
  partnership_data: {
    relationship_depth?: string;
    partnership_maturity?: string;
    context?: string;
    best_approach?: string;
  };
}

export interface ScoringMethodology {
  account_reach: { weight: string; description: string };
  icp_alignment: { weight: string; description: string };
  entry_point_quality: { weight: string; description: string };
  trust_evidence: { weight: string; description: string };
}

export interface PartnerRankingsResponse {
  partner_rankings: RankedPartner[];
  total: number;
  total_accounts: number;
  scoring_methodology: ScoringMethodology;
}
