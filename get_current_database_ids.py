#!/usr/bin/env python3
"""
Get Current Database IDs
Find the actual database IDs to enhance schemas
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_current_database_ids():
    """Get current database IDs from Notion workspace"""

    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return {}

    client = Client(auth=api_key)
    parent_page_id = "2b27f5fee5e2801cad6ee1771d29dc48"

    print("🔍 FINDING CURRENT DATABASE IDs...")
    print("-" * 40)

    try:
        # Get all child pages/databases from parent page
        response = client.blocks.children.list(parent_page_id)

        database_ids = {}

        for block in response['results']:
            if block['type'] == 'child_database':
                title = block['child_database']['title']
                db_id = block['id']

                # Map to our standard names
                if 'account' in title.lower():
                    database_ids['accounts'] = db_id
                elif 'trigger' in title.lower():
                    database_ids['trigger_events'] = db_id
                elif 'contact' in title.lower():
                    database_ids['contacts'] = db_id
                elif 'partnership' in title.lower():
                    database_ids['partnerships'] = db_id

                print(f"   📊 Found: {title}")
                print(f"       ID: {db_id}")

        print(f"\n📋 MAPPED DATABASE IDs:")
        for name, db_id in database_ids.items():
            print(f"   {name}: {db_id}")

        return database_ids

    except Exception as e:
        print(f"❌ Failed to get database IDs: {e}")
        return {}

if __name__ == "__main__":
    database_ids = get_current_database_ids()

    if database_ids:
        print(f"\n✅ Found {len(database_ids)} databases")

        # Generate updated enhancer code with correct IDs
        print(f"\n🔧 UPDATE ENHANCER WITH THESE IDs:")
        print("self.database_ids = {")
        for name, db_id in database_ids.items():
            print(f"    '{name}': '{db_id}',")
        print("}")
    else:
        print("❌ No databases found - may need to recreate them")