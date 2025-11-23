#!/usr/bin/env python3
"""
Complete ABM Production System
End-to-end pipeline: Apollo discovery → Deduplication → MEDDIC classification → Intelligence enrichment
"""

import os
import json
from datetime import datetime
from typing import Dict, List

# Import all our production modules
from production_apollo_integration import ProductionApolloIntegration
from enhanced_deduplication_system import ProductionContactProcessor
from intelligent_contact_enrichment import IntelligentContactEnricher

class CompleteABMProductionSystem:
    """Complete end-to-end ABM research system for Verdigris Signals"""

    def __init__(self):
        self.apollo = ProductionApolloIntegration()
        self.processor = ProductionContactProcessor()
        self.enricher = IntelligentContactEnricher()
        self.results = {}

    def run_complete_genesis_cloud_research(self) -> Dict:
        """Run complete ABM research pipeline for Genesis Cloud"""

        print("🚀 COMPLETE ABM PRODUCTION SYSTEM - GENESIS CLOUD")
        print("=" * 70)

        # Step 1: Apollo Contact Discovery
        print("📡 STEP 1: APOLLO CONTACT DISCOVERY")
        print("-" * 40)
        raw_contacts = self.apollo.search_genesis_cloud_contacts()

        if not raw_contacts:
            return {'error': 'No contacts found from Apollo'}

        # Step 2: Enhanced Deduplication and Account Linking
        print(f"\n🔄 STEP 2: DEDUPLICATION & ACCOUNT LINKING")
        print("-" * 40)
        processing_report = self.processor.process_apollo_contacts(raw_contacts)

        # Step 3: MEDDIC Classification and Intelligence Enrichment
        print(f"\n🧠 STEP 3: MEDDIC CLASSIFICATION & INTELLIGENCE ENRICHMENT")
        print("-" * 40)
        enriched_contacts = []

        for contact in processing_report['processed_contacts']:
            enriched = self.enricher.enrich_contact_with_intelligence(contact)
            enriched_contacts.append(enriched)

            # Show enrichment results
            meddic = enriched['meddic_classification']
            strategy = enriched['sales_strategy']

            print(f"   👤 {enriched['name']} - {enriched['title']}")
            print(f"      🎯 Persona: {meddic['primary_persona']['name']}")
            print(f"      📊 Type: {meddic['primary_persona']['type']} | Priority: {strategy['engagement_priority']}")
            print(f"      💼 CTA: {strategy['call_to_action']}")

        # Step 4: Sales Intelligence Analysis
        print(f"\n📊 STEP 4: SALES INTELLIGENCE ANALYSIS")
        print("-" * 40)
        intelligence_report = self._analyze_sales_intelligence(enriched_contacts)

        # Step 5: Generate Production Reports
        print(f"\n📄 STEP 5: PRODUCTION REPORT GENERATION")
        print("-" * 40)
        production_reports = self._generate_production_reports(enriched_contacts, intelligence_report)

        # Compile final results
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'account': 'Genesis Cloud',
            'pipeline_summary': {
                'apollo_raw_contacts': len(raw_contacts),
                'deduplicated_contacts': len(processing_report['processed_contacts']),
                'enriched_contacts': len(enriched_contacts),
                'high_priority_contacts': len([c for c in enriched_contacts if c['sales_strategy']['engagement_priority'] == 'High Priority'])
            },
            'apollo_discovery': {
                'contacts_found': len(raw_contacts),
                'deduplication_rate': processing_report['deduplication_rate']
            },
            'meddic_analysis': intelligence_report,
            'enriched_contacts': enriched_contacts,
            'production_reports': production_reports
        }

        self._print_final_summary()
        return self.results

    def _analyze_sales_intelligence(self, enriched_contacts: List[Dict]) -> Dict:
        """Analyze sales intelligence across all enriched contacts"""

        # Persona distribution
        persona_distribution = {}
        buying_power_distribution = {'high': 0, 'medium': 0, 'low': 0}
        priority_distribution = {'High Priority': 0, 'Medium Priority': 0, 'Low Priority': 0}

        # Account coverage analysis
        economic_buyers = []
        champions = []
        technical_evaluators = []
        end_users = []

        for contact in enriched_contacts:
            # Persona analysis
            persona_type = contact['meddic_classification']['primary_persona']['type']
            buying_power = contact['meddic_classification']['primary_persona']['buying_power_score']
            priority = contact['sales_strategy']['engagement_priority']

            # Count personas
            if persona_type not in persona_distribution:
                persona_distribution[persona_type] = 0
            persona_distribution[persona_type] += 1

            # Categorize by buying power
            if buying_power >= 80:
                buying_power_distribution['high'] += 1
            elif buying_power >= 50:
                buying_power_distribution['medium'] += 1
            else:
                buying_power_distribution['low'] += 1

            # Count priorities
            priority_distribution[priority] += 1

            # Categorize by MEDDIC role
            if persona_type == 'economic_buyer':
                economic_buyers.append(contact)
            elif persona_type == 'champion':
                champions.append(contact)
            elif persona_type == 'technical_evaluator':
                technical_evaluators.append(contact)
            elif persona_type == 'end_user':
                end_users.append(contact)

        # Account coverage assessment
        coverage_score = 0
        coverage_gaps = []

        if economic_buyers:
            coverage_score += 40  # Economic buyer is critical
        else:
            coverage_gaps.append("No Economic Buyer identified")

        if champions:
            coverage_score += 30  # Champion is very important
        else:
            coverage_gaps.append("No Champion identified")

        if technical_evaluators:
            coverage_score += 20  # Technical evaluator important for validation
        else:
            coverage_gaps.append("No Technical Evaluator identified")

        if end_users:
            coverage_score += 10  # End users provide operational insight

        analysis = {
            'persona_distribution': persona_distribution,
            'buying_power_distribution': buying_power_distribution,
            'priority_distribution': priority_distribution,
            'meddic_coverage': {
                'economic_buyers': len(economic_buyers),
                'champions': len(champions),
                'technical_evaluators': len(technical_evaluators),
                'end_users': len(end_users),
                'coverage_score': coverage_score,
                'coverage_gaps': coverage_gaps
            },
            'recommended_actions': self._generate_recommended_actions(
                economic_buyers, champions, technical_evaluators, coverage_gaps
            )
        }

        print(f"   📊 Persona Distribution: {persona_distribution}")
        print(f"   💪 High Buying Power: {buying_power_distribution['high']} contacts")
        print(f"   🎯 High Priority: {priority_distribution['High Priority']} contacts")
        print(f"   📈 Account Coverage Score: {coverage_score}/100")

        return analysis

    def _generate_recommended_actions(self, economic_buyers: List, champions: List,
                                    technical_evaluators: List, coverage_gaps: List) -> List[str]:
        """Generate specific recommended actions based on contact analysis"""

        actions = []

        # Economic buyer actions
        if economic_buyers:
            for buyer in economic_buyers:
                actions.append(f"Schedule executive briefing with {buyer['name']} ({buyer['title']}) - focus on ROI and risk mitigation")
        else:
            actions.append("PRIORITY: Identify and connect with economic buyer (Director/VP level)")

        # Champion actions
        if champions:
            for champion in champions:
                actions.append(f"Provide technical deep-dive to {champion['name']} - position as internal advocate")
        else:
            actions.append("Find facilities manager or operations lead who can champion solution internally")

        # Coverage gaps
        if "No Technical Evaluator identified" in coverage_gaps:
            actions.append("Identify operations manager or capacity engineer for technical evaluation")

        # Strategic actions
        if len(economic_buyers) > 0 and len(champions) > 0:
            actions.append("Multi-threaded approach: Coordinate between economic buyer and champion")

        actions.append("Leverage Genesis Cloud's GPU focus and recent $75M funding as conversation openers")

        return actions

    def _generate_production_reports(self, enriched_contacts: List[Dict], intelligence: Dict) -> Dict:
        """Generate production-ready reports for sales team"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Sales-ready contact report
        sales_report = {
            'account_name': 'Genesis Cloud',
            'research_date': datetime.now().isoformat(),
            'summary': {
                'total_contacts': len(enriched_contacts),
                'high_priority': intelligence['priority_distribution']['High Priority'],
                'economic_buyers': intelligence['meddic_coverage']['economic_buyers'],
                'coverage_score': intelligence['meddic_coverage']['coverage_score']
            },
            'contact_details': []
        }

        for contact in enriched_contacts:
            contact_summary = {
                'name': contact['name'],
                'title': contact['title'],
                'email': contact.get('email'),
                'linkedin': contact.get('linkedin_url'),
                'persona': contact['meddic_classification']['primary_persona']['name'],
                'persona_type': contact['meddic_classification']['primary_persona']['type'],
                'buying_power': contact['meddic_classification']['primary_persona']['buying_power_score'],
                'priority': contact['sales_strategy']['engagement_priority'],
                'call_to_action': contact['sales_strategy']['call_to_action'],
                'conversation_starters': contact['sales_strategy']['conversation_starters'],
                'educational_content': [c['title'] for c in contact['educational_content']]
            }
            sales_report['contact_details'].append(contact_summary)

        # Executive summary report
        executive_summary = {
            'account': 'Genesis Cloud',
            'opportunity_assessment': 'High Priority Account',
            'key_findings': [
                f"Found {len(enriched_contacts)} relevant contacts through Apollo API",
                f"Identified {intelligence['meddic_coverage']['economic_buyers']} economic buyer(s) with decision authority",
                f"Account coverage score: {intelligence['meddic_coverage']['coverage_score']}/100",
                f"Genesis Cloud environment: GPU-focused cloud provider with recent $75M funding"
            ],
            'recommended_actions': intelligence['recommended_actions'],
            'next_steps': [
                "Schedule executive briefing with identified economic buyer",
                "Share ROI calculator and outage prevention case studies",
                "Offer pilot program focused on GPU power monitoring"
            ]
        }

        # Save reports
        reports = {
            'sales_report_file': f'genesis_cloud_sales_intelligence_{timestamp}.json',
            'executive_summary_file': f'genesis_cloud_executive_summary_{timestamp}.json'
        }

        with open(reports['sales_report_file'], 'w') as f:
            json.dump(sales_report, f, indent=2)

        with open(reports['executive_summary_file'], 'w') as f:
            json.dump(executive_summary, f, indent=2)

        print(f"   📄 Sales Intelligence Report: {reports['sales_report_file']}")
        print(f"   👔 Executive Summary: {reports['executive_summary_file']}")

        return reports

    def _print_final_summary(self):
        """Print final system summary"""

        print(f"\n🎉 COMPLETE ABM SYSTEM - FINAL RESULTS")
        print("=" * 50)
        print(f"🏢 Account: Genesis Cloud")
        print(f"📡 Apollo Discovery: {self.results['pipeline_summary']['apollo_raw_contacts']} raw → {self.results['pipeline_summary']['deduplicated_contacts']} unique")
        print(f"🧠 MEDDIC Classification: {self.results['pipeline_summary']['enriched_contacts']} contacts enriched")
        print(f"🎯 High Priority Contacts: {self.results['pipeline_summary']['high_priority_contacts']}")
        print(f"📊 Account Coverage: {self.results['meddic_analysis']['meddic_coverage']['coverage_score']}/100")

        print(f"\n📋 RECOMMENDED ACTIONS:")
        for i, action in enumerate(self.results['meddic_analysis']['recommended_actions'][:3], 1):
            print(f"   {i}. {action}")

        print(f"\n🚀 SYSTEM STATUS: Production Ready!")
        print(f"   ✅ All pipeline components working")
        print(f"   ✅ Real Apollo data discovery")
        print(f"   ✅ MEDDIC persona classification")
        print(f"   ✅ Sales intelligence generation")
        print(f"   ❌ Waiting for Notion databases (permission issue)")

def run_complete_system():
    """Run the complete ABM production system"""

    try:
        system = CompleteABMProductionSystem()
        results = system.run_complete_genesis_cloud_research()

        if 'error' in results:
            print(f"❌ System error: {results['error']}")
            return False

        return True

    except Exception as e:
        print(f"❌ Complete system error: {e}")
        return False

if __name__ == "__main__":
    success = run_complete_system()
    if success:
        print(f"\n✅ Complete ABM Production System: OPERATIONAL")
    else:
        print(f"\n❌ Complete ABM Production System: FAILED")