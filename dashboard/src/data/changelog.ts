/**
 * Changelog Data - Version History for the ABM Intelligence Dashboard
 *
 * Each entry represents a release with features grouped by category.
 * This data drives the "What's New" modal in the header.
 */

export interface ChangelogEntry {
  version: string;
  date: string;
  title: string;
  highlights: string[];  // Key features (shown prominently)
  features: {
    category: 'core' | 'intelligence' | 'integration' | 'ui' | 'infrastructure';
    items: string[];
  }[];
}

export const CURRENT_VERSION = 'v0.11.0';

export const changelog: ChangelogEntry[] = [
  {
    version: 'v0.11.0',
    date: '2025-12-08',
    title: 'Partnership Discovery & Reliability',
    highlights: [
      'Automatic partnership deduplication (one vendor → multiple accounts)',
      'BD-friendly category-diverse partnership discovery',
      'Robust Notion API error handling with exception hierarchy'
    ],
    features: [
      {
        category: 'intelligence',
        items: [
          'Category-aware partnership filtering ensures BD sees all 8 vendor categories',
          'Lowered confidence threshold (30%) for category diversity exploration',
          'High-confidence partnerships (50%+) still prioritized after diversity pass'
        ]
      },
      {
        category: 'integration',
        items: [
          'Auto-dedupe: existing vendors gain account relations instead of duplicating',
          'Notion exception hierarchy: NotionError, NotionConfigError, NotionAPIError',
          'Database ID properties raise immediately if not configured',
          'Brave API rate limiting: 1.1s delay + jitter + Retry-After header support'
        ]
      },
      {
        category: 'infrastructure',
        items: [
          'Health endpoints: /api/health/pipeline and /api/health/notion-test',
          'Robust JSON response handling with detailed error context',
          'Schema fix: "Partner Name" → "Name" field alignment'
        ]
      }
    ]
  },
  {
    version: 'v0.10.0',
    date: '2025-12-02',
    title: 'Account Enrichment UI & Release Process',
    highlights: [
      'One-click account field enrichment from dashboard',
      'Formalized release process with What\'s New integration',
      'Account ID lookup improvements for Notion sync'
    ],
    features: [
      {
        category: 'ui',
        items: [
          'AccountFieldEnrichmentButton for on-demand Industry, Infrastructure & ICP scoring',
          'Progress indicators and success states for enrichment operations',
          'Force refresh option for re-enriching accounts',
          'Results display with infrastructure summary and ICP reasoning'
        ]
      },
      {
        category: 'infrastructure',
        items: [
          'Release process documentation and workflow',
          'Retrospective templates for continuous improvement',
          'CI/CD integration with automated deployment verification'
        ]
      },
      {
        category: 'integration',
        items: [
          'Account ID lookup now supports both synthetic and Notion UUIDs',
          'Improved error handling in enrichment endpoints',
          'Notion field updates for Industry, Physical Infrastructure, ICP Fit Score'
        ]
      }
    ]
  },
  {
    version: 'v0.9.0',
    date: '2025-11-30',
    title: 'Vendor Discovery & Batch Processing',
    highlights: [
      'AI-powered vendor discovery using GPT-4o-mini',
      'Batch vendor discovery across all accounts',
      'Dashboard vendor discovery button'
    ],
    features: [
      {
        category: 'intelligence',
        items: [
          'Dynamic vendor extraction from news and web searches',
          'Automatic vendor categorization (competitor, complementary, channel)',
          'Confidence scoring for discovered vendors',
          'Evidence snippets with source URLs'
        ]
      },
      {
        category: 'integration',
        items: [
          'Auto-save discovered vendors to Notion Partnerships database',
          'Batch discovery script with rate limiting',
          'Cost tracking for API usage (~$0.17 per account)'
        ]
      },
      {
        category: 'ui',
        items: [
          'VendorDiscoveryButton in account detail panel',
          'Progress indicators during long-running discovery',
          'Results display with category breakdown'
        ]
      }
    ]
  },
  {
    version: 'v0.8.0',
    date: '2025-11-29',
    title: 'Foundation Cleanup & Schema Compliance',
    highlights: [
      'Complete 5-phase schema compliance',
      'Technical debt elimination',
      'Production-ready architecture'
    ],
    features: [
      {
        category: 'infrastructure',
        items: [
          'Removed unused database files and deprecated modules',
          'Consolidated API endpoints',
          'Fixed Notion field mapping across all properties'
        ]
      },
      {
        category: 'core',
        items: [
          'GPU datacenter and physical infrastructure detection',
          'Partnership classification system enhancement',
          'External service integration documentation'
        ]
      }
    ]
  },
  {
    version: 'v0.7.0',
    date: '2025-11-28',
    title: 'ABM Data Stream Optimization',
    highlights: [
      'On-demand email reveal (saves Apollo credits)',
      'LinkedIn via Brave Search (no paid API)',
      'Active trigger event detection'
    ],
    features: [
      {
        category: 'intelligence',
        items: [
          'LinkedIn activity discovery with thought leadership scoring',
          '7 trigger event types: expansion, hiring, funding, partnership, AI workload, leadership, incident',
          'DataConflictResolver for multi-source data handling'
        ]
      },
      {
        category: 'integration',
        items: [
          'Notion-only caching with 30-day TTL',
          'Automated partnership classification pipeline',
          'Apollo email reveal endpoint (POST /api/contacts/{id}/reveal-email)'
        ]
      }
    ]
  },
  {
    version: 'v0.6.0',
    date: '2025-11-27',
    title: 'Complete Notion Integration',
    highlights: [
      'Full data synchronization with Notion',
      'Contacts, events, and partnerships from Notion',
      'Real-time score transparency'
    ],
    features: [
      {
        category: 'integration',
        items: [
          'Query contacts by account relation',
          'Trigger events from Notion database',
          'Partnership records with relationship metadata',
          'ICP Fit Score read directly from Notion'
        ]
      },
      {
        category: 'ui',
        items: [
          'Account detail shows contacts, events, partnerships',
          'Score badges reflect Notion values',
          'Priority levels derived from ICP Fit Score'
        ]
      }
    ]
  },
  {
    version: 'v0.5.0',
    date: '2025-11-26',
    title: 'Trusted Paths & Partner Rankings',
    highlights: [
      'Partner ranking algorithm',
      'Trusted introduction paths',
      'Partnerships tab in dashboard'
    ],
    features: [
      {
        category: 'intelligence',
        items: [
          'Partner scoring: Account Reach (35%) + ICP Alignment (25%) + Entry Point Quality (25%) + Trust Evidence (15%)',
          'Shared vendor analysis for warm introductions',
          'Verdigris partner matching'
        ]
      },
      {
        category: 'ui',
        items: [
          'PartnerRankings component with sortable cards',
          'Tab navigation between Accounts and Partnerships',
          'Matched accounts display per partner'
        ]
      }
    ]
  },
  {
    version: 'v0.4.0',
    date: '2025-11-25',
    title: 'Deep Research Pipeline',
    highlights: [
      '5-phase ABM research pipeline',
      'ResearchButton with live progress',
      'Comprehensive account enrichment'
    ],
    features: [
      {
        category: 'core',
        items: [
          'Phase 1: Company Intelligence',
          'Phase 2: Infrastructure Detection',
          'Phase 3: Buying Signal Analysis',
          'Phase 4: Contact Discovery',
          'Phase 5: Notion Sync'
        ]
      },
      {
        category: 'ui',
        items: [
          'ResearchButton with animated progress bar',
          'Phase-by-phase status updates',
          'Results summary with key findings'
        ]
      }
    ]
  },
  {
    version: 'v0.3.0',
    date: '2025-11-24',
    title: 'Contact Intelligence',
    highlights: [
      'MEDDIC role classification',
      'Contact enrichment button',
      'LinkedIn activity integration'
    ],
    features: [
      {
        category: 'intelligence',
        items: [
          'Entry Point detection (Technical Believers)',
          'Middle Decider identification (Tooling Decisions)',
          'Economic Buyer mapping (Budget Authority)',
          'Seniority scoring based on title analysis'
        ]
      },
      {
        category: 'ui',
        items: [
          'ContactCard with role badges',
          'EnrichmentButton for on-demand contact lookup',
          'Contact list with MEDDIC icons'
        ]
      }
    ]
  },
  {
    version: 'v0.2.0',
    date: '2025-11-23',
    title: 'Infrastructure Scoring',
    highlights: [
      'GPU infrastructure detection',
      'Physical infrastructure breakdown',
      'Visual scoring cards'
    ],
    features: [
      {
        category: 'core',
        items: [
          'GPU vendor detection (NVIDIA, AMD, Intel)',
          'Datacenter infrastructure analysis',
          'Cooling system identification',
          'Physical infrastructure categories'
        ]
      },
      {
        category: 'ui',
        items: [
          'InfrastructureBreakdown component',
          'Color-coded infrastructure badges',
          'TARGET ICP indicator for GPU accounts'
        ]
      }
    ]
  },
  {
    version: 'v0.1.0',
    date: '2025-11-22',
    title: 'Initial Release',
    highlights: [
      'Account scoring system',
      'Notion integration foundation',
      'React dashboard MVP'
    ],
    features: [
      {
        category: 'core',
        items: [
          'Account-first scoring methodology',
          'Infrastructure (35%) + Business Fit (35%) + Buying Signals (30%)',
          'Priority level calculation'
        ]
      },
      {
        category: 'integration',
        items: [
          'Notion API client for accounts database',
          'Flask API server',
          'Environment configuration'
        ]
      },
      {
        category: 'ui',
        items: [
          'AccountList with sorting and filtering',
          'AccountDetail panel',
          'ScoreBadge and ScoreCard components',
          'Dark theme with CSS variables'
        ]
      }
    ]
  }
];

// Helper to get category display name and color
export function getCategoryInfo(category: ChangelogEntry['features'][0]['category']): { name: string; color: string } {
  const info: Record<string, { name: string; color: string }> = {
    core: { name: 'Core', color: 'var(--color-priority-very-high)' },
    intelligence: { name: 'Intelligence', color: 'var(--color-priority-high)' },
    integration: { name: 'Integration', color: 'var(--color-accent-primary)' },
    ui: { name: 'UI/UX', color: 'var(--color-infra-vendor)' },
    infrastructure: { name: 'Infrastructure', color: 'var(--color-priority-medium)' }
  };
  return info[category] || { name: category, color: 'var(--color-text-secondary)' };
}
