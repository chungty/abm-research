#!/usr/bin/env python3
"""
Dashboard Data Service
Real-time data integration between Notion databases and the ABM dashboard
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import Flask, jsonify, render_template_string, send_file
from flask_cors import CORS
import threading
from pathlib import Path

from abm_config import config
from config.settings import (
    NOTION_ACCOUNTS_DB_ID,
    NOTION_CONTACTS_DB_ID,
    NOTION_TRIGGER_EVENTS_DB_ID,
    NOTION_PARTNERSHIPS_DB_ID
)
from lead_scoring_engine import scoring_engine
from enhanced_buying_signals_analyzer import enhanced_buying_signals_analyzer
from contact_value_analyzer import contact_value_analyzer

class NotionDataService:
    """Service to fetch and transform Notion data for dashboard"""

    def __init__(self):
        # Use abm_config for consistent API key management
        from abm_config import config as abm_config
        self.headers = abm_config.get_notion_headers()

        # Use environment variables for database IDs - no more hardcoded values!
        self.database_ids = {
            'accounts': NOTION_ACCOUNTS_DB_ID,
            'contacts': NOTION_CONTACTS_DB_ID,
            'trigger_events': NOTION_TRIGGER_EVENTS_DB_ID,
            'partnerships': NOTION_PARTNERSHIPS_DB_ID
        }

        # Validate that database IDs are configured
        missing_db_ids = [key for key, value in self.database_ids.items() if not value]
        if missing_db_ids:
            raise ValueError(f"Missing database ID environment variables: {missing_db_ids}. "
                           f"Please set NOTION_*_DB_ID environment variables in .env file.")

        self.cache = {}
        self.cache_timestamp = {}

    def get_cached_or_fetch(self, key: str, fetch_function, cache_duration: int = 300):
        """Get cached data or fetch fresh data"""
        now = time.time()

        if (key in self.cache and
            key in self.cache_timestamp and
            now - self.cache_timestamp[key] < cache_duration):
            return self.cache[key]

        data = fetch_function()
        self.cache[key] = data
        self.cache_timestamp[key] = now
        return data

    def fetch_accounts(self) -> List[Dict]:
        """Fetch account data from Notion"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_ids['accounts']}/query"

            payload = {
                "page_size": 100,
                "sorts": [
                    {
                        "property": "ICP Fit Score",
                        "direction": "descending"
                    }
                ]
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                accounts = []

                for result in data.get('results', []):
                    props = result.get('properties', {})

                    account = {
                        'id': result['id'],
                        'name': self._extract_title(props.get('Name', {})),
                        'domain': self._extract_rich_text(props.get('Domain', {})),
                        'icp_fit_score': self._extract_number(props.get('ICP Fit Score', {})),
                        'business_model': self._extract_select(props.get('Business Model', {})),
                        'employee_count': self._extract_number(props.get('Employee Count', {})),
                        'research_status': self._extract_select(props.get('Account Research Status', {})),
                        'last_updated': self._extract_date(props.get('Last Updated', {})),
                        'created_time': result.get('created_time')
                    }
                    accounts.append(account)

                return accounts
            else:
                print(f"Error fetching accounts: {response.text}")
                return []

        except Exception as e:
            print(f"Error in fetch_accounts: {e}")
            return []

    def fetch_contacts(self, account_id: str = None) -> List[Dict]:
        """Fetch contact data from Notion"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_ids['contacts']}/query"

            payload = {
                "page_size": 100,
                "sorts": [
                    {
                        "property": "ICP Fit Score",
                        "direction": "descending"
                    }
                ]
            }

            # Filter by account if specified
            if account_id:
                payload["filter"] = {
                    "property": "Account",
                    "relation": {
                        "contains": account_id
                    }
                }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                contacts = []

                for result in data.get('results', []):
                    props = result.get('properties', {})

                    # Extract Account relation to get company name
                    account_ids = self._extract_relation(props.get('Account', {}))
                    company_name = ''
                    if account_ids:
                        # Get the first account (primary account)
                        company_name = self._get_account_name_by_id(account_ids[0])

                    contact_name = self._extract_title(props.get('Name', {}))

                    contact = {
                        'id': result['id'],
                        'name': contact_name,
                        'full_name': contact_name,  # Frontend compatibility
                        'title': self._extract_rich_text(props.get('Title', {})),
                        'company_name': company_name,  # Critical for account plan modal
                        'email': self._extract_email(props.get('Email', {})),
                        'phone_number': self._extract_phone(props.get('Phone Number', {})),
                        'linkedin_url': self._extract_url(props.get('LinkedIn URL', {})),
                        'icp_fit_score': self._extract_number(props.get('ICP Fit Score', {})),
                        'buying_power_score': self._extract_number(props.get('Buying Power Score', {})),
                        'engagement_potential_score': self._extract_number(props.get('Engagement Potential Score', {})),
                        'buying_committee_role': self._extract_select(props.get('Buying committee role', {})),
                        'linkedin_activity_level': self._extract_select(props.get('LinkedIn Activity Level', {})),
                        'network_quality': self._extract_select(props.get('Network Quality', {})),
                        'content_themes': self._extract_multi_select(props.get('Content themes they value', {})),
                        'problems_owned': self._extract_multi_select(props.get('Problems they likely own', {})),
                        'research_status': self._extract_select(props.get('Research status', {})),
                        'connection_pathways': self._extract_rich_text(props.get('Connection pathways', {})),
                        'value_add_ideas': self._extract_rich_text(props.get('Value-add ideas', {})),
                        'created_time': result.get('created_time')
                    }

                    # Calculate enhanced lead score with organizational hierarchy
                    enhanced_score, scoring_breakdown = scoring_engine.calculate_enhanced_lead_score(contact)
                    contact['lead_score'] = enhanced_score
                    contact['final_lead_score'] = enhanced_score  # Frontend compatibility
                    contact['scoring_breakdown'] = scoring_breakdown

                    contacts.append(contact)

                return sorted(contacts, key=lambda x: x.get('lead_score', 0), reverse=True)
            else:
                print(f"Error fetching contacts: {response.text}")
                return []

        except Exception as e:
            print(f"Error in fetch_contacts: {e}")
            return []

    def fetch_trigger_events(self, account_id: str = None) -> List[Dict]:
        """Fetch trigger events from Notion"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_ids['trigger_events']}/query"

            payload = {
                "page_size": 100,
                "sorts": [
                    {
                        "property": "Relevance Score",
                        "direction": "descending"
                    }
                ]
            }

            # Filter by account if specified
            if account_id:
                payload["filter"] = {
                    "property": "Account",
                    "relation": {
                        "contains": account_id
                    }
                }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                events = []

                for result in data.get('results', []):
                    props = result.get('properties', {})

                    # Extract Account relation to get company name
                    account_ids = self._extract_relation(props.get('Account', {}))
                    company_name = ''
                    if account_ids:
                        # Get the first account (primary account)
                        company_name = self._get_account_name_by_id(account_ids[0])

                    event_description = self._extract_title(props.get('Name', {}))

                    event = {
                        'id': result['id'],
                        'description': event_description,
                        'event_description': event_description,  # Frontend compatibility
                        'company_name': company_name,  # Critical for account correlation
                        'event_type': self._extract_select(props.get('Event Type', {})),
                        'confidence_score': self._extract_number(props.get('Confidence Score', {})),
                        'relevance_score': self._extract_number(props.get('Relevance Score', {})),
                        'source_url': self._extract_url(props.get('Source URL', {})),
                        'source_type': self._extract_select(props.get('Source Type', {})),
                        'detected_date': self._extract_date(props.get('Detected Date', {})),
                        'timestamp': self._extract_date(props.get('Detected Date', {})) or result.get('created_time', ''),  # Frontend compatibility
                        'created_time': result.get('created_time'),
                        'urgency_level': self._calculate_urgency(
                            self._extract_number(props.get('Confidence Score', {})),
                            self._extract_number(props.get('Relevance Score', {}))
                        )
                    }
                    events.append(event)

                return events
            else:
                print(f"Error fetching trigger events: {response.text}")
                return []

        except Exception as e:
            print(f"Error in fetch_trigger_events: {e}")
            return []

    def fetch_partnerships(self) -> List[Dict]:
        """Fetch partnerships data from Notion"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_ids['partnerships']}/query"

            payload = {
                "page_size": 100,
                "sorts": [
                    {
                        "property": "Name",
                        "direction": "ascending"
                    }
                ]
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                partnerships = []

                for result in data.get('results', []):
                    props = result.get('properties', {})

                    # Extract Account relation to get target company
                    account_ids = self._extract_relation(props.get('Account', {}))
                    target_company = ''
                    if account_ids:
                        # Get the first account (target company)
                        target_company = self._get_account_name_by_id(account_ids[0])

                    partnership = {
                        'id': result['id'],
                        'name': self._extract_title(props.get('Name', {})),
                        'partner_name': self._extract_rich_text(props.get('Partner Name', {})),
                        'target_company': target_company,  # Critical for account correlation
                        'partnership_type': self._extract_select(props.get('Partnership Type', {})),
                        'status': self._extract_select(props.get('Status', {})),
                        'strategic_value': self._extract_select(props.get('Strategic Value', {})),
                        'description': self._extract_rich_text(props.get('Description', {})),
                        'verdigris_relevance': self._extract_rich_text(props.get('Verdigris Relevance', {})),
                        'created_time': result.get('created_time')
                    }
                    partnerships.append(partnership)

                return partnerships
            else:
                print(f"Error fetching partnerships: {response.text}")
                return []

        except Exception as e:
            print(f"Error in fetch_partnerships: {e}")
            return []

    def fetch_enhanced_trigger_events(self, account_id: str = None) -> List[Dict]:
        """Fetch trigger events with enhanced analysis including trend analysis and priority scoring"""
        try:
            print(f"🔍 Fetching enhanced buying signals with trend analysis...")

            # First fetch regular trigger events
            basic_events = self.fetch_trigger_events(account_id)

            if not basic_events:
                return []

            # Get account data for enhanced analysis
            account_data = None
            if account_id:
                accounts = self.fetch_accounts()
                account_data = next((acc for acc in accounts if acc.get('id') == account_id), None)

            # Use enhanced analyzer to process the events
            enhanced_signals = enhanced_buying_signals_analyzer.analyze_buying_signals(
                basic_events, account_data
            )

            # Convert to dashboard-friendly format
            dashboard_signals = enhanced_buying_signals_analyzer.convert_to_dashboard_format(enhanced_signals)

            print(f"✅ Enhanced {len(dashboard_signals)} buying signals with trend analysis")
            return dashboard_signals

        except Exception as e:
            print(f"⚠️ Error in enhanced trigger events analysis: {e}")
            # Fallback to basic events if enhancement fails
            return self.fetch_trigger_events(account_id)

    def fetch_contact_value_analysis(self, account_id: str = None) -> Dict:
        """Fetch contact value analysis with high-ICP contacts and role patterns"""
        try:
            print(f"👥 Fetching contact value analysis...")

            # Get contacts
            contacts = self.fetch_contacts(account_id)
            if not contacts:
                return {'error': 'No contacts found for analysis'}

            # Get account data for context
            account_data = None
            if account_id:
                accounts = self.fetch_accounts()
                account_data = next((acc for acc in accounts if acc.get('id') == account_id), None)
            elif contacts:
                # Use company name from first contact to find account
                company_name = contacts[0].get('company_name')
                if company_name:
                    accounts = self.fetch_accounts()
                    account_data = next((acc for acc in accounts if acc.get('name') == company_name), None)

            # Run contact value analysis
            analysis_result = contact_value_analyzer.analyze_contact_value(contacts, account_data)

            # Convert to dashboard format
            dashboard_data = contact_value_analyzer.convert_to_dashboard_format(analysis_result)

            print(f"✅ Contact value analysis complete for {len(contacts)} contacts")
            return dashboard_data

        except Exception as e:
            print(f"⚠️ Error in contact value analysis: {e}")
            return {'error': str(e)}

    def _calculate_urgency(self, confidence: float, relevance: float) -> str:
        """Calculate urgency level based on confidence and relevance"""
        if not confidence or not relevance:
            return 'Low'

        combined_score = (confidence + relevance) / 2

        if combined_score >= 80:
            return 'High'
        elif combined_score >= 60:
            return 'Medium'
        else:
            return 'Low'

    def _extract_title(self, prop: Dict) -> str:
        """Extract title from Notion property"""
        if not prop or prop.get('type') != 'title':
            return ''

        title_list = prop.get('title', [])
        if title_list:
            return ''.join([item.get('plain_text', '') for item in title_list])
        return ''

    def _extract_rich_text(self, prop: Dict) -> str:
        """Extract rich text from Notion property"""
        if not prop or prop.get('type') != 'rich_text':
            return ''

        rich_text_list = prop.get('rich_text', [])
        if rich_text_list:
            return ''.join([item.get('plain_text', '') for item in rich_text_list])
        return ''

    def _extract_number(self, prop: Dict) -> Optional[float]:
        """Extract number from Notion property"""
        if not prop or prop.get('type') != 'number':
            return None
        return prop.get('number')

    def _extract_select(self, prop: Dict) -> str:
        """Extract select value from Notion property"""
        if not prop or prop.get('type') != 'select':
            return ''

        select_obj = prop.get('select')
        if select_obj:
            return select_obj.get('name', '')
        return ''

    def _extract_multi_select(self, prop: Dict) -> List[str]:
        """Extract multi-select values from Notion property"""
        if not prop or prop.get('type') != 'multi_select':
            return []

        multi_select_list = prop.get('multi_select', [])
        return [item.get('name', '') for item in multi_select_list]

    def _extract_email(self, prop: Dict) -> str:
        """Extract email from Notion property"""
        if not prop or prop.get('type') != 'email':
            return ''
        return prop.get('email', '')

    def _extract_url(self, prop: Dict) -> str:
        """Extract URL from Notion property"""
        if not prop or prop.get('type') != 'url':
            return ''
        return prop.get('url', '')

    def _extract_date(self, prop: Dict) -> str:
        """Extract date from Notion property"""
        if not prop or prop.get('type') != 'date':
            return ''

        date_obj = prop.get('date')
        if date_obj:
            return date_obj.get('start', '')
        return ''

    def _extract_phone(self, prop: Dict) -> str:
        """Extract phone number from Notion property"""
        if not prop:
            return ''

        # Phone numbers can be stored as rich_text or phone_number type
        if prop.get('type') == 'phone_number':
            return prop.get('phone_number', '')
        elif prop.get('type') == 'rich_text':
            rich_text_list = prop.get('rich_text', [])
            if rich_text_list:
                return ''.join([item.get('plain_text', '') for item in rich_text_list])

        return ''

    def _extract_relation(self, prop: Dict) -> List[str]:
        """Extract relation IDs from Notion property"""
        if not prop or prop.get('type') != 'relation':
            return []

        relation_list = prop.get('relation', [])
        return [item.get('id', '') for item in relation_list if item.get('id')]

    def _get_account_name_by_id(self, account_id: str) -> str:
        """Get account name by ID from accounts cache"""
        if not hasattr(self, '_accounts_cache'):
            self._build_accounts_cache()

        return self._accounts_cache.get(account_id, 'Unknown Company')

    def _build_accounts_cache(self):
        """Build cache of account ID to name mappings"""
        try:
            accounts = self.fetch_accounts()
            self._accounts_cache = {
                acc.get('id'): acc.get('name', 'Unknown Company')
                for acc in accounts
            }
        except Exception as e:
            print(f"Error building accounts cache: {e}")
            self._accounts_cache = {}

    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""

        def fetch_all_data():
            accounts = self.fetch_accounts()
            contacts = self.fetch_contacts()
            # Use enhanced trigger events with trend analysis
            enhanced_events = self.fetch_enhanced_trigger_events()

            # Calculate enhanced summary stats
            stats = {
                'active_accounts': len(accounts),
                'total_contacts': len(contacts),
                'linkedin_enriched': len([c for c in contacts if c.get('linkedin_activity_level')]),
                'critical_signals': len([e for e in enhanced_events if e.get('priority_level') == 'Critical']),
                'high_priority_signals': len([e for e in enhanced_events if e.get('priority_level') == 'High']),
                'immediate_action_required': len([e for e in enhanced_events if 'within 24' in str(e.get('timing_recommendation', ''))])
            }

            # Get primary account (Genesis Cloud)
            primary_account = accounts[0] if accounts else None

            # Get contacts for primary account
            primary_contacts = contacts[:10]  # Top 10 contacts

            # Get recent enhanced events (top priority first)
            recent_events = enhanced_events[:5]  # Top 5 enhanced events

            return {
                'stats': stats,
                'primary_account': primary_account,
                'contacts': primary_contacts,
                'buying_signals': recent_events,  # Enhanced buying signals
                'trigger_events': recent_events,  # Backward compatibility
                'last_updated': datetime.now().isoformat()
            }

        return self.get_cached_or_fetch('dashboard_data', fetch_all_data, 60)  # Cache for 1 minute

# Flask app for serving dashboard
app = Flask(__name__)
CORS(app)

notion_service = NotionDataService()

@app.route('/')
def dashboard():
    """Serve the dashboard"""
    dashboard_path = Path(__file__).parent / 'abm_dashboard.html'
    return send_file(dashboard_path)

@app.route('/api/data')
def get_data():
    """API endpoint for dashboard data"""
    try:
        data = notion_service.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts')
def get_accounts():
    """Get accounts data"""
    try:
        accounts = notion_service.fetch_accounts()
        return jsonify(accounts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<account_id>')
def get_contacts(account_id):
    """Get contacts for specific account"""
    try:
        contacts = notion_service.fetch_contacts(account_id)
        return jsonify(contacts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<account_id>')
def get_events(account_id):
    """Get trigger events for specific account"""
    try:
        events = notion_service.fetch_trigger_events(account_id)
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-signals')
def get_enhanced_signals():
    """Get enhanced buying signals with trend analysis and priority scoring"""
    try:
        enhanced_signals = notion_service.fetch_enhanced_trigger_events()
        return jsonify(enhanced_signals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-signals/<account_id>')
def get_enhanced_signals_for_account(account_id):
    """Get enhanced buying signals for specific account"""
    try:
        enhanced_signals = notion_service.fetch_enhanced_trigger_events(account_id)
        return jsonify(enhanced_signals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact-value-analysis')
def get_contact_value_analysis():
    """Get contact value analysis with high-ICP contacts and role patterns"""
    try:
        contact_analysis = notion_service.fetch_contact_value_analysis()
        return jsonify(contact_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact-value-analysis/<account_id>')
def get_contact_value_analysis_for_account(account_id):
    """Get contact value analysis for specific account"""
    try:
        contact_analysis = notion_service.fetch_contact_value_analysis(account_id)
        return jsonify(contact_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/partnerships')
def get_partnerships():
    """Get partnerships data"""
    try:
        partnerships = notion_service.fetch_partnerships()
        return jsonify(partnerships)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'databases': notion_service.database_ids
    })

def run_dashboard_server():
    """Run the dashboard server"""
    print("🚀 STARTING ABM INTELLIGENCE DASHBOARD")
    print("=" * 50)
    print(f"📊 Dashboard: http://localhost:5002")
    print(f"🔌 API: http://localhost:5002/api/data")
    print(f"💾 Data Sources: {len(notion_service.database_ids)} Notion databases")
    print(f"🔄 Auto-refresh: Every 60 seconds")

    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)

# Global instance for the app
notion_service = NotionDataService()

# Add dashboard-compatible methods to NotionDataService class
def add_dashboard_methods():
    """Add dashboard-compatible methods to the NotionDataService class"""

    def get_accounts_with_contacts(self):
        """Get accounts with their associated contacts for dashboard"""
        accounts = self.fetch_accounts()
        for account in accounts[:10]:  # Limit to top 10
            company_name = account.get('properties', {}).get('Company Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
            if company_name:
                # Add contact count
                contacts = self.fetch_contacts(account.get('id', ''))
                account['contact_count'] = len(contacts)
                account['company_name'] = company_name
        return accounts

    def get_contacts_for_account(self, company_name):
        """Get contacts for a specific account by company name"""
        try:
            accounts = self.fetch_accounts()
            target_account = None
            for account in accounts:
                account_name = account.get('properties', {}).get('Company Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                if account_name.lower() == company_name.lower():
                    target_account = account
                    break

            if target_account:
                return self.fetch_contacts(target_account.get('id', ''))
            return []
        except Exception as e:
            print(f"Error getting contacts for {company_name}: {e}")
            return []

    def get_trigger_events_for_account(self, company_name, days_back=30):
        """Get trigger events for a specific account by company name"""
        try:
            accounts = self.fetch_accounts()
            target_account = None
            for account in accounts:
                account_name = account.get('properties', {}).get('Company Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                if account_name.lower() == company_name.lower():
                    target_account = account
                    break

            if target_account:
                return self.fetch_enhanced_trigger_events(target_account.get('id', ''))
            return []
        except Exception as e:
            print(f"Error getting trigger events for {company_name}: {e}")
            return []

    def get_strategic_partnerships(self):
        """Get strategic partnerships for dashboard"""
        return self.fetch_partnerships()[:10]  # Limit to top 10

    def get_account_by_name(self, company_name):
        """Get a specific account by company name"""
        try:
            accounts = self.fetch_accounts()
            for account in accounts:
                account_name = account.get('properties', {}).get('Company Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                if account_name.lower() == company_name.lower():
                    return account
            return None
        except Exception as e:
            print(f"Error getting account {company_name}: {e}")
            return None

    def get_contact_by_name(self, contact_name):
        """Get a specific contact by name"""
        try:
            all_contacts = self.fetch_contacts()
            for contact in all_contacts:
                # Try different name fields
                full_name = contact.get('properties', {}).get('Full Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                first_name = contact.get('properties', {}).get('First Name', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '')
                last_name = contact.get('properties', {}).get('Last Name', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '')

                if (full_name and contact_name.lower() in full_name.lower()) or \
                   (first_name and last_name and contact_name.lower() in f"{first_name} {last_name}".lower()):
                    return contact
            return None
        except Exception as e:
            print(f"Error getting contact {contact_name}: {e}")
            return None

    # Add methods to the class
    NotionDataService.get_accounts_with_contacts = get_accounts_with_contacts
    NotionDataService.get_contacts_for_account = get_contacts_for_account
    NotionDataService.get_trigger_events_for_account = get_trigger_events_for_account
    NotionDataService.get_strategic_partnerships = get_strategic_partnerships
    NotionDataService.get_account_by_name = get_account_by_name
    NotionDataService.get_contact_by_name = get_contact_by_name

# Call the function to add methods
add_dashboard_methods()


# Alias for dashboard compatibility
DashboardDataService = NotionDataService

if __name__ == "__main__":
    run_dashboard_server()