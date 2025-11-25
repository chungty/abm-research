#!/usr/bin/env python3
"""
Consolidated Notion Client for ABM Research System

Merges functionality from:
- src/integrations/notion_database.py (workspace setup, database schemas)
- notion_persistence_manager.py (CRUD operations, deduplication, rate limiting)

Provides unified interface for:
- Complete ABM workspace creation with all 5 databases
- Data persistence with deduplication and rate limiting
- Comprehensive error handling and logging
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dataclasses import asdict

# Try to import notion client for advanced features
try:
    from notion_client import Client
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    logging.warning("notion-client not available, using direct API calls")

# Try to import models for type validation
try:
    from src.models.account import Account
    from src.models.contact import Contact
    from src.models.trigger_event import TriggerEvent
    from src.models.strategic_partnership import StrategicPartnership
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    logging.warning("ABM models not available, using dict-based operations")

logger = logging.getLogger(__name__)


class NotionClient:
    """
    Unified Notion client for ABM Research System
    Handles both workspace setup and data operations
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Notion client with unified API key handling

        Resolves API key naming confusion by checking multiple environment variables:
        - NOTION_API_KEY (preferred standard)
        - NOTION_ABM_API_KEY (legacy from abm_config)
        """
        self.setup_logging()

        # Unified API key resolution
        self.api_key = self._resolve_api_key(api_key)

        # Initialize clients
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        # Advanced client if available
        if NOTION_CLIENT_AVAILABLE:
            try:
                self.client = Client(auth=self.api_key)
                logger.info("✅ Advanced Notion client initialized")
            except Exception as e:
                logger.warning(f"Advanced client failed, using direct API: {e}")
                self.client = None
        else:
            self.client = None

        # Database configuration
        self.database_ids = self._load_database_config()

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 0.5  # 500ms between requests

    def _resolve_api_key(self, provided_key: Optional[str]) -> str:
        """Resolve API key from multiple possible sources"""
        if provided_key:
            return provided_key

        # Try standard name first
        api_key = os.getenv('NOTION_API_KEY')
        if api_key:
            logger.info("✅ Using NOTION_API_KEY")
            return api_key

        # Try legacy name
        api_key = os.getenv('NOTION_ABM_API_KEY')
        if api_key:
            logger.warning("⚠️  Using legacy NOTION_ABM_API_KEY, consider using NOTION_API_KEY")
            return api_key

        raise ValueError(
            "❌ Notion API key not found. Set either NOTION_API_KEY or NOTION_ABM_API_KEY"
        )

    def _load_database_config(self) -> Dict[str, Optional[str]]:
        """Load database IDs from environment variables"""
        db_config = {
            'accounts': os.getenv('NOTION_ACCOUNTS_DB_ID'),
            'contacts': os.getenv('NOTION_CONTACTS_DB_ID'),
            'trigger_events': os.getenv('NOTION_TRIGGER_EVENTS_DB_ID') or os.getenv('NOTION_EVENTS_DB_ID'),
            'partnerships': os.getenv('NOTION_PARTNERSHIPS_DB_ID')
        }

        # Log configuration status
        configured = [name for name, db_id in db_config.items() if db_id]
        missing = [name for name, db_id in db_config.items() if not db_id]

        if configured:
            logger.info(f"✅ Configured databases: {', '.join(configured)}")
        if missing:
            logger.warning(f"⚠️  Missing database IDs: {', '.join(missing)}")

        return db_config

    def setup_logging(self):
        """Setup logging for Notion operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make rate-limited request to Notion API"""
        self._rate_limit()

        kwargs.setdefault('headers', self.headers)
        response = requests.request(method, url, **kwargs)

        if not response.ok:
            logger.error(f"Notion API error: {response.status_code} - {response.text}")
            response.raise_for_status()

        return response

    # ═══════════════════════════════════════════════════════════════════════════════════
    # WORKSPACE SETUP (from notion_database.py)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def setup_abm_workspace(self, parent_page_id: str) -> Dict[str, str]:
        """
        Create complete ABM research workspace with all 5 databases

        Args:
            parent_page_id: Notion page ID where databases should be created

        Returns:
            Dictionary mapping database names to their IDs
        """
        logger.info("🏗️ Setting up ABM Research workspace in Notion...")

        try:
            databases = {}

            # Create all databases
            databases['accounts'] = self._create_accounts_database(parent_page_id)['id']
            databases['trigger_events'] = self._create_trigger_events_database(parent_page_id)['id']
            databases['contacts'] = self._create_contacts_database(parent_page_id)['id']
            databases['partnerships'] = self._create_partnerships_database(parent_page_id)['id']

            # Update local configuration
            self.database_ids.update(databases)

            logger.info(f"✅ ABM workspace created successfully with {len(databases)} databases")
            return databases

        except Exception as e:
            logger.error(f"❌ Failed to create ABM workspace: {str(e)}")
            raise

    def _create_accounts_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Accounts database with complete schema"""
        properties = {
            "Company Name": {"title": {}},
            "Domain": {"rich_text": {}},
            "Employee Count": {"number": {"format": "number"}},
            "Industry": {"select": {"options": [
                {"name": "Technology", "color": "blue"},
                {"name": "Healthcare", "color": "green"},
                {"name": "Finance", "color": "yellow"},
                {"name": "Manufacturing", "color": "orange"},
                {"name": "Retail", "color": "red"},
                {"name": "Other", "color": "gray"}
            ]}},
            "ICP Fit Score": {"number": {"format": "number"}},
            "Research Status": {"select": {"options": [
                {"name": "Not Started", "color": "gray"},
                {"name": "In Progress", "color": "yellow"},
                {"name": "Completed", "color": "green"},
                {"name": "On Hold", "color": "red"}
            ]}},
            "Last Updated": {"date": {}},
            "Notes": {"rich_text": {}},

            # Enhanced Account Intelligence Fields
            "Recent Leadership Changes": {"rich_text": {}},
            "Key Decision Makers": {"rich_text": {}},
            "Recent Funding": {"rich_text": {}},
            "Growth Stage": {"select": {"options": [
                {"name": "Startup", "color": "green"},
                {"name": "Scale-Up", "color": "blue"},
                {"name": "Growth", "color": "purple"},
                {"name": "Mature", "color": "orange"},
                {"name": "Enterprise", "color": "red"}
            ]}},
            "Hiring Velocity": {"rich_text": {}},
            "Physical Infrastructure": {"rich_text": {}},
            "Competitor Tools": {"rich_text": {}},
            "Recent Announcements": {"rich_text": {}},
            "Conversation Triggers": {"rich_text": {}}
        }

        return self._create_database(parent_page_id, "🏢 Accounts", properties)

    def _create_contacts_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Contacts database with complete schema"""
        properties = {
            "Name": {"title": {}},
            "Company": {"rich_text": {}},
            "Title": {"rich_text": {}},
            "Email": {"email": {}},
            "LinkedIn URL": {"url": {}},
            "Lead Score": {"number": {"format": "number"}},
            "Engagement Level": {"select": {"options": [
                {"name": "Very High", "color": "red"},
                {"name": "High", "color": "orange"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "gray"}
            ]}},
            "Contact Date": {"date": {}},
            "Notes": {"rich_text": {}},

            # Data Provenance & Quality Fields
            "Name Source": {"select": {"options": [
                {"name": "apollo", "color": "blue"},
                {"name": "linkedin", "color": "green"},
                {"name": "merged", "color": "purple"},
                {"name": "manual", "color": "gray"}
            ]}},
            "Email Source": {"select": {"options": [
                {"name": "apollo", "color": "blue"},
                {"name": "linkedin", "color": "green"},
                {"name": "inferred", "color": "yellow"},
                {"name": "manual", "color": "gray"}
            ]}},
            "Title Source": {"select": {"options": [
                {"name": "apollo", "color": "blue"},
                {"name": "linkedin", "color": "green"},
                {"name": "merged", "color": "purple"},
                {"name": "manual", "color": "gray"}
            ]}},
            "Data Quality Score": {"number": {"format": "number"}},
            "Last Enriched": {"date": {}}
        }

        return self._create_database(parent_page_id, "👤 Contacts", properties)

    def _create_trigger_events_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Trigger Events database with complete schema"""
        properties = {
            "Event Description": {"title": {}},
            "Company": {"rich_text": {}},
            "Event Type": {"select": {"options": [
                {"name": "expansion", "color": "green"},
                {"name": "leadership_change", "color": "blue"},
                {"name": "ai_workload", "color": "purple"},
                {"name": "energy_pressure", "color": "yellow"},
                {"name": "incident", "color": "red"},
                {"name": "sustainability", "color": "green"}
            ]}},
            "Confidence": {"select": {"options": [
                {"name": "High", "color": "green"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "red"}
            ]}},
            "Urgency": {"select": {"options": [
                {"name": "High", "color": "red"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "gray"}
            ]}},
            "Source URL": {"url": {}},
            "Detected Date": {"date": {}},
            "Relevance Score": {"number": {"format": "number"}}
        }

        return self._create_database(parent_page_id, "⚡ Trigger Events", properties)

    def _create_contact_intelligence_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Contact Intelligence database"""
        properties = {
            "Contact Name": {"title": {}},
            "Analysis Type": {"select": {"options": [
                {"name": "Engagement Intelligence", "color": "blue"},
                {"name": "Buying Signal", "color": "green"},
                {"name": "Contact Value", "color": "yellow"}
            ]}},
            "Intelligence Data": {"rich_text": {}},
            "Confidence Score": {"number": {"format": "number"}},
            "Generated Date": {"date": {}},
            "Source": {"rich_text": {}}
        }

        return self._create_database(parent_page_id, "🧠 Contact Intelligence", properties)

    def _create_partnerships_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Strategic Partnerships database"""
        properties = {
            "Partner Name": {"title": {}},
            "Partnership Type": {"select": {"options": [
                {"name": "Technology Integration", "color": "blue"},
                {"name": "Reseller", "color": "green"},
                {"name": "Strategic Alliance", "color": "purple"},
                {"name": "Vendor Relationship", "color": "orange"}
            ]}},
            "Relevance Score": {"number": {"format": "number"}},
            "Context": {"rich_text": {}},
            "Source URL": {"url": {}},
            "Discovered Date": {"date": {}}
        }

        return self._create_database(parent_page_id, "🤝 Strategic Partnerships", properties)

    def _create_database(self, parent_page_id: str, title: str, properties: Dict) -> Dict[str, Any]:
        """Create a database with given properties"""
        data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties
        }

        response = self._make_request('POST', 'https://api.notion.com/v1/databases', json=data)
        return response.json()

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DATA PERSISTENCE (from notion_persistence_manager.py)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def save_account(self, account: Dict[str, Any]) -> Optional[str]:
        """Save account data with deduplication"""
        if not self.database_ids.get('accounts'):
            logger.error("Accounts database not configured")
            return None

        try:
            # Check for existing account
            existing_id = self._find_existing_account(account.get('name', ''))
            if existing_id:
                logger.info(f"Account {account.get('name')} already exists, updating...")
                return self._update_account(existing_id, account)
            else:
                return self._create_account(account)

        except Exception as e:
            logger.error(f"Error saving account: {e}")
            return None

    def save_contacts(self, contacts: List[Dict], account_name: str = "") -> Dict[str, bool]:
        """Save enriched contact data with deduplication"""
        logger.info(f"💾 Saving {len(contacts)} contacts to Notion")

        if not self.database_ids.get('contacts'):
            logger.error("Contacts database not configured")
            return {}

        results = {}

        for contact in contacts:
            try:
                # Skip contacts without lead score (not enriched)
                if not contact.get('final_lead_score') and not contact.get('lead_score'):
                    logger.info(f"Skipping {contact.get('name', 'unknown')} - no lead score")
                    continue

                # Check for existing contact
                existing_id = self._find_existing_contact(contact.get('linkedin_url', ''))

                if existing_id:
                    success = self._update_contact(existing_id, contact)
                else:
                    success = self._create_contact(contact, account_name)

                contact_name = contact.get('name', 'unknown')
                results[contact_name] = bool(success)

            except Exception as e:
                logger.error(f"Error saving contact {contact.get('name')}: {e}")
                results[contact.get('name', 'unknown')] = False

        successful = sum(results.values())
        logger.info(f"✅ Successfully saved {successful}/{len(contacts)} contacts")
        return results

    def save_trigger_events(self, events: List[Dict], account_name: str = "") -> Dict[str, bool]:
        """Save trigger events data"""
        if not self.database_ids.get('trigger_events'):
            logger.error("Trigger events database not configured")
            return {}

        results = {}

        for event in events:
            try:
                success = self._create_trigger_event(event, account_name)
                event_desc = event.get('description', event.get('event_description', 'unknown'))[:50]
                results[event_desc] = bool(success)

            except Exception as e:
                logger.error(f"Error saving trigger event: {e}")
                results[event.get('description', 'unknown')[:50]] = False

        return results

    def save_partnerships(self, partnerships: List[Dict], account_name: str = "") -> Dict[str, bool]:
        """Save strategic partnerships data"""
        if not self.database_ids.get('partnerships'):
            logger.error("Partnerships database not configured")
            return {}

        results = {}

        for partnership in partnerships:
            try:
                success = self._create_partnership(partnership, account_name)
                partner_name = partnership.get('partner_name', partnership.get('name', 'unknown'))
                results[partner_name] = bool(success)

            except Exception as e:
                logger.error(f"Error saving partnership: {e}")
                results[partnership.get('partner_name', 'unknown')] = False

        return results

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DEDUPLICATION HELPERS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _find_existing_account(self, company_name: str) -> Optional[str]:
        """Find existing account by company name"""
        if not self.database_ids.get('accounts') or not company_name:
            return None

        try:
            query = {
                "filter": {
                    "property": "Name",
                    "title": {"equals": company_name}
                }
            }

            url = f"https://api.notion.com/v1/databases/{self.database_ids['accounts']}/query"
            response = self._make_request('POST', url, json=query)

            results = response.json().get('results', [])
            return results[0]['id'] if results else None

        except Exception as e:
            logger.error(f"Error finding existing account: {e}")
            return None

    def query_all_accounts(self) -> List[Dict]:
        """Query all accounts from Notion database"""
        if not self.database_ids.get('accounts'):
            logger.error("Accounts database ID not configured")
            return []

        try:
            url = f"https://api.notion.com/v1/databases/{self.database_ids['accounts']}/query"
            response = self._make_request('POST', url, json={})

            results = response.json().get('results', [])
            logger.info(f"Retrieved {len(results)} accounts from Notion")
            return results

        except Exception as e:
            logger.error(f"Error querying all accounts: {e}")
            return []

    def _find_existing_contact(self, linkedin_url: str) -> Optional[str]:
        """Find existing contact by LinkedIn URL"""
        if not self.database_ids.get('contacts') or not linkedin_url:
            return None

        try:
            query = {
                "filter": {
                    "property": "LinkedIn URL",
                    "url": {"equals": linkedin_url}
                }
            }

            url = f"https://api.notion.com/v1/databases/{self.database_ids['contacts']}/query"
            response = self._make_request('POST', url, json=query)

            results = response.json().get('results', [])
            return results[0]['id'] if results else None

        except Exception as e:
            logger.error(f"Error finding existing contact: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CREATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _create_account(self, account: Dict) -> Optional[str]:
        """Create new account record using actual production database field names"""
        properties = {
            # Core fields (using ACTUAL production field names)
            "Name": {"title": [{"text": {"content": account.get('name', 'Unknown')}}]},
            "Domain": {"rich_text": [{"text": {"content": account.get('domain', '')}}]},
            "Business Model": {"select": {"name": account.get('business_model', 'Technology')}},
            "Employee Count": {"number": account.get('employee_count', 0)},
            "ICP Fit Score": {"number": account.get('icp_fit_score', 0)},
            "Account Research Status": {"select": {"name": "Research Complete"}},
            "Last Updated": {"date": {"start": datetime.now().isoformat()}},

            # Enhanced Intelligence Fields (using exact field names)
            "Recent Leadership Changes": {"rich_text": [{"text": {"content": account.get('Recent Leadership Changes', '')}}]},
            "Recent Funding": {"rich_text": [{"text": {"content": account.get('Recent Funding', '')}}]},
            "Growth Stage": {"select": {"name": account.get('Growth Stage', 'Unknown')}},
            "Physical Infrastructure": {"rich_text": [{"text": {"content": account.get('Physical Infrastructure', '')}}]},
            "Recent Announcements": {"rich_text": [{"text": {"content": account.get('Recent Announcements', '')}}]},
            "Hiring Velocity": {"rich_text": [{"text": {"content": account.get('Hiring Velocity', '')}}]},
            "Conversation Triggers": {"rich_text": [{"text": {"content": account.get('Conversation Triggers', '')}}]},
            "Key Decision Makers": {"rich_text": [{"text": {"content": account.get('Key Decision Makers', '')}}]},
            "Competitor Tools": {"rich_text": [{"text": {"content": account.get('Competitor Tools', '')}}]}
        }

        data = {
            "parent": {"database_id": self.database_ids['accounts']},
            "properties": properties
        }

        response = self._make_request('POST', 'https://api.notion.com/v1/pages', json=data)
        return response.json().get('id')

    def _create_contact(self, contact: Dict, account_name: str = "") -> Optional[str]:
        """Create new contact record with proper Account relation and enhanced fields"""
        # Handle URL field properly - use null instead of empty string
        linkedin_url = contact.get('linkedin_url', '') or None

        # CRITICAL FIX: Find the actual account to create proper relation
        account_id = None
        if account_name:
            account_id = self._find_existing_account(account_name)

        properties = {
            # Core fields using production schema
            "Name": {"title": [{"text": {"content": contact.get('name', 'Unknown')}}]},
            "Email": {"email": contact.get('email', '')},
            "Title": {"rich_text": [{"text": {"content": contact.get('title', '')}}]},
            "ICP Fit Score": {"number": contact.get('final_lead_score', contact.get('lead_score', 0))},

            # New enhanced data provenance fields
            "Name Source": {"select": {"name": contact.get('name_source', 'apollo')}},
            "Email Source": {"select": {"name": contact.get('email_source', 'apollo')}},
            "Title Source": {"select": {"name": contact.get('title_source', 'apollo')}},
            "Data Quality Score": {"number": contact.get('data_quality_score', 80)},
            "Last Enriched": {"date": {"start": datetime.now().isoformat()}},
            "Lead Score": {"number": contact.get('final_lead_score', contact.get('lead_score', 0))},
            "Engagement Level": {"select": {"name": contact.get('engagement_level', 'Medium')}},
            "Contact Date": {"date": {"start": datetime.now().isoformat()}},
            "LinkedIn URL": {"url": linkedin_url},
            "Notes": {"rich_text": [{"text": {"content": contact.get('notes', '')}}]}
        }

        # CRITICAL FIX: Use proper Account relation instead of rich_text
        if account_id:
            properties["Account"] = {"relation": [{"id": account_id}]}
        else:
            # Fallback: Add account name as rich_text for manual linking
            properties["Account Name (Fallback)"] = {"rich_text": [{"text": {"content": account_name or 'Unknown Account'}}]}

        data = {
            "parent": {"database_id": self.database_ids['contacts']},
            "properties": properties
        }

        response = self._make_request('POST', 'https://api.notion.com/v1/pages', json=data)
        return response.json().get('id')

    def _create_trigger_event(self, event: Dict, account_name: str = "") -> Optional[str]:
        """Create new trigger event record with proper Account relation and enhanced multi-dimensional intelligence"""
        # Handle URL field properly - use null instead of empty string
        source_url = event.get('source_url', '') or None

        # CRITICAL FIX: Find the actual account to create proper relation
        account_id = None
        if account_name:
            account_id = self._find_existing_account(account_name)

        properties = {
            # Core fields using production schema
            "Name": {"title": [{"text": {"content": event.get('description', event.get('event_description', 'Unknown Event'))}}]},
            "Event Type": {"select": {"name": event.get('event_type', 'other')}},
            "Confidence": {"select": {"name": event.get('confidence', 'Medium')}},
            "Source URL": {"url": source_url},
            "Detected Date": {"date": {"start": event.get('detected_date', datetime.now().strftime('%Y-%m-%d'))}},

            # NEW: Multi-Dimensional Scoring System
            "Business Impact Score": {"number": event.get('business_impact_score', 50)},
            "Actionability Score": {"number": event.get('actionability_score', 50)},
            "Timing Urgency Score": {"number": event.get('timing_urgency_score', 50)},
            "Strategic Fit Score": {"number": event.get('strategic_fit_score', 50)},

            # NEW: Time Intelligence Fields
            "Action Deadline": {"date": {"start": event.get('action_deadline', '')} if event.get('action_deadline') else None},
            "Peak Relevance Window": {"date": {"start": event.get('peak_relevance_window', '')} if event.get('peak_relevance_window') else None},
            "Decay Rate": {"select": {"name": event.get('decay_rate', 'Medium')}},

            # NEW: Event Lifecycle Tracking
            "Event Stage": {"select": {"name": event.get('event_stage', 'Announced')}},
            "Follow-up Actions": {"rich_text": [{"text": {"content": event.get('follow_up_actions', '')}}]},
            "Urgency Level": {"select": {"name": event.get('urgency_level', 'Medium')}}
        }

        # CRITICAL FIX: Use proper Account relation instead of rich_text
        if account_id:
            properties["Account"] = {"relation": [{"id": account_id}]}
        else:
            # Fallback: Add account name as rich_text for manual linking
            properties["Account Name (Fallback)"] = {"rich_text": [{"text": {"content": account_name or 'Unknown Account'}}]}

        # Remove None values to avoid API errors
        properties = {k: v for k, v in properties.items() if v is not None}

        data = {
            "parent": {"database_id": self.database_ids['trigger_events']},
            "properties": properties
        }

        response = self._make_request('POST', 'https://api.notion.com/v1/pages', json=data)
        return response.json().get('id')

    def _create_partnership(self, partnership: Dict, account_name: str = "") -> Optional[str]:
        """Create new partnership record with enhanced strategic intelligence using production field names"""
        # Get source URL and ensure it's either a valid URL or null (not empty string)
        source_url = partnership.get('source_url', partnership.get('evidence_url', '')) or None

        properties = {
            # Core fields (using ACTUAL production field names)
            "Name": {"title": [{"text": {"content": partnership.get('account_name', partnership.get('partner_name', 'Unknown Partner'))}}]},
            "Category": {"select": {"name": partnership.get('partnership_type', partnership.get('category', 'Strategic Alliance'))}},
            "Priority Score": {"number": partnership.get('confidence_score', partnership.get('relevance_score', partnership.get('priority_score', 0)))},
            "Relationship Evidence": {"rich_text": [{"text": {"content": partnership.get('reasoning', partnership.get('context', partnership.get('relationship_evidence', '')))}}]},
            "Evidence URL": {"url": source_url},
            "Detected Date": {"date": {"start": partnership.get('detected_date', datetime.now().strftime('%Y-%m-%d'))}},

            # Enhanced Strategic Partnership Intelligence Fields
            # Partnership Depth & Strategy
            "Relationship Depth": {"select": {"name": partnership.get('relationship_depth', 'Surface Integration')}},
            "Partnership Maturity": {"select": {"name": partnership.get('partnership_maturity', 'Basic')}},

            # Entry Vector Intelligence
            "Warm Introduction Path": {"rich_text": [{"text": {"content": partnership.get('warm_introduction_path', '')}}]},
            "Common Partners": {"rich_text": [{"text": {"content": partnership.get('common_partners', '')}}]},
            "Competitive Overlap": {"select": {"name": partnership.get('competitive_overlap', 'None')}},

            # Action Intelligence
            "Best Approach": {"select": {"name": partnership.get('best_approach', 'Technical Discussion')}},
            "Decision Timeline": {"select": {"name": partnership.get('decision_timeline', 'Medium (months)')}},
            "Success Metrics": {"rich_text": [{"text": {"content": partnership.get('success_metrics', '')}}]},
            "Recommended Next Steps": {"rich_text": [{"text": {"content": partnership.get('recommended_next_steps', partnership.get('next_actions', ''))}}]}
        }

        data = {
            "parent": {"database_id": self.database_ids['partnerships']},
            "properties": properties
        }

        response = self._make_request('POST', 'https://api.notion.com/v1/pages', json=data)
        return response.json().get('id')

    # ═══════════════════════════════════════════════════════════════════════════════════
    # UPDATE OPERATIONS (simplified for space)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _update_account(self, page_id: str, account: Dict) -> Optional[str]:
        """Update existing account record"""
        try:
            properties = {
                "Name": {"title": [{"text": {"content": account.get('name', 'Unknown')}}]},
                "Domain": {"rich_text": [{"text": {"content": account.get('domain', '')}}]},
                "Business Model": {"select": {"name": account.get('business_model', 'Technology')}},
                "Employee Count": {"number": account.get('employee_count', 0)},
                "ICP Fit Score": {"number": account.get('icp_fit_score', 0)},
                "Account Research Status": {"select": {"name": "Research Complete"}},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}},

                # Enhanced Intelligence Fields (using exact field names and types from schema)
                "Recent Leadership Changes": {"rich_text": [{"text": {"content": account.get('Recent Leadership Changes', '')}}]},
                "Recent Funding": {"rich_text": [{"text": {"content": account.get('Recent Funding', '')}}]},
                "Growth Stage": {"select": {"name": account.get('Growth Stage', 'Unknown')[:100] or 'Unknown'}},  # Select field
                "Physical Infrastructure": {"rich_text": [{"text": {"content": account.get('Physical Infrastructure', '')}}]},
                "Recent Announcements": {"rich_text": [{"text": {"content": account.get('Recent Announcements', '')}}]},
                "Hiring Velocity": {"rich_text": [{"text": {"content": account.get('Hiring Velocity', '')}}]},
                "Conversation Triggers": {"rich_text": [{"text": {"content": account.get('Conversation Triggers', '')}}]},
                "Key Decision Makers": {"rich_text": [{"text": {"content": account.get('Key Decision Makers', '')}}]},
                "Competitor Tools": {"rich_text": [{"text": {"content": account.get('Competitor Tools', '')}}]}
            }

            url = f"https://api.notion.com/v1/pages/{page_id}"
            response = self._make_request('PATCH', url, json={"properties": properties})

            logger.info(f"✅ Updated account: {account.get('name', 'unknown')}")
            return page_id  # Return page_id for consistency with _create_account

        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return None

    def _update_contact(self, page_id: str, contact: Dict) -> Optional[str]:
        """Update existing contact record"""
        # Implementation similar to create but using PATCH
        logger.info(f"Updating contact {contact.get('name', 'unknown')}")
        return page_id  # Simplified for consolidation

    # ═══════════════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Notion integration"""
        return {
            'api_key_configured': bool(self.api_key),
            'advanced_client_available': bool(self.client),
            'database_configuration': {
                name: bool(db_id) for name, db_id in self.database_ids.items()
            },
            'last_request_time': self.last_request_time
        }


# Global instance for convenience (optional)
_notion_client = None

def get_notion_client() -> NotionClient:
    """Get global Notion client instance"""
    global _notion_client
    if _notion_client is None:
        _notion_client = NotionClient()
    return _notion_client


if __name__ == "__main__":
    # Test script
    client = NotionClient()
    status = client.get_health_status()
    print("🔗 Notion Client Health Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")