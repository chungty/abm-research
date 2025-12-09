#!/usr/bin/env python3
"""
Test Permissions Fix

Quick test to verify Notion integration permissions are working after sharing databases.
"""

import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

import logging

from abm_research.integrations.notion_client import NotionClient

logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_permissions_fix():
    """Test that database permissions are now working"""

    print("🔧 TESTING NOTION PERMISSIONS FIX")
    print("=" * 50)
    print("This test verifies that database sharing permissions are working")
    print()

    notion_client = NotionClient()

    # Test each database for data access
    all_working = True

    for db_name, db_id in notion_client.database_ids.items():
        if db_id is None:
            continue

        print(f"🔍 Testing {db_name} database...")

        try:
            # Try to query database
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            response = notion_client._make_request("POST", url, json={"page_size": 1})

            if response.status_code == 200:
                results = response.json().get("results", [])
                print(f"   ✅ Permission working: Can access {len(results)} items")
            else:
                print(f"   ❌ Permission failed: {response.status_code}")
                print(f"   📄 Error: {response.text}")
                all_working = False

        except Exception as e:
            print(f"   ❌ Error testing database: {e}")
            all_working = False

    print()
    if all_working:
        print("🎉 SUCCESS: All database permissions are working!")
        print("✅ ABM system can now save data to Notion")
        print("✅ You should be able to see data in your database URLs")
        print()
        print("📋 Next steps:")
        print("1. Test ABM system with a real prospect")
        print("2. Check dashboard for data visibility")
        print("3. Verify data appears in Notion databases")
    else:
        print("❌ ISSUE: Some databases still have permission problems")
        print()
        print("📋 Fix steps:")
        print("1. Go to each failing database URL")
        print("2. Click 'Share' → Search 'Account Based Marketing and Sales'")
        print("3. Grant 'Full access' (not just 'View only')")
        print("4. Run this test again")


if __name__ == "__main__":
    test_permissions_fix()
