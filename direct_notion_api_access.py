#!/usr/bin/env python3
"""
Direct Notion API Access
Try accessing the Notion API directly without the client library
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def test_direct_api_access():
    """Test direct API access to your parent page and databases"""

    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    parent_page_id = "2b27f5fee5e2801cad6ee1771d29dc48"

    print("🔍 TESTING DIRECT NOTION API ACCESS")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    print(f"Parent Page ID: {parent_page_id}")

    # Test 1: Try to access the parent page directly
    print(f"\n📄 TEST 1: ACCESSING PARENT PAGE")
    print("-" * 30)

    try:
        url = f"https://api.notion.com/v1/pages/{parent_page_id}"
        response = requests.get(url, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully accessed parent page!")
            print(f"Page Object Type: {data.get('object')}")

            # Print page title if available
            if 'properties' in data and 'title' in data['properties']:
                title_property = data['properties']['title']
                if title_property.get('title'):
                    title_texts = title_property['title']
                    if title_texts:
                        title = ''.join([text['plain_text'] for text in title_texts])
                        print(f"Page Title: {title}")

        else:
            print(f"❌ Failed to access parent page")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ API request failed: {e}")

    # Test 2: Try to get child blocks (databases) of the parent page
    print(f"\n📊 TEST 2: GETTING CHILD BLOCKS (DATABASES)")
    print("-" * 30)

    try:
        url = f"https://api.notion.com/v1/blocks/{parent_page_id}/children"
        response = requests.get(url, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Found {len(results)} child blocks")

            databases_found = []
            for block in results:
                if block.get('type') == 'child_database':
                    db_id = block['id']
                    title = block['child_database'].get('title', 'Untitled')

                    print(f"📋 Database: {title}")
                    print(f"   ID: {db_id}")
                    print(f"   URL: https://www.notion.so/{db_id.replace('-', '')}")

                    databases_found.append({
                        'id': db_id,
                        'title': title
                    })

            if databases_found:
                print(f"\n📋 SUMMARY: Found {len(databases_found)} databases")
                return databases_found
            else:
                print(f"⚠️ No databases found in child blocks")

        else:
            print(f"❌ Failed to get child blocks")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Child blocks request failed: {e}")

    # Test 3: Try to access a database directly (if we have IDs)
    print(f"\n🔍 TEST 3: TESTING DATABASE ACCESS")
    print("-" * 30)

    # Let's try some common database IDs from earlier attempts
    test_db_ids = databases_found if 'databases_found' in locals() else []

    for db_info in test_db_ids[:2]:  # Test first 2 databases
        try:
            db_id = db_info['id']
            title = db_info['title']

            url = f"https://api.notion.com/v1/databases/{db_id}"
            response = requests.get(url, headers=headers, timeout=10)

            print(f"Testing {title}:")
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                properties = data.get('properties', {})
                print(f"   ✅ Accessed! Properties: {len(properties)}")

                # Show first few properties
                for i, (prop_name, prop_config) in enumerate(list(properties.items())[:3]):
                    prop_type = prop_config.get('type', 'unknown')
                    print(f"      • {prop_name} ({prop_type})")

                if len(properties) > 3:
                    print(f"      ... and {len(properties) - 3} more")

            else:
                print(f"   ❌ Failed to access database")
                print(f"   Response: {response.text[:100]}...")

        except Exception as e:
            print(f"   ❌ Database access failed: {e}")

    return []

if __name__ == "__main__":
    databases = test_direct_api_access()

    if databases:
        print(f"\n🎉 SUCCESS! Found {len(databases)} accessible databases")
        print("Ready to enhance with improved schemas!")
    else:
        print(f"\n❌ Could not access databases via direct API")