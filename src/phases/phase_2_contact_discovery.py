"""
Phase 2: Contact Discovery & Segmentation
Uses Apollo API to find and score contacts at target accounts
"""
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Account, Contact
from models.lead_scoring import LeadScoringEngine
from models.meddic_framework import MEDDICAnalyzer, ContactSource, ContactSourceAttribution
from data_sources.apollo_client import ApolloClient
from utils.rate_limiter import RateLimiter
from utils.data_classification import DataClassifier, DataSource, add_classification_to_dict

logger = logging.getLogger(__name__)


class ContactDiscoveryPhase:
    """Implements Phase 2: Contact Discovery & Segmentation"""

    def __init__(self, apollo_client: ApolloClient, scoring_config: Dict[str, Any]):
        self.apollo_client = apollo_client
        self.scoring_engine = LeadScoringEngine(scoring_config)
        self.meddic_analyzer = MEDDICAnalyzer()
        self.scoring_config = scoring_config

        # Rate limiter for Apollo API
        self.apollo_limiter = RateLimiter(delay=0.5)

    async def execute(self, account: Account, contact_limit: int = 50) -> Account:
        """Execute Phase 2 contact discovery for an account"""
        logger.info(f"Starting Phase 2 contact discovery for {account.name}")

        try:
            # Step 1: Get target titles for search
            target_titles = self.scoring_engine.get_target_titles()
            logger.info(f"Searching for {len(target_titles)} target title types")

            # Step 2: Search contacts via Apollo API
            logger.info("Searching contacts via Apollo API...")
            apollo_contacts = await self._search_apollo_contacts(
                account.domain, target_titles, contact_limit
            )

            if not apollo_contacts:
                logger.warning(f"No contacts found for {account.domain}")
                return account

            # Step 3: Convert to Contact objects with initial scoring
            logger.info("Converting to Contact objects and calculating initial scores...")
            contacts = await self._create_contact_objects(apollo_contacts, account)

            # Step 4: Segment into buying committee roles
            logger.info("Segmenting contacts into buying committee roles...")
            contacts = self._segment_buying_committee(contacts)

            # Step 5: Filter by score threshold for Phase 3
            logger.info("Filtering contacts for Phase 3 enrichment...")
            contacts = self._filter_contacts_for_phase_3(contacts)

            # Step 6: Add contacts to account
            for contact in contacts:
                account.add_contact(contact)

            logger.info(f"Phase 2 complete: Added {len(contacts)} contacts to {account.name}")
            return account

        except Exception as e:
            logger.error(f"Phase 2 failed for {account.name}: {e}")
            raise

    async def _search_apollo_contacts(self, domain: str, target_titles: List[str],
                                    limit: int) -> List[Dict[str, Any]]:
        """Search for contacts using Apollo API"""
        all_contacts = []

        async with self.apollo_limiter:
            try:
                contacts = await self.apollo_client.search_contacts(
                    domain=domain,
                    titles=target_titles,
                    limit=limit
                )
                all_contacts.extend(contacts)

            except Exception as e:
                logger.error(f"Apollo API error for {domain}: {e}")
                # Return empty list rather than failing completely
                return []

        # Remove duplicates based on email or LinkedIn URL
        seen = set()
        unique_contacts = []
        for contact in all_contacts:
            # Create unique identifier
            identifier = contact.get('email') or contact.get('linkedin_url') or contact.get('name')
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_contacts.append(contact)

        logger.info(f"Found {len(unique_contacts)} unique contacts for {domain}")
        return unique_contacts

    async def _create_contact_objects(self, apollo_contacts: List[Dict[str, Any]],
                                    account: Account) -> List[Contact]:
        """Convert Apollo API data to Contact objects with initial scoring"""
        contacts = []

        for apollo_data in apollo_contacts:
            try:
                # Create Contact object
                contact = Contact(
                    name=apollo_data.get('name', ''),
                    title=apollo_data.get('title', ''),
                    email=apollo_data.get('email'),
                    linkedin_url=apollo_data.get('linkedin_url')
                )

                # Set Apollo-specific data
                contact.apollo_contact_id = apollo_data.get('id')
                contact.apollo_bio = apollo_data.get('bio', '')

                # Determine role tenure from employment history
                employment_history = apollo_data.get('employment_history', [])
                current_role_tenure = self._calculate_role_tenure(employment_history)
                contact.role_tenure = current_role_tenure

                # Add source attribution
                contact.source_attribution = ContactSourceAttribution(
                    source_type=ContactSource.APOLLO_SEARCH,
                    source_url=f"https://app.apollo.io/contacts/{contact.apollo_contact_id}",
                    discovery_method=f"Apollo API search for target titles at {account.domain}",
                    confidence_level="High",
                    discovery_date=datetime.now().strftime("%Y-%m-%d"),
                    notes=f"Found via Apollo API contact search with {len(self.scoring_engine.get_target_titles())} target titles"
                )

                # MEDDIC analysis
                contact.meddic_profile = self.meddic_analyzer.analyze_contact_meddic(
                    contact.title,
                    contact.apollo_bio
                )

                # Calculate initial scores (Phase 2: ICP fit + buying power, no engagement yet)
                contact.calculate_icp_fit_score(self.scoring_config)
                contact.calculate_buying_power_score()
                # Engagement score remains 0 until Phase 3 LinkedIn analysis
                contact.engagement_potential_score = 0.0
                contact.calculate_final_lead_score(self.scoring_config)

                contacts.append(contact)

            except Exception as e:
                logger.error(f"Error creating contact from Apollo data: {e}")
                continue

        return contacts

    def _calculate_role_tenure(self, employment_history: List[Dict[str, Any]]) -> str:
        """Calculate tenure in current role from employment history"""
        if not employment_history:
            return "Unknown"

        # Find current role (usually first in list)
        current_role = employment_history[0] if employment_history else {}
        start_date = current_role.get('start_date')

        if not start_date:
            return "Unknown"

        try:
            # Parse start date (Apollo format varies)
            if isinstance(start_date, dict):
                year = start_date.get('year')
                month = start_date.get('month', 1)
            else:
                # Handle string dates
                year = int(str(start_date)[:4])
                month = 1

            if year:
                from datetime import date
                start = date(year, month, 1)
                today = date.today()

                # Calculate tenure
                years = today.year - start.year
                months = today.month - start.month

                if months < 0:
                    years -= 1
                    months += 12

                if years >= 1:
                    return f"{years} year{'s' if years != 1 else ''}"
                elif months >= 1:
                    return f"{months} month{'s' if months != 1 else ''}"
                else:
                    return "Less than 1 month"

        except Exception as e:
            logger.warning(f"Error calculating tenure: {e}")
            return "Unknown"

        return "Unknown"

    def _segment_buying_committee(self, contacts: List[Contact]) -> List[Contact]:
        """Segment contacts into buying committee roles"""
        logger.info("Segmenting contacts by buying committee roles...")

        # Contacts are already segmented via MEDDIC analysis in _create_contact_objects
        # Just log the distribution
        committee_counts = {}
        for contact in contacts:
            role = contact.buying_committee_role.value
            committee_counts[role] = committee_counts.get(role, 0) + 1

        logger.info(f"Buying committee distribution: {committee_counts}")
        return contacts

    def _filter_contacts_for_phase_3(self, contacts: List[Contact]) -> List[Contact]:
        """Filter contacts that meet threshold for Phase 3 enrichment"""
        threshold = self.scoring_config['scoring_thresholds']['high_priority']['min_score']

        # Since we don't have engagement scores yet in Phase 2, use a different threshold
        # Focus on ICP fit + buying power (engagement will be 0)
        phase_2_threshold = 40.0  # Lower threshold for Phase 2 since engagement is missing

        high_potential_contacts = []
        for contact in contacts:
            # Phase 2 scoring: Only ICP fit and buying power matter
            phase_2_score = (contact.icp_fit_score * 0.6) + (contact.buying_power_score * 0.4)

            if phase_2_score >= phase_2_threshold:
                high_potential_contacts.append(contact)

        logger.info(f"Filtered {len(high_potential_contacts)}/{len(contacts)} contacts for Phase 3 enrichment")
        return high_potential_contacts

    async def create_contact_summary(self, account: Account) -> Dict[str, Any]:
        """Create summary of Phase 2 contact discovery results"""
        contacts = account.contacts

        if not contacts:
            return {
                'total_contacts': 0,
                'phase_2_complete': False,
                'message': 'No contacts discovered'
            }

        # Calculate summary statistics
        total_contacts = len(contacts)
        avg_icp_score = sum(c.icp_fit_score for c in contacts) / total_contacts
        avg_buying_power = sum(c.buying_power_score for c in contacts) / total_contacts

        # Committee breakdown
        committee_breakdown = {}
        for contact in contacts:
            role = contact.buying_committee_role.value
            committee_breakdown[role] = committee_breakdown.get(role, 0) + 1

        # Score distribution
        high_icp = len([c for c in contacts if c.icp_fit_score >= 80])
        high_buying_power = len([c for c in contacts if c.buying_power_score >= 80])

        # MEDDIC role distribution
        meddic_breakdown = {}
        for contact in contacts:
            role = contact.meddic_profile.primary_role.value
            meddic_breakdown[role] = meddic_breakdown.get(role, 0) + 1

        return {
            'account_name': account.name,
            'total_contacts': total_contacts,
            'average_icp_score': round(avg_icp_score, 1),
            'average_buying_power': round(avg_buying_power, 1),
            'committee_breakdown': committee_breakdown,
            'meddic_breakdown': meddic_breakdown,
            'high_icp_contacts': high_icp,
            'high_buying_power_contacts': high_buying_power,
            'ready_for_phase_3': len([c for c in contacts if c.final_lead_score >= 40]),
            'phase_2_complete': True,
            'next_step': f'Phase 3: LinkedIn enrichment for high-scoring contacts'
        }

    def get_recommended_outreach_contacts(self, account: Account, limit: int = 5) -> List[Contact]:
        """Get top contacts recommended for immediate outreach"""
        # Sort by Phase 2 scoring (ICP fit + buying power)
        sorted_contacts = sorted(
            account.contacts,
            key=lambda c: (c.icp_fit_score * 0.6) + (c.buying_power_score * 0.4),
            reverse=True
        )

        return sorted_contacts[:limit]