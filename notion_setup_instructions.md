# Notion Database Setup Instructions

## Issue
The enhanced ABM databases with complete schemas (40+ fields matching SKILL.md) haven't been created in your Notion workspace due to API permissions.

## Solution Options

### Option 1: Manual Database Creation (Recommended)
Since the API has permission issues, I recommend manually creating the databases in Notion using the exact schemas I've designed:

#### 1. Accounts Database
Create a database called "Verdigris ABM - Accounts" with these properties:

**Basic Fields:**
- Company Name (Title)
- Domain (Text)
- Employee Count (Number)
- ICP Fit Score (Number, 0-100)
- Account Research Status (Select: Not Started, In Progress, Complete)
- Last Updated (Date)

**Enhanced Firmographic Fields:**
- Business Model (Select: Cloud Provider, Colocation, Hyperscaler, AI-focused DC, Energy-intensive Facilities, Other)
- Data Center Locations (Text)
- Primary Data Center Capacity (Text)
- Recent Funding Status (Text)
- Growth Indicators (Text)
- Created At (Created time)

#### 2. Trigger Events Database
Create a database called "Verdigris ABM - Trigger Events" with these properties:

**Core Fields:**
- Event Description (Title)
- Account (Relation to Accounts database)
- Event Type (Select: Expansion, Leadership Change, AI Workload, Energy Pressure, Incident, Sustainability)
- Confidence (Select: High, Medium, Low)
- Confidence Score (Number, 0-100)
- Relevance Score (Number, 0-100)
- Detected Date (Date)
- Source URL (URL)
- Created At (Created time)

#### 3. Contacts Database
Create a database called "Verdigris ABM - Contacts" with these properties:

**Basic Contact Fields:**
- Name (Title)
- Account (Relation to Accounts database)
- Title (Text)
- LinkedIn URL (URL)
- Email (Email)

**MEDDIC Classification:**
- Buying Committee Role (Select: Economic Buyer, Technical Evaluator, Champion, Influencer, User, Blocker)

**Lead Scoring (Transparent):**
- ICP Fit Score (Number, 0-100)
- Buying Power Score (Number, 0-100)
- Engagement Potential Score (Number, 0-100)
- Final Lead Score (Formula: round(prop("ICP Fit Score") * 0.4 + prop("Buying Power Score") * 0.3 + prop("Engagement Potential Score") * 0.3))

**Research Status:**
- Research Status (Select: Not Started, Enriched, Analyzed)
- Role Tenure (Text)

**LinkedIn Enrichment:**
- LinkedIn Activity Level (Select: Weekly+, Monthly, Quarterly, Inactive)
- Network Quality (Select: High, Standard)

**Engagement Intelligence:**
- Problems They Likely Own (Multi-select: Power Capacity Planning, Uptime Pressure, Cost Optimization, Predictive Maintenance, Energy Efficiency, Reliability Engineering, Compliance/Reporting, Capacity Planning)
- Content Themes They Value (Multi-select: AI Infrastructure, Power Optimization, Sustainability, Reliability Engineering, Cost Reduction, Predictive Analytics, Energy Management)
- Connection Pathways (Text)
- Value-Add Ideas (Text)

**Technical Fields:**
- Apollo Contact ID (Text)
- Created At (Created time)

#### 4. Strategic Partnerships Database
Create a database called "Verdigris ABM - Strategic Partnerships" with these properties:

**Basic Partnership Fields:**
- Partner Name (Title)
- Account (Relation to Accounts database)
- Category (Select: DCIM, EMS, Cooling, DC Equipment, Racks, GPUs, Critical Facilities Contractors, Professional Services)
- Confidence (Select: High, Medium, Low)

**Evidence Tracking:**
- Evidence URL (URL)
- Relationship Evidence (Text)
- Detected Date (Date)

**Opportunity Analysis:**
- Verdigris Opportunity (Text)
- Partnership Action (Select: Investigate, Contact, Monitor, Not Relevant)
- Priority Score (Number, 0-100)
- Created At (Created time)

### Option 2: Fix API Permissions
If you want to use the automated creation scripts I've built:

1. Go to your Notion integration settings
2. Ensure the integration has "Insert content" capability
3. Share a parent page with the integration where databases can be created
4. Update the parent page ID in the creation scripts

### Option 3: Use Existing Databases
If you have existing ABM databases, I can:
1. Analyze their current schemas
2. Provide instructions to add the missing fields manually
3. Update our code to work with the existing structure

## What Happens Next

Once the databases are created (by any method), our production pipeline will be able to:

1. **Populate Genesis Cloud Data**: Our working Apollo integration has found Lorena Acosta (Director of Operations) and classified her as an Economic Buyer with 100/100 buying power
2. **Apply MEDDIC Classification**: Automatically categorize all contacts with persona types, engagement strategies, and educational content recommendations
3. **Enable Sales Intelligence**: Provide role-based conversation starters, objection handling, and follow-up cadences
4. **Support Dashboard**: The live dashboard will show enriched contact data with sales strategies

## Current Status

✅ **Working Systems:**
- Apollo API integration (finding real contacts)
- Enhanced deduplication with account linking
- MEDDIC persona classification with role intelligence
- Intelligent contact enrichment with sales strategies
- Complete database schema designs (40+ fields)

❌ **Blocked:**
- Creating databases in Notion (permissions issue)

The ABM research system is functionally complete - it just needs the databases created in Notion to store the enriched data.

## Recommendation

I recommend **Option 1 (Manual Creation)** because:
1. It's the fastest path to get working databases
2. You have full control over the setup
3. Our code will immediately work with the properly structured databases
4. You can see exactly what fields are being created

Would you like me to provide more detailed step-by-step instructions for manual database creation?