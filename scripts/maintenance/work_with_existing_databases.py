#!/usr/bin/env python3
"""
Work with Existing Notion Databases
Use the existing databases and enhance them with missing schema fields
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime
from abm_config import config

def analyze_existing_database(database_id: str):
    """Analyze the existing database structure"""

    client = config.get_notion_client()

    print(f"🔍 ANALYZING EXISTING DATABASE: {database_id}")
    print("-" * 50)

    try:
        database = client.databases.retrieve(database_id)

        # Get database title
        title = ''
        if database.get('title'):
            title = ''.join([text['plain_text'] for text in database['title']])

        print(f"📊 Database Title: {title}")
        print(f"🆔 Database ID: {database_id}")

        # Get current properties
        current_props = database['properties']
        print(f"📋 Current Properties ({len(current_props)}):")

        for prop_name, prop_config in current_props.items():
            prop_type = prop_config['type']
            print(f"   • {prop_name} ({prop_type})")

        return {
            'id': database_id,
            'title': title,
            'properties': current_props
        }

    except Exception as e:
        print(f"❌ Failed to analyze database: {e}")
        return None

def find_related_databases(parent_page_id: str):
    """Find all databases under the parent page"""

    client = config.get_notion_client()

    print(f"🔍 FINDING RELATED DATABASES...")
    print("-" * 40)

    try:
        # Get child blocks of the parent page
        response = client.blocks.children.list(parent_page_id)

        databases_found = {}

        for block in response['results']:
            if block['type'] == 'child_database':
                db_id = block['id']
                title = block['child_database']['title']

                print(f"📊 Found database: {title}")
                print(f"   ID: {db_id}")

                # Categorize by title
                title_lower = title.lower()
                if 'account' in title_lower:
                    databases_found['accounts'] = db_id
                elif 'contact' in title_lower:
                    databases_found['contacts'] = db_id
                elif 'trigger' in title_lower or 'event' in title_lower:
                    databases_found['trigger_events'] = db_id
                elif 'partnership' in title_lower:
                    databases_found['partnerships'] = db_id

        print(f"\n📋 Categorized Databases:")
        for category, db_id in databases_found.items():
            print(f"   {category}: {db_id}")

        return databases_found

    except Exception as e:
        print(f"❌ Failed to find related databases: {e}")
        return {}

def enhance_accounts_database(database_id: str):
    """Add missing fields to Accounts database"""

    client = config.get_notion_client()

    print(f"🔧 ENHANCING ACCOUNTS DATABASE...")
    print("-" * 40)

    try:
        # Get current database
        database = client.databases.retrieve(database_id)
        current_props = database['properties']

        # Define required fields for enhanced Accounts schema
        required_fields = {
            "Company Name": {"title": {}},
            "Domain": {"rich_text": {}},
            "Employee Count": {"number": {"format": "number"}},
            "ICP Fit Score": {"number": {"format": "number"}},
            "Account Research Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Complete", "color": "green"}
                    ]
                }
            },
            "Business Model": {
                "select": {
                    "options": [
                        {"name": "Cloud Provider", "color": "blue"},
                        {"name": "Colocation", "color": "green"},
                        {"name": "Hyperscaler", "color": "purple"},
                        {"name": "AI-focused DC", "color": "orange"},
                        {"name": "Energy-intensive Facilities", "color": "red"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "Data Center Locations": {"rich_text": {}},
            "Primary Data Center Capacity": {"rich_text": {}},
            "Recent Funding Status": {"rich_text": {}},
            "Growth Indicators": {"rich_text": {}},
            "Last Updated": {"date": {}}
        }

        # Find missing fields
        missing_fields = {}
        for field_name, field_config in required_fields.items():
            if field_name not in current_props:
                missing_fields[field_name] = field_config
                print(f"   ➕ Will add: {field_name}")

        if not missing_fields:
            print("   ✅ Accounts database already has all required fields")
            return True

        # Add missing fields
        enhanced_props = {**current_props, **missing_fields}

        client.databases.update(
            database_id=database_id,
            properties=enhanced_props
        )

        print(f"   ✅ Added {len(missing_fields)} fields to Accounts database")
        return True

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def main():
    """Main function to work with existing databases"""

    print("🚀 WORKING WITH EXISTING NOTION DATABASES")
    print("=" * 60)

    # Use the correct database ID from your URL
    accounts_database_id = "2b27f5fee5e2801cad6ee1771d29dc48"

    # Step 1: Analyze the existing Accounts database
    accounts_analysis = analyze_existing_database(accounts_database_id)

    if not accounts_analysis:
        print("❌ Could not access the Accounts database")
        return

    # Step 2: Find related databases
    print(f"\n🔍 LOOKING FOR RELATED DATABASES...")

    # Try to find the parent page ID from the accounts database
    # The parent page should contain other databases too
    try:
        # Extract parent page ID by looking at the database's parent
        client = config.get_notion_client()
        db_info = client.databases.retrieve(accounts_database_id)

        if db_info.get('parent', {}).get('type') == 'page_id':
            parent_page_id = db_info['parent']['page_id']
            print(f"📄 Found parent page: {parent_page_id}")

            related_databases = find_related_databases(parent_page_id)

            if 'accounts' not in related_databases:
                related_databases['accounts'] = accounts_database_id

        else:
            print("⚠️ Could not determine parent page - using direct database ID")
            related_databases = {'accounts': accounts_database_id}

    except Exception as e:
        print(f"⚠️ Could not find related databases: {e}")
        related_databases = {'accounts': accounts_database_id}

    # Step 3: Enhance the Accounts database
    success = enhance_accounts_database(accounts_database_id)

    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"📊 Enhanced Accounts database: https://www.notion.so/{accounts_database_id.replace('-', '')}")
        print(f"🚀 Ready to populate with Genesis Cloud data!")

        # Save the database configuration
        config_content = f"""# Existing Database Configuration
# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATABASE_IDS = {{
    'accounts': '{accounts_database_id}',
"""

        for db_type, db_id in related_databases.items():
            if db_type != 'accounts':
                config_content += f"    '{db_type}': '{db_id}',\n"

        config_content += "}\n"

        with open('existing_database_config.py', 'w') as f:
            f.write(config_content)

        print(f"🔧 Database configuration saved to: existing_database_config.py")

if __name__ == "__main__":
    main()