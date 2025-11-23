# Verdigris ABM Intelligence System Design Document

## Executive Summary

This document outlines the comprehensive design for implementing the Verdigris ABM Research Skill as a production-grade system that preserves and enhances all critical features identified in the original skill specification. The goal is to ensure ZERO feature regression while building on the existing foundation.

## Critical Features That Must Be Preserved

Based on your feedback and the skill specification, these features are NON-NEGOTIABLE:

### 1. Contact Information (Complete & Detailed)
- **Full contact data**: Name, title, LinkedIn URL, email, phone (when available)
- **Multi-channel contact actions**: Email, LinkedIn, Phone with clickable interfaces
- **Role classification**: Economic Buyer, Technical Evaluator, Champion, Influencer
- **Transparent lead scoring**: Show all three dimensions (ICP Fit, Buying Power, Engagement)
- **Connection pathways**: Mutual connections, warm introduction paths
- **Problems they likely own**: Mapped to ICP pain points based on role
- **Content themes they value**: Derived from LinkedIn activity analysis

### 2. AI-Based Recommendations on Next Steps
- **Personalized outreach strategies**: Email templates, LinkedIn messages, call scripts
- **Timing recommendations**: When to reach out based on trigger events and role
- **Value proposition matching**: Specific Verdigris benefits relevant to each contact
- **Conversation starters**: 3-5 specific questions tailored to their role and challenges
- **Engagement intelligence**: How to approach based on LinkedIn activity patterns

### 3. Buying Signal Events (With Complete Context)
- **Event descriptions**: Detailed, actionable trigger event descriptions
- **Event categorization**: Expansion, Leadership Change, AI Workload, Energy Pressure, etc.
- **Confidence scoring**: High/Medium/Low with numerical scores
- **Relevance scoring**: 0-100 scale for Verdigris opportunity alignment
- **Source URLs**: Deep links to original articles, press releases, job postings
- **Detection timing**: When events were discovered vs. when they occurred
- **Urgency levels**: High/Medium/Low priority for sales action

### 4. Deep Links & Source Citations
- **Clickable source links**: Every trigger event must link to original source
- **LinkedIn profile links**: Direct links to contact profiles
- **Company website links**: Career pages, news sections, about pages
- **Press release links**: Official announcements and industry coverage
- **Social media links**: Relevant posts and discussions

## System Architecture Overview

### Current State Analysis

**What's Working:**
- Dashboard server infrastructure (`interactive_dashboard_server.py`)
- Notion API integration (`dashboard_data_service.py`)
- Lead scoring engine (`lead_scoring_engine.py`)
- Production ABM workflow (`production_abm_system.py`)
- Real-time progress tracking and job management

**What's Missing (Per Skill Spec):**
- Phase-by-phase research progression (5 distinct phases)
- Comprehensive trigger event detection and categorization
- LinkedIn activity analysis and engagement scoring
- Strategic partnership intelligence
- Transparent scoring dimension display
- Connection pathway analysis
- Value-add idea generation

## Detailed Implementation Plan

### Phase 1: Account Intelligence Baseline
**Current Implementation:** Partially complete in `production_abm_system.py`
**Enhancements Needed:**

1. **Trigger Event Detection Engine**
   ```python
   class TriggerEventDetector:
       def detect_events(self, company_domain, lookback_days=90):
           # Search sources: company news, press releases, job postings
           # Categories: expansion, leadership_change, ai_workload, energy_pressure, incident, sustainability
           # Score confidence: High (official), Medium (industry), Low (social)
           # Score relevance: 0-100 based on Verdigris value prop alignment
           return events_with_scores_and_links
   ```

2. **Enhanced ICP Scoring**
   ```python
   def calculate_icp_fit_score(self, company_data, trigger_events):
       base_score = self.get_company_type_score(company_data)  # Cloud/Colo/Hyperscaler
       trigger_bonus = self.calculate_trigger_alignment(trigger_events)
       return min(base_score + trigger_bonus, 100)
   ```

### Phase 2: Contact Discovery & Segmentation
**Current Implementation:** Basic Apollo integration exists
**Enhancements Needed:**

1. **Enhanced Apollo Search**
   - Target title expansion from skill config
   - Multi-source contact verification
   - Role tenure detection and scoring

2. **Buying Committee Segmentation**
   ```python
   def classify_buying_committee_role(self, title, seniority):
       # Economic Buyer: VP+ level (100 points)
       # Technical Evaluator: Director level (70 points)
       # Champion: Manager level (50 points)
       # Influencer: Adjacent roles (30 points)
   ```

### Phase 3: High-Priority Contact Enrichment
**Currently Missing - Critical Implementation**

1. **LinkedIn Profile Deep Analysis**
   ```python
   class LinkedInEnrichment:
       def enrich_high_priority_contacts(self, contacts):
           for contact in contacts:
               if contact.score > 60:
                   profile = self.fetch_linkedin_profile(contact.linkedin_url)
                   contact.responsibility_keywords = self.extract_keywords(profile.bio)
                   contact.activity_analysis = self.analyze_recent_activity(profile, days=90)
                   contact.network_quality = self.assess_network_connections(profile)
                   contact.engagement_score = self.calculate_engagement_potential(contact)
   ```

2. **Responsibility Keyword Matching**
   - Power/energy keywords: +20 points
   - Reliability/uptime keywords: +20 points
   - Capacity planning keywords: +20 points

3. **LinkedIn Activity Analysis**
   - Post frequency scoring (Weekly+ = 50, Monthly = 30, Quarterly = 10)
   - Content theme analysis (power, AI infrastructure, reliability, sustainability)
   - Network quality assessment (connections to DC operators, vendors)

### Phase 4: Engagement Intelligence (AI Recommendations)
**Partially Implemented - Needs Enhancement**

1. **Enhanced AI Recommendation Engine**
   ```python
   class EngagementIntelligence:
       def generate_recommendations(self, contact, trigger_events, account_context):
           return {
               'problems_they_own': self.map_role_to_pain_points(contact.title),
               'content_themes_valued': self.extract_from_linkedin_activity(contact),
               'connection_pathways': self.find_mutual_connections(contact),
               'value_add_ideas': self.generate_value_propositions(contact, trigger_events),
               'personalized_outreach': {
                   'email_template': self.generate_email_template(contact, account_context),
                   'linkedin_message': self.generate_linkedin_message(contact),
                   'call_script': self.generate_call_script(contact, trigger_events)
               },
               'timing_recommendations': self.calculate_optimal_timing(contact, trigger_events)
           }
   ```

2. **Pain Point Mapping**
   - Map titles to specific ICP pain points
   - Generate 2-3 specific value-add ideas per contact
   - Link to Verdigris case studies and content

### Phase 5: Strategic Partnership Intelligence
**Currently Missing - New Implementation Required**

1. **Vendor Relationship Detection**
   ```python
   class PartnershipIntelligence:
       def detect_partnerships(self, company_domain):
           partnerships = []
           categories = ['DCIM', 'EMS', 'Cooling', 'DC Equipment', 'Racks', 'GPUs',
                        'Critical Facilities', 'Professional Services']

           for category in categories:
               detected = self.scan_for_vendor_relationships(company_domain, category)
               for partner in detected:
                   partnerships.append({
                       'partner_name': partner.name,
                       'category': category,
                       'evidence_url': partner.source_url,
                       'confidence': partner.confidence,
                       'verdigris_angle': self.generate_opportunity_angle(category),
                       'action': 'Investigate'  # Investigate/Contact/Monitor/Not Relevant
                   })
           return partnerships
   ```

## Enhanced Dashboard Interface Requirements

### Contact Cards Enhancement
```html
<!-- Each contact must display ALL information -->
<div class="contact-card">
    <div class="contact-basic">
        <h3>{{ contact.name }}</h3>
        <p>{{ contact.title }}</p>
        <div class="contact-channels">
            <a href="mailto:{{ contact.email }}">📧 Email</a>
            <a href="{{ contact.linkedin_url }}" target="_blank">💼 LinkedIn</a>
            <a href="tel:{{ contact.phone }}">📱 Call</a>
        </div>
    </div>

    <div class="scoring-breakdown">
        <div class="score-dimension">ICP Fit: {{ contact.icp_fit_score }}/100</div>
        <div class="score-dimension">Buying Power: {{ contact.buying_power_score }}/100</div>
        <div class="score-dimension">Engagement: {{ contact.engagement_score }}/100</div>
        <div class="final-score">Final Score: {{ contact.final_score }}/100</div>
    </div>

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

### Buying Signals Enhancement
```html
<!-- Each trigger event must be clickable with full context -->
<div class="trigger-event">
    <div class="event-header">
        <h4>{{ event.description }}</h4>
        <span class="event-type {{ event.type }}">{{ event.event_type }}</span>
        <span class="urgency-badge {{ event.urgency }}">{{ event.urgency_level }}</span>
    </div>

    <div class="event-scores">
        <div class="confidence-ring">
            <svg><!-- Circular progress for confidence --></svg>
            <span>{{ event.confidence_score }}% Confidence</span>
        </div>
        <div class="relevance-score">{{ event.relevance_score }}% Relevance</div>
    </div>

    <div class="event-metadata">
        <p>Detected: {{ event.detected_date }}</p>
        <a href="{{ event.source_url }}" target="_blank" class="source-link">
            🔗 View Source
        </a>
    </div>
</div>
```

## Data Preservation Requirements

### Notion Database Schema (MUST MATCH SKILL SPEC)

**Accounts Table:**
- Company name (title), Domain (text), Employee count (number)
- ICP fit score (0-100), Account research status (select)
- Last updated (date)

**Contacts Table:**
- Name (title), Account (relation), Title (text)
- LinkedIn URL (url), Email (email), Phone (text)
- Buying committee role (select), Research status (select)
- **Lead Score Dimensions** (transparent scoring):
  - ICP Fit Score (0-100)
  - Buying Power Score (0-100)
  - Engagement Potential Score (0-100)
  - Final Lead Score (formula)
- Problems they likely own (multi-select)
- Content themes they value (multi-select)
- Connection pathways (text)
- Value-add ideas (text)

**Trigger Events Table:**
- Event description (title), Account (relation)
- Event type (select), Confidence (select), Relevance score (0-100)
- Detected date (date), Source URL (url)

**Strategic Partnerships Table:**
- Partner name (title), Account (relation), Category (select)
- Evidence URL (url), Confidence (select)
- Verdigris opportunity angle (text)
- Partnership team action (select)

## Migration Strategy (No Data Loss)

1. **Audit Current Data**: Export all existing Notion data
2. **Schema Enhancement**: Add missing fields without removing existing ones
3. **Data Enrichment**: Run enhancement pipeline on existing contacts
4. **Feature Addition**: Implement missing phases without breaking existing workflow
5. **Validation**: Ensure all original features still work

## Success Metrics

- **Contact Completeness**: 100% of contacts have all required fields populated
- **AI Recommendations**: Every contact >70 score has personalized recommendations
- **Buying Signals**: Every trigger event has source URL and confidence score
- **Deep Links**: All external references are clickable and verified
- **Scoring Transparency**: All three score dimensions visible in dashboard
- **Zero Regression**: All existing features continue to work

## Next Steps

1. **Immediate**: Create gap analysis between current system and skill spec
2. **Phase 1**: Implement missing trigger event detection with source links
3. **Phase 2**: Add LinkedIn enrichment and activity analysis
4. **Phase 3**: Enhance AI recommendation engine with value-add ideas
5. **Phase 4**: Implement strategic partnership intelligence
6. **Phase 5**: Update dashboard to display all enhanced data

This design ensures we build upon your existing working system while adding ALL the sophisticated features you originally designed, with zero loss of functionality you care about.