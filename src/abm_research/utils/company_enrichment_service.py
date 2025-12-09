#!/usr/bin/env python3
"""
Company Enrichment Service
Dynamically fetches company data using Apollo API and other sources
Replaces hardcoded lookup tables with scalable API-based enrichment
"""

import os
import re
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
        self.apollo_api_key = os.getenv("APOLLO_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")

        if not self.apollo_api_key:
            logger.warning("APOLLO_API_KEY not set - Apollo enrichment will be disabled")
        if not self.brave_api_key:
            logger.warning("BRAVE_API_KEY not set - Brave fallback will be disabled")

        self.apollo_base_url = "https://api.apollo.io/v1"
        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "X-Api-Key": self.apollo_api_key or "",
            }
        )

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

        # PRIMARY METHOD: Apollo Organization Enrichment API
        # This is the correct endpoint for enriching known domains
        company_data = self._enrich_via_apollo_organization_enrich(company_name, domain)

        if not company_data:
            # Fallback 1: Try Apollo people search to extract organization data
            company_data = self._enrich_via_apollo_people_search(company_name, domain)

        if not company_data:
            # Fallback 2: Try Brave Search API for web data
            company_data = self._enrich_via_brave_search(company_name, domain)

        if not company_data:
            # Final fallback: Create minimal company data
            company_data = self._create_minimal_company_data(company_name, domain)

        # Cache the result
        self.company_cache[cache_key] = company_data

        logger.info(f"✓ Company enriched via {company_data.enrichment_source}")
        return company_data

    def _enrich_via_apollo_organization_enrich(
        self, company_name: str, domain: str
    ) -> Optional[CompanyData]:
        """
        PRIMARY: Enrich company using Apollo's Organization Enrichment API
        This endpoint returns rich company data for a known domain.
        """
        if not self.apollo_api_key:
            logger.info("Apollo API key not configured, skipping Apollo enrichment")
            return None

        try:
            self._apply_rate_limit()

            logger.info(f"🔍 Apollo Organization Enrichment for {domain}")

            response = self.session.post(
                f"{self.apollo_base_url}/organizations/enrich", json={"domain": domain}
            )

            logger.debug(f"Apollo enrich response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                org = data.get("organization", {})

                if org and org.get("name"):
                    logger.info(
                        f"✓ Apollo enriched: {org.get('name')} ({org.get('estimated_num_employees', '?')} employees)"
                    )
                    return self._parse_apollo_enrichment(org, domain)
                else:
                    logger.info("Apollo enrichment returned no organization data")
            else:
                logger.warning(f"Apollo organization enrichment failed: {response.status_code}")
                logger.debug(f"Response: {response.text}")

        except Exception as e:
            logger.warning(f"Apollo organization enrichment failed: {e}")

        return None

    def _parse_apollo_enrichment(self, org_data: Dict, domain: str) -> CompanyData:
        """
        Parse Apollo Organization Enrichment API response into CompanyData
        This endpoint returns much richer data than the search endpoint.
        """
        # Get employee count (exact number from enrichment API)
        employee_count = org_data.get("estimated_num_employees")

        # Infer business model from industry, keywords, and description
        keywords = org_data.get("keywords", [])
        keywords_str = " ".join(keywords[:20]) if keywords else ""
        business_model = self._infer_business_model(
            org_data.get("industry"),
            f"{org_data.get('short_description', '')} {keywords_str}",
            org_data.get("name", ""),
        )

        # Extract funding information
        funding_stage = None
        funding_events = org_data.get("funding_events", [])
        if funding_events:
            latest_event = funding_events[0]  # Most recent first
            funding_stage = latest_event.get("type")

        return CompanyData(
            name=org_data.get("name", "Unknown"),
            domain=domain,
            employee_count=employee_count,
            business_model=business_model,
            industry=org_data.get("industry"),
            description=org_data.get("short_description"),
            apollo_account_id=str(org_data.get("account", {}).get("id", "")),
            apollo_organization_id=str(org_data.get("id", "")),
            linkedin_url=org_data.get("linkedin_url"),
            website=org_data.get("website_url"),
            founded_year=org_data.get("founded_year"),
            funding_stage=funding_stage,
            enrichment_source="apollo_enrichment",
            enriched_at=datetime.now(),
        )

    def _enrich_via_apollo_organizations(
        self, company_name: str, domain: str
    ) -> Optional[CompanyData]:
        """
        DEPRECATED: Apollo organizations search endpoint returns 0 results for most queries.
        Use _enrich_via_apollo_organization_enrich instead.
        Kept for backwards compatibility.
        """
        # This endpoint doesn't work well - skip it
        logger.debug("Skipping deprecated organizations/search endpoint")
        return None

    def _enrich_via_apollo_people_search(
        self, company_name: str, domain: str
    ) -> Optional[CompanyData]:
        """
        Fallback: Extract organization data from Apollo people search
        """
        try:
            self._apply_rate_limit()

            # Search for any person at this organization to get org data
            search_params = {
                "q_organization_domains": [domain],
                "per_page": 1,  # Just need one person to extract org data
            }

            logger.info(f"🔍 Searching Apollo people for org data at {domain}")
            logger.debug(f"People search params: {search_params}")

            response = self.session.post(
                f"{self.apollo_base_url}/mixed_people/search", json=search_params
            )

            logger.debug(f"People search response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                people = data.get("people", [])
                logger.info(f"Found {len(people)} people at {domain}")

                if people:
                    person = people[0]
                    organization = person.get("organization", {})
                    logger.debug(f"Person organization data: {organization}")

                    if organization and organization.get("name"):
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
        employees_range = org_data.get("estimated_num_employees")
        if employees_range:
            employee_count = self._parse_employee_range(employees_range)

        # Determine business model from industry/description
        business_model = self._infer_business_model(
            org_data.get("industry"),
            org_data.get("short_description", ""),
            org_data.get("name", ""),
        )

        return CompanyData(
            name=org_data.get("name", "Unknown"),
            domain=domain,
            employee_count=employee_count,
            business_model=business_model,
            industry=org_data.get("industry"),
            description=org_data.get("short_description"),
            apollo_account_id=str(org_data.get("id", "")),
            apollo_organization_id=str(org_data.get("id", "")),
            linkedin_url=org_data.get("linkedin_url"),
            website=org_data.get("website_url"),
            founded_year=org_data.get("founded_year"),
            funding_stage=org_data.get("funding_stage"),
            enrichment_source="apollo_organizations",
            enriched_at=datetime.now(),
        )

    def _parse_apollo_organization_from_person(self, org_data: Dict, domain: str) -> CompanyData:
        """
        Parse Apollo organization data from person search results
        """
        # Employee count from organization object in person data
        employee_count = None
        if "estimated_num_employees" in org_data:
            employee_count = self._parse_employee_range(org_data["estimated_num_employees"])

        # Infer business model
        business_model = self._infer_business_model(
            org_data.get("industry"), org_data.get("description", ""), org_data.get("name", "")
        )

        return CompanyData(
            name=org_data.get("name", "Unknown"),
            domain=domain,
            employee_count=employee_count,
            business_model=business_model,
            industry=org_data.get("industry"),
            description=org_data.get("description"),
            apollo_account_id=str(org_data.get("id", "")),
            apollo_organization_id=str(org_data.get("id", "")),
            linkedin_url=org_data.get("linkedin_url"),
            website=org_data.get("website_url"),
            enrichment_source="apollo_people_fallback",
            enriched_at=datetime.now(),
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
            if "-" in employees_range:
                parts = employees_range.split("-")
                min_emp = int(parts[0])
                max_emp = int(parts[1])
                # Return midpoint of range
                return (min_emp + max_emp) // 2

            # Handle "5000+" format
            elif "+" in employees_range:
                base = int(employees_range.replace("+", ""))
                # For 5000+, estimate 7500 (conservative multiplier)
                return int(base * 1.5)

            # Handle single numbers
            else:
                return int(employees_range)

        except (ValueError, IndexError):
            logger.warning(f"Could not parse employee range: {employees_range}")
            return None

    def _infer_business_model(
        self, industry: Optional[str], description: Optional[str], company_name: Optional[str]
    ) -> str:
        """
        Infer business model from industry and description
        Uses keyword matching to categorize business models
        """
        text_to_analyze = " ".join(
            filter(None, [industry or "", description or "", company_name or ""])
        ).lower()

        # Business model inference rules
        if any(
            keyword in text_to_analyze
            for keyword in ["cloud", "aws", "azure", "hosting", "infrastructure"]
        ):
            return "Cloud Infrastructure Provider"

        elif any(keyword in text_to_analyze for keyword in ["gpu", "compute", "processing", "hpc"]):
            return "GPU Cloud Computing"

        elif any(
            keyword in text_to_analyze
            for keyword in ["data center", "colocation", "colo", "facility"]
        ):
            return "Data Center Services"

        elif any(
            keyword in text_to_analyze
            for keyword in ["ai", "artificial intelligence", "machine learning", "ml"]
        ):
            return "AI Infrastructure Platform"

        elif any(keyword in text_to_analyze for keyword in ["edge", "cdn", "network"]):
            return "Edge Computing Services"

        elif any(keyword in text_to_analyze for keyword in ["software", "saas", "platform"]):
            return "B2B Software"

        elif any(keyword in text_to_analyze for keyword in ["hardware", "chip", "semiconductor"]):
            return "AI Hardware & Software"

        # Default fallback based on industry
        if industry:
            return f"{industry} Services"

        return "Technology Company"

    def _enrich_via_brave_search(self, company_name: str, domain: str) -> Optional[CompanyData]:
        """
        Fallback enrichment using Brave Search API to extract company data from web results.
        Searches for employee count, industry, and other public company information.
        """
        if not self.brave_api_key:
            logger.info("Brave API key not configured, skipping Brave enrichment")
            return None

        try:
            self._apply_rate_limit()

            # Search for company information
            query = f"{company_name} company employees headquarters funding"
            logger.info(f"🔍 Searching Brave for company data: {company_name}")

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 5},
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                logger.warning(f"Brave search failed: {response.status_code}")
                return None

            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            if not web_results:
                logger.info("No Brave search results found")
                return None

            # Extract data from search results
            employee_count = None
            industry = None
            description = None
            funding_stage = None

            for result in web_results:
                title = result.get("title", "").lower()
                desc = result.get("description", "")

                # Extract employee count from descriptions
                if not employee_count:
                    emp_match = re.search(
                        r"(\d{1,3}(?:,\d{3})*|\d+)\s*(?:\+\s*)?(?:employees?|workers|team members|people)",
                        desc,
                        re.I,
                    )
                    if emp_match:
                        emp_str = emp_match.group(1).replace(",", "")
                        employee_count = int(emp_str)
                        logger.info(f"Found employee count via Brave: {employee_count}")

                # Try to extract employee range like "51-200 employees"
                if not employee_count:
                    range_match = re.search(
                        r"(\d+)\s*[-–]\s*(\d+)\s*(?:employees?|people)", desc, re.I
                    )
                    if range_match:
                        min_emp = int(range_match.group(1))
                        max_emp = int(range_match.group(2))
                        employee_count = (min_emp + max_emp) // 2
                        logger.info(
                            f"Found employee range via Brave: {min_emp}-{max_emp}, using {employee_count}"
                        )

                # Extract funding information
                if not funding_stage:
                    funding_match = re.search(r"(Series\s+[A-F]|Seed|Pre-Seed|unicorn)", desc, re.I)
                    if funding_match:
                        funding_stage = funding_match.group(1)
                        logger.info(f"Found funding stage via Brave: {funding_stage}")

                # Use first result description as company description
                if not description and len(desc) > 50:
                    description = desc[:300]

            if employee_count or description:
                # Infer business model from search results
                combined_text = " ".join([r.get("description", "") for r in web_results[:3]])
                business_model = self._infer_business_model(industry, combined_text, company_name)

                logger.info(f"✓ Brave enrichment successful for {company_name}")
                return CompanyData(
                    name=company_name,
                    domain=domain,
                    employee_count=employee_count,
                    business_model=business_model,
                    industry=industry or "Technology",
                    description=description,
                    funding_stage=funding_stage,
                    enrichment_source="brave_search",
                    enriched_at=datetime.now(),
                )

            logger.info("Brave search found results but no extractable company data")
            return None

        except Exception as e:
            logger.warning(f"Brave search enrichment failed: {e}")
            return None

    def _create_minimal_company_data(self, company_name: str, domain: str) -> CompanyData:
        """
        Create minimal company data when all enrichment methods fail
        """
        return CompanyData(
            name=company_name,
            domain=domain,
            employee_count=None,  # Unknown, don't fake it
            business_model="Technology Company",  # Conservative fallback
            industry="Technology",
            description="Company data not available via API",
            apollo_account_id="",
            apollo_organization_id="",
            enrichment_source="minimal_fallback",
            enriched_at=datetime.now(),
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
            "total_companies_enriched": total,
            "enrichment_sources": sources,
            "cache_size": total,
        }


# Export singleton instance
company_enrichment_service = CompanyEnrichmentService()
