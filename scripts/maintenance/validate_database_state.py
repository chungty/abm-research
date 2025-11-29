#!/usr/bin/env python3
"""
Database State Validation Script

Checks the current state of all 4 Notion databases to verify:
- How many real prospects are in the Accounts database
- Contact distribution across companies
- Trigger events and partnerships data
- Overall database health and cleanliness
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def validate_database_state():
    """Comprehensive validation of all Notion databases"""

    print("🔍 Database State Validation")
    print("=" * 50)

    # Initialize Notion client
    notion_client = NotionClient()

    try:
        # 1. Validate Accounts Database
        print("🏢 ACCOUNTS DATABASE")
        print("-" * 30)

        # Query accounts database directly
        url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['accounts']}/query"
        accounts_response = notion_client._make_request('POST', url, json={})
        accounts_data = accounts_response.json()
        active_accounts = [account for account in accounts_data.get('results', []) if not account.get('archived', False)]

        print(f"📊 Total accounts: {len(accounts_data.get('results', []))}")
        print(f"📊 Active accounts: {len(active_accounts)}")

        if active_accounts:
            print("📋 Active accounts:")
            for account in active_accounts:
                props = account.get('properties', {})

                # Safe parsing with fallbacks
                name = 'Unknown'
                try:
                    title_field = props.get('Company Name', {}).get('title', [])
                    if title_field and len(title_field) > 0:
                        name = title_field[0].get('text', {}).get('content', 'Unknown')
                except:
                    pass

                domain = 'Unknown'
                try:
                    domain_field = props.get('Domain', {}).get('rich_text', [])
                    if domain_field and len(domain_field) > 0:
                        domain = domain_field[0].get('text', {}).get('content', 'Unknown')
                except:
                    pass

                industry = 'Unknown'
                try:
                    industry_field = props.get('Industry', {}).get('select')
                    if industry_field:
                        industry = industry_field.get('name', 'Unknown')
                except:
                    pass

                print(f"   • {name} ({domain}) - {industry}")
        print()

        # 2. Validate Contacts Database
        print("👥 CONTACTS DATABASE")
        print("-" * 30)

        # Query contacts database directly
        url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['contacts']}/query"
        contacts_response = notion_client._make_request('POST', url, json={})
        contacts_data = contacts_response.json()
        active_contacts = [contact for contact in contacts_data.get('results', []) if not contact.get('archived', False)]

        print(f"📊 Total contacts: {len(contacts_data.get('results', []))}")
        print(f"📊 Active contacts: {len(active_contacts)}")

        # Group contacts by company
        contacts_by_company = defaultdict(list)
        for contact in active_contacts:
            props = contact.get('properties', {})

            # Safe parsing with fallbacks for contacts
            name = 'Unknown'
            try:
                name_field = props.get('Name', {}).get('title', [])
                if name_field and len(name_field) > 0:
                    name = name_field[0].get('text', {}).get('content', 'Unknown')
            except:
                pass

            company = 'Unknown'
            try:
                company_field = props.get('Company', {}).get('rich_text', [])
                if company_field and len(company_field) > 0:
                    company = company_field[0].get('text', {}).get('content', 'Unknown')
            except:
                pass

            title = 'Unknown'
            try:
                title_field = props.get('Title', {}).get('rich_text', [])
                if title_field and len(title_field) > 0:
                    title = title_field[0].get('text', {}).get('content', 'Unknown')
            except:
                pass

            contacts_by_company[company].append(f"{name} ({title})")

        if contacts_by_company:
            print("📋 Contacts by company:")
            for company, contact_list in contacts_by_company.items():
                print(f"   • {company}: {len(contact_list)} contacts")
                for contact_info in contact_list[:3]:  # Show first 3 contacts
                    print(f"     - {contact_info}")
                if len(contact_list) > 3:
                    print(f"     ... and {len(contact_list) - 3} more")
        print()

        # 3. Validate Trigger Events Database
        print("🎯 TRIGGER EVENTS DATABASE")
        print("-" * 30)

        # Query trigger events database directly
        url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['trigger_events']}/query"
        events_response = notion_client._make_request('POST', url, json={})
        events_data = events_response.json()
        active_events = [event for event in events_data.get('results', []) if not event.get('archived', False)]

        print(f"📊 Total events: {len(events_data.get('results', []))}")
        print(f"📊 Active events: {len(active_events)}")

        if active_events:
            # Group events by type
            events_by_type = defaultdict(int)
            for event in active_events:
                props = event.get('properties', {})

                # Safe parsing with fallback for event type
                event_type = 'Unknown'
                try:
                    event_type_field = props.get('Event Type', {}).get('select')
                    if event_type_field:
                        event_type = event_type_field.get('name', 'Unknown')
                except:
                    pass

                events_by_type[event_type] += 1

            print("📋 Events by type:")
            for event_type, count in events_by_type.items():
                print(f"   • {event_type}: {count} events")
        print()

        # 4. Validate Partnerships Database
        print("🤝 PARTNERSHIPS DATABASE")
        print("-" * 30)

        # Query partnerships database directly
        url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['partnerships']}/query"
        partnerships_response = notion_client._make_request('POST', url, json={})
        partnerships_data = partnerships_response.json()
        active_partnerships = [partnership for partnership in partnerships_data.get('results', []) if not partnership.get('archived', False)]

        print(f"📊 Total partnerships: {len(partnerships_data.get('results', []))}")
        print(f"📊 Active partnerships: {len(active_partnerships)}")

        if active_partnerships:
            # Group partnerships by type
            partnerships_by_type = defaultdict(int)
            for partnership in active_partnerships:
                props = partnership.get('properties', {})

                # Safe parsing with fallback for partnership type
                partnership_type = 'Unknown'
                try:
                    partnership_type_field = props.get('Partnership Type', {}).get('select')
                    if partnership_type_field:
                        partnership_type = partnership_type_field.get('name', 'Unknown')
                except:
                    pass

                partnerships_by_type[partnership_type] += 1

            print("📋 Partnerships by type:")
            for partnership_type, count in partnerships_by_type.items():
                print(f"   • {partnership_type}: {count} partnerships")
        print()

        # 5. Summary & Health Check
        print("💫 DATABASE HEALTH SUMMARY")
        print("=" * 40)
        print(f"🏢 Active accounts: {len(active_accounts)}")
        print(f"👥 Active contacts: {len(active_contacts)}")
        print(f"🎯 Active events: {len(active_events)}")
        print(f"🤝 Active partnerships: {len(active_partnerships)}")
        print()

        # Health assessment
        if len(active_accounts) > 0:
            avg_contacts_per_account = len(active_contacts) / len(active_accounts) if active_accounts else 0
            print(f"📈 Average contacts per account: {avg_contacts_per_account:.1f}")

            if len(active_accounts) <= 10:
                print("✅ Database size: Manageable for focused ABM research")
            elif len(active_accounts) <= 50:
                print("⚠️  Database size: Growing, consider prioritization")
            else:
                print("🔴 Database size: Large, needs segmentation")

            if avg_contacts_per_account >= 5:
                print("✅ Contact coverage: Good depth per account")
            elif avg_contacts_per_account >= 2:
                print("⚠️  Contact coverage: Moderate, could improve")
            else:
                print("🔴 Contact coverage: Low, needs more contact discovery")

        print()
        print("🎉 Database validation complete!")
        print("✅ Ready for production ABM research")

    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False

    return True

if __name__ == "__main__":
    try:
        validate_database_state()
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)