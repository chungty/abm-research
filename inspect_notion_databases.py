"""
Inspect and Fix Notion Database Properties
Check what properties actually exist and fix any issues
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
import json

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def inspect_databases():
    """Inspect the actual database properties"""

    database_ids = {
        'accounts': 'c31d728f-4770-49e2-8f6b-d68717e2c160',
        'trigger_events': 'c8ae1662-cba9-4ea3-9cb3-2bcea3621963',
        'contacts': 'a6e0cace-85de-4afd-be6c-9c926d1d0e3d',
        'partnerships': 'fa1467c0-ad15-4b09-bb03-cc715f9b8577'
    }

    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return

    client = Client(auth=api_key)

    for db_name, db_id in database_ids.items():
        print(f"\n🔍 Inspecting {db_name.upper()} database:")
        print(f"   Database ID: {db_id}")

        try:
            db_info = client.databases.retrieve(database_id=db_id)
            properties = db_info['properties']

            print(f"   ✅ Found {len(properties)} properties:")
            for prop_name, prop_config in properties.items():
                prop_type = prop_config['type']
                print(f"      • {prop_name} ({prop_type})")

                # Show select options if it's a select property
                if prop_type == 'select' and 'select' in prop_config:
                    options = prop_config['select'].get('options', [])
                    if options:
                        option_names = [opt['name'] for opt in options]
                        print(f"        Options: {', '.join(option_names)}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def create_sample_account():
    """Create sample account with correct property names"""

    database_ids = {
        'accounts': 'c31d728f-4770-49e2-8f6b-d68717e2c160',
        'trigger_events': 'c8ae1662-cba9-4ea3-9cb3-2bcea3621963',
        'contacts': 'a6e0cace-85de-4afd-be6c-9c926d1d0e3d',
        'partnerships': 'fa1467c0-ad15-4b09-bb03-cc715f9b8577'
    }

    api_key = os.getenv('NOTION_ABM_API_KEY')
    client = Client(auth=api_key)

    print("\n📊 Creating Genesis Cloud Infrastructure account...")

    try:
        # Create account with correct properties
        account_data = {
            "Company Name": {
                "title": [{"text": {"content": "Genesis Cloud Infrastructure"}}]
            },
            "Domain": {
                "rich_text": [{"text": {"content": "genesis-cloud.com"}}]
            },
            "Employee Count": {"number": 450},
            "Business Model": {"select": {"name": "Cloud Provider"}},
            "ICP Fit Score": {"number": 88.0},
            "Account Research Status": {"select": {"name": "Complete"}},
            "Last Updated": {"date": {"start": "2024-11-20"}}
        }

        account_page = client.pages.create(
            parent={"type": "database_id", "database_id": database_ids['accounts']},
            properties=account_data
        )

        account_id = account_page['id']
        print(f"✅ Account created: {account_id}")
        return account_id

    except Exception as e:
        print(f"❌ Account creation failed: {str(e)}")
        return None

if __name__ == "__main__":
    inspect_databases()

    print("\n" + "="*50)
    print("🔧 Attempting to create sample account...")
    create_sample_account()