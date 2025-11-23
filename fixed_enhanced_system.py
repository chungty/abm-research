#!/usr/bin/env python3
"""
Fixed Enhanced ABM System - Corrected Apollo API usage + OpenAI Integration
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import openai

class FixedEnhancedApolloAPI:
    """Apollo API with corrected bulk enrichment and individual enrichment"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }

    def search_people_enhanced(self, domain: str) -> List[Dict]:
        """Enhanced people search with phone numbers and personal emails"""

        url = f"{self.base_url}/mixed_people/search"

        payload = {
            "api_key": self.api_key,
            "q_organization_domains": domain,
            "page": 1,
            "per_page": 25,
            "person_titles": [
                "VP Data Center Operations", "Director Data Center", "VP Infrastructure",
                "Director Infrastructure", "Head of Data Center", "VP Critical Infrastructure",
                "Director Operations", "VP Operations", "Manager Data Center"
            ],
            "q_person_seniorities": ["vp", "director", "manager", "head", "c_level"],
            "include_emails": True,
            "include_phone_numbers": True,  # Request phone numbers
            "prospected_by_current_team": ["no"]
        }

        try:
            print(f"🔍 Apollo Enhanced: Searching {domain}...")
            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                contacts = data.get('people', [])
                print(f"✅ Apollo Enhanced: Found {len(contacts)} contacts")

                # Try individual enrichment for key contacts
                enriched_contacts = self.enrich_key_contacts(contacts[:10])  # Top 10 only

                return enriched_contacts
            else:
                print(f"❌ Apollo Enhanced: API error {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Apollo Enhanced: Exception {e}")
            return []

    def enrich_key_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """Individual enrichment for key contacts"""

        enriched_contacts = []

        for i, contact in enumerate(contacts):
            print(f"🔍 Apollo Enrich: Contact {i+1}/{len(contacts)}")

            # Try individual people enrichment
            enriched_data = self.enrich_individual_contact(contact)

            if enriched_data:
                contact.update(enriched_data)
                contact['apollo_enriched'] = True

            enriched_contacts.append(contact)

            # Rate limiting
            time.sleep(0.5)

        return enriched_contacts

    def enrich_individual_contact(self, contact: Dict) -> Optional[Dict]:
        """Individual contact enrichment"""

        url = f"{self.base_url}/people/match"

        # Basic enrichment payload
        payload = {
            "api_key": self.api_key,
            "first_name": contact.get('first_name', ''),
            "last_name": contact.get('last_name', ''),
            "organization_name": contact.get('organization', {}).get('name', ''),
            "email": contact.get('email', ''),
            "reveal_personal_emails": True,
            "reveal_phone_number": True
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                person = data.get('person', {})

                if person:
                    enriched_data = {
                        'personal_email': person.get('personal_email', ''),
                        'phone_numbers': person.get('phone_numbers', []),
                        'phone_number': '',  # Will extract best number
                        'employment_history': person.get('employment_history', []),
                        'enrichment_timestamp': datetime.now().isoformat()
                    }

                    # Extract best phone number
                    phone_numbers = person.get('phone_numbers', [])
                    if phone_numbers:
                        # Prefer mobile, then work, then any
                        mobile = next((p.get('raw_number') for p in phone_numbers if p.get('type') == 'mobile'), None)
                        work = next((p.get('raw_number') for p in phone_numbers if p.get('type') == 'work'), None)
                        any_phone = phone_numbers[0].get('raw_number') if phone_numbers else None

                        enriched_data['phone_number'] = mobile or work or any_phone or ''

                    print(f"✅ Apollo Enrich: Enhanced {contact.get('name', 'Unknown')}")
                    return enriched_data
            else:
                print(f"❌ Apollo Enrich: Error {response.status_code} for {contact.get('name', 'Unknown')}")

        except Exception as e:
            print(f"❌ Apollo Enrich: Exception {e}")

        return None

class OpenAIIntelligenceEngine:
    """OpenAI-powered personalized intelligence generation"""

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def generate_personalized_outreach(self, contact: Dict, account_context: Dict) -> Dict:
        """Generate hyper-personalized outreach using OpenAI"""

        print(f"🧠 OpenAI: Generating intelligence for {contact.get('name', 'Unknown')}")

        # Build context
        context = self.build_contact_context(contact, account_context)

        try:
            # Generate personalized content
            intelligence = {
                'opening_line': self.generate_opening_line(context),
                'pain_points': self.generate_pain_points(context),
                'value_proposition': self.generate_value_prop(context),
                'email_subjects': self.generate_email_subjects(context),
                'linkedin_message': self.generate_linkedin_message(context),
                'call_opening': self.generate_call_opening(context),
                'openai_generated': True,
                'generation_timestamp': datetime.now().isoformat()
            }

            print(f"✅ OpenAI: Generated intelligence for {contact.get('name', 'Unknown')}")
            return intelligence

        except Exception as e:
            print(f"❌ OpenAI: Intelligence generation failed for {contact.get('name', 'Unknown')}: {e}")
            return self.fallback_intelligence(contact, account_context)

    def build_contact_context(self, contact: Dict, account_context: Dict) -> str:
        """Build comprehensive context for OpenAI prompt"""

        context_parts = [
            f"CONTACT PROFILE:",
            f"Name: {contact.get('name', contact.get('first_name', '') + ' ' + contact.get('last_name', ''))}",
            f"Title: {contact.get('title', 'Unknown')}",
            f"Company: {account_context.get('name', 'Unknown')}",
            f"Seniority: {contact.get('seniority', 'Unknown')}",
            f"Department: {', '.join(contact.get('departments', []))}",
            f"Industry: Data Center / Cloud Infrastructure",
            f"",
            f"COMPANY CONTEXT:",
            f"Domain: {account_context.get('domain', 'Unknown')}",
            f"Size: {account_context.get('size_category', 'Unknown')} company"
        ]

        # Add enrichment data if available
        if contact.get('apollo_enriched'):
            context_parts.append("DATA QUALITY: Apollo enriched with verified contact information")

        if contact.get('phone_number'):
            context_parts.append("CONTACT CHANNELS: Email + Phone available for multi-channel outreach")

        return "\n".join(context_parts)

    def generate_opening_line(self, context: str) -> str:
        """Generate personalized opening line"""

        prompt = f"""Based on this contact profile, write a highly personalized opening line for a cold outreach email about Verdigris' power monitoring solution for data centers.

{context}

REQUIREMENTS:
- Maximum 25 words
- Reference their specific role or company context
- Avoid generic phrases like "I noticed" or "I saw"
- Focus on a business challenge they likely face
- Make it about them, not about Verdigris

Example: "Managing power capacity while AI workloads scale across your infrastructure must be creating some interesting optimization challenges."

Write only the opening line:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return "Managing critical infrastructure at scale creates unique power monitoring challenges."

    def generate_pain_points(self, context: str) -> List[str]:
        """Generate role-specific pain points"""

        prompt = f"""Based on this contact profile, identify 3 specific pain points this person likely faces related to data center power management.

{context}

REQUIREMENTS:
- Focus on their specific role and seniority level
- Make them actionable and specific to power monitoring
- Avoid generic problems
- Consider their company's infrastructure challenges

Format as a numbered list:
1. [specific pain point]
2. [specific pain point]
3. [specific pain point]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            pain_points = []

            for line in content.split('\n'):
                if line.strip() and any(line.strip().startswith(p) for p in ['1.', '2.', '3.', '-', '•']):
                    pain_point = line.strip()
                    # Remove numbering
                    for prefix in ['1. ', '2. ', '3. ', '- ', '• ']:
                        if pain_point.startswith(prefix):
                            pain_point = pain_point[len(prefix):]
                            break
                    pain_points.append(pain_point)

            return pain_points[:3]
        except:
            return [
                "Lack of granular visibility into power consumption patterns",
                "Reactive maintenance instead of predictive infrastructure management",
                "Difficulty optimizing capacity utilization across distributed systems"
            ]

    def generate_value_prop(self, context: str) -> str:
        """Generate targeted value proposition"""

        prompt = f"""Based on this contact profile, write a specific value proposition for Verdigris' power monitoring solution.

{context}

REQUIREMENTS:
- Focus on their specific role and decision authority
- Mention specific benefits relevant to their situation
- Keep it under 35 words
- Make it about business outcomes, not features
- Be specific to data center power monitoring

Write only the value proposition:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return "Real-time power monitoring reduces infrastructure risk while optimizing capacity utilization across your data center portfolio."

    def generate_email_subjects(self, context: str) -> List[str]:
        """Generate A/B test email subjects"""

        prompt = f"""Based on this contact profile, write 3 different email subject lines for outreach about Verdigris power monitoring.

{context}

REQUIREMENTS:
- Each should be 4-8 words
- Reference their company or situation specifically
- Avoid spam words like "amazing", "revolutionary"
- Make them curiosity-driven but professional
- Each should test a different angle

Format:
1. [subject line]
2. [subject line]
3. [subject line]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()
            subjects = []

            for line in content.split('\n'):
                if line.strip() and any(line.strip().startswith(p) for p in ['1.', '2.', '3.', '-', '•']):
                    subject = line.strip()
                    # Remove numbering
                    for prefix in ['1. ', '2. ', '3. ', '- ', '• ']:
                        if subject.startswith(prefix):
                            subject = subject[len(prefix):]
                            break
                    subjects.append(subject)

            return subjects[:3]
        except:
            return [
                "Power infrastructure visibility question",
                "Data center optimization opportunity",
                "Infrastructure monitoring discussion"
            ]

    def generate_linkedin_message(self, context: str) -> str:
        """Generate LinkedIn connection message"""

        prompt = f"""Based on this contact profile, write a LinkedIn connection request message.

{context}

REQUIREMENTS:
- Maximum 200 characters (LinkedIn limit)
- Personalized to their role/company
- Professional but not salesy
- Request connection for industry insights

Write only the LinkedIn message:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.7
            )

            message = response.choices[0].message.content.strip()
            if len(message) > 200:
                message = message[:197] + "..."
            return message
        except:
            return "Hi! I work with data center teams on infrastructure optimization. Would love to connect and share industry insights."

    def generate_call_opening(self, context: str) -> str:
        """Generate phone call opening"""

        prompt = f"""Based on this contact profile, write a phone call opening for Verdigris power monitoring outreach.

{context}

REQUIREMENTS:
- Keep it under 30 words
- Professional and direct
- Reference their role specifically
- Create curiosity without being pushy
- Ask for permission to continue

Write only the call opening:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return "Hi, I help data center teams get better visibility into their power infrastructure. Do you have 2 minutes to discuss infrastructure monitoring?"

    def fallback_intelligence(self, contact: Dict, account_context: Dict) -> Dict:
        """Fallback intelligence when OpenAI fails"""

        name = contact.get('name', contact.get('first_name', 'there'))
        company = account_context.get('name', 'your company')

        return {
            'opening_line': f"Managing power infrastructure at {company} during growth phases creates unique monitoring challenges.",
            'pain_points': [
                "Limited visibility into granular power consumption patterns",
                "Reactive maintenance vs predictive infrastructure management",
                "Difficulty optimizing capacity utilization across facilities"
            ],
            'value_proposition': "Real-time power monitoring reduces infrastructure risk while optimizing capacity utilization.",
            'email_subjects': [
                f"{company} power monitoring discussion",
                "Infrastructure visibility opportunity",
                "Data center optimization insights"
            ],
            'linkedin_message': f"Hi {name}, I work with data center teams on power infrastructure visibility. Would love to connect!",
            'call_opening': "Hi, I help data center teams optimize their power infrastructure. Do you have a few minutes?",
            'openai_generated': False,
            'fallback_reason': 'OpenAI API unavailable'
        }

class FixedEnhancedABMSystem:
    """Fixed production ABM System with corrected Apollo + OpenAI integration"""

    def __init__(self):
        self.apollo_api = FixedEnhancedApolloAPI(os.getenv('APOLLO_API_KEY'))
        self.openai_engine = OpenAIIntelligenceEngine(os.getenv('OPENAI_API_KEY'))

    def research_account_fixed(self, domain: str) -> Dict:
        """Complete account research with fixed enhanced intelligence"""

        print(f"🚀 Fixed Enhanced ABM: Starting research for {domain}")

        # Phase 1: Enhanced contact discovery
        print(f"📊 Phase 1: Enhanced contact discovery")
        raw_contacts = self.apollo_api.search_people_enhanced(domain)

        if not raw_contacts:
            print(f"❌ No contacts found for {domain}")
            return {}

        # Phase 2: Process and score contacts (with lower threshold for testing)
        print(f"⚡ Phase 2: Contact processing and scoring")
        processed_contacts = self.process_and_score_contacts(raw_contacts, domain)

        # Phase 3: OpenAI intelligence generation for top contacts
        print(f"🧠 Phase 3: AI-powered intelligence generation")
        high_value_contacts = [c for c in processed_contacts if c.get('final_lead_score', 0) >= 60]  # Lower threshold

        account_context = {
            'name': domain.replace('.com', '').replace('.', ' ').title(),
            'domain': domain,
            'size_category': 'mid-market'
        }

        ai_enhanced_contacts = 0
        for contact in high_value_contacts[:3]:  # Top 3 contacts for cost control
            intelligence = self.openai_engine.generate_personalized_outreach(contact, account_context)
            contact.update(intelligence)
            if intelligence.get('openai_generated'):
                ai_enhanced_contacts += 1

        results = {
            'domain': domain,
            'total_contacts': len(processed_contacts),
            'high_value_contacts': len(high_value_contacts),
            'contacts': processed_contacts,
            'openai_enhanced_contacts': ai_enhanced_contacts,
            'research_timestamp': datetime.now().isoformat(),
            'apollo_enriched_contacts': len([c for c in processed_contacts if c.get('apollo_enriched')])
        }

        print(f"✅ Fixed Enhanced ABM: Research complete")
        print(f"   Total Contacts: {len(processed_contacts)}")
        print(f"   High-Value (Score ≥60): {len(high_value_contacts)}")
        print(f"   Apollo Enriched: {results['apollo_enriched_contacts']}")
        print(f"   OpenAI Enhanced: {ai_enhanced_contacts}")

        return results

    def process_and_score_contacts(self, contacts: List[Dict], domain: str) -> List[Dict]:
        """Process and score contacts with enhanced data"""

        processed = []

        for contact in contacts:
            # More generous base scoring for testing
            base_score = 50  # Higher base ICP score

            # Email availability bonus
            if contact.get('email'):
                base_score += 10
            if contact.get('personal_email'):
                base_score += 10

            # Phone number bonus
            if contact.get('phone_number'):
                base_score += 10

            # Apollo enrichment bonus
            if contact.get('apollo_enriched'):
                base_score += 15

            # Title-based scoring
            title = contact.get('title', '').lower()
            if any(term in title for term in ['vp', 'vice president']):
                buying_power = 100
                committee_role = 'Economic Buyer'
            elif 'director' in title:
                buying_power = 80
                committee_role = 'Technical Evaluator'
            elif any(term in title for term in ['manager', 'head']):
                buying_power = 60
                committee_role = 'Champion'
            else:
                buying_power = 30
                committee_role = 'Influencer'

            # Engagement potential
            engagement = 40  # Base engagement
            if contact.get('linkedin_url'):
                engagement += 20
            if contact.get('phone_number'):
                engagement += 20
            if contact.get('apollo_enriched'):
                engagement += 20

            # Final lead score (more generous)
            final_score = round((base_score * 0.4) + (buying_power * 0.3) + (engagement * 0.3))

            processed_contact = {
                'id': f"apollo_{contact.get('id', '')}",
                'name': contact.get('name', contact.get('first_name', '') + ' ' + contact.get('last_name', '')),
                'title': contact.get('title', '').strip(),
                'email': contact.get('email', ''),
                'personal_email': contact.get('personal_email', ''),
                'phone_number': contact.get('phone_number', ''),
                'linkedin_url': contact.get('linkedin_url', ''),
                'company': contact.get('organization', {}).get('name', ''),
                'seniority': contact.get('seniority', ''),
                'buying_committee_role': committee_role,
                'icp_fit_score': min(base_score, 100),
                'buying_power_score': buying_power,
                'engagement_potential_score': min(engagement, 100),
                'final_lead_score': min(final_score, 100),
                'apollo_enriched': contact.get('apollo_enriched', False),
                'multi_channel_ready': bool(contact.get('phone_number') and contact.get('email')),
                'source': 'apollo_enhanced_api',
                'last_updated': datetime.now().isoformat()
            }

            processed.append(processed_contact)

        # Sort by final lead score
        return sorted(processed, key=lambda x: x.get('final_lead_score', 0), reverse=True)

def main():
    """Test fixed enhanced ABM system"""

    if not os.getenv('APOLLO_API_KEY'):
        print("❌ APOLLO_API_KEY not found in environment")
        return

    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        return

    print("🚀 Testing Fixed Enhanced ABM System with Apollo + OpenAI")

    # Initialize system
    fixed_abm = FixedEnhancedABMSystem()

    # Test with CoreWeave (AI infrastructure company)
    test_domain = "coreweave.com"

    results = fixed_abm.research_account_fixed(test_domain)

    if results:
        print(f"\n📊 FIXED ENHANCED ABM RESULTS:")
        print(f"   Domain: {results.get('domain')}")
        print(f"   Total Contacts: {results.get('total_contacts')}")
        print(f"   High-Value Contacts: {results.get('high_value_contacts')}")
        print(f"   Apollo Enriched: {results.get('apollo_enriched_contacts')}")
        print(f"   OpenAI Enhanced: {results.get('openai_enhanced_contacts')}")

        # Show top contacts with AI intelligence
        contacts = results.get('contacts', [])
        ai_contacts = [c for c in contacts if c.get('openai_generated')]

        print(f"\n👥 TOP CONTACTS WITH AI INTELLIGENCE:")

        for i, contact in enumerate(ai_contacts[:3], 1):
            print(f"\n👤 CONTACT #{i}:")
            print(f"   Name: {contact.get('name')}")
            print(f"   Title: {contact.get('title')}")
            print(f"   Score: {contact.get('final_lead_score')}/100")
            print(f"   Email: {contact.get('email')}")
            print(f"   Phone: {contact.get('phone_number') or 'Not available'}")
            print(f"   Multi-Channel: {'✅' if contact.get('multi_channel_ready') else '❌'}")

            print(f"\n🎯 AI-GENERATED INTELLIGENCE:")
            print(f"   Opening: {contact.get('opening_line', 'N/A')}")
            print(f"   Value Prop: {contact.get('value_proposition', 'N/A')}")

            subjects = contact.get('email_subjects', [])
            if subjects:
                print(f"   Subjects: {', '.join(subjects)}")

            print(f"   LinkedIn: {contact.get('linkedin_message', 'N/A')[:100]}...")

if __name__ == '__main__':
    main()