#!/usr/bin/env python3
"""
Partnership Classification System for ABM Research

Distinguishes between Direct ICP targets, Strategic Partners, and Referral Partners
to optimize sales approach and resource allocation.

Example:
- Direct ICP: Companies with GPU datacenters needing power monitoring (target customers)
- Strategic Partners: AI infrastructure providers like Groq (technology partners)
- Referral Partners: Consultants, integrators who serve our ICP (referral sources)
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PartnershipType(Enum):
    """Types of business relationships for account classification"""
    DIRECT_ICP = "direct_icp"           # Target customers with power monitoring needs
    STRATEGIC_PARTNER = "strategic_partner"     # Technology/product partners
    REFERRAL_PARTNER = "referral_partner"       # Companies that can refer customers
    COMPETITIVE = "competitive"                 # Direct competitors
    VENDOR = "vendor"                          # Companies we buy from
    UNKNOWN = "unknown"                        # Needs further classification


class IndustryCategory(Enum):
    """Industry categories for partnership classification"""
    DATA_CENTER_OPERATOR = "data_center_operator"       # Direct ICP
    CLOUD_PROVIDER = "cloud_provider"                   # Strategic partner potential
    AI_INFRASTRUCTURE = "ai_infrastructure"             # Strategic partner potential
    HARDWARE_VENDOR = "hardware_vendor"                 # Strategic partner potential
    SOFTWARE_VENDOR = "software_vendor"                 # Strategic partner potential
    SYSTEMS_INTEGRATOR = "systems_integrator"           # Referral partner potential
    CONSULTANT = "consultant"                           # Referral partner potential
    POWER_MONITORING = "power_monitoring"               # Competitive
    FACILITY_MANAGEMENT = "facility_management"         # Competitive
    OTHER = "other"


@dataclass
class PartnershipClassification:
    """Result of partnership classification analysis"""
    partnership_type: PartnershipType
    industry_category: IndustryCategory
    confidence_score: float  # 0-100
    reasoning: str
    recommended_approach: str
    potential_value: str     # High, Medium, Low
    next_actions: List[str]


class PartnershipClassifier:
    """
    Classifies companies into partnership categories based on business model,
    industry, and strategic value for Verdigris power monitoring solutions.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Direct ICP indicators (companies that need power monitoring)
        self.direct_icp_indicators = {
            "business_models": [
                "data center operator", "colocation provider", "cloud provider",
                "gpu datacenter", "hyperscale operator", "edge computing provider"
            ],
            "infrastructure_keywords": [
                "gpu cluster", "nvidia h100", "nvidia a100", "ai training",
                "high performance computing", "hpc", "supercomputing",
                "data center", "datacenter", "server farm", "compute infrastructure"
            ],
            "power_indicators": [
                "high power density", "power consumption", "energy costs",
                "power efficiency", "power monitoring needs", "ups systems",
                "power distribution", "energy management"
            ]
        }

        # Strategic partner indicators (companies we can partner with)
        self.strategic_partner_indicators = {
            "ai_infrastructure": [
                "ai inference", "gpu as a service", "ml platform", "ai training platform",
                "compute as a service", "ai cloud", "inference api"
            ],
            "hardware_vendors": [
                "nvidia", "amd", "intel", "server manufacturer", "gpu vendor",
                "storage vendor", "networking equipment", "data center equipment"
            ],
            "software_platforms": [
                "dcim", "infrastructure management", "cloud management platform",
                "monitoring platform", "analytics platform", "iot platform"
            ],
            "cloud_services": [
                "aws", "azure", "google cloud", "oracle cloud", "alibaba cloud",
                "cloud infrastructure", "cloud platform", "managed services"
            ]
        }

        # Referral partner indicators (companies that serve our ICP)
        self.referral_partner_indicators = {
            "systems_integrators": [
                "systems integrator", "si", "technology integrator", "it services",
                "implementation partner", "consulting services", "managed services provider"
            ],
            "consultants": [
                "data center consulting", "infrastructure consulting", "energy consulting",
                "facilities consulting", "it consulting", "digital transformation"
            ],
            "service_providers": [
                "data center services", "facility management", "maintenance services",
                "installation services", "support services", "managed infrastructure"
            ]
        }

        # Competitive indicators (direct competitors)
        self.competitive_indicators = [
            "power monitoring", "energy monitoring", "power analytics",
            "power management software", "dcim", "facility monitoring",
            "energy efficiency software", "power optimization", "verdigris"
        ]

    def classify_partnership(self, company_data: Dict) -> PartnershipClassification:
        """
        Classify a company's partnership potential based on their business model,
        industry, and infrastructure.

        Args:
            company_data: Dictionary containing company information including:
                - name, domain, business_model, industry
                - physical_infrastructure, tech_stack, recent_announcements
                - employee_count, growth_stage, funding_info

        Returns:
            PartnershipClassification with recommended approach
        """
        self.logger.info(f"🔍 Classifying partnership potential for {company_data.get('name', 'Unknown')}")

        company_name = company_data.get('name', '').lower()
        business_model = company_data.get('business_model', '').lower()
        infrastructure = company_data.get('physical_infrastructure', '').lower()
        tech_stack = company_data.get('tech_stack', '').lower()
        announcements = company_data.get('recent_announcements', '').lower()

        # Combine all text for analysis
        combined_text = f"{company_name} {business_model} {infrastructure} {tech_stack} {announcements}"

        # Score each partnership type
        direct_icp_score = self._score_direct_icp(combined_text, company_data)
        strategic_partner_score = self._score_strategic_partner(combined_text, company_data)
        referral_partner_score = self._score_referral_partner(combined_text, company_data)
        competitive_score = self._score_competitive(combined_text, company_data)

        # Determine best classification
        scores = {
            PartnershipType.DIRECT_ICP: direct_icp_score,
            PartnershipType.STRATEGIC_PARTNER: strategic_partner_score,
            PartnershipType.REFERRAL_PARTNER: referral_partner_score,
            PartnershipType.COMPETITIVE: competitive_score
        }

        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]

        # If no clear winner, mark as unknown
        if confidence < 30:
            best_type = PartnershipType.UNKNOWN
            confidence = 0

        # Determine industry category
        industry_category = self._determine_industry_category(combined_text, company_data)

        # Generate classification result
        classification = self._generate_classification_result(
            best_type, industry_category, confidence, company_data
        )

        self.logger.info(f"✅ Classified as {best_type.value} with {confidence:.1f}% confidence")
        return classification

    def _score_direct_icp(self, text: str, company_data: Dict) -> float:
        """Score likelihood of being a direct ICP target customer"""
        score = 0.0

        # Check business model indicators
        for indicator in self.direct_icp_indicators["business_models"]:
            if indicator in text:
                score += 25

        # Check infrastructure indicators (strong signal)
        for indicator in self.direct_icp_indicators["infrastructure_keywords"]:
            if indicator in text:
                score += 20

        # Check power indicators (strongest signal)
        for indicator in self.direct_icp_indicators["power_indicators"]:
            if indicator in text:
                score += 30

        # High employee count suggests infrastructure scale
        employee_count = company_data.get('employee_count', 0) or 0
        if employee_count and employee_count > 1000:
            score += 10
        elif employee_count and employee_count > 500:
            score += 5

        return min(score, 100)

    def _score_strategic_partner(self, text: str, company_data: Dict) -> float:
        """Score likelihood of being a strategic partner"""
        score = 0.0

        # AI infrastructure providers (like Groq)
        for indicator in self.strategic_partner_indicators["ai_infrastructure"]:
            if indicator in text:
                score += 30

        # Hardware vendors
        for indicator in self.strategic_partner_indicators["hardware_vendors"]:
            if indicator in text:
                score += 25

        # Software platforms
        for indicator in self.strategic_partner_indicators["software_platforms"]:
            if indicator in text:
                score += 20

        # Cloud services
        for indicator in self.strategic_partner_indicators["cloud_services"]:
            if indicator in text:
                score += 20

        # Growth stage companies are often better partners
        growth_stage = company_data.get('growth_stage', '').lower()
        if growth_stage in ['growth', 'scale-up']:
            score += 10

        return min(score, 100)

    def _score_referral_partner(self, text: str, company_data: Dict) -> float:
        """Score likelihood of being a referral partner"""
        score = 0.0

        # Systems integrators
        for indicator in self.referral_partner_indicators["systems_integrators"]:
            if indicator in text:
                score += 25

        # Consultants
        for indicator in self.referral_partner_indicators["consultants"]:
            if indicator in text:
                score += 25

        # Service providers
        for indicator in self.referral_partner_indicators["service_providers"]:
            if indicator in text:
                score += 20

        return min(score, 100)

    def _score_competitive(self, text: str, company_data: Dict) -> float:
        """Score likelihood of being competitive"""
        score = 0.0

        for indicator in self.competitive_indicators:
            if indicator in text:
                score += 30

        return min(score, 100)

    def _determine_industry_category(self, text: str, company_data: Dict) -> IndustryCategory:
        """Determine the industry category based on company data"""

        # Check for specific industry indicators
        if any(term in text for term in ["data center operator", "datacenter operator", "colocation"]):
            return IndustryCategory.DATA_CENTER_OPERATOR

        if any(term in text for term in ["aws", "azure", "google cloud", "cloud provider"]):
            return IndustryCategory.CLOUD_PROVIDER

        if any(term in text for term in ["ai inference", "gpu as a service", "ai platform", "ml platform"]):
            return IndustryCategory.AI_INFRASTRUCTURE

        if any(term in text for term in ["nvidia", "amd", "server manufacturer", "hardware vendor"]):
            return IndustryCategory.HARDWARE_VENDOR

        if any(term in text for term in ["dcim", "monitoring platform", "software platform"]):
            return IndustryCategory.SOFTWARE_VENDOR

        if any(term in text for term in ["systems integrator", "si", "implementation partner"]):
            return IndustryCategory.SYSTEMS_INTEGRATOR

        if any(term in text for term in ["consulting", "consultant", "advisory"]):
            return IndustryCategory.CONSULTANT

        if any(term in text for term in ["power monitoring", "energy monitoring", "facility monitoring"]):
            return IndustryCategory.POWER_MONITORING

        return IndustryCategory.OTHER

    def _generate_classification_result(self, partnership_type: PartnershipType,
                                      industry_category: IndustryCategory,
                                      confidence: float, company_data: Dict) -> PartnershipClassification:
        """Generate comprehensive classification result with recommendations"""

        company_name = company_data.get('name', 'Unknown')

        # Generate reasoning and recommendations based on type
        if partnership_type == PartnershipType.DIRECT_ICP:
            reasoning = f"{company_name} shows strong indicators of needing power monitoring solutions"
            approach = "Direct sales engagement focusing on power efficiency and cost reduction"
            value = "High" if confidence > 70 else "Medium"
            actions = [
                "Schedule discovery call with facilities/infrastructure team",
                "Prepare power monitoring ROI analysis",
                "Identify key decision makers for infrastructure purchases"
            ]

        elif partnership_type == PartnershipType.STRATEGIC_PARTNER:
            reasoning = f"{company_name} serves companies that likely need power monitoring solutions"
            approach = "Partnership development - co-marketing and referral programs"
            value = "Medium" if confidence > 60 else "Low"
            actions = [
                "Reach out to business development team",
                "Propose joint go-to-market strategy",
                "Explore integration opportunities"
            ]

        elif partnership_type == PartnershipType.REFERRAL_PARTNER:
            reasoning = f"{company_name} provides services to companies that need power monitoring"
            approach = "Channel partnership - referral commission program"
            value = "Medium" if confidence > 50 else "Low"
            actions = [
                "Contact channel/partner team",
                "Develop referral incentive structure",
                "Create partner enablement materials"
            ]

        elif partnership_type == PartnershipType.COMPETITIVE:
            reasoning = f"{company_name} appears to compete in power monitoring space"
            approach = "Competitive intelligence - monitor pricing and positioning"
            value = "Low"
            actions = [
                "Add to competitive tracking list",
                "Monitor product announcements",
                "Analyze competitive positioning"
            ]

        else:  # UNKNOWN
            reasoning = f"{company_name} requires further analysis to determine partnership potential"
            approach = "Additional research needed before engagement"
            value = "Unknown"
            actions = [
                "Conduct deeper company research",
                "Identify key business focus areas",
                "Reassess after gathering more data"
            ]

        return PartnershipClassification(
            partnership_type=partnership_type,
            industry_category=industry_category,
            confidence_score=confidence,
            reasoning=reasoning,
            recommended_approach=approach,
            potential_value=value,
            next_actions=actions
        )

    def classify_from_account_intelligence(self, account_intel: Dict) -> PartnershipClassification:
        """
        Convenience method to classify partnership from AccountIntelligenceEngine output

        Args:
            account_intel: Output from AccountIntelligenceEngine.convert_to_notion_format()

        Returns:
            PartnershipClassification
        """
        # Map account intelligence to company data format
        company_data = {
            'name': account_intel.get('name', ''),
            'business_model': account_intel.get('Growth Stage', ''),
            'physical_infrastructure': account_intel.get('Physical Infrastructure', ''),
            'tech_stack': account_intel.get('Physical Infrastructure', ''),  # Same field in new format
            'recent_announcements': account_intel.get('Recent Announcements', ''),
            'employee_count': 0,  # Would need to be passed separately
            'growth_stage': account_intel.get('Growth Stage', '')
        }

        return self.classify_partnership(company_data)


# Export singleton instance for easy importing
partnership_classifier = PartnershipClassifier()