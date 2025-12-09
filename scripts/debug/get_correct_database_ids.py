#!/usr/bin/env python3
"""
Get Correct Database IDs

Retrieves the full correct database IDs from the workspace to fix the .env file.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_correct_database_ids():
    """Get the actual database IDs from workspace"""

    print("🔍 GETTING CORRECT DATABASE IDS")
    print("=" * 50)

    notion_client = NotionClient()

    try:
        # Search for all databases
        response = notion_client._make_request(
            'POST',
            'https://api.notion.com/v1/search',
            json={
                'filter': {'property': 'object', 'value': 'database'},
                'page_size': 100
            }
        )

        if response.status_code == 200:
            databases = response.json().get('results', [])
            print(f"Found {len(databases)} databases in workspace:")
            print()

            correct_mapping = {}

            for db in databases:
                title = "Untitled"
                if 'title' in db and db['title']:
                    title_parts = [t.get('text', {}).get('content', '') for t in db['title']]
                    title = ''.join(title_parts) or "Untitled"

                db_id = db.get('id', 'unknown')
                url = db.get('url', '')

                print(f"📊 '{title}'")
                print(f"   ID: {db_id}")
                print(f"   URL: {url}")
                print()

                # Map to our expected naming
                if title == 'ABM Accounts':
                    correct_mapping['accounts'] = db_id
                elif title == 'ABM Contacts':
                    correct_mapping['contacts'] = db_id
                elif title == 'ABM Trigger Events':
                    correct_mapping['trigger_events'] = db_id
                elif title == 'ABM Strategic Partnerships':
                    correct_mapping['partnerships'] = db_id

            print("🔧 CORRECT MAPPING FOR .ENV:")
            print("=" * 40)
            for key, db_id in correct_mapping.items():
                env_var = f"NOTION_{key.upper()}_DB_ID"
                print(f"{env_var}={db_id}")

            return correct_mapping

        else:
            print(f"❌ Search failed: {response.status_code}")
            return {}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

if __name__ == "__main__":
    get_correct_database_ids()
