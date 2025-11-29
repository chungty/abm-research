#!/usr/bin/env python3
"""
ABM Research System - Production Ready
Implements complete 5-phase ABM research workflow
Updated to use consolidated Notion client

Consolidated from: comprehensive_abm_system.py
Updated imports: notion_client.py (replacing notion_persistence_manager.py)
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Import all phase engines from package structure
try:
    from ..phases.enhanced_trigger_event_detector import enhanced_trigger_detector
    TRIGGER_DETECTOR_AVAILABLE = True
except ImportError:
    TRIGGER_DETECTOR_AVAILABLE = False
    logging.warning("Enhanced trigger detector not available")

try:
    from ..phases.linkedin_enrichment_engine import linkedin_enrichment_engine
    LINKEDIN_ENRICHMENT_AVAILABLE = True
except ImportError:
    LINKEDIN_ENRICHMENT_AVAILABLE = False
    logging.warning("LinkedIn enrichment engine not available")

try:
    from ..phases.enhanced_engagement_intelligence import enhanced_engagement_intelligence
    ENGAGEMENT_INTELLIGENCE_AVAILABLE = True
except ImportError:
    ENGAGEMENT_INTELLIGENCE_AVAILABLE = False
    logging.warning("Enhanced engagement intelligence not available")

try:
    from ..phases.strategic_partnership_intelligence import strategic_partnership_intelligence
    PARTNERSHIP_INTELLIGENCE_AVAILABLE = True
except ImportError:
    PARTNERSHIP_INTELLIGENCE_AVAILABLE = False
    logging.warning("Strategic partnership intelligence not available")

try:
    from ..utils.account_intelligence_engine import account_intelligence_engine
    from ..utils.data_conflict_resolver import data_conflict_resolver
    from ..utils.partnership_classifier import partnership_classifier
    ENHANCED_INTELLIGENCE_AVAILABLE = True
except ImportError:
    ENHANCED_INTELLIGENCE_AVAILABLE = False
    logging.warning("Enhanced intelligence components not available")

try:
    from ..phases.apollo_contact_discovery import apollo_discovery
    APOLLO_DISCOVERY_AVAILABLE = True
except ImportError:
    APOLLO_DISCOVERY_AVAILABLE = False
    logging.warning("Apollo contact discovery not available")

try:
    from .unified_lead_scorer import unified_lead_scorer
    UNIFIED_SCORER_AVAILABLE = True
except ImportError:
    UNIFIED_SCORER_AVAILABLE = False
    logging.warning("Unified lead scorer not available")

# Import consolidated Notion client from integrations
try:
    from ..integrations.notion_client import NotionClient
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    logging.warning("Consolidated Notion client not available")

# Import company enrichment service
try:
    from ..utils.company_enrichment_service import company_enrichment_service
    COMPANY_ENRICHMENT_AVAILABLE = True
except ImportError:
    COMPANY_ENRICHMENT_AVAILABLE = False
    logging.warning("Company enrichment service not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveABMSystem:
    """
    Production-ready ABM research system implementing all 5 phases

    Updated to use consolidated components:
    - notion_client.py for data persistence (replaces notion_persistence_manager.py)
    - Graceful fallback for missing components
    - Comprehensive error handling and logging
    """

    def __init__(self):
        logger.info("🚀 Initializing ABM Research System")
        logger.info("📋 Production-ready 5-phase workflow with consolidated components")

        # Initialize intelligence engines with fallback
        self.trigger_detector = enhanced_trigger_detector if TRIGGER_DETECTOR_AVAILABLE else None
        self.linkedin_enrichment = linkedin_enrichment_engine if LINKEDIN_ENRICHMENT_AVAILABLE else None
        self.engagement_intelligence = enhanced_engagement_intelligence if ENGAGEMENT_INTELLIGENCE_AVAILABLE else None
        self.partnership_intelligence = strategic_partnership_intelligence if PARTNERSHIP_INTELLIGENCE_AVAILABLE else None
        self.apollo_discovery = apollo_discovery if APOLLO_DISCOVERY_AVAILABLE else None
        self.scoring_engine = unified_lead_scorer if UNIFIED_SCORER_AVAILABLE else None

        # Enhanced intelligence components
        self.account_intelligence = account_intelligence_engine if ENHANCED_INTELLIGENCE_AVAILABLE else None
        self.conflict_resolver = data_conflict_resolver if ENHANCED_INTELLIGENCE_AVAILABLE else None
        self.partnership_classifier = partnership_classifier if ENHANCED_INTELLIGENCE_AVAILABLE else None

        # Initialize consolidated Notion client (UPDATED)
        self.notion_client = None
        if NOTION_CLIENT_AVAILABLE:
            try:
                self.notion_client = NotionClient()
                logger.info("✅ Consolidated Notion client initialized")
            except Exception as e:
                logger.warning(f"⚠️  Notion client initialization failed: {e}")

        # Log component availability
        self._log_component_status()

    def _log_component_status(self):
        """Log the status of all ABM system components"""
        components = {
            'Trigger Detection': TRIGGER_DETECTOR_AVAILABLE,
            'Contact Discovery': APOLLO_DISCOVERY_AVAILABLE,
            'LinkedIn Enrichment': LINKEDIN_ENRICHMENT_AVAILABLE,
            'Engagement Intelligence': ENGAGEMENT_INTELLIGENCE_AVAILABLE,
            'Partnership Intelligence': PARTNERSHIP_INTELLIGENCE_AVAILABLE,
            'Lead Scoring': UNIFIED_SCORER_AVAILABLE,
            'Notion Persistence': bool(self.notion_client)
        }

        logger.info("🔧 ABM System Component Status:")
        for component, available in components.items():
            status = "✅ Available" if available else "❌ Not Available"
            logger.info(f"  {component}: {status}")

    def conduct_complete_account_research(self, company_name: str, company_domain: str) -> Dict:
        """
        Complete 5-phase ABM research per specification

        Args:
            company_name: Target company name
            company_domain: Company domain for research

        Returns:
            Comprehensive account intelligence dictionary
        """
        logger.info(f"\n🎯 Starting ABM research for {company_name}")
        logger.info("=" * 60)

        research_results = {
            'account': {},
            'contacts': [],
            'events': [],
            'partnerships': [],
            'research_summary': {},
            'component_status': {},
            'success': False
        }

        start_time = datetime.now()

        try:
            # PHASE 1: Account Intelligence Baseline
            logger.info("\n📊 PHASE 1: Account Intelligence Baseline")
            account_data, trigger_events = self._phase_1_account_intelligence(
                company_name, company_domain
            )
            research_results['account'] = account_data
            research_results['events'] = trigger_events

            # PHASE 2: Contact Discovery & Segmentation
            logger.info("\n👥 PHASE 2: Contact Discovery & Segmentation")
            discovered_contacts = self._phase_2_contact_discovery(
                company_name, company_domain, account_data
            )
            research_results['contacts'] = discovered_contacts

            # PHASE 3: High-Priority Contact Enrichment
            logger.info("\n🔍 PHASE 3: High-Priority Contact Enrichment")
            enriched_contacts = self._phase_3_contact_enrichment(
                discovered_contacts
            )
            research_results['contacts'] = enriched_contacts

            # PHASE 4: Engagement Intelligence
            logger.info("\n🧠 PHASE 4: Engagement Intelligence")
            intelligence_enhanced_contacts = self._phase_4_engagement_intelligence(
                enriched_contacts, trigger_events, account_data
            )
            research_results['contacts'] = intelligence_enhanced_contacts

            # PHASE 5: Strategic Partnership Intelligence
            logger.info("\n🤝 PHASE 5: Strategic Partnership Intelligence")
            partnership_data = self._phase_5_partnership_intelligence(
                company_name, company_domain
            )

            # FIXED: Integrate account classification into account data
            if partnership_data.get('account_classification'):
                account_classification = partnership_data['account_classification']
                # Add partnership fields to account data
                research_results['account']['partnership_classification'] = account_classification.get('partnership_classification', 'unknown')
                research_results['account']['classification_confidence'] = account_classification.get('classification_confidence', 0.0)
                research_results['account']['classification_reasoning'] = account_classification.get('classification_reasoning', '')
                research_results['account']['recommended_approach'] = account_classification.get('recommended_approach', '')
                research_results['account']['potential_value'] = account_classification.get('potential_value', '')
                research_results['account']['next_actions'] = account_classification.get('next_actions', [])
                research_results['account']['classification_date'] = account_classification.get('classification_date', '')

                logger.info(f"✅ Account classification integrated: {research_results['account']['partnership_classification']} ({research_results['account']['classification_confidence']:.1f}%)")

            # Store only strategic partnerships list, not account classification
            research_results['partnerships'] = partnership_data.get('strategic_partnerships', [])

            # Generate comprehensive research summary
            research_results['research_summary'] = self._generate_research_summary(
                research_results, start_time
            )

            # STEP 6: Persist research data to Notion (UPDATED)
            logger.info("\n💾 STEP 6: Persisting Research to Notion")
            if self.notion_client:
                try:
                    persistence_results = self._save_complete_research_to_notion(research_results)
                    research_results['notion_persistence'] = persistence_results
                    logger.info(f"✅ Notion persistence complete:")
                    logger.info(f"   📋 Contacts saved: {persistence_results.get('contacts_saved', 0)}")
                    logger.info(f"   🎯 Events saved: {persistence_results.get('events_saved', 0)}")
                    logger.info(f"   🏢 Account saved: {persistence_results.get('account_saved', False)}")
                except Exception as e:
                    logger.error(f"⚠️  Notion persistence failed: {e}")
                    research_results['notion_persistence'] = {'error': str(e)}
            else:
                logger.warning("⚠️  Notion client not available, skipping persistence")
                research_results['notion_persistence'] = {'skipped': 'Notion client not available'}

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n✅ ABM research completed in {duration:.1f} seconds")
            research_results['success'] = True
            return research_results

        except Exception as e:
            logger.error(f"❌ Error in ABM research: {e}")
            research_results['research_summary'] = {
                'status': 'failed',
                'error': str(e),
                'research_duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            return research_results

    def _phase_1_account_intelligence(self, company_name: str, company_domain: str) -> tuple:
        """Phase 1: Account Intelligence Baseline"""
        if self.trigger_detector:
            logger.info("🔍 Detecting trigger events with real source URLs...")
            trigger_events = self.trigger_detector.detect_trigger_events(
                company_name, company_domain, lookback_days=90
            )

            formatted_events = []
            for event in trigger_events:
                formatted_events.append({
                    'id': f"event_{len(formatted_events) + 1}",
                    'description': event.description,
                    'event_type': event.event_type,
                    'confidence': event.confidence,
                    'confidence_score': event.confidence_score,
                    'relevance_score': event.relevance_score,
                    'source_url': event.source_url,
                    'source_type': event.source_type,
                    'detected_date': event.detected_date,
                    'occurred_date': event.occurred_date,
                    'urgency_level': event.urgency_level
                })

            logger.info(f"✅ Found {len(formatted_events)} trigger events")
        else:
            logger.warning("⚠️  Trigger detector not available, using mock data")
            formatted_events = [{
                'id': 'mock_event_1',
                'description': f'{company_name} expansion activities detected',
                'event_type': 'expansion',
                'confidence': 'Medium',
                'confidence_score': 75,
                'relevance_score': 80,
                'source_url': f'https://example.com/{company_name.lower().replace(" ", "-")}',
                'source_type': 'Mock Data',
                'detected_date': datetime.now().strftime('%Y-%m-%d'),
                'occurred_date': datetime.now().strftime('%Y-%m-%d'),
                'urgency_level': 'Medium'
            }]

        # Calculate ICP fit score with breakdown
        icp_fit_score, icp_breakdown = self._calculate_enhanced_icp_fit(formatted_events)

        # Use API-based company enrichment instead of hardcoded data
        enriched_company = self._enrich_company_data(company_name, company_domain)

        # Enhanced Account Intelligence (Phase 1A Enhancement)
        enhanced_intelligence = {}
        if self.account_intelligence:
            logger.info("🧠 Gathering enhanced account intelligence...")
            try:
                account_intel = self.account_intelligence.gather_account_intelligence(
                    company_name, company_domain, enriched_company
                )
                enhanced_intelligence = self.account_intelligence.convert_to_notion_format(account_intel)
                logger.info(f"✅ Enhanced intelligence: {account_intel.confidence_score:.1f} confidence, "
                          f"{len(account_intel.data_sources)} sources")
            except Exception as e:
                logger.warning(f"Enhanced intelligence failed: {e}")

        account_data = {
            'name': company_name,
            'domain': company_domain,
            'employee_count': enriched_company.get('employee_count', 0),
            'icp_fit_score': icp_fit_score,
            'industry': enriched_company.get('industry', 'Technology'),
            'business_model': enriched_company.get('business_model', 'Technology Company'),
            # Apollo fields from API enrichment
            'apollo_account_id': enriched_company.get('apollo_account_id', ''),
            'apollo_organization_id': enriched_company.get('apollo_organization_id', ''),
            # Add ICP breakdown components
            **icp_breakdown,
            # Enhanced intelligence fields
            **enhanced_intelligence
        }

        # Store account data for Phase 5 partnership classification
        self._current_account_data = account_data

        logger.info(f"✅ Account ICP fit score: {icp_fit_score}")
        return account_data, formatted_events

    def _phase_2_contact_discovery(self, company_name: str, company_domain: str, account_data: Dict) -> List[Dict]:
        """Phase 2: Contact Discovery & Segmentation"""
        if self.apollo_discovery:
            logger.info("🔍 Discovering contacts via Apollo API...")
            try:
                raw_contacts = self.apollo_discovery.discover_contacts(company_name, company_domain)
                contacts = self.apollo_discovery.convert_to_notion_format(raw_contacts, company_name)

                enhanced_contacts = []
                for contact in contacts:
                    if self.scoring_engine:
                        score = self.scoring_engine.calculate_lead_score(contact, account_data)
                        contact['lead_score'] = score  # Use field name expected by Notion client
                        contact['initial_lead_score'] = score  # Keep for backward compatibility
                    else:
                        contact['lead_score'] = 50  # Default score
                        contact['initial_lead_score'] = 50  # Default score

                    enhanced_contacts.append(contact)

                logger.info(f"✅ Discovered {len(enhanced_contacts)} contacts")
                return enhanced_contacts

            except Exception as e:
                logger.error(f"⚠️  Apollo discovery failed: {e}")
        else:
            logger.warning("⚠️  Apollo discovery not available")

        # Mock fallback
        logger.info("📝 Using mock contact data")
        return [{
            'name': f'Contact Manager at {company_name}',
            'title': 'Senior Manager',
            'email': f'manager@{company_domain}',
            'company': company_name,
            'initial_lead_score': 60
        }]

    def _phase_3_contact_enrichment(self, contacts: List[Dict]) -> List[Dict]:
        """Phase 3: High-Priority Contact Enrichment"""
        if not self.linkedin_enrichment:
            logger.warning("⚠️  LinkedIn enrichment not available, skipping enrichment")
            return contacts

        # Check for both field names (lead_score from Apollo, initial_lead_score for backward compatibility)
        def get_lead_score(contact):
            return max(contact.get('lead_score', 0), contact.get('initial_lead_score', 0))

        high_priority_contacts = [c for c in contacts if get_lead_score(c) >= 60]
        logger.info(f"🔍 Enriching {len(high_priority_contacts)} high-priority contacts...")

        enriched_contacts = []
        for contact in contacts:
            if get_lead_score(contact) >= 60:
                try:
                    # Get LinkedIn enrichment data
                    enriched_data = self.linkedin_enrichment.enrich_contact(contact)

                    # Phase 1B Enhancement: Intelligent conflict resolution
                    if self.conflict_resolver:
                        logger.debug(f"🔍 Resolving data conflicts for {contact.get('name', 'unknown')}")

                        # Separate Apollo (original) and LinkedIn (enriched) data
                        apollo_data = {k: v for k, v in contact.items()
                                     if k not in enriched_data or not isinstance(enriched_data, dict) or k not in enriched_data}

                        # Convert enriched_data to dict if it's not already
                        if hasattr(enriched_data, '__dict__'):
                            from dataclasses import asdict
                            linkedin_dict = asdict(enriched_data)
                        elif isinstance(enriched_data, dict):
                            linkedin_dict = enriched_data
                        else:
                            linkedin_dict = {}

                        merge_result = self.conflict_resolver.resolve_contact_conflicts(
                            apollo_data, linkedin_dict
                        )

                        # Use intelligently merged contact data
                        contact.update(merge_result.merged_contact)
                        contact['enrichment_status'] = 'enriched'
                        contact['data_conflicts_resolved'] = len(merge_result.conflicts_detected)

                        # Log conflicts for monitoring
                        if merge_result.conflicts_detected:
                            self.conflict_resolver.log_conflicts_summary(merge_result)

                    else:
                        # Fallback: Simple merge (original behavior)
                        contact.update(enriched_data)
                        contact['enrichment_status'] = 'enriched'

                except Exception as e:
                    logger.warning(f"Enrichment failed for {contact.get('name', 'unknown')}: {e}")
                    contact['enrichment_status'] = 'failed'
            else:
                contact['enrichment_status'] = 'skipped_low_score'

            enriched_contacts.append(contact)

        enriched_count = sum(1 for c in enriched_contacts if c.get('enrichment_status') == 'enriched')
        logger.info(f"✅ Enriched {enriched_count}/{len(high_priority_contacts)} contacts")
        return enriched_contacts

    def _phase_4_engagement_intelligence(self, contacts: List[Dict], events: List[Dict], account_data: Dict) -> List[Dict]:
        """Phase 4: Engagement Intelligence"""
        if not self.engagement_intelligence:
            logger.warning("⚠️  Engagement intelligence not available, skipping analysis")
            return contacts

        logger.info("🧠 Generating engagement intelligence...")

        intelligence_contacts = []
        for contact in contacts:
            try:
                intelligence_data = self.engagement_intelligence.generate_engagement_intelligence(
                    contact, events, account_data
                )
                # Convert dataclass to dictionary for contact update
                from dataclasses import asdict
                intelligence_dict = asdict(intelligence_data)
                contact.update(intelligence_dict)
                contact['intelligence_status'] = 'generated'
            except Exception as e:
                logger.warning(f"Intelligence generation failed for {contact.get('name', 'unknown')}: {e}")
                contact['intelligence_status'] = 'failed'

            intelligence_contacts.append(contact)

        intelligence_count = sum(1 for c in intelligence_contacts if c.get('intelligence_status') == 'generated')
        logger.info(f"✅ Generated intelligence for {intelligence_count}/{len(contacts)} contacts")
        return intelligence_contacts

    def _phase_5_partnership_intelligence(self, company_name: str, company_domain: str) -> Dict[str, any]:
        """Phase 5: Partnership Classification & Strategic Partnership Detection"""
        logger.info("🤝 Analyzing strategic partnership classification...")

        partnership_data = {
            'account_classification': None,
            'strategic_partnerships': []
        }

        # PART A: Classify the account itself (Strategic Partner, Direct ICP, etc.)
        if self.partnership_classifier:
            try:
                # Use account intelligence to build company profile for classification
                company_data = {
                    'name': company_name,
                    'domain': company_domain,
                    'business_model': '',
                    'physical_infrastructure': '',
                    'tech_stack': '',
                    'recent_announcements': '',
                    'employee_count': 0,
                    'growth_stage': ''
                }

                # Enhance with available account intelligence data if present
                if hasattr(self, '_current_account_data') and self._current_account_data:
                    account_data = self._current_account_data
                    company_data.update({
                        'business_model': account_data.get('business_model', ''),
                        'physical_infrastructure': account_data.get('Physical Infrastructure', ''),
                        'tech_stack': account_data.get('Physical Infrastructure', ''),
                        'recent_announcements': account_data.get('Recent Announcements', ''),
                        'employee_count': account_data.get('employee_count', 0) or 0,
                        'growth_stage': account_data.get('Growth Stage', '')
                    })

                    # CRITICAL FIX: Preserve original company name (account_data may have empty name)
                    company_data['name'] = company_name

                # DEBUG: Log exactly what data we're sending to the classifier
                debug_name = company_data.get('name', 'EMPTY_NAME')
                debug_infra = company_data.get('physical_infrastructure', 'EMPTY_INFRA')[:50]
                logger.info(f"🔍 DEBUG: Sending to classifier - Name: '{debug_name}', Infra: '{debug_infra}...'")

                # Classify partnership potential
                classification = self.partnership_classifier.classify_partnership(company_data)

                # FIXED: Partnership classification is account property, not partnership record
                account_classification = {
                    'partnership_classification': classification.partnership_type.value,
                    'classification_confidence': classification.confidence_score,
                    'classification_reasoning': classification.reasoning,
                    'recommended_approach': classification.recommended_approach,
                    'potential_value': classification.potential_value,
                    'next_actions': classification.next_actions,
                    'classification_date': datetime.now().isoformat()
                }

                partnership_data['account_classification'] = account_classification

                logger.info(f"✅ Account Classification: {classification.partnership_type.value} ({classification.confidence_score:.1f}% confidence)")

            except Exception as e:
                logger.warning(f"Account classification failed: {e}")

        # PART B: Detect actual strategic partnerships (DCIM vendors, GPU providers, etc.)
        # TODO: This would detect actual partner companies like "NVIDIA", "Schneider Electric"
        if self.partnership_intelligence:
            try:
                partnerships = self.partnership_intelligence.analyze_partnerships(company_name, company_domain)
                partnership_data['strategic_partnerships'] = partnerships
                logger.info(f"✅ Found {len(partnerships)} strategic technology partnerships")
            except Exception as e:
                logger.warning(f"Strategic partnership detection failed: {e}")

        return partnership_data

    def _save_complete_research_to_notion(self, research_results: Dict) -> Dict:
        """Save complete research to Notion using consolidated client (UPDATED)"""
        results = {
            'account_saved': False,
            'contacts_saved': 0,
            'events_saved': 0,
            'partnerships_saved': 0
        }

        try:
            # Save account
            if research_results.get('account'):
                account_id = self.notion_client.save_account(research_results['account'])
                results['account_saved'] = bool(account_id)

            # Save contacts
            if research_results.get('contacts'):
                contact_results = self.notion_client.save_contacts(
                    research_results['contacts'],
                    research_results['account'].get('name', '')
                )
                results['contacts_saved'] = sum(contact_results.values())

            # Save trigger events
            if research_results.get('events'):
                event_results = self.notion_client.save_trigger_events(
                    research_results['events'],
                    research_results['account'].get('name', '')
                )
                results['events_saved'] = sum(event_results.values())

            # Save partnerships
            if research_results.get('partnerships'):
                partnership_results = self.notion_client.save_partnerships(
                    research_results['partnerships'],
                    research_results['account'].get('name', '')
                )
                results['partnerships_saved'] = sum(partnership_results.values())

        except Exception as e:
            logger.error(f"Error saving to Notion: {e}")
            results['error'] = str(e)

        return results

    # Helper methods (simplified for space)
    def _calculate_enhanced_icp_fit(self, events: List[Dict]) -> tuple:
        """Calculate ICP fit score with detailed breakdown"""
        # Base infrastructure relevance scoring
        base_score = 50
        infrastructure_relevance = "Medium - Infrastructure Tech"

        # Trigger events impact
        events_count = len(events)
        event_bonus = min(events_count * 10, 40)
        events_impact = f"{events_count} events: " + ", ".join([e.get('event_type', 'Unknown') for e in events[:3]])

        # Company-level scoring (simplified for now)
        title_match = 60  # Default mid-level match
        responsibility_keywords = 40  # Default moderate relevance

        # Calculate final score
        final_score = min(base_score + event_bonus, 100)

        # Build calculation details
        calculation_details = f"Base: {base_score} + Events: {event_bonus} = {final_score}"

        return final_score, {
            'title_match_score': title_match,
            'responsibility_keywords_score': responsibility_keywords,
            'trigger_events_count': events_count,
            'trigger_events_impact': events_impact,
            'icp_calculation_details': calculation_details,
            'infrastructure_relevance': infrastructure_relevance
        }

    def _enrich_company_data(self, company_name: str, domain: str) -> Dict:
        """
        Enrich company data using scalable API-based service
        Replaces hardcoded lookup tables with dynamic Apollo API calls
        """
        if not COMPANY_ENRICHMENT_AVAILABLE:
            logger.warning("Company enrichment service not available, using minimal data")
            return {
                'employee_count': 0,
                'business_model': 'Technology Company',
                'industry': 'Technology',
                'apollo_account_id': '',
                'apollo_organization_id': ''
            }

        try:
            # Use the new API-based enrichment service
            company_data = company_enrichment_service.enrich_company(company_name, domain)

            return {
                'employee_count': company_data.employee_count or 0,
                'business_model': company_data.business_model or 'Technology Company',
                'industry': company_data.industry or 'Technology',
                'apollo_account_id': company_data.apollo_account_id or '',
                'apollo_organization_id': company_data.apollo_organization_id or '',
                'description': company_data.description or '',
                'linkedin_url': company_data.linkedin_url or '',
                'enrichment_source': company_data.enrichment_source,
                'enriched_at': company_data.enriched_at.isoformat() if company_data.enriched_at else ''
            }

        except Exception as e:
            logger.error(f"Company enrichment failed for {company_name} ({domain}): {e}")
            return {
                'employee_count': 0,
                'business_model': 'Technology Company',
                'industry': 'Technology',
                'apollo_account_id': '',
                'apollo_organization_id': ''
            }

    def _determine_industry(self, company_name: str, domain: str) -> str:
        """Determine company industry (simplified)"""
        return "Technology"  # Default industry


    def _generate_research_summary(self, results: Dict, start_time: datetime) -> Dict:
        """Generate comprehensive research summary"""
        duration = (datetime.now() - start_time).total_seconds()

        return {
            'status': 'completed',
            'research_duration_seconds': duration,
            'account_name': results.get('account', {}).get('name', 'Unknown'),
            'contacts_discovered': len(results.get('contacts', [])),
            'trigger_events_found': len(results.get('events', [])),
            'partnerships_identified': len(results.get('partnerships', [])),
            'high_priority_contacts': len([c for c in results.get('contacts', []) if c.get('initial_lead_score', 0) >= 70]),
            'notion_persistence_attempted': bool(results.get('notion_persistence')),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Main entry point for testing"""
    system = ComprehensiveABMSystem()

    # Test with sample company
    test_company = "Genesis Cloud Technologies"
    test_domain = "genesiscloud.com"

    logger.info(f"🧪 Testing ABM system with {test_company}")
    results = system.conduct_complete_account_research(test_company, test_domain)

    logger.info("\n📊 Research Results Summary:")
    summary = results.get('research_summary', {})
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main()