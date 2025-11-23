#!/usr/bin/env python3
"""
Notion Integration Permission Test
Test if the API integration has the right permissions for the databases
"""

import os
import requests
import json

def test_notion_integration_permissions():
    """Test if the integration has proper database access permissions"""

    print("🔐 NOTION INTEGRATION PERMISSION TEST")
    print("=" * 50)

    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    print(f"✅ Testing integration: {api_key[:15]}...{api_key[-4:]}")

    # Test 1: Check what we can search for
    print(f"\n🔍 TEST 1: Search for accessible content...")

    search_url = "https://api.notion.com/v1/search"
    search_payload = {
        "filter": {
            "value": "database",
            "property": "object"
        },
        "page_size": 10
    }

    try:
        response = requests.post(search_url, headers=headers, json=search_payload)
        print(f"   Search Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            databases = data.get('results', [])
            print(f"   ✅ Found {len(databases)} accessible databases")

            for db in databases[:3]:  # Show first 3
                db_id = db.get('id', '')
                title = ''
                if db.get('title'):
                    title = ' '.join([t.get('plain_text', '') for t in db['title']])
                print(f"      📊 {title}: {db_id}")
        else:
            print(f"   ❌ Search failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Search error: {e}")

    # Test 2: Try to retrieve integration details
    print(f"\n🔍 TEST 2: Check integration bot info...")

    # Get bot user info
    bot_url = "https://api.notion.com/v1/users/me"
    try:
        response = requests.get(bot_url, headers=headers)
        print(f"   Bot Info Status: {response.status_code}")

        if response.status_code == 200:
            bot_data = response.json()
            bot_name = bot_data.get('name', 'Unknown')
            bot_type = bot_data.get('type', 'Unknown')
            print(f"   ✅ Integration: {bot_name} (type: {bot_type})")
        else:
            print(f"   ❌ Bot info failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Bot info error: {e}")

    # Test 3: Test specific database with detailed error
    print(f"\n🔍 TEST 3: Detailed database access test...")

    test_db_id = "c31d728f477049e28f6bd68717e2c160"  # Accounts database
    db_url = f"https://api.notion.com/v1/databases/{test_db_id}"

    try:
        response = requests.get(db_url, headers=headers)
        print(f"   Database Retrieve Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ Can access database schema")
        elif response.status_code == 404:
            print(f"   ❌ Database not found or integration lacks permission")
            print(f"   💡 SOLUTION: Add this integration to the database in Notion:")
            print(f"      1. Open: https://www.notion.so/verdigris/{test_db_id}")
            print(f"      2. Click the '•••' menu (top right)")
            print(f"      3. Select 'Add connections'")
            print(f"      4. Add your integration to grant access")
        else:
            error_data = response.json()
            print(f"   ❌ Error: {error_data}")

    except Exception as e:
        print(f"   ❌ Database test error: {e}")

    # Test 4: List all pages (to see what we can access)
    print(f"\n🔍 TEST 4: List accessible pages...")

    search_pages_payload = {
        "filter": {
            "value": "page",
            "property": "object"
        },
        "page_size": 5
    }

    try:
        response = requests.post(search_url, headers=headers, json=search_pages_payload)
        print(f"   Pages Search Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            pages = data.get('results', [])
            print(f"   ✅ Found {len(pages)} accessible pages")

            for page in pages[:3]:
                page_id = page.get('id', '')
                title = 'Untitled'
                if page.get('properties', {}).get('title'):
                    title_prop = page['properties']['title']
                    if isinstance(title_prop, dict) and 'title' in title_prop:
                        title = ' '.join([t.get('plain_text', '') for t in title_prop['title']])

                print(f"      📄 {title}: {page_id}")
        else:
            print(f"   ❌ Pages search failed: {response.text}")

    except Exception as e:
        print(f"   ❌ Pages search error: {e}")

    print(f"\n💡 NEXT STEPS IF 404 ERRORS:")
    print(f"   1. The integration exists and works (✅ found 82 users)")
    print(f"   2. But it can't access your specific databases (❌ 404 errors)")
    print(f"   3. You need to explicitly grant access to each database:")
    print(f"      • Open each database in Notion")
    print(f"      • Click '•••' → 'Add connections'")
    print(f"      • Add your ABM Research integration")
    print(f"   4. After granting access, the databases will be accessible via API")

if __name__ == "__main__":
    test_notion_integration_permissions()