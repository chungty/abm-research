"""
Engagement Intelligence Models

Data structures for Phase 4 engagement intelligence analysis
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class EngagementPriority(Enum):
    """Priority levels for engagement activities"""
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OutreachChannel(Enum):
    """Recommended outreach channels"""
    LINKEDIN_SOCIAL = "linkedin_social"
    LINKEDIN_DIRECT = "linkedin_direct"
    EMAIL_DIRECT = "email_direct"
    PHONE_CALL = "phone_call"
    WARM_INTRODUCTION = "warm_introduction"
    CONTENT_ENGAGEMENT = "content_engagement"


@dataclass
class EngagementStrategy:
    """Comprehensive engagement strategy for a contact"""
    contact_name: str
    priority: EngagementPriority
    recommended_channels: List[OutreachChannel]
    timing_rationale: str
    approach_summary: str
    success_metrics: List[str]
    estimated_response_rate: float  # 0-100


@dataclass
class ContentHook:
    """Specific content hook for personalized outreach"""
    hook_type: str  # Recent post, shared interest, industry event, etc.
    description: str
    reference_text: str  # Exact text to reference
    confidence: str  # High, Medium, Low
    verdigris_angle: str  # How to connect to Verdigris value


@dataclass
class EngagementIntelligence:
    """Complete engagement intelligence for a contact"""
    contact_name: str
    final_lead_score: float

    # Problem analysis
    likely_problems: List[str]
    problem_confidence: str
    problem_rationale: str

    # Content analysis
    content_themes: List[str]
    content_quality: str
    content_source: str
    content_hooks: List[ContentHook] = field(default_factory=list)

    # Connection analysis
    connection_pathways: List[str]
    mutual_connections: int
    shared_groups: List[str]
    connection_confidence: str

    # Value-add opportunities
    value_add_ideas: List[str]
    recommended_assets: List[str]

    # Overall strategy
    engagement_strategy: Optional[EngagementStrategy] = None

    # Metadata
    analysis_date: datetime = field(default_factory=datetime.now)
    data_sources: List[str] = field(default_factory=list)

    def get_engagement_summary(self) -> Dict[str, Any]:
        """Get summary of engagement intelligence"""
        return {
            'contact': self.contact_name,
            'score': self.final_lead_score,
            'top_problems': self.likely_problems[:3],
            'best_hooks': [hook.description for hook in self.content_hooks[:2]],
            'strategy': self.engagement_strategy.approach_summary if self.engagement_strategy else "Not defined",
            'priority': self.engagement_strategy.priority.value if self.engagement_strategy else "medium"
        }

    def has_high_engagement_potential(self) -> bool:
        """Check if contact has high engagement potential"""
        return (
            self.final_lead_score >= 70 and
            self.content_quality in ['High', 'Medium'] and
            len(self.content_hooks) > 0
        )