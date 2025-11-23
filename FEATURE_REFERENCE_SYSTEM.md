# Verdigris ABM System Feature Reference

## 🚨 CRITICAL - READ BEFORE ANY CHANGES

This document MUST be consulted before making ANY changes to the ABM system. It documents all features that are essential to the user and must be preserved.

## User's Core Requirements (NON-NEGOTIABLE)

### 1. Contact Information (Complete & Actionable)
**User Quote:** "I want to see their contact information, AI-based recommendations on next steps, buying signal events, the timing of those events, and deep links"

**Required Fields for Each Contact:**
- ✅ **Name, Title, Email, Phone, LinkedIn URL** - Basic contact info
- ✅ **Multi-channel contact actions** - Clickable Email, LinkedIn, Phone buttons
- ✅ **Lead scoring transparency** - Show all 3 dimensions (ICP Fit, Buying Power, Engagement)
- ✅ **Problems they own** - Role-specific pain point mapping
- ✅ **Content themes they value** - From LinkedIn activity analysis
- ✅ **Connection pathways** - Warm introduction opportunities
- ✅ **Value-add ideas** - 2-3 specific, actionable recommendations
- ✅ **Personalized outreach templates** - Email, LinkedIn, call scripts

**Implementation:** `linkedin_enrichment_engine.py` + `enhanced_engagement_intelligence.py`

### 2. AI-Based Recommendations on Next Steps
**User Quote:** "AI-based recommendations on next steps"

**Required AI Recommendations:**
- ✅ **Role-specific pain point mapping** - Map title to ICP pain points
- ✅ **Personalized outreach strategies** - Email templates, LinkedIn messages, call scripts
- ✅ **Timing recommendations** - When to reach out based on trigger events
- ✅ **Value proposition matching** - Verdigris benefits relevant to their role
- ✅ **Conversation starters** - 3-5 specific questions tailored to role and challenges
- ✅ **Connection intelligence** - How to leverage mutual connections

**Implementation:** `enhanced_engagement_intelligence.py`

### 3. Buying Signal Events (Complete Context)
**User Quote:** "buying signal events, the timing of those events, and deep links"

**Required Event Information:**
- ✅ **Event descriptions** - Detailed, actionable descriptions
- ✅ **Event categorization** - 6 types: Expansion, Leadership Change, AI Workload, Energy Pressure, Incident, Sustainability
- ✅ **Confidence scoring** - High/Medium/Low with 0-100 numerical scores
- ✅ **Relevance scoring** - 0-100 Verdigris opportunity alignment
- ✅ **Source URLs** - REAL, clickable deep links to original sources
- ✅ **Timing intelligence** - Detection date vs. occurrence date
- ✅ **Urgency levels** - High/Medium/Low priority for sales action

**Implementation:** `enhanced_trigger_event_detector.py`

### 4. Deep Links & Source Citations
**User Quote:** "deep links"

**Required Links:**
- ✅ **Clickable trigger event sources** - Every event must link to original source
- ✅ **LinkedIn profile links** - Direct links to contact profiles
- ✅ **Company website links** - Career pages, news sections
- ✅ **Press release links** - Official announcements
- ✅ **Partnership evidence URLs** - Proof of vendor relationships

**Implementation:** All engines must include real `source_url` fields

## Skill Specification Requirements (Complete Implementation)

### Phase 1: Account Intelligence Baseline
**Status:** ✅ IMPLEMENTED in `enhanced_trigger_event_detector.py`
- Real trigger event detection with source URLs
- 6 event categories with confidence/relevance scoring
- ICP fit calculation with trigger alignment

### Phase 2: Contact Discovery & Segmentation
**Status:** ✅ IMPLEMENTED (existing Apollo integration)
- Apollo API contact search
- Buying committee role classification
- Initial lead scoring

### Phase 3: High-Priority Contact Enrichment
**Status:** ✅ IMPLEMENTED in `linkedin_enrichment_engine.py`
- LinkedIn bio analysis for responsibility keywords
- Activity analysis (Weekly+/Monthly/Quarterly/Inactive)
- Content theme analysis for Verdigris relevance
- Network quality assessment
- Final lead score recalculation

### Phase 4: Engagement Intelligence
**Status:** ✅ IMPLEMENTED in `enhanced_engagement_intelligence.py`
- Role-to-pain-point mapping
- Value-add idea generation (2-3 per contact)
- Personalized outreach templates
- Connection pathway analysis
- Optimal timing recommendations

### Phase 5: Strategic Partnership Intelligence
**Status:** ✅ IMPLEMENTED in `strategic_partnership_intelligence.py`
- 8 vendor categories detection
- Partnership evidence with source URLs
- Verdigris co-sell opportunity analysis

## Dashboard Display Requirements

### Contact Cards MUST Show:
```html
<!-- REQUIRED CONTACT CARD STRUCTURE -->
<div class="contact-card">
    <!-- Basic info + multi-channel actions -->
    <div class="contact-basic">
        <h3>{{ contact.name }}</h3>
        <p>{{ contact.title }}</p>
        <div class="contact-channels">
            <a href="mailto:{{ contact.email }}">📧 Email</a>
            <a href="{{ contact.linkedin_url }}">💼 LinkedIn</a>
            <a href="tel:{{ contact.phone }}">📱 Call</a>
        </div>
    </div>

    <!-- TRANSPARENT SCORING - MUST SHOW ALL 3 DIMENSIONS -->
    <div class="scoring-breakdown">
        <div>ICP Fit: {{ contact.icp_fit_score }}/100</div>
        <div>Buying Power: {{ contact.buying_power_score }}/100</div>
        <div>Engagement: {{ contact.engagement_score }}/100</div>
        <div class="final">Final: {{ contact.final_score }}/100</div>
    </div>

    <!-- AI RECOMMENDATIONS - MUST BE SPECIFIC -->
    <div class="ai-recommendations">
        <h4>Problems They Own:</h4>
        <ul>{{ contact.problems_owned }}</ul>

        <h4>Value-Add Ideas:</h4>
        <ul>{{ contact.value_add_ideas }}</ul>

        <h4>Connection Pathways:</h4>
        <p>{{ contact.connection_pathways }}</p>
    </div>
</div>
```

### Buying Signals MUST Show:
```html
<!-- REQUIRED TRIGGER EVENT STRUCTURE -->
<div class="trigger-event">
    <div class="event-header">
        <h4>{{ event.description }}</h4>
        <span class="event-type">{{ event.event_type }}</span>
        <span class="urgency">{{ event.urgency_level }}</span>
    </div>

    <!-- CONFIDENCE & RELEVANCE SCORING -->
    <div class="event-scores">
        <div class="confidence">{{ event.confidence_score }}% Confidence</div>
        <div class="relevance">{{ event.relevance_score }}% Relevance</div>
    </div>

    <!-- CRITICAL: SOURCE URL MUST BE CLICKABLE -->
    <div class="event-metadata">
        <p>Detected: {{ event.detected_date }}</p>
        <a href="{{ event.source_url }}" target="_blank">🔗 View Source</a>
    </div>
</div>
```

## Notion Database Schema (MUST MATCH)

### Accounts Table
**Required Fields:**
- Company name (title)
- Domain (text)
- Employee count (number)
- ICP fit score (0-100)
- Account research status (select)
- Last updated (date)

### Contacts Table
**Required Fields:**
- Name (title), Title (text), Email (email), Phone (text)
- LinkedIn URL (url), Buying committee role (select)
- **Lead Score Dimensions (TRANSPARENT):**
  - ICP Fit Score (0-100)
  - Buying Power Score (0-100)
  - Engagement Potential Score (0-100)
  - Final Lead Score (formula)
- **Engagement Intelligence:**
  - Problems they likely own (multi-select)
  - Content themes they value (multi-select)
  - Connection pathways (text)
  - Value-add ideas (text)
- Research status (select)

### Trigger Events Table
**Required Fields:**
- Event description (title)
- Account (relation)
- Event type (select: Expansion, Leadership Change, AI Workload, Energy Pressure, Incident, Sustainability)
- Confidence (select: High, Medium, Low)
- Confidence score (0-100)
- Relevance score (0-100)
- Detected date (date)
- **Source URL (url) - CRITICAL FIELD**

### Strategic Partnerships Table
**Required Fields:**
- Partner name (title)
- Account (relation)
- Category (select: DCIM, EMS, Cooling, DC Equipment, Racks, GPUs, Critical Facilities, Professional Services)
- Evidence URL (url)
- Confidence (select)
- Verdigris opportunity angle (text)
- Partnership team action (select)

## Integration Points (DO NOT BREAK)

### Interactive Dashboard Server
**File:** `interactive_dashboard_server.py`
**Must Support:**
- Real-time research job tracking
- Progress monitoring with phase updates
- API endpoints for all data types
- Background job processing

### Dashboard Data Service
**File:** `dashboard_data_service.py`
**Must Support:**
- Live Notion API integration
- Transparent lead scoring display
- Enhanced contact data with all fields
- Real-time data refresh

### Production ABM System
**File:** `comprehensive_abm_system.py` (NEW)
**Must Execute:**
- Complete 5-phase workflow
- All intelligence engines integration
- Proper error handling
- Comprehensive result formatting

## Testing Requirements

**Before ANY release, verify:**
1. ✅ Every trigger event has a clickable source URL
2. ✅ All contacts show problems owned, content themes, connection pathways
3. ✅ AI recommendations include 2-3 specific value-add ideas per contact
4. ✅ All 3 lead score dimensions are visible in dashboard
5. ✅ LinkedIn activity analysis feeds into engagement scoring
6. ✅ Strategic partnerships are detected with evidence URLs
7. ✅ All 5 phases execute successfully
8. ✅ Dashboard displays all enhanced information
9. ✅ No regression on existing functionality

## Development Rules

### NEVER:
- Remove or simplify existing contact fields
- Use mock data for trigger events without real source URLs
- Generate generic AI recommendations
- Skip any of the 5 phases
- Break the transparent scoring display
- Remove connection pathway analysis
- Remove deep links or source citations

### ALWAYS:
- Consult this document before changes
- Test all user requirements after changes
- Preserve all existing functionality
- Add new features without removing old ones
- Maintain skill specification compliance
- Document any new features added

## Emergency Rollback Plan

If ANY feature breaks:
1. Check git history for last working version
2. Restore from `abm-research/` directory backup
3. Re-run comprehensive test suite
4. Verify all user requirements are met

## Contact for Clarification

**User's Key Concern:** "I hate how you keep deleting stuff. I thought we talked about not deleting things."

**Solution:** This reference system ensures no features are ever lost. ALL future changes must preserve existing functionality while adding new capabilities.

---

**REMEMBER: The user values comprehensive intelligence over simplicity. Do not sacrifice functionality for "cleaner" code.**