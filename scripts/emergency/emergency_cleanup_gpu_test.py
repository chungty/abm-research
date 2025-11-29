#!/usr/bin/env python3
"""
Emergency Cleanup: GPU Test Data

Removes test data just added by the background GPU infrastructure test
that added 52 new test contacts for NVIDIA, CoreWeave, and Lambda Labs.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# The three companies that just polluted production
GPU_TEST_COMPANIES = [
    'NVIDIA Corporation',
    'CoreWeave',
    'Lambda Labs'
]

def emergency_gpu_test_cleanup():
    """Emergency cleanup of GPU test data from production"""

    print("🚨 EMERGENCY CLEANUP: GPU Test Data")
    print("=" * 50)
    print("Background GPU test just added 52 test contacts to production!")
    print("Removing test data from these companies:")
    for company in GPU_TEST_COMPANIES:
        print(f"   - {company}")
    print()

    # Initialize Notion client
    notion_client = NotionClient()

    total_cleaned = 0

    # 1. Clean accounts
    print("🏢 CLEANING ACCOUNTS")
    print("-" * 30)
    accounts_cleaned = 0

    for company_name in GPU_TEST_COMPANIES:
        try:
            account_id = notion_client._find_existing_account(company_name)
            if account_id:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{account_id}",
                    headers=notion_client.headers,
                    json={"archived": True}
                )
                print(f"   ✅ Archived account: {company_name}")
                accounts_cleaned += 1
            else:
                print(f"   ❌ No account found: {company_name}")
        except Exception as e:
            print(f"   ⚠️  Error cleaning {company_name}: {e}")

    # 2. Clean contacts
    print("\n👥 CLEANING CONTACTS")
    print("-" * 30)
    contacts_cleaned = 0

    # Get all contacts and filter by test companies
    url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['contacts']}/query"
    contacts_response = notion_client._make_request('POST', url, json={})
    all_contacts = contacts_response.json().get('results', [])

    for contact in all_contacts:
        props = contact.get('properties', {})

        # Extract company name safely
        company = 'Unknown'
        try:
            company_field = props.get('Company', {}).get('rich_text', [])
            if company_field and len(company_field) > 0:
                company = company_field[0].get('text', {}).get('content', 'Unknown')
        except:
            pass

        # Check if this contact belongs to a test company
        if company in GPU_TEST_COMPANIES:
            try:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{contact['id']}",
                    headers=notion_client.headers,
                    json={"archived": True}
                )
                print(f"   ✅ Archived contact from {company}")
                contacts_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error archiving contact from {company}: {e}")

    # 3. Clean trigger events
    print("\n🎯 CLEANING TRIGGER EVENTS")
    print("-" * 30)
    events_cleaned = 0

    url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['trigger_events']}/query"
    events_response = notion_client._make_request('POST', url, json={})
    all_events = events_response.json().get('results', [])

    for event in all_events:
        props = event.get('properties', {})

        # Extract company name safely
        company = 'Unknown'
        try:
            company_field = props.get('Company', {}).get('rich_text', [])
            if company_field and len(company_field) > 0:
                company = company_field[0].get('text', {}).get('content', 'Unknown')
        except:
            pass

        if company in GPU_TEST_COMPANIES:
            try:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{event['id']}",
                    headers=notion_client.headers,
                    json={"archived": True}
                )
                print(f"   ✅ Archived event from {company}")
                events_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error archiving event from {company}: {e}")

    # 4. Clean partnerships
    print("\n🤝 CLEANING PARTNERSHIPS")
    print("-" * 30)
    partnerships_cleaned = 0

    url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['partnerships']}/query"
    partnerships_response = notion_client._make_request('POST', url, json={})
    all_partnerships = partnerships_response.json().get('results', [])

    for partnership in all_partnerships:
        props = partnership.get('properties', {})

        # Extract company name safely
        company = 'Unknown'
        try:
            company_field = props.get('Company Name', {}).get('rich_text', [])
            if company_field and len(company_field) > 0:
                company = company_field[0].get('text', {}).get('content', 'Unknown')
        except:
            pass

        if company in GPU_TEST_COMPANIES:
            try:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{partnership['id']}",
                    headers=notion_client.headers,
                    json={"archived": True}
                )
                print(f"   ✅ Archived partnership from {company}")
                partnerships_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error archiving partnership from {company}: {e}")

    # SUMMARY
    total_cleaned = accounts_cleaned + contacts_cleaned + events_cleaned + partnerships_cleaned
    print(f"\n📊 EMERGENCY CLEANUP SUMMARY")
    print("=" * 40)
    print(f"🏢 Accounts archived: {accounts_cleaned}")
    print(f"👥 Contacts archived: {contacts_cleaned}")
    print(f"🎯 Events archived: {events_cleaned}")
    print(f"🤝 Partnerships archived: {partnerships_cleaned}")
    print(f"📋 TOTAL items cleaned: {total_cleaned}")
    print()
    print("🎉 Production database is clean again!")
    print("⚠️  NEXT: Use TestModeABMSystem for all future testing!")

if __name__ == "__main__":
    emergency_gpu_test_cleanup()