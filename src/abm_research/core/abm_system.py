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
    from .unified_lead_scorer import unified_lead_scorer, account_scorer, meddic_contact_scorer

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

# Import vendor relationship discovery for Phase 5 partnership detection
try:
    from ..intelligence.vendor_relationship_discovery import VendorRelationshipDiscovery

    VENDOR_DISCOVERY_AVAILABLE = True
except ImportError:
    VENDOR_DISCOVERY_AVAILABLE = False
    logging.warning("Vendor relationship discovery not available")

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
        self.linkedin_enrichment = (
            linkedin_enrichment_engine if LINKEDIN_ENRICHMENT_AVAILABLE else None
        )
        self.engagement_intelligence = (
            enhanced_engagement_intelligence if ENGAGEMENT_INTELLIGENCE_AVAILABLE else None
        )
        self.partnership_intelligence = (
            strategic_partnership_intelligence if PARTNERSHIP_INTELLIGENCE_AVAILABLE else None
        )
        self.apollo_discovery = apollo_discovery if APOLLO_DISCOVERY_AVAILABLE else None
        self.scoring_engine = unified_lead_scorer if UNIFIED_SCORER_AVAILABLE else None

        # Enhanced intelligence components
        self.account_intelligence = (
            account_intelligence_engine if ENHANCED_INTELLIGENCE_AVAILABLE else None
        )
        self.conflict_resolver = data_conflict_resolver if ENHANCED_INTELLIGENCE_AVAILABLE else None
        self.partnership_classifier = (
            partnership_classifier if ENHANCED_INTELLIGENCE_AVAILABLE else None
        )

        # Initialize vendor discovery for Phase 5 (NEW)
        self.vendor_discovery = None
        if VENDOR_DISCOVERY_AVAILABLE:
            try:
                self.vendor_discovery = VendorRelationshipDiscovery()
                logger.info("✅ Vendor discovery module initialized")
            except Exception as e:
                logger.warning(f"⚠️  Vendor discovery initialization failed: {e}")

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
            "Trigger Detection": TRIGGER_DETECTOR_AVAILABLE,
            "Contact Discovery": APOLLO_DISCOVERY_AVAILABLE,
            "LinkedIn Enrichment": LINKEDIN_ENRICHMENT_AVAILABLE,
            "Engagement Intelligence": ENGAGEMENT_INTELLIGENCE_AVAILABLE,
            "Partnership Intelligence": PARTNERSHIP_INTELLIGENCE_AVAILABLE,
            "Lead Scoring": UNIFIED_SCORER_AVAILABLE,
            "Notion Persistence": bool(self.notion_client),
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
            "account": {},
            "contacts": [],
            "events": [],
            "partnerships": [],
            "research_summary": {},
            "component_status": {},
            "success": False,
        }

        start_time = datetime.now()

        try:
            # PHASE 1: Account Intelligence Baseline
            logger.info("\n📊 PHASE 1: Account Intelligence Baseline")
            account_data, trigger_events = self._phase_1_account_intelligence(
                company_name, company_domain
            )
            research_results["account"] = account_data
            research_results["events"] = trigger_events

            # PHASE 2: Contact Discovery & Segmentation
            logger.info("\n👥 PHASE 2: Contact Discovery & Segmentation")
            discovered_contacts = self._phase_2_contact_discovery(
                company_name, company_domain, account_data
            )
            research_results["contacts"] = discovered_contacts

            # PHASE 3: High-Priority Contact Enrichment
            logger.info("\n🔍 PHASE 3: High-Priority Contact Enrichment")
            enriched_contacts = self._phase_3_contact_enrichment(discovered_contacts)
            research_results["contacts"] = enriched_contacts

            # PHASE 4: Engagement Intelligence
            logger.info("\n🧠 PHASE 4: Engagement Intelligence")
            intelligence_enhanced_contacts = self._phase_4_engagement_intelligence(
                enriched_contacts, trigger_events, account_data
            )
            research_results["contacts"] = intelligence_enhanced_contacts

            # PHASE 5: Strategic Partnership Intelligence
            logger.info("\n🤝 PHASE 5: Strategic Partnership Intelligence")
            partnership_data = self._phase_5_partnership_intelligence(
                company_name, company_domain, trigger_events
            )

            # FIXED: Integrate account classification into account data
            if partnership_data.get("account_classification"):
                account_classification = partnership_data["account_classification"]
                # Add partnership fields to account data
                research_results["account"][
                    "partnership_classification"
                ] = account_classification.get("partnership_classification", "unknown")
                research_results["account"][
                    "classification_confidence"
                ] = account_classification.get("classification_confidence", 0.0)
                research_results["account"][
                    "classification_reasoning"
                ] = account_classification.get("classification_reasoning", "")
                research_results["account"]["recommended_approach"] = account_classification.get(
                    "recommended_approach", ""
                )
                research_results["account"]["potential_value"] = account_classification.get(
                    "potential_value", ""
                )
                research_results["account"]["next_actions"] = account_classification.get(
                    "next_actions", []
                )
                research_results["account"]["classification_date"] = account_classification.get(
                    "classification_date", ""
                )

                logger.info(
                    f"✅ Account classification integrated: {research_results['account']['partnership_classification']} ({research_results['account']['classification_confidence']:.1f}%)"
                )

            # Store only strategic partnerships list, not account classification
            research_results["partnerships"] = partnership_data.get("strategic_partnerships", [])

            # Generate comprehensive research summary
            research_results["research_summary"] = self._generate_research_summary(
                research_results, start_time
            )

            # STEP 6: Persist research data to Notion (UPDATED)
            logger.info("\n💾 STEP 6: Persisting Research to Notion")
            if self.notion_client:
                try:
                    persistence_results = self._save_complete_research_to_notion(research_results)
                    research_results["notion_persistence"] = persistence_results
                    logger.info(f"✅ Notion persistence complete:")
                    logger.info(
                        f"   📋 Contacts saved: {persistence_results.get('contacts_saved', 0)}"
                    )
                    logger.info(f"   🎯 Events saved: {persistence_results.get('events_saved', 0)}")
                    logger.info(
                        f"   🏢 Account saved: {persistence_results.get('account_saved', False)}"
                    )
                except Exception as e:
                    logger.error(f"⚠️  Notion persistence failed: {e}")
                    research_results["notion_persistence"] = {"error": str(e)}
            else:
                logger.warning("⚠️  Notion client not available, skipping persistence")
                research_results["notion_persistence"] = {"skipped": "Notion client not available"}

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n✅ ABM research completed in {duration:.1f} seconds")
            research_results["success"] = True
            return research_results

        except Exception as e:
            logger.error(f"❌ Error in ABM research: {e}")
            research_results["research_summary"] = {
                "status": "failed",
                "error": str(e),
                "research_duration_seconds": (datetime.now() - start_time).total_seconds(),
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
                formatted_events.append(
                    {
                        "id": f"event_{len(formatted_events) + 1}",
                        "description": event.description,
                        "event_type": event.event_type,
                        "confidence": event.confidence,
                        "confidence_score": event.confidence_score,
                        "relevance_score": event.relevance_score,
                        "source_url": event.source_url,
                        "source_type": event.source_type,
                        "detected_date": event.detected_date,
                        "occurred_date": event.occurred_date,
                        "urgency_level": event.urgency_level,
                    }
                )

            logger.info(f"✅ Found {len(formatted_events)} trigger events")
        else:
            logger.warning("⚠️  Trigger detector not available, using mock data")
            formatted_events = [
                {
                    "id": "mock_event_1",
                    "description": f"{company_name} expansion activities detected",
                    "event_type": "expansion",
                    "confidence": "Medium",
                    "confidence_score": 75,
                    "relevance_score": 80,
                    "source_url": f'https://example.com/{company_name.lower().replace(" ", "-")}',
                    "source_type": "Mock Data",
                    "detected_date": datetime.now().strftime("%Y-%m-%d"),
                    "occurred_date": datetime.now().strftime("%Y-%m-%d"),
                    "urgency_level": "Medium",
                }
            ]

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
                enhanced_intelligence = self.account_intelligence.convert_to_notion_format(
                    account_intel
                )
                logger.info(
                    f"✅ Enhanced intelligence: {account_intel.confidence_score:.1f} confidence, "
                    f"{len(account_intel.data_sources)} sources"
                )
            except Exception as e:
                logger.warning(f"Enhanced intelligence failed: {e}")

        account_data = {
            "name": company_name,
            "domain": company_domain,
            "employee_count": enriched_company.get("employee_count", 0),
            "icp_fit_score": icp_fit_score,
            "industry": enriched_company.get("industry", "Technology"),
            "business_model": enriched_company.get("business_model", "Technology Company"),
            # Apollo fields from API enrichment
            "apollo_account_id": enriched_company.get("apollo_account_id", ""),
            "apollo_organization_id": enriched_company.get("apollo_organization_id", ""),
            # Add ICP breakdown components
            **icp_breakdown,
            # Enhanced intelligence fields
            **enhanced_intelligence,
        }

        # ACCOUNT-FIRST SCORING: Calculate infrastructure-aware account score
        # This is an ACCOUNT-level score - the company owns the infrastructure, not contacts
        if UNIFIED_SCORER_AVAILABLE and account_scorer:
            logger.info("🏢 Calculating Account-First score with infrastructure breakdown...")
            try:
                # Prepare account data for scoring (merge all available intelligence)
                scoring_input = {
                    "Physical Infrastructure": account_data.get("Physical Infrastructure", ""),
                    "physical_infrastructure": account_data.get("Physical Infrastructure", ""),
                    "current_tech_stack": account_data.get("current_tech_stack", ""),
                    "business_model": account_data.get("business_model", ""),
                    "employee_count": account_data.get("employee_count", 0),
                    "data_center_locations": account_data.get("data_center_locations", []),
                    "growth_indicators": account_data.get("growth_indicators", []),
                    "trigger_events": formatted_events,  # Pass trigger events for buying signals
                }

                # Calculate comprehensive account score
                account_score_result = account_scorer.calculate_account_score(scoring_input)

                # Store scores on account for dashboard display
                account_data["account_score"] = account_score_result.total_score
                account_data["infrastructure_score"] = account_score_result.infrastructure_fit.score
                account_data["business_fit_score"] = account_score_result.business_fit.score
                account_data["buying_signals_score"] = account_score_result.buying_signals.score
                account_data["account_priority_level"] = account_score_result.priority_level

                # Store full breakdowns for dashboard traceability (JSON serializable)
                account_data[
                    "infrastructure_breakdown"
                ] = account_score_result.infrastructure_fit.to_dict()
                account_data["account_score_breakdown"] = account_score_result.get_score_breakdown()

                logger.info(
                    f"✅ Account Score: {account_score_result.total_score:.1f} ({account_score_result.priority_level})"
                )
                logger.info(
                    f"   Infrastructure: {account_score_result.infrastructure_fit.score:.1f} | "
                    f"Business: {account_score_result.business_fit.score:.1f} | "
                    f"Signals: {account_score_result.buying_signals.score:.1f}"
                )

                # Log detected infrastructure keywords for visibility
                infra_breakdown = account_score_result.infrastructure_fit.breakdown
                detected_categories = [
                    cat for cat, data in infra_breakdown.items() if data.get("detected")
                ]
                if detected_categories:
                    logger.info(f"   🔍 Detected infrastructure: {', '.join(detected_categories)}")

            except Exception as e:
                logger.warning(f"⚠️  Account scoring failed: {e}")
                account_data["account_score"] = 0.0
                account_data["infrastructure_score"] = 0.0
                account_data["account_score_breakdown"] = {"error": str(e)}

        # Store account data for Phase 5 partnership classification
        self._current_account_data = account_data

        logger.info(f"✅ Account ICP fit score: {icp_fit_score}")
        return account_data, formatted_events

    def _phase_2_contact_discovery(
        self, company_name: str, company_domain: str, account_data: Dict
    ) -> List[Dict]:
        """Phase 2: Contact Discovery & Segmentation with MEDDIC scoring"""
        if self.apollo_discovery:
            logger.info("🔍 Discovering contacts via Apollo API...")
            try:
                raw_contacts = self.apollo_discovery.discover_contacts(company_name, company_domain)
                contacts = self.apollo_discovery.convert_to_notion_format(
                    raw_contacts, company_name
                )

                enhanced_contacts = []
                for contact in contacts:
                    # MEDDIC SCORING: Prioritize Entry Point roles (Technical Believers)
                    # This INVERTS traditional scoring that would prioritize VPs/CIOs first
                    if UNIFIED_SCORER_AVAILABLE and meddic_contact_scorer:
                        try:
                            meddic_result = meddic_contact_scorer.calculate_contact_score(
                                contact, account_data
                            )

                            # Store MEDDIC scores
                            contact["lead_score"] = meddic_result.total_score
                            contact["initial_lead_score"] = meddic_result.total_score
                            contact[
                                "champion_potential_score"
                            ] = meddic_result.champion_potential_score
                            contact["role_tier"] = meddic_result.role_tier
                            contact["role_classification"] = meddic_result.role_classification
                            contact[
                                "champion_potential_level"
                            ] = meddic_result.champion_potential_level
                            contact["recommended_approach"] = meddic_result.recommended_approach
                            contact["why_prioritize"] = meddic_result.why_prioritize
                            contact["meddic_score_breakdown"] = meddic_result.get_score_breakdown()

                        except Exception as e:
                            logger.warning(
                                f"MEDDIC scoring failed for {contact.get('name', 'unknown')}: {e}"
                            )
                            # Fallback to legacy scoring
                            if self.scoring_engine:
                                score = self.scoring_engine.calculate_lead_score(
                                    contact, account_data
                                )
                                contact["lead_score"] = score
                                contact["initial_lead_score"] = score
                            else:
                                contact["lead_score"] = 50
                                contact["initial_lead_score"] = 50
                    elif self.scoring_engine:
                        # Legacy scoring fallback
                        score = self.scoring_engine.calculate_lead_score(contact, account_data)
                        contact["lead_score"] = score
                        contact["initial_lead_score"] = score
                    else:
                        contact["lead_score"] = 50
                        contact["initial_lead_score"] = 50

                    enhanced_contacts.append(contact)

                # Log MEDDIC scoring summary
                if UNIFIED_SCORER_AVAILABLE and meddic_contact_scorer:
                    entry_points = [
                        c for c in enhanced_contacts if c.get("role_tier") == "entry_point"
                    ]
                    middle_deciders = [
                        c for c in enhanced_contacts if c.get("role_tier") == "middle_decider"
                    ]
                    economic_buyers = [
                        c for c in enhanced_contacts if c.get("role_tier") == "economic_buyer"
                    ]
                    logger.info(
                        f"✅ MEDDIC Segmentation: {len(entry_points)} Entry Points, "
                        f"{len(middle_deciders)} Middle Deciders, {len(economic_buyers)} Economic Buyers"
                    )

                    # Highlight high-champion-potential contacts
                    high_champions = [
                        c
                        for c in enhanced_contacts
                        if c.get("champion_potential_level") in ["Very High", "High"]
                    ]
                    if high_champions:
                        logger.info(f"🏆 High Champion Potential: {len(high_champions)} contacts")
                        for c in high_champions[:3]:  # Show top 3
                            logger.info(
                                f"   → {c.get('name', 'Unknown')}: {c.get('title', 'Unknown')} "
                                f"({c.get('champion_potential_level', 'N/A')})"
                            )

                logger.info(f"✅ Discovered {len(enhanced_contacts)} contacts")
                return enhanced_contacts

            except Exception as e:
                logger.error(f"⚠️  Apollo discovery failed: {e}")
        else:
            logger.warning("⚠️  Apollo discovery not available")

        # Mock fallback
        logger.info("📝 Using mock contact data")
        return [
            {
                "name": f"Contact Manager at {company_name}",
                "title": "Senior Manager",
                "email": f"manager@{company_domain}",
                "company": company_name,
                "initial_lead_score": 60,
            }
        ]

    def _phase_3_contact_enrichment(self, contacts: List[Dict]) -> List[Dict]:
        """Phase 3: High-Priority Contact Enrichment"""
        if not self.linkedin_enrichment:
            logger.warning("⚠️  LinkedIn enrichment not available, skipping enrichment")
            return contacts

        # Normalize field names from Apollo output (Notion format uses capitals, Python uses lowercase)
        # This fixes the bug where high-scoring contacts were being skipped due to field name mismatch
        for contact in contacts:
            # Normalize Lead Score field names
            if "Lead Score" in contact and "lead_score" not in contact:
                contact["lead_score"] = contact["Lead Score"]
            if "Initial Lead Score" in contact and "initial_lead_score" not in contact:
                contact["initial_lead_score"] = contact["Initial Lead Score"]

        # Check for both field names (lead_score from Apollo, initial_lead_score for backward compatibility)
        def get_lead_score(contact):
            return max(contact.get("lead_score", 0), contact.get("initial_lead_score", 0))

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
                        logger.debug(
                            f"🔍 Resolving data conflicts for {contact.get('name', 'unknown')}"
                        )

                        # Separate Apollo (original) and LinkedIn (enriched) data
                        apollo_data = {
                            k: v
                            for k, v in contact.items()
                            if k not in enriched_data
                            or not isinstance(enriched_data, dict)
                            or k not in enriched_data
                        }

                        # Convert enriched_data to dict if it's not already
                        if hasattr(enriched_data, "__dict__"):
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
                        contact["enrichment_status"] = "enriched"
                        contact["data_conflicts_resolved"] = len(merge_result.conflicts_detected)

                        # Log conflicts for monitoring
                        if merge_result.conflicts_detected:
                            self.conflict_resolver.log_conflicts_summary(merge_result)

                    else:
                        # Fallback: Simple merge (original behavior)
                        contact.update(enriched_data)
                        contact["enrichment_status"] = "enriched"

                except Exception as e:
                    logger.warning(f"Enrichment failed for {contact.get('name', 'unknown')}: {e}")
                    contact["enrichment_status"] = "failed"
            else:
                contact["enrichment_status"] = "skipped_low_score"

            enriched_contacts.append(contact)

        enriched_count = sum(
            1 for c in enriched_contacts if c.get("enrichment_status") == "enriched"
        )
        logger.info(f"✅ Enriched {enriched_count}/{len(high_priority_contacts)} contacts")
        return enriched_contacts

    def _phase_4_engagement_intelligence(
        self, contacts: List[Dict], events: List[Dict], account_data: Dict
    ) -> List[Dict]:
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
                contact["intelligence_status"] = "generated"
            except Exception as e:
                logger.warning(
                    f"Intelligence generation failed for {contact.get('name', 'unknown')}: {e}"
                )
                contact["intelligence_status"] = "failed"

            intelligence_contacts.append(contact)

        intelligence_count = sum(
            1 for c in intelligence_contacts if c.get("intelligence_status") == "generated"
        )
        logger.info(f"✅ Generated intelligence for {intelligence_count}/{len(contacts)} contacts")
        return intelligence_contacts

    def _phase_5_partnership_intelligence(
        self, company_name: str, company_domain: str, trigger_events: List[Dict] = None
    ) -> Dict[str, any]:
        """Phase 5: Partnership Classification & Strategic Partnership Detection

        Args:
            company_name: Target company name
            company_domain: Company domain
            trigger_events: Optional list of trigger events for partnership angle generation
        """
        logger.info("🤝 Analyzing strategic partnership classification...")

        partnership_data = {"account_classification": None, "strategic_partnerships": []}

        # PART A: Classify the account itself (Strategic Partner, Direct ICP, etc.)
        if self.partnership_classifier:
            try:
                # Use account intelligence to build company profile for classification
                company_data = {
                    "name": company_name,
                    "domain": company_domain,
                    "business_model": "",
                    "physical_infrastructure": "",
                    "tech_stack": "",
                    "recent_announcements": "",
                    "employee_count": 0,
                    "growth_stage": "",
                }

                # Enhance with available account intelligence data if present
                if hasattr(self, "_current_account_data") and self._current_account_data:
                    account_data = self._current_account_data
                    company_data.update(
                        {
                            "business_model": account_data.get("business_model", ""),
                            "physical_infrastructure": account_data.get(
                                "Physical Infrastructure", ""
                            ),
                            "tech_stack": account_data.get("Physical Infrastructure", ""),
                            "recent_announcements": account_data.get("Recent Announcements", ""),
                            "employee_count": account_data.get("employee_count", 0) or 0,
                            "growth_stage": account_data.get("Growth Stage", ""),
                        }
                    )

                    # CRITICAL FIX: Preserve original company name (account_data may have empty name)
                    company_data["name"] = company_name

                # DEBUG: Log exactly what data we're sending to the classifier
                debug_name = company_data.get("name", "EMPTY_NAME")
                debug_infra = company_data.get("physical_infrastructure", "EMPTY_INFRA")[:50]
                logger.info(
                    f"🔍 DEBUG: Sending to classifier - Name: '{debug_name}', Infra: '{debug_infra}...'"
                )

                # Classify partnership potential
                classification = self.partnership_classifier.classify_partnership(company_data)

                # FIXED: Partnership classification is account property, not partnership record
                account_classification = {
                    "partnership_classification": classification.partnership_type.value,
                    "classification_confidence": classification.confidence_score,
                    "classification_reasoning": classification.reasoning,
                    "recommended_approach": classification.recommended_approach,
                    "potential_value": classification.potential_value,
                    "next_actions": classification.next_actions,
                    "classification_date": datetime.now().isoformat(),
                }

                partnership_data["account_classification"] = account_classification

                logger.info(
                    f"✅ Account Classification: {classification.partnership_type.value} ({classification.confidence_score:.1f}% confidence)"
                )

            except Exception as e:
                logger.warning(f"Account classification failed: {e}")

        # PART B: Discover actual vendor relationships using AI-powered extraction
        # Uses GPT-4o-mini to analyze search results and extract vendor names
        if self.vendor_discovery:
            try:
                logger.info(f"🔍 Running vendor discovery for {company_name}...")

                # Call the vendor discovery module (save_to_notion=False since we'll save via research pipeline)
                discovery_result = self.vendor_discovery.discover_unknown_vendors(
                    account_name=company_name,
                    save_to_notion=False,  # We'll save via our own save method with account relation
                    min_confidence=0.6,
                )

                if discovery_result.get("status") == "success" and discovery_result.get(
                    "discovered_vendors"
                ):
                    discovered = discovery_result["discovered_vendors"]

                    # Convert discovered vendors to partnership format for Notion
                    partnerships = []
                    for vendor in discovered:
                        # Generate partnership angle with AI/template source tracking
                        angle_data = self._generate_partnership_angle(
                            vendor, company_name, trigger_events
                        )

                        partnership = {
                            "partner_name": vendor.get("vendor_name", ""),
                            "partnership_type": self._map_vendor_category_to_partnership_type(
                                vendor.get("category", "evaluate")
                            ),
                            "relevance_score": int(vendor.get("confidence", 0.5) * 100),
                            "relationship_depth": self._calculate_relationship_depth(vendor),
                            "relationship_evidence": self._format_evidence(vendor),
                            "partnership_angle": angle_data.get("content", ""),
                            "partnership_angle_source": angle_data.get("source", "template"),
                            "partnership_angle_source_label": angle_data.get(
                                "source_label", "Template-Based"
                            ),
                            "discovery_source": "vendor_discovery_ai",
                            "discovery_date": datetime.now().isoformat(),
                        }
                        partnerships.append(partnership)

                    partnership_data["strategic_partnerships"] = partnerships
                    logger.info(f"✅ Discovered {len(partnerships)} vendor relationships")

                    # Log category breakdown
                    category_summary = discovery_result.get("category_summary", {})
                    if category_summary:
                        categories_str = ", ".join(
                            f"{k}:{v}" for k, v in category_summary.items() if v > 0
                        )
                        logger.info(f"   Categories: {categories_str}")
                else:
                    logger.info(
                        "ℹ️  No new vendors discovered (may already be in known vendors list)"
                    )

            except Exception as e:
                logger.warning(f"Vendor discovery failed: {e}")
        else:
            logger.warning("⚠️  Vendor discovery module not available")

        return partnership_data

    def _map_vendor_category_to_partnership_type(self, category: str) -> str:
        """Map vendor discovery category to partnership type"""
        mapping = {
            "competitor": "Competitive Intelligence",
            "channel": "Channel Partner",
            "intro_path": "Strategic Partner",
            "evaluate": "Technology Vendor",
            "unknown": "Technology Vendor",
        }
        return mapping.get(category, "Technology Vendor")

    def _calculate_relationship_depth(self, vendor: Dict) -> str:
        """Calculate relationship depth based on mention count and evidence"""
        mention_count = vendor.get("mention_count", 0)
        confidence = vendor.get("confidence", 0)

        if mention_count >= 5 and confidence >= 0.8:
            return "Deep Integration"
        elif mention_count >= 3 or confidence >= 0.7:
            return "Active Partnership"
        elif mention_count >= 2:
            return "Mentioned Relationship"
        else:
            return "Potential Relationship"

    def _format_evidence(self, vendor: Dict) -> str:
        """Format evidence snippets into readable string"""
        snippets = vendor.get("evidence_snippets", [])
        if not snippets:
            return f"Discovered via AI analysis ({vendor.get('relationship_type', 'unknown')} relationship)"

        # Take first 2 snippets, truncate each
        formatted = []
        for snippet in snippets[:2]:
            clean_snippet = snippet.strip()[:200]
            if len(snippet) > 200:
                clean_snippet += "..."
            formatted.append(f"• {clean_snippet}")

        return "\n".join(formatted)

    def _generate_partnership_angle(
        self, vendor: Dict, account_name: str, trigger_events: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate AI-powered actionable partnership angle for BD professionals.

        Uses Brave Search + OpenAI to research the relationship and formulate
        specific, contextualized BD recommendations.

        Args:
            vendor: Vendor discovery data with name, category, evidence
            account_name: The account we're researching partnerships for
            trigger_events: Optional list of trigger events for timing context

        Returns:
            Dict with 'content' (the angle text) and 'source' ('ai' or 'template')
        """
        vendor_name = vendor.get("vendor_name", "Unknown")
        category = vendor.get("category", "evaluate")
        relationship = vendor.get("relationship_type", "uses")
        confidence = vendor.get("confidence", 0.5)
        evidence = vendor.get("evidence_snippets", [])

        # Try AI-powered research first
        try:
            ai_angle = self._generate_ai_partnership_angle(
                vendor_name=vendor_name,
                account_name=account_name,
                category=category,
                relationship=relationship,
                evidence=evidence,
                trigger_events=trigger_events or [],
            )
            if ai_angle:
                return {"content": ai_angle, "source": "ai", "source_label": "AI-Researched"}
        except Exception as e:
            logger.warning(f"AI partnership angle generation failed: {e}")

        # Fallback to template-based generation
        template_angle = self._generate_template_partnership_angle(
            vendor_name=vendor_name,
            account_name=account_name,
            category=category,
            relationship=relationship,
            confidence=confidence,
            evidence=evidence,
        )
        return {"content": template_angle, "source": "template", "source_label": "Template-Based"}

    def _generate_ai_partnership_angle(
        self,
        vendor_name: str,
        account_name: str,
        category: str,
        relationship: str,
        evidence: List[str],
        trigger_events: List[Dict],
    ) -> Optional[str]:
        """
        Use Brave Search + OpenAI to generate research-backed partnership angle.
        """
        import os
        import requests

        # Step 1: Quick Brave search for recent context
        search_context = []
        brave_api_key = os.environ.get("BRAVE_API_KEY")

        if brave_api_key:
            try:
                # Search for recent partnership/relationship news
                query = f'"{account_name}" "{vendor_name}" partnership OR collaboration OR integration 2024'
                headers = {"Accept": "application/json", "X-Subscription-Token": brave_api_key}
                response = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    for result in data.get("web", {}).get("results", [])[:3]:
                        search_context.append(
                            {
                                "title": result.get("title", ""),
                                "description": result.get("description", ""),
                            }
                        )
            except Exception as e:
                logger.debug(f"Brave search failed for partnership context: {e}")

        # Step 2: Format trigger events as timing signals
        timing_signals = []
        for event in trigger_events[:3]:  # Top 3 most relevant
            event_type = event.get("event_type", event.get("type", ""))
            description = event.get("description", event.get("title", ""))
            if event_type and description:
                timing_signals.append(f"- {event_type}: {description[:100]}")

        # Step 3: Use OpenAI to synthesize actionable BD approach
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            return None

        # Format evidence snippets
        evidence_text = (
            "\n".join([f"- {e[:150]}" for e in evidence[:3]])
            if evidence
            else "No specific evidence available"
        )

        # Format search context
        search_text = (
            "\n".join([f"- {r['title']}: {r['description'][:100]}" for r in search_context])
            if search_context
            else "No recent news found"
        )

        # Format timing signals
        timing_text = "\n".join(timing_signals) if timing_signals else "No recent trigger events"

        # Category context
        category_context = {
            "competitor": "They compete in overlapping markets",
            "channel": "They have a distribution/reseller relationship",
            "intro_path": f"{account_name} uses/partners with {vendor_name}",
            "evaluate": f"{account_name} has some relationship with {vendor_name}",
        }.get(category, "Unknown relationship type")

        prompt = f"""You are a B2B sales strategist for Verdigris, an energy analytics and sustainability SaaS company that helps enterprises with GPU datacenters and physical infrastructure reduce energy costs and meet sustainability goals.

Generate a specific, actionable partnership approach for a BD professional.

CONTEXT:
- Our Account: {account_name}
- Target Partner: {vendor_name}
- Relationship Type: {category_context}
- Relationship Evidence: {relationship}

EXISTING EVIDENCE:
{evidence_text}

RECENT NEWS/CONTEXT:
{search_text}

TIMING SIGNALS (Trigger Events for {account_name}):
{timing_text}

Write a 3-4 sentence partnership angle that includes:
1. WHY this partnership matters (specific synergy or opportunity)
2. HOW to engage (specific first step, who to contact, what to propose)
3. TIMING consideration (based on trigger events if relevant)
4. VALUE PROP (what Verdigris brings to the table)

Be specific and actionable. Reference actual context from the evidence/news when possible.
Format: Start with the partnership type in caps, then provide the actionable guidance."""

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7,
                },
                timeout=15,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI partnership angle generation failed: {e}")

        return None

    def _generate_template_partnership_angle(
        self,
        vendor_name: str,
        account_name: str,
        category: str,
        relationship: str,
        confidence: float,
        evidence: List[str],
    ) -> str:
        """
        Fallback template-based partnership angle generation.
        """
        if category == "competitor":
            return (
                f"COMPETITIVE INTEL: {account_name} and {vendor_name} compete in overlapping markets. "
                f"BD APPROACH: (1) Research their customer base for accounts frustrated with {vendor_name}'s limitations. "
                f"(2) Position Verdigris as complementary/alternative during {vendor_name} contract renewals. "
                f"(3) Target mutual customers where consolidation pressure exists. "
                f"VALUE PROP: Emphasize Verdigris differentiation vs {vendor_name} in energy analytics/sustainability."
            )

        elif category == "channel":
            return (
                f"CHANNEL OPPORTUNITY: {vendor_name} distributes or resells for {account_name}. "
                f"BD APPROACH: (1) Explore co-selling arrangement where {vendor_name} bundles Verdigris with their solution. "
                f"(2) Request warm intro to their enterprise sales team. "
                f"(3) Propose joint case study if they serve datacenter/infrastructure customers. "
                f"ACCESS: {vendor_name} likely has established relationships with {account_name}'s customer base. "
                f"VALUE PROP: Position Verdigris as add-on that increases {vendor_name}'s deal size."
            )

        elif category == "intro_path":
            confidence_str = (
                "strong"
                if confidence >= 0.8
                else "established"
                if confidence >= 0.6
                else "emerging"
            )
            return (
                f"WARM INTRO PATH: {account_name} has {confidence_str} relationship with {vendor_name} ({relationship}). "
                f"BD APPROACH: (1) Ask {account_name} for intro to their {vendor_name} contact. "
                f"(2) Propose joint pilot at {vendor_name}'s facilities using {account_name} as reference. "
                f"(3) Explore if {vendor_name} is evaluating energy management solutions. "
                f"ACCESS: {account_name} can provide credibility and context for {vendor_name} engagement. "
                f"VALUE PROP: Leverage {account_name}'s results to demonstrate ROI to {vendor_name}."
            )

        else:  # 'evaluate' or unknown
            return (
                f"VENDOR RELATIONSHIP: {account_name} {relationship} {vendor_name}. "
                f"BD APPROACH: (1) Understand what problems {vendor_name} solves for {account_name}. "
                f"(2) Identify if Verdigris can integrate with or complement {vendor_name}'s solution. "
                f"(3) Explore if {vendor_name} serves other accounts in our target list. "
                f"NEXT STEP: Research {vendor_name}'s partner ecosystem and identify Verdigris fit. "
                f"VALUE PROP: Energy visibility/sustainability data that enhances {vendor_name}'s infrastructure story."
            )

    def _save_complete_research_to_notion(self, research_results: Dict) -> Dict:
        """Save complete research to Notion using consolidated client (UPDATED)"""
        results = {
            "account_saved": False,
            "contacts_saved": 0,
            "events_saved": 0,
            "partnerships_saved": 0,
        }

        try:
            # Save account
            if research_results.get("account"):
                account_id = self.notion_client.save_account(research_results["account"])
                results["account_saved"] = bool(account_id)

            # Save contacts
            if research_results.get("contacts"):
                contact_results = self.notion_client.save_contacts(
                    research_results["contacts"], research_results["account"].get("name", "")
                )
                results["contacts_saved"] = sum(contact_results.values())

            # Save trigger events
            if research_results.get("events"):
                event_results = self.notion_client.save_trigger_events(
                    research_results["events"], research_results["account"].get("name", "")
                )
                results["events_saved"] = sum(event_results.values())

            # Save partnerships
            if research_results.get("partnerships"):
                partnership_results = self.notion_client.save_partnerships(
                    research_results["partnerships"], research_results["account"].get("name", "")
                )
                results["partnerships_saved"] = sum(partnership_results.values())

        except Exception as e:
            logger.error(f"Error saving to Notion: {e}")
            results["error"] = str(e)

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
        events_impact = f"{events_count} events: " + ", ".join(
            [e.get("event_type", "Unknown") for e in events[:3]]
        )

        # Company-level scoring (simplified for now)
        title_match = 60  # Default mid-level match
        responsibility_keywords = 40  # Default moderate relevance

        # Calculate final score
        final_score = min(base_score + event_bonus, 100)

        # Build calculation details
        calculation_details = f"Base: {base_score} + Events: {event_bonus} = {final_score}"

        return final_score, {
            "title_match_score": title_match,
            "responsibility_keywords_score": responsibility_keywords,
            "trigger_events_count": events_count,
            "trigger_events_impact": events_impact,
            "icp_calculation_details": calculation_details,
            "infrastructure_relevance": infrastructure_relevance,
        }

    def _enrich_company_data(self, company_name: str, domain: str) -> Dict:
        """
        Enrich company data using scalable API-based service
        Replaces hardcoded lookup tables with dynamic Apollo API calls
        """
        if not COMPANY_ENRICHMENT_AVAILABLE:
            logger.warning("Company enrichment service not available, using minimal data")
            return {
                "employee_count": 0,
                "business_model": "Technology Company",
                "industry": "Technology",
                "apollo_account_id": "",
                "apollo_organization_id": "",
            }

        try:
            # Use the new API-based enrichment service
            company_data = company_enrichment_service.enrich_company(company_name, domain)

            return {
                "employee_count": company_data.employee_count or 0,
                "business_model": company_data.business_model or "Technology Company",
                "industry": company_data.industry or "Technology",
                "apollo_account_id": company_data.apollo_account_id or "",
                "apollo_organization_id": company_data.apollo_organization_id or "",
                "description": company_data.description or "",
                "linkedin_url": company_data.linkedin_url or "",
                "enrichment_source": company_data.enrichment_source,
                "enriched_at": company_data.enriched_at.isoformat()
                if company_data.enriched_at
                else "",
            }

        except Exception as e:
            logger.error(f"Company enrichment failed for {company_name} ({domain}): {e}")
            return {
                "employee_count": 0,
                "business_model": "Technology Company",
                "industry": "Technology",
                "apollo_account_id": "",
                "apollo_organization_id": "",
            }

    def _determine_industry(self, company_name: str, domain: str) -> str:
        """Determine company industry (simplified)"""
        return "Technology"  # Default industry

    def _generate_research_summary(self, results: Dict, start_time: datetime) -> Dict:
        """Generate comprehensive research summary"""
        duration = (datetime.now() - start_time).total_seconds()

        return {
            "status": "completed",
            "research_duration_seconds": duration,
            "account_name": results.get("account", {}).get("name", "Unknown"),
            "contacts_discovered": len(results.get("contacts", [])),
            "trigger_events_found": len(results.get("events", [])),
            "partnerships_identified": len(results.get("partnerships", [])),
            "high_priority_contacts": len(
                [c for c in results.get("contacts", []) if c.get("initial_lead_score", 0) >= 70]
            ),
            "notion_persistence_attempted": bool(results.get("notion_persistence")),
            "timestamp": datetime.now().isoformat(),
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
    summary = results.get("research_summary", {})
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main()
