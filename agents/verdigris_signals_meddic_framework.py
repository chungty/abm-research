#!/usr/bin/env python3
"""
Verdigris Signals-Specific MEDDIC Framework
Data center power monitoring decision process based on industry research
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PersonaType(Enum):
    """Data center power monitoring personas based on research"""

    CHAMPION = "champion"
    ECONOMIC_BUYER = "economic_buyer"
    TECHNICAL_EVALUATOR = "technical_evaluator"
    END_USER = "end_user"
    INFLUENCER = "influencer"
    BLOCKER = "blocker"


@dataclass
class VerdigrisSignalsPersona:
    """Persona definition for Verdigris Signals MEDDIC"""

    name: str
    persona_type: PersonaType
    title_patterns: List[str]
    responsibilities: List[str]
    pain_points: List[str]
    value_props: List[str]
    engagement_approach: str
    buying_power_score: int  # 0-100
    influence_score: int  # 0-100


class VerdigrisSignalsMEDDIC:
    """MEDDIC framework specifically for Verdigris Signals power monitoring solution"""

    def __init__(self):
        self.personas = self._build_signals_personas()
        self.decision_criteria = self._build_decision_criteria()
        self.buying_process = self._build_buying_process()

    def _build_signals_personas(self) -> Dict[str, VerdigrisSignalsPersona]:
        """Build personas based on data center power monitoring research"""

        return {
            # CHAMPION: The person who will advocate internally for Verdigris Signals
            "facilities_manager": VerdigrisSignalsPersona(
                name="Data Center Facilities Manager / Critical Facilities Engineer",
                persona_type=PersonaType.CHAMPION,
                title_patterns=[
                    "Data Center Facilities Manager",
                    "Critical Facilities Engineer",
                    "Facilities Manager",
                    "Data Center Manager",
                    "Critical Infrastructure Manager",
                ],
                responsibilities=[
                    "Operating and managing critical power distribution systems",
                    "Managing monitoring systems for electrical infrastructure",
                    "Ensuring uptime and preventing power-related outages",
                    "Day-to-day oversight of power tracking via DCIM/BMS tools",
                ],
                pain_points=[
                    "Manual power tracking causing errors and inefficiency",
                    "Reactive maintenance instead of preventive",
                    "Difficulty optimizing load distribution to avoid overloads",
                    "Limited visibility into power anomalies before they cause issues",
                ],
                value_props=[
                    "Real-time power monitoring prevents outages",
                    "Predictive analytics enable preventive maintenance",
                    "Automated anomaly detection reduces manual oversight",
                    "Circuit-level visibility optimizes load distribution",
                ],
                engagement_approach="Focus on operational efficiency and uptime protection. Share case studies of prevented outages and maintenance cost savings.",
                buying_power_score=70,  # Can influence but usually needs approval
                influence_score=95,  # Highest influence as direct user
            ),
            # ECONOMIC BUYER: The person with budget authority
            "operations_director": VerdigrisSignalsPersona(
                name="Director of Data Center Operations / VP Infrastructure",
                persona_type=PersonaType.ECONOMIC_BUYER,
                title_patterns=[
                    "Director of Data Center Operations",
                    "VP Infrastructure",
                    "VP IT Infrastructure",
                    "Operations Director",
                    "Director Infrastructure",
                    "VP Operations",
                ],
                responsibilities=[
                    "Budget responsibility for data center infrastructure",
                    "Strategic decisions about monitoring tools and DCIM systems",
                    "Building business cases for infrastructure investments",
                    "Getting executive approval for operational tools",
                ],
                pain_points=[
                    "Need to justify ROI for monitoring tool investments",
                    "Pressure to improve PUE and energy efficiency",
                    "Risk of power-related downtime affecting SLAs",
                    "Balancing OpEx/CapEx for monitoring solutions",
                ],
                value_props=[
                    "ROI through prevented outages and efficiency gains",
                    "PUE improvement via better power optimization",
                    "Risk mitigation for power-related downtime",
                    "Cost justification through predictive maintenance savings",
                ],
                engagement_approach="Lead with business case and ROI. Quantify risk reduction and cost savings. Position as strategic infrastructure investment.",
                buying_power_score=100,  # Final budget authority
                influence_score=85,  # High influence on buying decision
            ),
            # TECHNICAL EVALUATOR: The person who will evaluate the solution
            "operations_manager": VerdigrisSignalsPersona(
                name="Operations Manager / Capacity Engineer",
                persona_type=PersonaType.TECHNICAL_EVALUATOR,
                title_patterns=[
                    "Operations Manager",
                    "Capacity Engineer",
                    "Data Center Operations Manager",
                    "Facilities Operations Manager",
                    "Critical Systems Manager",
                ],
                responsibilities=[
                    "Overseeing major facility equipment operations",
                    "Analyzing trends in power consumption and cooling needs",
                    "Ensuring efficient operations and future scalability",
                    "Technical evaluation of monitoring solutions",
                ],
                pain_points=[
                    "Difficulty tracking power trends for capacity planning",
                    "Manual analysis of power consumption data",
                    "Reactive approach to power and cooling optimization",
                    "Limited visibility into future capacity needs",
                ],
                value_props=[
                    "Advanced analytics for capacity planning",
                    "Trend analysis for power consumption optimization",
                    "Automated reporting for operational efficiency",
                    "Predictive insights for scaling decisions",
                ],
                engagement_approach="Technical demos focusing on analytics capabilities. Show trend analysis and capacity planning features.",
                buying_power_score=60,  # Can recommend but needs approval
                influence_score=80,  # Strong technical influence
            ),
            # END USER: The hands-on operators
            "facilities_engineer": VerdigrisSignalsPersona(
                name="Facilities Engineer / Data Center Technician",
                persona_type=PersonaType.END_USER,
                title_patterns=[
                    "Facilities Engineer",
                    "Data Center Technician",
                    "Critical Facilities Technician",
                    "Infrastructure Engineer",
                    "Facilities Technician",
                    "Data Center Engineer",
                ],
                responsibilities=[
                    "Continuous monitoring of power usage in real time",
                    "Responding to power anomaly alerts",
                    "Day-to-day management of intelligent PDUs and sensors",
                    "First responder to power-related incidents",
                ],
                pain_points=[
                    "Getting overwhelmed by false alerts from monitoring systems",
                    "Difficulty prioritizing which power issues need immediate attention",
                    "Manual processes for tracking power trends",
                    "Limited tools for proactive power management",
                ],
                value_props=[
                    "Smart alerting reduces false positives",
                    "Priority-based alert system for quick response",
                    "Automated power trend tracking",
                    "Proactive anomaly detection prevents emergencies",
                ],
                engagement_approach="Focus on day-to-day operational benefits. Show how the tool makes their job easier and more effective.",
                buying_power_score=20,  # Little buying power
                influence_score=60,  # Moderate influence through feedback
            ),
            # CHAMPION (Alternative): For GPU-heavy environments
            "capacity_engineer": VerdigrisSignalsPersona(
                name="Capacity Planning Engineer / Energy Specialist",
                persona_type=PersonaType.CHAMPION,
                title_patterns=[
                    "Capacity Engineer",
                    "Energy Specialist",
                    "Capacity Planning Engineer",
                    "Power Engineer",
                    "Energy Manager",
                    "Sustainability Engineer",
                ],
                responsibilities=[
                    "Optimizing power and cooling for high-density workloads (GPU)",
                    "Long-term capacity planning for power infrastructure",
                    "Energy efficiency and sustainability initiatives",
                    "Power trend analysis for future scaling",
                ],
                pain_points=[
                    "Extreme power density from GPU workloads",
                    "Difficulty predicting power needs for AI infrastructure",
                    "Energy efficiency pressure from sustainability goals",
                    "Complex cooling optimization for high-power equipment",
                ],
                value_props=[
                    "GPU-specific power monitoring and optimization",
                    "Predictive capacity planning for AI workloads",
                    "Energy efficiency optimization for sustainability goals",
                    "Advanced cooling optimization through power insights",
                ],
                engagement_approach="Focus on AI/GPU use cases. Share high-density monitoring examples and sustainability ROI.",
                buying_power_score=60,  # Can influence budget decisions
                influence_score=90,  # High influence in GPU-focused environments
            ),
            # POTENTIAL BLOCKER: Legacy system advocates
            "dcim_administrator": VerdigrisSignalsPersona(
                name="DCIM Administrator / Existing Tool Manager",
                persona_type=PersonaType.BLOCKER,
                title_patterns=[
                    "DCIM Administrator",
                    "Systems Administrator",
                    "IT Manager",
                    "Network Operations Manager",
                    "Infrastructure Administrator",
                ],
                responsibilities=[
                    "Managing existing DCIM or monitoring systems",
                    "Maintaining current operational workflows",
                    "Ensuring continuity of existing monitoring processes",
                    "Training and supporting current tool usage",
                ],
                pain_points=[
                    "Concern about disrupting existing workflows",
                    "Investment in current system training and processes",
                    "Integration complexity with existing tools",
                    "Change management for operational teams",
                ],
                value_props=[
                    "Integration capabilities with existing DCIM systems",
                    "Migration path that preserves existing workflows",
                    "Enhanced capabilities that build on current tools",
                    "Training and change management support",
                ],
                engagement_approach="Position as enhancement rather than replacement. Show integration capabilities and smooth migration path.",
                buying_power_score=40,  # Can influence through resistance
                influence_score=50,  # Moderate influence through operational concerns
            ),
        }

    def _build_decision_criteria(self) -> Dict[str, Dict]:
        """Build decision criteria based on data center power monitoring research"""

        return {
            "technical_requirements": {
                "real_time_monitoring": {
                    "importance": "critical",
                    "description": "Continuous power monitoring with instant anomaly detection",
                    "verdigris_advantage": "Circuit-level real-time monitoring with sub-second resolution",
                },
                "predictive_analytics": {
                    "importance": "high",
                    "description": "AI-powered prediction of power component failures",
                    "verdigris_advantage": "ML models trained on power signatures for failure prediction",
                },
                "integration_capabilities": {
                    "importance": "high",
                    "description": "Integration with existing DCIM and BMS systems",
                    "verdigris_advantage": "API-first architecture with DCIM integrations",
                },
                "alerting_system": {
                    "importance": "critical",
                    "description": "Configurable alerts with priority levels",
                    "verdigris_advantage": "Smart alerting that reduces false positives",
                },
            },
            "business_requirements": {
                "roi_justification": {
                    "importance": "critical",
                    "description": "Clear ROI through outage prevention and efficiency gains",
                    "verdigris_advantage": "Quantified ROI through prevented downtime and energy savings",
                },
                "scalability": {
                    "importance": "high",
                    "description": "Solution that grows with data center expansion",
                    "verdigris_advantage": "Cloud-based solution that scales automatically",
                },
                "budget_fit": {
                    "importance": "critical",
                    "description": "Fits within OpEx/CapEx budget constraints",
                    "verdigris_advantage": "Subscription model that fits OpEx budgets",
                },
            },
        }

    def _build_buying_process(self) -> Dict[str, Dict]:
        """Build typical buying process for data center monitoring tools"""

        return {
            "awareness": {
                "stage_description": "Problem recognition and solution awareness",
                "key_personas": ["facilities_manager", "operations_manager"],
                "typical_triggers": [
                    "Power-related outage or near-miss incident",
                    "Manual power tracking causing operational issues",
                    "New high-density equipment (GPU) deployment",
                    "Executive pressure for better energy efficiency",
                ],
                "verdigris_actions": [
                    "Share relevant case studies and ROI examples",
                    "Provide industry benchmarking data",
                    "Offer power monitoring assessment",
                ],
            },
            "consideration": {
                "stage_description": "Evaluating solution options and building business case",
                "key_personas": ["operations_director", "facilities_manager"],
                "typical_activities": [
                    "Researching available monitoring solutions",
                    "Building ROI business case for management",
                    "Identifying budget sources and approval process",
                    "Getting stakeholder buy-in for evaluation",
                ],
                "verdigris_actions": [
                    "Provide ROI calculator and business case template",
                    "Share customer success stories from similar environments",
                    "Offer executive briefing materials",
                ],
            },
            "evaluation": {
                "stage_description": "Technical evaluation and vendor selection",
                "key_personas": ["operations_manager", "facilities_engineer"],
                "typical_activities": [
                    "Technical demos and proof-of-concept trials",
                    "Integration testing with existing systems",
                    "Reference customer calls",
                    "Pricing and contract negotiations",
                ],
                "verdigris_actions": [
                    "Provide technical demo focused on their use cases",
                    "Offer pilot program in limited area",
                    "Connect with reference customers",
                    "Provide integration documentation",
                ],
            },
            "purchase": {
                "stage_description": "Final approval and procurement",
                "key_personas": ["operations_director"],
                "typical_activities": [
                    "Final executive approval and budget allocation",
                    "Legal review and contract execution",
                    "Implementation planning and timeline",
                    "Training and change management planning",
                ],
                "verdigris_actions": [
                    "Support final business case presentation",
                    "Provide implementation timeline and milestones",
                    "Offer training and change management support",
                ],
            },
        }

    def classify_contact(self, contact: Dict) -> Dict:
        """Classify a contact into MEDDIC personas based on title and role"""

        title = (contact.get("title") or "").lower()
        name = (contact.get("name") or "").lower()

        # Score each persona match
        persona_scores = {}

        for persona_key, persona in self.personas.items():
            score = 0

            # Check title patterns
            for pattern in persona.title_patterns:
                pattern_words = pattern.lower().split()
                title_words = title.split()

                # Exact match gets full points
                if pattern.lower() == title:
                    score += 100
                    break

                # Partial word matches
                matching_words = set(pattern_words) & set(title_words)
                if matching_words:
                    score += (len(matching_words) / len(pattern_words)) * 80

                # Key role indicators
                if "director" in pattern_words and "director" in title_words:
                    score += 20
                if "manager" in pattern_words and "manager" in title_words:
                    score += 15
                if "engineer" in pattern_words and "engineer" in title_words:
                    score += 10

            # Bonus for specific domain keywords
            domain_keywords = [
                "facilities",
                "infrastructure",
                "operations",
                "critical",
                "power",
                "data center",
            ]
            for keyword in domain_keywords:
                if keyword in title:
                    score += 5

            persona_scores[persona_key] = score

        # Find best match
        best_persona_key = max(persona_scores, key=persona_scores.get)
        best_score = persona_scores[best_persona_key]
        best_persona = self.personas[best_persona_key]

        # Classification result
        classification = {
            "contact": contact,
            "primary_persona": {
                "key": best_persona_key,
                "name": best_persona.name,
                "type": best_persona.persona_type.value,
                "match_score": best_score,
                "buying_power_score": best_persona.buying_power_score,
                "influence_score": best_persona.influence_score,
            },
            "all_persona_scores": persona_scores,
            "engagement_strategy": {
                "approach": best_persona.engagement_approach,
                "value_props": best_persona.value_props,
                "pain_points": best_persona.pain_points,
            },
            "confidence": "high" if best_score >= 80 else "medium" if best_score >= 40 else "low",
        }

        return classification


def test_meddic_classification():
    """Test MEDDIC classification with sample contacts"""

    print("🎯 TESTING VERDIGRIS SIGNALS MEDDIC CLASSIFICATION")
    print("=" * 60)

    meddic = VerdigrisSignalsMEDDIC()

    # Test contacts
    test_contacts = [
        {"name": "Lorena Acosta", "title": "Director of Operations"},
        {"name": "John Smith", "title": "Data Center Facilities Manager"},
        {"name": "Sarah Johnson", "title": "VP Infrastructure"},
        {"name": "Mike Chen", "title": "Critical Facilities Engineer"},
        {"name": "Lisa Park", "title": "Capacity Engineer"},
    ]

    for contact in test_contacts:
        classification = meddic.classify_contact(contact)

        print(f"\n👤 {contact['name']} - {contact['title']}")
        print(f"   🎯 Primary Persona: {classification['primary_persona']['name']}")
        print(f"   📊 Persona Type: {classification['primary_persona']['type']}")
        print(f"   💪 Buying Power: {classification['primary_persona']['buying_power_score']}/100")
        print(f"   🎭 Influence: {classification['primary_persona']['influence_score']}/100")
        print(f"   🔍 Match Confidence: {classification['confidence']}")
        print(f"   💡 Engagement: {classification['engagement_strategy']['approach'][:60]}...")

    return True


if __name__ == "__main__":
    test_meddic_classification()
