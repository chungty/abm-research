#!/usr/bin/env python3
"""Debug the actual Notion API issue"""

import os
import requests
import json

def test_notion_access():
    print("🔍 Debugging Notion API Access")

    # Get all the API keys
    abm_key = os.getenv('NOTION_ABM_API_KEY')
    regular_key = os.getenv('NOTION_API_KEY')
    contacts_db = os.getenv('NOTION_CONTACTS_DB_ID')

    print(f"ABM Key: {abm_key[:20]}... (length: {len(abm_key)})")
    print(f"Regular Key: {regular_key[:20]}... (length: {len(regular_key)})")
    print(f"Contacts DB: {contacts_db}")

    # Test both keys with detailed error reporting
    for key_name, api_key in [("NOTION_ABM_API_KEY", abm_key), ("NOTION_API_KEY", regular_key)]:
        print(f"\n🧪 Testing {key_name}")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

        # Test 1: Can we access the user info?
        try:
            resp = requests.get('https://api.notion.com/v1/users/me', headers=headers)
            if resp.status_code == 200:
                user_info = resp.json()
                print(f"  ✅ User access: {user_info.get('name', 'No name')} ({user_info.get('type', 'unknown')})")
            else:
                print(f"  ❌ User access failed: {resp.status_code} - {resp.text}")
                continue
        except Exception as e:
            print(f"  ❌ User access error: {e}")
            continue

        # Test 2: Can we query the contacts database?
        try:
            resp = requests.post(
                f'https://api.notion.com/v1/databases/{contacts_db}/query',
                headers=headers,
                json={'page_size': 1}
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"  ✅ Database access: Found {len(data.get('results', []))} contacts")
            else:
                error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
                print(f"  ❌ Database access failed: {resp.status_code}")
                print(f"     Error: {json.dumps(error_data, indent=2)}")
        except Exception as e:
            print(f"  ❌ Database access error: {e}")

        # Test 3: Can we get database info?
        try:
            resp = requests.get(f'https://api.notion.com/v1/databases/{contacts_db}', headers=headers)
            if resp.status_code == 200:
                db_info = resp.json()
                print(f"  ✅ Database info: {db_info.get('title', [{}])[0].get('plain_text', 'No title')}")
                print(f"     Properties: {len(db_info.get('properties', {}))}")
            else:
                error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
                print(f"  ❌ Database info failed: {resp.status_code}")
                print(f"     Error: {json.dumps(error_data, indent=2)}")
        except Exception as e:
            print(f"  ❌ Database info error: {e}")

if __name__ == "__main__":
    test_notion_access()