# ABM Research Notion Schema

**Last Updated:** December 2, 2025
**Status:** Production Schema (Post-Cleanup)

This document defines the authoritative schema for the 4 Notion databases used by the ABM Research pipeline. All fields listed are actively written by the pipeline AND consumed by the dashboard.

---

## Schema Philosophy

After the December 2025 schema cleanup, we follow these principles:

1. **No Aspirational Fields** - Every field must be written by the pipeline AND displayed in the dashboard
2. **Notion is Source of Truth** - ICP Fit Score is read from Notion, not recalculated
3. **Graceful Fallbacks** - Read operations handle missing fields; write operations only include production fields
4. **Minimal Payload** - Remove unused fields to reduce API costs and improve performance

---

## Database 1: Accounts

**Purpose:** Target companies for sales outreach

| Field Name | Type | Required | Description | Pipeline Source |
|------------|------|----------|-------------|-----------------|
| `Name` | title | Yes | Company name | User input / enrichment |
| `Domain` | rich_text | Yes | Company website domain | Apollo / user input |
| `Business Model` | select | No | Industry category | LLM classification |
| `Employee Count` | number | No | Company size | Apollo enrichment |
| `ICP Fit Score` | number | Yes | 0-100 ICP alignment score | Pipeline calculation |
| `Account Research Status` | select | No | Research progress | Pipeline status updates |
| `Last Updated` | date | Yes | Last modification timestamp | Auto-updated |
| `Physical Infrastructure` | rich_text | No | GPU/datacenter detection results | Infrastructure detection phase |

### Removed Fields (Dec 2025 Cleanup)
The following fields were removed because they weren't displayed in the dashboard:
- Recent Leadership Changes
- Recent Funding
- Growth Stage
- Recent Announcements
- Hiring Velocity
- Conversation Triggers
- Key Decision Makers
- Competitor Tools

**Roadmap:** Consider adding Competitor Tools back when competitive analysis tab is implemented.

---

## Database 2: Contacts

**Purpose:** Key stakeholders at target accounts

| Field Name | Type | Required | Description | Pipeline Source |
|------------|------|----------|-------------|-----------------|
| `Name` | title | Yes | Contact full name | Apollo enrichment |
| `Email` | email | No | Work email address | Apollo (on-demand reveal) |
| `Title` | rich_text | No | Job title | Apollo enrichment |
| `ICP Fit Score` | number | No | Contact lead score | MEDDIC classification |
| `Account` | relation | Yes | Link to parent account | Account lookup |
| `Name Source` | select | No | Data provenance | Apollo/LinkedIn/manual |
| `Email Source` | select | No | Data provenance | Apollo/LinkedIn/manual |
| `Title Source` | select | No | Data provenance | Apollo/LinkedIn/manual |
| `Data Quality Score` | number | No | 0-100 data confidence | Multi-source validation |
| `Last Enriched` | date | No | Last enrichment timestamp | Auto-updated |
| `Lead Score` | number | No | Priority ranking | Pipeline calculation |
| `Engagement Level` | select | No | Low/Medium/High | LinkedIn activity analysis |
| `Contact Date` | date | No | When contact was discovered | Auto-set |
| `LinkedIn URL` | url | No | LinkedIn profile link | Apollo enrichment |
| `Notes` | rich_text | No | Free-form notes | Manual / pipeline |

### Fallback Field
| `Account Name (Fallback)` | rich_text | No | Used when Account relation cannot be established |

### Dashboard Feature Gaps
The following are written but need dashboard display:
- Name Source / Email Source / Title Source (show data provenance)
- Data Quality Score (confidence indicator)
- Engagement Level (from LinkedIn analysis)

---

## Database 3: Trigger Events

**Purpose:** Buying signals and sales timing intelligence

| Field Name | Type | Required | Description | Pipeline Source |
|------------|------|----------|-------------|-----------------|
| `Name` | title | Yes | Event description | LLM extraction |
| `Event Type` | select | Yes | Category (see below) | LLM classification |
| `Confidence` | select | No | Low/Medium/High | LLM confidence |
| `Source URL` | url | No | Evidence link | Brave Search result |
| `Detected Date` | date | Yes | When event was found | Auto-set |
| `Account` | relation | Yes | Link to parent account | Account lookup |

### Multi-Dimensional Scoring Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `Business Impact Score` | number | 0-100 revenue/strategy impact |
| `Actionability Score` | number | 0-100 how actionable this signal is |
| `Timing Urgency Score` | number | 0-100 time sensitivity |
| `Strategic Fit Score` | number | 0-100 alignment with Verdigris |

### Time Intelligence Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `Action Deadline` | date | When action should be taken by |
| `Peak Relevance Window` | date | Optimal outreach window |
| `Decay Rate` | select | How quickly relevance decreases |

### Event Lifecycle Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `Event Stage` | select | Announced/In Progress/Completed |
| `Follow-up Actions` | rich_text | Recommended next steps |
| `Urgency Level` | select | Critical/High/Medium/Low |

### Event Types
```
expansion      - New facilities, regions, capacity
hiring         - DevOps, SRE, Infrastructure roles
funding        - Series A/B/C, IPO, acquisition
partnership    - New vendor relationships
ai_workload    - GPU, AI/ML announcements
leadership     - CTO, VP Infra changes
incident       - Outages, reliability issues
other          - Uncategorized signals
```

### Fallback Field
| `Account Name (Fallback)` | rich_text | No | Used when Account relation cannot be established |

---

## Database 4: Partnerships

**Purpose:** Vendor relationships for trusted introduction paths

| Field Name | Type | Required | Description | Pipeline Source |
|------------|------|----------|-------------|-----------------|
| `Partner Name` | title | Yes | Vendor/partner company name | LLM extraction |
| `Category` | select | No | Partnership type (see below) | LLM classification |
| `Priority Score` | number | No | 0-100 relevance/confidence | LLM scoring |
| `Relationship Evidence` | rich_text | No | Proof of relationship | Search snippet |
| `Detected Date` | date | Yes | When partnership was discovered | Auto-set |
| `Account` | relation | No* | Link to account using this vendor | Account lookup |

*Note: `Account` relation is optional because Verdigris's own partners don't need an account link.

### Partnership Strategy Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `Relationship Depth` | select | Surface Integration / Deep Partnership / Strategic Alliance |
| `Partnership Maturity` | select | Basic / Established / Strategic |
| `Best Approach` | select | Technical Discussion / Executive Intro / Partner Referral |
| `Is Verdigris Partner` | checkbox | True if Verdigris works with this company |

### Partnership Categories
```
Strategic Partner   - Co-selling or referral opportunity
Direct ICP          - They're a sales target themselves
Referral Partner    - Can introduce us to accounts
Competitive         - Watch for displacement opportunities
Channel Partner     - Distribution/reseller relationship
GPU/AI              - NVIDIA, AMD, Intel partnerships
Power Systems       - Schneider Electric, Eaton, Vertiv
Cooling             - Liquid/immersion cooling vendors
```

### Trusted Paths Feature
When `Is Verdigris Partner` = true AND the same vendor appears in an account's partnerships, we have a "trusted path" - a warm introduction opportunity.

### Removed Fields (Dec 2025 Cleanup)
The following aspirational fields were removed:
- Evidence URL (use Relationship Evidence instead)
- Common Partners
- Competitive Overlap
- Decision Timeline
- Success Metrics
- Recommended Next Steps
- Account Name (Fallback) (removed - require proper relation)

---

## Data Flow

```
External APIs                    Notion Databases                Dashboard
─────────────────────────────────────────────────────────────────────────────

Apollo    ───┐                   ┌─ Accounts ─────────────────┐
             │                   │   └─ ICP Fit Score         │──→ Account List
Brave     ───┼──→ Pipeline ──────┼─ Contacts                  │──→ Contact Cards
             │                   │   └─ Account (relation)    │──→ MEDDIC Roles
OpenAI    ───┘                   ├─ Trigger Events            │──→ Buying Signals
                                 │   └─ Account (relation)    │──→ Event Timeline
                                 └─ Partnerships              │──→ Partner Rankings
                                     └─ Account (relation)    │──→ Trusted Paths
```

---

## API Response Mapping

The Flask API (`server.py`) transforms Notion data for the dashboard:

### Accounts Endpoint
```json
{
  "id": "notion-page-id",
  "name": "Company Name",
  "domain": "company.com",
  "icp_fit_score": 85,
  "account_score": 85,
  "account_priority_level": "Very High",
  "business_model": "AI Infrastructure",
  "employee_count": 500,
  "physical_infrastructure": "NVIDIA H100, Liquid Cooling"
}
```

### Contacts Endpoint
```json
{
  "id": "notion-page-id",
  "name": "John Doe",
  "title": "VP of Infrastructure",
  "email": "john@company.com",
  "account_id": "account-page-id",
  "buying_committee_role": "economic_buyer",
  "lead_score": 85,
  "linkedin_url": "https://linkedin.com/in/johndoe"
}
```

### Trigger Events Endpoint
```json
{
  "id": "notion-page-id",
  "description": "Announced $50M datacenter expansion",
  "event_type": "expansion",
  "confidence": "High",
  "detected_date": "2025-01-15",
  "source_url": "https://news.example.com/article",
  "business_impact_score": 80,
  "actionability_score": 75
}
```

### Partnerships Endpoint
```json
{
  "id": "notion-page-id",
  "partner_name": "NVIDIA",
  "partnership_type": "GPU/AI",
  "relevance_score": 90,
  "relationship_depth": "Deep Partnership",
  "is_verdigris_partner": false,
  "account_id": "account-page-id"
}
```

---

## Implementation Reference

**File:** `src/abm_research/integrations/notion_client.py`

| Operation | Method | Lines |
|-----------|--------|-------|
| Create Account | `_create_account()` | 614-638 |
| Update Account | `_update_account()` | 792-815 |
| Create Contact | `_create_contact()` | 640-683 |
| Create Trigger Event | `_create_trigger_event()` | 685-736 |
| Create Partnership | `_create_partnership()` | 738-786 |

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-02 | Initial schema documentation after cleanup | Claude |
| 2025-12-02 | Removed 8 unused Account fields | Claude |
| 2025-12-02 | Removed 7 unused Partnership fields | Claude |
| 2025-12-02 | Fixed Partnership title field ("Name" → "Partner Name") | Claude |
