"""
Trigger Event model for ABM Research System
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any
from enum import Enum


class EventType(Enum):
    EXPANSION = "Expansion"
    INHERITED_INFRASTRUCTURE = "Inherited Infrastructure"
    LEADERSHIP_CHANGE = "Leadership Change"
    AI_WORKLOAD = "AI Workload"
    ENERGY_PRESSURE = "Energy Pressure"
    DOWNTIME_INCIDENT = "Downtime/Incident"
    SUSTAINABILITY = "Sustainability"


class ConfidenceLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class TriggerEvent:
    """Represents a trigger event detected for an account"""

    # Core event data
    description: str
    event_type: EventType
    confidence_level: ConfidenceLevel

    # Scoring
    confidence_score: float  # 0-100 numeric confidence
    relevance_score: float  # 0-100 alignment to Verdigris triggers

    # Source and timing
    source_url: Optional[str] = None
    detected_date: date = field(default_factory=date.today)
    event_date: Optional[date] = None  # when the event actually occurred

    # Relations
    account: Optional['Account'] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and adjust scores after initialization"""
        # Apply recency decay to confidence score
        if self.event_date and (date.today() - self.event_date).days > 60:
            self.confidence_score = max(self.confidence_score - 10, 0)

        # Ensure scores are within valid range
        self.confidence_score = max(0, min(100, self.confidence_score))
        self.relevance_score = max(0, min(100, self.relevance_score))

        # Set confidence level if not provided
        if self.confidence_score >= 90:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence_score >= 60:
            self.confidence_level = ConfidenceLevel.MEDIUM
        else:
            self.confidence_level = ConfidenceLevel.LOW

    @classmethod
    def from_detection(cls, description: str, event_type: EventType, source_url: str,
                      event_date: Optional[date] = None, confidence_modifier: float = 1.0) -> 'TriggerEvent':
        """Create trigger event from detection with automatic scoring"""

        # Base confidence by source type
        base_confidence = cls._get_source_confidence(source_url)
        confidence_score = min(100, base_confidence * confidence_modifier)

        # Calculate relevance based on event type and description
        relevance_score = cls._calculate_relevance(event_type, description)

        return cls(
            description=description,
            event_type=event_type,
            confidence_level=ConfidenceLevel.HIGH,  # Will be adjusted in __post_init__
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            source_url=source_url,
            event_date=event_date or date.today()
        )

    @staticmethod
    def _get_source_confidence(source_url: str) -> float:
        """Determine confidence score based on source URL"""
        if not source_url:
            return 30

        url_lower = source_url.lower()

        # High confidence sources (90-100)
        high_confidence_domains = [
            'newsroom', 'press-releases', 'investors', 'sec.gov',
            'linkedin.com/company', 'careers.'
        ]
        if any(domain in url_lower for domain in high_confidence_domains):
            return 95

        # Medium confidence sources (60-80)
        medium_confidence_domains = [
            'datacenterdynamics.com', 'datacenterknowledge.com',
            'bloomberg.com', 'reuters.com', 'wsj.com'
        ]
        if any(domain in url_lower for domain in medium_confidence_domains):
            return 70

        # Default to low confidence
        return 40

    @staticmethod
    def _calculate_relevance(event_type: EventType, description: str) -> float:
        """Calculate relevance score based on event type and description content"""
        desc_lower = description.lower()

        # High relevance keywords
        high_relevance_terms = [
            'power', 'energy', 'capacity', 'uptime', 'ai infrastructure',
            'gpu', 'data center operations', 'electrical', 'cooling'
        ]

        # Medium relevance keywords
        medium_relevance_terms = [
            'infrastructure', 'facility', 'expansion', 'merger',
            'acquisition', 'sustainability', 'cost reduction'
        ]

        # Base score by event type
        type_base_scores = {
            EventType.AI_WORKLOAD: 90,
            EventType.ENERGY_PRESSURE: 85,
            EventType.DOWNTIME_INCIDENT: 80,
            EventType.EXPANSION: 70,
            EventType.LEADERSHIP_CHANGE: 65,
            EventType.SUSTAINABILITY: 60,
            EventType.INHERITED_INFRASTRUCTURE: 55
        }

        base_score = type_base_scores.get(event_type, 50)

        # Boost for high relevance keywords
        high_matches = sum(1 for term in high_relevance_terms if term in desc_lower)
        if high_matches >= 2:
            return min(100, base_score + 20)
        elif high_matches >= 1:
            return min(100, base_score + 10)

        # Boost for medium relevance keywords
        medium_matches = sum(1 for term in medium_relevance_terms if term in desc_lower)
        if medium_matches >= 3:
            return min(100, base_score + 10)
        elif medium_matches >= 1:
            return min(100, base_score + 5)

        return base_score

    def is_recent(self, days: int = 90) -> bool:
        """Check if event is within specified recency window"""
        if not self.event_date:
            return True  # Assume recent if no date

        return (date.today() - self.event_date).days <= days

    def is_high_priority(self) -> bool:
        """Check if event is high priority (high confidence and relevance)"""
        return (self.confidence_score >= 80 and
                self.relevance_score >= 70 and
                self.is_recent())

    def get_verdigris_angle(self) -> str:
        """Get specific Verdigris value proposition based on event type"""
        angles = {
            EventType.AI_WORKLOAD: "High-density GPU workloads create power capacity planning urgency and cooling challenges - perfect fit for Verdigris real-time monitoring",
            EventType.ENERGY_PRESSURE: "Rising energy costs and PUE pressure directly align with Verdigris energy visibility and optimization capabilities",
            EventType.EXPANSION: "New facility buildouts need monitoring infrastructure from day one - opportunity to specify Verdigris in design phase",
            EventType.LEADERSHIP_CHANGE: "New leaders often review vendor stack and seek quick wins - good timing for Verdigris introduction",
            EventType.DOWNTIME_INCIDENT: "Recent outage pain creates urgency for predictive monitoring and risk detection capabilities",
            EventType.SUSTAINABILITY: "ESG reporting requirements need accurate power metering - Verdigris provides granular energy data",
            EventType.INHERITED_INFRASTRUCTURE: "Acquired infrastructure creates visibility gaps and integration complexity - Verdigris unifies monitoring across disparate systems"
        }
        return angles.get(self.event_type, "General data center monitoring and optimization opportunity")

    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion database format"""
        return {
            'Event description': {'title': [{'text': {'content': self.description}}]},
            'Event type': {'select': {'name': self.event_type.value}},
            'Confidence': {'select': {'name': self.confidence_level.value}},
            'Confidence score': {'number': round(self.confidence_score, 1)},
            'Relevance score': {'number': round(self.relevance_score, 1)},
            'Detected date': {'date': {'start': self.detected_date.isoformat()}},
            'Source URL': {'url': self.source_url} if self.source_url else None
        }

    def __str__(self) -> str:
        return f"TriggerEvent({self.event_type.value}, R:{self.relevance_score:.0f}, C:{self.confidence_score:.0f})"

    def __repr__(self) -> str:
        return (f"TriggerEvent(type={self.event_type.value}, "
                f"relevance={self.relevance_score:.1f}, "
                f"confidence={self.confidence_score:.1f})")