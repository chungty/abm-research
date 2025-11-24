#!/usr/bin/env python3
"""
Company Enrichment Service
Dynamically fetches company data using Apollo API and other sources
Replaces hardcoded lookup tables with scalable API-based enrichment
"""

import os
import time
import requests
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CompanyData:
    """Structured company data from enrichment APIs"""
    name: str
    domain: str
    employee_count: Optional[int] = None
    business_model: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    apollo_account_id: Optional[str] = None
    apollo_organization_id: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    founded_year: Optional[int] = None
    funding_stage: Optional[str] = None
    enrichment_source: str = "unknown"
    enriched_at: Optional[datetime] = None

class CompanyEnrichmentService:
    """
    Scalable company enrichment using Apollo API and fallback sources
    Dynamically fetches company data without hardcoded lookup tables
    """

    def __init__(self):
        self.apollo_api_key = os.getenv('APOLLO_API_KEY')
        if not self.apollo_api_key:
            raise ValueError("APOLLO_API_KEY environment variable is required")

        self.apollo_base_url = "https://api.apollo.io/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.apollo_api_key
        })

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 1.0  # 1 second between requests

        # Cache for enriched companies (in-memory cache for session)
        self.company_cache = {}

    def enrich_company(self, company_name: str, domain: str) -> CompanyData:
        """
        Enrich company data using Apollo API and fallback sources

        Args:
            company_name: Company name
            domain: Company domain (e.g., 'example.com')

        Returns:
            CompanyData object with enriched information
        """
        logger.info(f"🏢 Enriching company data: {company_name} ({domain})")

        # Check cache first
        cache_key = f"{domain.lower()}_{company_name.lower()}"
        if cache_key in self.company_cache:
            logger.info("✓ Using cached company data")
            return self.company_cache[cache_key]

        # Prevent mock data injection
        if 'coreweave' in domain.lower() or 'coreweave' in company_name.lower():
            raise ValueError("CoreWeave is mock data - not allowed")

        # Primary method: Apollo people search to extract organization data
        # (organizations endpoint appears to require different subscription tier)
        company_data = self._enrich_via_apollo_people_search(company_name, domain)

        if not company_data:
            # Fallback: Try Apollo organizations search (may not be available for this account)
            company_data = self._enrich_via_apollo_organizations(company_name, domain)

        if not company_data:
            # Final fallback: Create minimal company data
            company_data = self._create_minimal_company_data(company_name, domain)

        # Cache the result
        self.company_cache[cache_key] = company_data

        logger.info(f"✓ Company enriched via {company_data.enrichment_source}")
        return company_data

    def _enrich_via_apollo_organizations(self, company_name: str, domain: str) -> Optional[CompanyData]:
        """
        Enrich company using Apollo's organizations endpoint
        """
        try:
            self._apply_rate_limit()

            # Apollo organizations search API
            search_params = {
                "q_organization_domains": [domain],
                "per_page": 1
            }

            logger.info(f"🔍 Searching Apollo organizations for {domain}")
            logger.debug(f"Search params: {search_params}")

            response = self.session.post(
                f"{self.apollo_base_url}/organizations/search",
                json=search_params
            )

            logger.debug(f"Apollo response status: {response.status_code}")
            logger.debug(f"Apollo response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                organizations = data.get('organizations', [])
                logger.info(f"Found {len(organizations)} organizations")

                if organizations:
                    org = organizations[0]
                    logger.info(f"Using organization: {org.get('name', 'Unknown')}")
                    return self._parse_apollo_organization(org, domain)
                else:
                    logger.info("No organization found in Apollo organizations search")
            else:
                logger.warning(f"Apollo organizations search failed: {response.status_code}")
                logger.warning(f"Response: {response.text}")

        except Exception as e:
            logger.warning(f"Apollo organization enrichment failed: {e}")

        return None

    def _enrich_via_apollo_people_search(self, company_name: str, domain: str) -> Optional[CompanyData]:
        """
        Fallback: Extract organization data from Apollo people search
        """
        try:
            self._apply_rate_limit()

            # Search for any person at this organization to get org data
            search_params = {
                "q_organization_domains": [domain],
                "per_page": 1  # Just need one person to extract org data
            }

            logger.info(f"🔍 Searching Apollo people for org data at {domain}")
            logger.debug(f"People search params: {search_params}")

            response = self.session.post(
                f"{self.apollo_base_url}/mixed_people/search",
                json=search_params
            )

            logger.debug(f"People search response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                people = data.get('people', [])
                logger.info(f"Found {len(people)} people at {domain}")

                if people:
                    person = people[0]
                    organization = person.get('organization', {})
                    logger.debug(f"Person organization data: {organization}")

                    if organization and organization.get('name'):
                        logger.info(f"Extracting org data from person: {organization.get('name')}")
                        return self._parse_apollo_organization_from_person(organization, domain)
                    else:
                        logger.info("Person found but no organization data available")
                else:
                    logger.info("No people found in Apollo people search")
            else:
                logger.warning(f"Apollo people search failed: {response.status_code}")
                logger.debug(f"People search response: {response.text}")

        except Exception as e:
            logger.warning(f"Apollo people search fallback failed: {e}")

        return None

    def _parse_apollo_organization(self, org_data: Dict, domain: str) -> CompanyData:
        """
        Parse Apollo organization data into CompanyData structure
        """
        # Extract employee count
        employee_count = None
        employees_range = org_data.get('estimated_num_employees')
        if employees_range:
            employee_count = self._parse_employee_range(employees_range)

        # Determine business model from industry/description
        business_model = self._infer_business_model(
            org_data.get('industry'),
            org_data.get('short_description', ''),
            org_data.get('name', '')
        )

        return CompanyData(
            name=org_data.get('name', 'Unknown'),
            domain=domain,
            employee_count=employee_count,
            business_model=business_model,
            industry=org_data.get('industry'),
            description=org_data.get('short_description'),
            apollo_account_id=str(org_data.get('id', '')),
            apollo_organization_id=str(org_data.get('id', '')),
            linkedin_url=org_data.get('linkedin_url'),
            website=org_data.get('website_url'),
            founded_year=org_data.get('founded_year'),
            funding_stage=org_data.get('funding_stage'),
            enrichment_source="apollo_organizations",
            enriched_at=datetime.now()
        )

    def _parse_apollo_organization_from_person(self, org_data: Dict, domain: str) -> CompanyData:
        """
        Parse Apollo organization data from person search results
        """
        # Employee count from organization object in person data
        employee_count = None
        if 'estimated_num_employees' in org_data:
            employee_count = self._parse_employee_range(org_data['estimated_num_employees'])

        # Infer business model
        business_model = self._infer_business_model(
            org_data.get('industry'),
            org_data.get('description', ''),
            org_data.get('name', '')
        )

        return CompanyData(
            name=org_data.get('name', 'Unknown'),
            domain=domain,
            employee_count=employee_count,
            business_model=business_model,
            industry=org_data.get('industry'),
            description=org_data.get('description'),
            apollo_account_id=str(org_data.get('id', '')),
            apollo_organization_id=str(org_data.get('id', '')),
            linkedin_url=org_data.get('linkedin_url'),
            website=org_data.get('website_url'),
            enrichment_source="apollo_people_fallback",
            enriched_at=datetime.now()
        )

    def _parse_employee_range(self, employees_range: str) -> Optional[int]:
        """
        Parse Apollo employee range string to estimated count

        Examples: "1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5000+"
        """
        if not employees_range:
            return None

        try:
            # Handle ranges like "1-10", "51-200"
            if '-' in employees_range:
                parts = employees_range.split('-')
                min_emp = int(parts[0])
                max_emp = int(parts[1])
                # Return midpoint of range
                return (min_emp + max_emp) // 2

            # Handle "5000+" format
            elif '+' in employees_range:
                base = int(employees_range.replace('+', ''))
                # For 5000+, estimate 7500 (conservative multiplier)
                return int(base * 1.5)

            # Handle single numbers
            else:
                return int(employees_range)

        except (ValueError, IndexError):
            logger.warning(f"Could not parse employee range: {employees_range}")
            return None

    def _infer_business_model(self, industry: Optional[str], description: Optional[str], company_name: Optional[str]) -> str:
        """
        Infer business model from industry and description
        Uses keyword matching to categorize business models
        """
        text_to_analyze = " ".join(filter(None, [industry or "", description or "", company_name or ""])).lower()

        # Business model inference rules
        if any(keyword in text_to_analyze for keyword in ['cloud', 'aws', 'azure', 'hosting', 'infrastructure']):
            return 'Cloud Infrastructure Provider'

        elif any(keyword in text_to_analyze for keyword in ['gpu', 'compute', 'processing', 'hpc']):
            return 'GPU Cloud Computing'

        elif any(keyword in text_to_analyze for keyword in ['data center', 'colocation', 'colo', 'facility']):
            return 'Data Center Services'

        elif any(keyword in text_to_analyze for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            return 'AI Infrastructure Platform'

        elif any(keyword in text_to_analyze for keyword in ['edge', 'cdn', 'network']):
            return 'Edge Computing Services'

        elif any(keyword in text_to_analyze for keyword in ['software', 'saas', 'platform']):
            return 'B2B Software'

        elif any(keyword in text_to_analyze for keyword in ['hardware', 'chip', 'semiconductor']):
            return 'AI Hardware & Software'

        # Default fallback based on industry
        if industry:
            return f"{industry} Services"

        return 'Technology Company'

    def _create_minimal_company_data(self, company_name: str, domain: str) -> CompanyData:
        """
        Create minimal company data when all enrichment methods fail
        """
        return CompanyData(
            name=company_name,
            domain=domain,
            employee_count=None,  # Unknown, don't fake it
            business_model='Technology Company',  # Conservative fallback
            industry='Technology',
            description='Company data not available via API',
            apollo_account_id='',
            apollo_organization_id='',
            enrichment_source="minimal_fallback",
            enriched_at=datetime.now()
        )

    def _apply_rate_limit(self):
        """Apply rate limiting between API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def get_enrichment_stats(self) -> Dict:
        """Get statistics about enriched companies"""
        total = len(self.company_cache)
        sources = {}

        for company in self.company_cache.values():
            source = company.enrichment_source
            sources[source] = sources.get(source, 0) + 1

        return {
            'total_companies_enriched': total,
            'enrichment_sources': sources,
            'cache_size': total
        }

# Export singleton instance
company_enrichment_service = CompanyEnrichmentService()