#!/usr/bin/env python3
"""
Debug ABM Account Save Issues

Tests account save functionality in the exact context of the ABM system
to identify why account_saved status reports False when saves actually work.
"""

import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

from abm_research.integrations.notion_client import NotionClient
from abm_research.core.abm_system import ComprehensiveABMSystem
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def debug_abm_account_save():
    """Debug ABM account save vs direct account save"""

    print("🔍 ABM Account Save Debug")
    print("=" * 50)

    # Initialize both systems
    print("🔧 Initializing systems...")
    notion_client = NotionClient()
    abm_system = ComprehensiveABMSystem()
    print()

    # Test 1: Direct account save (we know this works)
    print("📋 Test 1: Direct Account Save (Known Working)")
    print("-" * 50)

    direct_account = {
        "name": "Direct Save Test Company",
        "domain": "directtest.com",
        "business_model": "Technology",
        "employee_count": 75,
        "icp_fit_score": 80,
        "research_status": "In Progress",
        "notes": "Testing direct account save",
    }

    try:
        direct_account_id = notion_client.save_account(direct_account)
        print(f"   ✅ Direct save result: {direct_account_id} (type: {type(direct_account_id)})")
        print(f"   ✅ Direct save bool: {bool(direct_account_id)}")
    except Exception as e:
        print(f"   ❌ Direct save failed: {e}")
        return False
    print()

    # Test 2: ABM-style account data structure
    print("📋 Test 2: ABM Account Data Format Test")
    print("-" * 50)

    # Let's create a minimal ABM research result to test the save
    print("   🧪 Running minimal ABM research for comparison...")
    try:
        # Use a simple, clean test case
        result = abm_system.conduct_complete_account_research("ABM Test Company", "abmtest.com")

        print(f"   📊 ABM Research completed")
        account_data = result.get("account", {})
        saved_status = result.get("saved_to_notion", {})

        print(f"   📋 Account data keys: {list(account_data.keys())}")
        print(f"   📋 Account name: {account_data.get('name', 'NOT FOUND')}")
        print(f"   📋 Save status: {saved_status}")

        # Test the exact account data that ABM generated
        if account_data:
            print("   🔧 Testing save with ABM-generated account data...")
            abm_account_id = notion_client.save_account(account_data)
            print(f"   📊 ABM account save result: {abm_account_id} (type: {type(abm_account_id)})")
            print(f"   📊 ABM account save bool: {bool(abm_account_id)}")

            # Compare the account data formats
            print("   🔍 Comparing account data formats:")
            print(f"      Direct account keys: {list(direct_account.keys())}")
            print(f"      ABM account keys: {list(account_data.keys())}")

            # Check for required fields
            required_fields = ["name", "domain"]
            for field in required_fields:
                direct_val = direct_account.get(field)
                abm_val = account_data.get(field)
                print(f"      {field}: Direct='{direct_val}' vs ABM='{abm_val}'")
        else:
            print(f"   ❌ ABM research returned no account data")

    except Exception as e:
        print(f"   ❌ ABM research failed: {e}")
        return False
    print()

    # Test 3: Examine the ABM save method directly
    print("📋 Test 3: ABM Save Method Direct Test")
    print("-" * 50)

    # Look at what the ABM system's save_research_to_notion method does
    try:
        print("   🔧 Testing ABM save_research_to_notion method...")

        # Create a mock research result with the same structure as ABM produces
        mock_research_result = {
            "account": {
                "name": "Mock ABM Account",
                "domain": "mockabm.com",
                "business_model": "Technology Company",
                "employee_count": None,
                "icp_fit_score": 60,
                "research_status": "Completed",
            },
            "contacts": [],
            "trigger_events": [],
            "partnerships": [],
        }

        # Call the ABM system's save method directly
        save_results = abm_system.save_research_to_notion(mock_research_result)

        print(f"   📊 ABM save_research_to_notion result: {save_results}")
        print(f"   📊 Account saved status: {save_results.get('account_saved', 'NOT FOUND')}")

        # Also test if the account was actually saved
        saved_account_id = notion_client._find_existing_account("Mock ABM Account")
        print(f"   🔍 Account actually exists in Notion: {bool(saved_account_id)}")
        if saved_account_id:
            print(f"   📋 Found account ID: {saved_account_id[:20]}...")

    except Exception as e:
        print(f"   ❌ ABM save method test failed: {e}")
        return False

    print()
    print("✅ ABM account save debug complete!")
    return True


if __name__ == "__main__":
    success = debug_abm_account_save()
    exit(0 if success else 1)
