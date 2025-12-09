#!/usr/bin/env python3
"""
Quick test to validate the Notion save fix for Phase 1.1
"""
import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

from abm_research.integrations.notion_client import NotionClient


def test_notion_save_fix():
    """Test that account saves now return proper IDs instead of False"""

    # Initialize Notion client
    notion_client = NotionClient()

    # Create a minimal test account to verify save functionality
    test_account = {
        "name": "Test Company Save Fix",
        "domain": "testcompany.com",
        "business_model": "Technology",
        "employee_count": 100,
        "icp_fit_score": 75,
        "research_status": "In Progress",
        "notes": "Testing Notion save fix for Phase 1.1",
    }

    print("🧪 Testing Notion save fix...")

    # Test account creation
    account_id = notion_client.save_account(test_account)

    if account_id and isinstance(account_id, str):
        print(f"✅ SUCCESS: Account created with ID: {account_id[:20]}...")
        print(f"✅ Return type: {type(account_id)} (should be str)")

        # Test account update (save_account automatically handles updates via deduplication)
        test_account["notes"] = "Updated notes - testing update functionality"
        updated_id = notion_client.save_account(test_account)

        if updated_id and isinstance(updated_id, str):
            print(f"✅ SUCCESS: Account updated with ID: {updated_id[:20]}...")
            print(f"✅ Update return type: {type(updated_id)} (should be str)")
            print(f"✅ IDs match: {account_id == updated_id} (should be True for update)")
            print("\n🎉 Phase 1.1 FIX VALIDATED: Notion saves now return proper account IDs!")

            # Clean up test account
            print("📝 Note: Test account left in database for reference")

        else:
            print(f"❌ FAILURE: Account update returned: {updated_id} (type: {type(updated_id)})")
            return False
    else:
        print(f"❌ FAILURE: Account creation returned: {account_id} (type: {type(account_id)})")
        return False

    return True


if __name__ == "__main__":
    success = test_notion_save_fix()
    exit(0 if success else 1)
