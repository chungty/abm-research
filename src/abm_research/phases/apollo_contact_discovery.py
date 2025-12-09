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
        self.api_key = os.getenv("APOLLO_API_KEY")
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY environment variable is required")

        self.base_url = "https://api.apollo.io/v1"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "X-Api-Key": self.api_key,
            }
        )

        # Rate limiting tracking
        self.last_search_time = 0
        self.last_enrichment_time = 0
        self.search_delay = 1.0  # 1 second between searches
        self.enrichment_delay = 2.0  # 2 seconds between enrichments

        logger.info("🚀 Apollo Contact Discovery initialized")

    def discover_contacts(
        self, company_name: str, company_domain: str, max_contacts: int = 50
    ) -> List[ApolloContact]:
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

    def _search_people(
        self, company_name: str, company_domain: str, max_contacts: int = 50
    ) -> List[ApolloContact]:
        """
        Stage 1: Search Apollo database (no credits consumed)
        Returns basic prospect information for filtering
        """
        self._rate_limit_search()

        # OPTION 4: Infrastructure & Operations Focus
        # Target Verdigris Signals buying committee for power monitoring sales

        # Key titles for data center power monitoring buying committee
        infrastructure_titles = [
            # Decision Makers (Budget Authority)
            "VP Operations",
            "Vice President Operations",
            "VP Infrastructure",
            "Vice President Infrastructure",
            "VP Engineering",
            "Vice President Engineering",
            "CTO",
            "Chief Technology Officer",
            "Head of Engineering",
            "Head of Operations",
            "Director Operations",
            "Director Infrastructure",
            "Director Engineering",
            "Facilities Manager",
            "Director Facilities",
            "VP Facilities",
            # Technical Influencers (Problem Owners & Champions)
            "Site Reliability Engineer",
            "SRE",
            "Senior SRE",
            "Lead SRE",
            "Principal SRE",
            "Infrastructure Engineer",
            "Senior Infrastructure Engineer",
            "Lead Infrastructure Engineer",
            "DevOps Engineer",
            "Senior DevOps Engineer",
            "Lead DevOps Engineer",
            "Platform Engineer",
            "Senior Platform Engineer",
            "Systems Engineer",
            "Data Center Engineer",
            "Facilities Engineer",
            "Energy Engineer",
            "Sustainability Engineer",
            "Power Engineer",
            # Operations Teams (End Users)
            "NOC Engineer",
            "Operations Engineer",
            "Network Operations",
            "Data Center Operations",
            "Facilities Operations",
        ]

        search_params = {
            "q_organization_domains": company_domain,
            "person_titles": infrastructure_titles,
            "person_departments": [
                "engineering",
                "information_technology",
                "operations",
                "facilities",
            ],
            "person_seniorities": ["manager", "senior", "director", "vp", "c_suite", "owner"],
            "page": 1,
            "per_page": min(max_contacts, 100),  # Apollo max is 100 per page
        }

        try:
            logger.info(f"🔍 Searching Apollo for contacts at {company_domain}")
            response = self.session.post(f"{self.base_url}/mixed_people/search", json=search_params)
            response.raise_for_status()

            data = response.json()
            prospects = []

            for person_data in data.get("people", []):
                contact = self._parse_search_result(person_data, company_name, company_domain)
                if contact:
                    prospects.append(contact)

            logger.info(f"✅ Search completed: {len(prospects)} prospects found")
            return prospects

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Apollo search failed: {e}")
            return []

    def _filter_high_priority_prospects(
        self, prospects: List[ApolloContact], max_priority: int = 20
    ) -> List[ApolloContact]:
        """
        Stage 2: Intelligent filtering before enrichment
        Prioritize contacts most likely to be valuable for ABM
        """

        def priority_score(contact: ApolloContact) -> int:
            score = 0

            # Seniority scoring (higher is better)
            seniority_scores = {
                "c_suite": 100,
                "vp": 90,
                "director": 80,
                "manager": 60,
                "senior": 70,
                "entry": 30,
                "intern": 10,
            }
            if contact.seniority:
                score += seniority_scores.get(contact.seniority.lower(), 40)

            # Title relevance scoring
            if contact.title:
                title_lower = contact.title.lower()

                # High-value keywords
                if any(
                    keyword in title_lower
                    for keyword in ["cto", "vp", "director", "head of", "chief"]
                ):
                    score += 50

                # Infrastructure-specific keywords
                if any(
                    keyword in title_lower
                    for keyword in ["infrastructure", "devops", "sre", "reliability", "platform"]
                ):
                    score += 30

                # Engineering keywords
                if any(
                    keyword in title_lower
                    for keyword in ["engineer", "engineering", "technical", "systems"]
                ):
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
            batch = prospects[i : i + batch_size]

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
                name_parts = contact.name.split(" ", 1)
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
            # Note: reveal_phone_number requires webhook_url, removing to fix 400 error
        }

        try:
            response = self.session.post(
                f"{self.base_url}/people/bulk_match", json=enrichment_params
            )
            response.raise_for_status()

            data = response.json()
            enriched_contacts = []

            # Match enriched data back to original contacts
            matches = data.get("matches", [])
            for i, (original_contact, match_data) in enumerate(zip(contacts, matches)):
                if match_data and match_data.get("person"):
                    enriched_contact = self._parse_enrichment_result(
                        original_contact, match_data["person"]
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

    def _parse_search_result(
        self, person_data: dict, company_name: str, company_domain: str
    ) -> Optional[ApolloContact]:
        """Parse person data from Apollo search results"""
        try:
            # Extract organization info
            organization = person_data.get("organization", {})

            contact = ApolloContact(
                apollo_id=person_data.get("id"),
                name=person_data.get("name"),
                first_name=person_data.get("first_name"),
                last_name=person_data.get("last_name"),
                title=person_data.get("title"),
                company_name=organization.get("name") or company_name,
                company_domain=organization.get("primary_domain") or company_domain,
                seniority=person_data.get("seniority"),
                department=person_data.get("departments", [None])[0]
                if person_data.get("departments")
                else None,
                city=person_data.get("city"),
                state=person_data.get("state"),
                country=person_data.get("country"),
                apollo_score=person_data.get("apollo_match_score"),
                enriched=False,  # Not enriched yet
                search_timestamp=datetime.now().isoformat(),
            )

            return contact

        except Exception as e:
            logger.error(f"❌ Error parsing search result: {e}")
            return None

    def _parse_enrichment_result(
        self, original_contact: ApolloContact, person_data: dict
    ) -> ApolloContact:
        """Parse enriched person data and merge with original contact"""
        try:
            # Update contact with enriched data
            original_contact.email = person_data.get("email")
            original_contact.phone = person_data.get("sanitized_phone")
            original_contact.linkedin_url = person_data.get("linkedin_url")

            # Update any improved data from enrichment
            if person_data.get("title"):
                original_contact.title = person_data.get("title")
            if person_data.get("seniority"):
                original_contact.seniority = person_data.get("seniority")

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
                "remaining_credits": data.get("credits_remaining"),
                "monthly_limit": data.get("monthly_credits_limit"),
                "reset_date": data.get("credits_reset_date"),
            }

            logger.info(f"💰 Apollo Credits: {credits_info['remaining_credits']} remaining")
            return credits_info

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to check Apollo credits: {e}")
            return None

    def convert_to_notion_format(
        self, contacts: List[ApolloContact], company_name: str = None
    ) -> List[Dict]:
        """
        Convert Apollo contacts to enhanced schema format with confidence indicators and data provenance
        """
        notion_contacts = []

        for contact in contacts:
            notion_contact = self._convert_to_enhanced_schema(contact, company_name)
            notion_contacts.append(notion_contact)

        return notion_contacts

    def _convert_to_enhanced_schema(self, contact: ApolloContact, company_name: str = None) -> Dict:
        """Convert single contact to enhanced schema format with confidence indicators"""

        # Helper function for confidence indicators
        def format_with_confidence(
            value: str, confidence: int = None, searched: bool = True, source: str = "apollo"
        ) -> str:
            if not searched:
                return "N/A - not searched in this analysis"
            elif not value or value.strip() == "":
                return f"Not found (searched via {source}, 95% confidence)"
            else:
                conf = f"({confidence}% confidence)" if confidence else "(80% confidence)"
                return f"{value} {conf}"

        # Calculate data quality score based on completeness and enrichment
        data_quality_score = self._calculate_data_quality_score(contact)

        # Determine lead score based on title, seniority, and data quality
        lead_score = self._calculate_lead_score(contact)

        # Generate engagement level based on contact characteristics
        engagement_level = self._determine_engagement_level(contact)

        return {
            # Core Contact Fields with confidence indicators
            "Name": format_with_confidence(
                contact.name or f"{contact.first_name or ''} {contact.last_name or ''}".strip(),
                85 if contact.name else 75,
                True,
                "apollo",
            ),
            "Email": format_with_confidence(
                contact.email,
                90 if contact.enriched else None,
                contact.enriched,
                "apollo enrichment" if contact.enriched else "apollo",
            ),
            "Title": format_with_confidence(
                contact.title, 80 if contact.title else None, True, "apollo"
            ),
            # Enhanced Data Provenance Fields
            "Name Source": "apollo",
            "Email Source": "apollo" if contact.email else "not_found",
            "Title Source": "apollo" if contact.title else "not_found",
            "Data Quality Score": data_quality_score,
            "Last Enriched": contact.enrichment_timestamp or contact.search_timestamp,
            # Lead Scoring and Engagement
            "Lead Score": lead_score,
            "ICP Fit Score": lead_score,  # Use same score for backward compatibility
            "Engagement Level": engagement_level,
            # Additional Contact Information
            "LinkedIn URL": contact.linkedin_url or None,
            "Phone": contact.phone,
            "Contact Date": contact.search_timestamp,
            "Notes": self._generate_contact_notes(contact),
            # Professional Details
            "Seniority": contact.seniority or "Unknown",
            "Department": contact.department or "Unknown",
            "Location": self._format_location(contact),
            # ABM Intelligence
            "Buying Committee Role": self._map_to_buying_committee_role(
                contact.title, contact.seniority
            ),
            "Contact Priority": self._determine_contact_priority(contact),
            # Metadata and Legacy Compatibility
            "Apollo ID": contact.apollo_id,
            "Apollo Score": contact.apollo_score,
            "Data Enriched": contact.enriched,
            "Discovery Source": "apollo_api",
            "Discovery Date": contact.search_timestamp,
            "Enrichment Date": contact.enrichment_timestamp,
            # Account Relations - Use company name for now, ABM system will handle account lookup
            "Company Name (for Account Relation)": contact.company_name or company_name,
            "Company Domain": contact.company_domain,
            # Legacy field names for backward compatibility
            "name": contact.name or f"{contact.first_name or ''} {contact.last_name or ''}".strip(),
            "title": contact.title or "Unknown Title",
            "email": contact.email,
            "phone": contact.phone,
            "linkedin_url": contact.linkedin_url,
            "company_name": contact.company_name,
            "company_domain": contact.company_domain,
            "seniority": contact.seniority,
            "department": contact.department,
            "city": contact.city,
            "state": contact.state,
            "country": contact.country,
            "buying_committee_role": self._map_to_buying_committee_role(
                contact.title, contact.seniority
            ),
            "apollo_id": contact.apollo_id,
            "apollo_score": contact.apollo_score,
            "data_enriched": contact.enriched,
            "discovery_source": "apollo_api",
            "discovery_date": contact.search_timestamp,
            "enrichment_date": contact.enrichment_timestamp,
        }

    def _calculate_data_quality_score(self, contact: ApolloContact) -> int:
        """Calculate data quality score based on completeness and reliability"""
        score = 0

        # Base score for having a contact
        score += 20

        # Name completeness
        if contact.name or (contact.first_name and contact.last_name):
            score += 15

        # Professional information
        if contact.title:
            score += 20
        if contact.company_name:
            score += 15
        if contact.company_domain:
            score += 10

        # Contact information (premium value)
        if contact.email:
            score += 20  # Email is highly valuable
        if contact.linkedin_url:
            score += 10
        if contact.phone:
            score += 5

        # Apollo confidence
        if contact.apollo_score:
            score += min(contact.apollo_score / 10, 10)  # Max 10 points from Apollo score

        # Enrichment bonus
        if contact.enriched:
            score += 15

        return min(100, int(score))

    def _calculate_lead_score(self, contact: ApolloContact) -> int:
        """Calculate lead score based on buying power and influence"""
        score = 40  # Base score

        # Seniority scoring (decision-making power)
        seniority_scores = {
            "c_suite": 40,
            "vp": 35,
            "director": 30,
            "manager": 20,
            "senior": 15,
            "entry": 5,
            "intern": 0,
        }
        if contact.seniority:
            score += seniority_scores.get(contact.seniority.lower(), 10)

        # Title-based scoring
        if contact.title:
            title_lower = contact.title.lower()

            # High-value decision maker keywords
            if any(
                keyword in title_lower
                for keyword in ["cto", "cio", "vp", "vice president", "chief", "head of"]
            ):
                score += 30

            # Director level
            elif "director" in title_lower:
                score += 25

            # Senior/Lead level
            elif any(
                keyword in title_lower for keyword in ["senior", "lead", "principal", "staff"]
            ):
                score += 15

            # Infrastructure/DevOps specific (Verdigris relevance)
            if any(
                keyword in title_lower
                for keyword in [
                    "infrastructure",
                    "devops",
                    "sre",
                    "reliability",
                    "platform",
                    "facilities",
                ]
            ):
                score += 15

        # Data quality bonus
        data_quality = self._calculate_data_quality_score(contact)
        if data_quality > 80:
            score += 10
        elif data_quality > 60:
            score += 5

        # Apollo confidence bonus
        if contact.apollo_score and contact.apollo_score > 80:
            score += 10

        return min(100, int(score))

    def _determine_engagement_level(self, contact: ApolloContact) -> str:
        """Determine appropriate engagement level based on contact characteristics"""
        lead_score = self._calculate_lead_score(contact)

        if lead_score >= 80:
            return "High"
        elif lead_score >= 60:
            return "Medium"
        else:
            return "Low"

    def _determine_contact_priority(self, contact: ApolloContact) -> str:
        """Determine contact priority for sales engagement"""
        lead_score = self._calculate_lead_score(contact)
        data_quality = self._calculate_data_quality_score(contact)

        # High priority: High lead score and good data quality
        if lead_score >= 75 and data_quality >= 70:
            return "High"

        # Medium priority: Decent lead score or good data
        elif lead_score >= 60 or data_quality >= 80:
            return "Medium"

        else:
            return "Low"

    def _format_location(self, contact: ApolloContact) -> str:
        """Format location string from contact data"""
        location_parts = []

        if contact.city:
            location_parts.append(contact.city)
        if contact.state:
            location_parts.append(contact.state)
        if contact.country:
            location_parts.append(contact.country)

        return ", ".join(location_parts) if location_parts else "Unknown"

    def _generate_contact_notes(self, contact: ApolloContact) -> str:
        """Generate intelligent contact notes based on available data"""
        notes = []

        # Apollo insights
        if contact.apollo_score and contact.apollo_score > 80:
            notes.append(f"High Apollo match score ({contact.apollo_score})")

        # Enrichment status
        if contact.enriched:
            notes.append("Successfully enriched with email/contact data")
        else:
            notes.append("Basic contact info only - enrichment needed")

        # Professional insights
        if contact.seniority in ["c_suite", "vp", "director"]:
            notes.append("Key decision maker - high priority for outreach")

        # Infrastructure relevance
        if contact.title and any(
            keyword in contact.title.lower()
            for keyword in ["infrastructure", "devops", "sre", "facilities", "operations"]
        ):
            notes.append("Infrastructure role - excellent fit for power monitoring solutions")

        return "; ".join(notes) if notes else "Standard contact profile"

    def _map_to_buying_committee_role(self, title: str, seniority: str) -> str:
        """
        Map contact title and seniority to buying committee roles
        Used for ABM campaign segmentation
        """
        if not title:
            return "Unknown"

        title_lower = title.lower()

        # Decision makers
        if any(
            keyword in title_lower
            for keyword in ["cto", "cio", "vp", "chief", "head of", "director"]
        ):
            return "Decision Maker"

        # Technical influencers
        elif any(
            keyword in title_lower
            for keyword in ["senior", "lead", "principal", "staff", "architect"]
        ):
            return "Technical Influencer"

        # End users
        elif any(
            keyword in title_lower for keyword in ["engineer", "developer", "analyst", "specialist"]
        ):
            return "End User"

        # Procurers (if we find procurement/finance folks)
        elif any(
            keyword in title_lower for keyword in ["procurement", "finance", "budget", "purchasing"]
        ):
            return "Economic Buyer"

        return "Technical Influencer"  # Default for technical roles


# Lazy singleton - only instantiate when needed (and when API key is available)
_apollo_discovery = None


def get_apollo_discovery():
    """Get Apollo discovery instance (lazy initialization)"""
    global _apollo_discovery
    if _apollo_discovery is None:
        _apollo_discovery = ApolloContactDiscovery()
    return _apollo_discovery


# For backward compatibility - will fail if used without API key
apollo_discovery = None  # Set to None, use get_apollo_discovery() instead


# Backward compatibility function for existing code
def discover_contacts(company_name: str, company_domain: str) -> List[Dict]:
    """
    Backward compatibility wrapper for existing ABM system
    """
    discovery = get_apollo_discovery()
    contacts = discovery.discover_contacts(company_name, company_domain)
    return discovery.convert_to_notion_format(contacts)


if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Apollo Contact Discovery...")

    # Check credits first
    discovery = get_apollo_discovery()
    credits = discovery.get_api_credits_remaining()
    if credits:
        print(f"💰 Available credits: {credits['remaining_credits']}")

    # Test with a sample company
    test_contacts = discover_contacts("Genesis Cloud", "genesiscloud.com")
    print(f"✅ Found {len(test_contacts)} contacts")

    for contact in test_contacts[:3]:  # Show first 3
        print(f"   📧 {contact['name']} - {contact['title']} - {contact.get('email', 'No email')}")
