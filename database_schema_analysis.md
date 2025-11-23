# Database Schema Requirements Analysis

Based on the comprehensive ABM dashboard design, here are the complete field requirements for each Notion database:

## Accounts Database
**Current Status**: ✅ Basic structure exists, needs enhancement

### Required Fields:
- `Name` (title) - ✅ EXISTS - Company name with ICP score
- `Domain` (text) - ❌ MISSING - Company domain (genesiscloud.com)
- `Employee Count` (number) - ❌ MISSING - Number of employees
- `ICP Fit Score` (number, 0-100) - ❌ MISSING - Extracted from name currently
- `Account Research Status` (select: Not Started, In Progress, Complete) - ❌ MISSING
- `Last Updated` (date) - ❌ MISSING
- `Company Type` (select: Cloud Provider, Colocation, Hyperscaler, AI Infrastructure) - ❌ MISSING
- `Primary Business Model` (rich_text) - ❌ MISSING
- `Data Center Locations` (rich_text) - ❌ MISSING
- `Recent Funding Status` (rich_text) - ❌ MISSING
- `Growth Indicators` (multi_select) - ❌ MISSING

### Relations:
- Trigger Events (relation to Trigger Events database)
- Contacts (relation to Contacts database)
- Strategic Partnerships (relation to Partnerships database)

## Contacts Database
**Current Status**: ✅ Good structure, minor enhancements needed

### Required Fields:
- `Name` (title) - ✅ EXISTS
- `Account` (relation to Accounts) - ❌ MISSING - Critical for filtering
- `Title` (rich_text) - ✅ EXISTS
- `LinkedIn URL` (url) - ✅ EXISTS
- `Email` (email) - ❌ MISSING - Only defined in schema, not populated
- `Buying Committee Role` (select: Economic Buyer, Technical Evaluator, Champion, Influencer) - ✅ EXISTS
- `ICP Fit Score` (number, 0-100) - ✅ EXISTS
- `Buying Power Score` (number, 0-100) - ✅ EXISTS
- `Engagement Potential Score` (number, 0-100) - ✅ EXISTS
- `Final Lead Score` (formula) - ✅ EXISTS
- `Research Status` (select: Not Started, Enriched, Analyzed) - ✅ EXISTS
- `Role Tenure` (rich_text) - ❌ MISSING
- `Problems They Likely Own` (multi_select) - ✅ EXISTS
- `Content Themes They Value` (multi_select) - ✅ EXISTS
- `Connection Pathways` (rich_text) - ❌ MISSING
- `Value-add Ideas` (rich_text) - ✅ EXISTS
- `LinkedIn Activity Level` (select: Weekly+, Monthly, Quarterly, Inactive) - ❌ MISSING
- `Network Quality Score` (number, 0-100) - ❌ MISSING
- `Last Contact Attempt` (date) - ❌ MISSING
- `Contact Status` (select: Not Contacted, Outreach Sent, Responded, Meeting Scheduled) - ❌ MISSING

## Trigger Events Database
**Current Status**: ❌ EMPTY - Needs complete population

### Required Fields:
- `Event Description` (title) - Event summary
- `Account` (relation to Accounts) - Link to account
- `Event Type` (select: Expansion, Leadership Change, AI Workload, Energy Pressure, Incident, Sustainability) - Category
- `Confidence` (select: High, Medium, Low) - Source reliability
- `Confidence Score` (number, 0-100) - Numeric confidence
- `Relevance Score` (number, 0-100) - Alignment to Verdigris value props
- `Detected Date` (date) - When event occurred
- `Source URL` (url) - Evidence link
- `Event Details` (rich_text) - Full description
- `Verdigris Relevance Reason` (rich_text) - Why this matters
- `Engagement Timing` (select: Immediate, 30 Days, 90 Days, Monitor) - When to act
- `Internal Notes` (rich_text) - Team comments

## Strategic Partnerships Database
**Current Status**: ❌ EMPTY - Needs complete population

### Required Fields:
- `Partner Name` (title) - Vendor/partner company name
- `Account` (relation to Accounts) - Target account
- `Category` (select: DCIM, EMS, Cooling, DC Equipment, Racks, GPUs, Critical Facilities, Professional Services) - Partner type
- `Relationship Evidence URL` (url) - Source of partnership info
- `Relationship Evidence` (rich_text) - Description of partnership
- `Detected Date` (date) - When partnership was discovered
- `Confidence` (select: High, Medium, Low) - Evidence quality
- `Verdigris Opportunity Angle` (rich_text) - How Verdigris can leverage
- `Partnership Team Action` (select: Investigate, Contact, Monitor, Not Relevant) - Next steps
- `Contact Priority` (select: High, Medium, Low) - Urgency level
- `Integration Potential` (select: Direct API, Co-sell, Referral, Education) - Type of opportunity
- `Internal Notes` (rich_text) - Strategy notes

## Contact Intelligence Database (Optional Enhancement)
**Current Status**: ❌ DOES NOT EXIST - Consider adding

### Purpose:
Detailed research notes and activity tracking for high-priority contacts

### Required Fields:
- `Contact` (relation to Contacts) - Link to contact
- `Recent Activity Summary` (rich_text) - Last 90 days LinkedIn activity
- `Network Analysis` (rich_text) - Connection quality assessment
- `Detailed Engagement Notes` (rich_text) - Research findings
- `Content Engagement History` (rich_text) - What they interact with
- `Buying Signal Strength` (select: Strong, Moderate, Weak, Unknown) - Purchase intent
- `Decision Making Influence` (select: High, Medium, Low) - Role in buying process
- `Personal Interests` (rich_text) - Non-work interests for relationship building
- `Communication Style` (select: Direct, Analytical, Relationship-focused, Technical) - Approach preference
- `Best Contact Method` (select: Email, LinkedIn, Phone, Warm Intro) - Preferred outreach

## Key Issues Found:

### 1. Missing Account Relations
- Contacts database needs Account relation field to filter by company
- Trigger Events database needs Account relation
- Partnerships database needs Account relation

### 2. Missing Core Account Data
- Employee count, domain, company type not stored
- ICP score only extractable from Name field currently

### 3. Empty Supporting Databases
- Trigger Events database is completely empty
- Partnerships database is completely empty
- These provide critical context for timing and warm intro opportunities

### 4. Missing Engagement Tracking
- No contact attempt history
- No outreach status tracking
- No meeting scheduling integration

## Immediate Action Required:

1. **Add Account relations to all databases** - Critical for dashboard filtering
2. **Enhance Account database** with missing firmographic fields
3. **Populate Trigger Events** with Genesis Cloud research
4. **Populate Partnerships** with Genesis Cloud vendor relationships
5. **Add engagement tracking** fields for sales process management