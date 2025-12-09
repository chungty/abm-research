#!/usr/bin/env python3
"""
Notion Database Access Investigation

Investigates why database URLs don't work and finds the proper way to access databases.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def investigate_database_access():
    """Investigate database access issues and find proper URLs"""

    print("🔍 NOTION DATABASE ACCESS INVESTIGATION")
    print("=" * 60)
    print("Issue: User cannot access databases through provided URLs")
    print("Goal: Find proper database URLs and understand access permissions")
    print()

    notion_client = NotionClient()

    print("📋 DATABASE IDS FROM CONFIG:")
    for db_name, db_id in notion_client.database_ids.items():
        print(f"   • {db_name}: {db_id}")
    print()

    # 1. Try to get database metadata to understand structure
    print("📊 STEP 1: Database Metadata Investigation")
    print("-" * 50)

    for db_name, db_id in notion_client.database_ids.items():
        print(f"\n🔍 Investigating {db_name} database...")

        try:
            # Get database metadata
            response = notion_client._make_request(
                'GET',
                f"https://api.notion.com/v1/databases/{db_id}"
            )

            if response.status_code == 200:
                db_data = response.json()

                # Extract key information
                title = "Unknown"
                if 'title' in db_data and db_data['title']:
                    title_parts = [t.get('text', {}).get('content', '') for t in db_data['title']]
                    title = ''.join(title_parts) or "Untitled"

                url = db_data.get('url', 'No URL found')
                parent = db_data.get('parent', {})
                created_time = db_data.get('created_time', 'Unknown')

                print(f"   ✅ Database found: '{title}'")
                print(f"   📝 Database URL: {url}")
                print(f"   🏠 Parent: {parent}")
                print(f"   📅 Created: {created_time}")

                # Check properties count
                properties = db_data.get('properties', {})
                print(f"   📊 Properties: {len(properties)} fields")

                # Try to construct proper Notion URL
                if url and url != 'No URL found':
                    print(f"   🔗 Shareable URL: {url}")
                else:
                    # Construct URL manually
                    workspace_url = "https://www.notion.so/verdigris"
                    # Remove hyphens from database ID for URL
                    clean_id = db_id.replace('-', '')
                    constructed_url = f"{workspace_url}/{clean_id}"
                    print(f"   🔗 Constructed URL: {constructed_url}")

            else:
                print(f"   ❌ Database access failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")

                if response.status_code == 404:
                    print(f"   ⚠️  Database not found - may be in different workspace or deleted")
                elif response.status_code == 403:
                    print(f"   ⚠️  Access forbidden - integration may lack permissions")

        except Exception as e:
            print(f"   ❌ Error accessing database: {e}")

    # 2. Try to query each database to see if we can access the data
    print(f"\n📊 STEP 2: Database Data Access Test")
    print("-" * 50)

    for db_name, db_id in notion_client.database_ids.items():
        print(f"\n🔍 Testing data access for {db_name}...")

        try:
            # Try to query database
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            response = notion_client._make_request('POST', url, json={'page_size': 5})

            if response.status_code == 200:
                results = response.json().get('results', [])
                total_count = len(results)

                print(f"   ✅ Data access successful: {total_count} items returned")

                if results:
                    # Show first item details
                    first_item = results[0]
                    item_id = first_item.get('id', 'unknown')
                    item_url = first_item.get('url', 'No URL')
                    created_time = first_item.get('created_time', 'Unknown')

                    print(f"   📄 Sample item ID: {item_id}")
                    print(f"   🔗 Sample item URL: {item_url}")

                    # Try to get item title
                    props = first_item.get('properties', {})
                    for prop_name, prop_data in props.items():
                        if prop_data.get('type') == 'title' and prop_data.get('title'):
                            title_parts = [t.get('text', {}).get('content', '') for t in prop_data['title']]
                            title = ''.join(title_parts)
                            if title:
                                print(f"   📝 Sample item title: '{title}'")
                                break
                else:
                    print(f"   ⚠️  Database is empty (no items found)")

            else:
                print(f"   ❌ Data query failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")

        except Exception as e:
            print(f"   ❌ Error querying database: {e}")

    # 3. Check workspace and integration permissions
    print(f"\n🔒 STEP 3: Integration Permissions Check")
    print("-" * 50)

    try:
        # Try to get current user info (tests basic API access)
        response = notion_client._make_request('GET', 'https://api.notion.com/v1/users/me')

        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('name', 'Unknown')
            user_type = user_data.get('type', 'Unknown')

            print(f"   ✅ API access working")
            print(f"   👤 Integration user: {user_name} ({user_type})")
        else:
            print(f"   ❌ Basic API access failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Permission check failed: {e}")

    # 4. Recommendations
    print(f"\n📋 STEP 4: Recommendations")
    print("-" * 40)
    print("Based on the investigation:")
    print()
    print("1. If databases are accessible via API but not browser URLs:")
    print("   → Database URLs may need to include workspace name")
    print("   → Or databases may be private and not shareable")
    print()
    print("2. If 404 errors occurred:")
    print("   → Database IDs in .env may be incorrect")
    print("   → Databases may have been moved or deleted")
    print("   → Check your Notion workspace for actual database locations")
    print()
    print("3. If 403 errors occurred:")
    print("   → Integration needs additional permissions")
    print("   → Databases may not be shared with the integration")
    print()
    print("4. To find correct database URLs:")
    print("   → Go to your Notion workspace manually")
    print("   → Navigate to each database")
    print("   → Copy the actual URL from your browser")
    print("   → These are the URLs that will work for sharing")

if __name__ == "__main__":
    investigate_database_access()
