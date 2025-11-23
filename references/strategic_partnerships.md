# Strategic Partnership Intelligence

## Overview

Identify existing vendor relationships at target accounts to uncover co-sell opportunities, integration pathways, and warm introduction routes for Verdigris partnerships team.

## Vendor Categories (Verdigris-Relevant)

### 1. Data Center Infrastructure Management (DCIM)
**Examples:** Schneider Electric EcoStruxure, Sunbird DCIM, FNT Command, nlyte, Device42, CA Technologies

**Detection signals:**
- Job postings mentioning DCIM software
- LinkedIn posts about DCIM implementations
- Integration partnerships announced
- Employee profiles listing DCIM skills

**Verdigris opportunity angle:**
- Integration potential (API connectivity for real-time power data)
- Co-sell partnerships (Verdigris + DCIM = complete visibility)
- Complementary capabilities (Verdigris fills gaps in electrical risk detection)

### 2. Energy Management Systems (EMS)
**Examples:** Siemens Desigo, Honeywell Forge, Johnson Controls Metasys, Veolia Energy Management

**Detection signals:**
- Press releases about energy optimization initiatives
- Job postings for EMS specialists
- Sustainability reports mentioning EMS platforms

**Verdigris opportunity angle:**
- Data enrichment (Verdigris provides granular circuit-level data)
- Upgrade path (Verdigris replaces legacy EMS for data centers)

### 3. Cooling Systems
**Examples:** Vertiv (Liebert), Schneider Electric (APC), Stulz, Rittal, Trane, Carrier

**Detection signals:**
- Facility expansion announcements mentioning cooling vendors
- Job postings for "Vertiv technician" or similar
- LinkedIn posts about cooling infrastructure

**Verdigris opportunity angle:**
- Co-deployment (Verdigris monitors cooling system electrical performance)
- Optimization (identify inefficient cooling via power data)

### 4. Data Center Equipment (PDUs, UPS, Generators)
**Examples:** Eaton, APC by Schneider, Vertiv, Generac, Caterpillar, Cummins

**Detection signals:**
- Equipment procurement announcements
- Job postings for UPS/generator technicians
- LinkedIn posts about infrastructure upgrades

**Verdigris opportunity angle:**
- Monitoring integration (track health of critical equipment)
- Warranty/SLA compliance (prove equipment performance)

### 5. Racks and Cabinets
**Examples:** Chatsworth Products (CPI), Legrand, Panduit, Rittal, APC NetShelter

**Detection signals:**
- Buildout announcements
- LinkedIn posts from facilities managers
- Job postings mentioning rack infrastructure

**Verdigris opportunity angle:**
- Rack-level monitoring (Verdigris per-rack power visibility)
- Capacity planning (right-size rack deployments based on actual usage)

### 6. GPU Infrastructure Vendors
**Examples:** NVIDIA DGX, AMD Instinct, CoreWeave, Lambda Labs, Supermicro, Dell PowerEdge

**Detection signals:**
- AI infrastructure announcements
- GPU cluster buildouts
- Partnerships with AI companies
- Job postings for HPC/AI infrastructure engineers

**Verdigris opportunity angle:**
- High-density monitoring (GPU racks push power/cooling limits)
- AI-specific use case (predictive capacity planning for GPU workloads)

### 7. Critical Facilities Contractors
**Examples:** AECOM, Turner Construction, DPR Construction, FORTIS, Gensler, Mazzetti

**Detection signals:**
- Facility construction/renovation announcements
- LinkedIn posts about new builds
- Job postings for construction project managers

**Verdigris opportunity angle:**
- Design-build integration (specify Verdigris in new facilities)
- Retrofit projects (add monitoring to existing infrastructure)

### 8. Professional Services (Commissioning, MEP, Energy Consulting)
**Examples:** Cx Associates, EYP Mission Critical, Stantec, Buro Happold, WSP, RMF Engineering

**Detection signals:**
- LinkedIn posts about commissioning projects
- Job postings for commissioning engineers
- Press releases about MEP upgrades

**Verdigris opportunity angle:**
- Post-commissioning monitoring (continuous validation)
- Energy audits (Verdigris provides ongoing audit data)

## Detection Workflow

1. **Web search**: "{company name} + {vendor category}" (e.g., "Genesis Cloud Schneider Electric")
2. **LinkedIn company page**: Search posts for vendor mentions
3. **Job postings**: Look for specific vendor software/hardware in requirements
4. **Employee LinkedIn profiles**: Check for vendor-specific skills or certifications
5. **Company website**: Scan case studies, testimonials, partner pages
6. **Industry databases**: Check partnership directories (e.g., Uptime Institute, DCD partners)

## Output Format

For each detected partnership:
- **Partner name** (specific company)
- **Category** (from 8 categories above)
- **Relationship evidence** (source URL, quote/screenshot)
- **Detected date** (when relationship was discovered)
- **Confidence level** (High: direct announcement, Medium: job posting, Low: social signal)
- **Verdigris opportunity angle** (specific co-sell/integration recommendation)
- **Partnership team action** (select: Investigate, Contact, Monitor, Not Relevant)

## Filtering Rules

**Include:**
- Vendors in the 8 categories above
- Relationships detected in past 24 months
- Medium or high confidence evidence

**Exclude:**
- Generic IT vendors (Microsoft, Google Workspace, Salesforce, etc.)
- Office equipment/furniture
- Non-technical service providers (catering, janitorial)
- Consumer brands (unless part of data center infrastructure)

## Opportunity Prioritization

**High priority (investigate immediately):**
- DCIM vendors (direct integration opportunity)
- GPU infrastructure vendors (AI workload angle)
- New facility construction (design-in opportunity)

**Medium priority (monitor for warm intro):**
- Cooling system vendors
- Professional services firms
- Energy management platforms

**Low priority (informational only):**
- Legacy equipment vendors with no integration path
- Commodity suppliers (racks, cables)
