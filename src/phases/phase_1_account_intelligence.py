"""
Phase 1: Account Intelligence Baseline
Gathers firmographics, detects trigger events, and calculates ICP fit
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging

from ..models import Account, TriggerEvent
from ..models.trigger_event import EventType
from ..data_sources.apollo_client import ApolloClient
from ..data_sources.web_scraper import WebScraper
from ..data_sources.trigger_event_detector import TriggerEventDetector
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class AccountIntelligencePhase:
    """Implements Phase 1: Account Intelligence Baseline"""

    def __init__(self, apollo_client: ApolloClient, web_scraper: WebScraper):
        self.apollo_client = apollo_client
        self.web_scraper = web_scraper
        self.trigger_detector = TriggerEventDetector(web_scraper)

        # Rate limiters for different data sources
        self.apollo_limiter = RateLimiter(delay=0.5)  # Apollo API
        self.web_limiter = RateLimiter(delay=1.0)     # Web scraping

    async def execute(self, account: Account) -> Account:
        """Execute Phase 1 research for an account"""
        logger.info(f"Starting Phase 1 research for {account.name}")

        try:
            # Step 1: Gather company firmographics
            logger.info("Gathering company firmographics...")
            account = await self._gather_firmographics(account)

            # Step 2: Detect trigger events
            logger.info("Detecting trigger events...")
            trigger_events = await self._detect_trigger_events(account)
            for event in trigger_events:
                account.add_trigger_event(event)

            # Step 3: Calculate ICP fit score
            logger.info("Calculating ICP fit score...")
            account.calculate_icp_fit_score()

            # Update research status
            account.research_status = Account.AccountResearchStatus.COMPLETE
            account.last_updated = datetime.now()

            logger.info(f"Phase 1 complete for {account.name} (ICP: {account.icp_fit_score:.1f})")
            return account

        except Exception as e:
            logger.error(f"Phase 1 failed for {account.name}: {e}")
            account.research_status = Account.AccountResearchStatus.IN_PROGRESS
            raise

    async def _gather_firmographics(self, account: Account) -> Account:
        """Gather company firmographics from Apollo and web sources"""

        # Get Apollo company data
        async with self.apollo_limiter:
            apollo_data = await self.apollo_client.get_company_by_domain(account.domain)

        if apollo_data:
            # Map Apollo data to account fields
            account.employee_count = apollo_data.get('employee_count')
            account.revenue = apollo_data.get('estimated_num_employees_range')
            account.linkedin_company_url = apollo_data.get('linkedin_url')
            account.apollo_company_id = apollo_data.get('id')

            # Extract business model from Apollo industry/description
            industry = apollo_data.get('industry', '').lower()
            account.business_model = self._classify_business_model(industry)

        # Supplement with web scraping
        async with self.web_limiter:
            web_data = await self.web_scraper.scrape_company_about_page(account.domain)

        if web_data:
            # Extract additional firmographic data
            if not account.employee_count and 'employee_count' in web_data:
                account.employee_count = web_data['employee_count']

            if 'data_center_locations' in web_data:
                account.data_center_locations = web_data['data_center_locations']

            if 'facility_capacity' in web_data:
                account.facility_capacity = web_data['facility_capacity']

        return account

    def _classify_business_model(self, industry: str) -> str:
        """Classify business model based on industry description"""
        industry_lower = industry.lower()

        if any(term in industry_lower for term in ['cloud', 'aws', 'azure', 'gcp']):
            return 'cloud'
        elif any(term in industry_lower for term in ['colocation', 'colo', 'data center']):
            return 'colocation'
        elif any(term in industry_lower for term in ['hyperscale', 'hyperscaler']):
            return 'hyperscaler'
        elif any(term in industry_lower for term in ['ai', 'ml', 'artificial intelligence', 'gpu']):
            return 'ai-focused'
        elif any(term in industry_lower for term in ['energy', 'power', 'utility']):
            return 'energy-intensive'
        else:
            return 'other'

    async def _detect_trigger_events(self, account: Account) -> List[TriggerEvent]:
        """Detect trigger events for the account"""
        all_events = []

        # Define event sources and lookback period
        lookback_days = 90
        since_date = date.today() - timedelta(days=lookback_days)

        # Search company website/newsroom
        async with self.web_limiter:
            website_events = await self.trigger_detector.scan_company_website(
                account.domain, since_date
            )
            all_events.extend(website_events)

        # Search industry news sources
        async with self.web_limiter:
            news_events = await self.trigger_detector.search_news_sources(
                account.name, since_date
            )
            all_events.extend(news_events)

        # Check LinkedIn company page
        if account.linkedin_company_url:
            async with self.web_limiter:
                linkedin_events = await self.trigger_detector.scan_linkedin_company(
                    account.linkedin_company_url, since_date
                )
                all_events.extend(linkedin_events)

        # Search job postings for growth/turnover signals
        async with self.web_limiter:
            job_events = await self.trigger_detector.scan_job_postings(
                account.domain, since_date
            )
            all_events.extend(job_events)

        # Filter and score events
        filtered_events = self._filter_and_score_events(all_events, account)

        logger.info(f"Detected {len(filtered_events)} trigger events for {account.name}")
        return filtered_events

    def _filter_and_score_events(self, events: List[TriggerEvent],
                                account: Account) -> List[TriggerEvent]:
        """Filter and score trigger events for relevance"""
        filtered = []

        for event in events:
            # Skip low-confidence events
            if event.confidence_score < 30:
                continue

            # Skip events older than lookback period
            if not event.is_recent(days=90):
                continue

            # Attach to account
            event.account = account

            # Boost relevance for data center specific companies
            if account.business_model in ['cloud', 'colocation', 'hyperscaler']:
                event.relevance_score = min(event.relevance_score + 10, 100)

            filtered.append(event)

        # Sort by relevance score (highest first) and limit to top 5
        filtered.sort(key=lambda e: e.relevance_score, reverse=True)
        return filtered[:5]

    def get_phase_summary(self, account: Account) -> Dict[str, Any]:
        """Get summary of Phase 1 results"""
        return {
            'account_name': account.name,
            'icp_fit_score': account.icp_fit_score,
            'business_model': account.business_model,
            'employee_count': account.employee_count,
            'trigger_events_detected': len(account.trigger_events),
            'high_relevance_events': len([e for e in account.trigger_events if e.relevance_score >= 80]),
            'research_status': account.research_status.value,
            'phase_1_complete': True
        }