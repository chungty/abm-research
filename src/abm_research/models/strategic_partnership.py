"""
Strategic Partnership model for ABM Research System
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional


class PartnershipCategory(Enum):
    DCIM = "DCIM"
    EMS = "EMS"
    COOLING = "Cooling"
    DC_EQUIPMENT = "DC Equipment"
    RACKS = "Racks"
    GPUS = "GPUs"
    CRITICAL_FACILITIES = "Critical Facilities"
    PROFESSIONAL_SERVICES = "Professional Services"


class PartnershipConfidence(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PartnershipAction(Enum):
    INVESTIGATE = "Investigate"
    CONTACT = "Contact"
    MONITOR = "Monitor"
    NOT_RELEVANT = "Not Relevant"


@dataclass
class StrategicPartnership:
    """Represents a detected strategic partnership at an account"""

    # Core partnership data
    partner_name: str
    category: PartnershipCategory
    relationship_evidence: str  # Description of the relationship
    confidence: PartnershipConfidence

    # Source information
    evidence_url: Optional[str] = None
    detected_date: date = field(default_factory=date.today)

    # Verdigris opportunity analysis
    opportunity_angle: str = ""
    partnership_action: PartnershipAction = PartnershipAction.MONITOR

    # Relations
    account: Optional["Account"] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Set opportunity angle and action based on category"""
        if not self.opportunity_angle:
            self.opportunity_angle = self._get_default_opportunity_angle()

        if self.partnership_action == PartnershipAction.MONITOR:
            self.partnership_action = self._get_default_action()

    def _get_default_opportunity_angle(self) -> str:
        """Get default Verdigris opportunity angle based on partnership category"""
        angles = {
            PartnershipCategory.DCIM: "Integration potential for real-time power data feeds and enhanced electrical risk detection capabilities",
            PartnershipCategory.EMS: "Data enrichment with granular circuit-level data to improve energy management accuracy",
            PartnershipCategory.COOLING: "Co-deployment opportunity to monitor cooling system electrical performance and optimize efficiency",
            PartnershipCategory.DC_EQUIPMENT: "Monitoring integration to track health and performance of critical infrastructure equipment",
            PartnershipCategory.RACKS: "Rack-level monitoring for precise capacity planning and right-sizing deployments",
            PartnershipCategory.GPUS: "High-density monitoring for AI workloads with predictive capacity planning for GPU clusters",
            PartnershipCategory.CRITICAL_FACILITIES: "Design-build integration opportunity to specify Verdigris monitoring in new facility construction",
            PartnershipCategory.PROFESSIONAL_SERVICES: "Post-commissioning continuous validation and ongoing energy audit data provision",
        }
        return angles.get(
            self.category, "General monitoring and optimization integration opportunity"
        )

    def _get_default_action(self) -> PartnershipAction:
        """Get default partnership action based on category priority"""
        high_priority_categories = [
            PartnershipCategory.DCIM,
            PartnershipCategory.GPUS,
            PartnershipCategory.CRITICAL_FACILITIES,
        ]

        medium_priority_categories = [
            PartnershipCategory.COOLING,
            PartnershipCategory.EMS,
            PartnershipCategory.PROFESSIONAL_SERVICES,
        ]

        if self.category in high_priority_categories:
            return PartnershipAction.INVESTIGATE
        elif self.category in medium_priority_categories:
            return PartnershipAction.CONTACT
        else:
            return PartnershipAction.MONITOR

    @classmethod
    def from_detection(
        cls,
        partner_name: str,
        category: PartnershipCategory,
        evidence: str,
        source_url: Optional[str] = None,
        confidence_modifier: float = 1.0,
    ) -> "StrategicPartnership":
        """Create partnership from detection with automatic confidence scoring"""

        # Determine confidence based on source and evidence quality
        confidence = cls._determine_confidence(evidence, source_url, confidence_modifier)

        return cls(
            partner_name=partner_name,
            category=category,
            relationship_evidence=evidence,
            confidence=confidence,
            evidence_url=source_url,
        )

    @staticmethod
    def _determine_confidence(
        evidence: str, source_url: Optional[str], modifier: float
    ) -> PartnershipConfidence:
        """Determine confidence level based on evidence and source"""
        base_score = 50  # Medium by default

        # Boost for strong evidence keywords
        evidence_lower = evidence.lower()
        high_confidence_terms = [
            "partnership",
            "integration",
            "deployment",
            "contract",
            "agreement",
        ]
        medium_confidence_terms = ["using", "implements", "works with", "powered by"]

        if any(term in evidence_lower for term in high_confidence_terms):
            base_score += 30
        elif any(term in evidence_lower for term in medium_confidence_terms):
            base_score += 15

        # Boost for reliable sources
        if source_url:
            url_lower = source_url.lower()
            if any(domain in url_lower for domain in ["newsroom", "press-release", "case-study"]):
                base_score += 25
            elif any(domain in url_lower for domain in ["linkedin.com", "careers"]):
                base_score += 15

        # Apply modifier
        final_score = base_score * modifier

        # Convert to confidence level
        if final_score >= 80:
            return PartnershipConfidence.HIGH
        elif final_score >= 50:
            return PartnershipConfidence.MEDIUM
        else:
            return PartnershipConfidence.LOW

    def get_priority_score(self) -> int:
        """Get numeric priority score for sorting (higher = more important)"""
        category_scores = {
            PartnershipCategory.DCIM: 100,
            PartnershipCategory.GPUS: 95,
            PartnershipCategory.CRITICAL_FACILITIES: 90,
            PartnershipCategory.COOLING: 70,
            PartnershipCategory.EMS: 65,
            PartnershipCategory.PROFESSIONAL_SERVICES: 60,
            PartnershipCategory.DC_EQUIPMENT: 50,
            PartnershipCategory.RACKS: 40,
        }

        base_score = category_scores.get(self.category, 30)

        # Boost for high confidence
        if self.confidence == PartnershipConfidence.HIGH:
            base_score += 20
        elif self.confidence == PartnershipConfidence.MEDIUM:
            base_score += 10

        return base_score

    def is_high_priority(self) -> bool:
        """Check if partnership requires immediate investigation"""
        return (
            self.category
            in [
                PartnershipCategory.DCIM,
                PartnershipCategory.GPUS,
                PartnershipCategory.CRITICAL_FACILITIES,
            ]
            and self.confidence != PartnershipConfidence.LOW
        )

    def get_co_sell_potential(self) -> str:
        """Get specific co-sell strategy based on partner and category"""
        strategies = {
            PartnershipCategory.DCIM: f"Joint solution: {self.partner_name} DCIM + Verdigris real-time power data = complete infrastructure visibility",
            PartnershipCategory.GPUS: f"AI workload specialization: {self.partner_name} hardware + Verdigris monitoring = optimized GPU cluster management",
            PartnershipCategory.COOLING: f"Efficiency partnership: {self.partner_name} cooling + Verdigris electrical monitoring = maximized cooling ROI",
            PartnershipCategory.CRITICAL_FACILITIES: f"Design-build advantage: {self.partner_name} construction + Verdigris pre-specified monitoring = turnkey intelligent facility",
            PartnershipCategory.EMS: f"Data enhancement: Upgrade {self.partner_name} EMS with Verdigris granular power intelligence",
            PartnershipCategory.PROFESSIONAL_SERVICES: f"Service extension: {self.partner_name} commissioning + Verdigris ongoing monitoring = continuous optimization",
            PartnershipCategory.DC_EQUIPMENT: f"Equipment intelligence: {self.partner_name} hardware + Verdigris monitoring = predictive maintenance capability",
            PartnershipCategory.RACKS: f"Rack optimization: {self.partner_name} infrastructure + Verdigris per-rack monitoring = precise capacity planning",
        }
        return strategies.get(
            self.category,
            f"Integration opportunity with {self.partner_name} {self.category.value} solutions",
        )

    def to_notion_format(self) -> dict[str, Any]:
        """Convert to Notion database format"""
        return {
            "Partner name": {"title": [{"text": {"content": self.partner_name}}]},
            "Category": {"select": {"name": self.category.value}},
            "Relationship evidence URL": {"url": self.evidence_url} if self.evidence_url else None,
            "Detected date": {"date": {"start": self.detected_date.isoformat()}},
            "Confidence": {"select": {"name": self.confidence.value}},
            "Verdigris opportunity angle": {
                "rich_text": [{"text": {"content": self.opportunity_angle}}]
            },
            "Partnership team action": {"select": {"name": self.partnership_action.value}},
        }

    def __str__(self) -> str:
        return f"Partnership({self.partner_name}, {self.category.value}, {self.confidence.value})"

    def __repr__(self) -> str:
        return (
            f"StrategicPartnership(partner='{self.partner_name}', "
            f"category={self.category.value}, "
            f"confidence={self.confidence.value})"
        )
