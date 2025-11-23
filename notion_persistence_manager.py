#!/usr/bin/env python3
"""
Notion Persistence Manager
Saves enriched LinkedIn data and ABM research results to Notion databases
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class NotionPersistenceManager:
    """
    Manages persistence of enriched ABM data to Notion databases
    Handles contacts, accounts, trigger events, and research intelligence
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Load configuration
        self.load_config()

        # Notion API setup - use the API key that has database access
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        if not self.notion_api_key:
            raise ValueError("NOTION_API_KEY not found in environment variables")

        self.headers = {
            'Authorization': f'Bearer {self.notion_api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 0.5  # 500ms between requests

    def setup_logging(self):
        """Setup logging for persistence operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('notion_persistence.log'),
                logging.StreamHandler()
            ]
        )

    def load_config(self):
        """Load Notion database IDs from environment or config"""
        self.database_ids = {
            'accounts': os.getenv('NOTION_ACCOUNTS_DB_ID'),
            'contacts': os.getenv('NOTION_CONTACTS_DB_ID'),
            'trigger_events': os.getenv('NOTION_TRIGGER_EVENTS_DB_ID'),
            'partnerships': os.getenv('NOTION_PARTNERSHIPS_DB_ID'),
            'intelligence': os.getenv('NOTION_INTELLIGENCE_DB_ID')
        }

        # Check for missing database IDs
        missing_ids = [name for name, db_id in self.database_ids.items() if not db_id]
        if missing_ids:
            self.logger.warning(f"Missing Notion database IDs: {missing_ids}")
            self.logger.warning("Some persistence features will be disabled")

    def save_enriched_contacts(self, contacts: List[Dict], account_name: str = None) -> Dict[str, bool]:
        """
        Save enriched contact data to Notion contacts database
        Includes LinkedIn enrichment data and engagement scores
        """
        self.logger.info(f"💾 Saving {len(contacts)} enriched contacts to Notion")

        if not self.database_ids.get('contacts'):
            self.logger.error("Contacts database ID not configured")
            return {}

        results = {}
        processed_contacts = []  # Track contacts actually processed

        for contact in contacts:
            contact_name = contact.get('name', 'Unknown')

            try:
                # Only save contacts that have been enriched
                if not contact.get('final_lead_score'):
                    self.logger.info(f"   ⏭️ Skipped {contact_name}: No final_lead_score (not enriched)")
                    results[contact_name] = None  # Mark as skipped, not failed
                    continue

                processed_contacts.append(contact)
                contact_data = self._format_contact_for_notion(contact, account_name)

                # Check if contact already exists
                existing_contact = self._find_existing_contact(contact)

                if existing_contact:
                    # Update existing contact
                    success = self._update_notion_contact(existing_contact['id'], contact_data)
                    results[contact_name] = success
                    if success:
                        self.logger.info(f"   ✅ Updated: {contact_name}")
                    else:
                        self.logger.error(f"   ❌ Failed to update: {contact_name}")
                else:
                    # Create new contact
                    success = self._create_notion_contact(contact_data)
                    results[contact_name] = success
                    if success:
                        self.logger.info(f"   ✅ Created: {contact_name}")
                    else:
                        self.logger.error(f"   ❌ Failed to create: {contact_name}")

                # Rate limiting
                self._apply_rate_limit()

            except Exception as e:
                self.logger.error(f"   ❌ Failed to save {contact_name}: {e}")
                results[contact_name] = False

        # Count only processed contacts
        success_count = sum(1 for success in results.values() if success is True)
        processed_count = len(processed_contacts)
        skipped_count = len(contacts) - processed_count

        self.logger.info(f"✅ Successfully saved {success_count}/{processed_count} processed contacts ({skipped_count} skipped)")

        return results

    def save_trigger_events(self, events: List[Dict], account_name: str) -> Dict[str, bool]:
        """Save trigger events to Notion with enriched analysis"""
        self.logger.info(f"💾 Saving {len(events)} trigger events for {account_name}")

        if not self.database_ids.get('trigger_events'):
            self.logger.error("Trigger events database ID not configured")
            return {}

        results = {}

        for event in events:
            try:
                event_data = self._format_event_for_notion(event, account_name)

                # Create new trigger event
                success = self._create_notion_event(event_data)
                event_key = f"{event.get('event_type', 'Unknown')} - {account_name}"
                results[event_key] = success

                if success:
                    self.logger.info(f"   ✓ Saved event: {event.get('event_type')}")

                self._apply_rate_limit()

            except Exception as e:
                self.logger.error(f"   ❌ Failed to save event: {e}")
                results[f"Event_{len(results)}"] = False

        return results

    def save_account_intelligence(self, account_data: Dict, research_summary: Dict) -> bool:
        """Save account-level intelligence and ICP scoring"""
        self.logger.info(f"💾 Saving account intelligence for {account_data.get('name', 'Unknown')}")

        if not self.database_ids.get('accounts'):
            self.logger.error("Accounts database ID not configured")
            return False

        try:
            formatted_data = self._format_account_for_notion(account_data, research_summary)

            # Check if account already exists
            existing_account = self._find_existing_account(account_data.get('name', ''))

            if existing_account:
                success = self._update_notion_account(existing_account['id'], formatted_data)
                self.logger.info(f"   ✓ Updated account: {account_data.get('name')}")
            else:
                success = self._create_notion_account(formatted_data)
                self.logger.info(f"   ✓ Created account: {account_data.get('name')}")

            return success

        except Exception as e:
            self.logger.error(f"   ❌ Failed to save account intelligence: {e}")
            return False

    def _format_contact_for_notion(self, contact: Dict, account_name: str = None) -> Dict:
        """Format enriched contact data for Notion API using existing schema"""
        properties = {
            'Name': {
                'title': [{'text': {'content': contact.get('name', 'Unknown')}}]
            },
            'Title': {
                'rich_text': [{'text': {'content': contact.get('title', '')}}]
            },
            'Email': {
                'email': contact.get('email') if contact.get('email') else None
            },
            'LinkedIn URL': {
                'url': contact.get('linkedin_url') if contact.get('linkedin_url') else None
            },
            'Final Lead Score': {
                'number': float(contact.get('final_lead_score', 0))
            },
            'ICP Fit Score': {
                'number': float(contact.get('icp_fit_score', 0))
            },
            'Buying Power Score': {
                'number': float(contact.get('buying_power_score', 0))
            },
            'Engagement Potential Score': {  # Maps to existing field
                'number': float(contact.get('engagement_potential_score', 0))
            }
        }

        # Map LinkedIn enrichment to existing fields
        if contact.get('content_themes'):
            themes_text = ', '.join(contact.get('content_themes', []))
            properties['Content Themes They Value'] = {  # Maps to existing field
                'rich_text': [{'text': {'content': themes_text[:2000]}}]
            }

        if contact.get('connection_pathways'):
            properties['Connection Pathways'] = {  # Existing field
                'rich_text': [{'text': {'content': contact.get('connection_pathways', '')[:2000]}}]
            }

        # Map responsibility keywords to problems they own (conceptually related)
        if contact.get('responsibility_keywords'):
            keywords_text = ', '.join(contact.get('responsibility_keywords', []))
            problems_text = f"Responsible for: {keywords_text}"
            properties['Problems They Likely Own'] = {  # Maps to existing field
                'rich_text': [{'text': {'content': problems_text[:2000]}}]
            }

        # Set research status
        properties['Research Status'] = {
            'select': {'name': contact.get('research_status', 'Analyzed')}
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        return {'properties': properties}

    def _format_event_for_notion(self, event: Dict, account_name: str) -> Dict:
        """Format trigger event for Notion API"""
        properties = {
            'Account': {
                'title': [{'text': {'content': account_name}}]
            },
            'Event Type': {
                'select': {'name': event.get('event_type', 'Unknown')}
            },
            'Description': {
                'rich_text': [{'text': {'content': event.get('description', '')[:2000]}}]
            },
            'Confidence': {
                'number': self._convert_confidence_to_number(event.get('confidence', 0))
            },
            'Relevance Score': {
                'number': float(event.get('relevance_score', 0))
            },
            'Urgency': {
                'select': {'name': event.get('urgency', 'Medium')}
            },
            'Source URL': {
                'url': event.get('source_url') if event.get('source_url') else None
            },
            'Date Detected': {
                'date': {'start': datetime.now().isoformat()}
            }
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        return {'properties': properties}

    def _format_account_for_notion(self, account_data: Dict, research_summary: Dict) -> Dict:
        """Format account intelligence for Notion API"""
        properties = {
            'Company Name': {
                'title': [{'text': {'content': account_data.get('name', 'Unknown')}}]
            },
            'Domain': {
                'rich_text': [{'text': {'content': account_data.get('domain', '')}}]
            },
            'ICP Fit Score': {
                'number': float(account_data.get('icp_fit_score', 0))
            },
            'Company Type': {
                'select': {'name': account_data.get('company_type', 'Unknown')}
            },
            'Research Status': {
                'select': {'name': 'Analyzed'}
            },
            'Last Research Date': {
                'date': {'start': datetime.now().isoformat()}
            }
        }

        # Add research summary metrics
        if research_summary:
            if research_summary.get('total_contacts'):
                properties['Total Contacts'] = {
                    'number': int(research_summary.get('total_contacts', 0))
                }

            if research_summary.get('high_priority_contacts'):
                properties['High Priority Contacts'] = {
                    'number': int(research_summary.get('high_priority_contacts', 0))
                }

            if research_summary.get('trigger_events_count'):
                properties['Trigger Events'] = {
                    'number': int(research_summary.get('trigger_events_count', 0))
                }

        return {'properties': properties}

    def _create_notion_contact(self, contact_data: Dict) -> bool:
        """Create new contact in Notion"""
        try:
            url = 'https://api.notion.com/v1/pages'
            payload = {
                'parent': {'database_id': self.database_ids['contacts']},
                **contact_data
            }

            response = requests.post(url, headers=self.headers, json=payload)
            success = response.status_code in [200, 201]  # Notion can return 200 or 201 for successful creation
            if not success:
                self.logger.error(f"Notion API error creating contact: {response.status_code} - {response.text}")
            return success

        except Exception as e:
            self.logger.error(f"Error creating contact: {e}")
            return False

    def _update_notion_contact(self, contact_id: str, contact_data: Dict) -> bool:
        """Update existing contact in Notion"""
        try:
            url = f'https://api.notion.com/v1/pages/{contact_id}'
            response = requests.patch(url, headers=self.headers, json=contact_data)
            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error updating contact: {e}")
            return False

    def _create_notion_event(self, event_data: Dict) -> bool:
        """Create trigger event in Notion"""
        try:
            url = 'https://api.notion.com/v1/pages'
            payload = {
                'parent': {'database_id': self.database_ids['trigger_events']},
                **event_data
            }

            response = requests.post(url, headers=self.headers, json=payload)
            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error creating event: {e}")
            return False

    def _create_notion_account(self, account_data: Dict) -> bool:
        """Create account in Notion"""
        try:
            url = 'https://api.notion.com/v1/pages'
            payload = {
                'parent': {'database_id': self.database_ids['accounts']},
                **account_data
            }

            response = requests.post(url, headers=self.headers, json=payload)
            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error creating account: {e}")
            return False

    def _update_notion_account(self, account_id: str, account_data: Dict) -> bool:
        """Update existing account in Notion"""
        try:
            url = f'https://api.notion.com/v1/pages/{account_id}'
            response = requests.patch(url, headers=self.headers, json=account_data)
            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"Error updating account: {e}")
            return False

    def _find_existing_contact(self, contact: Dict) -> Optional[Dict]:
        """Find existing contact in Notion by name or email"""
        try:
            url = f'https://api.notion.com/v1/databases/{self.database_ids["contacts"]}/query'

            # Search by name first
            filter_data = {
                'filter': {
                    'property': 'Name',
                    'title': {
                        'equals': contact.get('name', '')
                    }
                }
            }

            response = requests.post(url, headers=self.headers, json=filter_data)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]

        except Exception as e:
            self.logger.warning(f"Error searching for existing contact: {e}")

        return None

    def _find_existing_account(self, company_name: str) -> Optional[Dict]:
        """Find existing account in Notion by company name"""
        try:
            url = f'https://api.notion.com/v1/databases/{self.database_ids["accounts"]}/query'

            filter_data = {
                'filter': {
                    'property': 'Company Name',
                    'title': {
                        'equals': company_name
                    }
                }
            }

            response = requests.post(url, headers=self.headers, json=filter_data)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]

        except Exception as e:
            self.logger.warning(f"Error searching for existing account: {e}")

        return None

    def _apply_rate_limit(self):
        """Apply rate limiting to avoid Notion API limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def save_complete_research(self, research_results: Dict) -> Dict[str, Any]:
        """
        Save complete ABM research results to Notion
        Main entry point for persisting all research data
        """
        self.logger.info("🗄️ Saving complete ABM research to Notion databases")

        persistence_results = {
            'contacts_saved': 0,
            'events_saved': 0,
            'account_updated': False,
            'errors': []
        }

        try:
            account_name = research_results.get('account', {}).get('name', 'Unknown')

            # Save enriched contacts
            if research_results.get('contacts'):
                contact_results = self.save_enriched_contacts(
                    research_results['contacts'],
                    account_name
                )
                persistence_results['contacts_saved'] = sum(1 for success in contact_results.values() if success)

            # Save trigger events
            if research_results.get('events'):
                event_results = self.save_trigger_events(
                    research_results['events'],
                    account_name
                )
                persistence_results['events_saved'] = sum(1 for success in event_results.values() if success)

            # Save account intelligence
            if research_results.get('account'):
                persistence_results['account_updated'] = self.save_account_intelligence(
                    research_results['account'],
                    research_results.get('research_summary', {})
                )

            self.logger.info(f"✅ Research persistence complete:")
            self.logger.info(f"   📋 Contacts: {persistence_results['contacts_saved']} saved")
            self.logger.info(f"   🎯 Events: {persistence_results['events_saved']} saved")
            self.logger.info(f"   🏢 Account: {'Updated' if persistence_results['account_updated'] else 'Not updated'}")

        except Exception as e:
            error_msg = f"Error in complete research persistence: {e}"
            self.logger.error(error_msg)
            persistence_results['errors'].append(error_msg)

        return persistence_results

    def _convert_confidence_to_number(self, confidence) -> float:
        """Convert confidence from text or number to numeric value"""
        if isinstance(confidence, (int, float)):
            return float(confidence)

        # Convert text confidence to numeric scale (0-100)
        confidence_str = str(confidence).lower()
        confidence_mapping = {
            'high': 85.0,
            'medium': 65.0,
            'low': 35.0,
            'very high': 95.0,
            'very low': 15.0
        }

        return confidence_mapping.get(confidence_str, 50.0)  # Default to medium

# Export for use by ABM system
notion_persistence_manager = NotionPersistenceManager()