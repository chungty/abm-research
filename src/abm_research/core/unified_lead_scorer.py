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