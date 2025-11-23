"""
Phase 5: Strategic Partnership Intelligence

Identifies existing vendor relationships at target accounts to uncover co-sell opportunities,
integration pathways, and warm introduction routes for Verdigris partnerships team.
"""
import logging
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, date

from ..models.account import Account
from ..models.strategic_partnership import PartnershipCategory, PartnershipAction
from ..utils.data_classification import DataClassification, DataSource
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class PartnershipConfidence(Enum):
    """Confidence levels for detected partnerships"""
    HIGH = "High"      # Direct announcement, official partnership
    MEDIUM = "Medium"  # Job posting, industry news
    LOW = "Low"        # Social signals, indirect evidence


@dataclass
class DetectedPartnership:
    """Represents a detected vendor relationship"""
    partner_name: str
    category: PartnershipCategory
    relationship_evidence: str
    evidence_url: Optional[str] = None
    detected_date: date = None
    confidence: PartnershipConfidence = PartnershipConfidence.MEDIUM
    confidence_score: float = 70.0
    verdigris_opportunity: str = ""
    partnership_action: PartnershipAction = PartnershipAction.INVESTIGATE

    def __post_init__(self):
        """Set defaults after initialization"""
        if not self.detected_date:
            self.detected_date = date.today()

        if not self.verdigris_opportunity:
            self.verdigris_opportunity = self._generate_opportunity_angle()

    def _generate_opportunity_angle(self) -> str:
        """Generate Verdigris opportunity angle based on category"""
        opportunity_angles = {
            PartnershipCategory.DCIM: "Integration potential for real-time power data feeds",
            PartnershipCategory.EMS: "Data enrichment with granular circuit-level monitoring",
            PartnershipCategory.COOLING: "Co-deployment to monitor cooling system electrical performance",
            PartnershipCategory.DC_EQUIPMENT: "Monitoring integration to track equipment health and performance",
            PartnershipCategory.RACKS: "Rack-level power visibility for capacity planning",
            PartnershipCategory.GPUS: "High-density monitoring for AI workloads and thermal management",
            PartnershipCategory.CRITICAL_FACILITIES: "Post-commissioning continuous validation and monitoring",
            PartnershipCategory.PROFESSIONAL_SERVICES: "Energy audit capabilities with ongoing monitoring data"
        }
        return opportunity_angles.get(self.category, "General monitoring integration opportunity")


class PartnershipIntelligenceAnalyzer:
    """Phase 5: Detects and analyzes strategic partnerships at target accounts"""

    def __init__(self):
        self.data_classification = DataClassification()
        self.web_limiter = RateLimiter(requests_per_second=2)  # Respectful web scraping
        self.linkedin_limiter = RateLimiter(requests_per_second=1)

        # Vendor databases by category (from references/strategic_partnerships.md)
        self.vendor_categories = {
            PartnershipCategory.DCIM: [
                "Schneider Electric EcoStruxure", "Sunbird DCIM", "FNT Command",
                "nlyte", "Device42", "CA Technologies DCIM"
            ],
            PartnershipCategory.EMS: [
                "Siemens Desigo", "Honeywell Forge", "Johnson Controls Metasys",
                "Veolia Energy Management", "Schneider EcoStruxure"
            ],
            PartnershipCategory.COOLING: [
                "Vertiv", "Liebert", "Schneider Electric APC", "Stulz", "Rittal",
                "Trane", "Carrier"
            ],
            PartnershipCategory.DC_EQUIPMENT: [
                "Eaton", "APC by Schneider", "Vertiv", "Generac", "Caterpillar",
                "Cummins", "Schneider Electric"
            ],
            PartnershipCategory.RACKS: [
                "Chatsworth Products", "CPI", "Legrand", "Panduit", "Rittal",
                "APC NetShelter"
            ],
            PartnershipCategory.GPUS: [
                "NVIDIA DGX", "AMD Instinct", "CoreWeave", "Lambda Labs",
                "Supermicro", "Dell PowerEdge"
            ],
            PartnershipCategory.CRITICAL_FACILITIES: [
                "AECOM", "Turner Construction", "DPR Construction", "FORTIS",
                "Gensler", "Mazzetti"
            ],
            PartnershipCategory.PROFESSIONAL_SERVICES: [
                "Cx Associates", "EYP Mission Critical", "Stantec", "Buro Happold",
                "WSP", "RMF Engineering"
            ]
        }

    async def analyze_partnership_intelligence(self, account: Account) -> Dict[str, Any]:
        """
        Detect and analyze strategic partnerships for the account

        Args:
            account: Target account to analyze

        Returns:
            Dictionary with partnership intelligence data
        """
        logger.info(f"🤝 Phase 5: Analyzing partnership intelligence for {account.name}")

        detected_partnerships = []

        # Scan each vendor category for partnerships
        for category, vendors in self.vendor_categories.items():
            logger.info(f"🔍 Scanning {category.value} partnerships...")

            category_partnerships = await self._detect_category_partnerships(
                account, category, vendors
            )
            detected_partnerships.extend(category_partnerships)

        # Filter and prioritize partnerships
        filtered_partnerships = self._filter_partnerships(detected_partnerships)
        prioritized_partnerships = self._prioritize_partnerships(filtered_partnerships)

        # Generate partnership intelligence report
        intelligence_report = {
            'account_name': account.name,
            'analysis_summary': {
                'total_detected': len(detected_partnerships),
                'filtered_count': len(filtered_partnerships),
                'high_priority': len([p for p in prioritized_partnerships
                                    if p.partnership_action == PartnershipAction.INVESTIGATE]),
                'analysis_date': self.data_classification.get_current_timestamp(),
                'phase_5_complete': True
            },
            'detected_partnerships': prioritized_partnerships,
            'category_breakdown': self._generate_category_breakdown(prioritized_partnerships),
            'opportunity_summary': self._generate_opportunity_summary(prioritized_partnerships)
        }

        # Add partnerships to account
        for partnership in prioritized_partnerships:
            account.add_strategic_partnership(
                partner_name=partnership.partner_name,
                category=partnership.category,
                evidence_url=partnership.evidence_url,
                confidence=partnership.confidence.value,
                opportunity_angle=partnership.verdigris_opportunity,
                action=partnership.partnership_action
            )

        logger.info(f"✅ Phase 5 partnership intelligence complete: {len(prioritized_partnerships)} partnerships detected")
        return intelligence_report

    async def _detect_category_partnerships(self, account: Account, category: PartnershipCategory,
                                          vendors: List[str]) -> List[DetectedPartnership]:
        """Detect partnerships in a specific vendor category"""

        partnerships = []

        for vendor in vendors:
            # Mock detection for demonstration (in production, would use real web scraping)
            partnership = await self._mock_detect_partnership(account, category, vendor)
            if partnership:
                partnerships.append(partnership)

        return partnerships

    async def _mock_detect_partnership(self, account: Account, category: PartnershipCategory,
                                     vendor: str) -> Optional[DetectedPartnership]:
        """
        Mock partnership detection for testing
        In production, this would perform actual web searches and scraping
        """

        # Apply rate limiting
        async with self.web_limiter:
            # Simulate detection likelihood based on category and account characteristics
            detection_probability = self._calculate_detection_probability(account, category)

            # Mock detection logic
            import random
            if random.random() < detection_probability:
                return self._generate_mock_partnership(account, category, vendor)

        return None

    def _calculate_detection_probability(self, account: Account, category: PartnershipCategory) -> float:
        """Calculate probability of detecting a partnership based on account characteristics"""

        base_probability = 0.3  # 30% base chance

        # Increase probability based on account size
        if account.employee_count:
            if account.employee_count > 1000:
                base_probability += 0.3
            elif account.employee_count > 500:
                base_probability += 0.2

        # Increase probability for certain business models
        if account.business_model in ['cloud', 'hyperscaler']:
            base_probability += 0.2

        # Category-specific adjustments
        category_multipliers = {
            PartnershipCategory.DC_EQUIPMENT: 1.2,  # Most likely to have
            PartnershipCategory.COOLING: 1.1,
            PartnershipCategory.DCIM: 0.9,
            PartnershipCategory.GPUS: 1.3 if any(event.event_type.value == 'AI_WORKLOAD' for event in account.trigger_events) else 0.7,
            PartnershipCategory.PROFESSIONAL_SERVICES: 0.8
        }

        multiplier = category_multipliers.get(category, 1.0)
        return min(0.8, base_probability * multiplier)  # Cap at 80%

    def _generate_mock_partnership(self, account: Account, category: PartnershipCategory,
                                 vendor: str) -> DetectedPartnership:
        """Generate mock partnership data for testing"""

        # Mock evidence types with different confidence levels
        evidence_scenarios = [
            {
                'evidence': f"Job posting mentions {vendor} experience required",
                'confidence': PartnershipConfidence.MEDIUM,
                'url': f"https://{account.domain}/careers/infrastructure-engineer"
            },
            {
                'evidence': f"LinkedIn post about {vendor} deployment success",
                'confidence': PartnershipConfidence.MEDIUM,
                'url': f"https://linkedin.com/company/{account.name.lower().replace(' ', '-')}/posts"
            },
            {
                'evidence': f"Press release announcing {vendor} partnership",
                'confidence': PartnershipConfidence.HIGH,
                'url': f"https://{account.domain}/newsroom/press-releases"
            },
            {
                'evidence': f"Employee LinkedIn profile lists {vendor} certifications",
                'confidence': PartnershipConfidence.LOW,
                'url': f"https://linkedin.com/in/employee-profile"
            }
        ]

        import random
        scenario = random.choice(evidence_scenarios)

        # Determine partnership action based on category priority
        high_priority_categories = [
            PartnershipCategory.DCIM,
            PartnershipCategory.GPUS,
            PartnershipCategory.CRITICAL_FACILITIES
        ]

        if category in high_priority_categories and scenario['confidence'] in [PartnershipConfidence.HIGH, PartnershipConfidence.MEDIUM]:
            action = PartnershipAction.INVESTIGATE
        elif scenario['confidence'] == PartnershipConfidence.HIGH:
            action = PartnershipAction.CONTACT
        else:
            action = PartnershipAction.MONITOR

        partnership = DetectedPartnership(
            partner_name=vendor,
            category=category,
            relationship_evidence=f"🧪 [MOCK] {scenario['evidence']}",
            evidence_url=scenario['url'],
            confidence=scenario['confidence'],
            partnership_action=action
        )

        # Set confidence score
        confidence_scores = {
            PartnershipConfidence.HIGH: 90.0,
            PartnershipConfidence.MEDIUM: 70.0,
            PartnershipConfidence.LOW: 40.0
        }
        partnership.confidence_score = confidence_scores[scenario['confidence']]

        return partnership

    def _filter_partnerships(self, partnerships: List[DetectedPartnership]) -> List[DetectedPartnership]:
        """Filter partnerships based on confidence and recency"""

        filtered = []
        for partnership in partnerships:
            # Filter by minimum confidence
            if partnership.confidence_score >= 40:  # Minimum threshold

                # Check recency (partnerships detected in last 24 months)
                if partnership.detected_date:
                    days_ago = (date.today() - partnership.detected_date).days
                    if days_ago <= 730:  # 24 months
                        filtered.append(partnership)
                else:
                    filtered.append(partnership)  # Keep if no date

        return filtered

    def _prioritize_partnerships(self, partnerships: List[DetectedPartnership]) -> List[DetectedPartnership]:
        """Prioritize partnerships by strategic value and confidence"""

        # Define priority scoring
        category_priorities = {
            PartnershipCategory.DCIM: 100,           # Highest priority - direct integration
            PartnershipCategory.GPUS: 95,            # High priority - AI angle
            PartnershipCategory.CRITICAL_FACILITIES: 90,  # High priority - design-in opportunity
            PartnershipCategory.EMS: 80,             # Medium-high priority
            PartnershipCategory.COOLING: 75,         # Medium priority
            PartnershipCategory.DC_EQUIPMENT: 70,    # Medium priority
            PartnershipCategory.PROFESSIONAL_SERVICES: 65,  # Medium-low priority
            PartnershipCategory.RACKS: 60            # Lower priority
        }

        confidence_multipliers = {
            PartnershipConfidence.HIGH: 1.0,
            PartnershipConfidence.MEDIUM: 0.8,
            PartnershipConfidence.LOW: 0.6
        }

        # Calculate priority scores
        for partnership in partnerships:
            base_priority = category_priorities.get(partnership.category, 50)
            confidence_multiplier = confidence_multipliers.get(partnership.confidence, 0.5)
            partnership.priority_score = base_priority * confidence_multiplier

        # Sort by priority score (highest first)
        return sorted(partnerships, key=lambda p: p.priority_score, reverse=True)

    def _generate_category_breakdown(self, partnerships: List[DetectedPartnership]) -> Dict[str, Dict[str, Any]]:
        """Generate breakdown by partnership category"""

        breakdown = {}
        for category in PartnershipCategory:
            category_partnerships = [p for p in partnerships if p.category == category]

            if category_partnerships:
                breakdown[category.value] = {
                    'count': len(category_partnerships),
                    'partners': [p.partner_name for p in category_partnerships],
                    'highest_confidence': max(p.confidence_score for p in category_partnerships),
                    'recommended_actions': list(set(p.partnership_action.value for p in category_partnerships))
                }

        return breakdown

    def _generate_opportunity_summary(self, partnerships: List[DetectedPartnership]) -> Dict[str, Any]:
        """Generate summary of partnership opportunities"""

        if not partnerships:
            return {'total_opportunities': 0, 'recommendations': []}

        # Count by action type
        action_counts = {}
        for partnership in partnerships:
            action = partnership.partnership_action.value
            action_counts[action] = action_counts.get(action, 0) + 1

        # Generate strategic recommendations
        recommendations = []

        high_priority = [p for p in partnerships if p.partnership_action == PartnershipAction.INVESTIGATE]
        if high_priority:
            recommendations.append(
                f"🔥 IMMEDIATE: Investigate {len(high_priority)} high-priority partnerships for co-sell opportunities"
            )

        dcim_partners = [p for p in partnerships if p.category == PartnershipCategory.DCIM]
        if dcim_partners:
            recommendations.append(
                f"🔌 INTEGRATION: {len(dcim_partners)} DCIM partnerships identified for API integration"
            )

        gpu_partners = [p for p in partnerships if p.category == PartnershipCategory.GPUS]
        if gpu_partners:
            recommendations.append(
                f"🤖 AI ANGLE: {len(gpu_partners)} GPU infrastructure partnerships for high-density monitoring"
            )

        return {
            'total_opportunities': len(partnerships),
            'action_breakdown': action_counts,
            'strategic_recommendations': recommendations
        }