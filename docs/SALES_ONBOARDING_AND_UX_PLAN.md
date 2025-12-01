# Sales Onboarding & UX Improvement Plan

## Overview

This document outlines the strategy for making the Verdigris Signal Intelligence dashboard both **educational** (teaching sales employees key concepts) and **intuitive** (fixing UX issues and simplifying workflows).

---

## Part 1: Sales Education Features

### 1.1 Educational Context: What Sales Employees Need to Know

Sales employees need to understand several key concepts to effectively use this tool:

#### A. Physical Infrastructure Basics
**Why it matters**: Accounts with GPU/datacenter infrastructure are our ICP (Ideal Customer Profile).

| Infrastructure Type | What It Is | Why We Care |
|-------------------|------------|-------------|
| **GPU Infrastructure** | NVIDIA H100/A100, AMD MI300X | Direct ICP - these companies run AI workloads |
| **Datacenter Presence** | Colocation, owned facilities | Indicates scale and infrastructure needs |
| **Cooling Systems** | Liquid cooling, immersion | Advanced cooling = high-density compute |
| **Power Infrastructure** | UPS, generators, PDUs | Power management = Verdigris sweet spot |

#### B. ICP Fit Criteria
**Why it matters**: Not all accounts are equal. Understanding fit helps prioritize.

| Criteria | Score Weight | High-Fit Indicators |
|----------|-------------|---------------------|
| **Infrastructure** | 35% | GPU detected, datacenter ownership |
| **Business Fit** | 35% | AI/ML focus, large employee count, US-based |
| **Buying Signals** | 30% | Recent funding, expansion, hiring, AI workload increase |

#### C. MEDDIC Contact Roles
**Why it matters**: Different contacts serve different purposes in the sales cycle.

| Role | Description | How to Use |
|------|-------------|------------|
| **Entry Point** | Technical believers (Engineers, DevOps) | Start conversations, build internal champions |
| **Middle Decider** | Tooling decisions (IT Directors, Infra Managers) | Influence evaluation criteria |
| **Economic Buyer** | Budget authority (VPs, C-level, Finance) | Final approval, ROI conversations |

### 1.2 Proposed Educational Features

#### Feature 1: Contextual Tooltips (Quick Implementation)
Add info icons (ℹ️) next to key terms that reveal explanations on hover.

**Implementation locations:**
- `ScoreBadge.tsx`: Explain what the score means
- `InfrastructureBreakdown.tsx`: Explain each infrastructure type
- `ContactCard.tsx`: Explain MEDDIC roles
- `AccountDetail.tsx`: Explain score components

**Example tooltips:**
```typescript
// Infrastructure tooltip
"GPU Infrastructure detected means this company runs AI/ML workloads -
our #1 ICP indicator. Companies with NVIDIA H100/A100 clusters typically
have significant power management needs."

// Score tooltip
"Account Score (0-100) combines Infrastructure (35%), Business Fit (35%),
and Buying Signals (30%). Scores above 70 are 'Very High' priority."
```

#### Feature 2: Onboarding Tour (Medium Implementation)
A guided walkthrough for first-time users using a library like `react-joyride`.

**Tour stops:**
1. **Account List**: "These are your target accounts, sorted by score. Higher = better fit."
2. **Score Badge**: "Scores indicate ICP fit. Green = Very High priority."
3. **Infrastructure Breakdown**: "This shows what physical infrastructure we detected."
4. **Deep Research Button**: "Click to run our 5-phase AI research pipeline."
5. **Vendor Discovery**: "Discover new vendor relationships using AI."
6. **Contacts Section**: "Contacts are classified by MEDDIC role for sales strategy."

#### Feature 3: Glossary Page / Help Modal (Full Implementation)
A dedicated page or modal with comprehensive definitions.

**Sections:**
- Infrastructure Types (with icons and examples)
- Scoring Methodology (with worked examples)
- MEDDIC Framework (with outreach templates)
- Button Explanations (what each action does)
- Workflow Examples (step-by-step guides)

#### Feature 4: Inline Education Cards (Full Implementation)
Dismissable cards in the UI that teach concepts in context.

**Example placements:**
- First time viewing account with GPU: "This account has GPU infrastructure detected!"
- Empty contacts: "No contacts yet? Click 'Enrich Contacts' to discover them."
- Low score explanation: "Score below 60? Focus on higher-priority accounts first."

---

## Part 2: UX Improvements & Bug Fixes

### 2.1 Identified UX Issues

Based on the user's concerns, here are the issues to address:

| Issue | Severity | Current Behavior | Desired Behavior |
|-------|----------|------------------|------------------|
| **Filtering unclear** | Medium | Filters exist but hard to discover | Clear filter UI with labels |
| **Sorting confusion** | Medium | Sort by dropdown works | Add visual indicator of sort |
| **Add account flow** | High | Button exists but easy to miss | More prominent CTA |
| **Deep Research unclear** | High | Button with no explanation | Tooltip + confirmation dialog |
| **Research on existing** | High | Research button exists | Clearer labeling |
| **Button purposes unclear** | High | Multiple action buttons | Group + label by purpose |

### 2.2 Proposed UX Fixes

#### Fix 1: Button Grouping & Labels
Group related actions with clear headers:

```
┌─────────────────────────────────────────────────────┐
│ 🔬 INTELLIGENCE ACTIONS                             │
├─────────────────────────────────────────────────────┤
│ [Deep Research]  Run 5-phase AI analysis pipeline   │
│ [Enrich Contacts] Discover contacts via Apollo      │
│ [Discover Vendors] Find vendor relationships        │
├─────────────────────────────────────────────────────┤
│ 📊 QUICK ACTIONS                                    │
├─────────────────────────────────────────────────────┤
│ [Refresh Events]  Re-scan for trigger events        │
└─────────────────────────────────────────────────────┘
```

#### Fix 2: Confirmation Dialogs
Before running expensive operations, show a dialog:

```
┌─────────────────────────────────────────────────────┐
│ Run Deep Research on "NVIDIA Corporation"?          │
├─────────────────────────────────────────────────────┤
│ This will:                                          │
│ • Search for company intelligence                   │
│ • Detect infrastructure & partnerships              │
│ • Find trigger events and buying signals            │
│ • Discover contacts and classify by MEDDIC          │
│ • Update Notion with findings                       │
│                                                     │
│ Estimated time: 2-5 minutes                         │
│ Estimated cost: ~$0.30 API credits                  │
│                                                     │
│           [Cancel]  [Run Research]                  │
└─────────────────────────────────────────────────────┘
```

#### Fix 3: Empty State Guidance
When no account is selected, show a more helpful guide:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              📊 Getting Started                     │
│                                                     │
│  1. Select an account from the left panel           │
│  2. Review their ICP score and infrastructure       │
│  3. Click "Deep Research" for full analysis         │
│  4. Find contacts and plan your outreach            │
│                                                     │
│  Need to add a new account?                         │
│  Click [+ Add Account] in the account list          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Fix 4: Filter/Sort Improvements
Make filters more discoverable:

```
┌─────────────────────────────────────────────────────┐
│ 🎯 ACCOUNTS (11)                                    │
├─────────────────────────────────────────────────────┤
│ Filter: [All ▼] [Has GPU ▼] [Priority ▼]           │
│ Sort:   [Score ↓]  ← showing sort direction        │
├─────────────────────────────────────────────────────┤
│ [+ Add Account]  [🔄 Refresh]                       │
└─────────────────────────────────────────────────────┘
```

---

## Part 3: Comprehensive UX Testing Plan

### 3.1 Functional Test Cases

| # | Test Area | Test Case | Steps | Expected Result |
|---|-----------|-----------|-------|-----------------|
| 1 | Account List | Load accounts | Open app | Accounts load with scores |
| 2 | Account List | Sort by score | Click sort dropdown | List reorders correctly |
| 3 | Account List | Filter by priority | Select "Very High" | Only high-score accounts show |
| 4 | Add Account | Create new account | Click +, enter domain | Account appears in list |
| 5 | Add Account | Validation | Enter invalid domain | Shows error message |
| 6 | Account Detail | View account | Click account row | Detail panel opens |
| 7 | Account Detail | Close panel | Click X button | Panel closes |
| 8 | Deep Research | Run research | Click button | Progress shows, results appear |
| 9 | Deep Research | Cancel midway | Click during progress | Operation handles gracefully |
| 10 | Contact Enrichment | Enrich contacts | Click button | Contacts discovered and shown |
| 11 | Vendor Discovery | Discover vendors | Click button | Vendors discovered and categorized |
| 12 | Trigger Events | Refresh events | Click refresh | New events detected |
| 13 | Partnerships Tab | View partnerships | Click tab | Partnership list loads |
| 14 | What's New | Open changelog | Click button | Modal opens with versions |
| 15 | Score Display | Score accuracy | Check against Notion | Scores match Notion values |

### 3.2 Edge Case Tests

| # | Scenario | Test Case | Expected Handling |
|---|----------|-----------|-------------------|
| 1 | No accounts | Empty database | Show "No accounts" state |
| 2 | No contacts | Account with 0 contacts | Show "No contacts yet" prompt |
| 3 | No GPU | Account without GPU | Show appropriate infrastructure |
| 4 | API down | Server not running | Show error with helpful message |
| 5 | Long names | Account with 50+ char name | Truncate gracefully |
| 6 | Special chars | Account name with &,',< | Render without XSS |
| 7 | Slow network | 3G connection speed | Show loading states |
| 8 | Concurrent ops | Click 2 buttons fast | Handle race conditions |

### 3.3 Mobile/Responsive Tests

| # | Viewport | Test Case | Expected Result |
|---|----------|-----------|-----------------|
| 1 | Desktop (1920px) | Full layout | Two-column layout |
| 2 | Laptop (1366px) | Standard view | Responsive scaling |
| 3 | Tablet (768px) | Collapsed view | Stacked layout |
| 4 | Mobile (375px) | Mobile view | Single column |

### 3.4 Accessibility Tests

| # | Test | Tool | Acceptance |
|---|------|------|------------|
| 1 | Keyboard nav | Manual | All interactive elements focusable |
| 2 | Screen reader | VoiceOver | Labels read correctly |
| 3 | Color contrast | axe-core | WCAG AA compliance |
| 4 | Focus indicators | Manual | Visible focus rings |

---

## Part 4: Implementation Priority

### Phase 1: Quick Wins (1-2 days)
- [ ] Add tooltips to key UI elements
- [ ] Improve empty state guidance
- [ ] Add confirmation dialog for Deep Research
- [ ] Fix any obvious filtering/sorting bugs

### Phase 2: Core Features (3-5 days)
- [ ] Implement button grouping with labels
- [ ] Add onboarding tour with react-joyride
- [ ] Create Help/Glossary modal
- [ ] Run full UX test suite

### Phase 3: Advanced Features (5-10 days)
- [ ] Inline education cards with localStorage persistence
- [ ] Video tutorials / animated guides
- [ ] Contextual help based on user actions
- [ ] Analytics to track feature usage

---

## Part 5: Files to Create/Modify

### New Files
```
dashboard/src/components/Tooltip.tsx          # Reusable tooltip component
dashboard/src/components/OnboardingTour.tsx   # Guided tour component
dashboard/src/components/HelpModal.tsx        # Glossary/help modal
dashboard/src/components/ConfirmDialog.tsx    # Confirmation dialog
dashboard/src/data/tooltips.ts                # Tooltip content
dashboard/src/data/glossary.ts                # Glossary definitions
```

### Existing Files to Modify
```
dashboard/src/components/AccountDetail.tsx    # Add tooltips, button grouping
dashboard/src/components/AccountList.tsx      # Improve filter/sort UX
dashboard/src/components/ScoreBadge.tsx       # Add score explanation tooltip
dashboard/src/components/ResearchButton.tsx   # Add confirmation dialog
dashboard/src/components/EnrichmentButton.tsx # Add confirmation dialog
dashboard/src/App.tsx                         # Add onboarding tour trigger
```

---

## Summary

This plan addresses both **education** (helping sales understand concepts) and **usability** (making the app intuitive). The phased approach allows for quick wins while building toward a more comprehensive solution.

Key principles:
1. **Progressive disclosure**: Show simple info first, details on demand
2. **Contextual learning**: Teach where the user needs to know
3. **Confirm before costly actions**: Prevent accidental operations
4. **Clear feedback**: Always show what's happening

Next step: Implement Phase 1 (tooltips, empty states, confirmation dialogs).
