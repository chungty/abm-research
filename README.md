# Verdigris ABM Intelligence System

Production-ready Account-Based Marketing intelligence platform that transforms research data into actionable sales strategies.

## 🎯 Vision: Research → Intelligence → Action

This system doesn't just collect account data - it synthesizes contextual intelligence into ready-to-execute sales actions with pre-written messaging, partnership angles, and optimal timing.

## 🚀 Account Command Center Features

- **Opportunity Intelligence Briefing**: 30-second strategic context for each account
- **Priority Action Queue**: Contact prioritization with synthesized next actions
- **Conversation Assets**: Pre-written LinkedIn messages and email templates
- **Partnership Intelligence**: Warm intro paths via existing vendor relationships
- **Live Trigger Monitoring**: Real-time opportunity detection with business context
- **Competitive Positioning**: Strategic advantages and conversation positioning

## 🏗️ Architecture: Intelligence-Driven Sales Workflow

```
Trigger Detection → Account Research → Contact Intelligence → Action Synthesis → Sales Execution
       ↓                    ↓              ↓                    ↓                ↓
   Market Events        ICP Scoring     LinkedIn Activity    Message Templates   Revenue
   Competitive Intel    Partnership     Role Analysis        Timing Strategy     Results
   Leadership Changes   Context         Pain Points          Intro Pathways      Closed Deals
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Install dependencies
pip install -e .

# Configure environment
cp .env.template .env
# Add your API keys: NOTION_API_KEY, APOLLO_API_KEY
```

### 2. Launch Account Command Center
```bash
cd src && python3 abm_research/dashboard/abm_dashboard.py
```

**Visit**: http://localhost:8081 to see Genesis Cloud account intelligence demo

### 3. API Access
```bash
# Start research via API
curl -X POST -H "Content-Type: application/json" \
  -d '{"company_name":"Genesis Cloud","domain":"genesiscloud.com"}' \
  http://localhost:8081/api/research/start

# Check system health
curl http://localhost:8081/api/health
```

## 📋 Core Architecture

### Consolidated System (src/abm_research/)
- **core/abm_system.py**: 5-phase research pipeline orchestration
- **dashboard/abm_dashboard.py**: Account Command Center interface
- **integrations/notion_client.py**: Unified Notion workspace management
- **phases/**: Individual research phase implementations
- **intelligence/**: AI-powered analysis engines

### Example Account Workflow
```bash
# Genesis Cloud Intelligence Briefing generates:
1. Opportunity Brief: "10x GPU expansion + power challenges = 14-day window"
2. Priority Actions: Jennifer Martinez (VP Ops) - LinkedIn message ready
3. Partnership Angles: NVIDIA intro path identified
4. Competitive Position: vs Schneider Electric positioning prepared
5. Message Templates: Personalized outreach with CoreWeave case study
```

## 🧪 Testing & Validation

```bash
# Test consolidated system
python3 -c "from abm_research.core.abm_system import ComprehensiveABMSystem; \
  abm = ComprehensiveABMSystem(); \
  result = abm.conduct_complete_account_research('Stripe', 'stripe.com'); \
  print('✅ Research Complete:', len(result.get('contacts', [])))"

# Validate all imports
pytest tests/unit/ -v

# End-to-end integration test
python3 -c "import requests; \
  r = requests.post('http://localhost:8081/api/research/start', \
    json={'company_name': 'Test Company', 'domain': 'test.com'}); \
  print('API Response:', r.json())"
```

## 🎯 Results: From Research Data to Sales Action

**Traditional ABM**: "Here's contact data for Genesis Cloud"
**Verdigris ABM Intelligence**:

```
🎯 GENESIS CLOUD OPPORTUNITY BRIEF
10x GPU expansion triggered by CoreWeave funding pressure.
VP Ops posted about power density challenges 3 days ago.
→ SEND: LinkedIn message with CoreWeave case study reference
→ TIMING: Next 14 days during infrastructure planning
→ INTRO: NVIDIA partnership team warm introduction available
→ POSITIONING: "Predictive monitoring prevents $2M+ expansion delays"
```

**Impact**: From hours of research → seconds of strategic execution
