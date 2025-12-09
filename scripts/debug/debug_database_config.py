#!/usr/bin/env python3
"""
Debug Database Configuration Script

Tests database ID configuration and Notion save functionality
to identify why accounts are marked as "failed" in main output
while internal logs claim success.
"""

import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

import logging

from abm_research.config.settings import (
    NOTION_ACCOUNTS_DB_ID,
    NOTION_CONTACTS_DB_ID,
    NOTION_PARTNERSHIPS_DB_ID,
    NOTION_TRIGGER_EVENTS_DB_ID,
)
from abm_research.integrations.notion_client import NotionClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def debug_database_configuration():
    """Debug database configuration and test Notion connectivity"""

    print("🔍 Database Configuration Debug")
    print("=" * 50)

    # 1. Check environment variables
    print("📋 Environment Variables:")
    env_vars = [
        ("NOTION_ACCOUNTS_DB_ID", NOTION_ACCOUNTS_DB_ID),
        ("NOTION_CONTACTS_DB_ID", NOTION_CONTACTS_DB_ID),
        ("NOTION_TRIGGER_EVENTS_DB_ID", NOTION_TRIGGER_EVENTS_DB_ID),
        ("NOTION_PARTNERSHIPS_DB_ID", NOTION_PARTNERSHIPS_DB_ID),
    ]

    for var_name, var_value in env_vars:
        if var_value:
            print(f"   ✅ {var_name}: {var_value}")
        else:
            print(f"   ❌ {var_name}: NOT SET")
    print()

    # 2. Test Notion client initialization
    print("🔧 Notion Client Initialization:")
    try:
        notion_client = NotionClient()
        print("   ✅ Client initialized successfully")
        print("   🗂️  Database IDs configured:")
        for db_name, db_id in notion_client.database_ids.items():
            print(f"      {db_name}: {db_id}")
        print()
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return False

    # 3. Test account save functionality
    print("💾 Testing Account Save:")
    test_account = {
        "name": "Database Config Test Company",
        "domain": "dbtest.com",
        "business_model": "Technology",
        "employee_count": 50,
        "icp_fit_score": 70,
        "research_status": "In Progress",
        "notes": "Testing database configuration",
    }

    try:
        account_id = notion_client.save_account(test_account)
        if account_id and isinstance(account_id, str):
            print(f"   ✅ Account save SUCCESS: {account_id[:20]}...")
            print(f"   ✅ Return type: {type(account_id)}")

            # Test finding the account
            found_id = notion_client._find_existing_account(test_account["name"])
            if found_id:
                print(f"   ✅ Account retrieval SUCCESS: {found_id[:20]}...")
            else:
                print("   ⚠️  Account save succeeded but retrieval failed")

        else:
            print(f"   ❌ Account save FAILED: {account_id} (type: {type(account_id)})")
            return False

    except Exception as e:
        print(f"   ❌ Account save ERROR: {e}")
        return False

    # 4. Test database connectivity for each database
    print("🔗 Testing Database Connectivity:")
    for db_name, db_id in notion_client.database_ids.items():
        if db_id:
            try:
                url = f"https://api.notion.com/v1/databases/{db_id}/query"
                response = notion_client._make_request("POST", url, json={"page_size": 1})
                if response.status_code == 200:
                    print(f"   ✅ {db_name}: Connected successfully")
                else:
                    print(f"   ❌ {db_name}: Failed (status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ {db_name}: Error - {e}")
        else:
            print(f"   ❌ {db_name}: No database ID configured")

    print()
    print("✅ Database configuration debug complete!")
    return True


if __name__ == "__main__":
    success = debug_database_configuration()
    exit(0 if success else 1)
