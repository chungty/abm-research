#!/usr/bin/env python3
"""
Enhanced Account Plan Generator
Creates comprehensive account plans with ICP composition, signal links, and recommended actions
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# OpenAI for custom outreach generation
try:
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    openai_available = True
except ImportError:
    openai_available = False

@dataclass
class ICPComposition:
    """ICP composition analysis"""
    total_contacts: int
    tier_1_contacts: int
    tier_2_contacts: int
    tier_3_contacts: int
    decision_makers: List[str]
    influencers: List[str]
    champions: List[str]
    icp_coverage_score: float  # 0-1 score
    missing_roles: List[str]

@dataclass
class SignalContactMapping:
    """Maps signals to relevant contacts"""
    signal_id: str
    signal_description: str
    priority_level: str
    relevant_contacts: List[str]  # Contact names who should act on this signal
    recommended_approach: str
    timing_window: str

@dataclass
class RecommendedAction:
    """Specific recommended action"""
    action_id: str
    priority: str  # "Critical", "High", "Medium", "Low"
    action_type: str  # "Immediate Outreach", "Nurture", "Research", "Meeting"
    description: str
    target_contacts: List[str]
    success_metrics: List[str]
    timeline: str
    estimated_effort: str  # "Low", "Medium", "High"

@dataclass
class AccountStrategy:
    """Overall account strategy"""
    strategy_type: str  # "Executive-Led", "Operations-Driven", etc.
    primary_value_prop: str
    key_stakeholders: List[str]
    decision_timeline: str
    budget_expectations: str
    competitive_considerations: str
    risk_factors: List[str]

@dataclass
class EnhancedAccountPlan:
    """Complete enhanced account plan"""
    account_name: str
    generated_date: str
    plan_confidence: float  # 0-1 score based on data quality
    icp_composition: ICPComposition
    signal_mappings: List[SignalContactMapping]
    recommended_actions: List[RecommendedAction]
    account_strategy: AccountStrategy
    next_review_date: str
    contact_information: Dict  # Easy reference contact info

class EnhancedAccountPlanGenerator:
    """
    Generates comprehensive account plans with ICP composition, signal links, and recommended actions
    """

    def __init__(self):
        print("📋 Initializing Enhanced Account Plan Generator")
        print("🎯 Creating comprehensive account plans with actionable intelligence")

        # Import intelligence engines
        try:
            from contact_value_analyzer import contact_value_analyzer
            from enhanced_buying_signals_analyzer import enhanced_buying_signals_analyzer
            from dashboard_data_service import notion_service

            self.contact_analyzer = contact_value_analyzer
            self.signals_analyzer = enhanced_buying_signals_analyzer
            self.data_service = notion_service

        except ImportError as e:
            print(f"⚠️ Warning: Could not import all required modules: {e}")
            self.contact_analyzer = None
            self.signals_analyzer = None
            self.data_service = None

    def generate_enhanced_account_plan(self, account_id: str = None, company_name: str = None) -> EnhancedAccountPlan:
        """
        Generate comprehensive account plan with ICP composition, signal links, and recommended actions
        """
        print(f"\n📋 Generating enhanced account plan...")
        print("=" * 60)

        # Convert account_id to string if it's a number
        if account_id is not None:
            account_id = str(account_id)

        if not self.contact_analyzer or not self.signals_analyzer or not self.data_service:
            print("❌ Required intelligence engines not available")
            return None

        try:
            # Gather all intelligence data
            account_data = self._gather_account_data(account_id, company_name)
            contacts_data = self._gather_contacts_data(account_id, company_name)
            signals_data = self._gather_signals_data(account_id, company_name)
            partnerships_data = self._gather_partnerships_data(account_id, company_name)

            if not account_data or not contacts_data:
                print("❌ Insufficient data for account plan generation")
                return None

            # Generate plan components
            icp_composition = self._analyze_icp_composition(contacts_data, account_data)
            signal_mappings = self._map_signals_to_contacts(signals_data, contacts_data)
            recommended_actions = self._generate_recommended_actions(
                icp_composition, signal_mappings, contacts_data, signals_data
            )
            account_strategy = self._develop_account_strategy(
                account_data, contacts_data, signals_data, partnerships_data, icp_composition
            )

            # Create contact information reference
            contact_info = self._create_contact_reference(contacts_data)

            # Calculate plan confidence
            plan_confidence = self._calculate_plan_confidence(
                contacts_data, signals_data, icp_composition
            )

            # Create comprehensive account plan
            account_plan = EnhancedAccountPlan(
                account_name=account_data.get('name', 'Unknown Company'),
                generated_date=datetime.now().isoformat(),
                plan_confidence=plan_confidence,
                icp_composition=icp_composition,
                signal_mappings=signal_mappings,
                recommended_actions=recommended_actions,
                account_strategy=account_strategy,
                next_review_date=(datetime.now() + timedelta(days=30)).isoformat(),
                contact_information=contact_info
            )

            # Print summary
            plan_dict = asdict(account_plan)
            self._print_account_plan_summary(plan_dict)

            return account_plan

        except Exception as e:
            print(f"❌ Error generating account plan: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _gather_account_data(self, account_id: str, company_name: str) -> Optional[Dict]:
        """Gather account data"""
        try:
            accounts = self.data_service.fetch_accounts()

            if account_id:
                return next((acc for acc in accounts if acc.get('id') == account_id), None)
            elif company_name:
                return next((acc for acc in accounts if acc.get('name') == company_name), None)
            else:
                return accounts[0] if accounts else None

        except Exception as e:
            print(f"⚠️ Error gathering account data: {e}")
            return None

    def _gather_contacts_data(self, account_id: str, company_name: str) -> List[Dict]:
        """Gather contacts with value analysis"""
        try:
            # Get raw contacts
            contacts = self.data_service.fetch_contacts(account_id)

            # Filter by company name if specified
            if company_name and not account_id:
                contacts = [c for c in contacts if c.get('company_name') == company_name]

            # Run contact value analysis
            if contacts:
                account_data = self._gather_account_data(account_id, company_name)
                value_analysis = self.contact_analyzer.analyze_contact_value(contacts, account_data)
                return value_analysis.get('contact_values', [])

            return []

        except Exception as e:
            print(f"⚠️ Error gathering contacts data: {e}")
            return []

    def _gather_signals_data(self, account_id: str, company_name: str) -> List[Dict]:
        """Gather enhanced buying signals"""
        try:
            # Get basic events first
            events = self.data_service.fetch_trigger_events(account_id)

            # Filter by company name if specified
            if company_name and not account_id:
                events = [e for e in events if e.get('company_name') == company_name]

            # Enhance with signals analyzer
            if events:
                account_data = self._gather_account_data(account_id, company_name)
                enhanced_signals = self.signals_analyzer.analyze_buying_signals(events, account_data)
                return self.signals_analyzer.convert_to_dashboard_format(enhanced_signals)

            return []

        except Exception as e:
            print(f"⚠️ Error gathering signals data: {e}")
            return []

    def _gather_partnerships_data(self, account_id: str, company_name: str) -> List[Dict]:
        """Gather partnerships data"""
        try:
            partnerships = self.data_service.fetch_partnerships()

            # Filter by company name
            if company_name:
                partnerships = [p for p in partnerships if p.get('target_company') == company_name]

            return partnerships

        except Exception as e:
            print(f"⚠️ Error gathering partnerships data: {e}")
            return []

    def _analyze_icp_composition(self, contacts_data: List[Dict], account_data: Dict) -> ICPComposition:
        """Analyze ICP composition from contact value analysis"""

        total_contacts = len(contacts_data)
        if total_contacts == 0:
            return ICPComposition(
                total_contacts=0, tier_1_contacts=0, tier_2_contacts=0, tier_3_contacts=0,
                decision_makers=[], influencers=[], champions=[],
                icp_coverage_score=0.0, missing_roles=[]
            )

        # Count by tier
        tier_1_contacts = len([c for c in contacts_data if c.get('value_tier') == 'Tier 1'])
        tier_2_contacts = len([c for c in contacts_data if c.get('value_tier') == 'Tier 2'])
        tier_3_contacts = len([c for c in contacts_data if c.get('value_tier') == 'Tier 3'])

        # Categorize by buying influence
        decision_makers = []
        influencers = []
        champions = []

        for contact in contacts_data:
            name = contact.get('name', 'Unknown')
            role_analysis = contact.get('role_analysis', {})
            buying_influence = role_analysis.get('buying_influence', 'User')

            if buying_influence == 'Decision Maker':
                decision_makers.append(name)
            elif buying_influence == 'Influencer':
                influencers.append(name)
            elif buying_influence == 'Champion':
                champions.append(name)

        # Calculate ICP coverage score
        required_roles = {'Decision Maker': 1, 'Influencer': 1, 'Champion': 1}
        found_roles = {'Decision Maker': len(decision_makers), 'Influencer': len(influencers), 'Champion': len(champions)}

        coverage_score = sum(min(found_roles[role], required) for role, required in required_roles.items()) / sum(required_roles.values())

        # Identify missing roles
        missing_roles = [role for role, required in required_roles.items() if found_roles[role] < required]

        return ICPComposition(
            total_contacts=total_contacts,
            tier_1_contacts=tier_1_contacts,
            tier_2_contacts=tier_2_contacts,
            tier_3_contacts=tier_3_contacts,
            decision_makers=decision_makers,
            influencers=influencers,
            champions=champions,
            icp_coverage_score=coverage_score,
            missing_roles=missing_roles
        )

    def _map_signals_to_contacts(self, signals_data: List[Dict], contacts_data: List[Dict]) -> List[SignalContactMapping]:
        """Map buying signals to relevant contacts"""

        mappings = []

        for signal in signals_data:
            signal_id = signal.get('id', f"signal_{len(mappings)}")
            description = signal.get('description', 'Unknown Signal')
            priority_level = signal.get('priority_level', 'Medium')

            # Find relevant contacts based on signal type and contact roles
            relevant_contacts = self._find_relevant_contacts_for_signal(signal, contacts_data)

            # Generate recommended approach
            approach = self._generate_signal_approach(signal, relevant_contacts)

            # Determine timing window
            timing_window = signal.get('timing_recommendation', 'Contact within 2-4 weeks')

            mapping = SignalContactMapping(
                signal_id=signal_id,
                signal_description=description,
                priority_level=priority_level,
                relevant_contacts=relevant_contacts,
                recommended_approach=approach,
                timing_window=timing_window
            )

            mappings.append(mapping)

        return mappings

    def _find_relevant_contacts_for_signal(self, signal: Dict, contacts_data: List[Dict]) -> List[str]:
        """Find contacts most relevant to a specific signal"""

        relevant_contacts = []
        signal_description = signal.get('description', '').lower()
        verdigris_relevance = signal.get('verdigris_relevance', '').lower()

        # Prioritize high-value contacts
        high_value_contacts = [c for c in contacts_data if c.get('value_tier') in ['Tier 1', 'Tier 2']]

        for contact in high_value_contacts:
            name = contact.get('name', 'Unknown')
            role_analysis = contact.get('role_analysis', {})
            department = role_analysis.get('department', '').lower()
            buying_influence = role_analysis.get('buying_influence', '')

            # Match signal to contact relevance
            relevance_score = 0

            # Department matching
            if 'energy' in signal_description and department in ['operations', 'facilities', 'sustainability']:
                relevance_score += 2
            elif 'technology' in signal_description and department in ['engineering', 'it']:
                relevance_score += 2
            elif 'cost' in signal_description and department in ['finance', 'operations']:
                relevance_score += 2

            # Role influence matching
            if buying_influence in ['Decision Maker', 'Champion']:
                relevance_score += 1

            # Verdigris solution relevance
            if any(keyword in verdigris_relevance for keyword in ['energy', 'monitoring', 'efficiency']):
                if department in ['operations', 'facilities', 'sustainability']:
                    relevance_score += 1

            if relevance_score >= 2:
                relevant_contacts.append(name)

        # Ensure we have at least one contact if possible
        if not relevant_contacts and high_value_contacts:
            # Default to highest-value decision maker
            decision_maker = next((c for c in high_value_contacts
                                 if c.get('role_analysis', {}).get('buying_influence') == 'Decision Maker'), None)
            if decision_maker:
                relevant_contacts.append(decision_maker.get('name', 'Unknown'))

        return relevant_contacts[:3]  # Limit to top 3 relevant contacts

    def _generate_signal_approach(self, signal: Dict, relevant_contacts: List[str]) -> str:
        """Generate recommended approach for a signal"""

        priority = signal.get('priority_level', 'Medium')
        sales_angle = signal.get('sales_angle', '')
        verdigris_relevance = signal.get('verdigris_relevance', '')

        if priority == 'Critical':
            return f"Immediate outreach to {', '.join(relevant_contacts[:2])} with focus on {sales_angle}. Reference specific trigger event and Verdigris value: {verdigris_relevance[:100]}..."
        elif priority == 'High':
            return f"Schedule meetings with {', '.join(relevant_contacts)} within 1 week. Lead with {sales_angle} and emphasize {verdigris_relevance[:100]}..."
        else:
            return f"Nurture {', '.join(relevant_contacts)} with relevant content. Focus on {verdigris_relevance[:100]}... when ready for deeper engagement."

    def _generate_recommended_actions(self, icp_composition: ICPComposition,
                                    signal_mappings: List[SignalContactMapping],
                                    contacts_data: List[Dict],
                                    signals_data: List[Dict]) -> List[RecommendedAction]:
        """Generate specific recommended actions"""

        actions = []
        action_id = 1

        # Critical signal actions
        critical_mappings = [m for m in signal_mappings if m.priority_level == 'Critical']
        for mapping in critical_mappings:
            action = RecommendedAction(
                action_id=f"action_{action_id}",
                priority="Critical",
                action_type="Immediate Outreach",
                description=f"Immediate outreach for: {mapping.signal_description}",
                target_contacts=mapping.relevant_contacts,
                success_metrics=["Response received", "Meeting scheduled", "Interest confirmed"],
                timeline="24-48 hours",
                estimated_effort="Medium"
            )
            actions.append(action)
            action_id += 1

        # High-value contact engagement
        tier_1_contacts = [c for c in contacts_data if c.get('value_tier') == 'Tier 1']
        if tier_1_contacts:
            for contact in tier_1_contacts[:3]:  # Top 3 Tier 1 contacts
                action = RecommendedAction(
                    action_id=f"action_{action_id}",
                    priority="High",
                    action_type="Strategic Engagement",
                    description=f"Strategic engagement with {contact.get('name')} - {contact.get('role_analysis', {}).get('title', 'Key Contact')}",
                    target_contacts=[contact.get('name')],
                    success_metrics=["Executive briefing scheduled", "Technical evaluation initiated", "Budget discussion"],
                    timeline="1-2 weeks",
                    estimated_effort="High"
                )
                actions.append(action)
                action_id += 1

        # ICP gap filling
        if icp_composition.missing_roles:
            action = RecommendedAction(
                action_id=f"action_{action_id}",
                priority="Medium",
                action_type="Research",
                description=f"Identify and connect with missing roles: {', '.join(icp_composition.missing_roles)}",
                target_contacts=["Team Research"],
                success_metrics=["Missing contacts identified", "Introductions arranged", "Expanded network"],
                timeline="2-4 weeks",
                estimated_effort="Medium"
            )
            actions.append(action)
            action_id += 1

        # Nurture actions for Tier 2 contacts
        tier_2_contacts = [c for c in contacts_data if c.get('value_tier') == 'Tier 2']
        if tier_2_contacts:
            action = RecommendedAction(
                action_id=f"action_{action_id}",
                priority="Medium",
                action_type="Nurture",
                description=f"Content nurture campaign for {len(tier_2_contacts)} Tier 2 contacts",
                target_contacts=[c.get('name') for c in tier_2_contacts[:5]],
                success_metrics=["Content engagement", "LinkedIn activity", "Response to outreach"],
                timeline="4-8 weeks",
                estimated_effort="Low"
            )
            actions.append(action)
            action_id += 1

        return actions

    def _develop_account_strategy(self, account_data: Dict, contacts_data: List[Dict],
                                signals_data: List[Dict], partnerships_data: List[Dict],
                                icp_composition: ICPComposition) -> AccountStrategy:
        """Develop overall account strategy"""

        # Determine strategy type from organizational pattern
        decision_makers = len([c for c in contacts_data if c.get('role_analysis', {}).get('buying_influence') == 'Decision Maker'])

        if decision_makers >= 3:
            strategy_type = "Executive-Led Consensus"
            decision_timeline = "3-6 months"
        elif any('operations' in c.get('role_analysis', {}).get('department', '').lower() for c in contacts_data):
            strategy_type = "Operations-Driven"
            decision_timeline = "2-4 months"
        else:
            strategy_type = "Technical Evaluation"
            decision_timeline = "4-6 months"

        # Determine primary value prop
        if signals_data and any('energy' in s.get('description', '').lower() for s in signals_data):
            primary_value_prop = "Energy cost reduction and operational efficiency through intelligent monitoring"
        elif signals_data and any('sustainability' in s.get('description', '').lower() for s in signals_data):
            primary_value_prop = "ESG compliance and sustainability metrics through comprehensive energy analytics"
        else:
            primary_value_prop = "Operational intelligence and cost optimization through AI-powered energy monitoring"

        # Key stakeholders
        key_stakeholders = []
        for contact in contacts_data:
            if contact.get('value_tier') in ['Tier 1', 'Tier 2']:
                role_info = contact.get('role_analysis', {})
                stakeholder_info = f"{contact.get('name')} ({role_info.get('department', 'Unknown')} - {role_info.get('buying_influence', 'Contact')})"
                key_stakeholders.append(stakeholder_info)

        # Budget expectations
        employee_count = account_data.get('employee_count', 100)
        if employee_count >= 500:
            budget_expectations = "$50K-200K+ annual - Enterprise scale implementation"
        elif employee_count >= 100:
            budget_expectations = "$20K-50K annual - Mid-market solution"
        else:
            budget_expectations = "$10K-20K annual - SMB focused deployment"

        # Competitive considerations
        competitive_considerations = "Monitor for competing energy management solutions. Emphasize AI differentiation and ROI speed."

        # Risk factors
        risk_factors = []
        if icp_composition.icp_coverage_score < 0.5:
            risk_factors.append("Incomplete buying committee - missing key stakeholders")
        if not signals_data:
            risk_factors.append("Limited trigger events - may indicate low urgency")
        if len([c for c in contacts_data if c.get('engagement_readiness') == 'Ready']) == 0:
            risk_factors.append("No ready-to-engage contacts - requires nurturing phase")

        return AccountStrategy(
            strategy_type=strategy_type,
            primary_value_prop=primary_value_prop,
            key_stakeholders=key_stakeholders[:5],  # Top 5 stakeholders
            decision_timeline=decision_timeline,
            budget_expectations=budget_expectations,
            competitive_considerations=competitive_considerations,
            risk_factors=risk_factors or ["Standard competitive and timing risks"]
        )

    def _create_contact_reference(self, contacts_data: List[Dict]) -> Dict:
        """Create easy reference contact information"""

        contact_reference = {
            'tier_1_contacts': [],
            'tier_2_contacts': [],
            'decision_makers': [],
            'quick_reference': {}
        }

        for contact in contacts_data:
            name = contact.get('name', 'Unknown')
            role_analysis = contact.get('role_analysis', {})

            contact_info = {
                'name': name,
                'title': role_analysis.get('title', 'Unknown Title'),
                'department': role_analysis.get('department', 'Unknown'),
                'email': contact.get('email', ''),
                'linkedin_url': contact.get('linkedin_url', ''),
                'phone_number': contact.get('phone_number', ''),
                'buying_influence': role_analysis.get('buying_influence', 'User'),
                'engagement_readiness': contact.get('engagement_readiness', 'Cold'),
                'value_tier': contact.get('value_tier', 'Tier 3')
            }

            # Categorize contacts
            if contact.get('value_tier') == 'Tier 1':
                contact_reference['tier_1_contacts'].append(contact_info)
            elif contact.get('value_tier') == 'Tier 2':
                contact_reference['tier_2_contacts'].append(contact_info)

            if role_analysis.get('buying_influence') == 'Decision Maker':
                contact_reference['decision_makers'].append(contact_info)

            # Quick reference by name
            contact_reference['quick_reference'][name] = contact_info

        return contact_reference

    def _calculate_plan_confidence(self, contacts_data: List[Dict], signals_data: List[Dict],
                                 icp_composition: ICPComposition) -> float:
        """Calculate confidence score for the account plan"""

        confidence_factors = []

        # Contact data quality
        if len(contacts_data) >= 5:
            confidence_factors.append(0.3)
        elif len(contacts_data) >= 3:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)

        # ICP coverage
        confidence_factors.append(icp_composition.icp_coverage_score * 0.3)

        # Signal quality
        if len(signals_data) >= 3:
            confidence_factors.append(0.2)
        elif len(signals_data) >= 1:
            confidence_factors.append(0.15)
        else:
            confidence_factors.append(0.05)

        # Engagement readiness
        ready_contacts = len([c for c in contacts_data if c.get('engagement_readiness') == 'Ready'])
        if ready_contacts >= 2:
            confidence_factors.append(0.2)
        elif ready_contacts >= 1:
            confidence_factors.append(0.15)
        else:
            confidence_factors.append(0.1)

        return sum(confidence_factors)

    def _print_account_plan_summary(self, plan_dict: Dict):
        """Print comprehensive account plan summary"""

        print(f"\n📋 ENHANCED ACCOUNT PLAN SUMMARY")
        print("=" * 60)

        print(f"🏢 Account: {plan_dict['account_name']}")
        print(f"📅 Generated: {plan_dict['generated_date'][:19]}")
        print(f"🎯 Plan Confidence: {plan_dict['plan_confidence']:.1%}")
        print(f"📋 Next Review: {plan_dict['next_review_date'][:10]}")

        icp = plan_dict['icp_composition']
        print(f"\n👥 ICP COMPOSITION")
        print(f"   Total Contacts: {icp['total_contacts']}")
        print(f"   Tier 1: {icp['tier_1_contacts']}, Tier 2: {icp['tier_2_contacts']}")
        print(f"   Decision Makers: {len(icp['decision_makers'])}")
        print(f"   ICP Coverage: {icp['icp_coverage_score']:.1%}")
        if icp['missing_roles']:
            print(f"   Missing Roles: {', '.join(icp['missing_roles'])}")

        signals = plan_dict['signal_mappings']
        print(f"\n📊 SIGNAL-CONTACT MAPPINGS")
        print(f"   Total Signals: {len(signals)}")
        critical_signals = [s for s in signals if s['priority_level'] == 'Critical']
        if critical_signals:
            print(f"   Critical Signals: {len(critical_signals)}")
            for signal in critical_signals[:2]:
                print(f"     • {signal['signal_description'][:60]}...")

        actions = plan_dict['recommended_actions']
        print(f"\n🎯 RECOMMENDED ACTIONS ({len(actions)} total)")
        for action in actions:
            print(f"   {action['priority']:8} | {action['action_type']:18} | {action['timeline']}")
            print(f"            {action['description'][:70]}...")

        strategy = plan_dict['account_strategy']
        print(f"\n🏛️ ACCOUNT STRATEGY")
        print(f"   Strategy Type: {strategy['strategy_type']}")
        print(f"   Timeline: {strategy['decision_timeline']}")
        print(f"   Budget Range: {strategy['budget_expectations']}")
        print(f"   Key Stakeholders: {len(strategy['key_stakeholders'])}")
        if strategy['risk_factors']:
            print(f"   Risk Factors: {len(strategy['risk_factors'])}")

        contact_info = plan_dict['contact_information']
        print(f"\n📞 CONTACT REFERENCE")
        print(f"   Tier 1 Contacts: {len(contact_info['tier_1_contacts'])}")
        print(f"   Tier 2 Contacts: {len(contact_info['tier_2_contacts'])}")
        print(f"   Decision Makers: {len(contact_info['decision_makers'])}")

# Export for use by other modules
enhanced_account_plan_generator = EnhancedAccountPlanGenerator()

def main():
    """Test the enhanced account plan generator"""
    print("📋 Enhanced Account Plan Generator initialized")
    print("💡 Use generate_enhanced_account_plan() method to create comprehensive plans")

if __name__ == "__main__":
    main()
