#!/usr/bin/env python3
"""
Trigger Event Discovery via Brave Search (Decision #3)
Active detection of expansion, hiring, funding, partnership, AI, leadership, and incident signals.
Designed to save results directly to Notion's Trigger Events database.
"""

import os
import re
import time
import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredTriggerEvent:
    """A trigger event discovered via Brave Search"""

    # Core fields
    event_type: str  # expansion, hiring, funding, partnership, ai_workload, leadership, incident
    description: str
    company_name: str

    # Source tracking
    source_url: str
    source_type: str  # News Article, Press Release, Company Website, Job Posting

    # Scoring
    confidence_score: int  # 0-100
    relevance_score: int  # 0-100 (alignment to ICP)
    urgency_level: str  # High, Medium, Low

    # Timing
    detected_date: str  # ISO date string
    event_date: Optional[str] = None  # When the event actually occurred

    # Notion relation (set after save)
    account_id: Optional[str] = None


class TriggerEventDiscovery:
    """
    Discover trigger events for accounts using Brave Search.
    Focused on the 7 key event types from the ABM plan.
    """

    # Event type configurations with search keywords
    EVENT_TYPES = {
        "expansion": {
            "keywords": [
                "expansion",
                "new data center",
                "new facility",
                "construction",
                "capacity increase",
                "new location",
                "buildout",
            ],
            "weight": 1.5,  # High ICP relevance
            "source_priority": ["News Article", "Press Release", "Company Website"],
        },
        "hiring": {
            "keywords": [
                "hiring",
                "job opening",
                "recruiting",
                "new positions",
                "team expansion",
                "careers",
                "looking for",
            ],
            "weight": 1.2,
            "source_priority": ["Job Posting", "LinkedIn", "Company Website"],
        },
        "funding": {
            "keywords": [
                "funding",
                "series",
                "raised",
                "investment",
                "valuation",
                "venture capital",
                "IPO",
                "financing",
            ],
            "weight": 1.4,
            "source_priority": ["News Article", "Press Release"],
        },
        "partnership": {
            "keywords": [
                "partnership",
                "collaboration",
                "alliance",
                "joint venture",
                "strategic partner",
                "integration",
                "ecosystem",
            ],
            "weight": 1.3,
            "source_priority": ["Press Release", "News Article"],
        },
        "ai_workload": {
            "keywords": [
                "AI infrastructure",
                "GPU",
                "machine learning",
                "deep learning",
                "artificial intelligence",
                "ML workloads",
                "AI compute",
            ],
            "weight": 1.8,  # Very high ICP relevance
            "source_priority": ["News Article", "Press Release", "Company Website"],
        },
        "leadership": {
            "keywords": [
                "appointed",
                "new CEO",
                "new CTO",
                "joins",
                "leadership",
                "executive",
                "promoted",
                "board",
            ],
            "weight": 1.1,
            "source_priority": ["Press Release", "News Article", "LinkedIn"],
        },
        "incident": {
            "keywords": [
                "outage",
                "downtime",
                "incident",
                "failure",
                "disruption",
                "issue",
                "problem",
                "blackout",
            ],
            "weight": 1.6,  # High urgency signals
            "source_priority": ["News Article", "Social Media"],
        },
        "dc_power_project": {
            # DC Rectifier ICP - Companies investing in DC power infrastructure
            "keywords": [
                "DC power",
                "rectifier",
                "48V",
                "380V",
                "48VDC",
                "380VDC",
                "power conversion",
                "AC-to-DC",
                "DC infrastructure",
                "rectifier upgrade",
                "DC deployment",
                "DC distribution",
                "busbar",
                "power shelf",
            ],
            "weight": 1.8,  # High relevance - power infrastructure target ICP
            "source_priority": ["Press Release", "News Article", "Company Website"],
        },
    }

    def __init__(self):
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        if not self.brave_api_key:
            logger.warning("BRAVE_API_KEY not set - trigger event discovery disabled")

        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 1.0

    def discover_events(
        self,
        company_name: str,
        company_domain: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        lookback_days: int = 90,
    ) -> List[DiscoveredTriggerEvent]:
        """
        Discover trigger events for a company using Brave Search.

        Args:
            company_name: Name of the company to search
            company_domain: Domain for additional context
            event_types: Specific event types to search (default: all)
            lookback_days: How far back to search

        Returns:
            List of discovered trigger events
        """
        logger.info(f"Discovering trigger events for: {company_name}")

        if not self.brave_api_key:
            logger.warning("No Brave API key - returning empty results")
            return []

        # Default to all event types
        types_to_search = event_types or list(self.EVENT_TYPES.keys())

        all_events = []
        for event_type in types_to_search:
            if event_type not in self.EVENT_TYPES:
                logger.warning(f"Unknown event type: {event_type}")
                continue

            events = self._search_event_type(
                company_name=company_name,
                company_domain=company_domain,
                event_type=event_type,
                lookback_days=lookback_days,
            )
            all_events.extend(events)

        # Deduplicate by URL
        unique_events = self._deduplicate_events(all_events)

        # Sort by relevance * confidence
        sorted_events = sorted(
            unique_events, key=lambda e: e.relevance_score * e.confidence_score, reverse=True
        )

        logger.info(f"Discovered {len(sorted_events)} unique trigger events")
        return sorted_events[:20]  # Return top 20 events

    def _search_event_type(
        self, company_name: str, company_domain: Optional[str], event_type: str, lookback_days: int
    ) -> List[DiscoveredTriggerEvent]:
        """Search for a specific event type"""
        events = []
        config = self.EVENT_TYPES[event_type]

        try:
            self._apply_rate_limit()

            # Build search query
            keywords = config["keywords"][:3]  # Use top 3 keywords
            keyword_query = " OR ".join(keywords)
            query = f'"{company_name}" ({keyword_query})'

            # Determine freshness parameter
            if lookback_days <= 7:
                freshness = "pd"  # Past day
            elif lookback_days <= 30:
                freshness = "pw"  # Past week
            elif lookback_days <= 90:
                freshness = "pm"  # Past month
            else:
                freshness = "py"  # Past year

            logger.debug(f"Searching: {event_type} for {company_name}")

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 10, "freshness": freshness},
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                logger.warning(f"Brave search failed: {response.status_code}")
                return events

            data = response.json()

            # Check for news results first
            news_results = data.get("news", {}).get("results", [])
            web_results = data.get("web", {}).get("results", [])

            # Process news results (higher confidence)
            for result in news_results:
                event = self._parse_news_result(result, event_type, company_name, config)
                if event:
                    events.append(event)

            # Process web results (lower confidence)
            for result in web_results:
                event = self._parse_web_result(result, event_type, company_name, config)
                if event:
                    events.append(event)

            logger.debug(f"Found {len(events)} events for {event_type}")

        except Exception as e:
            logger.warning(f"Error searching {event_type}: {e}")

        return events

    def _parse_news_result(
        self, result: Dict, event_type: str, company_name: str, config: Dict
    ) -> Optional[DiscoveredTriggerEvent]:
        """Parse a news search result into a trigger event"""
        try:
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")
            age = result.get("age", "")

            # Skip if no URL
            if not url:
                return None

            # Calculate confidence (news = higher)
            base_confidence = 75
            if "press release" in title.lower() or "announces" in title.lower():
                base_confidence = 85
            elif "reports" in title.lower() or "confirms" in title.lower():
                base_confidence = 80

            # Calculate relevance based on ICP weight
            base_relevance = int(50 * config["weight"])

            # Boost if description contains strong keywords
            keywords_found = sum(
                1 for kw in config["keywords"] if kw.lower() in description.lower()
            )
            base_relevance += min(30, keywords_found * 10)

            # Determine urgency
            urgency = self._calculate_urgency(event_type, age, base_confidence)

            # Create event
            return DiscoveredTriggerEvent(
                event_type=event_type,
                description=self._create_description(title, description, company_name, event_type),
                company_name=company_name,
                source_url=url,
                source_type="News Article",
                confidence_score=min(100, base_confidence),
                relevance_score=min(100, base_relevance),
                urgency_level=urgency,
                detected_date=datetime.now().isoformat(),
                event_date=self._parse_age_to_date(age),
            )

        except Exception as e:
            logger.warning(f"Error parsing news result: {e}")
            return None

    def _parse_web_result(
        self, result: Dict, event_type: str, company_name: str, config: Dict
    ) -> Optional[DiscoveredTriggerEvent]:
        """Parse a web search result into a trigger event"""
        try:
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")

            # Skip if no URL
            if not url:
                return None

            # Determine source type from URL
            source_type = self._determine_source_type(url)

            # Calculate confidence (web = lower than news)
            base_confidence = 55
            if "official" in url.lower() or "press" in url.lower():
                base_confidence = 70
            elif "linkedin.com" in url.lower():
                base_confidence = 65

            # Calculate relevance
            base_relevance = int(45 * config["weight"])
            keywords_found = sum(
                1 for kw in config["keywords"] if kw.lower() in description.lower()
            )
            base_relevance += min(25, keywords_found * 8)

            # Determine urgency
            urgency = self._calculate_urgency(event_type, None, base_confidence)

            return DiscoveredTriggerEvent(
                event_type=event_type,
                description=self._create_description(title, description, company_name, event_type),
                company_name=company_name,
                source_url=url,
                source_type=source_type,
                confidence_score=min(100, base_confidence),
                relevance_score=min(100, base_relevance),
                urgency_level=urgency,
                detected_date=datetime.now().isoformat(),
                event_date=None,
            )

        except Exception as e:
            logger.warning(f"Error parsing web result: {e}")
            return None

    def _create_description(
        self, title: str, snippet: str, company_name: str, event_type: str
    ) -> str:
        """Create a clean event description"""
        # Clean up title
        title = re.sub(r"\s+", " ", title).strip()

        # If title mentions company, use it directly
        if company_name.lower() in title.lower():
            return title[:200]

        # Otherwise, combine with context
        return f"{company_name}: {title}"[:200]

    def _determine_source_type(self, url: str) -> str:
        """Determine source type from URL"""
        url_lower = url.lower()

        if "linkedin.com" in url_lower:
            return "LinkedIn"
        elif "/careers" in url_lower or "/jobs" in url_lower or "greenhouse.io" in url_lower:
            return "Job Posting"
        elif "/press" in url_lower or "/news" in url_lower:
            return "Press Release"
        elif any(domain in url_lower for domain in [".com/blog", "medium.com", "substack.com"]):
            return "Blog Post"
        else:
            return "Company Website"

    def _calculate_urgency(self, event_type: str, age: Optional[str], confidence: int) -> str:
        """Calculate urgency level"""
        # Base urgency by event type
        high_urgency_types = {"incident", "funding", "expansion"}
        medium_urgency_types = {"leadership", "partnership", "ai_workload"}

        if event_type in high_urgency_types:
            base_urgency = "High"
        elif event_type in medium_urgency_types:
            base_urgency = "Medium"
        else:
            base_urgency = "Low"

        # Adjust by recency
        if age:
            if any(term in age.lower() for term in ["hour", "today", "minute"]):
                return "High"  # Very recent
            elif any(term in age.lower() for term in ["day", "yesterday"]):
                if base_urgency == "Low":
                    return "Medium"
                return base_urgency
            elif "week" in age.lower():
                if base_urgency == "High":
                    return "Medium"
                return base_urgency

        return base_urgency

    def _parse_age_to_date(self, age: Optional[str]) -> Optional[str]:
        """Parse age string to ISO date"""
        if not age:
            return None

        try:
            age_lower = age.lower()
            today = datetime.now()

            if "hour" in age_lower or "minute" in age_lower:
                return today.date().isoformat()
            elif "yesterday" in age_lower:
                return (today - timedelta(days=1)).date().isoformat()
            elif "day" in age_lower:
                # Try to extract number
                match = re.search(r"(\d+)", age_lower)
                if match:
                    days = int(match.group(1))
                    return (today - timedelta(days=days)).date().isoformat()
            elif "week" in age_lower:
                match = re.search(r"(\d+)", age_lower)
                if match:
                    weeks = int(match.group(1))
                    return (today - timedelta(weeks=weeks)).date().isoformat()
                return (today - timedelta(weeks=1)).date().isoformat()
            elif "month" in age_lower:
                match = re.search(r"(\d+)", age_lower)
                if match:
                    months = int(match.group(1))
                    return (today - timedelta(days=months * 30)).date().isoformat()
                return (today - timedelta(days=30)).date().isoformat()

        except Exception:
            pass

        return None

    def _deduplicate_events(
        self, events: List[DiscoveredTriggerEvent]
    ) -> List[DiscoveredTriggerEvent]:
        """Remove duplicate events based on URL"""
        seen_urls = set()
        unique = []

        for event in events:
            if event.source_url not in seen_urls:
                seen_urls.add(event.source_url)
                unique.append(event)

        return unique

    def _apply_rate_limit(self):
        """Apply rate limiting between API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def to_notion_properties(
        self, event: DiscoveredTriggerEvent, account_page_id: Optional[str] = None
    ) -> Dict:
        """
        Convert a discovered event to Notion properties format.
        Ready to be saved to the Trigger Events database.
        """
        properties = {
            "Event Description": {"title": [{"text": {"content": event.description}}]},
            "Event Type": {"select": {"name": event.event_type.replace("_", " ").title()}},
            "Confidence": {"select": {"name": self._score_to_level(event.confidence_score)}},
            "Source URL": {"url": event.source_url},
            "Detected Date": {"date": {"start": event.detected_date[:10]}},  # Just the date part
            "Urgency Level": {"select": {"name": event.urgency_level}},
        }

        # Add event date if available
        if event.event_date:
            properties["Occurred Date"] = {"date": {"start": event.event_date}}

        # Add account relation if provided
        if account_page_id:
            properties["Account"] = {"relation": [{"id": account_page_id}]}

        return properties

    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to High/Medium/Low"""
        if score >= 75:
            return "High"
        elif score >= 50:
            return "Medium"
        return "Low"


# Export singleton instance
trigger_event_discovery = TriggerEventDiscovery()
