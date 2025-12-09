#!/usr/bin/env python3
"""
Contact Value Analyzer
Analyzes contact data to identify high-ICP contacts, role patterns, and organizational insights
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

@dataclass
class ContactRole:
    """Contact role analysis"""
    title: str
    department: str
    seniority_level: str  # "C-Suite", "VP", "Director", "Manager", "Individual Contributor"
    buying_influence: str  # "Decision Maker", "Influencer", "Champion", "User", "Gatekeeper"
    verdigris_relevance: float  # 0-1 score for Verdigris solution fit

@dataclass
class ContactValue:
    """Contact value assessment"""
    contact_id: str
    name: str
    icp_fit_score: float
    buying_power_score: float
    engagement_potential: float
    final_value_score: float
    value_tier: str  # "Tier 1", "Tier 2", "Tier 3"
    role_analysis: ContactRole
    engagement_readiness: str  # "Ready", "Warm", "Cold"
    recommended_approach: str

@dataclass
class RolePattern:
    """Organizational role pattern"""
    pattern_name: str
    roles_involved: List[str]
    decision_process: str
    typical_timeline: str
    success_factors: List[str]

@dataclass
class OrganizationalInsight:
    """Company organizational insights"""
    company_name: str
    total_contacts: int
    tier_1_contacts: int
    tier_2_contacts: int
    tier_3_contacts: int
    dominant_departments: List[str]
    decision_makers: List[str]
    champions_identified: List[str]
    organizational_pattern: RolePattern
    buying_committee_completeness: float  # 0-1 score

class ContactValueAnalyzer:
    """
    Analyzes contact value and identifies high-ICP contacts with role patterns
    """

    def __init__(self):
        print("👥 Initializing Contact Value Analyzer")
        print("🎯 Identifying high-ICP contacts and role patterns")

        # Role hierarchy mapping
        self.seniority_levels = {
            'C-Suite': ['CEO', 'CTO', 'CFO', 'COO', 'CHRO', 'Chief', 'President', 'Chairman'],
            'VP': ['VP', 'Vice President', 'SVP', 'EVP'],
            'Director': ['Director', 'Dir', 'Head of'],
            'Manager': ['Manager', 'Mgr', 'Lead', 'Principal'],
            'Individual Contributor': ['Engineer', 'Analyst', 'Specialist', 'Coordinator']
        }

        # Department classification
        self.departments = {
            'Engineering': ['Engineering', 'Development', 'Software', 'Technology', 'DevOps', 'Infrastructure'],
            'Operations': ['Operations', 'Ops', 'Facilities', 'Manufacturing', 'Production'],
            'Finance': ['Finance', 'Financial', 'Accounting', 'Treasury', 'Controller'],
            'Sustainability': ['Sustainability', 'Environmental', 'ESG', 'Green', 'Climate'],
            'Procurement': ['Procurement', 'Purchasing', 'Sourcing', 'Vendor'],
            'IT': ['IT', 'Information Technology', 'Systems', 'Digital'],
            'Energy': ['Energy', 'Power', 'Utilities', 'Grid']
        }

        # Buying influence mapping
        self.buying_influence_rules = {
            'Decision Maker': ['CEO', 'CFO', 'COO', 'VP', 'Director'],
            'Influencer': ['Manager', 'Lead', 'Principal', 'Head'],
            'Champion': ['sustainability', 'energy', 'efficiency'],  # keyword-based
            'User': ['Engineer', 'Analyst', 'Specialist'],
            'Gatekeeper': ['procurement', 'purchasing', 'sourcing']
        }

        # Verdigris solution relevance scoring
        self.verdigris_keywords = {
            'energy_monitoring': ['energy', 'power', 'consumption', 'monitoring'],
            'sustainability': ['sustainability', 'environmental', 'carbon', 'green'],
            'cost_optimization': ['cost', 'savings', 'optimization', 'efficiency'],
            'facilities': ['facilities', 'building', 'infrastructure', 'operations'],
            'data_analytics': ['analytics', 'data', 'insights', 'reporting']
        }

    def analyze_contact_value(self, contacts: List[Dict], company_data: Dict = None) -> Dict:
        """
        Analyze contact value and organizational patterns
        """
        print(f"\n👥 Analyzing value for {len(contacts)} contacts")
        print("=" * 60)

        # Analyze individual contacts
        contact_values = []
        for contact in contacts:
            value_analysis = self._analyze_single_contact_value(contact)
            contact_values.append(value_analysis)

        # Sort by value score
        contact_values.sort(key=lambda x: x.final_value_score, reverse=True)

        # Analyze organizational patterns
        org_insights = self._analyze_organizational_patterns(contact_values, company_data)

        # Generate role patterns
        role_patterns = self._identify_role_patterns(contact_values)

        # Calculate summary metrics
        summary_metrics = self._calculate_summary_metrics(contact_values)

        analysis_result = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_contacts_analyzed': len(contacts),
            'contact_values': [asdict(cv) for cv in contact_values],
            'organizational_insights': asdict(org_insights),
            'role_patterns': [asdict(rp) for rp in role_patterns],
            'summary_metrics': summary_metrics
        }

        self._print_value_analysis(analysis_result)
        return analysis_result

    def _analyze_single_contact_value(self, contact: Dict) -> ContactValue:
        """Analyze value for a single contact"""

        # Extract contact information
        name = contact.get('name', 'Unknown')
        title = contact.get('title', '')

        # Analyze role
        role_analysis = self._analyze_contact_role(contact)

        # Calculate value scores
        icp_fit = contact.get('icp_fit_score', 0) / 100.0 if contact.get('icp_fit_score') else 0.5
        buying_power = contact.get('buying_power_score', 0) / 100.0 if contact.get('buying_power_score') else 0.3
        engagement_potential = contact.get('engagement_potential_score', 0) / 100.0 if contact.get('engagement_potential_score') else 0.4

        # Enhanced value calculation with role weighting
        role_weight = self._calculate_role_weight(role_analysis)
        verdigris_relevance = role_analysis.verdigris_relevance

        # Composite value score
        final_value_score = (
            icp_fit * 0.3 +
            buying_power * 0.25 +
            engagement_potential * 0.2 +
            role_weight * 0.15 +
            verdigris_relevance * 0.1
        )

        # Determine value tier
        if final_value_score >= 0.8:
            value_tier = "Tier 1"
        elif final_value_score >= 0.6:
            value_tier = "Tier 2"
        else:
            value_tier = "Tier 3"

        # Determine engagement readiness
        linkedin_activity = contact.get('linkedin_activity_level', '')
        research_status = contact.get('research_status', '')

        if linkedin_activity == 'High' and research_status == 'Fully Analyzed':
            engagement_readiness = "Ready"
        elif linkedin_activity in ['Medium', 'High'] or research_status in ['Basic Profile', 'Ready for Enrichment']:
            engagement_readiness = "Warm"
        else:
            engagement_readiness = "Cold"

        # Generate recommended approach
        recommended_approach = self._generate_approach_recommendation(
            role_analysis, value_tier, engagement_readiness
        )

        return ContactValue(
            contact_id=contact.get('id', ''),
            name=name,
            icp_fit_score=icp_fit,
            buying_power_score=buying_power,
            engagement_potential=engagement_potential,
            final_value_score=final_value_score,
            value_tier=value_tier,
            role_analysis=role_analysis,
            engagement_readiness=engagement_readiness,
            recommended_approach=recommended_approach
        )

    def _analyze_contact_role(self, contact: Dict) -> ContactRole:
        """Analyze contact role and influence"""

        title = contact.get('title', '').lower()

        # Determine seniority level
        seniority_level = "Individual Contributor"  # Default
        for level, keywords in self.seniority_levels.items():
            if any(keyword.lower() in title for keyword in keywords):
                seniority_level = level
                break

        # Determine department
        department = "General"  # Default
        for dept, keywords in self.departments.items():
            if any(keyword.lower() in title for keyword in keywords):
                department = dept
                break

        # Determine buying influence
        buying_influence = "User"  # Default
        for influence, keywords in self.buying_influence_rules.items():
            if influence == 'Champion':
                # Check for sustainability/energy keywords
                if any(keyword in title for keyword in keywords):
                    buying_influence = influence
                    break
            else:
                # Check for role keywords
                if any(keyword.lower() in title for keyword in keywords):
                    buying_influence = influence
                    break

        # Calculate Verdigris relevance
        verdigris_relevance = self._calculate_verdigris_relevance(title, department)

        return ContactRole(
            title=contact.get('title', ''),
            department=department,
            seniority_level=seniority_level,
            buying_influence=buying_influence,
            verdigris_relevance=verdigris_relevance
        )

    def _calculate_verdigris_relevance(self, title: str, department: str) -> float:
        """Calculate Verdigris solution relevance score"""
        relevance_score = 0.0

        for solution, keywords in self.verdigris_keywords.items():
            for keyword in keywords:
                if keyword in title.lower():
                    relevance_score += 0.2
                if keyword in department.lower():
                    relevance_score += 0.1

        # Boost for high-relevance departments
        if department in ['Sustainability', 'Energy', 'Operations', 'Facilities']:
            relevance_score += 0.3
        elif department in ['Engineering', 'IT']:
            relevance_score += 0.2

        return min(1.0, relevance_score)

    def _calculate_role_weight(self, role: ContactRole) -> float:
        """Calculate role importance weighting"""
        seniority_weights = {
            'C-Suite': 1.0,
            'VP': 0.8,
            'Director': 0.6,
            'Manager': 0.4,
            'Individual Contributor': 0.2
        }

        influence_weights = {
            'Decision Maker': 1.0,
            'Influencer': 0.7,
            'Champion': 0.8,
            'User': 0.3,
            'Gatekeeper': 0.5
        }

        seniority_weight = seniority_weights.get(role.seniority_level, 0.2)
        influence_weight = influence_weights.get(role.buying_influence, 0.3)

        return (seniority_weight + influence_weight) / 2.0

    def _analyze_organizational_patterns(self, contact_values: List[ContactValue],
                                       company_data: Dict) -> OrganizationalInsight:
        """Analyze organizational patterns and buying committee completeness"""

        company_name = company_data.get('name', 'Unknown Company') if company_data else 'Unknown Company'
        total_contacts = len(contact_values)

        # Count by tier
        tier_counts = Counter(cv.value_tier for cv in contact_values)

        # Analyze departments
        departments = [cv.role_analysis.department for cv in contact_values]
        dominant_departments = [dept for dept, count in Counter(departments).most_common(3)]

        # Identify decision makers and champions
        decision_makers = [cv.name for cv in contact_values
                          if cv.role_analysis.buying_influence == 'Decision Maker'][:5]
        champions = [cv.name for cv in contact_values
                    if cv.role_analysis.buying_influence == 'Champion'][:3]

        # Determine organizational pattern
        organizational_pattern = self._determine_org_pattern(contact_values)

        # Calculate buying committee completeness
        buying_committee_completeness = self._calculate_committee_completeness(contact_values)

        return OrganizationalInsight(
            company_name=company_name,
            total_contacts=total_contacts,
            tier_1_contacts=tier_counts.get('Tier 1', 0),
            tier_2_contacts=tier_counts.get('Tier 2', 0),
            tier_3_contacts=tier_counts.get('Tier 3', 0),
            dominant_departments=dominant_departments,
            decision_makers=decision_makers,
            champions_identified=champions,
            organizational_pattern=organizational_pattern,
            buying_committee_completeness=buying_committee_completeness
        )

    def _determine_org_pattern(self, contact_values: List[ContactValue]) -> RolePattern:
        """Determine the organizational decision-making pattern"""

        # Analyze role distribution
        seniority_levels = [cv.role_analysis.seniority_level for cv in contact_values]
        departments = [cv.role_analysis.department for cv in contact_values]

        seniority_counts = Counter(seniority_levels)
        dept_counts = Counter(departments)

        # Determine pattern based on analysis
        if seniority_counts.get('C-Suite', 0) >= 2:
            return RolePattern(
                pattern_name="Executive-Led Decision Making",
                roles_involved=["CEO", "CTO", "CFO", "VP Operations"],
                decision_process="Top-down executive approval with technical validation",
                typical_timeline="3-6 months",
                success_factors=["Executive sponsorship", "ROI demonstration", "Technical feasibility"]
            )
        elif dept_counts.get('Operations', 0) >= 2 or dept_counts.get('Facilities', 0) >= 2:
            return RolePattern(
                pattern_name="Operations-Driven Process",
                roles_involved=["Operations Manager", "Facilities Director", "Engineering Lead"],
                decision_process="Bottom-up operational need with budget approval",
                typical_timeline="2-4 months",
                success_factors=["Operational pain point", "Cost justification", "Implementation ease"]
            )
        elif dept_counts.get('Sustainability', 0) >= 1:
            return RolePattern(
                pattern_name="Sustainability-Driven Initiative",
                roles_involved=["Sustainability Officer", "Operations Director", "CFO"],
                decision_process="ESG mandate with operational and financial validation",
                typical_timeline="4-8 months",
                success_factors=["ESG compliance", "Sustainability metrics", "Cost-neutral or positive"]
            )
        else:
            return RolePattern(
                pattern_name="Distributed Decision Making",
                roles_involved=["Multiple stakeholders across departments"],
                decision_process="Consensus-based with multiple approval stages",
                typical_timeline="6-12 months",
                success_factors=["Cross-functional buy-in", "Pilot program", "Gradual rollout"]
            )

    def _calculate_committee_completeness(self, contact_values: List[ContactValue]) -> float:
        """Calculate buying committee completeness score"""

        required_roles = ['Decision Maker', 'Influencer', 'Champion', 'User']
        found_roles = set()

        for cv in contact_values:
            found_roles.add(cv.role_analysis.buying_influence)

        completeness = len(found_roles.intersection(required_roles)) / len(required_roles)
        return completeness

    def _identify_role_patterns(self, contact_values: List[ContactValue]) -> List[RolePattern]:
        """Identify common role patterns in the organization"""

        # This is a simplified implementation - could be expanded
        patterns = []

        # Energy Management Pattern
        energy_contacts = [cv for cv in contact_values
                          if 'energy' in cv.role_analysis.title.lower() or
                             cv.role_analysis.department == 'Energy']
        if energy_contacts:
            patterns.append(RolePattern(
                pattern_name="Energy Management Focus",
                roles_involved=[cv.role_analysis.title for cv in energy_contacts[:3]],
                decision_process="Energy team evaluation with operations approval",
                typical_timeline="2-3 months",
                success_factors=["Energy cost reduction", "Monitoring capabilities", "Reporting accuracy"]
            ))

        return patterns

    def _generate_approach_recommendation(self, role: ContactRole, tier: str,
                                        readiness: str) -> str:
        """Generate recommended approach for engaging contact"""

        if tier == "Tier 1" and readiness == "Ready":
            if role.buying_influence == "Decision Maker":
                return "Executive briefing with ROI focus and strategic value proposition"
            elif role.buying_influence == "Champion":
                return "Technical deep-dive with sustainability impact and operational benefits"
            else:
                return "Solution demonstration with peer references and case studies"

        elif tier == "Tier 2" and readiness in ["Ready", "Warm"]:
            if role.department in ["Sustainability", "Operations"]:
                return "Industry-specific use case presentation with operational efficiency focus"
            else:
                return "Educational content followed by consultative discovery call"

        else:
            return "Nurture with relevant content and industry insights until engagement increases"

    def _calculate_summary_metrics(self, contact_values: List[ContactValue]) -> Dict:
        """Calculate summary metrics for contact value analysis"""

        total_contacts = len(contact_values)
        if total_contacts == 0:
            return {}

        tier_1_count = len([cv for cv in contact_values if cv.value_tier == "Tier 1"])
        tier_2_count = len([cv for cv in contact_values if cv.value_tier == "Tier 2"])

        ready_contacts = len([cv for cv in contact_values if cv.engagement_readiness == "Ready"])
        decision_makers = len([cv for cv in contact_values if cv.role_analysis.buying_influence == "Decision Maker"])

        avg_value_score = sum(cv.final_value_score for cv in contact_values) / total_contacts
        avg_verdigris_relevance = sum(cv.role_analysis.verdigris_relevance for cv in contact_values) / total_contacts

        return {
            'total_contacts': total_contacts,
            'tier_1_percentage': (tier_1_count / total_contacts) * 100,
            'tier_2_percentage': (tier_2_count / total_contacts) * 100,
            'ready_for_engagement': ready_contacts,
            'decision_makers_identified': decision_makers,
            'average_value_score': round(avg_value_score, 3),
            'average_verdigris_relevance': round(avg_verdigris_relevance, 3),
            'engagement_opportunity_score': round((tier_1_count + tier_2_count) / total_contacts * 100, 1)
        }

    def _print_value_analysis(self, analysis: Dict):
        """Print contact value analysis results"""

        metrics = analysis['summary_metrics']
        org_insights = analysis['organizational_insights']

        print(f"\n📊 CONTACT VALUE ANALYSIS RESULTS")
        print("=" * 60)

        print(f"🏢 Company: {org_insights['company_name']}")
        print(f"👥 Total Contacts: {metrics['total_contacts']}")
        print(f"🎯 Tier 1 Contacts: {org_insights['tier_1_contacts']} ({metrics['tier_1_percentage']:.1f}%)")
        print(f"📈 Tier 2 Contacts: {org_insights['tier_2_contacts']} ({metrics['tier_2_percentage']:.1f}%)")
        print(f"✅ Ready for Engagement: {metrics['ready_for_engagement']}")
        print(f"👤 Decision Makers: {metrics['decision_makers_identified']}")
        print(f"📊 Avg Value Score: {metrics['average_value_score']}")
        print(f"🎯 Verdigris Relevance: {metrics['average_verdigris_relevance']:.1%}")

        print(f"\n🏛️ ORGANIZATIONAL INSIGHTS")
        print(f"   Primary Departments: {', '.join(org_insights['dominant_departments'][:3])}")
        print(f"   Decision Makers: {', '.join(org_insights['decision_makers'][:3])}")
        print(f"   Champions: {', '.join(org_insights['champions_identified'][:2]) if org_insights['champions_identified'] else 'None identified'}")
        print(f"   Buying Committee: {org_insights['buying_committee_completeness']:.1%} complete")

        print(f"\n🎯 KEY RECOMMENDATIONS:")
        print(f"   • Focus on {org_insights['tier_1_contacts']} Tier 1 contacts for immediate outreach")
        print(f"   • {metrics['engagement_opportunity_score']:.1f}% of contacts are viable prospects")
        print(f"   • Pattern: {org_insights['organizational_pattern']['pattern_name']}")
        print(f"   • Timeline: {org_insights['organizational_pattern']['typical_timeline']}")

    def convert_to_dashboard_format(self, analysis_result: Dict) -> Dict:
        """Convert analysis results to dashboard-friendly format"""

        contact_values = analysis_result['contact_values']
        org_insights = analysis_result['organizational_insights']
        metrics = analysis_result['summary_metrics']

        # Get top contacts by tier
        tier_1_contacts = [cv for cv in contact_values if cv['value_tier'] == 'Tier 1'][:5]
        tier_2_contacts = [cv for cv in contact_values if cv['value_tier'] == 'Tier 2'][:5]

        return {
            'summary': metrics,
            'organizational_insights': org_insights,
            'top_tier_1_contacts': tier_1_contacts,
            'top_tier_2_contacts': tier_2_contacts,
            'role_patterns': analysis_result['role_patterns'],
            'analysis_timestamp': analysis_result['analysis_timestamp']
        }

# Export for use by other modules
contact_value_analyzer = ContactValueAnalyzer()

def main():
    """Test the contact value analyzer"""
    print("👥 Contact Value Analyzer initialized")
    print("💡 Use analyze_contact_value() method to analyze contacts")

if __name__ == "__main__":
    main()
