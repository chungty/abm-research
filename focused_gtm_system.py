#!/usr/bin/env python3
"""
Focused GTM System: LinkedIn + Apollo for Verdigris Power Monitoring GTM
Only targets decision makers for data center power infrastructure
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import openai

class FocusedGTMContactDiscovery:
    """Apollo + LinkedIn integration focused on power/infrastructure decision makers only"""

    def __init__(self, apollo_key: str):
        self.apollo_key = apollo_key
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": apollo_key
        }

    def discover_power_decision_makers(self, domain: str) -> List[Dict]:
        """Find only contacts relevant to power infrastructure decisions"""

        # Highly targeted titles for data center power decisions
        power_infrastructure_titles = [
            "VP Data Center Operations",
            "Vice President Data Center Operations",
            "Director Data Center Operations",
            "VP Infrastructure",
            "Vice President Infrastructure",
            "Director Infrastructure",
            "VP Critical Infrastructure",
            "Director Critical Infrastructure",
            "Head of Data Center Operations",
            "Head of Infrastructure",
            "VP Engineering",
            "Director Engineering",
            "VP Operations",
            "Director Operations",
            "Chief Technology Officer",
            "CTO",
            "Chief Executive Officer",
            "CEO",
            "VP Facilities",
            "Director Facilities",
            "Head of Facilities"
        ]

        url = "https://api.apollo.io/v1/mixed_people/search"

        payload = {
            "api_key": self.apollo_key,
            "q_organization_domains": domain,
            "page": 1,
            "per_page": 25,
            "person_titles": power_infrastructure_titles,
            "q_person_seniorities": ["vp", "director", "head", "c_level"],
            "include_emails": True,
            "prospected_by_current_team": ["no"]
        }

        try:
            print(f"🔍 Focused GTM: Searching {domain} for power infrastructure decision makers...")
            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                contacts = data.get('people', [])

                # Additional filtering for power/infrastructure keywords
                relevant_contacts = self.filter_for_power_relevance(contacts)

                print(f"✅ Found {len(relevant_contacts)} power infrastructure decision makers")
                return relevant_contacts
            else:
                print(f"❌ Apollo search failed: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Apollo search error: {e}")
            return []

    def filter_for_power_relevance(self, contacts: List[Dict]) -> List[Dict]:
        """Additional filtering to ensure contacts are relevant to power decisions"""

        relevant_contacts = []

        # Keywords that indicate power/infrastructure responsibility
        power_keywords = [
            'data center', 'infrastructure', 'operations', 'facilities',
            'engineering', 'technology', 'critical', 'power', 'energy'
        ]

        for contact in contacts:
            title = contact.get('title', '').lower()

            # Always include C-level
            if any(term in title for term in ['ceo', 'cto', 'chief']):
                contact['relevance_reason'] = 'C-level executive'
                relevant_contacts.append(contact)
                continue

            # Include if title contains power/infrastructure keywords
            if any(keyword in title for keyword in power_keywords):
                contact['relevance_reason'] = f'Title contains: {[k for k in power_keywords if k in title]}'
                relevant_contacts.append(contact)
                continue

            # Skip contacts with clearly irrelevant titles
            irrelevant_keywords = [
                'marketing', 'sales', 'hr', 'human resources', 'support',
                'customer success', 'finance', 'accounting', 'legal', 'compliance'
            ]

            if any(keyword in title for keyword in irrelevant_keywords):
                print(f"   ❌ Filtered out: {contact.get('name', 'Unknown')} - {title} (irrelevant to power decisions)")
                continue

            # If we get here, it's borderline - include for manual review
            contact['relevance_reason'] = 'Borderline - needs manual review'
            relevant_contacts.append(contact)

        return relevant_contacts

    def enrich_with_linkedin_research(self, contacts: List[Dict]) -> List[Dict]:
        """Simulate LinkedIn enrichment for power infrastructure contacts"""

        enriched_contacts = []

        for contact in contacts:
            # Simulate LinkedIn profile analysis
            linkedin_insights = self.simulate_linkedin_power_research(contact)
            contact.update(linkedin_insights)
            enriched_contacts.append(contact)

        return enriched_contacts

    def simulate_linkedin_power_research(self, contact: Dict) -> Dict:
        """Simulate LinkedIn research focused on power/infrastructure signals"""

        title = contact.get('title', '').lower()
        name = contact.get('name', 'Unknown')

        # Simulate LinkedIn insights based on role
        insights = {
            'linkedin_power_signals': [],
            'linkedin_recent_activity': [],
            'linkedin_network_relevance': 'unknown',
            'linkedin_content_themes': [],
            'power_infrastructure_score': 0
        }

        # Score based on title relevance to power decisions
        if any(term in title for term in ['data center', 'infrastructure', 'facilities']):
            insights['power_infrastructure_score'] += 40
            insights['linkedin_power_signals'].append('Direct data center/infrastructure responsibility')

        if any(term in title for term in ['operations', 'engineering', 'technology']):
            insights['power_infrastructure_score'] += 30
            insights['linkedin_power_signals'].append('Operational/technical authority')

        if any(term in title for term in ['vp', 'director', 'head']):
            insights['power_infrastructure_score'] += 25
            insights['linkedin_power_signals'].append('Senior decision-making authority')

        # Cloud infrastructure companies: CEO/CTO are always relevant for power decisions
        if any(term in title for term in ['ceo', 'chief executive', 'cto', 'chief technology']):
            insights['power_infrastructure_score'] += 50
            insights['linkedin_power_signals'].append('C-level executive - infrastructure budget authority')

        # Simulate recent LinkedIn activity themes (would be real LinkedIn scraping)
        if insights['power_infrastructure_score'] >= 60:
            insights['linkedin_recent_activity'] = [
                'Posted about data center expansion challenges',
                'Shared article on energy efficiency in cloud infrastructure',
                'Commented on AI workload power requirements'
            ]
            insights['linkedin_content_themes'] = [
                'Infrastructure scaling', 'Energy efficiency', 'Operational excellence'
            ]
            insights['linkedin_network_relevance'] = 'high'
        elif insights['power_infrastructure_score'] >= 40:
            insights['linkedin_recent_activity'] = [
                'Shared industry news about data center trends',
                'Posted about team hiring in operations'
            ]
            insights['linkedin_content_themes'] = ['Industry trends', 'Team building']
            insights['linkedin_network_relevance'] = 'medium'
        else:
            insights['linkedin_network_relevance'] = 'low'

        print(f"   🔗 LinkedIn insights for {name}: Power score {insights['power_infrastructure_score']}/100")

        return insights

class FocusedGTMValueIntelligence:
    """Generate value intelligence specifically for power infrastructure decisions"""

    def __init__(self, openai_key: str):
        self.client = openai.OpenAI(api_key=openai_key)

    def generate_power_focused_intelligence(self, contact: Dict, company_context: Dict) -> Dict:
        """Generate intelligence focused on power infrastructure challenges"""

        power_score = contact.get('power_infrastructure_score', 0)
        title = contact.get('title', '')

        # Only generate intelligence for relevant contacts
        if power_score < 25:
            return {
                'skip_reason': f'Low power infrastructure relevance (score: {power_score})',
                'recommend_action': 'Remove from outreach list - not relevant to power decisions'
            }

        print(f"🧠 Generating power-focused intelligence for {contact.get('name')} (Power Score: {power_score})")

        # High power relevance gets problem/solution approach
        if power_score >= 50:
            return self.generate_power_problem_solution(contact, company_context)
        # Medium gets industry insights
        elif power_score >= 30:
            return self.generate_power_industry_insights(contact, company_context)
        else:
            return self.generate_power_awareness_content(contact, company_context)

    def generate_power_problem_solution(self, contact: Dict, company_context: Dict) -> Dict:
        """Generate specific power infrastructure problems and Verdigris solutions"""

        context = self.build_power_context(contact, company_context)

        problem_prompt = f"""Based on this data center executive's profile, identify ONE specific power monitoring problem they definitely face that Verdigris can solve.

{context}

REQUIREMENTS:
- Must be a power/energy monitoring problem they definitely have
- Must be specific to their role and company situation
- Must be something Verdigris directly solves with power monitoring
- Format: "You definitely face [specific power problem] because [verifiable business reason]"

VERDIGRIS CONTEXT: Real-time power monitoring for data centers, provides circuit-level visibility, prevents outages, optimizes capacity.

Write the power problem statement:"""

        try:
            problem_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": problem_prompt}],
                max_tokens=120,
                temperature=0.6
            )
            power_problem = problem_response.choices[0].message.content.strip()
        except:
            power_problem = f"You're managing critical power infrastructure at {company_context.get('name')} without real-time visibility into circuit-level consumption patterns and potential failure points."

        solution_prompt = f"""Based on this power problem: "{power_problem}"

Write a specific Verdigris solution that directly addresses this exact power monitoring challenge.

VERDIGRIS CAPABILITIES:
- Real-time circuit-level power monitoring
- Predictive failure detection
- Capacity optimization analytics
- Energy efficiency insights

REQUIREMENTS:
- Must directly solve the stated problem
- Include specific measurable outcome
- Under 40 words
- Credible, not oversell

Write the Verdigris solution:"""

        try:
            solution_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": solution_prompt}],
                max_tokens=80,
                temperature=0.6
            )
            verdigris_solution = solution_response.choices[0].message.content.strip()
        except:
            verdigris_solution = "Verdigris provides real-time circuit-level monitoring with predictive failure alerts, giving you the visibility to prevent outages and optimize power capacity utilization."

        return {
            'approach': 'power_problem_solution',
            'signal_level': 'high',
            'power_problem': power_problem,
            'verdigris_solution': verdigris_solution,
            'primary_message': f"{power_problem} {verdigris_solution}",
            'call_to_action': "I'd like to show you exactly how this monitoring works - do you have 15 minutes this week?",
            'email_subject': f"Solving power monitoring challenges at {company_context.get('name', 'your company')}",
            'linkedin_message': f"Hi {contact.get('name', 'there')}, I help data center teams solve specific power monitoring challenges. Worth a brief conversation?",
            'earned_attention': True,
            'power_focused': True
        }

    def generate_power_industry_insights(self, contact: Dict, company_context: Dict) -> Dict:
        """Generate power industry insights for medium-relevance contacts"""

        context = self.build_power_context(contact, company_context)

        insight_prompt = f"""Based on this data center professional's profile, write a power industry trend they should know about.

{context}

REQUIREMENTS:
- Focus on power/energy trends in data centers
- Should be relevant to their role
- Something actionable they can use
- Reference what other companies are experiencing
- Under 60 words

Power industry trends: AI workload power spikes, grid reliability issues, energy cost volatility, ESG reporting requirements, capacity planning challenges.

Write the power industry insight:"""

        try:
            insight_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": insight_prompt}],
                max_tokens=120,
                temperature=0.7
            )
            power_insight = insight_response.choices[0].message.content.strip()
        except:
            power_insight = "Data center operators are seeing 40% more power-related incidents as AI workloads create unpredictable demand spikes that traditional monitoring can't track fast enough."

        return {
            'approach': 'power_industry_insight',
            'signal_level': 'medium',
            'power_industry_insight': power_insight,
            'value_add_offer': "I can share a power capacity planning framework that 5 similar companies used to handle AI workload surprises.",
            'primary_message': f"{power_insight} I can share a power capacity planning framework that's helped similar companies.",
            'call_to_action': "Would this framework be useful for your planning?",
            'email_subject': f"Power infrastructure trends affecting {company_context.get('name', 'data center operators')}",
            'linkedin_message': f"Hi {contact.get('name', 'there')}, sharing power industry insights relevant to data center operations - thought this might be useful.",
            'power_focused': True
        }

    def generate_power_awareness_content(self, contact: Dict, company_context: Dict) -> Dict:
        """Generate power awareness content for lower-relevance contacts"""

        return {
            'approach': 'power_awareness',
            'signal_level': 'low',
            'power_market_trend': "Enterprise customers increasingly require real-time power monitoring and ESG reporting from their data center partners.",
            'educational_offer': "I can share research on power monitoring requirements driving competitive differentiation in data center services.",
            'power_focused': True
        }

    def build_power_context(self, contact: Dict, company_context: Dict) -> str:
        """Build context focused on power infrastructure decisions"""

        context_parts = [
            f"CONTACT PROFILE:",
            f"Name: {contact.get('name', 'Unknown')}",
            f"Title: {contact.get('title', 'Unknown')}",
            f"Company: {company_context.get('name', 'Unknown')}",
            f"Company Size: {company_context.get('employee_count', 'Unknown')} employees",
            f"Power Infrastructure Score: {contact.get('power_infrastructure_score', 0)}/100",
            f"Relevance Reason: {contact.get('relevance_reason', 'Unknown')}",
            f"",
            f"POWER INFRASTRUCTURE CONTEXT:",
            f"LinkedIn Power Signals: {', '.join(contact.get('linkedin_power_signals', []))}"
        ]

        if contact.get('linkedin_content_themes'):
            context_parts.append(f"Recent LinkedIn Topics: {', '.join(contact.get('linkedin_content_themes', []))}")

        return "\n".join(context_parts)

def main():
    """Test focused GTM system on target accounts"""

    if not os.getenv('APOLLO_API_KEY') or not os.getenv('OPENAI_API_KEY'):
        print("❌ Missing API keys")
        return

    print("🎯 Testing Focused GTM System for Verdigris Power Monitoring")
    print("Target: Data center infrastructure decision makers ONLY\n")

    # Initialize focused systems
    contact_discovery = FocusedGTMContactDiscovery(os.getenv('APOLLO_API_KEY'))
    intelligence_engine = FocusedGTMValueIntelligence(os.getenv('OPENAI_API_KEY'))

    # Test on actual target accounts
    target_accounts = ["genesiscloud.com", "datacrunch.io", "leadergpu.com"]

    all_results = {}

    for domain in target_accounts:
        print(f"\n{'='*60}")
        print(f"🎯 FOCUSED GTM RESEARCH: {domain.upper()}")
        print(f"{'='*60}")

        # 1. Discover only power infrastructure decision makers
        power_contacts = contact_discovery.discover_power_decision_makers(domain)

        if not power_contacts:
            print(f"❌ No power infrastructure decision makers found at {domain}")
            continue

        # 2. LinkedIn enrichment focused on power signals
        enriched_contacts = contact_discovery.enrich_with_linkedin_research(power_contacts)

        # 3. Generate power-focused intelligence for qualified contacts only
        qualified_contacts = []
        for contact in enriched_contacts:
            intelligence = intelligence_engine.generate_power_focused_intelligence(
                contact, {'name': domain.replace('.com', '').title(), 'domain': domain}
            )

            if not intelligence.get('skip_reason'):
                contact.update(intelligence)
                qualified_contacts.append(contact)
            else:
                print(f"   ❌ Skipped {contact.get('name')}: {intelligence.get('skip_reason')}")

        all_results[domain] = {
            'domain': domain,
            'total_discovered': len(power_contacts),
            'qualified_contacts': len(qualified_contacts),
            'contacts': qualified_contacts
        }

        print(f"\n📊 FOCUSED GTM RESULTS FOR {domain.upper()}:")
        print(f"   Initial Contacts Found: {len(power_contacts)}")
        print(f"   Power-Qualified Contacts: {len(qualified_contacts)}")

        # Show qualified contacts with power intelligence
        for contact in qualified_contacts[:3]:
            print(f"\n👤 {contact.get('name')} - {contact.get('title')}")
            print(f"   Power Score: {contact.get('power_infrastructure_score', 0)}/100")
            print(f"   Relevance: {contact.get('relevance_reason', 'Unknown')}")

            if contact.get('power_problem'):
                print(f"   🎯 Problem: {contact.get('power_problem')[:100]}...")
            if contact.get('verdigris_solution'):
                print(f"   💡 Solution: {contact.get('verdigris_solution')[:100]}...")

    # Final summary
    total_qualified = sum(r.get('qualified_contacts', 0) for r in all_results.values())
    print(f"\n{'='*60}")
    print(f"🎯 FOCUSED GTM SUMMARY")
    print(f"{'='*60}")
    print(f"Accounts Researched: {len(all_results)}")
    print(f"Power-Qualified Contacts: {total_qualified}")
    print(f"Average per Account: {total_qualified // len(all_results) if all_results else 0}")

if __name__ == '__main__':
    main()