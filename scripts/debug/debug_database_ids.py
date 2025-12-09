#!/usr/bin/env python3
"""
Debug Database ID Issues

Since permissions are correct, investigate if database IDs are wrong or API calls are malformed.
"""

import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

import logging

from abm_research.integrations.notion_client import NotionClient

logging.basicConfig(level=logging.INFO, format="%(message)s")


def debug_database_ids():
    """Debug what's wrong with database ID usage"""

    print("🔍 DEBUGGING DATABASE ID ISSUES")
    print("=" * 60)
    print("Since permissions are correct, investigating database ID mismatches")
    print()

    notion_client = NotionClient()

    print("📋 CONFIGURED DATABASE IDS:")
    for db_name, db_id in notion_client.database_ids.items():
        print(f"   • {db_name}: {db_id}")
    print()

    # Test 1: Compare configured IDs with metadata response IDs
    print("🔍 STEP 1: Verify Database ID Consistency")
    print("-" * 50)

    for db_name, db_id in notion_client.database_ids.items():
        if db_id is None:
            print(f"❌ {db_name}: No database ID configured")
            continue

        print(f"\n🔍 Testing {db_name}...")
        print(f"   Config ID: {db_id}")

        try:
            # Get database metadata
            metadata_response = notion_client._make_request(
                "GET", f"https://api.notion.com/v1/databases/{db_id}"
            )

            if metadata_response.status_code == 200:
                db_data = metadata_response.json()
                actual_id = db_data.get("id", "unknown")
                api_url = db_data.get("url", "No URL")

                print("   ✅ Metadata call works")
                print(f"   API returns ID: {actual_id}")
                print(f"   API returns URL: {api_url}")

                # Check if IDs match (accounting for hyphen differences)
                config_id_clean = db_id.replace("-", "")
                actual_id_clean = actual_id.replace("-", "")

                if config_id_clean == actual_id_clean:
                    print("   ✅ Database IDs match")
                else:
                    print("   ❌ DATABASE ID MISMATCH!")
                    print(f"      Expected: {config_id_clean}")
                    print(f"      Actual:   {actual_id_clean}")

                # Now test the query call with the EXACT ID from metadata
                print(f"   🧪 Testing query with metadata ID: {actual_id}")

                query_response = notion_client._make_request(
                    "POST",
                    f"https://api.notion.com/v1/databases/{actual_id}/query",
                    json={"page_size": 1},
                )

                if query_response.status_code == 200:
                    results = query_response.json().get("results", [])
                    print(f"   ✅ Query works with metadata ID: {len(results)} items")
                else:
                    print(f"   ❌ Query fails even with metadata ID: {query_response.status_code}")
                    print(f"   📄 Error: {query_response.text[:200]}...")

            else:
                print(f"   ❌ Metadata call failed: {metadata_response.status_code}")
                print(f"   📄 Error: {metadata_response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # Test 2: Check if there are multiple databases with same name
    print("\n🔍 STEP 2: Search for Database Name Conflicts")
    print("-" * 50)

    try:
        # Use search API to find databases by title
        search_response = notion_client._make_request(
            "POST",
            "https://api.notion.com/v1/search",
            json={"filter": {"property": "object", "value": "database"}, "page_size": 100},
        )

        if search_response.status_code == 200:
            search_results = search_response.json().get("results", [])
            print(f"🔍 Found {len(search_results)} databases in workspace:")

            for db in search_results:
                title = "Untitled"
                if "title" in db and db["title"]:
                    title_parts = [t.get("text", {}).get("content", "") for t in db["title"]]
                    title = "".join(title_parts) or "Untitled"

                db_id = db.get("id", "unknown")
                created = db.get("created_time", "unknown")

                print(f"   📊 '{title}' (ID: {db_id[:8]}...) created {created[:10]}")

                # Check if this matches our expected databases
                expected_titles = [
                    "🏢 Accounts",
                    "👤 Contacts",
                    "⚡ Trigger Events",
                    "🤝 Strategic Partnerships",
                ]
                if title in expected_titles:
                    print("      ⭐ This is one of our target databases!")

        else:
            print(f"   ❌ Search failed: {search_response.status_code}")

    except Exception as e:
        print(f"   ❌ Search error: {e}")

    # Test 3: Raw API call test
    print("\n🔍 STEP 3: Direct API Authentication Test")
    print("-" * 50)

    try:
        # Test basic API access
        me_response = notion_client._make_request("GET", "https://api.notion.com/v1/users/me")

        if me_response.status_code == 200:
            user_data = me_response.json()
            print("✅ API authentication working")
            print(f"   User: {user_data.get('name', 'Unknown')}")
            print(f"   Type: {user_data.get('type', 'Unknown')}")

            # Check API version and headers
            headers = notion_client.headers
            print(f"   Notion-Version: {headers.get('Notion-Version', 'Not set')}")
            print(f"   Authorization: {'Set' if 'Authorization' in headers else 'Missing'}")

        else:
            print(f"❌ API authentication failed: {me_response.status_code}")

    except Exception as e:
        print(f"❌ API test error: {e}")


if __name__ == "__main__":
    debug_database_ids()
