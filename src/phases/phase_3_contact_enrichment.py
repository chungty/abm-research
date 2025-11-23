"""
Phase 3: High-Priority Contact Enrichment
LinkedIn analysis and engagement scoring for contacts that passed Phase 2 filtering
"""
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Account, Contact
from models.contact import ResearchStatus
from data_sources.linkedin_scraper import LinkedInScraper
from utils.rate_limiter import RateLimiter
from utils.data_classification import DataClassifier, add_classification_to_dict

logger = logging.getLogger(__name__)


class ContactEnrichmentPhase:
    """Implements Phase 3: High-Priority Contact Enrichment"""

    def __init__(self, linkedin_scraper: LinkedInScraper, scoring_config: Dict[str, Any]):
        self.linkedin_scraper = linkedin_scraper
        self.scoring_config = scoring_config

        # Rate limiter for LinkedIn (2s between requests to avoid detection)
        self.linkedin_limiter = RateLimiter(delay=2.0)

    async def execute(self, account: Account, score_threshold: float = 40.0) -> Account:
        """Execute Phase 3 LinkedIn enrichment for high-scoring contacts"""
        logger.info(f"Starting Phase 3 LinkedIn enrichment for {account.name}")

        # Filter contacts that meet threshold from Phase 2
        eligible_contacts = [
            c for c in account.contacts
            if self._calculate_phase_2_score(c) >= score_threshold and c.linkedin_url
        ]

        logger.info(f"Found {len(eligible_contacts)} contacts eligible for LinkedIn enrichment")

        if not eligible_contacts:
            logger.warning("No contacts meet Phase 3 threshold or have LinkedIn URLs")
            return account

        try:
            # Enrich each eligible contact
            for contact in eligible_contacts:
                logger.info(f"Enriching contact: {contact.name}")
                await self._enrich_contact(contact)

                # Update research status
                contact.research_status = ResearchStatus.ENRICHED

            logger.info(f"Phase 3 complete: Enriched {len(eligible_contacts)} contacts")
            return account

        except Exception as e:
            logger.error(f"Phase 3 failed for {account.name}: {e}")
            raise

    def _calculate_phase_2_score(self, contact: Contact) -> float:
        """Calculate Phase 2 score (ICP + Buying Power)"""
        return (contact.icp_fit_score * 0.6) + (contact.buying_power_score * 0.4)

    async def _enrich_contact(self, contact: Contact):
        """Enrich individual contact with LinkedIn data"""
        if not contact.linkedin_url:
            logger.warning(f"No LinkedIn URL for {contact.name}")
            return

        try:
            async with self.linkedin_limiter:
                # Get LinkedIn profile data
                profile_data = await self.linkedin_scraper.get_profile_data(contact.linkedin_url)

                if profile_data:
                    # Analyze LinkedIn activity
                    activity_data = await self.linkedin_scraper.analyze_activity(
                        contact.linkedin_url,
                        days=90
                    )

                    # Update contact with LinkedIn insights
                    await self._update_contact_with_linkedin_data(contact, profile_data, activity_data)

                else:
                    logger.warning(f"Could not retrieve LinkedIn data for {contact.name}")
                    # Use fallback scoring for contacts without LinkedIn access
                    self._apply_fallback_engagement_scoring(contact)

        except Exception as e:
            logger.error(f"Error enriching {contact.name}: {e}")
            # Apply fallback scoring
            self._apply_fallback_engagement_scoring(contact)

    async def _update_contact_with_linkedin_data(self, contact: Contact,
                                               profile_data: Dict[str, Any],
                                               activity_data: Dict[str, Any]):
        """Update contact with LinkedIn enrichment data"""

        # Update LinkedIn activity level
        contact.linkedin_activity_level = activity_data.get('activity_level', 'inactive')

        # Update content themes from activity analysis
        contact.linkedin_content_themes = activity_data.get('content_themes', [])

        # Update network quality indicator
        contact.linkedin_network_quality = activity_data.get('network_quality', False)

        # Calculate engagement potential score
        contact.calculate_engagement_potential_score()

        # Recalculate final lead score with all components
        contact.calculate_final_lead_score(self.scoring_config)

        # Update research status
        contact.research_status = ResearchStatus.ENRICHED

    def _apply_fallback_engagement_scoring(self, contact: Contact):
        """Apply fallback engagement scoring when LinkedIn data unavailable"""

        # Use heuristics based on role and title for engagement scoring
        title_lower = contact.title.lower()

        # Estimate activity level based on role seniority
        if any(term in title_lower for term in ['vp', 'vice president', 'head', 'chief']):
            contact.linkedin_activity_level = 'monthly'  # Executives typically post monthly
        elif 'director' in title_lower:
            contact.linkedin_activity_level = 'quarterly'  # Directors post less frequently
        else:
            contact.linkedin_activity_level = 'inactive'  # Assume inactive for lower levels

        # Assign generic content themes based on role
        if any(term in title_lower for term in ['operations', 'infrastructure']):
            contact.linkedin_content_themes = ['infrastructure', 'operations']
        elif any(term in title_lower for term in ['sustainability', 'esg']):
            contact.linkedin_content_themes = ['sustainability', 'energy efficiency']
        elif 'engineering' in title_lower:
            contact.linkedin_content_themes = ['technology', 'engineering']
        else:
            contact.linkedin_content_themes = []

        # Network quality: assume good for senior roles
        contact.linkedin_network_quality = any(term in title_lower for term in [
            'vp', 'vice president', 'director', 'head', 'chief'
        ])

        # Calculate engagement score with fallback data
        contact.calculate_engagement_potential_score()
        contact.calculate_final_lead_score(self.scoring_config)

        logger.info(f"Applied fallback engagement scoring for {contact.name}")

    async def create_enrichment_summary(self, account: Account) -> Dict[str, Any]:
        """Create summary of Phase 3 enrichment results"""
        enriched_contacts = [c for c in account.contacts if c.research_status == ResearchStatus.ENRICHED]

        if not enriched_contacts:
            return {
                'total_enriched': 0,
                'phase_3_complete': False,
                'message': 'No contacts enriched in Phase 3'
            }

        # Calculate summary statistics
        total_enriched = len(enriched_contacts)
        avg_final_score = sum(c.final_lead_score for c in enriched_contacts) / total_enriched
        avg_engagement = sum(c.engagement_potential_score for c in enriched_contacts) / total_enriched

        # Activity level distribution
        activity_breakdown = {}
        for contact in enriched_contacts:
            level = contact.linkedin_activity_level
            activity_breakdown[level] = activity_breakdown.get(level, 0) + 1

        # High-priority contacts (70+ final score)
        high_priority = [c for c in enriched_contacts if c.final_lead_score >= 70]

        # Content theme analysis
        all_themes = []
        for contact in enriched_contacts:
            all_themes.extend(contact.linkedin_content_themes)

        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        # Top themes
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'account_name': account.name,
            'total_enriched': total_enriched,
            'average_final_score': round(avg_final_score, 1),
            'average_engagement_score': round(avg_engagement, 1),
            'activity_breakdown': activity_breakdown,
            'high_priority_contacts': len(high_priority),
            'top_content_themes': dict(top_themes),
            'linkedin_accessible_contacts': len([c for c in enriched_contacts if c.linkedin_url]),
            'phase_3_complete': True,
            'next_step': 'Phase 4: Engagement Intelligence and connection pathways'
        }

    def get_final_contact_recommendations(self, account: Account, limit: int = 5) -> List[Contact]:
        """Get final contact recommendations after Phase 3 enrichment"""

        # Sort by final lead score (all components included)
        enriched_contacts = [c for c in account.contacts if c.research_status == ResearchStatus.ENRICHED]
        sorted_contacts = sorted(enriched_contacts, key=lambda c: c.final_lead_score, reverse=True)

        return sorted_contacts[:limit]

    def analyze_engagement_patterns(self, account: Account) -> Dict[str, Any]:
        """Analyze LinkedIn engagement patterns across contacts"""
        enriched_contacts = [c for c in account.contacts if c.research_status == ResearchStatus.ENRICHED]

        if not enriched_contacts:
            return {'message': 'No enriched contacts to analyze'}

        # Analyze activity patterns
        high_activity = len([c for c in enriched_contacts if c.linkedin_activity_level in ['weekly+', 'monthly']])
        low_activity = len([c for c in enriched_contacts if c.linkedin_activity_level in ['quarterly', 'inactive']])

        # Network quality analysis
        quality_networks = len([c for c in enriched_contacts if c.linkedin_network_quality])

        # Content theme popularity
        theme_analysis = {}
        verdigris_relevant_themes = [
            'power', 'energy', 'ai infrastructure', 'capacity planning',
            'uptime', 'reliability', 'sustainability', 'data center'
        ]

        contacts_with_relevant_themes = 0
        for contact in enriched_contacts:
            has_relevant_theme = any(
                any(theme_word in content_theme.lower() for theme_word in verdigris_relevant_themes)
                for content_theme in contact.linkedin_content_themes
            )
            if has_relevant_theme:
                contacts_with_relevant_themes += 1

        return {
            'total_contacts_analyzed': len(enriched_contacts),
            'high_activity_contacts': high_activity,
            'low_activity_contacts': low_activity,
            'quality_network_contacts': quality_networks,
            'contacts_with_relevant_themes': contacts_with_relevant_themes,
            'engagement_opportunity_score': round(
                (high_activity + quality_networks + contacts_with_relevant_themes) / len(enriched_contacts) * 100, 1
            ),
            'recommendation': self._get_engagement_recommendation(high_activity, quality_networks, contacts_with_relevant_themes, len(enriched_contacts))
        }

    def _get_engagement_recommendation(self, high_activity: int, quality_networks: int, relevant_themes: int, total: int) -> str:
        """Generate engagement recommendation based on LinkedIn analysis"""
        engagement_score = (high_activity + quality_networks + relevant_themes) / total

        if engagement_score >= 0.6:
            return "🔥 HIGH: Strong LinkedIn engagement potential - prioritize social selling approach"
        elif engagement_score >= 0.4:
            return "📋 MEDIUM: Moderate engagement potential - mix of direct outreach and LinkedIn"
        else:
            return "📝 LOW: Limited LinkedIn activity - focus on direct email and phone outreach"