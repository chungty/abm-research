#!/usr/bin/env python3
"""
Update Existing Notion Databases with Focused GTM Data
Works with user's existing 4 databases instead of creating new ones
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from focused_gtm_system import FocusedGTMContactDiscovery, FocusedGTMValueIntelligence

class ExistingDatabaseUpdater:
    """Update existing Notion databases with focused GTM results"""

    def __init__(self):
        self.notion_token = os.getenv('NOTION_ABM_API_KEY')
        if not self.notion_token:
            raise ValueError("NOTION_ABM_API_KEY not found")

        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # FIXED DATABASE IDs - USER SPECIFIED, DO NOT CHANGE
        self.database_ids = {
            'accounts': 'c31d728f-4770-49e2-8f6b-d68717e2c160',
            'contacts': 'a6e0cace-85de-4afd-be6c-9c926d1d0e3d',
            'events': 'c8ae1662-cba9-4ea3-9cb3-2bcea3621963',
            'intelligence': 'fa1467c0-ad15-4b09-bb03-cc715f9b8577'
        }

        print(f"✅ Using FIXED database IDs:")
        for db_type, db_id in self.database_ids.items():
            print(f"   📊 {db_type.title()}: {db_id}")
        print(f"   🚨 NEVER creating new databases - only updating existing ones")

    def discover_existing_databases(self) -> Dict[str, str]:
        """Find existing databases by searching for ABM-related databases"""

        try:
            # Search for databases
            response = requests.post(
                "https://api.notion.com/v1/search",
                headers=self.headers,
                json={
                    "query": "ABM",
                    "filter": {"property": "object", "value": "database"},
                    "page_size": 100
                }
            )

            if response.status_code == 200:
                data = response.json()
                databases = data.get('results', [])

                print(f"🔍 Found {len(databases)} ABM-related databases:")

                discovered_dbs = {}
                for db in databases:
                    db_id = db['id']
                    title_parts = db.get('title', [])
                    db_title = title_parts[0]['text']['content'] if title_parts else 'Untitled'

                    print(f"   📊 {db_title}: {db_id}")

                    # Categorize databases by name keywords
                    title_lower = db_title.lower()
                    if 'account' in title_lower:
                        discovered_dbs['accounts'] = db_id
                    elif 'contact' in title_lower:
                        discovered_dbs['contacts'] = db_id
                    elif 'event' in title_lower or 'trigger' in title_lower:
                        discovered_dbs['events'] = db_id
                    elif 'partnership' in title_lower or 'intelligence' in title_lower:
                        discovered_dbs['intelligence'] = db_id

                self.database_ids = discovered_dbs
                print(f"✅ Categorized {len(discovered_dbs)} databases for updating")
                return discovered_dbs

            else:
                print(f"❌ Failed to discover databases: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ Error discovering databases: {e}")
            return {}

    def get_database_schema(self, database_id: str) -> Dict:
        """Get existing database schema to understand available fields"""

        try:
            response = requests.get(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers
            )

            if response.status_code == 200:
                database_info = response.json()
                properties = database_info.get('properties', {})

                print(f"📋 Database schema:")
                for prop_name, prop_info in properties.items():
                    prop_type = prop_info.get('type', 'unknown')
                    print(f"   - {prop_name}: {prop_type}")

                return properties
            else:
                print(f"❌ Failed to get database schema: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ Error getting database schema: {e}")
            return {}

    def update_accounts_database(self, accounts_data: List[Dict]):
        """Update existing accounts database with new data"""

        if 'accounts' not in self.database_ids:
            print("❌ No accounts database found")
            return

        accounts_db_id = self.database_ids['accounts']
        print(f"\n📊 Updating accounts database: {accounts_db_id}")

        # Get existing schema
        schema = self.get_database_schema(accounts_db_id)

        for account_data in accounts_data:
            company_name = account_data.get('company_context', {}).get('name', 'Unknown')

            # Build properties based on available fields
            properties = {}

            # Map our data to existing fields (flexible mapping)
            field_mappings = {
                'Company Name': company_name,
                'Domain': account_data.get('domain', ''),
                'Total Contacts': account_data.get('qualified_contacts', 0),
                'Research Status': 'Complete',
                'Last Updated': datetime.now().isoformat()
            }

            for field_name, value in field_mappings.items():
                if field_name in schema:
                    field_type = schema[field_name].get('type')

                    if field_type == 'title':
                        properties[field_name] = {"title": [{"text": {"content": str(value)}}]}
                    elif field_type == 'rich_text':
                        properties[field_name] = {"rich_text": [{"text": {"content": str(value)}}]}
                    elif field_type == 'number':
                        properties[field_name] = {"number": int(value) if isinstance(value, (int, float)) else 0}
                    elif field_type == 'select':
                        properties[field_name] = {"select": {"name": str(value)}}
                    elif field_type == 'date':
                        properties[field_name] = {"date": {"start": value if isinstance(value, str) else datetime.now().isoformat()}}

            if properties:
                try:
                    response = requests.post(
                        f"https://api.notion.com/v1/pages",
                        headers=self.headers,
                        json={
                            "parent": {"database_id": accounts_db_id},
                            "properties": properties
                        }
                    )

                    if response.status_code == 200:
                        print(f"✅ Added account: {company_name}")
                    else:
                        print(f"❌ Failed to add account {company_name}: {response.status_code}")

                except Exception as e:
                    print(f"❌ Error adding account {company_name}: {e}")

    def update_contacts_database(self, all_contacts: List[Dict]):
        """Update existing contacts database with focused GTM contacts"""

        if 'contacts' not in self.database_ids:
            print("❌ No contacts database found")
            return

        contacts_db_id = self.database_ids['contacts']
        print(f"\n👥 Updating contacts database: {contacts_db_id}")

        # Get existing schema
        schema = self.get_database_schema(contacts_db_id)

        for contact in all_contacts:
            name = contact.get('name', 'Unknown')

            # Build properties for power-focused contacts
            properties = {}

            field_mappings = {
                'Name': name,
                'Title': contact.get('title', ''),
                'Company': contact.get('company', ''),
                'Email': contact.get('email', ''),
                'LinkedIn URL': contact.get('linkedin_url', ''),
                'Power Infrastructure Score': contact.get('power_infrastructure_score', 0),
                'Relevance Reason': contact.get('relevance_reason', ''),
                'Signal Level': contact.get('signal_level', 'medium'),
                'Approach': contact.get('approach', ''),
                'Power Problem': contact.get('power_problem', ''),
                'Verdigris Solution': contact.get('verdigris_solution', ''),
                'Primary Message': contact.get('primary_message', ''),
                'Email Subject': contact.get('email_subject', ''),
                'Call to Action': contact.get('call_to_action', ''),
                'Last Updated': datetime.now().isoformat()
            }

            for field_name, value in field_mappings.items():
                if field_name in schema and value:
                    field_type = schema[field_name].get('type')

                    try:
                        if field_type == 'title':
                            properties[field_name] = {"title": [{"text": {"content": str(value)[:2000]}}]}
                        elif field_type == 'rich_text':
                            properties[field_name] = {"rich_text": [{"text": {"content": str(value)[:2000]}}]}
                        elif field_type == 'number':
                            properties[field_name] = {"number": int(value) if isinstance(value, (int, float)) else 0}
                        elif field_type == 'select':
                            properties[field_name] = {"select": {"name": str(value)[:100]}}
                        elif field_type == 'email':
                            properties[field_name] = {"email": str(value)[:320]}
                        elif field_type == 'url':
                            properties[field_name] = {"url": str(value)[:2000]}
                        elif field_type == 'date':
                            properties[field_name] = {"date": {"start": value if isinstance(value, str) else datetime.now().isoformat()}}
                    except:
                        continue  # Skip invalid field mappings

            if properties:
                try:
                    response = requests.post(
                        f"https://api.notion.com/v1/pages",
                        headers=self.headers,
                        json={
                            "parent": {"database_id": contacts_db_id},
                            "properties": properties
                        }
                    )

                    if response.status_code == 200:
                        print(f"✅ Added contact: {name}")
                    else:
                        print(f"❌ Failed to add contact {name}: {response.status_code}")
                        print(f"   Error: {response.text}")

                except Exception as e:
                    print(f"❌ Error adding contact {name}: {e}")

    def clear_existing_data(self, database_id: str):
        """Clear existing data from database (optional)"""

        try:
            # Query existing pages
            response = requests.post(
                f"https://api.notion.com/v1/databases/{database_id}/query",
                headers=self.headers,
                json={"page_size": 100}
            )

            if response.status_code == 200:
                data = response.json()
                existing_pages = data.get('results', [])

                print(f"🗑️ Found {len(existing_pages)} existing records to potentially clear")
                # Note: Actual deletion would go here if requested

            return len(existing_pages)

        except Exception as e:
            print(f"❌ Error checking existing data: {e}")
            return 0

def main():
    """Update existing Notion databases with focused GTM data"""

    print("🔄 Updating Existing Notion Databases with Focused GTM Data\n")

    try:
        # Initialize systems
        database_updater = ExistingDatabaseUpdater()
        contact_discovery = FocusedGTMContactDiscovery(os.getenv('APOLLO_API_KEY'))
        intelligence_engine = FocusedGTMValueIntelligence(os.getenv('OPENAI_API_KEY'))

        # 1. Use fixed database IDs (no discovery needed)
        existing_dbs = database_updater.database_ids

        print(f"✅ Using {len(existing_dbs)} fixed database IDs (no discovery required)")

        # 2. Research target accounts with focused GTM
        target_accounts = ["genesiscloud.com", "datacrunch.io", "leadergpu.com"]
        all_account_data = []
        all_contacts = []

        print(f"\n🎯 Researching {len(target_accounts)} target accounts with focused GTM...")

        for domain in target_accounts:
            print(f"\n📊 Researching {domain}...")

            # Discover power infrastructure decision makers
            power_contacts = contact_discovery.discover_power_decision_makers(domain)
            if not power_contacts:
                continue

            # LinkedIn enrichment
            enriched_contacts = contact_discovery.enrich_with_linkedin_research(power_contacts)

            # Generate power-focused intelligence
            qualified_contacts = []
            for contact in enriched_contacts:
                intelligence = intelligence_engine.generate_power_focused_intelligence(
                    contact, {'name': domain.replace('.com', '').title(), 'domain': domain}
                )

                if not intelligence.get('skip_reason'):
                    contact.update(intelligence)
                    qualified_contacts.append(contact)

            # Collect data for database updates
            account_data = {
                'domain': domain,
                'company_context': {'name': domain.replace('.com', '').title()},
                'qualified_contacts': len(qualified_contacts),
                'contacts': qualified_contacts
            }

            all_account_data.append(account_data)
            all_contacts.extend(qualified_contacts)

            print(f"✅ {domain}: {len(qualified_contacts)} qualified contacts")

        # 3. Update existing databases
        print(f"\n🔄 Updating existing Notion databases...")

        # Update accounts database
        database_updater.update_accounts_database(all_account_data)

        # Update contacts database
        database_updater.update_contacts_database(all_contacts)

        # Summary
        print(f"\n✅ DATABASE UPDATE COMPLETE")
        print(f"   Accounts Updated: {len(all_account_data)}")
        print(f"   Contacts Added: {len(all_contacts)}")
        print(f"   Databases Used: {len(existing_dbs)}")

        # Show database links
        print(f"\n🔗 UPDATED DATABASES:")
        for db_type, db_id in existing_dbs.items():
            print(f"   {db_type.title()}: https://notion.so/{db_id.replace('-', '')}")

    except Exception as e:
        print(f"❌ Failed to update databases: {e}")

if __name__ == '__main__':
    main()