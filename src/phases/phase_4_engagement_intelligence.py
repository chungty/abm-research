"""
Phase 4: Engagement Intelligence (Diagnostic)

Generates actionable insights for human review, not automated outreach.
For contacts scoring >70 after Phase 3 enrichment.
"""
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from ..models.account import Account
from ..models.contact import Contact, ResearchStatus
from ..models.trigger_event import TriggerEvent
from ..models.meddic_framework import MEDDICRole
from ..utils.data_classification import DataClassification, DataSource
from ..config.settings import load_lead_scoring_config

logger = logging.getLogger(__name__)


class ConnectionPathway(Enum):
    """Types of connection pathways to contacts"""
    MUTUAL_CONNECTIONS = "mutual_connections"
    SHARED_GROUPS = "shared_groups"
    INDUSTRY_EVENTS = "industry_events"
    CONTENT_ENGAGEMENT = "content_engagement"
    NO_DIRECT_PATH = "no_direct_path"


@dataclass
class ProblemMapping:
    """Problems a contact likely owns based on role and context"""
    contact_name: str
    likely_problems: List[str]
    confidence_level: str  # High, Medium, Low
    source_rationale: str


@dataclass
class ContentThemeAnalysis:
    """Content themes the contact values"""
    contact_name: str
    valued_themes: List[str]
    engagement_frequency: str
    content_quality: str  # High, Medium, Low engagement
    source: str  # LinkedIn activity, role assumption, etc.


@dataclass
class ConnectionDiagnostic:
    """Connection pathway analysis"""
    contact_name: str
    pathway_type: ConnectionPathway
    pathway_description: str
    mutual_connections_count: int
    shared_groups: List[str]
    confidence: str  # High, Medium, Low


@dataclass
class ValueAddIdea:
    """Specific value-add opportunity for engagement"""
    contact_name: str
    idea_type: str  # Case study, Educational content, Introduction, etc.
    description: str
    verdigris_asset: str  # Which content/resource to use
    timing_rationale: str
    confidence: str


class EngagementIntelligenceAnalyzer:
    """Phase 4: Generates engagement intelligence for high-scoring contacts"""

    def __init__(self):
        self.scoring_config = load_lead_scoring_config()
        self.data_classification = DataClassification()

    async def analyze_engagement_intelligence(self, account: Account) -> Dict[str, Any]:
        """
        Generate comprehensive engagement intelligence for high-scoring contacts

        Args:
            account: Account with Phase 3 enriched contacts

        Returns:
            Dictionary with engagement intelligence data
        """
        logger.info(f"🔍 Phase 4: Analyzing engagement intelligence for {account.name}")

        # Filter high-priority contacts (70+ score)
        high_priority_contacts = self._get_high_priority_contacts(account)

        if not high_priority_contacts:
            logger.warning(f"No contacts scoring 70+ found for {account.name}")
            return self._empty_intelligence_result()

        logger.info(f"📊 Found {len(high_priority_contacts)} high-priority contacts for intelligence analysis")

        # Generate intelligence for each contact
        intelligence_data = {
            'account_name': account.name,
            'analysis_summary': {
                'total_analyzed': len(high_priority_contacts),
                'analysis_date': self.data_classification.get_current_timestamp(),
                'phase_4_complete': False
            },
            'problem_mappings': [],
            'content_analyses': [],
            'connection_diagnostics': [],
            'value_add_ideas': []
        }

        for contact in high_priority_contacts:
            # 1. Map problems they likely own
            problem_mapping = self._analyze_likely_problems(contact, account)
            intelligence_data['problem_mappings'].append(problem_mapping)

            # 2. Identify content themes they value
            content_analysis = self._analyze_content_themes(contact)
            intelligence_data['content_analyses'].append(content_analysis)

            # 3. Diagnose connection pathways
            connection_diagnostic = await self._diagnose_connection_pathways(contact)
            intelligence_data['connection_diagnostics'].append(connection_diagnostic)

            # 4. Generate value-add ideas
            value_ideas = self._generate_value_add_ideas(contact, problem_mapping, content_analysis, account)
            intelligence_data['value_add_ideas'].extend(value_ideas)

            # Mark contact as analyzed
            contact.research_status = ResearchStatus.ANALYZED

        intelligence_data['analysis_summary']['phase_4_complete'] = True
        logger.info(f"✅ Phase 4 engagement intelligence complete for {account.name}")

        return intelligence_data

    def _get_high_priority_contacts(self, account: Account) -> List[Contact]:
        """Get contacts with final scores >= 70"""
        return [
            contact for contact in account.contacts
            if contact.final_lead_score >= 70
            and contact.research_status in [ResearchStatus.ENRICHED, ResearchStatus.ANALYZED]
        ]

    def _analyze_likely_problems(self, contact: Contact, account: Account) -> ProblemMapping:
        """Map problems contact likely owns based on title and seniority"""

        # Load ICP pain points from config
        icp_pain_points = self.scoring_config.get('icp_pain_points', [])

        # Match problems based on title keywords and MEDDIC role
        likely_problems = []
        confidence_level = "Medium"
        rationale_parts = []

        title_lower = contact.title.lower()

        # Role-based problem mapping
        if any(keyword in title_lower for keyword in ['vp', 'head', 'director']):
            # Senior roles: strategic problems
            strategic_problems = [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "Cost reduction mandates",
                "AI workload expansion challenges"
            ]
            likely_problems.extend([p for p in strategic_problems if p in icp_pain_points])
            confidence_level = "High"
            rationale_parts.append("Senior leadership role")

        if any(keyword in title_lower for keyword in ['operations', 'facilities', 'site']):
            # Operational roles: tactical problems
            operational_problems = [
                "Uptime and reliability pressure",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting"
            ]
            likely_problems.extend([p for p in operational_problems if p in icp_pain_points])
            rationale_parts.append("Operations responsibility")

        if any(keyword in title_lower for keyword in ['sustainability', 'esg', 'environmental']):
            # Sustainability roles: ESG problems
            sustainability_problems = [
                "Sustainability and ESG reporting requirements",
                "Energy efficiency and PUE optimization"
            ]
            likely_problems.extend([p for p in sustainability_problems if p in icp_pain_points])
            rationale_parts.append("Sustainability focus")

        # Account trigger events influence problems
        if account.trigger_events:
            for event in account.trigger_events:
                if event.event_type.value in ['expansion', 'ai_workload']:
                    if "AI workload expansion challenges" not in likely_problems:
                        likely_problems.append("AI workload expansion challenges")
                    rationale_parts.append(f"Account {event.event_type.value} trigger")
                elif event.event_type.value == 'energy_pressure':
                    if "Energy efficiency and PUE optimization" not in likely_problems:
                        likely_problems.append("Energy efficiency and PUE optimization")
                    rationale_parts.append("Account energy pressure trigger")

        # If no specific problems found, use role defaults
        if not likely_problems:
            likely_problems = ["Power capacity planning and management", "Uptime and reliability pressure"]
            confidence_level = "Low"
            rationale_parts.append("General data center operations role")

        source_rationale = f"Based on: {', '.join(rationale_parts)}"

        return ProblemMapping(
            contact_name=contact.name,
            likely_problems=likely_problems[:4],  # Limit to top 4
            confidence_level=confidence_level,
            source_rationale=source_rationale
        )

    def _analyze_content_themes(self, contact: Contact) -> ContentThemeAnalysis:
        """Identify content themes contact values"""

        # Use LinkedIn themes if available
        if contact.linkedin_content_themes:
            valued_themes = contact.linkedin_content_themes.copy()
            engagement_frequency = getattr(contact, 'linkedin_activity_level', 'unknown')
            content_quality = self._assess_content_quality(valued_themes)
            source = "LinkedIn activity analysis"
        else:
            # Fallback to role-based assumptions
            valued_themes = self._infer_themes_from_role(contact.title)
            engagement_frequency = "assumed"
            content_quality = "Medium"
            source = "Role-based assumption"

        return ContentThemeAnalysis(
            contact_name=contact.name,
            valued_themes=valued_themes,
            engagement_frequency=engagement_frequency,
            content_quality=content_quality,
            source=source
        )

    def _assess_content_quality(self, themes: List[str]) -> str:
        """Assess quality of content engagement based on themes"""
        verdigris_relevant = ['power', 'energy', 'infrastructure', 'ai', 'sustainability', 'operations']

        relevance_count = sum(1 for theme in themes
                            for keyword in verdigris_relevant
                            if keyword.lower() in theme.lower())

        if relevance_count >= 3:
            return "High"
        elif relevance_count >= 1:
            return "Medium"
        else:
            return "Low"

    def _infer_themes_from_role(self, title: str) -> List[str]:
        """Infer likely content interests based on role"""
        title_lower = title.lower()
        themes = []

        if any(keyword in title_lower for keyword in ['operations', 'facilities']):
            themes.extend(["data center operations", "infrastructure management"])

        if any(keyword in title_lower for keyword in ['sustainability', 'esg']):
            themes.extend(["sustainability", "energy efficiency"])

        if any(keyword in title_lower for keyword in ['infrastructure', 'engineering']):
            themes.extend(["technical architecture", "system reliability"])

        if any(keyword in title_lower for keyword in ['ai', 'cloud', 'hpc']):
            themes.extend(["AI infrastructure", "cloud computing"])

        # Default themes for data center roles
        if not themes:
            themes = ["industry news", "operational efficiency"]

        return themes

    async def _diagnose_connection_pathways(self, contact: Contact) -> ConnectionDiagnostic:
        """Diagnose potential connection pathways"""

        # For now, this is a diagnostic placeholder - in production would:
        # 1. Check LinkedIn mutual connections (if API available)
        # 2. Identify shared groups/associations
        # 3. Look for event attendance overlap

        pathway_type = ConnectionPathway.NO_DIRECT_PATH
        pathway_description = "No direct connections identified in initial scan"
        mutual_connections_count = 0
        shared_groups = []
        confidence = "Medium"

        # Mock analysis based on LinkedIn data
        if hasattr(contact, 'linkedin_network_quality') and contact.linkedin_network_quality:
            pathway_type = ConnectionPathway.MUTUAL_CONNECTIONS
            pathway_description = "High-quality LinkedIn network suggests potential mutual connections"
            mutual_connections_count = 5  # Mock estimate
            confidence = "Medium"

        # Check for industry group potential based on role
        title_lower = contact.title.lower()
        if any(keyword in title_lower for keyword in ['vp', 'director', 'head']):
            shared_groups = ["Data Center Executive Council", "Uptime Institute"]
            if pathway_type == ConnectionPathway.NO_DIRECT_PATH:
                pathway_type = ConnectionPathway.SHARED_GROUPS
                pathway_description = f"Senior role suggests membership in industry groups: {', '.join(shared_groups)}"

        return ConnectionDiagnostic(
            contact_name=contact.name,
            pathway_type=pathway_type,
            pathway_description=pathway_description,
            mutual_connections_count=mutual_connections_count,
            shared_groups=shared_groups,
            confidence=confidence
        )

    def _generate_value_add_ideas(self, contact: Contact, problem_mapping: ProblemMapping,
                                content_analysis: ContentThemeAnalysis, account: Account) -> List[ValueAddIdea]:
        """Generate specific value-add ideas for engagement"""

        ideas = []

        # Idea 1: Problem-solution alignment
        if "AI workload expansion challenges" in problem_mapping.likely_problems:
            ideas.append(ValueAddIdea(
                contact_name=contact.name,
                idea_type="Case Study",
                description="Share Verdigris case study on GPU rack optimization and power monitoring",
                verdigris_asset="GPU Density Case Study",
                timing_rationale="AI infrastructure challenges are timely given market trends",
                confidence="High"
            ))

        if "Energy efficiency and PUE optimization" in problem_mapping.likely_problems:
            ideas.append(ValueAddIdea(
                contact_name=contact.name,
                idea_type="Benchmark Data",
                description="Provide industry PUE benchmarks and optimization strategies",
                verdigris_asset="PUE Optimization Whitepaper",
                timing_rationale="Energy costs are rising industry-wide",
                confidence="High"
            ))

        # Idea 2: Content theme alignment
        if any("sustainability" in theme.lower() for theme in content_analysis.valued_themes):
            ideas.append(ValueAddIdea(
                contact_name=contact.name,
                idea_type="Educational Content",
                description="Share insights on Scope 2 emissions monitoring for data centers",
                verdigris_asset="Sustainability Monitoring Guide",
                timing_rationale="ESG reporting requirements increasing",
                confidence="Medium"
            ))

        # Idea 3: Role tenure based
        if hasattr(contact, 'role_tenure'):
            tenure = contact.role_tenure.lower()
            if any(indicator in tenure for indicator in ['6 months', 'new', 'recent']):
                ideas.append(ValueAddIdea(
                    contact_name=contact.name,
                    idea_type="Relationship Building",
                    description="Focus on educational content and industry insights, not sales",
                    verdigris_asset="Industry Trend Report",
                    timing_rationale="New in role - building credibility phase",
                    confidence="High"
                ))

        # Idea 4: Trigger event based
        if account.trigger_events:
            for event in account.trigger_events:
                if event.relevance_score >= 70:  # High relevance trigger
                    ideas.append(ValueAddIdea(
                        contact_name=contact.name,
                        idea_type="Trigger Response",
                        description=f"Reference their recent {event.event_type.value} and offer relevant insights",
                        verdigris_asset="Relevant Case Study or Benchmark",
                        timing_rationale=f"Recent {event.event_type.value} creates receptive moment",
                        confidence="High"
                    ))
                    break  # Only use one trigger event per contact

        # Ensure at least one idea per contact
        if not ideas:
            ideas.append(ValueAddIdea(
                contact_name=contact.name,
                idea_type="General Outreach",
                description="Share general data center efficiency insights",
                verdigris_asset="Data Center Efficiency Report",
                timing_rationale="Established relationship building",
                confidence="Medium"
            ))

        return ideas[:3]  # Limit to top 3 ideas per contact

    def _empty_intelligence_result(self) -> Dict[str, Any]:
        """Return empty intelligence result structure"""
        return {
            'account_name': 'Unknown',
            'analysis_summary': {
                'total_analyzed': 0,
                'analysis_date': self.data_classification.get_current_timestamp(),
                'phase_4_complete': False
            },
            'problem_mappings': [],
            'content_analyses': [],
            'connection_diagnostics': [],
            'value_add_ideas': []
        }