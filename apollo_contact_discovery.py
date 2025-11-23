#!/usr/bin/env python3
"""
Modern Apollo Contact Discovery System
Optimized for credit-efficient ABM research with batch enrichment
"""

import os
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ApolloContact:
    """Structured contact data from Apollo"""
    # Basic identification
    apollo_id: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Professional information
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None

    # Contact information (from enrichment)
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

    # Location
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    # Apollo metadata
    apollo_score: Optional[int] = None
    enriched: bool = False
    search_timestamp: Optional[str] = None
    enrichment_timestamp: Optional[str] = None

class ApolloContactDiscovery:
    """
    Modern Apollo API integration for ABM contact discovery
    Implements credit-efficient two-stage workflow: search → selective enrichment
    """

    def __init__(self):
        self.api_key = os.getenv('APOLLO_API_KEY')
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY environment variable is required")

        self.base_url = "https://api.apollo.io/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.api_key
        })

        # Rate limiting tracking
        self.last_search_time = 0
        self.last_enrichment_time = 0
        self.search_delay = 1.0  # 1 second between searches
        self.enrichment_delay = 2.0  # 2 seconds between enrichments

        logger.info("🚀 Apollo Contact Discovery initialized")

    def discover_contacts(self, company_name: str, company_domain: str,
                         max_contacts: int = 50) -> List[ApolloContact]:
        """
        Main entry point for contact discovery
        Implements two-stage workflow for credit efficiency
        """
        logger.info(f"🔍 Starting contact discovery for {company_name}")

        # Stage 1: Search (no credits consumed)
        prospects = self._search_people(company_name, company_domain, max_contacts)
        logger.info(f"📊 Found {len(prospects)} prospects from search")

        if not prospects:
            return []

        # Stage 2: Intelligent filtering before enrichment
        priority_prospects = self._filter_high_priority_prospects(prospects)
        logger.info(f"🎯 Filtered to {len(priority_prospects)} high-priority prospects")

        # Stage 3: Batch enrichment (credits consumed)
        enriched_contacts = self._batch_enrich_contacts(priority_prospects)
        logger.info(f"✅ Enriched {len(enriched_contacts)} contacts with full data")

        return enriched_contacts

    def _search_people(self, company_name: str, company_domain: str,
                      max_contacts: int = 50) -> List[ApolloContact]:
        """
        Stage 1: Search Apollo database (no credits consumed)
        Returns basic prospect information for filtering
        """
        self._rate_limit_search()

        # Target key ABM roles for B2B infrastructure companies
        target_titles = [
            # C-Suite & VP Level
            "CTO", "Chief Technology Officer", "VP Engineering", "VP Infrastructure",
            "VP Operations", "Chief Infrastructure Officer", "Head of Engineering",

            # Directors & Senior Management
            "Director of Infrastructure", "Director of Engineering", "Director of Operations",
            "Infrastructure Director", "Engineering Director", "DevOps Director",

            # Senior & Lead Roles
            "Senior Infrastructure Engineer", "Lead DevOps Engineer", "Principal Engineer",
            "Staff Engineer", "Senior Site Reliability Engineer", "Lead SRE",

            # Specialized Infrastructure Roles
            "Infrastructure Engineer", "DevOps Engineer", "Site Reliability Engineer",
            "Cloud Engineer", "Platform Engineer", "Systems Engineer"
        ]

        # Apollo search parameters optimized for infrastructure contacts
        search_params = {
            "q_organization_domains": company_domain,
            "person_titles": target_titles,
            "person_seniorities": ["senior", "director", "vp", "c_suite", "owner"],
            "person_departments": ["engineering", "information_technology", "operations"],
            "page": 1,
            "per_page": min(max_contacts, 100),  # Apollo max is 100 per page
            "organization_num_employees_ranges": ["11,50", "51,200", "201,500", "501,1000", "1001,5000", "5001,10000"]
        }

        try:
            logger.info(f"🔍 Searching Apollo for contacts at {company_domain}")
            response = self.session.post(f"{self.base_url}/mixed_people/search",
                                       json=search_params)
            response.raise_for_status()

            data = response.json()
            prospects = []

            for person_data in data.get('people', []):
                contact = self._parse_search_result(person_data, company_name, company_domain)
                if contact:
                    prospects.append(contact)

            logger.info(f"✅ Search completed: {len(prospects)} prospects found")
            return prospects

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Apollo search failed: {e}")
            return []

    def _filter_high_priority_prospects(self, prospects: List[ApolloContact],
                                      max_priority: int = 20) -> List[ApolloContact]:
        """
        Stage 2: Intelligent filtering before enrichment
        Prioritize contacts most likely to be valuable for ABM
        """
        def priority_score(contact: ApolloContact) -> int:
            score = 0

            # Seniority scoring (higher is better)
            seniority_scores = {
                "c_suite": 100, "vp": 90, "director": 80, "manager": 60,
                "senior": 70, "entry": 30, "intern": 10
            }
            if contact.seniority:
                score += seniority_scores.get(contact.seniority.lower(), 40)

            # Title relevance scoring
            if contact.title:
                title_lower = contact.title.lower()

                # High-value keywords
                if any(keyword in title_lower for keyword in
                      ["cto", "vp", "director", "head of", "chief"]):
                    score += 50

                # Infrastructure-specific keywords
                if any(keyword in title_lower for keyword in
                      ["infrastructure", "devops", "sre", "reliability", "platform"]):
                    score += 30

                # Engineering keywords
                if any(keyword in title_lower for keyword in
                      ["engineer", "engineering", "technical", "systems"]):
                    score += 20

            # Apollo confidence scoring
            if contact.apollo_score:
                score += min(contact.apollo_score, 50)  # Cap at 50 points

            return score

        # Sort by priority score and take top prospects
        prospects_with_scores = [(p, priority_score(p)) for p in prospects]
        prospects_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Log top priorities for visibility
        logger.info("🎯 Top priority prospects:")
        for contact, score in prospects_with_scores[:5]:
            logger.info(f"   {contact.name} ({contact.title}) - Score: {score}")

        return [p for p, score in prospects_with_scores[:max_priority]]

    def _batch_enrich_contacts(self, prospects: List[ApolloContact]) -> List[ApolloContact]:
        """
        Stage 3: Batch enrichment for full contact data (credits consumed)
        Process up to 10 contacts per API call for efficiency
        """
        enriched_contacts = []
        batch_size = 10  # Apollo's batch limit

        for i in range(0, len(prospects), batch_size):
            batch = prospects[i:i + batch_size]

            self._rate_limit_enrichment()
            logger.info(f"🔄 Enriching batch {i//batch_size + 1}: {len(batch)} contacts")

            enriched_batch = self._enrich_contact_batch(batch)
            enriched_contacts.extend(enriched_batch)

            # Log progress
            successful_enrichments = len([c for c in enriched_batch if c.enriched])
            logger.info(f"✅ Batch complete: {successful_enrichments}/{len(batch)} enriched")

        return enriched_contacts

    def _enrich_contact_batch(self, contacts: List[ApolloContact]) -> List[ApolloContact]:
        """
        Enrich a batch of contacts using Apollo's bulk enrichment API
        """
        # Prepare enrichment payload
        details = []
        for contact in contacts:
            # Use multiple identifiers for better match rates
            contact_details = {}

            if contact.first_name and contact.last_name:
                contact_details["first_name"] = contact.first_name
                contact_details["last_name"] = contact.last_name
            elif contact.name:
                # Split name if we only have full name
                name_parts = contact.name.split(' ', 1)
                contact_details["first_name"] = name_parts[0]
                if len(name_parts) > 1:
                    contact_details["last_name"] = name_parts[1]

            if contact.company_domain:
                contact_details["organization_domain"] = contact.company_domain
            elif contact.company_name:
                contact_details["organization_name"] = contact.company_name

            if contact.title:
                contact_details["title"] = contact.title

            details.append(contact_details)

        # Make bulk enrichment request
        enrichment_params = {
            "details": details,
            "reveal_personal_emails": True,  # Get personal emails when available
            "reveal_phone_number": True      # Get phone numbers when available
        }

        try:
            response = self.session.post(f"{self.base_url}/people/bulk_match",
                                       json=enrichment_params)
            response.raise_for_status()

            data = response.json()
            enriched_contacts = []

            # Match enriched data back to original contacts
            matches = data.get('matches', [])
            for i, (original_contact, match_data) in enumerate(zip(contacts, matches)):
                if match_data and match_data.get('person'):
                    enriched_contact = self._parse_enrichment_result(
                        original_contact, match_data['person']
                    )
                    enriched_contacts.append(enriched_contact)
                else:
                    # Keep original contact even if enrichment failed
                    original_contact.enriched = False
                    enriched_contacts.append(original_contact)

            return enriched_contacts

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Batch enrichment failed: {e}")
            # Return original contacts with enriched=False
            for contact in contacts:
                contact.enriched = False
            return contacts

    def _parse_search_result(self, person_data: dict, company_name: str,
                           company_domain: str) -> Optional[ApolloContact]:
        """Parse person data from Apollo search results"""
        try:
            # Extract organization info
            organization = person_data.get('organization', {})

            contact = ApolloContact(
                apollo_id=person_data.get('id'),
                name=person_data.get('name'),
                first_name=person_data.get('first_name'),
                last_name=person_data.get('last_name'),
                title=person_data.get('title'),
                company_name=organization.get('name') or company_name,
                company_domain=organization.get('primary_domain') or company_domain,
                seniority=person_data.get('seniority'),
                department=person_data.get('departments', [None])[0] if person_data.get('departments') else None,
                city=person_data.get('city'),
                state=person_data.get('state'),
                country=person_data.get('country'),
                apollo_score=person_data.get('apollo_match_score'),
                enriched=False,  # Not enriched yet
                search_timestamp=datetime.now().isoformat()
            )

            return contact

        except Exception as e:
            logger.error(f"❌ Error parsing search result: {e}")
            return None

    def _parse_enrichment_result(self, original_contact: ApolloContact,
                               person_data: dict) -> ApolloContact:
        """Parse enriched person data and merge with original contact"""
        try:
            # Update contact with enriched data
            original_contact.email = person_data.get('email')
            original_contact.phone = person_data.get('sanitized_phone')
            original_contact.linkedin_url = person_data.get('linkedin_url')

            # Update any improved data from enrichment
            if person_data.get('title'):
                original_contact.title = person_data.get('title')
            if person_data.get('seniority'):
                original_contact.seniority = person_data.get('seniority')

            # Mark as successfully enriched
            original_contact.enriched = True
            original_contact.enrichment_timestamp = datetime.now().isoformat()

            return original_contact

        except Exception as e:
            logger.error(f"❌ Error parsing enrichment result: {e}")
            original_contact.enriched = False
            return original_contact

    def _rate_limit_search(self):
        """Rate limiting for search API calls"""
        current_time = time.time()
        elapsed = current_time - self.last_search_time

        if elapsed < self.search_delay:
            sleep_time = self.search_delay - elapsed
            logger.debug(f"⏱️ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_search_time = time.time()

    def _rate_limit_enrichment(self):
        """Rate limiting for enrichment API calls"""
        current_time = time.time()
        elapsed = current_time - self.last_enrichment_time

        if elapsed < self.enrichment_delay:
            sleep_time = self.enrichment_delay - elapsed
            logger.debug(f"⏱️ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.last_enrichment_time = time.time()

    def get_api_credits_remaining(self) -> Optional[Dict]:
        """
        Check remaining Apollo API credits
        Useful for monitoring usage and planning research
        """
        try:
            response = self.session.get(f"{self.base_url}/auth/health")
            response.raise_for_status()

            data = response.json()
            credits_info = {
                'remaining_credits': data.get('credits_remaining'),
                'monthly_limit': data.get('monthly_credits_limit'),
                'reset_date': data.get('credits_reset_date')
            }

            logger.info(f"💰 Apollo Credits: {credits_info['remaining_credits']} remaining")
            return credits_info

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to check Apollo credits: {e}")
            return None

    def convert_to_notion_format(self, contacts: List[ApolloContact]) -> List[Dict]:
        """
        Convert Apollo contacts to Notion database format
        Compatible with existing ABM system expectations
        """
        notion_contacts = []

        for contact in contacts:
            notion_contact = {
                'name': contact.name or f"{contact.first_name} {contact.last_name}".strip(),
                'title': contact.title or 'Unknown Title',
                'email': contact.email,
                'phone': contact.phone,
                'linkedin_url': contact.linkedin_url,
                'company_name': contact.company_name,
                'company_domain': contact.company_domain,
                'seniority': contact.seniority,
                'department': contact.department,
                'city': contact.city,
                'state': contact.state,
                'country': contact.country,

                # ABM system compatibility
                'buying_committee_role': self._map_to_buying_committee_role(contact.title, contact.seniority),
                'apollo_id': contact.apollo_id,
                'apollo_score': contact.apollo_score,
                'data_enriched': contact.enriched,
                'discovery_source': 'apollo_api',
                'discovery_date': contact.search_timestamp,
                'enrichment_date': contact.enrichment_timestamp
            }

            notion_contacts.append(notion_contact)

        return notion_contacts

    def _map_to_buying_committee_role(self, title: str, seniority: str) -> str:
        """
        Map contact title and seniority to buying committee roles
        Used for ABM campaign segmentation
        """
        if not title:
            return 'Unknown'

        title_lower = title.lower()

        # Decision makers
        if any(keyword in title_lower for keyword in
               ['cto', 'cio', 'vp', 'chief', 'head of', 'director']):
            return 'Decision Maker'

        # Technical influencers
        elif any(keyword in title_lower for keyword in
                 ['senior', 'lead', 'principal', 'staff', 'architect']):
            return 'Technical Influencer'

        # End users
        elif any(keyword in title_lower for keyword in
                 ['engineer', 'developer', 'analyst', 'specialist']):
            return 'End User'

        # Procurers (if we find procurement/finance folks)
        elif any(keyword in title_lower for keyword in
                 ['procurement', 'finance', 'budget', 'purchasing']):
            return 'Economic Buyer'

        return 'Technical Influencer'  # Default for technical roles


# Export singleton instance for easy importing
apollo_discovery = ApolloContactDiscovery()

# Backward compatibility function for existing code
def discover_contacts(company_name: str, company_domain: str) -> List[Dict]:
    """
    Backward compatibility wrapper for existing ABM system
    """
    contacts = apollo_discovery.discover_contacts(company_name, company_domain)
    return apollo_discovery.convert_to_notion_format(contacts)

if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Apollo Contact Discovery...")

    # Check credits first
    credits = apollo_discovery.get_api_credits_remaining()
    if credits:
        print(f"💰 Available credits: {credits['remaining_credits']}")

    # Test with a sample company
    test_contacts = discover_contacts("Genesis Cloud", "genesiscloud.com")
    print(f"✅ Found {len(test_contacts)} contacts")

    for contact in test_contacts[:3]:  # Show first 3
        print(f"   📧 {contact['name']} - {contact['title']} - {contact.get('email', 'No email')}")