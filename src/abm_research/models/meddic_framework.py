"""
MEDDIC Sales Framework Integration for Contact Segmentation
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class MEDDICRole(Enum):
    """MEDDIC framework roles for strategic sales process"""

    METRICS_OWNER = "Metrics Owner"
    ECONOMIC_BUYER = "Economic Buyer"
    DECISION_MAKER = "Decision Maker"
    DECISION_CRITERIA = "Decision Criteria Owner"
    IDENTIFY_PAIN = "Pain Identifier"
    CHAMPION = "Champion"
    INFLUENCER = "Influencer"
    USER = "User"


class ContactSource(Enum):
    """How the contact was discovered"""

    APOLLO_SEARCH = "Apollo API Search"
    LINKEDIN_DISCOVERY = "LinkedIn Discovery"
    COMPANY_WEBSITE = "Company Website"
    NEWS_MENTION = "News/Press Release"
    REFERRAL = "Referral/Introduction"
    SOCIAL_MEDIA = "Social Media"
    MANUAL_RESEARCH = "Manual Research"


@dataclass
class ContactSourceAttribution:
    """Tracks how and where a contact was discovered"""

    source_type: ContactSource
    source_url: Optional[str] = None
    discovery_method: str = ""  # Specific search terms, referral path, etc.
    confidence_level: str = "Medium"  # High, Medium, Low
    discovery_date: Optional[str] = None
    notes: str = ""


@dataclass
class MEDDICProfile:
    """MEDDIC framework profile for strategic contact analysis"""

    # Primary MEDDIC role
    primary_role: MEDDICRole
    secondary_roles: List[MEDDICRole] = field(default_factory=list)

    # MEDDIC analysis
    metrics_access: bool = False  # Can they access/share metrics?
    economic_authority: bool = False  # Do they control budget?
    decision_influence: float = 0.0  # 0-100 influence on decision
    pain_ownership: List[str] = field(default_factory=list)  # Pain points they own
    champion_potential: float = 0.0  # 0-100 likelihood to champion Verdigris

    # Sales strategy
    engagement_strategy: str = ""
    key_value_props: List[str] = field(default_factory=list)
    potential_objections: List[str] = field(default_factory=list)

    def get_sales_approach(self) -> str:
        """Get recommended sales approach based on MEDDIC role"""
        approaches = {
            MEDDICRole.METRICS_OWNER: "Focus on ROI metrics, cost savings, and measurable outcomes. Request current KPIs and success metrics.",
            MEDDICRole.ECONOMIC_BUYER: "Present business case with clear ROI. Discuss budget, timeline, and procurement process.",
            MEDDICRole.DECISION_MAKER: "Executive-level value proposition. Focus on strategic outcomes and competitive advantage.",
            MEDDICRole.DECISION_CRITERIA: "Understand evaluation criteria and requirements. Position Verdigris capabilities against their checklist.",
            MEDDICRole.IDENTIFY_PAIN: "Deep discovery on current challenges. Position Verdigris as solution to their specific pain points.",
            MEDDICRole.CHAMPION: "Enable them to sell internally. Provide proof points, case studies, and champion enablement materials.",
            MEDDICRole.INFLUENCER: "Build relationship and credibility. Share technical insights and thought leadership content.",
            MEDDICRole.USER: "Focus on ease of use, day-to-day benefits, and how Verdigris improves their work experience.",
        }
        return approaches.get(self.primary_role, "Relationship building and discovery")


class MEDDICAnalyzer:
    """Analyzes contacts for MEDDIC framework fit"""

    def __init__(self):
        # Title patterns for MEDDIC role classification
        self.role_patterns = {
            MEDDICRole.METRICS_OWNER: [
                "analyst",
                "performance",
                "metrics",
                "kpi",
                "reporting",
                "business intelligence",
            ],
            MEDDICRole.ECONOMIC_BUYER: [
                "vp",
                "vice president",
                "svp",
                "chief",
                "president",
                "head of",
            ],
            MEDDICRole.DECISION_MAKER: [
                "ceo",
                "cto",
                "cfo",
                "coo",
                "president",
                "founder",
                "owner",
            ],
            MEDDICRole.DECISION_CRITERIA: [
                "director of",
                "head of",
                "lead",
                "principal",
                "architect",
                "consultant",
            ],
            MEDDICRole.IDENTIFY_PAIN: [
                "operations",
                "engineering",
                "infrastructure",
                "facilities",
                "maintenance",
            ],
            MEDDICRole.CHAMPION: ["manager", "senior manager", "team lead", "supervisor"],
            MEDDICRole.USER: ["technician", "specialist", "coordinator", "operator", "engineer"],
        }

    def analyze_contact_meddic(
        self, title: str, bio: str = None, company_role: str = None
    ) -> MEDDICProfile:
        """Analyze contact for MEDDIC framework classification"""

        title_lower = title.lower()
        bio_lower = (bio or "").lower()

        # Determine primary role
        primary_role = self._classify_primary_role(title_lower, bio_lower)

        # Determine secondary roles
        secondary_roles = self._classify_secondary_roles(title_lower, bio_lower, primary_role)

        # Analyze MEDDIC attributes
        profile = MEDDICProfile(
            primary_role=primary_role,
            secondary_roles=secondary_roles,
            metrics_access=self._has_metrics_access(title_lower, bio_lower),
            economic_authority=self._has_economic_authority(title_lower),
            decision_influence=self._calculate_decision_influence(title_lower, primary_role),
            pain_ownership=self._identify_pain_ownership(title_lower, bio_lower),
            champion_potential=self._assess_champion_potential(title_lower, primary_role),
            engagement_strategy=self._get_engagement_strategy(primary_role),
            key_value_props=self._get_key_value_props(primary_role),
            potential_objections=self._get_potential_objections(primary_role),
        )

        return profile

    def _classify_primary_role(self, title_lower: str, bio_lower: str) -> MEDDICRole:
        """Classify primary MEDDIC role based on title and bio"""

        # Check each role pattern
        for role, patterns in self.role_patterns.items():
            if any(pattern in title_lower for pattern in patterns):
                return role

        # Default classification based on seniority
        if any(term in title_lower for term in ["vp", "vice president", "svp"]):
            return MEDDICRole.ECONOMIC_BUYER
        elif any(term in title_lower for term in ["director", "head"]):
            return MEDDICRole.DECISION_CRITERIA
        elif any(term in title_lower for term in ["manager", "lead"]):
            return MEDDICRole.CHAMPION
        else:
            return MEDDICRole.USER

    def _classify_secondary_roles(
        self, title_lower: str, bio_lower: str, primary_role: MEDDICRole
    ) -> List[MEDDICRole]:
        """Identify secondary MEDDIC roles"""
        secondary = []

        # Cross-functional roles
        if "operations" in title_lower or "operations" in bio_lower:
            if primary_role != MEDDICRole.IDENTIFY_PAIN:
                secondary.append(MEDDICRole.IDENTIFY_PAIN)

        if any(term in bio_lower for term in ["budget", "cost", "roi", "procurement"]):
            if primary_role not in [MEDDICRole.ECONOMIC_BUYER, MEDDICRole.METRICS_OWNER]:
                secondary.append(MEDDICRole.METRICS_OWNER)

        return secondary

    def _has_metrics_access(self, title_lower: str, bio_lower: str) -> bool:
        """Determine if contact likely has access to metrics"""
        metrics_indicators = [
            "director",
            "vp",
            "head",
            "manager",
            "analyst",
            "performance",
            "reporting",
            "metrics",
            "kpi",
            "dashboard",
        ]
        return any(
            indicator in title_lower or indicator in bio_lower for indicator in metrics_indicators
        )

    def _has_economic_authority(self, title_lower: str) -> bool:
        """Determine if contact has budget authority"""
        authority_indicators = [
            "vp",
            "vice president",
            "svp",
            "chief",
            "ceo",
            "cto",
            "cfo",
            "president",
            "head of",
            "director of",
        ]
        return any(indicator in title_lower for indicator in authority_indicators)

    def _calculate_decision_influence(self, title_lower: str, primary_role: MEDDICRole) -> float:
        """Calculate decision influence score (0-100)"""
        base_scores = {
            MEDDICRole.DECISION_MAKER: 95,
            MEDDICRole.ECONOMIC_BUYER: 85,
            MEDDICRole.DECISION_CRITERIA: 70,
            MEDDICRole.METRICS_OWNER: 60,
            MEDDICRole.CHAMPION: 50,
            MEDDICRole.IDENTIFY_PAIN: 45,
            MEDDICRole.INFLUENCER: 35,
            MEDDICRole.USER: 25,
        }

        base_score = base_scores.get(primary_role, 30)

        # Boost for senior titles
        if any(term in title_lower for term in ["vp", "vice president", "svp", "chief"]):
            base_score += 15
        elif "director" in title_lower:
            base_score += 10
        elif "senior" in title_lower:
            base_score += 5

        return min(100, base_score)

    def _identify_pain_ownership(self, title_lower: str, bio_lower: str) -> List[str]:
        """Identify pain points this contact likely owns"""
        pain_mapping = {
            "operations": ["Uptime pressure", "Operational efficiency", "Cost optimization"],
            "infrastructure": ["Capacity planning", "Infrastructure reliability", "Scalability"],
            "facilities": ["Energy efficiency", "Power management", "Cooling optimization"],
            "engineering": ["Technical performance", "System reliability", "Innovation"],
            "sustainability": ["ESG reporting", "Energy efficiency", "Carbon footprint"],
            "finance": ["Cost control", "Budget optimization", "ROI measurement"],
        }

        owned_pains = []
        combined_text = f"{title_lower} {bio_lower}"

        for domain, pains in pain_mapping.items():
            if domain in combined_text:
                owned_pains.extend(pains)

        return list(set(owned_pains))  # Remove duplicates

    def _assess_champion_potential(self, title_lower: str, primary_role: MEDDICRole) -> float:
        """Assess likelihood to become a champion (0-100)"""
        champion_scores = {
            MEDDICRole.CHAMPION: 85,
            MEDDICRole.IDENTIFY_PAIN: 70,
            MEDDICRole.USER: 60,
            MEDDICRole.DECISION_CRITERIA: 50,
            MEDDICRole.METRICS_OWNER: 45,
            MEDDICRole.INFLUENCER: 40,
            MEDDICRole.ECONOMIC_BUYER: 30,  # Usually too senior to champion
            MEDDICRole.DECISION_MAKER: 25,  # Usually too senior to champion
        }

        return champion_scores.get(primary_role, 40)

    def _get_engagement_strategy(self, primary_role: MEDDICRole) -> str:
        """Get engagement strategy for the role"""
        strategies = {
            MEDDICRole.METRICS_OWNER: "Lead with quantifiable outcomes and ROI metrics",
            MEDDICRole.ECONOMIC_BUYER: "Focus on business impact and strategic value",
            MEDDICRole.DECISION_MAKER: "Executive briefing on competitive advantage",
            MEDDICRole.DECISION_CRITERIA: "Deep dive on technical capabilities and requirements",
            MEDDICRole.IDENTIFY_PAIN: "Discovery-focused conversations on current challenges",
            MEDDICRole.CHAMPION: "Enable with proof points and internal selling materials",
            MEDDICRole.INFLUENCER: "Thought leadership and technical credibility building",
            MEDDICRole.USER: "Focus on day-to-day benefits and ease of use",
        }
        return strategies.get(primary_role, "Relationship building and needs discovery")

    def _get_key_value_props(self, primary_role: MEDDICRole) -> List[str]:
        """Get key value propositions for the role"""
        value_props = {
            MEDDICRole.METRICS_OWNER: [
                "Real-time visibility",
                "Accurate reporting",
                "Predictive insights",
            ],
            MEDDICRole.ECONOMIC_BUYER: [
                "Cost reduction",
                "Risk mitigation",
                "Operational efficiency",
            ],
            MEDDICRole.DECISION_MAKER: [
                "Competitive advantage",
                "Strategic differentiation",
                "Innovation leadership",
            ],
            MEDDICRole.DECISION_CRITERIA: [
                "Technical superiority",
                "Integration capabilities",
                "Scalability",
            ],
            MEDDICRole.IDENTIFY_PAIN: ["Problem solving", "Pain relief", "Process improvement"],
            MEDDICRole.CHAMPION: [
                "Career advancement",
                "Problem solving recognition",
                "Innovation credit",
            ],
            MEDDICRole.INFLUENCER: [
                "Technical excellence",
                "Industry recognition",
                "Thought leadership",
            ],
            MEDDICRole.USER: ["Ease of use", "Time savings", "Better work experience"],
        }
        return value_props.get(primary_role, ["Value demonstration", "Relationship building"])

    def _get_potential_objections(self, primary_role: MEDDICRole) -> List[str]:
        """Get potential objections for the role"""
        objections = {
            MEDDICRole.METRICS_OWNER: [
                "ROI timeframe",
                "Data accuracy concerns",
                "Integration complexity",
            ],
            MEDDICRole.ECONOMIC_BUYER: [
                "Budget constraints",
                "Competitive solutions",
                "Implementation risk",
            ],
            MEDDICRole.DECISION_MAKER: ["Strategic fit", "Vendor stability", "Market timing"],
            MEDDICRole.DECISION_CRITERIA: [
                "Technical requirements",
                "Integration challenges",
                "Support quality",
            ],
            MEDDICRole.IDENTIFY_PAIN: [
                "Solution fit",
                "Implementation disruption",
                "Training requirements",
            ],
            MEDDICRole.CHAMPION: ["Internal politics", "Change resistance", "Resource constraints"],
            MEDDICRole.INFLUENCER: [
                "Technical concerns",
                "Competitive preference",
                "Status quo bias",
            ],
            MEDDICRole.USER: ["Usability concerns", "Training time", "Workflow disruption"],
        }
        return objections.get(primary_role, ["General skepticism", "Status quo preference"])
