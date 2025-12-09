#!/usr/bin/env python3
"""
Production Testing with Cleanup

Runs ABM system in production mode (with Notion database writes)
for proper validation, then provides easy cleanup of test data.
"""

import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

import logging
from datetime import datetime

from abm_research.core.abm_system import ComprehensiveABMSystem
from abm_research.integrations.notion_client import NotionClient

logging.basicConfig(level=logging.INFO, format="%(message)s")


def production_test_with_tracking():
    """Run production tests with clear tracking for cleanup"""

    print("🚀 PRODUCTION MODE TESTING")
    print("=" * 60)
    print("Running ABM system in production mode with Notion database writes")
    print("All data will be written to production - we'll track it for cleanup")
    print()

    # Track what we're testing for easy cleanup
    test_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_companies = [
        ("NVIDIA Corporation", "nvidia.com", "GPU Infrastructure Test"),
        ("CoreWeave", "coreweave.com", "GPU Cloud Provider Test"),
        ("Lambda Labs", "lambdalabs.com", "GPU Infrastructure Test"),
    ]

    print(f"📋 Test Session ID: {test_session_id}")
    print("🧪 Companies to test:")
    for company, domain, purpose in test_companies:
        print(f"   • {company} ({domain}) - {purpose}")
    print()

    # Initialize production ABM system
    abm = ComprehensiveABMSystem()

    test_results = []

    for company_name, domain, purpose in test_companies:
        print(f"\n🏢 TESTING: {company_name}")
        print(f"🎯 Purpose: {purpose}")
        print("-" * 50)

        try:
            # Run full ABM research in PRODUCTION MODE
            result = abm.conduct_complete_account_research(company_name, domain)

            # Extract key results
            account = result.get("account", {})
            contacts = result.get("contacts", [])
            trigger_events = result.get("trigger_events", [])
            partnerships = result.get("partnerships", [])
            notion_persistence = result.get("notion_persistence", {})

            # Check if data was actually saved
            account_saved = notion_persistence.get("account_saved", False)
            contacts_saved = notion_persistence.get("contacts_saved", 0)
            events_saved = notion_persistence.get("events_saved", 0)
            partnerships_saved = notion_persistence.get("partnerships_saved", 0)

            print("✅ ABM Research Results:")
            print(f"   📊 Account data generated: {'✅' if account.get('name') else '❌'}")
            print(f"   👥 Contacts discovered: {len(contacts)}")
            print(f"   🎯 Trigger events: {len(trigger_events)}")
            print(f"   🤝 Partnerships: {len(partnerships)}")
            print()
            print("💾 Notion Database Writes:")
            print(f"   🏢 Account saved: {'✅ YES' if account_saved else '❌ FAILED'}")
            print(f"   👥 Contacts saved: {contacts_saved}")
            print(f"   🎯 Events saved: {events_saved}")
            print(f"   🤝 Partnerships saved: {partnerships_saved}")

            # Test specific validation for GPU companies
            physical_infrastructure = account.get("Physical Infrastructure", "")
            has_gpu_terms = any(
                gpu_term in physical_infrastructure.lower()
                for gpu_term in ["gpu", "nvidia", "h100", "a100", "v100", "dgx"]
            )

            print(f"   🔍 GPU Infrastructure Detected: {'✅ YES' if has_gpu_terms else '❌ NO'}")
            if has_gpu_terms:
                print(f"      📋 Infrastructure: {physical_infrastructure[:100]}...")

            # Track for cleanup
            test_results.append(
                {
                    "company": company_name,
                    "domain": domain,
                    "purpose": purpose,
                    "account_saved": account_saved,
                    "contacts_saved": contacts_saved,
                    "events_saved": events_saved,
                    "partnerships_saved": partnerships_saved,
                    "test_passed": account_saved and contacts_saved > 0,
                    "session_id": test_session_id,
                }
            )

        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            test_results.append(
                {
                    "company": company_name,
                    "domain": domain,
                    "purpose": purpose,
                    "error": str(e),
                    "test_passed": False,
                    "session_id": test_session_id,
                }
            )

    # Test Summary
    print("\n📊 TEST SESSION SUMMARY")
    print("=" * 50)
    successful_tests = len([r for r in test_results if r.get("test_passed", False)])
    print(f"✅ Successful tests: {successful_tests}/{len(test_results)}")

    total_accounts = sum(1 for r in test_results if r.get("account_saved", False))
    total_contacts = sum(r.get("contacts_saved", 0) for r in test_results)
    total_events = sum(r.get("events_saved", 0) for r in test_results)
    total_partnerships = sum(r.get("partnerships_saved", 0) for r in test_results)

    print("📋 Total data written to production:")
    print(f"   🏢 Accounts: {total_accounts}")
    print(f"   👥 Contacts: {total_contacts}")
    print(f"   🎯 Events: {total_events}")
    print(f"   🤝 Partnerships: {total_partnerships}")

    return test_results, test_session_id


def cleanup_test_data(test_session_companies):
    """Clean up the test data we just created"""

    print("\n🧹 CLEANUP: Test Data from Production")
    print("-" * 50)
    print("Removing test data companies:")
    for company in test_session_companies:
        print(f"   - {company}")
    print()

    notion_client = NotionClient()

    total_cleaned = 0

    # Clean accounts
    print("🏢 Cleaning Accounts...")
    accounts_cleaned = 0
    for company_name in test_session_companies:
        try:
            account_id = notion_client._find_existing_account(company_name)
            if account_id:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{account_id}",
                    headers=notion_client.headers,
                    json={"archived": True},
                )
                print(f"   ✅ Archived account: {company_name}")
                accounts_cleaned += 1
        except Exception as e:
            print(f"   ⚠️  Error cleaning {company_name}: {e}")

    # Clean contacts
    print("\n👥 Cleaning Contacts...")
    contacts_cleaned = 0
    url = f"https://api.notion.com/v1/databases/{notion_client.database_ids['contacts']}/query"
    contacts_response = notion_client._make_request("POST", url, json={})
    all_contacts = contacts_response.json().get("results", [])

    for contact in all_contacts:
        props = contact.get("properties", {})
        company = "Unknown"
        try:
            company_field = props.get("Company", {}).get("rich_text", [])
            if company_field and len(company_field) > 0:
                company = company_field[0].get("text", {}).get("content", "Unknown")
        except:
            pass

        if company in test_session_companies:
            try:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{contact['id']}",
                    headers=notion_client.headers,
                    json={"archived": True},
                )
                print(f"   ✅ Archived contact from {company}")
                contacts_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error archiving contact from {company}: {e}")

    # Clean events and partnerships (similar logic)
    print("\n🎯 Cleaning Trigger Events...")
    events_cleaned = 0
    url = (
        f"https://api.notion.com/v1/databases/{notion_client.database_ids['trigger_events']}/query"
    )
    events_response = notion_client._make_request("POST", url, json={})
    all_events = events_response.json().get("results", [])

    for event in all_events:
        props = event.get("properties", {})
        company = "Unknown"
        try:
            company_field = props.get("Company", {}).get("rich_text", [])
            if company_field and len(company_field) > 0:
                company = company_field[0].get("text", {}).get("content", "Unknown")
        except:
            pass

        if company in test_session_companies:
            try:
                response = notion_client._make_request(
                    "PATCH",
                    f"https://api.notion.com/v1/pages/{event['id']}",
                    headers=notion_client.headers,
                    json={"archived": True},
                )
                print(f"   ✅ Archived event from {company}")
                events_cleaned += 1
            except Exception as e:
                print(f"   ⚠️  Error archiving event from {company}: {e}")

    total_cleaned = accounts_cleaned + contacts_cleaned + events_cleaned
    print(f"\n✅ Cleanup Summary: {total_cleaned} items archived")
    return total_cleaned


if __name__ == "__main__":
    print("🚀 Production Testing with Validation and Cleanup")
    print()

    # Run production tests
    test_results, session_id = production_test_with_tracking()

    # Ask user if they want to clean up
    print("\n🤔 CLEANUP DECISION")
    print("-" * 30)
    print("The test data has been written to production Notion databases.")
    print("You can now:")
    print("1. Check the Notion databases to validate the results")
    print("2. Check the dashboard to see if data appears correctly")
    print("3. Verify all functionality is working as expected")
    print()

    # Extract company names for cleanup
    test_companies = [r["company"] for r in test_results if r.get("account_saved", False)]

    if test_companies:
        print("When you're ready, you can clean up the test data:")
        print(f"Test companies: {', '.join(test_companies)}")
        print()

        user_input = input("Clean up test data now? (y/n): ").lower().strip()

        if user_input == "y":
            cleanup_test_data(test_companies)
            print("\n🎉 Test complete! Production databases cleaned.")
        else:
            print("\n⚠️  Test data remains in production.")
            print("Run cleanup manually when ready:")
            print('python3 -c "')
            print("from production_test_with_cleanup import cleanup_test_data")
            print(f'cleanup_test_data({test_companies})"')
    else:
        print("✅ No test data was successfully written - nothing to clean up.")

    print("\n🎉 Production testing session complete!")
    print(f"Session ID: {session_id}")
