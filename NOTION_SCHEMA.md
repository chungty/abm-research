# Notion Database Schema Documentation

This document defines the exact field mappings between the ABM Research System and Notion databases.

## Accounts Database Fields
**Database ID**: `NOTION_ACCOUNTS_DB_ID` from .env

| ABM System Field | Notion Field Name | Type | Description |
|------------------|------------------|------|-------------|
| `name` | "Company Name" | title | Primary company identifier |
| `domain` | "Domain" | rich_text | Company website domain |
| `employee_count` | "Employee Count" | number | Number of employees |
| `icp_fit_score` | "ICP Fit Score" | number | Ideal Customer Profile score |
| `business_model` | "Industry" | select | Company industry category |
| `research_status` | "Research Status" | select | Account research completion status |
| `last_updated` | "Last Updated" | date | Last modification date |
| `notes` | "Notes" | rich_text | Additional research notes |

### Enhanced Intelligence Fields
| ABM System Field | Notion Field Name | Type | Description |
|------------------|------------------|------|-------------|
| `Recent Leadership Changes` | "Recent Leadership Changes" | rich_text | Executive team changes |
| `Recent Funding` | "Recent Funding" | rich_text | Funding rounds and investments |
| `Growth Stage` | "Growth Stage" | select | Company maturity stage |
| `Physical Infrastructure` | "Physical Infrastructure" | rich_text | Hardware, datacenter info |
| `Recent Announcements` | "Recent Announcements" | rich_text | Company news and updates |
| `Hiring Velocity` | "Hiring Velocity" | rich_text | Recruitment activity |
| `Conversation Triggers` | "Conversation Triggers" | rich_text | Sales conversation starters |
| `Key Decision Makers` | "Key Decision Makers" | rich_text | Key contacts identified |
| `Competitor Tools` | "Competitor Tools" | rich_text | Competitive intelligence |

## Partnerships Database Fields
**Database ID**: `NOTION_PARTNERSHIPS_DB_ID` from .env

| ABM System Field | Notion Field Name | Type | Description |
|------------------|------------------|------|-------------|
| `account_name` | "Partner Name" | title | Company being classified |
| `partnership_type` | "Partnership Type" | select | direct_icp, strategic_partner, etc. |
| `confidence_score` | "Relevance Score" | number | Classification confidence 0-100 |
| `reasoning` | "Context" | rich_text | Explanation of classification |
| `classification_date` | "Discovered Date" | date | When classification was made |
| `source_url` | "Source URL" | url | Reference link (if any) |

## Contacts Database Fields
**Database ID**: `NOTION_CONTACTS_DB_ID` from .env

| ABM System Field | Notion Field Name | Type | Description |
|------------------|------------------|------|-------------|
| `name` | "Name" | title | Contact full name |
| `email` | "Email" | email | Primary email address |
| `title` | "Title" | rich_text | Job title/position |
| `company` | "Company" | rich_text | Company name |
| `priority_score` | "Priority Score" | number | Contact prioritization score |

## Trigger Events Database Fields
**Database ID**: `NOTION_TRIGGER_EVENTS_DB_ID` from .env

| ABM System Field | Notion Field Name | Type | Description |
|------------------|------------------|------|-------------|
| `description` | "Description" | title | Event description |
| `event_type` | "Event Type" | select | Type of trigger event |
| `confidence` | "Confidence" | select | High/Medium/Low confidence |
| `source_url` | "Source URL" | url | Link to original source |
| `discovered_date` | "Discovered Date" | date | When event was found |

## Field Mapping Rules

1. **Title Fields**: Always use the exact Notion field name in quotes
2. **Rich Text Fields**: Can store any text content
3. **Select Fields**: Must use predefined options in Notion
4. **Number Fields**: Integer or float values
5. **Date Fields**: ISO format dates
6. **URL Fields**: Valid HTTP/HTTPS URLs

## Usage in Code

```python
# ❌ WRONG - Using ABM system field names directly
{
    'Name': company_name,  # This will fail
    'Business Model': business_model  # This will fail
}

# ✅ CORRECT - Using actual Notion field names
{
    'Company Name': company_name,
    'Industry': business_model
}
```

## Common Mapping Errors to Avoid

- `name` → Use `"Company Name"` not `"Name"`
- `business_model` → Use `"Industry"` not `"Business Model"`
- `account_research_status` → Use `"Research Status"` not `"Account Research Status"`
- `partner_name` → Use `"Partner Name"` not `"Account Name"`
- `relevance_score` → Use `"Relevance Score"` not `"Confidence Score"` in Partnerships

## External Service Integrations

This section documents how external data sources map to Notion fields through the ABM Research System.

### Apollo API Integration
Apollo provides contact and company enrichment data that flows into multiple Notion databases:

**Account Data Flow**: `Apollo Organizations API → Company Enrichment Service → Notion Accounts DB`
| Apollo Field | ABM System Field | Notion Field | Description |
|--------------|------------------|--------------|-------------|
| `name` | `name` | "Company Name" | Company name from Apollo |
| `domain` | `domain` | "Domain" | Website domain |
| `employees` | `employee_count` | "Employee Count" | Number of employees |
| `industry` | `business_model` | "Industry" | Company industry |
| `id` | `apollo_account_id` | Internal tracking | Apollo account ID |

**Contact Data Flow**: `Apollo People API → Contact Discovery → Notion Contacts DB`
| Apollo Field | ABM System Field | Notion Field | Description |
|--------------|------------------|--------------|-------------|
| `first_name + last_name` | `name` | "Name" | Contact full name |
| `email` | `email` | "Email" | Primary email |
| `title` | `title` | "Title" | Job title |
| `organization.name` | `company` | "Company" | Company name |

### LinkedIn Enrichment Integration
LinkedIn data enhances contact profiles through our enrichment pipeline:

**Data Flow**: `LinkedIn Scraping → Contact Enrichment → Conflict Resolution → Notion Contacts DB`
| LinkedIn Source | ABM System Field | Notion Field | Resolution Strategy |
|-----------------|------------------|--------------|-------------------|
| Profile name | `name` | "Name" | Apollo vs LinkedIn conflict resolution |
| Job title | `title` | "Title" | Most recent/detailed title wins |
| Company | `company` | "Company" | Cross-reference with Apollo data |
| Profile URL | `linkedin_url` | Internal tracking | Source attribution |

### Web Intelligence (Brave Search) Integration
Brave Search provides real-time company intelligence:

**Data Flow**: `Brave Search API → Account Intelligence Engine → Notion Accounts DB`
| Intelligence Type | Search Query | Notion Field | Processing |
|-------------------|--------------|--------------|-----------|
| Leadership changes | "company leadership changes news" | "Recent Leadership Changes" | AI summarization |
| Funding rounds | "company funding investment news" | "Recent Funding" | AI extraction |
| Growth indicators | "company expansion hiring news" | "Growth Stage" | Classification engine |
| Infrastructure | "company datacenter GPU infrastructure" | "Physical Infrastructure" | Hardware detection |
| Announcements | "company press releases news" | "Recent Announcements" | Recent news filtering |
| Hiring trends | "company job openings hiring" | "Hiring Velocity" | Velocity analysis |

### Partnership Classification Integration
Partnership data flows from intelligence analysis to strategic classification:

**Data Flow**: `Multiple Sources → Partnership Classifier → Notion Partnerships DB`
| Analysis Source | Classification Input | Notion Field | Logic |
|-----------------|---------------------|--------------|-------|
| Company intelligence | `business_model` + `physical_infrastructure` | "Partnership Type" | Direct ICP vs Strategic Partner |
| Web research | `tech_stack` + `announcements` | "Relevance Score" | Confidence scoring 0-100 |
| Industry analysis | Combined text analysis | "Context" | Reasoning explanation |
| Real-time classification | `datetime.now()` | "Discovered Date" | Classification timestamp |

### Trigger Events Integration
Real-time events detected from multiple sources:

**Data Flow**: `News APIs + Web Search → Event Detection → Notion Trigger Events DB`
| Event Source | Detection Method | Notion Field | Processing |
|--------------|------------------|--------------|-----------|
| News APIs | Keyword monitoring | "Description" | Event summarization |
| Web scraping | Change detection | "Event Type" | Classification (funding, leadership, etc.) |
| Company monitoring | Periodic checks | "Confidence" | High/Medium/Low scoring |
| Source tracking | URL preservation | "Source URL" | Attribution link |

### Data Quality & Conflict Resolution
Multi-source data requires intelligent conflict resolution:

**Resolution Strategy**: `Apollo Data + LinkedIn Data + Web Intelligence → Conflict Resolver → Enhanced Contacts`
| Conflict Type | Resolution Rule | Tracking Field | Quality Metric |
|---------------|----------------|----------------|----------------|
| Name differences | Most complete/recent wins | "Name Source" | Source attribution |
| Email conflicts | Apollo email preferred | "Email Source" | Primary vs secondary |
| Title mismatches | Most detailed/recent | "Title Source" | Recency + detail score |
| Company variations | Canonical name from Apollo | "Company Source" | Standardization |
| Quality scoring | Multi-factor analysis | "Data Quality Score" | 0-100 composite score |

## Integration Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Apollo API    │───▶│  ABM Research    │───▶│   Notion API    │
│  - Contacts     │    │    System        │    │ - Accounts DB   │
│  - Companies    │    │                  │    │ - Contacts DB   │
└─────────────────┘    │  ┌─────────────┐ │    │ - Partnerships  │
                       │  │ Intelligence│ │    │ - Trigger Events│
┌─────────────────┐    │  │   Engine    │ │    └─────────────────┘
│ LinkedIn Scraper│───▶│  └─────────────┘ │           ▲
└─────────────────┘    │                  │           │
                       │  ┌─────────────┐ │           │
┌─────────────────┐    │  │  Conflict   │ │           │
│  Brave Search   │───▶│  │  Resolver   │ │───────────┘
│   Web Intel     │    │  └─────────────┘ │
└─────────────────┘    │                  │
                       │  ┌─────────────┐ │
┌─────────────────┐    │  │Partnership  │ │
│  News/Events    │───▶│  │ Classifier  │ │
│   Monitoring    │    │  └─────────────┘ │
└─────────────────┘    └──────────────────┘
```

## Service-Specific Field Mappings

### Apollo API Response → ABM System
```python
# Apollo Organization Response
apollo_org = {
    "name": "Groq Inc",
    "domain": "groq.com",
    "employees": 150,
    "industry": "AI Infrastructure"
}

# Maps to ABM System fields:
abm_account = {
    "name": apollo_org["name"],           # → "Company Name"
    "domain": apollo_org["domain"],       # → "Domain"
    "employee_count": apollo_org["employees"], # → "Employee Count"
    "business_model": apollo_org["industry"]   # → "Industry"
}
```

### Web Intelligence → Enhanced Fields
```python
# Brave Search Intelligence Response
intelligence = {
    "recent_funding": "Series B $50M led by Accel",
    "growth_stage": "Scale-up",
    "physical_infrastructure": "NVIDIA H100 GPU clusters",
    "hiring_velocity": "30% growth in engineering roles"
}

# Maps directly to Notion enhanced intelligence fields:
# → "Recent Funding", "Growth Stage", "Physical Infrastructure", "Hiring Velocity"
```

### Partnership Classification → Strategic Data
```python
# Partnership Classifier Output
classification = {
    "partnership_type": "strategic_partner",
    "confidence_score": 85,
    "reasoning": "AI infrastructure provider serving companies needing power monitoring"
}

# Maps to Partnerships database:
# → "Partnership Type", "Relevance Score", "Context"
```

---
**Last Updated**: 2024-11-24
**Maintained by**: ABM Research System
**External Services**: Apollo API, LinkedIn, Brave Search, News Monitoring
