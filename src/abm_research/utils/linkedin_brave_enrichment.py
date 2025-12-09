#!/usr/bin/env python3
"""
LinkedIn Enrichment via Brave Search (Decision #2)
Fetches public LinkedIn activity without requiring LinkedIn API access.
Uses Brave Search to discover posts, activity, and professional insights.
"""

import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class LinkedInActivity:
    """Public LinkedIn activity discovered via Brave Search"""

    person_name: str
    linkedin_url: Optional[str] = None

    # Discovered activity
    recent_posts: list[str] = field(default_factory=list)
    topics_of_interest: list[str] = field(default_factory=list)
    engagement_signals: list[str] = field(default_factory=list)
    professional_updates: list[str] = field(default_factory=list)

    # Metadata
    activity_score: int = 0  # 0-100 activity level
    last_active_indicator: Optional[str] = None  # "Very Active", "Active", "Moderate", "Low"
    enriched_at: Optional[datetime] = None
    enrichment_source: str = "brave_search"

    # Champion potential signals
    thought_leadership_score: int = 0  # Based on posts, articles
    network_influence_score: int = 0  # Based on engagement


class LinkedInBraveEnrichment:
    """
    Enrich contact LinkedIn data using Brave Search API
    Discovers public LinkedIn activity without paid LinkedIn API
    """

    def __init__(self):
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        if not self.brave_api_key:
            logger.warning("BRAVE_API_KEY not set - LinkedIn enrichment via Brave disabled")

        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 1.0

        # Topic keywords for champion scoring
        self.champion_topics = [
            "infrastructure",
            "data center",
            "power",
            "energy",
            "efficiency",
            "sustainability",
            "cloud",
            "AI",
            "ML",
            "gpu",
            "monitoring",
            "devops",
            "engineering",
            "architecture",
            "scale",
        ]

    def enrich_linkedin_activity(
        self,
        person_name: str,
        company_name: Optional[str] = None,
        title: Optional[str] = None,
        linkedin_url: Optional[str] = None,
    ) -> LinkedInActivity:
        """
        Enrich contact with LinkedIn activity discovered via Brave Search

        Args:
            person_name: Full name of the contact
            company_name: Current company for context
            title: Job title for context
            linkedin_url: Known LinkedIn URL (optional)

        Returns:
            LinkedInActivity with discovered information
        """
        logger.info(f"Enriching LinkedIn activity for: {person_name}")

        activity = LinkedInActivity(
            person_name=person_name, linkedin_url=linkedin_url, enriched_at=datetime.now()
        )

        if not self.brave_api_key:
            logger.warning("No Brave API key - returning empty activity")
            return activity

        # Strategy: Multiple targeted searches

        # 1. Find LinkedIn profile URL if not provided
        if not linkedin_url:
            linkedin_url = self._find_linkedin_profile(person_name, company_name, title)
            activity.linkedin_url = linkedin_url

        # 2. Search for LinkedIn posts by this person
        posts = self._search_linkedin_posts(person_name, company_name)
        activity.recent_posts = posts

        # 3. Discover topics and professional interests
        topics = self._discover_professional_topics(person_name, company_name, title)
        activity.topics_of_interest = topics

        # 4. Look for engagement signals (mentions, features, interviews)
        engagement = self._search_engagement_signals(person_name, company_name)
        activity.engagement_signals = engagement

        # 5. Find professional updates (promotions, conference talks, awards)
        updates = self._search_professional_updates(person_name, company_name, title)
        activity.professional_updates = updates

        # Calculate scores
        activity.activity_score = self._calculate_activity_score(activity)
        activity.last_active_indicator = self._determine_activity_level(activity)
        activity.thought_leadership_score = self._calculate_thought_leadership(activity)
        activity.network_influence_score = self._calculate_network_influence(activity)

        logger.info(
            f"LinkedIn enrichment complete: activity_score={activity.activity_score}, "
            f"thought_leadership={activity.thought_leadership_score}"
        )

        return activity

    def _find_linkedin_profile(
        self, person_name: str, company_name: Optional[str], title: Optional[str]
    ) -> Optional[str]:
        """Find LinkedIn profile URL via Brave Search"""
        try:
            self._apply_rate_limit()

            # Build targeted search query
            query_parts = [f'site:linkedin.com/in "{person_name}"']
            if company_name:
                query_parts.append(f'"{company_name}"')
            if title:
                query_parts.append(f'"{title}"')

            query = " ".join(query_parts)
            logger.debug(f"LinkedIn profile search: {query}")

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

            for result in web_results:
                url = result.get("url", "")
                # Match LinkedIn profile URLs
                if "linkedin.com/in/" in url:
                    logger.info(f"Found LinkedIn profile: {url}")
                    return url

            return None

        except Exception as e:
            logger.warning(f"Error finding LinkedIn profile: {e}")
            return None

    def _search_linkedin_posts(self, person_name: str, company_name: Optional[str]) -> list[str]:
        """Search for LinkedIn posts by this person"""
        posts = []

        try:
            self._apply_rate_limit()

            # Search for LinkedIn posts
            query = f'site:linkedin.com "{person_name}" (post OR article OR shared)'
            if company_name:
                query += f' "{company_name}"'

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 10},
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                return posts

            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            for result in web_results:
                title = result.get("title", "")
                description = result.get("description", "")
                url = result.get("url", "")

                # Skip if not LinkedIn content
                if "linkedin.com" not in url:
                    continue

                # Extract post summary
                if description and len(description) > 20:
                    post_summary = self._clean_post_text(description)
                    if post_summary:
                        posts.append(post_summary[:200])

            logger.info(f"Found {len(posts)} LinkedIn posts")
            return posts[:5]  # Return top 5 posts

        except Exception as e:
            logger.warning(f"Error searching LinkedIn posts: {e}")
            return posts

    def _discover_professional_topics(
        self, person_name: str, company_name: Optional[str], title: Optional[str]
    ) -> list[str]:
        """Discover professional topics this person writes/speaks about"""
        topics = []

        try:
            self._apply_rate_limit()

            # Search for their writing/speaking topics
            query = f'"{person_name}" (article OR keynote OR talk OR webinar OR podcast)'
            if company_name:
                query += f' "{company_name}"'

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 10},
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                return topics

            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            # Extract topics from search results
            topic_candidates = {}
            for result in web_results:
                text = f"{result.get('title', '')} {result.get('description', '')}".lower()

                for topic in self.champion_topics:
                    if topic in text:
                        topic_candidates[topic] = topic_candidates.get(topic, 0) + 1

            # Return most mentioned topics
            sorted_topics = sorted(topic_candidates.items(), key=lambda x: x[1], reverse=True)
            topics = [topic for topic, count in sorted_topics[:5]]

            logger.info(f"Discovered topics: {topics}")
            return topics

        except Exception as e:
            logger.warning(f"Error discovering topics: {e}")
            return topics

    def _search_engagement_signals(
        self, person_name: str, company_name: Optional[str]
    ) -> list[str]:
        """Search for engagement signals (mentions, features, interviews)"""
        signals = []

        try:
            self._apply_rate_limit()

            # Search for mentions, interviews, features
            query = f'"{person_name}" (interview OR featured OR speaker OR panelist OR quoted)'
            if company_name:
                query += f' "{company_name}"'

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 10, "freshness": "pm"},  # Past month
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                return signals

            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            for result in web_results:
                title = result.get("title", "")
                url = result.get("url", "")

                # Skip LinkedIn URLs for this search
                if "linkedin.com" in url:
                    continue

                if title:
                    signal = f"{title[:100]}"
                    signals.append(signal)

            logger.info(f"Found {len(signals)} engagement signals")
            return signals[:5]

        except Exception as e:
            logger.warning(f"Error searching engagement signals: {e}")
            return signals

    def _search_professional_updates(
        self, person_name: str, company_name: Optional[str], title: Optional[str]
    ) -> list[str]:
        """Search for professional updates (promotions, awards, speaking)"""
        updates = []

        try:
            self._apply_rate_limit()

            # Search for professional updates
            query = f'"{person_name}" (promoted OR joined OR appointed OR award OR recognized)'
            if company_name:
                query += f' "{company_name}"'

            response = requests.get(
                self.brave_base_url,
                params={"q": query, "count": 10, "freshness": "py"},  # Past year
                headers={"X-Subscription-Token": self.brave_api_key, "Accept": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                return updates

            data = response.json()
            web_results = data.get("web", {}).get("results", [])

            for result in web_results:
                description = result.get("description", "")

                if description and person_name.lower().split()[0] in description.lower():
                    update = self._clean_post_text(description)[:150]
                    if update:
                        updates.append(update)

            logger.info(f"Found {len(updates)} professional updates")
            return updates[:3]

        except Exception as e:
            logger.warning(f"Error searching professional updates: {e}")
            return updates

    def _clean_post_text(self, text: str) -> str:
        """Clean up post/description text"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Remove common LinkedIn boilerplate
        text = re.sub(r"(View|See|Read) (more|full).*?(?=\.|$)", "", text, flags=re.I)
        return text.strip()

    def _calculate_activity_score(self, activity: LinkedInActivity) -> int:
        """Calculate overall activity score (0-100)"""
        score = 0

        # Posts contribute up to 30 points
        post_count = len(activity.recent_posts)
        score += min(30, post_count * 10)

        # Topics contribute up to 20 points
        topic_count = len(activity.topics_of_interest)
        score += min(20, topic_count * 5)

        # Engagement signals contribute up to 25 points
        engagement_count = len(activity.engagement_signals)
        score += min(25, engagement_count * 8)

        # Professional updates contribute up to 25 points
        update_count = len(activity.professional_updates)
        score += min(25, update_count * 10)

        return min(100, score)

    def _determine_activity_level(self, activity: LinkedInActivity) -> str:
        """Determine activity level description"""
        score = activity.activity_score

        if score >= 80:
            return "Very Active"
        elif score >= 60:
            return "Active"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low"

    def _calculate_thought_leadership(self, activity: LinkedInActivity) -> int:
        """Calculate thought leadership score based on posts/articles"""
        score = 0

        # Posts show thought leadership
        score += len(activity.recent_posts) * 15

        # Topics aligned with our ICP boost the score
        icp_topics = {"infrastructure", "data center", "power", "energy", "gpu", "AI", "cloud"}
        aligned_topics = [
            t for t in activity.topics_of_interest if any(icp in t for icp in icp_topics)
        ]
        score += len(aligned_topics) * 10

        # Speaking engagements are strong signals
        speaking_keywords = ["speaker", "keynote", "panelist", "webinar"]
        for signal in activity.engagement_signals:
            if any(kw in signal.lower() for kw in speaking_keywords):
                score += 15

        return min(100, score)

    def _calculate_network_influence(self, activity: LinkedInActivity) -> int:
        """Calculate network influence score based on engagement"""
        score = 0

        # Engagement signals indicate network influence
        score += len(activity.engagement_signals) * 12

        # Being featured/interviewed shows influence
        feature_keywords = ["featured", "interview", "quoted"]
        for signal in activity.engagement_signals:
            if any(kw in signal.lower() for kw in feature_keywords):
                score += 10

        # Professional updates (promotions, awards) indicate influence
        score += len(activity.professional_updates) * 8

        return min(100, score)

    def _apply_rate_limit(self):
        """Apply rate limiting between API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()


# Export singleton instance
linkedin_brave_enrichment = LinkedInBraveEnrichment()
