#!/usr/bin/env python3
"""
Product Design Agent - Ensures Implementation Compliance with SKILL.md
Validates that all implementations follow the 5-phase ABM research specification
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ProductDesignAgent:
    """Ensures all implementations comply with SKILL.md specification"""

    def __init__(self, repo_path: str = "/Users/chungty/Projects/vdg-clean/abm-research"):
        self.repo_path = Path(repo_path)
        self.skill_spec_path = Path("/tmp/verdigris-abm-research/SKILL.md")
        self.references_path = Path("/tmp/verdigris-abm-research/references")
        self.compliance_log = []

        print("📋 Product Design Agent initialized")
        print(f"🎯 Specification: {self.skill_spec_path}")
        print(f"📚 References: {self.references_path}")

    def validate_skill_compliance(self) -> Dict:
        """Validate current implementation against SKILL.md specification"""

        print("\n🔍 VALIDATING SKILL.MD COMPLIANCE...")

        validation_results = {
            'overall_compliance': False,
            'phase_compliance': {
                'phase_1_account_intelligence': False,
                'phase_2_contact_discovery': False,
                'phase_3_contact_enrichment': False,
                'phase_4_engagement_intelligence': False,
                'phase_5_strategic_partnerships': False
            },
            'notion_structure_compliance': False,
            'scoring_formula_compliance': False,
            'api_integration_compliance': False,
            'missing_components': [],
            'recommendations': []
        }

        # Check if specification file exists and is readable
        if not self.skill_spec_path.exists():
            validation_results['missing_components'].append("SKILL.md specification file not found")
            return validation_results

        # Validate 5-phase workflow implementation
        self._validate_phase_implementations(validation_results)

        # Validate Notion database structure
        self._validate_notion_structure(validation_results)

        # Validate scoring formula implementation
        self._validate_scoring_formulas(validation_results)

        # Validate API integrations
        self._validate_api_integrations(validation_results)

        # Calculate overall compliance
        validation_results['overall_compliance'] = self._calculate_overall_compliance(validation_results)

        # Generate recommendations
        validation_results['recommendations'] = self._generate_compliance_recommendations(validation_results)

        self._print_compliance_summary(validation_results)
        return validation_results

    def _validate_phase_implementations(self, validation_results: Dict):
        """Check if all 5 phases are properly implemented"""

        print("   📊 Validating 5-phase workflow implementation...")

        # Look for comprehensive ABM research implementation
        abm_research_file = self.repo_path / "comprehensive_abm_research.py"

        if abm_research_file.exists():
            try:
                with open(abm_research_file, 'r') as f:
                    content = f.read()

                # Check for each phase implementation
                phases_to_check = [
                    ('phase_1_account_intelligence', 'phase1_account_intelligence_baseline'),
                    ('phase_2_contact_discovery', 'phase2_contact_discovery_segmentation'),
                    ('phase_3_contact_enrichment', 'phase3_high_priority_contact_enrichment'),
                    ('phase_4_engagement_intelligence', 'phase4_engagement_intelligence'),
                    ('phase_5_strategic_partnerships', 'phase5_strategic_partnership_intelligence')
                ]

                for phase_key, function_name in phases_to_check:
                    if function_name in content:
                        validation_results['phase_compliance'][phase_key] = True
                        print(f"      ✅ {phase_key.replace('_', ' ').title()}")
                    else:
                        print(f"      ❌ {phase_key.replace('_', ' ').title()} - Missing function: {function_name}")

            except Exception as e:
                print(f"      ⚠️ Error reading ABM research file: {e}")
                validation_results['missing_components'].append("ABM research implementation unreadable")
        else:
            print("      ❌ No comprehensive ABM research implementation found")
            validation_results['missing_components'].append("comprehensive_abm_research.py not found")

    def _validate_notion_structure(self, validation_results: Dict):
        """Validate Notion database structure matches specification"""

        print("   🗄️ Validating Notion database structure...")

        # Check if QA agent has real database IDs
        qa_agent_file = self.repo_path / "agents" / "qa_verification_agent.py"

        if qa_agent_file.exists():
            try:
                with open(qa_agent_file, 'r') as f:
                    content = f.read()

                # Check for actual database IDs (not None or empty)
                required_databases = ['accounts', 'trigger_events', 'contacts', 'partnerships']

                if 'actual_database_ids' in content:
                    # Look for database ID pattern
                    for db_name in required_databases:
                        if f"'{db_name}':" in content and "None" not in content.split(f"'{db_name}':")[1].split(',')[0]:
                            validation_results['notion_structure_compliance'] = True
                            print(f"      ✅ Found {db_name} database configuration")
                        else:
                            validation_results['notion_structure_compliance'] = False
                            print(f"      ❌ Missing or invalid {db_name} database configuration")
                            break
                else:
                    print("      ❌ No actual database IDs found")
                    validation_results['missing_components'].append("Real Notion database IDs not configured")

            except Exception as e:
                print(f"      ⚠️ Error validating Notion structure: {e}")
        else:
            print("      ❌ QA Verification Agent not found")
            validation_results['missing_components'].append("QA Verification Agent missing")

    def _validate_scoring_formulas(self, validation_results: Dict):
        """Validate scoring formula implementation matches lead_scoring_config.json"""

        print("   🧮 Validating scoring formula implementation...")

        scoring_config_file = self.references_path / "lead_scoring_config.json"

        if scoring_config_file.exists():
            try:
                with open(scoring_config_file, 'r') as f:
                    scoring_config = json.load(f)

                # Check if weights are properly configured
                expected_weights = scoring_config.get('scoring_formula', {}).get('component_weights', {})

                if (expected_weights.get('icp_fit_weight') == 0.40 and
                    expected_weights.get('buying_power_weight') == 0.30 and
                    expected_weights.get('engagement_weight') == 0.30):
                    validation_results['scoring_formula_compliance'] = True
                    print("      ✅ Scoring formula weights configured correctly")
                else:
                    print("      ❌ Scoring formula weights misconfigured")

            except Exception as e:
                print(f"      ⚠️ Error validating scoring config: {e}")
                validation_results['missing_components'].append("Scoring configuration invalid")
        else:
            print("      ❌ lead_scoring_config.json not found")
            validation_results['missing_components'].append("lead_scoring_config.json missing")

    def _validate_api_integrations(self, validation_results: Dict):
        """Check if required API integrations are properly implemented"""

        print("   🔗 Validating API integrations...")

        # Check for Apollo API integration
        apollo_integration_found = False
        openai_integration_found = False
        notion_integration_found = False

        # Scan Python files for API integrations
        python_files = list(self.repo_path.glob('**/*.py'))

        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                if 'apollo' in content.lower() or 'apollo_api_key' in content:
                    apollo_integration_found = True

                if 'openai' in content.lower() or 'gpt-4o-mini' in content:
                    openai_integration_found = True

                if 'notion' in content.lower() or 'notion_api_key' in content:
                    notion_integration_found = True

            except Exception:
                continue

        # Report integration status
        integrations = [
            (apollo_integration_found, "Apollo API", "Contact discovery"),
            (openai_integration_found, "OpenAI API", "Intelligence generation"),
            (notion_integration_found, "Notion API", "Database population")
        ]

        all_integrations_found = True
        for found, api_name, purpose in integrations:
            if found:
                print(f"      ✅ {api_name} integration found ({purpose})")
            else:
                print(f"      ❌ {api_name} integration missing ({purpose})")
                validation_results['missing_components'].append(f"{api_name} integration")
                all_integrations_found = False

        validation_results['api_integration_compliance'] = all_integrations_found

    def _calculate_overall_compliance(self, validation_results: Dict) -> bool:
        """Calculate overall compliance score"""

        # Count compliant components
        phase_compliance = sum(validation_results['phase_compliance'].values())
        total_phases = len(validation_results['phase_compliance'])

        compliance_score = 0

        # Phase compliance (60% weight)
        compliance_score += (phase_compliance / total_phases) * 0.6

        # Structure compliance (20% weight)
        if validation_results['notion_structure_compliance']:
            compliance_score += 0.2

        # Scoring formula compliance (10% weight)
        if validation_results['scoring_formula_compliance']:
            compliance_score += 0.1

        # API integration compliance (10% weight)
        if validation_results['api_integration_compliance']:
            compliance_score += 0.1

        return compliance_score >= 0.8  # 80% compliance threshold

    def _generate_compliance_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate specific recommendations to improve compliance"""

        recommendations = []

        # Phase-specific recommendations
        for phase, compliant in validation_results['phase_compliance'].items():
            if not compliant:
                phase_name = phase.replace('_', ' ').title()
                recommendations.append(f"🔄 IMPLEMENT {phase_name} according to SKILL.md specification")

        # Structure recommendations
        if not validation_results['notion_structure_compliance']:
            recommendations.append("🗄️ CONFIGURE real Notion database IDs in QA Verification Agent")

        # Scoring recommendations
        if not validation_results['scoring_formula_compliance']:
            recommendations.append("🧮 IMPLEMENT proper lead scoring formula (ICP:40%, Buying Power:30%, Engagement:30%)")

        # API recommendations
        if not validation_results['api_integration_compliance']:
            recommendations.append("🔗 INTEGRATE missing APIs (Apollo, OpenAI, Notion)")

        # Missing components
        for component in validation_results['missing_components']:
            recommendations.append(f"📋 CREATE missing component: {component}")

        # Process improvement recommendations
        recommendations.extend([
            "🚪 IMPLEMENT sequential gates (no Phase N+1 until Phase N passes QA)",
            "✅ REQUIRE QA verification before claiming task completion",
            "📊 USE transparent scoring dimensions in Notion for review/adjustment"
        ])

        return recommendations

    def _print_compliance_summary(self, validation_results: Dict):
        """Print comprehensive compliance summary"""

        print(f"\n📋 SKILL.MD COMPLIANCE REPORT")
        print("=" * 50)

        overall_status = "✅ COMPLIANT" if validation_results['overall_compliance'] else "❌ NON-COMPLIANT"
        print(f"Overall Status: {overall_status}")

        print(f"\n🔄 PHASE COMPLIANCE:")
        for phase, compliant in validation_results['phase_compliance'].items():
            status = "✅" if compliant else "❌"
            phase_name = phase.replace('_', ' ').title()
            print(f"   {status} {phase_name}")

        print(f"\n🏗️ INFRASTRUCTURE COMPLIANCE:")
        structure_status = "✅" if validation_results['notion_structure_compliance'] else "❌"
        scoring_status = "✅" if validation_results['scoring_formula_compliance'] else "❌"
        api_status = "✅" if validation_results['api_integration_compliance'] else "❌"

        print(f"   {structure_status} Notion Database Structure")
        print(f"   {scoring_status} Scoring Formula Implementation")
        print(f"   {api_status} API Integration Completeness")

        if validation_results['missing_components']:
            print(f"\n⚠️ MISSING COMPONENTS:")
            for i, component in enumerate(validation_results['missing_components'], 1):
                print(f"   {i}. {component}")

        print(f"\n🎯 COMPLIANCE RECOMMENDATIONS:")
        for i, rec in enumerate(validation_results['recommendations'], 1):
            print(f"   {i}. {rec}")

    def approve_implementation_gate(self, component_name: str) -> Dict:
        """Gate approval for implementation components"""

        print(f"\n🚪 EVALUATING IMPLEMENTATION GATE: {component_name}")

        gate_result = {
            'component': component_name,
            'approved': False,
            'blockers': [],
            'requirements_met': [],
            'timestamp': datetime.now().isoformat()
        }

        # Run compliance validation first
        compliance_results = self.validate_skill_compliance()

        if component_name == "Data Pipeline Agent":
            # Check if 5-phase implementation exists
            if all(compliance_results['phase_compliance'].values()):
                gate_result['requirements_met'].append("All 5 phases implemented")
            else:
                gate_result['blockers'].append("Missing phase implementations")

            # Check if APIs are integrated
            if compliance_results['api_integration_compliance']:
                gate_result['requirements_met'].append("API integrations complete")
            else:
                gate_result['blockers'].append("API integrations missing")

        elif component_name == "Dashboard Integration":
            # Check if Notion structure is compliant
            if compliance_results['notion_structure_compliance']:
                gate_result['requirements_met'].append("Notion database structure compliant")
            else:
                gate_result['blockers'].append("Notion database structure non-compliant")

        elif component_name == "System Integration":
            # Check overall compliance
            if compliance_results['overall_compliance']:
                gate_result['requirements_met'].append("Overall system compliance achieved")
            else:
                gate_result['blockers'].append("System not fully compliant with SKILL.md")

        # Approve if no blockers
        gate_result['approved'] = len(gate_result['blockers']) == 0

        # Print gate decision
        status = "✅ APPROVED" if gate_result['approved'] else "❌ BLOCKED"
        print(f"Gate Decision: {status}")

        if gate_result['requirements_met']:
            print("Requirements Met:")
            for req in gate_result['requirements_met']:
                print(f"   ✅ {req}")

        if gate_result['blockers']:
            print("Blockers:")
            for blocker in gate_result['blockers']:
                print(f"   🚫 {blocker}")

        return gate_result

    def generate_implementation_blueprint(self) -> Dict:
        """Generate detailed implementation blueprint based on SKILL.md"""

        print("\n📐 GENERATING IMPLEMENTATION BLUEPRINT...")

        blueprint = {
            'phases': {
                'phase_1': {
                    'name': 'Account Intelligence Baseline',
                    'required_functions': ['gather_firmographics', 'detect_trigger_events', 'assess_icp_fit'],
                    'apis_required': ['Apollo', 'Web Search'],
                    'output_format': 'Account record with ICP fit score and trigger events',
                    'qa_criteria': 'ICP fit score calculated, 3-5 trigger events detected'
                },
                'phase_2': {
                    'name': 'Contact Discovery & Segmentation',
                    'required_functions': ['apollo_contact_search', 'initial_contact_scoring', 'segment_buying_committee'],
                    'apis_required': ['Apollo'],
                    'output_format': '10-30 contacts with buying committee roles and initial scores',
                    'qa_criteria': 'Contacts segmented into 4 roles, initial lead scores calculated'
                },
                'phase_3': {
                    'name': 'High-Priority Contact Enrichment',
                    'required_functions': ['linkedin_profile_enrichment', 'activity_analysis', 'recalculate_scores'],
                    'apis_required': ['LinkedIn', 'Web Search'],
                    'output_format': 'Updated scores for contacts >60, engagement potential calculated',
                    'qa_criteria': 'Final lead scores include all 3 dimensions (ICP Fit, Buying Power, Engagement)'
                },
                'phase_4': {
                    'name': 'Engagement Intelligence',
                    'required_functions': ['map_problems_owned', 'identify_content_themes', 'diagnose_connection_pathways', 'generate_value_add_ideas'],
                    'apis_required': ['OpenAI GPT-4o-mini'],
                    'output_format': 'Actionable engagement strategies for contacts >70',
                    'qa_criteria': 'Problems/content themes tagged, 2-3 value-add ideas per high-priority contact'
                },
                'phase_5': {
                    'name': 'Strategic Partnership Intelligence',
                    'required_functions': ['scan_vendor_relationships', 'document_partnerships', 'generate_opportunity_angles'],
                    'apis_required': ['Web Search'],
                    'output_format': '3-10 strategic partnerships with Verdigris opportunity angles',
                    'qa_criteria': 'Partnerships categorized into 8 vendor categories, opportunity angles generated'
                }
            },
            'notion_databases': {
                'accounts': {
                    'required_fields': ['Company name', 'Domain', 'Employee count', 'ICP fit score', 'Account research status'],
                    'relations': ['Trigger Events', 'Contacts', 'Strategic Partnerships']
                },
                'trigger_events': {
                    'required_fields': ['Event description', 'Event type', 'Confidence', 'Relevance score', 'Source URL'],
                    'relations': ['Account']
                },
                'contacts': {
                    'required_fields': ['Name', 'Title', 'LinkedIn URL', 'Buying committee role', 'ICP Fit Score', 'Buying Power Score', 'Engagement Potential Score', 'Final Lead Score'],
                    'relations': ['Account']
                },
                'strategic_partnerships': {
                    'required_fields': ['Partner name', 'Category', 'Relationship evidence URL', 'Verdigris opportunity angle'],
                    'relations': ['Account']
                }
            },
            'sequential_gates': [
                "Phase 1 → QA verifies account baseline complete",
                "Phase 2 → QA verifies contact list populated",
                "Phase 3 → QA verifies enrichment for high-priority contacts",
                "Phase 4 → QA verifies engagement intelligence generated",
                "Phase 5 → QA verifies partnerships documented",
                "Notion Population → QA verifies all databases accessible and populated",
                "Dashboard Integration → QA verifies data flows from Notion to UI"
            ]
        }

        self._print_blueprint_summary(blueprint)
        return blueprint

    def _print_blueprint_summary(self, blueprint: Dict):
        """Print implementation blueprint summary"""

        print(f"\n📐 IMPLEMENTATION BLUEPRINT")
        print("=" * 50)

        for phase_key, phase_data in blueprint['phases'].items():
            print(f"\n🔄 {phase_data['name'].upper()}")
            print(f"   Functions: {', '.join(phase_data['required_functions'])}")
            print(f"   APIs: {', '.join(phase_data['apis_required'])}")
            print(f"   Output: {phase_data['output_format']}")
            print(f"   QA: {phase_data['qa_criteria']}")

        print(f"\n🗄️ NOTION DATABASE STRUCTURE")
        for db_name, db_spec in blueprint['notion_databases'].items():
            print(f"   {db_name.title()}: {len(db_spec['required_fields'])} fields, {len(db_spec['relations'])} relations")

        print(f"\n🚪 SEQUENTIAL GATES")
        for i, gate in enumerate(blueprint['sequential_gates'], 1):
            print(f"   {i}. {gate}")


if __name__ == "__main__":
    design_agent = ProductDesignAgent()

    # Validate current compliance
    compliance_results = design_agent.validate_skill_compliance()

    # Generate implementation blueprint
    blueprint = design_agent.generate_implementation_blueprint()