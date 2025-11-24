"""
Apollo.io API client for company and contact data
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ApolloClient:
    """Client for Apollo.io API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'X-Api-Key': self.api_key
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, params: Dict = None,
                          data: Dict = None) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Apollo API"""
        if not self.session:
            raise RuntimeError("Apollo client not initialized. Use 'async with' context manager.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with self.session.request(method, url, params=params, json=data) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit - wait and retry once
                    logger.warning("Apollo API rate limit hit, waiting 10 seconds...")
                    await asyncio.sleep(10)
                    async with self.session.request(method, url, params=params, json=data) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            logger.error(f"Apollo API retry failed: {retry_response.status}")
                            return None
                else:
                    logger.error(f"Apollo API error: {response.status} - {await response.text()}")
                    return None

        except Exception as e:
            logger.error(f"Apollo API request failed: {e}")
            return None

    async def get_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get company information by domain"""
        logger.info(f"Fetching company data for domain: {domain}")

        params = {
            'domain': domain
        }

        response = await self._make_request('GET', '/organizations/enrich', params=params)

        if response and 'organization' in response:
            org = response['organization']
            return {
                'id': org.get('id'),
                'name': org.get('name'),
                'domain': org.get('primary_domain'),
                'employee_count': org.get('estimated_num_employees'),
                'estimated_num_employees_range': org.get('estimated_num_employees_range'),
                'industry': org.get('industry'),
                'linkedin_url': org.get('linkedin_url'),
                'twitter_url': org.get('twitter_url'),
                'facebook_url': org.get('facebook_url'),
                'primary_phone': org.get('primary_phone'),
                'founded_year': org.get('founded_year'),
                'publicly_traded_symbol': org.get('publicly_traded_symbol'),
                'publicly_traded_exchange': org.get('publicly_traded_exchange'),
                'logo_url': org.get('logo_url'),
                'short_description': org.get('short_description'),
                'annual_revenue': org.get('annual_revenue')
            }

        return None

    async def search_contacts(self, domain: str, titles: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search for contacts at a company by domain and titles"""
        logger.info(f"Searching contacts for domain: {domain}, titles: {titles[:3]}...")

        # Build search payload
        payload = {
            'q_organization_domains': [domain],
            'person_titles': titles,
            'per_page': min(limit, 50),  # Apollo max per page
            'page': 1
        }

        response = await self._make_request('POST', '/mixed_people/search', data=payload)

        if response and 'people' in response:
            contacts = []
            for person in response['people']:
                contact_data = {
                    'id': person.get('id'),
                    'name': person.get('name'),
                    'first_name': person.get('first_name'),
                    'last_name': person.get('last_name'),
                    'title': person.get('title'),
                    'email': person.get('email'),
                    'linkedin_url': person.get('linkedin_url'),
                    'twitter_url': person.get('twitter_url'),
                    'github_url': person.get('github_url'),
                    'facebook_url': person.get('facebook_url'),
                    'sanitized_phone': person.get('sanitized_phone'),
                    'bio': person.get('bio'),
                    'city': person.get('city'),
                    'state': person.get('state'),
                    'country': person.get('country'),
                    'employment_history': person.get('employment_history', []),
                    'organization': person.get('organization', {})
                }
                contacts.append(contact_data)

            logger.info(f"Found {len(contacts)} contacts for {domain}")
            return contacts

        logger.warning(f"No contacts found for {domain}")
        return []

    async def get_contact_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed contact information by ID"""
        logger.info(f"Fetching detailed contact data for ID: {contact_id}")

        params = {
            'id': contact_id
        }

        response = await self._make_request('GET', '/people/match', params=params)

        if response and 'person' in response:
            return response['person']

        return None

    async def enrich_contact(self, email: str = None, linkedin_url: str = None) -> Optional[Dict[str, Any]]:
        """Enrich contact data by email or LinkedIn URL"""
        if not email and not linkedin_url:
            raise ValueError("Either email or linkedin_url must be provided")

        logger.info(f"Enriching contact: email={email}, linkedin={linkedin_url}")

        payload = {}
        if email:
            payload['email'] = email
        if linkedin_url:
            payload['linkedin_url'] = linkedin_url

        response = await self._make_request('POST', '/people/enrich', data=payload)

        if response and 'person' in response:
            return response['person']

        return None

    async def get_target_titles(self) -> List[str]:
        """Get default target titles for data center operations contacts"""
        return [
            "Vice President of Data Center Operations",
            "Vice President of Critical Infrastructure",
            "Vice President of Infrastructure & Operations",
            "Director of Data Center Operations",
            "Director of Data Center Facilities",
            "Director of Critical Infrastructure",
            "Director of Site Operations",
            "Senior Manager of Data Center Operations",
            "Manager of Data Center Operations",
            "Head of Data Center Engineering",
            "Global Head of Data Center Operations",
            "VP Data Center Operations",
            "VP Critical Infrastructure",
            "VP Infrastructure Operations"
        ]

    async def test_connection(self) -> bool:
        """Test Apollo API connection and authentication"""
        try:
            response = await self._make_request('GET', '/auth/health')
            return response is not None
        except Exception as e:
            logger.error(f"Apollo connection test failed: {e}")
            return False