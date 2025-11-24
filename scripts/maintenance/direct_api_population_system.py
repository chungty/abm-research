#!/usr/bin/env python3
"""
Direct API Population System
Populate enhanced databases using only direct API calls - no notion-client library
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from abm_config import config
from config.settings import (
    NOTION_ACCOUNTS_DB_ID,
    NOTION_CONTACTS_DB_ID,
    NOTION_TRIGGER_EVENTS_DB_ID,
    NOTION_PARTNERSHIPS_DB_ID
)

# Import our working components
from production_apollo_integration import ProductionApolloIntegration
from verdigris_signals_meddic_framework import VerdigrisSignalsMEDDIC
from enhanced_deduplication_system import EnhancedDeduplicationSystem

class DirectNotionAPI:
    """Direct Notion API integration - no client library"""

    def __init__(self):
        # Get headers from our cleaned config
        self.headers = config.get_notion_headers()

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

    def create_account_entry(self, account_data: dict) -> str:
        """Create account entry in Notion using direct API"""

        try:
            url = f"https://api.notion.com/v1/pages"

            # Build properties based on enhanced schema
            properties = {
                "Name": {
                    "title": [{"type": "text", "text": {"content": account_data.get('name', 'Unknown Company')}}]
                }
            }

            # Add optional fields if available
            if account_data.get('domain'):
                properties["Domain"] = {
                    "rich_text": [{"type": "text", "text": {"content": account_data['domain']}}]
                }

            if account_data.get('employee_count'):
                properties["Employee Count"] = {"number": account_data['employee_count']}

            if account_data.get('icp_fit_score'):
                properties["ICP Fit Score"] = {"number": account_data['icp_fit_score']}

            if account_data.get('apollo_account_id'):
                properties["Apollo Account ID"] = {
                    "rich_text": [{"type": "text", "text": {"content": str(account_data['apollo_account_id'])}}]
                }

            if account_data.get('apollo_organization_id'):
                properties["Apollo Organization ID"] = {
                    "rich_text": [{"type": "text", "text": {"content": str(account_data['apollo_organization_id'])}}]
                }

            # Set status and timestamp
            properties["Account Research Status"] = {"select": {"name": "In Progress"}}
            properties["Last Updated"] = {"date": {"start": datetime.now().isoformat()}}

            payload = {
                "parent": {"database_id": self.database_ids['accounts']},
                "properties": properties
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                account_id = response.json()['id']
                print(f"   ✅ Created account: {account_data.get('name', 'Unknown')} ({account_id})")
                return account_id
            else:
                print(f"   ❌ Failed to create account: {response.text}")
                return None

        except Exception as e:
            print(f"   ❌ Account creation failed: {e}")
            return None

    def create_contact_entry(self, contact_data: dict, account_id: str = None) -> str:
        """Create contact entry in Notion using direct API"""

        try:
            url = f"https://api.notion.com/v1/pages"

            properties = {
                "Name": {
                    "title": [{"type": "text", "text": {"content": contact_data.get('name', 'Unknown Contact')}}]
                }
            }

            # Add account relation if provided
            if account_id:
                properties["Account"] = {"relation": [{"id": account_id}]}

            # Add contact details
            if contact_data.get('title'):
                properties["Title"] = {
                    "rich_text": [{"type": "text", "text": {"content": contact_data['title']}}]
                }

            if contact_data.get('email'):
                properties["Email"] = {"email": contact_data['email']}

            if contact_data.get('linkedin_url'):
                properties["LinkedIn URL"] = {"url": contact_data['linkedin_url']}

            # Add MEDDIC scoring
            if contact_data.get('icp_fit_score'):
                properties["ICP Fit Score"] = {"number": contact_data['icp_fit_score']}

            if contact_data.get('buying_power_score'):
                properties["Buying Power Score"] = {"number": contact_data['buying_power_score']}

            if contact_data.get('engagement_potential_score'):
                properties["Engagement Potential Score"] = {"number": contact_data['engagement_potential_score']}

            # Map to existing field names (from our analysis)
            if contact_data.get('buying_committee_role'):
                properties["Buying committee role"] = {"select": {"name": contact_data['buying_committee_role']}}

            # Add Apollo integration fields
            if contact_data.get('apollo_contact_id'):
                properties["Apollo Contact ID"] = {
                    "rich_text": [{"type": "text", "text": {"content": str(contact_data['apollo_contact_id'])}}]
                }

            if contact_data.get('apollo_person_id'):
                properties["Apollo Person ID"] = {
                    "rich_text": [{"type": "text", "text": {"content": str(contact_data['apollo_person_id'])}}]
                }

            # Add problems and content themes using existing field names
            if contact_data.get('problems_they_likely_own'):
                problems = contact_data['problems_they_likely_own']
                if problems:
                    properties["Problems they likely own"] = {
                        "multi_select": [{"name": problem} for problem in problems if problem]
                    }

            if contact_data.get('content_themes_they_value'):
                themes = contact_data['content_themes_they_value']
                if themes:
                    properties["Content themes they value"] = {
                        "multi_select": [{"name": theme} for theme in themes if theme]
                    }

            # Use existing field names
            properties["Research status"] = {"select": {"name": "Enriched"}}

            payload = {
                "parent": {"database_id": self.database_ids['contacts']},
                "properties": properties
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                contact_id = response.json()['id']
                print(f"   ✅ Created contact: {contact_data.get('name', 'Unknown')} ({contact_id})")
                return contact_id
            else:
                print(f"   ❌ Failed to create contact: {response.text}")
                return None

        except Exception as e:
            print(f"   ❌ Contact creation failed: {e}")
            return None

class CleanABMSystem:
    """Clean ABM system using only direct API calls"""

    def __init__(self):
        print("🚀 INITIALIZING CLEAN ABM SYSTEM (Direct API Only)")
        print("-" * 50)

        self.apollo = ProductionApolloIntegration()
        self.meddic = VerdigrisSignalsMEDDIC()
        self.deduplication = EnhancedDeduplicationSystem()
        self.notion = DirectNotionAPI()

        print("✅ All components initialized successfully")

    def process_genesis_cloud(self):
        """Process Genesis Cloud with enhanced intelligence"""

        print("\n🎯 PROCESSING GENESIS CLOUD WITH CLEAN API SYSTEM")
        print("=" * 70)

        # 1. Discover contacts using our proven Apollo integration
        print("\n📋 STEP 1: DISCOVERING GENESIS CLOUD CONTACTS")
        print("-" * 50)

        contacts = self.apollo.find_contacts_for_company("Genesis Cloud")

        if not contacts:
            print("❌ No contacts found for Genesis Cloud")
            return

        print(f"✅ Found {len(contacts)} contacts from Apollo")

        # 2. Apply deduplication
        print(f"\n🔧 STEP 2: APPLYING DEDUPLICATION")
        print("-" * 30)

        deduplicated_contacts = self.deduplication.deduplicate_contacts(contacts)
        print(f"✅ After deduplication: {len(deduplicated_contacts)} unique contacts")

        # 3. Apply MEDDIC classification and scoring
        print(f"\n🎯 STEP 3: APPLYING VERDIGRIS SIGNALS MEDDIC")
        print("-" * 45)

        classified_contacts = []
        for contact in deduplicated_contacts:
            classification = self.meddic.classify_contact(contact)

            # Enhance contact with MEDDIC data and Apollo IDs
            enhanced_contact = {
                **contact,
                **classification,
                'apollo_contact_id': contact.get('id'),
                'apollo_person_id': contact.get('person_id')
            }

            classified_contacts.append(enhanced_contact)

        # Sort by lead score (highest first)
        classified_contacts.sort(key=lambda c: c.get('final_lead_score', 0), reverse=True)

        print(f"✅ Applied MEDDIC classification to all contacts")
        print(f"📊 Top lead score: {classified_contacts[0].get('final_lead_score', 0):.1f}")

        # 4. Create account entry in Notion
        print(f"\n📊 STEP 4: CREATING GENESIS CLOUD ACCOUNT")
        print("-" * 40)

        account_data = {
            'name': 'Genesis Cloud',
            'domain': 'genesiscloud.com',
            'employee_count': 50,  # Estimated based on our research
            'icp_fit_score': 85,  # High-performance GPU cloud provider - perfect fit for Verdigris Signals
            'apollo_organization_id': contacts[0].get('organization_id') if contacts else None
        }

        account_id = self.notion.create_account_entry(account_data)

        if not account_id:
            print("❌ Could not create account entry - stopping")
            return

        # 5. Create contact entries in Notion
        print(f"\n👤 STEP 5: CREATING CONTACT ENTRIES (Direct API)")
        print("-" * 45)

        successful_contacts = 0

        # Process top 10 contacts to avoid overwhelming the system
        for i, contact in enumerate(classified_contacts[:10]):
            print(f"\nProcessing contact {i+1}/10:")

            contact_id = self.notion.create_contact_entry(contact, account_id)
            if contact_id:
                successful_contacts += 1

        # 6. Generate summary
        print(f"\n🎉 GENESIS CLOUD PROCESSING COMPLETE!")
        print("=" * 50)
        print(f"📊 Account created: Genesis Cloud ({account_id})")
        print(f"👤 Contacts created: {successful_contacts}/{min(10, len(classified_contacts))}")
        print(f"🎯 Top lead score: {classified_contacts[0].get('final_lead_score', 0):.1f}")
        print(f"🏆 Best persona: {classified_contacts[0].get('buying_committee_role', 'Unknown')}")

        # Show top 3 contacts
        print(f"\n🌟 TOP 3 CONTACTS:")
        for i, contact in enumerate(classified_contacts[:3]):
            score = contact.get('final_lead_score', 0)
            role = contact.get('buying_committee_role', 'Unknown')
            title = contact.get('title', 'Unknown Title')
            print(f"   {i+1}. {contact.get('name', 'Unknown')} - {title}")
            print(f"      Score: {score:.1f} pts | Role: {role}")

        print(f"\n🔗 View in Notion:")
        print(f"   📊 Accounts: https://www.notion.so/{self.notion.database_ids['accounts'].replace('-', '')}")
        print(f"   👤 Contacts: https://www.notion.so/{self.notion.database_ids['contacts'].replace('-', '')}")

        return {
            'account_id': account_id,
            'contacts_created': successful_contacts,
            'total_contacts': len(classified_contacts),
            'top_lead_score': classified_contacts[0].get('final_lead_score', 0) if classified_contacts else 0,
            'top_contacts': classified_contacts[:3]
        }

def main():
    """Main function"""

    print("🧹 CLEAN ABM SYSTEM - DIRECT API ONLY")
    print("=" * 60)
    print("No notion-client library - pure HTTP API integration")

    # Test configuration first
    print(f"\n🔧 Configuration Check:")
    config.print_config_status()

    # Initialize and run system
    system = CleanABMSystem()
    results = system.process_genesis_cloud()

    if results:
        print(f"\n✅ SYSTEM SUCCESSFULLY POPULATED DATABASES!")
        print(f"🚀 Sales team can now engage with {results['contacts_created']} Genesis Cloud contacts!")
        print(f"📈 Lead scores range from {results['top_lead_score']:.1f} down")

        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Review contacts in Notion and validate MEDDIC classifications")
        print(f"   2. Begin outreach with highest-scoring Economic Buyers and Champions")
        print(f"   3. Use personalized value propositions based on their likely problems")

if __name__ == "__main__":
    main()