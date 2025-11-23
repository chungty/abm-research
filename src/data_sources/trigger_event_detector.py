"""
Trigger Event Detection System
Implements the detection methodology from trigger_events.md
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import logging
import re

from ..models.trigger_event import TriggerEvent, EventType, ConfidenceLevel
from .web_scraper import WebScraper

logger = logging.getLogger(__name__)


class TriggerEventDetector:
    """Detects trigger events for target accounts"""

    def __init__(self, web_scraper: WebScraper):
        self.web_scraper = web_scraper

        # Event detection keywords by category
        self.event_keywords = {
            EventType.EXPANSION: [
                'expansion', 'new data center', 'new facility', 'construction',
                'acquired', 'acquisition', 'opening', 'buildout'
            ],
            EventType.INHERITED_INFRASTRUCTURE: [
                'merger', 'acquisition', 'inherited', 'legacy system',
                'integration', 'consolidation'
            ],
            EventType.LEADERSHIP_CHANGE: [
                'new', 'appointed', 'hired', 'joins', 'cto', 'vp',
                'director', 'chief', 'head of'
            ],
            EventType.AI_WORKLOAD: [
                'ai', 'artificial intelligence', 'machine learning', 'ml',
                'gpu', 'nvidia', 'hpc', 'high performance computing'
            ],
            EventType.ENERGY_PRESSURE: [
                'energy cost', 'power cost', 'efficiency', 'pue',
                'sustainability', 'carbon', 'renewable'
            ],
            EventType.DOWNTIME_INCIDENT: [
                'outage', 'downtime', 'incident', 'failure', 'disruption',
                'offline', 'maintenance'
            ],
            EventType.SUSTAINABILITY: [
                'sustainability', 'green', 'carbon neutral', 'renewable',
                'esg', 'environment', 'climate'
            ]
        }

        # News sources by confidence level
        self.news_sources = {
            'high_confidence': [
                'sec.gov', 'investors.', 'newsroom', 'press-release'
            ],
            'medium_confidence': [
                'datacenterdynamics.com', 'datacenterknowledge.com',
                'bloomberg.com', 'reuters.com', 'wsj.com',
                'missioncriticalmagazine.com'
            ],
            'low_confidence': [
                'twitter.com', 'linkedin.com/posts', 'reddit.com'
            ]
        }

    async def scan_company_website(self, domain: str, since_date: date) -> List[TriggerEvent]:
        """Scan company website for trigger events"""
        logger.info(f"Scanning {domain} website for trigger events since {since_date}")

        events = []

        # Search newsroom/press releases
        keywords = []
        for event_type, type_keywords in self.event_keywords.items():
            keywords.extend(type_keywords)

        try:
            articles = await self.web_scraper.search_company_newsroom(domain, keywords)

            for article in articles:
                # Skip old articles
                if article.get('date') and article['date'] < since_date:
                    continue

                # Analyze article for trigger events
                detected_events = self._analyze_article_for_events(
                    article, domain, source_confidence=95  # High confidence for company sources
                )
                events.extend(detected_events)

        except Exception as e:
            logger.error(f"Error scanning company website {domain}: {e}")

        return events

    async def search_news_sources(self, company_name: str, since_date: date) -> List[TriggerEvent]:
        """Search industry news sources for company mentions"""
        logger.info(f"Searching news sources for {company_name} since {since_date}")

        events = []

        # For now, this is a placeholder - would integrate with news APIs
        # TODO: Integrate with Google News API, Bing News API, or RSS feeds
        logger.warning("News source integration not yet implemented")

        return events

    async def scan_linkedin_company(self, linkedin_url: str, since_date: date) -> List[TriggerEvent]:
        """Scan LinkedIn company page for announcements"""
        logger.info(f"Scanning LinkedIn company page: {linkedin_url}")

        events = []

        try:
            # Extract domain from LinkedIn URL to get company posts
            # This would require LinkedIn scraping capabilities
            # TODO: Implement LinkedIn company page scraping
            logger.warning("LinkedIn company scanning not yet implemented")

        except Exception as e:
            logger.error(f"Error scanning LinkedIn company page: {e}")

        return events

    async def scan_job_postings(self, domain: str, since_date: date) -> List[TriggerEvent]:
        """Scan job postings for growth/turnover signals"""
        logger.info(f"Scanning job postings for {domain}")

        events = []

        # Look for specific role types that indicate trigger events
        leadership_roles = [
            'VP', 'Vice President', 'Director', 'Head of', 'Chief'
        ]

        operations_roles = [
            'Data Center Operations', 'Infrastructure', 'Facilities',
            'Site Operations', 'Critical Systems'
        ]

        try:
            # This would integrate with job board APIs or scraping
            # TODO: Integrate with job board APIs (Indeed, LinkedIn Jobs, etc.)
            logger.warning("Job posting integration not yet implemented")

        except Exception as e:
            logger.error(f"Error scanning job postings: {e}")

        return events

    def _analyze_article_for_events(self, article: Dict[str, Any], domain: str,
                                   source_confidence: int) -> List[TriggerEvent]:
        """Analyze article content for trigger events"""
        events = []

        title = article.get('title', '')
        content = article.get('content', '')
        full_text = f"{title} {content}".lower()

        # Check each event type
        for event_type, keywords in self.event_keywords.items():
            if self._text_contains_keywords(full_text, keywords):
                # Create trigger event
                event = self._create_trigger_event(
                    event_type=event_type,
                    article=article,
                    domain=domain,
                    source_confidence=source_confidence
                )
                if event:
                    events.append(event)

        return events

    def _text_contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords"""
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False

    def _create_trigger_event(self, event_type: EventType, article: Dict[str, Any],
                            domain: str, source_confidence: int) -> Optional[TriggerEvent]:
        """Create trigger event from article"""
        try:
            title = article.get('title', '')
            content = article.get('content', '')
            url = article.get('url', '')
            event_date = article.get('date')

            # Generate description
            description = self._generate_event_description(event_type, title, content)
            if not description:
                return None

            # Calculate relevance score based on content
            relevance_score = self._calculate_relevance_score(event_type, title, content)

            # Create the event
            event = TriggerEvent(
                description=description,
                event_type=event_type,
                confidence_level=ConfidenceLevel.HIGH,  # Will be adjusted in __post_init__
                confidence_score=source_confidence,
                relevance_score=relevance_score,
                source_url=url,
                event_date=event_date or date.today()
            )

            return event

        except Exception as e:
            logger.error(f"Error creating trigger event: {e}")
            return None

    def _generate_event_description(self, event_type: EventType, title: str, content: str) -> str:
        """Generate event description from article title and content"""
        if title:
            return title.strip()

        # Extract first meaningful sentence from content
        if content:
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Skip short fragments
                    return sentence[:200] + "..." if len(sentence) > 200 else sentence

        return f"{event_type.value} detected"

    def _calculate_relevance_score(self, event_type: EventType, title: str, content: str) -> float:
        """Calculate relevance score based on event type and content"""
        full_text = f"{title} {content}".lower()

        # Base scores by event type (aligned with your skill)
        base_scores = {
            EventType.AI_WORKLOAD: 90,
            EventType.ENERGY_PRESSURE: 85,
            EventType.DOWNTIME_INCIDENT: 80,
            EventType.EXPANSION: 70,
            EventType.LEADERSHIP_CHANGE: 65,
            EventType.SUSTAINABILITY: 60,
            EventType.INHERITED_INFRASTRUCTURE: 55
        }

        base_score = base_scores.get(event_type, 50)

        # High relevance keywords (boost score)
        high_relevance_terms = [
            'power', 'energy', 'capacity', 'uptime', 'ai infrastructure',
            'gpu', 'data center operations', 'electrical', 'cooling'
        ]

        # Medium relevance keywords
        medium_relevance_terms = [
            'infrastructure', 'facility', 'expansion', 'merger',
            'acquisition', 'sustainability', 'cost reduction'
        ]

        # Count keyword matches
        high_matches = sum(1 for term in high_relevance_terms if term in full_text)
        medium_matches = sum(1 for term in medium_relevance_terms if term in full_text)

        # Apply boosts
        if high_matches >= 2:
            base_score += 20
        elif high_matches >= 1:
            base_score += 10

        if medium_matches >= 3:
            base_score += 10
        elif medium_matches >= 1:
            base_score += 5

        return min(100, base_score)

    def _determine_source_confidence(self, url: str) -> int:
        """Determine confidence level based on source URL"""
        if not url:
            return 30

        url_lower = url.lower()

        # Check high confidence sources
        for domain in self.news_sources['high_confidence']:
            if domain in url_lower:
                return 95

        # Check medium confidence sources
        for domain in self.news_sources['medium_confidence']:
            if domain in url_lower:
                return 70

        # Check low confidence sources
        for domain in self.news_sources['low_confidence']:
            if domain in url_lower:
                return 40

        # Default confidence for unknown sources
        return 50

    async def get_trigger_event_summary(self, events: List[TriggerEvent]) -> Dict[str, Any]:
        """Generate summary of detected trigger events"""
        if not events:
            return {
                'total_events': 0,
                'high_priority_events': 0,
                'event_types': {},
                'confidence_distribution': {}
            }

        # Count by event type
        event_types = {}
        for event in events:
            event_type = event.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Count by confidence
        confidence_distribution = {
            'High': len([e for e in events if e.confidence_level == ConfidenceLevel.HIGH]),
            'Medium': len([e for e in events if e.confidence_level == ConfidenceLevel.MEDIUM]),
            'Low': len([e for e in events if e.confidence_level == ConfidenceLevel.LOW])
        }

        return {
            'total_events': len(events),
            'high_priority_events': len([e for e in events if e.is_high_priority()]),
            'event_types': event_types,
            'confidence_distribution': confidence_distribution,
            'average_relevance': sum(e.relevance_score for e in events) / len(events),
            'most_relevant_event': max(events, key=lambda e: e.relevance_score).description if events else None
        }