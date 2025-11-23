#!/usr/bin/env python3
"""Quick test to verify Notion API access"""

import os
import requests

# Test both API keys
notion_api_key = os.getenv('NOTION_API_KEY')
notion_abm_api_key = os.getenv('NOTION_ABM_API_KEY')
contacts_db_id = os.getenv('NOTION_CONTACTS_DB_ID')

print("🔍 Testing Notion API Access")
print(f"NOTION_API_KEY: {'✓' if notion_api_key else '✗'}")
print(f"NOTION_ABM_API_KEY: {'✓' if notion_abm_api_key else '✗'}")
print(f"CONTACTS_DB_ID: {contacts_db_id}")

def test_api_key(api_key, key_name):
    """Test if an API key can access the contacts database"""
    if not api_key:
        print(f"❌ {key_name}: Not found")
        return False

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    # Try to query the database
    url = f'https://api.notion.com/v1/databases/{contacts_db_id}/query'
    try:
        response = requests.post(url, headers=headers, json={'page_size': 1})
        if response.status_code == 200:
            print(f"✅ {key_name}: Can access contacts database")
            return True
        else:
            print(f"❌ {key_name}: {response.status_code} - {response.json().get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ {key_name}: Exception - {e}")
        return False

print("\n🧪 Testing API Access...")
test_api_key(notion_api_key, "NOTION_API_KEY")
test_api_key(notion_abm_api_key, "NOTION_ABM_API_KEY")