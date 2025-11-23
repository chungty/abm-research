#!/usr/bin/env python3
"""Check actual Notion database schema"""

import os
import requests
import json

# Use working API key
api_key = os.getenv('NOTION_API_KEY')  # This one works
contacts_db_id = os.getenv('NOTION_CONTACTS_DB_ID')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

print("🔍 Checking Contacts Database Schema")
print(f"Database ID: {contacts_db_id}")

# Get database schema
url = f'https://api.notion.com/v1/databases/{contacts_db_id}'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    db_info = response.json()
    properties = db_info.get('properties', {})

    print(f"\n✅ Found {len(properties)} existing properties:")
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get('type', 'unknown')
        print(f"   📋 {prop_name}: {prop_type}")

    # Check what we need vs what exists
    needed_fields = [
        'Company', 'Engagement Score', 'LinkedIn Data Source',
        'LinkedIn Activity', 'Content Themes', 'Responsibility Keywords',
        'Final Lead Score', 'ICP Fit Score', 'Buying Power Score',
        'Last Enriched', 'LinkedIn URL', 'Connection Pathways'
    ]

    print(f"\n🔍 Field Compatibility Check:")
    missing = []
    existing = []

    for field in needed_fields:
        if field in properties:
            existing.append(field)
            print(f"   ✅ {field}: EXISTS")
        else:
            missing.append(field)
            print(f"   ❌ {field}: MISSING")

    print(f"\n📊 Summary:")
    print(f"   ✅ Existing: {len(existing)} fields")
    print(f"   ❌ Missing: {len(missing)} fields")

    if missing:
        print(f"\n🛠️ Options:")
        print(f"   1. Add missing properties to database")
        print(f"   2. Map to existing fields")
        print(f"   3. Use basic schema only")

else:
    print(f"❌ Error: {response.status_code} - {response.text}")