#!/usr/bin/env python3
"""
Intelligent Contact Enrichment with Verdigris Signals MEDDIC
Integrates persona classification, role intelligence, and sales insights
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Import our systems
from verdigris_signals_meddic_framework import VerdigrisSignalsMEDDIC
from enhanced_deduplication_system import ProductionContactProcessor

class IntelligentContactEnricher:
    """Enriches contacts with MEDDIC classification and sales intelligence"""

    def __init__(self):
        self.meddic = VerdigrisSignalsMEDDIC()
        self.role_intelligence = self._build_role_intelligence()

    def _build_role_intelligence(self) -> Dict:
        """Build comprehensive role intelligence database based on research"""

        return {
            'power_monitoring_roles': {
                'who_monitors_power': {
                    'primary_roles': [
                        'Data Center Facilities Manager',
                        'Critical Facilities Engineer',
                        'Operations Manager',
                        'Capacity Engineer'
                    ],
                    'key_responsibilities': [
                        'Operating and managing critical power distribution systems',
                        'Day-to-day power tracking via DCIM or building management tools',
                        'Continuous monitoring via intelligent PDUs and sensors',
                        'Optimizing load distribution to avoid overloads'
                    ],
                    'verdigris_relevance': 'These are primary users who would benefit from real-time circuit-level monitoring'
                },
                'who_gets_alerts': {
                    'primary_roles': [
                        'Facilities Engineer',
                        'Data Center Technician',
                        'Critical Facilities Technician',
                        'On-call facility engineers'
                    ],
                    'alert_scenarios': [
                        'Power threshold exceeded or irregularities detected',
                        'Circuit overload conditions',
                        'Backup system failures',
                        'Voltage drops or anomalies'
                    ],
                    'verdigris_relevance': 'Would benefit from smart alerting that reduces false positives and provides actionable insights'
                },
                'who_decides_on_tools': {
                    'primary_roles': [
                        'Data Center Manager',
                        'Director of Data Center Operations',
                        'Director of Infrastructure',
                        'VP Infrastructure'
                    ],
                    'decision_process': [
                        'Evaluate monitoring solutions based on operational needs',
                        'Build business case and ROI justification',
                        'Get buy-in from higher management (CIO/CTO/CFO)',
                        'Champion specific tools to leadership'
                    ],
                    'verdigris_relevance': 'Economic buyers who need ROI-focused business case and risk mitigation arguments'
                },
                'who_champions_predictive': {
                    'primary_roles': [
                        'Data Center Facilities Manager',
                        'Operations Director',
                        'Capacity Planning Engineer',
                        'Energy Specialist (for GPU environments)'
                    ],
                    'value_drivers': [
                        'Preventing outages through early anomaly detection',
                        'Enabling preventive vs reactive maintenance',
                        'Improving energy efficiency and PUE',
                        'Optimizing power/cooling for high-density workloads'
                    ],
                    'verdigris_relevance': 'Natural champions who would advocate for predictive power analytics internally'
                },
                'who_has_budget': {
                    'primary_roles': [
                        'VP of IT Infrastructure',
                        'Director of Data Center Operations',
                        'CIO/CTO (final approval)',
                        'CFO (for major expenditures)'
                    ],
                    'budget_considerations': [
                        'Infrastructure monitoring falls under data center OpEx/CapEx',
                        'Often integrated into larger projects (new builds, consolidations)',
                        'Requires ROI justification and executive approval',
                        'Budget authority typically at management level, not individual technician'
                    ],
                    'verdigris_relevance': 'Economic buyers who control purse strings and need financial justification'
                }
            },
            'engagement_intelligence': {
                'gpu_environments': {
                    'special_considerations': 'GPU-focused neocloud data centers have extremely high power draw',
                    'key_personas': ['Capacity Planning Engineer', 'Energy Specialist'],
                    'unique_pain_points': ['Dense workload power optimization', 'AI infrastructure capacity planning'],
                    'verdigris_angle': 'GPU-specific monitoring and high-density optimization capabilities'
                },
                'traditional_environments': {
                    'special_considerations': 'Mid-size to large traditional data centers with mixed workloads',
                    'key_personas': ['Data Center Facilities Manager', 'Operations Manager'],
                    'unique_pain_points': ['General power efficiency', 'Uptime optimization', 'Cost management'],
                    'verdigris_angle': 'Comprehensive power monitoring with ROI focus'
                },
                'hyperscale_environments': {
                    'special_considerations': 'Large-scale operations with sophisticated existing monitoring',
                    'key_personas': ['Director of Infrastructure', 'VP Operations'],
                    'unique_pain_points': ['Integration complexity', 'Scale optimization', 'Advanced analytics needs'],
                    'verdigris_angle': 'Advanced analytics and integration capabilities that enhance existing systems'
                }
            }
        }

    def enrich_contact_with_intelligence(self, contact: Dict) -> Dict:
        """Enrich contact with MEDDIC classification and role intelligence"""

        # Step 1: MEDDIC Classification
        meddic_classification = self.meddic.classify_contact(contact)

        # Step 2: Role Intelligence Analysis
        role_analysis = self._analyze_role_intelligence(contact, meddic_classification)

        # Step 3: Sales Strategy Generation
        sales_strategy = self._generate_sales_strategy(contact, meddic_classification, role_analysis)

        # Step 4: Educational Content Recommendations
        educational_content = self._recommend_educational_content(contact, meddic_classification)

        # Compile enriched contact
        enriched_contact = {
            **contact,  # Original contact data
            'meddic_classification': meddic_classification,
            'role_intelligence': role_analysis,
            'sales_strategy': sales_strategy,
            'educational_content': educational_content,
            'enrichment_timestamp': datetime.now().isoformat(),
            'enrichment_confidence': self._calculate_enrichment_confidence(meddic_classification, role_analysis)
        }

        return enriched_contact

    def _analyze_role_intelligence(self, contact: Dict, meddic: Dict) -> Dict:
        """Analyze contact's role against power monitoring intelligence"""

        title = (contact.get('title') or '').lower()
        persona_type = meddic['primary_persona']['type']

        # Find relevant role intelligence
        relevant_intelligence = []

        for category, info in self.role_intelligence['power_monitoring_roles'].items():
            for role in info.get('primary_roles', []):
                if any(word in title for word in role.lower().split()):
                    relevant_intelligence.append({
                        'category': category,
                        'role_match': role,
                        'responsibilities': info.get('key_responsibilities', info.get('decision_process', info.get('value_drivers', info.get('budget_considerations', [])))),
                        'verdigris_relevance': info.get('verdigris_relevance', '')
                    })

        # Environment classification
        company = (contact.get('company') or '').lower()
        environment_type = 'traditional'
        if any(keyword in company for keyword in ['gpu', 'ai', 'cloud', 'compute']):
            environment_type = 'gpu'
        elif any(keyword in company for keyword in ['aws', 'google', 'microsoft', 'meta', 'hyperscal']):
            environment_type = 'hyperscale'

        return {
            'relevant_intelligence': relevant_intelligence,
            'environment_type': environment_type,
            'environment_considerations': self.role_intelligence['engagement_intelligence'].get(f'{environment_type}_environments', {}),
            'power_monitoring_relevance': len(relevant_intelligence) > 0
        }

    def _generate_sales_strategy(self, contact: Dict, meddic: Dict, role_analysis: Dict) -> Dict:
        """Generate specific sales strategy based on persona and role intelligence"""

        persona_type = meddic['primary_persona']['type']
        buying_power = meddic['primary_persona']['buying_power_score']
        influence_score = meddic['primary_persona']['influence_score']

        # Base strategy from MEDDIC
        base_approach = meddic['engagement_strategy']['approach']
        value_props = meddic['engagement_strategy']['value_props']

        # Environment-specific adjustments
        environment_info = role_analysis.get('environment_considerations', {})

        strategy = {
            'primary_approach': base_approach,
            'value_propositions': value_props,
            'call_to_action': self._determine_cta(persona_type, buying_power),
            'engagement_priority': self._calculate_engagement_priority(buying_power, influence_score),
            'conversation_starters': self._generate_conversation_starters(contact, role_analysis),
            'objection_handling': self._generate_objection_handling(persona_type),
            'follow_up_cadence': self._suggest_follow_up_cadence(persona_type, buying_power)
        }

        return strategy

    def _recommend_educational_content(self, contact: Dict, meddic: Dict) -> List[Dict]:
        """Recommend educational content based on persona and interests"""

        persona_type = meddic['primary_persona']['type']
        title = (contact.get('title') or '').lower()

        content_recommendations = []

        # Persona-specific content
        if persona_type == 'economic_buyer':
            content_recommendations.extend([
                {
                    'type': 'ROI Calculator',
                    'title': 'Data Center Power Monitoring ROI Calculator',
                    'description': 'Calculate potential savings from power monitoring and predictive analytics',
                    'relevance': 'Budget decision makers need quantified ROI'
                },
                {
                    'type': 'Case Study',
                    'title': 'Power Monitoring ROI: $2M Outage Prevention Case Study',
                    'description': 'Real customer example of outage prevention and cost savings',
                    'relevance': 'Economic buyers respond to peer success stories'
                }
            ])

        elif persona_type == 'champion':
            content_recommendations.extend([
                {
                    'type': 'Technical Deep-Dive',
                    'title': 'Circuit-Level Power Monitoring: Technical Overview',
                    'description': 'Deep technical explanation of real-time power monitoring capabilities',
                    'relevance': 'Champions need technical ammunition for internal advocacy'
                },
                {
                    'type': 'Implementation Guide',
                    'title': 'Power Monitoring Implementation Best Practices',
                    'description': 'Step-by-step guide for successful power monitoring deployment',
                    'relevance': 'Champions need to show feasibility to management'
                }
            ])

        elif persona_type == 'technical_evaluator':
            content_recommendations.extend([
                {
                    'type': 'Technical Demo',
                    'title': 'Interactive Power Analytics Dashboard',
                    'description': 'Live demo of analytics capabilities and trend analysis',
                    'relevance': 'Technical evaluators need hands-on product experience'
                },
                {
                    'type': 'Integration Guide',
                    'title': 'DCIM Integration Capabilities and APIs',
                    'description': 'Technical documentation for existing system integration',
                    'relevance': 'Technical evaluators worry about integration complexity'
                }
            ])

        elif persona_type == 'end_user':
            content_recommendations.extend([
                {
                    'type': 'User Interface Tour',
                    'title': 'Day-in-the-Life: Power Monitoring Dashboard',
                    'description': 'Walkthrough of daily operational workflows and alerts',
                    'relevance': 'End users need to see how tool improves their daily work'
                },
                {
                    'type': 'Training Material',
                    'title': 'Power Anomaly Response Playbook',
                    'description': 'Best practices for responding to power monitoring alerts',
                    'relevance': 'End users want to be more effective at their jobs'
                }
            ])

        # Role-specific content
        if 'capacity' in title or 'planning' in title:
            content_recommendations.append({
                'type': 'White Paper',
                'title': 'Predictive Capacity Planning for AI Workloads',
                'description': 'Advanced analytics for GPU and high-density power planning',
                'relevance': 'Capacity planners need forward-looking insights'
            })

        return content_recommendations

    def _determine_cta(self, persona_type: str, buying_power: int) -> str:
        """Determine appropriate call-to-action based on persona"""

        if persona_type == 'economic_buyer' and buying_power >= 80:
            return "Schedule executive briefing on power monitoring ROI"
        elif persona_type == 'champion':
            return "Offer pilot program or technical deep-dive session"
        elif persona_type == 'technical_evaluator':
            return "Provide technical demo and integration assessment"
        elif persona_type == 'end_user':
            return "Show user interface walkthrough and day-in-the-life demo"
        else:
            return "Share relevant case study and schedule follow-up call"

    def _calculate_engagement_priority(self, buying_power: int, influence_score: int) -> str:
        """Calculate engagement priority score"""

        combined_score = (buying_power * 0.6) + (influence_score * 0.4)

        if combined_score >= 80:
            return "High Priority"
        elif combined_score >= 60:
            return "Medium Priority"
        else:
            return "Low Priority"

    def _generate_conversation_starters(self, contact: Dict, role_analysis: Dict) -> List[str]:
        """Generate conversation starters based on role intelligence"""

        starters = []
        title = (contact.get('title') or '').lower()

        if 'director' in title or 'vp' in title:
            starters.extend([
                f"I noticed {contact.get('company', 'your organization')} is likely dealing with power capacity planning challenges. How are you currently handling power monitoring?",
                "What's your biggest concern when it comes to preventing power-related outages?",
                "How do you currently justify ROI for infrastructure monitoring investments?"
            ])

        elif 'manager' in title or 'engineer' in title:
            starters.extend([
                "What tools are you currently using for day-to-day power monitoring?",
                "How much time do you spend manually tracking power consumption and trends?",
                "What's the most frustrating part of your current power monitoring setup?"
            ])

        elif role_analysis.get('environment_type') == 'gpu':
            starters.append(
                "With high-density GPU workloads, how are you handling the extreme power monitoring requirements?"
            )

        return starters

    def _generate_objection_handling(self, persona_type: str) -> List[Dict]:
        """Generate common objections and handling strategies"""

        objections = []

        if persona_type == 'economic_buyer':
            objections.extend([
                {
                    'objection': "We already have a DCIM system",
                    'response': "Verdigris integrates with existing DCIM systems to enhance them with circuit-level insights and predictive analytics. Think of it as adding AI-powered intelligence to your current setup."
                },
                {
                    'objection': "The ROI isn't clear",
                    'response': "One prevented outage typically pays for years of monitoring. We have customers who've prevented multi-million dollar outages in their first year. I can share specific ROI examples from similar environments."
                }
            ])

        elif persona_type == 'technical_evaluator':
            objections.extend([
                {
                    'objection': "Integration will be too complex",
                    'response': "We have pre-built integrations with major DCIM systems and a full API. Most integrations are completed in days, not months. I can show you our integration documentation and timeline."
                },
                {
                    'objection': "Our team doesn't have time to learn another system",
                    'response': "The interface is designed for data center professionals and requires minimal training. Most users are productive within hours. We also provide comprehensive onboarding support."
                }
            ])

        return objections

    def _suggest_follow_up_cadence(self, persona_type: str, buying_power: int) -> str:
        """Suggest appropriate follow-up cadence"""

        if persona_type == 'economic_buyer' and buying_power >= 80:
            return "Weekly follow-ups with executive-level content and ROI updates"
        elif persona_type == 'champion':
            return "Bi-weekly follow-ups with technical content and implementation planning"
        elif persona_type == 'technical_evaluator':
            return "Weekly follow-ups during evaluation phase with technical materials"
        else:
            return "Monthly follow-ups with educational content and industry updates"

    def _calculate_enrichment_confidence(self, meddic: Dict, role_analysis: Dict) -> str:
        """Calculate overall confidence in enrichment accuracy"""

        meddic_confidence = meddic.get('confidence', 'low')
        role_relevance = role_analysis.get('power_monitoring_relevance', False)

        if meddic_confidence == 'high' and role_relevance:
            return 'high'
        elif meddic_confidence in ['high', 'medium'] and role_relevance:
            return 'medium'
        elif meddic_confidence == 'high':
            return 'medium'
        else:
            return 'low'

def test_intelligent_enrichment():
    """Test the intelligent contact enrichment system"""

    print("🧠 TESTING INTELLIGENT CONTACT ENRICHMENT")
    print("=" * 60)

    enricher = IntelligentContactEnricher()

    # Test with our real Genesis Cloud contact
    test_contact = {
        'name': 'Lorena Acosta',
        'title': 'Director of Operations',
        'company': 'Genesis Cloud',
        'email': 'lorena@genesiscloud.com',
        'linkedin_url': 'https://linkedin.com/in/lorena-acosta'
    }

    enriched = enricher.enrich_contact_with_intelligence(test_contact)

    print(f"👤 {enriched['name']} - {enriched['title']}")
    print(f"\n🎯 MEDDIC Classification:")
    print(f"   Persona: {enriched['meddic_classification']['primary_persona']['name']}")
    print(f"   Type: {enriched['meddic_classification']['primary_persona']['type']}")
    print(f"   Buying Power: {enriched['meddic_classification']['primary_persona']['buying_power_score']}/100")

    print(f"\n🔍 Role Intelligence:")
    print(f"   Environment: {enriched['role_intelligence']['environment_type']}")
    print(f"   Power Monitoring Relevance: {enriched['role_intelligence']['power_monitoring_relevance']}")

    print(f"\n💼 Sales Strategy:")
    print(f"   Priority: {enriched['sales_strategy']['engagement_priority']}")
    print(f"   CTA: {enriched['sales_strategy']['call_to_action']}")

    print(f"\n📚 Educational Content ({len(enriched['educational_content'])} items):")
    for content in enriched['educational_content'][:2]:
        print(f"   • {content['title']} ({content['type']})")

    print(f"\n✨ Enrichment Confidence: {enriched['enrichment_confidence']}")

    return enriched

if __name__ == "__main__":
    enriched_contact = test_intelligent_enrichment()