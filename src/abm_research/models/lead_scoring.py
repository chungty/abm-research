"""
Lead Scoring models and utilities for ABM Research System
"""
from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ScoreThreshold(Enum):
    HIGH_PRIORITY = 70.0
    MEDIUM_PRIORITY = 50.0
    LOW_PRIORITY = 0.0


@dataclass
class LeadScore:
    """Represents a calculated lead score with transparency"""

    # Component scores (0-100 each)
    icp_fit_score: float
    buying_power_score: float
    engagement_potential_score: float

    # Final weighted score
    final_score: float

    # Configuration used for calculation
    icp_fit_weight: float = 0.40
    buying_power_weight: float = 0.30
    engagement_weight: float = 0.30

    def get_priority_level(self) -> str:
        """Get priority level based on final score"""
        if self.final_score >= ScoreThreshold.HIGH_PRIORITY.value:
            return "High Priority"
        elif self.final_score >= ScoreThreshold.MEDIUM_PRIORITY.value:
            return "Medium Priority"
        else:
            return "Low Priority"

    def get_score_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of score components"""
        return {
            'ICP Fit': round(self.icp_fit_score, 1),
            'Buying Power': round(self.buying_power_score, 1),
            'Engagement Potential': round(self.engagement_potential_score, 1),
            'Final Score': round(self.final_score, 1)
        }

    def get_weighted_contributions(self) -> Dict[str, float]:
        """Get how much each component contributes to final score"""
        return {
            'ICP Fit Contribution': round(self.icp_fit_score * self.icp_fit_weight, 1),
            'Buying Power Contribution': round(self.buying_power_score * self.buying_power_weight, 1),
            'Engagement Contribution': round(self.engagement_potential_score * self.engagement_weight, 1)
        }

    @classmethod
    def calculate(cls, icp_fit: float, buying_power: float, engagement: float,
                 config: Dict[str, Any]) -> 'LeadScore':
        """Calculate lead score using configuration weights"""

        weights = config['scoring_formula']['component_weights']

        final_score = (
            icp_fit * weights['icp_fit_weight'] +
            buying_power * weights['buying_power_weight'] +
            engagement * weights['engagement_weight']
        )

        return cls(
            icp_fit_score=icp_fit,
            buying_power_score=buying_power,
            engagement_potential_score=engagement,
            final_score=final_score,
            icp_fit_weight=weights['icp_fit_weight'],
            buying_power_weight=weights['buying_power_weight'],
            engagement_weight=weights['engagement_weight']
        )


class LeadScoringEngine:
    """Engine for calculating and managing lead scores"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def score_contact_icp_fit(self, title: str, bio: str = None, tenure: str = None) -> float:
        """Calculate ICP fit score for a contact"""
        score = 0.0

        # Title match scoring
        title_lower = title.lower()
        title_scores = self.config['icp_fit_scoring']['components']['title_match']['scoring']

        if any(level in title_lower for level in ['vp', 'vice president', 'head']):
            score = title_scores['VP_or_Head_level']
        elif 'director' in title_lower:
            score = title_scores['Director_level']
        elif 'senior manager' in title_lower:
            score = title_scores['Senior_Manager']
        elif 'manager' in title_lower:
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

        # Role tenure adjustment
        if tenure:
            tenure_scores = self.config['icp_fit_scoring']['components']['role_tenure']['scoring']
            if 'month' in tenure and any(char.isdigit() for char in tenure):
                months = int(''.join(filter(str.isdigit, tenure)))
                if months < 6:
                    score += tenure_scores['less_than_6_months']
                else:
                    score += tenure_scores['6_to_12_months']
            elif 'year' in tenure and any(char.isdigit() for char in tenure):
                years = int(''.join(filter(str.isdigit, tenure)))
                if years >= 3:
                    score += tenure_scores['more_than_3_years']
                elif years >= 1:
                    score += tenure_scores['1_to_3_years']

        return max(0, min(100, score))

    def score_buying_power(self, title: str) -> float:
        """Calculate buying power score based on title"""
        title_lower = title.lower()

        if any(level in title_lower for level in ['vp', 'vice president', 'head', 'chief']):
            return 100.0
        elif 'director' in title_lower:
            return 70.0
        elif any(level in title_lower for level in ['manager', 'lead']):
            return 50.0
        else:
            return 30.0

    def score_engagement_potential(self, linkedin_activity: str, content_themes: List[str],
                                 network_quality: bool) -> float:
        """Calculate engagement potential score"""
        score = 0.0

        # LinkedIn activity frequency
        activity_config = self.config['engagement_potential_scoring']['components']['linkedin_activity']['scoring']
        score += activity_config.get(linkedin_activity.lower().replace('+', '_plus'), 0)

        # Content relevance
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
        if network_quality:
            score += self.config['engagement_potential_scoring']['components']['network_quality']['score']

        return min(score, 100)

    def calculate_lead_score(self, icp_fit: float, buying_power: float, engagement: float) -> LeadScore:
        """Calculate final lead score with all components"""
        return LeadScore.calculate(icp_fit, buying_power, engagement, self.config)

    def get_target_titles(self) -> List[str]:
        """Get list of target titles for contact discovery"""
        return self.config.get('target_titles', [])

    def get_pain_points(self) -> List[str]:
        """Get list of ICP pain points for problem matching"""
        return self.config.get('icp_pain_points', [])

    def should_enrich_contact(self, lead_score: float, threshold: float = None) -> bool:
        """Determine if contact should proceed to Phase 3 enrichment"""
        threshold = threshold or self.config['scoring_thresholds']['high_priority']['min_score']
        return lead_score >= threshold