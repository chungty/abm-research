#!/usr/bin/env python3
"""
Test Database ID Loading

Quick test to see what database IDs are actually being loaded from environment.
"""

import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

from abm_research.integrations.notion_client import NotionClient


def test_database_ids():
    """Test what database IDs are being loaded"""

    print("🔍 TESTING DATABASE ID LOADING")
    print("=" * 50)

    # Check environment variables directly
    print("📋 ENVIRONMENT VARIABLES:")
    env_vars = [
        "NOTION_ACCOUNTS_DB_ID",
        "NOTION_CONTACTS_DB_ID",
        "NOTION_TRIGGER_EVENTS_DB_ID",
        "NOTION_PARTNERSHIPS_DB_ID",
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        print(f"   {var} = {value}")
    print()

    # Check NotionClient loading
    print("🔗 NOTION CLIENT LOADING:")
    try:
        client = NotionClient()
        print("   ✅ NotionClient initialized successfully")
        print(f"   Database config: {client.database_ids}")
        print()

        # Test one database access
        if client.database_ids.get("accounts"):
            print("🧪 TESTING ACCOUNTS DATABASE ACCESS:")
            print(f"   Using ID: {client.database_ids['accounts']}")
            try:
                response = client._make_request(
                    "GET", f"https://api.notion.com/v1/databases/{client.database_ids['accounts']}"
                )
                if response.status_code == 200:
                    db_data = response.json()
                    title = "Untitled"
                    if "title" in db_data and db_data["title"]:
                        title_parts = [
                            t.get("text", {}).get("content", "") for t in db_data["title"]
                        ]
                        title = "".join(title_parts) or "Untitled"
                    print(f"   ✅ Success: Connected to '{title}' database")
                else:
                    print(f"   ❌ Failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("   ❌ No accounts database ID configured")

    except Exception as e:
        print(f"   ❌ Failed to initialize NotionClient: {e}")


if __name__ == "__main__":
    test_database_ids()
