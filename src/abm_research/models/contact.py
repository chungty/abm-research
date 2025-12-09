"""
Contact model for ABM Research System
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ResearchStatus(Enum):
    NOT_STARTED = "Not Started"
    ENRICHED = "Enriched"
    ANALYZED = "Analyzed"


class BuyingCommitteeRole(Enum):
    ECONOMIC_BUYER = "Economic Buyer"
    TECHNICAL_EVALUATOR = "Technical Evaluator"
    CHAMPION = "Champion"
    INFLUENCER = "Influencer"


@dataclass
class Contact:
    """Represents a contact at a target account"""

    # Core identifiers
    name: str
    title: str
    email: Optional[str] = None
    linkedin_url: Optional[str] = None

    # Account relationship
    account: Optional['Account'] = None

    # Buying committee classification
    buying_committee_role: BuyingCommitteeRole = BuyingCommitteeRole.CHAMPION

    # Lead scoring dimensions (shown transparently)
    icp_fit_score: float = 0.0  # 0-100
    buying_power_score: float = 0.0  # 0-100
    engagement_potential_score: float = 0.0  # 0-100
    final_lead_score: float = 0.0  # calculated from components

    # Research status and timeline
    research_status: ResearchStatus = ResearchStatus.NOT_STARTED
    role_tenure: Optional[str] = None  # "6 months", "2 years", etc.

    # Phase 3 enrichment data (LinkedIn analysis)
    linkedin_activity_level: str = "unknown"  # weekly+, monthly, quarterly, inactive
    linkedin_content_themes: List[str] = field(default_factory=list)
    linkedin_network_quality: bool = False  # connected to DC operators/vendors

    # Phase 4 engagement intelligence
    problems_they_own: List[str] = field(default_factory=list)  # tags from ICP pain points
    content_themes_they_value: List[str] = field(default_factory=list)
    connection_pathways: str = ""  # diagnostic text
    value_add_ideas: List[str] = field(default_factory=list)  # 2-3 bullets

    # Apollo data
    apollo_contact_id: Optional[str] = None
    apollo_bio: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Calculate initial scores after initialization"""
        self.calculate_buying_power_score()

    def calculate_icp_fit_score(self, scoring_config: Dict[str, Any]) -> float:
        """Calculate ICP fit based on title match and responsibility keywords"""
        score = 0.0

        # Title match scoring
        title_lower = self.title.lower()
        title_scores = scoring_config['icp_fit_scoring']['components']['title_match']['scoring']

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

        # Responsibility keyword bonuses (from bio/about section)
        if self.apollo_bio:
            bio_lower = self.apollo_bio.lower()
            keywords = scoring_config['icp_fit_scoring']['components']['responsibility_keywords']['keywords']

            for category, config in keywords.items():
                for term in config['terms']:
                    if term.lower() in bio_lower:
                        score += config['points']
                        break  # Only add points once per category

        # Role tenure adjustment
        if self.role_tenure:
            tenure_scores = scoring_config['icp_fit_scoring']['components']['role_tenure']['scoring']
            if 'month' in self.role_tenure and int(self.role_tenure.split()[0]) < 6:
                score += tenure_scores['less_than_6_months']
            elif 'year' in self.role_tenure:
                years = int(self.role_tenure.split()[0])
                if years >= 3:
                    score += tenure_scores['more_than_3_years']
                elif years >= 1:
                    score += tenure_scores['1_to_3_years']
            else:
                score += tenure_scores['6_to_12_months']

        self.icp_fit_score = min(max(score, 0), 100)
        return self.icp_fit_score

    def calculate_buying_power_score(self) -> float:
        """Calculate buying power based on title level"""
        title_lower = self.title.lower()

        if any(level in title_lower for level in ['vp', 'vice president', 'head', 'chief']):
            self.buying_power_score = 100.0
            self.buying_committee_role = BuyingCommitteeRole.ECONOMIC_BUYER
        elif 'director' in title_lower:
            self.buying_power_score = 70.0
            self.buying_committee_role = BuyingCommitteeRole.TECHNICAL_EVALUATOR
        elif any(level in title_lower for level in ['manager', 'lead']):
            self.buying_power_score = 50.0
            self.buying_committee_role = BuyingCommitteeRole.CHAMPION
        else:
            self.buying_power_score = 30.0
            self.buying_committee_role = BuyingCommitteeRole.INFLUENCER

        return self.buying_power_score

    def calculate_engagement_potential_score(self) -> float:
        """Calculate engagement potential from LinkedIn activity"""
        score = 0.0

        # LinkedIn activity frequency
        activity_scores = {
            'weekly+': 50,
            'monthly': 30,
            'quarterly': 10,
            'inactive': 0
        }
        score += activity_scores.get(self.linkedin_activity_level, 0)

        # Content relevance
        high_relevance_topics = [
            'power', 'energy', 'AI infrastructure', 'capacity planning',
            'uptime', 'reliability', 'cost optimization', 'sustainability', 'PUE'
        ]

        relevant_themes = [theme for theme in self.linkedin_content_themes
                          if any(topic in theme.lower() for topic in high_relevance_topics)]

        if len(relevant_themes) >= 3:
            score += 25  # high relevance
        elif len(relevant_themes) >= 1:
            score += 15  # medium relevance

        # Network quality
        if self.linkedin_network_quality:
            score += 25

        self.engagement_potential_score = min(score, 100)
        return self.engagement_potential_score

    def calculate_final_lead_score(self, scoring_config: Dict[str, Any]) -> float:
        """Calculate final weighted lead score"""
        weights = scoring_config['scoring_formula']['component_weights']

        self.final_lead_score = (
            self.icp_fit_score * weights['icp_fit_weight'] +
            self.buying_power_score * weights['buying_power_weight'] +
            self.engagement_potential_score * weights['engagement_weight']
        )

        return self.final_lead_score

    def update_scores(self, scoring_config: Dict[str, Any]) -> float:
        """Recalculate all scores"""
        self.calculate_icp_fit_score(scoring_config)
        self.calculate_buying_power_score()
        self.calculate_engagement_potential_score()
        self.calculate_final_lead_score(scoring_config)
        return self.final_lead_score

    def add_linkedin_analysis(self, activity_level: str, content_themes: List[str], network_quality: bool):
        """Add LinkedIn enrichment data from Phase 3"""
        self.linkedin_activity_level = activity_level
        self.linkedin_content_themes = content_themes
        self.linkedin_network_quality = network_quality
        self.research_status = ResearchStatus.ENRICHED

    def add_engagement_intelligence(self, problems: List[str], content_themes: List[str],
                                  pathways: str, value_ideas: List[str]):
        """Add engagement intelligence from Phase 4"""
        self.problems_they_own = problems
        self.content_themes_they_value = content_themes
        self.connection_pathways = pathways
        self.value_add_ideas = value_ideas
        self.research_status = ResearchStatus.ANALYZED

    def is_high_priority(self, threshold: float = 70.0) -> bool:
        """Check if contact meets high priority threshold"""
        return self.final_lead_score >= threshold

    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion database format"""
        return {
            'Name': {'title': [{'text': {'content': self.name}}]},
            'Title': {'rich_text': [{'text': {'content': self.title}}]},
            'LinkedIn URL': {'url': self.linkedin_url} if self.linkedin_url else None,
            'Email': {'email': self.email} if self.email else None,
            'Buying committee role': {'select': {'name': self.buying_committee_role.value}},
            'ICP Fit Score': {'number': round(self.icp_fit_score, 1)},
            'Buying Power Score': {'number': round(self.buying_power_score, 1)},
            'Engagement Potential Score': {'number': round(self.engagement_potential_score, 1)},
            'Final Lead Score': {'number': round(self.final_lead_score, 1)},
            'Research status': {'select': {'name': self.research_status.value}},
            'Role tenure': {'rich_text': [{'text': {'content': self.role_tenure or ''}}]},
            'Problems they likely own': {'multi_select': [{'name': p} for p in self.problems_they_own]},
            'Content themes they value': {'multi_select': [{'name': t} for t in self.content_themes_they_value]},
            'Connection pathways': {'rich_text': [{'text': {'content': self.connection_pathways}}]},
            'Value-add ideas': {'rich_text': [{'text': {'content': '\n'.join(self.value_add_ideas)}}]}
        }

    def __str__(self) -> str:
        return f"Contact({self.name}, {self.title}, Score: {self.final_lead_score:.1f})"

    def __repr__(self) -> str:
        return (f"Contact(name='{self.name}', title='{self.title}', "
                f"lead_score={self.final_lead_score:.1f})")
