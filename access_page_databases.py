#!/usr/bin/env python3
"""
Access Databases Within Parent Page
Work with the four databases inside the parent page
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime
from abm_config import config

def access_parent_page_databases():
    """Access databases within the parent page"""

    client = config.get_notion_client()
    parent_page_id = "2b27f5fee5e2801cad6ee1771d29dc48"

    print(f"🔍 ACCESSING DATABASES IN PARENT PAGE")
    print(f"Parent Page ID: {parent_page_id}")
    print("=" * 60)

    try:
        # First, verify we can access the parent page
        page_info = client.pages.retrieve(parent_page_id)
        print(f"✅ Successfully accessed parent page")

        # Get the child blocks (databases) within the parent page
        response = client.blocks.children.list(parent_page_id)

        databases_found = {}
        print(f"\n📊 FOUND DATABASES:")

        for block in response['results']:
            if block['type'] == 'child_database':
                db_id = block['id']
                title = block['child_database']['title']

                print(f"   📋 {title}")
                print(f"       ID: {db_id}")
                print(f"       URL: https://www.notion.so/{db_id.replace('-', '')}")

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

        print(f"\n📋 CATEGORIZED DATABASES:")
        for category, db_id in databases_found.items():
            print(f"   {category}: {db_id}")

        # Now try to access each database and analyze its schema
        print(f"\n🔍 ANALYZING DATABASE SCHEMAS:")

        for category, db_id in databases_found.items():
            try:
                db_info = client.databases.retrieve(db_id)
                props = db_info['properties']

                print(f"\n   📊 {category.upper()} DATABASE:")
                print(f"      Fields: {len(props)}")
                for prop_name, prop_config in list(props.items())[:5]:  # Show first 5
                    print(f"      • {prop_name} ({prop_config['type']})")
                if len(props) > 5:
                    print(f"      ... and {len(props) - 5} more fields")

            except Exception as e:
                print(f"   ❌ Could not access {category} database: {e}")

        # Save the database configuration
        if databases_found:
            config_content = f"""# Your Existing Database Configuration
# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Parent Page: https://www.notion.so/{parent_page_id.replace('-', '')}

DATABASE_IDS = {{
"""
            for category, db_id in databases_found.items():
                config_content += f"    '{category}': '{db_id}',\n"

            config_content += """}}

# Direct Notion URLs
DATABASE_URLS = {
"""
            for category, db_id in databases_found.items():
                config_content += f"    '{category}': 'https://www.notion.so/{db_id.replace('-', '')}',\n"

            config_content += "}\n"

            with open('your_existing_database_config.py', 'w') as f:
                f.write(config_content)

            print(f"\n✅ SUCCESS!")
            print(f"📁 Found {len(databases_found)} databases in your page")
            print(f"🔧 Configuration saved to: your_existing_database_config.py")

        return databases_found

    except Exception as e:
        print(f"❌ Failed to access parent page: {e}")
        return {}

def enhance_existing_database(database_id: str, database_type: str):
    """Add missing fields to an existing database"""

    client = config.get_notion_client()

    print(f"\n🔧 ENHANCING {database_type.upper()} DATABASE...")
    print("-" * 40)

    try:
        # Get current database
        database = client.databases.retrieve(database_id)
        current_props = database['properties']

        # Define missing fields based on database type
        missing_fields = {}

        if database_type == 'accounts':
            required_fields = {
                "ICP Fit Score": {"number": {"format": "number"}},
                "Business Model": {
                    "select": {
                        "options": [
                            {"name": "Cloud Provider", "color": "blue"},
                            {"name": "Colocation", "color": "green"},
                            {"name": "Hyperscaler", "color": "purple"},
                            {"name": "AI-focused DC", "color": "orange"}
                        ]
                    }
                },
                "Data Center Locations": {"rich_text": {}},
                "Recent Funding Status": {"rich_text": {}},
                "Growth Indicators": {"rich_text": {}}
            }

        elif database_type == 'contacts':
            required_fields = {
                "Buying Committee Role": {
                    "select": {
                        "options": [
                            {"name": "Economic Buyer", "color": "green"},
                            {"name": "Technical Evaluator", "color": "blue"},
                            {"name": "Champion", "color": "purple"},
                            {"name": "Influencer", "color": "yellow"},
                            {"name": "User", "color": "gray"},
                            {"name": "Blocker", "color": "red"}
                        ]
                    }
                },
                "ICP Fit Score": {"number": {"format": "number"}},
                "Buying Power Score": {"number": {"format": "number"}},
                "Engagement Potential Score": {"number": {"format": "number"}},
                "Problems They Likely Own": {
                    "multi_select": {
                        "options": [
                            {"name": "Power Capacity Planning", "color": "red"},
                            {"name": "Uptime Pressure", "color": "orange"},
                            {"name": "Cost Optimization", "color": "yellow"},
                            {"name": "Energy Efficiency", "color": "blue"}
                        ]
                    }
                },
                "Content Themes They Value": {
                    "multi_select": {
                        "options": [
                            {"name": "AI Infrastructure", "color": "purple"},
                            {"name": "Power Optimization", "color": "red"},
                            {"name": "Sustainability", "color": "green"}
                        ]
                    }
                },
                "Apollo Contact ID": {"rich_text": {}}
            }

        else:
            print(f"   ⚠️ Skipping {database_type} - enhancement not defined yet")
            return True

        # Find missing fields
        for field_name, field_config in required_fields.items():
            if field_name not in current_props:
                missing_fields[field_name] = field_config

        if not missing_fields:
            print(f"   ✅ {database_type} database already has all key fields")
            return True

        print(f"   ➕ Adding {len(missing_fields)} fields:")
        for field_name in missing_fields.keys():
            print(f"      • {field_name}")

        # Add missing fields
        enhanced_props = {**current_props, **missing_fields}

        client.databases.update(
            database_id=database_id,
            properties=enhanced_props
        )

        print(f"   ✅ Successfully enhanced {database_type} database")
        return True

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def main():
    """Main function"""

    print("🚀 ACCESSING YOUR EXISTING ABM DATABASES")
    print("=" * 60)

    # Access databases within the parent page
    databases = access_parent_page_databases()

    if not databases:
        print("❌ Could not find databases in the parent page")
        return

    # Enhance the most important databases
    success_count = 0

    if 'accounts' in databases:
        if enhance_existing_database(databases['accounts'], 'accounts'):
            success_count += 1

    if 'contacts' in databases:
        if enhance_existing_database(databases['contacts'], 'contacts'):
            success_count += 1

    print(f"\n🎉 ENHANCEMENT COMPLETE!")
    print(f"   ✅ Enhanced {success_count} databases")
    print(f"   🚀 Ready for production ABM system!")

if __name__ == "__main__":
    main()