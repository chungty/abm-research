# Trigger Event Detection

## Overview

Trigger events signal timing opportunities for engagement. Events are scored by confidence level based on source credibility and recency.

## Confidence Scoring

### High Confidence (Score: 90-100)
- **Company press releases** (official company blog, newsroom)
- **SEC filings** (8-K, 10-K, 10-Q)
- **Official LinkedIn company page announcements**
- **Direct job postings on company career site**

### Medium Confidence (Score: 60-80)
- **Industry news outlets**: Data Center Dynamics, Data Center Frontier, Data Center Knowledge
- **Business news**: Bloomberg, Reuters, WSJ
- **Trade publications**: Mission Critical, Datacenter Forum
- **LinkedIn employee posts** about company news

### Low Confidence (Score: 30-50)
- **General news aggregators**
- **Social media signals** (Twitter/X, unverified sources)
- **Third-party job boards** (may be stale postings)
- **Rumors or unverified reports**

## Recency Filters

- **Default lookback**: 90 days
- **Decay factor**: Events older than 60 days receive -10 confidence points
- **Stale threshold**: Events older than 180 days are flagged as potentially outdated

## Event Categories

### 1. Expansion/Consolidation
**Indicators:**
- New data center construction announcements
- Facility acquisitions
- Colocation capacity expansions
- Geographic expansion into new markets

**Why it matters:** Signals need for new monitoring infrastructure, capacity planning challenges, integration complexity

### 2. Inherited Infrastructure
**Indicators:**
- Merger or acquisition announcements
- Post-merger integration updates
- "Inherited" or "legacy" system references in job postings

**Why it matters:** Creates operational complexity, unknown electrical risks, need for visibility across disparate systems

### 3. Leadership Changes
**Indicators:**
- New VP/Director of Data Center Operations hired
- LinkedIn job change announcements (VP+ level)
- Press releases about executive appointments

**Why it matters:** New leaders often review vendors, seek quick wins, have 90-day mandates for improvements

### 4. AI Workload Expansion
**Indicators:**
- GPU infrastructure buildouts
- HPC cluster expansions
- AI/ML initiative announcements
- Partnership with AI companies (e.g., OpenAI, Anthropic, Cohere)

**Why it matters:** High-density loads create power/cooling challenges, capacity planning urgency, cost pressure

### 5. Energy/Cost Pressure
**Indicators:**
- Mentions of "rising energy costs" in earnings calls
- Sustainability/ESG reporting requirements announced
- PUE targets set or updated
- Cost reduction initiatives

**Why it matters:** Direct alignment with Verdigris value props (energy visibility, cost optimization)

### 6. Downtime/Incidents
**Indicators:**
- Public outage reports (Downdetector, status pages)
- Post-mortem blog posts
- Customer complaints on social media
- Near-miss incident references

**Why it matters:** Pain is acute, urgency for preventive solutions, receptive to risk detection tools

### 7. Sustainability Mandates
**Indicators:**
- ESG reporting commitments
- Carbon neutrality targets announced
- SEC climate disclosure compliance prep
- Renewable energy procurement goals

**Why it matters:** Need accurate power metering for Scope 2/3 reporting, regulatory pressure

## Detection Workflow

1. **Web search** for account name + event keywords (past 90 days)
2. **Scan company website** newsroom/blog for announcements
3. **Check LinkedIn** company page for posts
4. **Search job postings** for operations roles (signals growth/turnover)
5. **Review LinkedIn** employee posts mentioning company developments

## Output Format

For each detected event:
- **Event type** (from 7 categories above)
- **Confidence level** (High/Medium/Low with numeric score)
- **Detected date** (when event occurred, not when discovered)
- **Source URL** (for verification)
- **Relevance score** (0-100, how aligned to Verdigris triggers)
- **Description** (2-3 sentences summarizing the event and implications)

## Relevance Scoring

**High relevance (80-100):**
- Directly mentions power, energy, capacity, uptime, or AI infrastructure
- Leadership change in target role (Data Center Operations)
- Facility expansion with explicit power/cooling challenges

**Medium relevance (50-79):**
- Indirect indicators (M&A, general growth, cost reduction)
- Leadership changes in adjacent roles (CTO, VP Infrastructure)
- Sustainability initiatives without explicit energy focus

**Low relevance (0-49):**
- Generic company news
- Events outside operations domain
- Tangentially related announcements
