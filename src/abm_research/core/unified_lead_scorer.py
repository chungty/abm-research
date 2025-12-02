#!/usr/bin/env python3
"""
Unified Lead Scoring Engine - Consolidates 3 duplicate implementations
Combines organizational hierarchy, geographic scoring, and AI-powered recommendations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import openai

logger = logging.getLogger(__name__)


class ScoreThreshold(Enum):
    """Lead score priority thresholds"""
    HIGH_PRIORITY = 70.0
    MEDIUM_PRIORITY = 50.0
    LOW_PRIORITY = 0.0


class GeographicPriority(Enum):
    """Geographic market priority classification"""
    US_PRIMARY = "US Primary"
    US_SECONDARY = "US Secondary"
    INTERNATIONAL_WITH_US = "International with US Presence"
    INTERNATIONAL_ONLY = "International Only"


@dataclass
class DecisionInfluence:
    """Maps roles to their decision-making influence based on org charts"""
    budget_authority: float      # 0-1: Can they approve budget?
    pain_ownership: float        # 0-1: Do they own the pain point?
    champion_ability: float      # 0-1: Can they sell internally?
    entry_point_value: float     # 0-1: Good starting point for outreach?


@dataclass
class InfrastructureBreakdown:
    """Infrastructure scoring breakdown with full traceability"""
    score: float  # 0-100
    breakdown: Dict[str, Dict[str, Any]]  # category -> {detected, points, max_points}
    raw_text: str  # Original infrastructure text for reference

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for Notion storage"""
        return {
            'score': round(self.score, 1),
            'breakdown': self.breakdown,
            'raw_text': self.raw_text
        }


@dataclass
class BusinessFitBreakdown:
    """Business fit scoring breakdown"""
    score: float
    industry_fit: Dict[str, Any]
    company_size_fit: Dict[str, Any]
    geographic_fit: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': round(self.score, 1),
            'industry_fit': self.industry_fit,
            'company_size_fit': self.company_size_fit,
            'geographic_fit': self.geographic_fit
        }


@dataclass
class BuyingSignalsBreakdown:
    """Buying signals scoring breakdown"""
    score: float
    trigger_events: Dict[str, Any]
    expansion_signals: Dict[str, Any]
    hiring_signals: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': round(self.score, 1),
            'trigger_events': self.trigger_events,
            'expansion_signals': self.expansion_signals,
            'hiring_signals': self.hiring_signals
        }


@dataclass
class AccountScore:
    """Comprehensive account score with full traceability for dashboard display"""
    total_score: float  # 0-100
    infrastructure_fit: InfrastructureBreakdown
    business_fit: BusinessFitBreakdown
    buying_signals: BuyingSignalsBreakdown
    priority_level: str  # "Very High", "High", "Medium", "Low"

    def get_score_breakdown(self) -> Dict[str, Any]:
        """Get full breakdown for dashboard display"""
        return {
            'total_score': round(self.total_score, 1),
            'infrastructure_fit': {
                'score': round(self.infrastructure_fit.score, 1),
                'weight': '35%',
                'breakdown': self.infrastructure_fit.breakdown
            },
            'business_fit': {
                'score': round(self.business_fit.score, 1),
                'weight': '35%',
                'breakdown': self.business_fit.to_dict()
            },
            'buying_signals': {
                'score': round(self.buying_signals.score, 1),
                'weight': '30%',
                'breakdown': self.buying_signals.to_dict()
            },
            'priority_level': self.priority_level
        }


@dataclass
class LeadScore:
    """Comprehensive lead score with full transparency"""
    # Core component scores (0-100 each)
    icp_fit_score: float
    buying_power_score: float
    engagement_potential_score: float
    geographic_fit_score: float
    organizational_influence_score: float

    # Final weighted score
    final_score: float

    # Additional context
    role_classification: str
    geographic_priority: GeographicPriority
    priority_level: str

    def get_score_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of all score components"""
        return {
            'ICP Fit': round(self.icp_fit_score, 1),
            'Buying Power': round(self.buying_power_score, 1),
            'Engagement Potential': round(self.engagement_potential_score, 1),
            'Geographic Fit': round(self.geographic_fit_score, 1),
            'Organizational Influence': round(self.organizational_influence_score, 1),
            'Final Score': round(self.final_score, 1)
        }


# ============================================================================
# ACCOUNT SCORER - Account-First Scoring with Infrastructure Traceability
# ============================================================================

class AccountScorer:
    """
    Score accounts based on infrastructure fit, business fit, and buying signals.
    Infrastructure is an ACCOUNT-level attribute - the company owns the UPS, not individual contacts.

    Scoring Dimensions:
    - Infrastructure Fit (35%): Physical data center infrastructure detection
    - Business Fit (35%): Industry, company size, geographic alignment
    - Buying Signals (30%): Trigger events, expansion, hiring signals

    Full traceability: Stores exact keywords detected for dashboard display.
    """

    # Infrastructure keywords for scoring (aligned with account_intelligence_engine.py)
    # PRIORITY: GPU/Neocloud infrastructure is TARGET ICP - highest scoring
    INFRASTRUCTURE_KEYWORDS = {
        'gpu_infrastructure': {
            # TARGET ICP: Neocloud GPU datacenters - HIGHEST PRIORITY
            'keywords': ['nvidia', 'h100', 'a100', 'dgx', 'gpu cluster', 'ai infrastructure',
                        'v100', 'gpu farm', 'ml infrastructure', 'hgx', 'cuda', 'gpu compute',
                        'ai training', 'inference cluster', 'neocloud'],
            'max_points': 40,  # HIGHEST - target ICP
            'description': 'GPU/AI infrastructure - TARGET ICP (neocloud datacenter)'
        },
        'target_vendors': {
            'keywords': ['schneider electric', 'apc', 'vertiv', 'eaton', 'liebert', 'raritan'],
            'max_points': 30,
            'description': 'Target vendor (competitive displacement opportunity)'
        },
        'power_systems': {
            'keywords': ['ups', 'pdu', 'power distribution', 'uninterruptible power',
                        'power monitoring', 'power management', 'power meters', 'rack pdu'],
            'max_points': 25,
            'description': 'Power infrastructure detected'
        },
        'cooling_systems': {
            # Liquid cooling especially important for GPU datacenters
            'keywords': ['crac', 'crah', 'precision cooling', 'liquid cooling', 'immersion cooling',
                        'thermal management', 'data center cooling', 'rear door cooling',
                        'direct-to-chip cooling'],
            'max_points': 20,
            'description': 'Cooling infrastructure (critical for GPU density)'
        },
        'dcim_software': {
            'keywords': ['dcim', 'struxureware', 'trellis', 'nlyte', 'sunbird', 'device42'],
            'max_points': 15,
            'description': 'DCIM software detected'
        },
        'dc_rectifier_systems': {
            # DC Rectifier ICP - Companies interested in DC power infrastructure
            'keywords': [
                # Core DC Power terms
                '48vdc', '48v dc', '380vdc', '380v dc', 'dc power', 'dc distribution',
                'rectifier', 'ac-to-dc', 'ac to dc', 'power conversion',
                # Equipment
                'busbar', 'dc busbar', 'rectifier cabinet', 'power shelf',
                # Efficiency terms
                'rectifier efficiency', 'conversion efficiency', 'dc efficiency',
                # Vendor signals (key DC rectifier vendors)
                'eltek', 'delta electronics rectifier', 'huawei digital power',
                'abb power', 'emerson network power', 'zte power'
            ],
            'max_points': 35,  # High priority - new ICP vertical (DC power infrastructure)
            'description': 'DC rectifier/power infrastructure - TARGET ICP'
        }
    }

    # Business fit configuration - GPU/Neocloud is TARGET ICP
    INDUSTRY_FIT = {
        # TARGET ICP: GPU-focused neocloud providers
        'gpu cloud': {'score': 100, 'label': 'GPU Cloud (Target ICP)'},
        'neocloud': {'score': 100, 'label': 'Neocloud (Target ICP)'},
        'ai infrastructure': {'score': 100, 'label': 'AI Infrastructure (Target ICP)'},
        'ai-focused': {'score': 100, 'label': 'AI/ML Infrastructure (Target ICP)'},

        # High-value traditional datacenters
        'cloud': {'score': 90, 'label': 'Cloud Provider'},
        'colocation': {'score': 90, 'label': 'Colocation Provider'},
        'hyperscaler': {'score': 85, 'label': 'Hyperscaler'},
        'data center': {'score': 85, 'label': 'Data Center'},

        # Lower priority
        'energy-intensive': {'score': 60, 'label': 'Energy-Intensive Industry'},
        'enterprise': {'score': 45, 'label': 'Enterprise'},
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_account_score(self, account_data: Dict[str, Any]) -> AccountScore:
        """
        Calculate comprehensive account score with full traceability.

        Args:
            account_data: Dictionary containing account information including:
                - Physical Infrastructure: String of detected infrastructure
                - business_model: Company type (cloud, colocation, etc.)
                - data_center_locations: List of locations
                - growth_indicators: List of expansion/hiring signals
                - trigger_events: List of trigger event dicts

        Returns:
            AccountScore with total_score and detailed breakdowns
        """
        # Calculate each dimension
        infrastructure = self._score_infrastructure(account_data)
        business_fit = self._score_business_fit(account_data)
        buying_signals = self._score_buying_signals(account_data)

        # Weighted total (35% + 35% + 30% = 100%)
        total = (
            infrastructure.score * 0.35 +
            business_fit.score * 0.35 +
            buying_signals.score * 0.30
        )

        # Determine priority level
        if total >= 80:
            priority = "Very High"
        elif total >= 65:
            priority = "High"
        elif total >= 50:
            priority = "Medium"
        else:
            priority = "Low"

        return AccountScore(
            total_score=min(total, 100),
            infrastructure_fit=infrastructure,
            business_fit=business_fit,
            buying_signals=buying_signals,
            priority_level=priority
        )

    def _score_infrastructure(self, account_data: Dict[str, Any]) -> InfrastructureBreakdown:
        """
        Score infrastructure with full keyword traceability.
        Returns exact keywords detected for dashboard display.
        """
        # Get infrastructure text from account data
        raw_text = account_data.get('Physical Infrastructure', '') or \
                   account_data.get('physical_infrastructure', '') or \
                   account_data.get('current_tech_stack', '') or ''

        if not raw_text:
            return InfrastructureBreakdown(
                score=0.0,
                breakdown={
                    cat: {'detected': [], 'points': 0, 'max_points': config['max_points']}
                    for cat, config in self.INFRASTRUCTURE_KEYWORDS.items()
                },
                raw_text=''
            )

        text_lower = raw_text.lower()
        breakdown = {}
        total_points = 0
        max_possible = 0

        for category, config in self.INFRASTRUCTURE_KEYWORDS.items():
            detected = [kw for kw in config['keywords'] if kw.lower() in text_lower]
            points = config['max_points'] if detected else 0
            total_points += points
            max_possible += config['max_points']

            breakdown[category] = {
                'detected': detected,
                'points': points,
                'max_points': config['max_points'],
                'description': config['description']
            }

        # Calculate normalized score (0-100)
        score = (total_points / max_possible) * 100 if max_possible > 0 else 0

        return InfrastructureBreakdown(
            score=min(100, score),
            breakdown=breakdown,
            raw_text=raw_text
        )

    def _score_business_fit(self, account_data: Dict[str, Any]) -> BusinessFitBreakdown:
        """Score business fit based on industry, size, and geography."""

        # Industry fit
        business_model = account_data.get('business_model', '').lower()
        industry_match = None
        industry_score = 30  # Default for unknown

        for industry, config in self.INDUSTRY_FIT.items():
            if industry in business_model:
                industry_match = config['label']
                industry_score = config['score']
                break

        industry_fit = {
            'detected': industry_match or 'Unknown',
            'score': industry_score,
            'business_model': account_data.get('business_model', 'Unknown')
        }

        # Company size fit (larger = more power monitoring opportunity)
        employee_count = account_data.get('employee_count', 0) or 0
        if employee_count > 5000:
            size_score = 100
            size_label = 'Enterprise'
        elif employee_count > 1000:
            size_score = 85
            size_label = 'Large'
        elif employee_count > 200:
            size_score = 70
            size_label = 'Mid-Market'
        elif employee_count > 50:
            size_score = 50
            size_label = 'Growth'
        else:
            size_score = 30
            size_label = 'Startup'

        company_size_fit = {
            'employee_count': employee_count,
            'size_category': size_label,
            'score': size_score
        }

        # Geographic fit (US market preference)
        locations = account_data.get('data_center_locations', [])
        if isinstance(locations, str):
            locations = [locations]

        us_indicators = ['us', 'usa', 'united states', 'california', 'texas',
                        'virginia', 'new york', 'oregon', 'washington', 'arizona']
        us_locations = [loc for loc in locations
                       if any(ind in loc.lower() for ind in us_indicators)]

        if us_locations:
            geo_score = 100
            geo_priority = 'US Primary'
        elif locations:
            geo_score = 50
            geo_priority = 'International'
        else:
            geo_score = 60
            geo_priority = 'Unknown'

        geographic_fit = {
            'us_locations': us_locations,
            'all_locations': locations,
            'priority': geo_priority,
            'score': geo_score
        }

        # Weighted business fit score
        total_score = (industry_score * 0.5 + size_score * 0.25 + geo_score * 0.25)

        return BusinessFitBreakdown(
            score=total_score,
            industry_fit=industry_fit,
            company_size_fit=company_size_fit,
            geographic_fit=geographic_fit
        )

    def _score_buying_signals(self, account_data: Dict[str, Any]) -> BuyingSignalsBreakdown:
        """Score buying signals from trigger events and growth indicators."""

        # Trigger events
        trigger_events = account_data.get('trigger_events', [])
        if isinstance(trigger_events, str):
            trigger_events = [trigger_events]

        high_value_triggers = []
        trigger_score = 0

        for event in trigger_events:
            if isinstance(event, dict):
                relevance = event.get('relevance_score', 0)
                event_type = event.get('event_type', 'Unknown')
            else:
                relevance = 50
                event_type = str(event)

            if relevance >= 80:
                high_value_triggers.append(event_type)
                trigger_score += 25
            elif relevance >= 60:
                trigger_score += 15

        trigger_score = min(trigger_score, 100)

        trigger_breakdown = {
            'high_value_triggers': high_value_triggers[:3],  # Top 3
            'total_triggers': len(trigger_events),
            'score': trigger_score
        }

        # Expansion signals
        growth_indicators = account_data.get('growth_indicators', [])
        if isinstance(growth_indicators, str):
            growth_indicators = [growth_indicators]

        expansion_keywords = ['expansion', 'new data center', 'building', 'capacity',
                            'new facility', 'growth', 'scale', 'expand']
        expansion_matches = [ind for ind in growth_indicators
                           if any(kw in ind.lower() for kw in expansion_keywords)]

        expansion_score = min(len(expansion_matches) * 30, 100)
        expansion_breakdown = {
            'detected': expansion_matches[:3],
            'score': expansion_score
        }

        # Hiring signals
        hiring_keywords = ['hiring', 'recruiting', 'new role', 'open position',
                         'facilities', 'data center', 'infrastructure']
        hiring_matches = [ind for ind in growth_indicators
                        if any(kw in ind.lower() for kw in hiring_keywords)]

        hiring_score = min(len(hiring_matches) * 25, 100)
        hiring_breakdown = {
            'detected': hiring_matches[:3],
            'score': hiring_score
        }

        # Weighted buying signals score
        total_score = (trigger_score * 0.5 + expansion_score * 0.3 + hiring_score * 0.2)

        return BuyingSignalsBreakdown(
            score=total_score,
            trigger_events=trigger_breakdown,
            expansion_signals=expansion_breakdown,
            hiring_signals=hiring_breakdown
        )


# Export singleton instance
account_scorer = AccountScorer()


# ============================================================================
# MEDDIC CONTACT SCORER - Champion Potential Based Scoring
# ============================================================================

@dataclass
class MEDDICContactScore:
    """MEDDIC-style contact score with champion potential focus"""
    total_score: float  # 0-100
    champion_potential_score: float  # 0-100 (45% weight)
    role_fit_score: float  # 0-100 (30% weight)
    engagement_potential_score: float  # 0-100 (25% weight)

    # Classification
    role_tier: str  # "entry_point", "middle_decider", "economic_buyer"
    role_classification: str  # Specific role name
    champion_potential_level: str  # "Very High", "High", "Medium", "Low"

    # For dashboard display
    why_prioritize: List[str]  # List of reasons to prioritize this contact
    recommended_approach: str  # Outreach recommendation

    def get_score_breakdown(self) -> Dict[str, Any]:
        return {
            'total_score': round(self.total_score, 1),
            'champion_potential': {
                'score': round(self.champion_potential_score, 1),
                'weight': '45%',
                'level': self.champion_potential_level
            },
            'role_fit': {
                'score': round(self.role_fit_score, 1),
                'weight': '30%',
                'tier': self.role_tier,
                'classification': self.role_classification
            },
            'engagement_potential': {
                'score': round(self.engagement_potential_score, 1),
                'weight': '25%'
            },
            'why_prioritize': self.why_prioritize,
            'recommended_approach': self.recommended_approach
        }


class MEDDICContactScorer:
    """
    MEDDIC-style contact scoring that prioritizes Entry Point roles (Technical Believers)
    who feel the pain and become champions.

    This INVERTS traditional lead scoring that would prioritize VPs/CIOs first.

    Scoring Dimensions:
    - Champion Potential (45%): Entry point roles who feel pain, own data
    - Role Fit (30%): Buying committee position (Entry → Middle → Top)
    - Engagement Potential (25%): LinkedIn activity, content relevance

    Role Tiers (from your MEDDIC diagrams):
    - Entry Point (HIGHEST): Technical Believers who feel the pain
    - Middle: Tooling & Ops Deciders who make tooling decisions
    - Top (for later engagement): Economic Buyers who approve budget
    """

    # MEDDIC Role Classification based on user's diagrams
    # TARGET ICP: Neocloud/GPU datacenter - pain points reflect high-power GPU workloads
    ROLE_TIERS = {
        'entry_point': {
            'score': 95,  # Highest priority for initial outreach
            'champion_potential': 'very_high',
            'roles': [
                'Capacity & Energy Engineer',
                'Critical Facilities Engineers',
                'SRE/Infrastructure Engineers',
                'Facilities Manager',
                'NOC & Operations Team',
            ],
            'pain_indicators': [
                # GPU/Neocloud-specific pain points
                'gpu instability', 'gpu thermal', 'gpu power', 'cluster power',
                'ai workload', 'training cluster', 'inference', 'nvidia', 'h100', 'a100',
                # Traditional datacenter pain points
                'overloads', 'alarms', 'pue', 'forecasting', 'thermal events',
                'power visibility', 'monitoring', 'reliability', 'capacity',
                'cooling', 'power density', 'rack power'
            ],
            'engagement_approach': 'Pain-based outreach: Focus on GPU power/thermal challenges'
        },
        'middle_decider': {
            'score': 80,
            'champion_potential': 'high',
            'roles': [
                'Monitoring/DCIM Product Owner',
                'Director, Data Center Facilities',
                'Director, Data Center Operations',
                'Director, Cloud Platform & SRE',
                'Director, Infrastructure Engineering',
                'SRE Manager',
            ],
            'decision_indicators': [
                'tooling', 'evaluation', 'integration', 'monitoring stack',
                'vendor', 'implementation', 'solution'
            ],
            'engagement_approach': 'Solution-focused: How we integrate with their stack'
        },
        'economic_buyer': {
            'score': 65,  # Lower for initial outreach - engage via champion
            'champion_potential': 'low',
            'roles': [
                'VP, Infrastructure & Data Centers',
                'VP of Operations',
                'CIO',
                'CTO',
                'Finance/FP&A',
            ],
            'engagement_approach': 'Via champion referral - business case focused'
        }
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_contact_score(self, contact: Dict, account_data: Dict = None) -> MEDDICContactScore:
        """
        Calculate MEDDIC-style contact score prioritizing champion potential.

        Args:
            contact: Contact data with title, bio, linkedin_activity, etc.
            account_data: Account context (optional)

        Returns:
            MEDDICContactScore with full breakdown
        """
        account_data = account_data or {}
        title = contact.get('title', '')

        # Classify role
        role_tier, role_classification = self._classify_role(title)

        # Calculate component scores
        champion_score = self._score_champion_potential(contact, role_tier)
        role_score = self._score_role_fit(role_tier)
        engagement_score = self._score_engagement_potential(contact)

        # Weighted total (45% + 30% + 25% = 100%)
        total = (
            champion_score * 0.45 +
            role_score * 0.30 +
            engagement_score * 0.25
        )

        # Determine champion potential level
        if champion_score >= 85:
            champion_level = "Very High"
        elif champion_score >= 70:
            champion_level = "High"
        elif champion_score >= 50:
            champion_level = "Medium"
        else:
            champion_level = "Low"

        # Generate "Why prioritize" reasons
        why_prioritize = self._generate_prioritization_reasons(
            contact, role_tier, role_classification, champion_score
        )

        # Get recommended approach
        tier_config = self.ROLE_TIERS.get(role_tier, self.ROLE_TIERS['entry_point'])
        recommended_approach = tier_config.get('engagement_approach', 'Standard outreach')

        return MEDDICContactScore(
            total_score=min(total, 100),
            champion_potential_score=champion_score,
            role_fit_score=role_score,
            engagement_potential_score=engagement_score,
            role_tier=role_tier,
            role_classification=role_classification,
            champion_potential_level=champion_level,
            why_prioritize=why_prioritize,
            recommended_approach=recommended_approach
        )

    def _classify_role(self, title: str) -> Tuple[str, str]:
        """
        Classify contact into MEDDIC role tier and specific role.

        IMPORTANT: Check seniority level FIRST to avoid false matches.
        Keywords like 'infrastructure' appear in multiple tiers, so we need
        to check VP/Director/CIO prefixes before general keyword matching.
        """
        import re
        title_lower = title.lower()

        # Helper: Check if word appears as whole word (not substring)
        def has_word(text: str, word: str) -> bool:
            return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

        # STEP 1: Check seniority level FIRST (prevents false matches)
        # VP, Chief, and C-Suite are ALWAYS economic buyers
        # Use word boundaries to avoid "coo" matching in "operations"
        c_suite_titles = ['cio', 'cto', 'cfo', 'coo', 'chief information officer',
                         'chief technology officer', 'chief operating officer']
        if any(has_word(title_lower, term) for term in c_suite_titles):
            return 'economic_buyer', 'C-Suite Executive'

        if any(term in title_lower for term in ['vp', 'vice president']):
            # VP roles are economic buyers (budget authority)
            if any(term in title_lower for term in ['infrastructure', 'data center', 'operations']):
                return 'economic_buyer', 'VP, Infrastructure & Data Centers'
            return 'economic_buyer', 'VP of Operations'

        # Director level = middle deciders (tooling decisions)
        if 'director' in title_lower:
            if any(term in title_lower for term in ['infrastructure', 'engineering']):
                return 'middle_decider', 'Director, Infrastructure Engineering'
            elif any(term in title_lower for term in ['data center', 'datacenter']) and 'operations' in title_lower:
                return 'middle_decider', 'Director, Data Center Operations'
            elif 'facilities' in title_lower:
                return 'middle_decider', 'Director, Data Center Facilities'
            elif any(term in title_lower for term in ['cloud', 'sre', 'platform']):
                return 'middle_decider', 'Director, Cloud Platform & SRE'
            return 'middle_decider', 'Director'

        # STEP 2: Check middle-decider specific roles FIRST
        # (More specific patterns like "SRE Manager" before generic "SRE")
        middle_indicators = [
            ('sre manager', 'SRE Manager'),
            ('reliability manager', 'SRE Manager'),
            ('dcim', 'Monitoring/DCIM Product Owner'),
            ('monitoring manager', 'Monitoring/DCIM Product Owner'),
            ('product owner', 'Monitoring/DCIM Product Owner'),
        ]

        for indicator, role_name in middle_indicators:
            if indicator in title_lower:
                return 'middle_decider', role_name

        # STEP 3: Check entry-point roles (Technical Believers)
        entry_point_indicators = [
            ('capacity', 'Capacity & Energy Engineer'),
            ('energy engineer', 'Capacity & Energy Engineer'),
            ('critical facilities', 'Critical Facilities Engineers'),
            ('facilities engineer', 'Critical Facilities Engineers'),
            ('sre', 'SRE/Infrastructure Engineers'),
            ('site reliability', 'SRE/Infrastructure Engineers'),
            ('infrastructure engineer', 'SRE/Infrastructure Engineers'),
            ('facilities manager', 'Facilities Manager'),
            ('noc', 'NOC & Operations Team'),
            ('operations analyst', 'NOC & Operations Team'),
        ]

        for indicator, role_name in entry_point_indicators:
            if indicator in title_lower:
                return 'entry_point', role_name

        # STEP 4: General fallback based on common title patterns
        if 'manager' in title_lower:
            if 'facilities' in title_lower:
                return 'entry_point', 'Facilities Manager'
            return 'middle_decider', 'Manager'

        if 'engineer' in title_lower:
            return 'entry_point', 'Technical Staff'

        if 'analyst' in title_lower:
            return 'entry_point', 'Technical Staff'

        return 'entry_point', 'Unknown'

    def _score_champion_potential(self, contact: Dict, role_tier: str) -> float:
        """
        Score champion potential based on role tier and pain indicators.
        Entry points who feel pain are best champions.
        """
        tier_config = self.ROLE_TIERS.get(role_tier, {})
        base_score = 50.0

        # Base score by tier
        if role_tier == 'entry_point':
            base_score = 85.0  # High base - they feel the pain
        elif role_tier == 'middle_decider':
            base_score = 65.0  # Medium - they make decisions
        else:  # economic_buyer
            base_score = 30.0  # Low - they approve, not champion

        # Bonus for pain indicators in bio/activity
        bio = (contact.get('bio', '') or contact.get('summary', '') or '').lower()
        pain_keywords = tier_config.get('pain_indicators', [])
        pain_matches = sum(1 for kw in pain_keywords if kw in bio)
        base_score += min(pain_matches * 3, 15)  # Up to +15 bonus

        # Bonus for ownership indicators
        ownership_keywords = ['owns', 'responsible for', 'manages', 'leads', 'oversees']
        if any(kw in bio for kw in ownership_keywords):
            base_score += 10

        return min(100, base_score)

    def _score_role_fit(self, role_tier: str) -> float:
        """Score based on role tier position in buying committee."""
        tier_config = self.ROLE_TIERS.get(role_tier, {})
        return tier_config.get('score', 50.0)

    def _score_engagement_potential(self, contact: Dict) -> float:
        """Score engagement potential based on LinkedIn activity."""
        score = 30.0  # Base

        # LinkedIn activity
        activity_level = contact.get('linkedin_activity_level', '').lower()
        if 'high' in activity_level:
            score += 30
        elif 'medium' in activity_level:
            score += 20
        elif 'low' in activity_level:
            score += 10

        # Content relevance
        content_themes = contact.get('content_themes', [])
        relevant_topics = ['data center', 'power', 'energy', 'infrastructure',
                         'monitoring', 'efficiency', 'sustainability']

        relevant_matches = sum(1 for theme in content_themes
                              if any(topic in theme.lower() for topic in relevant_topics))
        score += min(relevant_matches * 10, 30)

        # Network quality
        if contact.get('network_quality'):
            score += 10

        return min(100, score)

    def _generate_prioritization_reasons(self, contact: Dict, role_tier: str,
                                        role_classification: str, champion_score: float) -> List[str]:
        """Generate human-readable reasons for prioritizing this contact."""
        reasons = []

        if role_tier == 'entry_point':
            reasons.append(f"Entry Point role: {role_classification} - feels the pain daily")
            reasons.append("Can become internal champion who sells Verdigris up the chain")
            reasons.append("Has visibility into power/thermal events and infrastructure issues")
        elif role_tier == 'middle_decider':
            reasons.append(f"Tooling Decider: {role_classification} - makes integration decisions")
            reasons.append("Can validate need and drive tooling selection")
        else:
            reasons.append(f"Economic Buyer: {role_classification} - budget authority")
            reasons.append("Engage via champion referral with business case")

        # Add champion-specific reasons
        if champion_score >= 85:
            reasons.append("Very high champion potential - prioritize for first outreach")
        elif champion_score >= 70:
            reasons.append("Strong champion potential - good initial target")

        # Add bio-based reasons
        bio = (contact.get('bio', '') or '').lower()
        if 'monitoring' in bio or 'visibility' in bio:
            reasons.append("Bio mentions monitoring/visibility - direct pain point alignment")
        if 'infrastructure' in bio or 'data center' in bio:
            reasons.append("Bio mentions infrastructure - relevant domain expertise")

        return reasons[:4]  # Limit to 4 reasons


# Export singleton instance
meddic_contact_scorer = MEDDICContactScorer()


class UnifiedLeadScorer:
    """
    Unified Lead Scoring Engine that consolidates all previous implementations:
    - Basic lead scoring (ICP fit, buying power, engagement)
    - Organizational hierarchy and decision influence mapping
    - Geographic scoring for US market preference
    - AI-powered personalized recommendations
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._load_default_config()

        # Initialize OpenAI for AI recommendations
        try:
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            self.logger.warning(f"OpenAI client initialization failed: {e}")
            self.openai_client = None

        # Load decision influence mapping
        self.decision_influence_map = self._load_decision_influence_map()

        # Load US geographic indicators
        self.us_indicators = self._load_us_indicators()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default scoring configuration"""
        return {
            'scoring_formula': {
                'component_weights': {
                    'icp_fit_weight': 0.30,
                    'buying_power_weight': 0.25,
                    'engagement_weight': 0.20,
                    'geographic_weight': 0.15,
                    'organizational_influence_weight': 0.10
                }
            },
            'scoring_thresholds': {
                'high_priority': {'min_score': 70.0},
                'medium_priority': {'min_score': 50.0}
            },
            'icp_fit_scoring': {
                'components': {
                    'title_match': {
                        'scoring': {
                            'VP_or_Head_level': 90,
                            'Director_level': 75,
                            'Senior_Manager': 60,
                            'Manager': 45,
                            'Other': 30
                        }
                    },
                    'responsibility_keywords': {
                        'max_bonus': 20,
                        'keywords': {
                            'infrastructure': {'terms': ['infrastructure', 'data center', 'datacenter'], 'points': 8},
                            'power_energy': {'terms': ['power', 'energy', 'efficiency'], 'points': 10},
                            'monitoring': {'terms': ['monitoring', 'analytics', 'observability'], 'points': 7},
                            'operations': {'terms': ['operations', 'ops', 'reliability'], 'points': 6}
                        }
                    }
                }
            },
            'engagement_potential_scoring': {
                'components': {
                    'linkedin_activity': {
                        'scoring': {
                            'high_activity': 30,
                            'medium_activity': 20,
                            'low_activity': 10,
                            'minimal_activity': 5
                        }
                    },
                    'content_relevance': {
                        'high_relevance_topics': ['data center', 'power monitoring', 'energy efficiency', 'infrastructure'],
                        'scoring': {
                            'high_relevance': 25,
                            'medium_relevance': 15,
                            'low_relevance': 5
                        }
                    },
                    'network_quality': {'score': 15}
                }
            }
        }

    def _load_decision_influence_map(self) -> Dict[str, DecisionInfluence]:
        """Map roles to decision influence based on organizational charts"""
        return {
            # TOP TIER - Economic Buyers (Budget Authority + Strategic Alignment)
            'CIO': DecisionInfluence(1.0, 0.7, 0.9, 0.4),
            'CTO': DecisionInfluence(1.0, 0.8, 0.9, 0.4),
            'VP, Infrastructure & Data Centers': DecisionInfluence(0.9, 0.9, 0.9, 0.6),
            'VP of Operations': DecisionInfluence(0.9, 0.8, 0.9, 0.6),
            'Finance/FP&A': DecisionInfluence(0.8, 0.3, 0.6, 0.2),

            # MIDDLE TIER - Decision Makers & Business Case Builders
            'Director, Infrastructure Engineering': DecisionInfluence(0.7, 0.9, 0.8, 0.7),
            'Director, Data Center Operations': DecisionInfluence(0.7, 0.9, 0.8, 0.7),
            'Director, Data Center Facilities': DecisionInfluence(0.7, 0.8, 0.8, 0.7),
            'Director, Cloud Platform & SRE': DecisionInfluence(0.6, 0.8, 0.8, 0.6),
            'Monitoring/DCIM Product Owner': DecisionInfluence(0.5, 0.9, 0.8, 0.8),

            # OPERATIONAL TIER - Technical Evaluators & Champions
            'SRE Manager': DecisionInfluence(0.4, 0.8, 0.7, 0.8),
            'Facilities Manager': DecisionInfluence(0.4, 0.9, 0.6, 0.7),
            'NOC & Operations Team': DecisionInfluence(0.3, 0.8, 0.6, 0.8),
            'Capacity & Energy Engineer': DecisionInfluence(0.3, 0.9, 0.7, 0.9),
            'Critical Facilities Engineers': DecisionInfluence(0.3, 0.9, 0.7, 0.9),
            'SRE/Infrastructure Engineers': DecisionInfluence(0.3, 0.8, 0.8, 0.9),

            # DEFAULT for unmapped roles
            'Unknown': DecisionInfluence(0.2, 0.5, 0.5, 0.5)
        }

    def _load_us_indicators(self) -> List[str]:
        """Load US geographic indicators for market fit scoring"""
        return [
            # States
            'california', 'texas', 'new york', 'florida', 'illinois', 'pennsylvania',
            'ohio', 'georgia', 'north carolina', 'michigan', 'virginia', 'washington',
            'arizona', 'massachusetts', 'tennessee', 'indiana', 'missouri', 'maryland',
            'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama', 'louisiana',
            'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah', 'iowa', 'nevada',
            'arkansas', 'mississippi', 'kansas', 'new mexico', 'nebraska', 'west virginia',
            'idaho', 'hawaii', 'new hampshire', 'maine', 'montana', 'rhode island',
            'delaware', 'south dakota', 'north dakota', 'alaska', 'vermont', 'wyoming',

            # Major cities
            'new york city', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
            'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis',
            'seattle', 'denver', 'boston', 'atlanta', 'miami', 'las vegas',

            # Common abbreviations
            'ny', 'ca', 'tx', 'fl', 'il', 'pa', 'oh', 'ga', 'nc', 'mi', 'va', 'wa',
            'az', 'ma', 'tn', 'in', 'mo', 'md', 'wi', 'co', 'mn', 'sc', 'al', 'la',

            # Other indicators
            'usa', 'united states', 'americas', 'north america'
        ]

    def calculate_comprehensive_lead_score(self, contact: Dict, account_data: Dict = None) -> LeadScore:
        """
        Calculate comprehensive lead score incorporating all scoring dimensions

        Args:
            contact: Contact data dictionary
            account_data: Account data for context (optional)

        Returns:
            LeadScore object with full breakdown
        """
        account_data = account_data or {}

        # Calculate component scores
        icp_fit = self._score_icp_fit(contact)
        buying_power = self._score_buying_power(contact.get('title', ''))
        engagement = self._score_engagement_potential(contact)
        geographic_fit, geographic_priority = self._score_geographic_fit(account_data)

        # Calculate organizational influence
        role_classification = self._normalize_role(contact.get('title', ''))
        influence = self.decision_influence_map.get(role_classification, self.decision_influence_map['Unknown'])
        organizational_score = self._calculate_organizational_influence_score(influence)

        # Calculate weighted final score
        weights = self.config['scoring_formula']['component_weights']
        final_score = (
            icp_fit * weights['icp_fit_weight'] +
            buying_power * weights['buying_power_weight'] +
            engagement * weights['engagement_weight'] +
            geographic_fit * weights['geographic_weight'] +
            organizational_score * weights['organizational_influence_weight']
        )

        # Determine priority level
        if final_score >= ScoreThreshold.HIGH_PRIORITY.value:
            priority_level = "High Priority"
        elif final_score >= ScoreThreshold.MEDIUM_PRIORITY.value:
            priority_level = "Medium Priority"
        else:
            priority_level = "Low Priority"

        return LeadScore(
            icp_fit_score=icp_fit,
            buying_power_score=buying_power,
            engagement_potential_score=engagement,
            geographic_fit_score=geographic_fit,
            organizational_influence_score=organizational_score,
            final_score=min(final_score, 100.0),
            role_classification=role_classification,
            geographic_priority=geographic_priority,
            priority_level=priority_level
        )

    def _score_icp_fit(self, contact: Dict) -> float:
        """Calculate ICP fit score based on title and responsibilities"""
        score = 0.0
        title = contact.get('title', '').lower()
        bio = contact.get('bio', '') or contact.get('summary', '') or ''

        # Title match scoring
        title_scores = self.config['icp_fit_scoring']['components']['title_match']['scoring']
        if any(level in title for level in ['vp', 'vice president', 'head']):
            score = title_scores['VP_or_Head_level']
        elif 'director' in title:
            score = title_scores['Director_level']
        elif 'senior manager' in title:
            score = title_scores['Senior_Manager']
        elif 'manager' in title:
            score = title_scores['Manager']
        else:
            score = title_scores['Other']

        # Responsibility keyword bonuses
        if bio:
            keywords = self.config['icp_fit_scoring']['components']['responsibility_keywords']['keywords']
            bio_lower = bio.lower()

            bonus = 0
            for category, config in keywords.items():
                for term in config['terms']:
                    if term.lower() in bio_lower:
                        bonus += config['points']
                        break  # Only add points once per category

            max_bonus = self.config['icp_fit_scoring']['components']['responsibility_keywords']['max_bonus']
            score += min(bonus, max_bonus)

        return max(0, min(100, score))

    def _score_buying_power(self, title: str) -> float:
        """Calculate buying power score based on title hierarchy"""
        title_lower = title.lower()

        if any(level in title_lower for level in ['vp', 'vice president', 'head', 'chief']):
            return 100.0
        elif 'director' in title_lower:
            return 70.0
        elif any(level in title_lower for level in ['manager', 'lead']):
            return 50.0
        else:
            return 30.0

    def _score_engagement_potential(self, contact: Dict) -> float:
        """Calculate engagement potential score"""
        score = 0.0

        # LinkedIn activity
        activity_level = contact.get('linkedin_activity_level', 'low_activity').lower()
        activity_config = self.config['engagement_potential_scoring']['components']['linkedin_activity']['scoring']
        score += activity_config.get(activity_level, activity_config['low_activity'])

        # Content relevance
        content_themes = contact.get('content_themes', [])
        high_relevance_topics = self.config['engagement_potential_scoring']['components']['content_relevance']['high_relevance_topics']
        relevant_themes = [theme for theme in content_themes
                          if any(topic in theme.lower() for topic in high_relevance_topics)]

        content_scores = self.config['engagement_potential_scoring']['components']['content_relevance']['scoring']
        if len(relevant_themes) >= 3:
            score += content_scores['high_relevance']
        elif len(relevant_themes) >= 1:
            score += content_scores['medium_relevance']
        else:
            score += content_scores['low_relevance']

        # Network quality
        if contact.get('network_quality', False):
            score += self.config['engagement_potential_scoring']['components']['network_quality']['score']

        return min(score, 100)

    def _score_geographic_fit(self, account_data: Dict) -> Tuple[float, GeographicPriority]:
        """
        Comprehensive geographic fit scoring based on US market presence
        Enhanced version with sophisticated pattern matching and multi-source analysis
        """
        import re

        score = 50  # neutral baseline
        priority = GeographicPriority.INTERNATIONAL_ONLY
        red_flags = []
        us_presence = False

        # Check data center locations with improved matching
        data_center_locations = account_data.get('data_center_locations', [])
        if isinstance(data_center_locations, str):
            data_center_locations = [data_center_locations]

        us_data_centers = []
        international_data_centers = []

        for location in data_center_locations:
            if not location:
                continue

            location_lower = location.lower().strip()
            is_us_location = False

            # Check for exact matches or word boundaries for US indicators
            for us_indicator in self.us_indicators:
                # For short abbreviations (2-3 chars), require word boundaries
                if len(us_indicator) <= 3:
                    pattern = r'\b' + re.escape(us_indicator) + r'\b'
                    if re.search(pattern, location_lower):
                        is_us_location = True
                        break
                else:
                    # For longer names, allow substring matching but be more careful
                    if us_indicator in location_lower:
                        # Additional check: make sure it's not a false positive
                        # Skip if it's clearly an international location
                        international_keywords = [
                            'iceland', 'sweden', 'norway', 'denmark', 'finland',
                            'germany', 'france', 'uk', 'united kingdom', 'canada',
                            'australia', 'japan', 'singapore', 'ireland'
                        ]
                        if not any(intl in location_lower for intl in international_keywords):
                            is_us_location = True
                            break

            if is_us_location:
                us_data_centers.append(location)
                us_presence = True
            else:
                international_data_centers.append(location)

        # Primary scoring logic based on data centers
        if us_data_centers:
            if len(us_data_centers) >= len(international_data_centers):
                # US-primary company
                score = 100
                priority = GeographicPriority.US_PRIMARY
            else:
                # International with US presence
                score = 75
                priority = GeographicPriority.INTERNATIONAL_WITH_US
        else:
            # No US data centers detected
            if international_data_centers:
                score = 25
                priority = GeographicPriority.INTERNATIONAL_ONLY
                red_flags.append(f"No US data center presence detected. Locations: {', '.join(international_data_centers[:3])}")
            else:
                score = 40
                priority = GeographicPriority.INTERNATIONAL_ONLY
                red_flags.append("No clear geographic data center information available")

        # Check employee/office locations if provided
        employee_locations = account_data.get('employee_locations', [])
        if isinstance(employee_locations, str):
            employee_locations = [employee_locations]

        if employee_locations:
            us_employees = [loc for loc in employee_locations
                          if any(us_indicator in loc.lower() for us_indicator in self.us_indicators)]
            if us_employees:
                us_presence = True
                if not us_data_centers:
                    score += 15  # Boost for US employees even without US data centers
            elif not us_data_centers:
                red_flags.append(f"No US employee presence detected. Employee locations: {', '.join(employee_locations[:3])}")

        # Check company description for US market focus
        company_description = account_data.get('company_description', '')
        if company_description:
            desc_lower = company_description.lower()
            if any(us_indicator in desc_lower for us_indicator in self.us_indicators):
                us_presence = True
                if score < 50:
                    score += 10  # Small boost for US market mentions

        # Final adjustments
        if not us_presence:
            red_flags.append("⚠️ RED FLAG: No US market presence detected - may not align with Verdigris go-to-market focus")

        # Store red flags for potential future use (accessible via _last_geographic_red_flags)
        self._last_geographic_red_flags = red_flags

        return min(100, max(0, score)), priority

    def _calculate_organizational_influence_score(self, influence: DecisionInfluence) -> float:
        """Calculate organizational influence score based on decision factors"""
        return (
            influence.entry_point_value * 0.4 +     # PRIMARY: Best place to start?
            influence.pain_ownership * 0.3 +        # Do they feel the pain?
            influence.champion_ability * 0.2 +      # Can they sell internally?
            influence.budget_authority * 0.1        # SECONDARY: Can they approve?
        ) * 100  # Scale to 0-100

    def _normalize_role(self, title: str) -> str:
        """Normalize job titles to standard role classifications"""
        title_lower = title.lower()

        # C-Suite
        if any(term in title_lower for term in ['cio', 'cto', 'chief information', 'chief technology']):
            return 'CIO' if 'cio' in title_lower or 'information' in title_lower else 'CTO'

        # VP Level
        if 'vp' in title_lower or 'vice president' in title_lower:
            if any(term in title_lower for term in ['infrastructure', 'data center']):
                return 'VP, Infrastructure & Data Centers'
            elif 'operations' in title_lower:
                return 'VP of Operations'

        # Director Level
        if 'director' in title_lower:
            if any(term in title_lower for term in ['infrastructure', 'engineering']):
                return 'Director, Infrastructure Engineering'
            elif any(term in title_lower for term in ['data center', 'datacenter']) and 'operations' in title_lower:
                return 'Director, Data Center Operations'
            elif 'facilities' in title_lower:
                return 'Director, Data Center Facilities'
            elif any(term in title_lower for term in ['cloud', 'sre', 'platform']):
                return 'Director, Cloud Platform & SRE'

        # Manager Level
        if 'manager' in title_lower:
            if 'sre' in title_lower or 'reliability' in title_lower:
                return 'SRE Manager'
            elif 'facilities' in title_lower:
                return 'Facilities Manager'

        # Engineer Level
        if any(term in title_lower for term in ['engineer', 'engineering']):
            if any(term in title_lower for term in ['capacity', 'energy']):
                return 'Capacity & Energy Engineer'
            elif any(term in title_lower for term in ['facilities', 'critical']):
                return 'Critical Facilities Engineers'
            elif any(term in title_lower for term in ['sre', 'infrastructure', 'reliability']):
                return 'SRE/Infrastructure Engineers'

        # Product/Program roles
        if any(term in title_lower for term in ['product', 'program']) and any(term in title_lower for term in ['monitoring', 'dcim']):
            return 'Monitoring/DCIM Product Owner'

        # Operations
        if any(term in title_lower for term in ['noc', 'operations', 'ops']) and not any(term in title_lower for term in ['director', 'manager', 'vp']):
            return 'NOC & Operations Team'

        # Finance
        if any(term in title_lower for term in ['finance', 'fp&a', 'financial']):
            return 'Finance/FP&A'

        return 'Unknown'

    def calculate_lead_score(self, contact: Dict, account_data: Dict = None) -> float:
        """
        Simplified interface for backward compatibility
        Returns just the final score as float
        """
        try:
            lead_score_obj = self.calculate_comprehensive_lead_score(contact, account_data)
            return lead_score_obj.final_score
        except Exception as e:
            self.logger.error(f"Lead scoring failed for {contact.get('name', 'unknown')}: {e}")
            # Basic fallback score
            role = self._normalize_role(contact.get('title', ''))
            influence = self.decision_influence_map.get(role, self.decision_influence_map['Unknown'])
            return min(influence.entry_point_value * 80, 100)

    def should_enrich_contact(self, lead_score: float, threshold: float = None) -> bool:
        """Determine if contact should proceed to enrichment"""
        threshold = threshold or self.config['scoring_thresholds']['high_priority']['min_score']
        return lead_score >= threshold


# Export singleton instance for easy importing
unified_lead_scorer = UnifiedLeadScorer()