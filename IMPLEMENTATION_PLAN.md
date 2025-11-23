# ABM Research System - Full Implementation Plan

**Objective**: Create a working ABM research system that actually populates your real Notion databases and provides a usable dashboard for Genesis Cloud and other target accounts.

**Critical Success Criteria**:
- ✅ Data flows from research → Notion → dashboard
- ✅ No false success claims - QA Agent verifies everything
- ✅ Uses your actual Notion database URLs (not new databases)
- ✅ Sequential gates prevent progression until requirements are met

---

## Agent Architecture Overview

### 🎯 The Problem This Solves
Previous implementations claimed success but QA testing revealed:
- 0/4 databases accessible
- No Genesis Cloud data in Notion
- Dashboard reading hardcoded data instead of Notion
- Pattern of claiming completion without verification

### 🤖 Agent Solution
5 specialized agents with sequential gates prevent false progress:

1. **QA Verification Agent** - Tests every claim before marking complete
2. **Product Design Agent** - Holds process accountable to SKILL.md
3. **Data Pipeline Agent** - Owns research-to-Notion data flow
4. **Codebase Hygiene Agent** - Maintains repository cleanliness
5. **System Integration Agent** - Orchestrates with sequential gates

---

## Sequential Gate Implementation

### 🚪 Gate 1: System Health Check
**Requirement**: Codebase health score ≥70%, all required files present

**Verification**:
```bash
python agents/codebase_hygiene_agent.py
```

**Must Pass Before**: Any other gates can execute
**Blockers**: Missing files, too many unused/duplicate files
**Resolution**: Run codebase cleanup, organize files into agents/core/dashboard directories

---

### 🚪 Gate 2: SKILL.md Compliance
**Requirement**: Implementation matches 5-phase specification exactly

**Verification**:
```bash
python agents/product_design_agent.py
```

**Must Pass Before**: Data pipeline execution
**Blockers**: Missing phase implementations, incorrect scoring formulas, API integrations not configured
**Resolution**: Implement missing components according to `/tmp/verdigris-abm-research/SKILL.md`

---

### 🚪 Gate 3: Data Pipeline Execution
**Requirement**: Complete 5-phase ABM research for Genesis Cloud

**Verification**:
```bash
python agents/data_pipeline_agent.py
```

**Must Pass Before**: Notion validation
**Blockers**: API failures, incomplete phases, Notion population errors
**Resolution**: Fix API integrations, ensure all 5 phases complete successfully

---

### 🚪 Gate 4: Notion Database Validation
**Requirement**: All 4 databases accessible with Genesis Cloud data populated

**Verification**:
```bash
python agents/qa_verification_agent.py
```

**Must Pass Before**: Dashboard integration
**Blockers**: Database connection failures, empty databases, incorrect data structure
**Resolution**: Fix Notion API configuration, verify database schemas match specification

---

### 🚪 Gate 5: End-to-End Integration
**Requirement**: Dashboard reads live data from Notion databases

**Verification**:
```bash
python agents/system_integration_agent.py
```

**Must Pass Before**: System declared operational
**Blockers**: Dashboard not connected to Notion, data flow broken
**Resolution**: Implement dashboard-Notion integration, verify data flows correctly

---

## Step-by-Step Execution Plan

### Step 1: Validate Current System State
```bash
# Check what's actually working vs. claimed
cd /Users/chungty/Projects/vdg-clean/abm-research
python agents/qa_verification_agent.py
```

**Expected Result**: FAIL status with specific blockers identified
**Action**: Document all failures - these become our todo list

### Step 2: System Health Restoration
```bash
# Clean up codebase and organize structure
python agents/codebase_hygiene_agent.py
```

**Expected Result**: Health score ≥70%, organized file structure
**Action**: Move files to proper directories, remove unused code

### Step 3: SKILL.md Compliance Verification
```bash
# Ensure implementation matches specification
python agents/product_design_agent.py
```

**Expected Result**: All 5 phases implemented, scoring formulas correct, APIs configured
**Action**: Fix any non-compliant implementations

### Step 4: Execute Data Pipeline
```bash
# Run complete 5-phase research for Genesis Cloud
export NOTION_API_KEY="your_actual_notion_key"
export APOLLO_API_KEY="OlqAmaYqWy--Gds7mmoH-g"
export OPENAI_API_KEY="sk-proj-..."
python agents/data_pipeline_agent.py
```

**Expected Result**: 5/5 phases completed, Notion databases populated
**Action**: Fix any API failures, ensure complete data flow

### Step 5: Notion Validation
```bash
# Verify databases are accessible and contain data
python agents/qa_verification_agent.py
```

**Expected Result**: PASS status on all database tests
**Action**: If failed, investigate Notion API issues, verify database schemas

### Step 6: Dashboard Integration
```bash
# Connect dashboard to read from real Notion databases
python agents/system_integration_agent.py
```

**Expected Result**: Dashboard displays live Genesis Cloud data from Notion
**Action**: Implement dashboard-Notion API integration

### Step 7: Complete Workflow Verification
```bash
# Test end-to-end workflow
python agents/system_integration_agent.py
```

**Expected Result**: All 5 gates pass, system declared operational
**Action**: Address any remaining blockers

---

## Critical Implementation Details

### 🗄️ Your Actual Notion Database IDs
**Never create new databases** - use these exact IDs:
- Accounts: `c31d728f-4770-49e2-8f6b-d68717e2c160`
- Trigger Events: `c8ae1662-cba9-4ea3-9cb3-2bcea3621963`
- Contacts: `a6e0cace-85de-4afd-be6c-9c926d1d0e3d`
- Strategic Partnerships: `fa1467c0-ad15-4b09-bb03-cc715f9b8577`

### 🔑 Required API Keys
```bash
export NOTION_API_KEY="your_actual_notion_integration_key"
export APOLLO_API_KEY="OlqAmaYqWy--Gds7mmoH-g"
export OPENAI_API_KEY="sk-proj-kQ1wGx1DfmpLwDoXT3oWScS6-7bgB1hUakEf7TWefVNAUjFYtOZsGVrEb9APo5UXGdBhkyOcZIA"
```

### 📊 Scoring Formula (Must Match SKILL.md)
**Final Lead Score** = (ICP Fit × 0.40) + (Buying Power × 0.30) + (Engagement × 0.30)

### 🎯 Target Contact Filtering
**ONLY target power infrastructure decision makers**:
- VP/Director of Data Center Operations
- VP/Director of Critical Infrastructure
- VP/Director of Site Operations
- Head of Data Center Engineering

**EXCLUDE**: HR managers, tech support, generic IT roles

---

## Quality Assurance Protocol

### 🔍 Before Marking Any Task Complete:
1. **Run QA Agent**: `python agents/qa_verification_agent.py`
2. **Verify Claims**: Check actual database contents, not logs
3. **Test Data Flow**: Confirm dashboard shows live Notion data
4. **Document Failures**: List specific blockers, not general errors

### 🚫 Never Claim Success Until:
- QA Agent returns PASS status
- All sequential gates completed
- Manual verification confirms data flow
- Dashboard displays correct live data

---

## Success Metrics

### 📈 System Operational Definition:
- ✅ All 5 sequential gates pass
- ✅ QA Agent reports PASS status (not FAIL)
- ✅ Genesis Cloud data visible in all 4 Notion databases
- ✅ Dashboard reads and displays live Notion data
- ✅ Can execute complete workflow for new accounts

### 📊 Genesis Cloud Success Criteria:
- **Accounts**: 1 record with ICP fit score and research status
- **Trigger Events**: 3-5 events with confidence/relevance scores
- **Contacts**: 10-30 contacts with final lead scores and buying committee roles
- **Strategic Partnerships**: 3-10 partnerships with Verdigris opportunity angles

---

## Troubleshooting Guide

### 🐛 Common Issues and Fixes:

**"Database not accessible"**
- Verify Notion API key is correct and has database permissions
- Check database IDs match exactly (no typos)
- Test API connection with simple query first

**"Data pipeline fails at Phase X"**
- Check API rate limits and retry logic
- Verify input data format matches expected structure
- Test individual phase functions independently

**"Dashboard shows hardcoded data"**
- Confirm dashboard is making Notion API calls
- Check API responses contain actual data
- Verify JSON parsing and display logic

**"QA tests still failing after fixes"**
- Re-run QA agent after each fix
- Check QA agent is testing current state, not cached results
- Verify test criteria match actual requirements

---

## Next Steps After Implementation

### 🎯 Once System is Operational:
1. **Test with additional accounts** (besides Genesis Cloud)
2. **Refine scoring formulas** based on salesperson feedback
3. **Add more trigger event sources** for better coverage
4. **Enhance dashboard UI** with additional visualizations
5. **Implement automated account research scheduling**

### 📋 Value-Add Content Development:
- Create white papers for different ICP pain points
- Develop case studies for specific use cases (AI workloads, sustainability)
- Build content matching system for engagement intelligence

---

## Implementation Timeline

**Phase 1** (Day 1): System Health & Compliance - Run Gates 1-2
**Phase 2** (Day 2): Data Pipeline Implementation - Run Gate 3
**Phase 3** (Day 3): Notion Integration - Run Gate 4
**Phase 4** (Day 4): Dashboard Integration - Run Gate 5
**Phase 5** (Day 5): End-to-End Testing & Documentation

**Success Definition**: All 5 gates pass, QA Agent reports PASS, Genesis Cloud data flows from research → Notion → dashboard without false claims or manual intervention.

---

*This implementation plan uses sequential gates to prevent the pattern of claiming success without verification. Each gate must pass before progression, ensuring we build a truly working system rather than sophisticated-looking code that doesn't actually function.*