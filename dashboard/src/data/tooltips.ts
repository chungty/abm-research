/**
 * Tooltip Content - Educational text for sales onboarding
 *
 * These tooltips help sales employees understand key concepts
 * without leaving the dashboard.
 */

export const tooltips = {
  // Score-related tooltips
  accountScore: `Account Score (0-100) measures how well this company fits our ICP.

Scoring formula:
• Infrastructure: 35% weight
• Business Fit: 35% weight
• Buying Signals: 30% weight

Priority levels:
• 80-100: Very High (green)
• 60-79: High (blue)
• 40-59: Medium (yellow)
• 0-39: Low (gray)`,

  infrastructureScore: `Infrastructure Score measures physical infrastructure alignment.

High scores indicate:
• GPU/AI compute presence (NVIDIA, AMD)
• Datacenter ownership or colocation
• Cooling infrastructure
• Power management needs

This is our #1 ICP indicator - companies with datacenters have power management needs.`,

  businessFitScore: `Business Fit Score evaluates company characteristics.

Factors considered:
• Industry alignment (AI, Cloud, Tech)
• Company size (employee count)
• Geographic presence (US priority)
• Business model fit

Higher scores = better alignment with Verdigris's target market.`,

  buyingSignalsScore: `Buying Signals Score detects active purchase intent.

High-value signals:
• Datacenter expansion announcements
• Infrastructure hiring (DevOps, SRE)
• Recent funding rounds
• AI workload increases
• Leadership changes in IT/Infra

Recent signals indicate timely sales opportunities.`,

  // Infrastructure type tooltips
  gpuInfrastructure: `GPU Infrastructure = AI/ML Compute Capability

Why we care:
Companies running GPU clusters (NVIDIA H100/A100, AMD MI300X) are running AI workloads that require significant power and cooling.

This is our strongest ICP indicator.`,

  datacenterPresence: `Datacenter Presence indicates scale.

Types we track:
• Owned facilities (strongest signal)
• Colocation (co-lo) arrangements
• Hyperscaler usage (AWS, GCP, Azure)

Owned or co-lo = direct power management opportunity.`,

  coolingInfrastructure: `Cooling Systems indicate infrastructure density.

Advanced cooling signals:
• Liquid cooling = high-density compute
• Immersion cooling = cutting-edge AI
• Direct-to-chip cooling = NVIDIA DGX/HGX

These companies have significant power/cooling optimization needs.`,

  physicalInfrastructure: `Physical Infrastructure covers datacenter equipment.

Categories tracked:
• PDUs (Power Distribution Units)
• UPS (Uninterruptible Power Supply)
• CRAC/CRAH cooling units
• Building Management Systems

More infrastructure = more Verdigris opportunity.`,

  dcRectifierSystems: `DC Rectifier Signals indicate power infrastructure interest.

Why we care:
Companies transitioning to DC power (48VDC/380VDC) are upgrading infrastructure and need visibility into per-rack efficiency.

High-value signals:
• Active RFP/procurement = IMMEDIATE outreach
• 48VDC/380VDC mentions = architecture transition
• Delta/ABB/Vertiv relationships = vendor engagement

Target Contacts:
• Critical Facilities Manager (Entry Point)
• Power Engineers (Technical Champion)
• VP of Data Center Operations (Economic Buyer)

Talk Track: "As you transition to DC power, visibility into per-rack efficiency becomes critical for optimizing your investment..."`,

  // MEDDIC role tooltips
  entryPoint: `Entry Points are Technical Believers.

Job titles:
• DevOps Engineer
• Site Reliability Engineer
• Infrastructure Engineer
• Cloud Architect

Sales approach:
Start here to build internal champions. They understand the technical value and can advocate upward.`,

  middleDecider: `Middle Deciders control tooling choices.

Job titles:
• IT Director
• Infrastructure Manager
• Cloud Operations Lead
• Engineering Manager

Sales approach:
These people decide what tools get evaluated. Build technical credibility and ROI case.`,

  economicBuyer: `Economic Buyers have budget authority.

Job titles:
• VP of Infrastructure
• VP of Engineering
• CFO/Finance Director
• CTO

Sales approach:
Final sign-off. Focus on business outcomes, cost savings, and strategic value.`,

  // Button action tooltips
  deepResearch: `Deep Research runs our 5-phase AI pipeline:

Phase 1: Company Intelligence
• Firmographics, business model, news

Phase 2: Infrastructure Detection
• GPU, datacenter, cooling analysis

Phase 3: Buying Signals
• Expansion, hiring, funding signals

Phase 4: Contact Discovery
• Find key stakeholders via Apollo

Phase 5: Notion Sync
• Save all findings to Notion

Time: 2-5 minutes | Cost: ~$0.30`,

  enrichContacts: `Contact Enrichment discovers stakeholders.

What happens:
• Searches Apollo for contacts at this company
• Classifies by MEDDIC role (Entry/Middle/Economic)
• Calculates seniority and engagement scores
• Saves to Notion Contacts database

Use this to find who to reach out to.`,

  vendorDiscovery: `Vendor Discovery finds partnership opportunities.

What happens:
• Searches news for vendor relationships
• Uses AI to extract company names
• Categorizes as competitor/partner/channel
• Saves to Notion Partnerships database

Discovers intro paths through shared vendors.`,

  triggerEvents: `Trigger Events are buying signals.

Event types we detect:
• Expansion (new facilities, regions)
• Hiring (DevOps, SRE, Infra roles)
• Funding (Series A/B/C, IPO)
• Partnerships (new vendor relationships)
• AI Workload (GPU announcements)
• Leadership (CTO, VP Infra changes)
• Incidents (outages, reliability issues)

Recent events = timely outreach opportunity.`,

  // Partnership tooltips
  partnershipType: `Partnership Types indicate relationship value.

Categories:
• Direct ICP: They're a sales target
• Strategic Partner: Co-selling opportunity
• Referral Partner: Can introduce us to others
• Competitive: Watch for displacement

Use partnerships to find warm introduction paths.`,

  partnerScore: `Partner Score ranks introduction potential.

Factors:
• Account Reach (35%): How many accounts they connect to
• ICP Alignment (25%): Quality of connected accounts
• Entry Point Quality (25%): Access to decision makers
• Trust Evidence (15%): Strength of relationships

Higher score = better partner to engage.`,
};

// Quick reference card content for empty states
export const quickStartGuide = {
  title: 'Getting Started',
  steps: [
    {
      number: 1,
      title: 'Select an Account',
      description: 'Click any account in the list to view details and scores',
    },
    {
      number: 2,
      title: 'Review ICP Score',
      description: 'Check Infrastructure, Business Fit, and Buying Signals scores',
    },
    {
      number: 3,
      title: 'Run Deep Research',
      description: 'Click "Deep Research" for comprehensive AI-powered analysis',
    },
    {
      number: 4,
      title: 'Find Contacts',
      description: 'Use "Enrich Contacts" to discover stakeholders',
    },
    {
      number: 5,
      title: 'Plan Outreach',
      description: 'Use MEDDIC roles to plan your sales approach',
    },
  ],
};

// Infrastructure glossary for reference
export const infrastructureGlossary = [
  {
    term: 'GPU Cluster',
    definition: 'A group of graphics processing units used for AI/ML training and inference',
    example: 'NVIDIA DGX H100 cluster for training large language models',
  },
  {
    term: 'Colocation (Co-lo)',
    definition: 'Renting space in a third-party datacenter for your own servers',
    example: 'Equinix, Digital Realty, CoreSite facilities',
  },
  {
    term: 'PDU',
    definition: 'Power Distribution Unit - distributes power to server racks',
    example: 'Intelligent PDUs with per-outlet monitoring',
  },
  {
    term: 'UPS',
    definition: 'Uninterruptible Power Supply - battery backup for critical systems',
    example: 'Eaton, APC, Vertiv UPS systems',
  },
  {
    term: 'CRAC/CRAH',
    definition: 'Computer Room Air Conditioning/Handler - datacenter cooling',
    example: 'Precision cooling units for server rooms',
  },
  {
    term: 'Liquid Cooling',
    definition: 'Using liquid instead of air to cool high-density compute',
    example: 'Direct-to-chip cooling for NVIDIA H100 GPUs',
  },
  {
    term: 'PUE',
    definition: 'Power Usage Effectiveness - datacenter efficiency metric',
    example: 'PUE of 1.2 means 20% overhead for cooling/lighting',
  },
];
