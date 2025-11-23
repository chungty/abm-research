# ABM Research System

A production-ready Account-Based Marketing intelligence system with LinkedIn enrichment and Notion integration.

## 🎯 Features

- **Complete ABM Pipeline**: 5-phase research system (Account Intelligence, Contact Discovery, LinkedIn Enrichment, Engagement Intelligence, Partnership Intelligence)
- **LinkedIn Real Data Integration**: AI-enhanced profile analysis with activity tracking and content themes
- **Notion Persistence**: Automatic saving of enriched contact data to Notion databases
- **Apollo Integration**: Contact discovery via Apollo API
- **Trigger Event Detection**: Real-time monitoring for expansion, leadership changes, AI workloads, etc.
- **Intelligent Caching**: Local LinkedIn profile caching to minimize API costs

## 🏗️ Architecture

```
LinkedIn Profile → AI Enhancement → Local Cache → Notion Database → Dashboard
     ↓                    ↓              ↓            ↓              ↓
Real/Enhanced        Engagement     Performance    Persistence    Real-time
Profile Data         Analysis        Caching        Layer         Display
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
cp .env.template .env
# Fill in your API keys in .env
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test the System
```bash
python test_linkedin_integration.py      # Test LinkedIn integration
python test_notion_persistence.py        # Test Notion persistence
```

### 4. Run ABM Research
```bash
python comprehensive_abm_system.py
```

## 📋 Core Components

- **linkedin_enrichment_engine.py**: LinkedIn profile analysis and scoring
- **notion_persistence_manager.py**: Notion database integration
- **comprehensive_abm_system.py**: Complete 5-phase research pipeline
- **apollo_contact_discovery.py**: Contact discovery via Apollo
- **enhanced_trigger_event_detector.py**: Real-time trigger event monitoring

## 🧪 Testing

```bash
python test_linkedin_integration.py     # LinkedIn enrichment tests
python test_notion_persistence.py       # Notion integration tests
python test_full_abm_integration.py     # Complete pipeline tests
```

## 📊 Results

The system enriches LinkedIn profiles with:
- Lead scores with engagement dimension
- Activity levels and content themes
- Connection pathways for warm introductions
- Responsibility keyword analysis

All data automatically saves to Notion for dashboard use.
