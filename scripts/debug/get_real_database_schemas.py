#!/usr/bin/env python3
"""
Get Real Database Schemas

Query the actual Notion databases to see what fields they really have.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient

def get_real_schemas():
    """Get the actual field names from all databases"""

    print("🔍 GETTING REAL DATABASE SCHEMAS")
    print("=" * 60)

    client = NotionClient()

    databases = [
        ('accounts', 'Accounts'),
        ('contacts', 'Contacts'),
        ('trigger_events', 'Trigger Events'),
        ('partnerships', 'Partnerships')
    ]

    for db_key, db_name in databases:
        db_id = client.database_ids.get(db_key)
        if not db_id:
            print(f"❌ {db_name}: No database ID configured")
            continue

        print(f"\n📊 {db_name.upper()} DATABASE SCHEMA:")
        print(f"   ID: {db_id}")
        print("   Fields:")

        try:
            response = client._make_request(
                'GET',
                f"https://api.notion.com/v1/databases/{db_id}"
            )

            if response.status_code == 200:
                db_data = response.json()
                properties = db_data.get('properties', {})

                for field_name, field_config in properties.items():
                    field_type = field_config.get('type', 'unknown')
                    print(f"      • '{field_name}' ({field_type})")

                print(f"   ✅ Total fields: {len(properties)}")

            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    get_real_schemas()