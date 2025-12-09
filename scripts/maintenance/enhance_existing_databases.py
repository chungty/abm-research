#!/usr/bin/env python3
"""
Enhance Existing Notion Databases
Add missing schema fields to the existing ABM databases using direct API access
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from abm_config import config
from config.settings import (
    NOTION_ACCOUNTS_DB_ID,
    NOTION_CONTACTS_DB_ID,
    NOTION_TRIGGER_EVENTS_DB_ID,
    NOTION_PARTNERSHIPS_DB_ID
)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_headers():
    """Get Notion API headers"""
    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        raise ValueError("NOTION_ABM_API_KEY not found")

    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

def analyze_database_schema(database_id: str, database_name: str):
    """Analyze current database schema"""

    headers = get_headers()

    print(f"\n🔍 ANALYZING {database_name.upper()} DATABASE SCHEMA")
    print("-" * 50)

    try:
        url = f"https://api.notion.com/v1/databases/{database_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', {})

            print(f"📊 Current Properties ({len(properties)}):")
            for prop_name, prop_config in properties.items():
                prop_type = prop_config.get('type', 'unknown')
                print(f"   • {prop_name} ({prop_type})")

            return properties
        else:
            print(f"❌ Failed to analyze database: {response.text}")
            return {}

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {}

def enhance_accounts_database(database_id: str):
    """Enhance Accounts database with missing fields"""

    headers = get_headers()
    current_props = analyze_database_schema(database_id, "Accounts")

    print(f"\n🔧 ENHANCING ACCOUNTS DATABASE")
    print("-" * 40)

    # Define complete enhanced schema based on SKILL.md and our research
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
        "Apollo Account ID": {"rich_text": {}},
        "Apollo Organization ID": {"rich_text": {}},
        "Last Updated": {"date": {}},
        "Created At": {"created_time": {}}
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

    # Update database with missing fields
    try:
        enhanced_props = {**current_props, **missing_fields}

        url = f"https://api.notion.com/v1/databases/{database_id}"
        payload = {"properties": enhanced_props}

        response = requests.patch(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            print(f"   ✅ Added {len(missing_fields)} fields to Accounts database")
            return True
        else:
            print(f"   ❌ Enhancement failed: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def enhance_contacts_database(database_id: str, accounts_db_id: str):
    """Enhance Contacts database with Verdigris Signals MEDDIC framework"""

    headers = get_headers()
    current_props = analyze_database_schema(database_id, "Contacts")

    print(f"\n👤 ENHANCING CONTACTS DATABASE")
    print("-" * 40)

    # Define complete enhanced schema with Verdigris Signals MEDDIC
    required_fields = {
        "Name": {"title": {}},
        "Account": {"relation": {"database_id": accounts_db_id}},
        "Title": {"rich_text": {}},
        "LinkedIn URL": {"url": {}},
        "Email": {"email": {}},
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
        "Final Lead Score": {
            "formula": {
                "expression": "round(prop(\"ICP Fit Score\") * 0.4 + prop(\"Buying Power Score\") * 0.3 + prop(\"Engagement Potential Score\") * 0.3)"
            }
        },
        "Research Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "Enriched", "color": "yellow"},
                    {"name": "Analyzed", "color": "green"}
                ]
            }
        },
        "Role Tenure": {"rich_text": {}},
        "LinkedIn Activity Level": {
            "select": {
                "options": [
                    {"name": "Weekly+", "color": "green"},
                    {"name": "Monthly", "color": "yellow"},
                    {"name": "Quarterly", "color": "orange"},
                    {"name": "Inactive", "color": "red"}
                ]
            }
        },
        "Network Quality": {
            "select": {
                "options": [
                    {"name": "High", "color": "green"},
                    {"name": "Standard", "color": "yellow"}
                ]
            }
        },
        "Problems They Likely Own": {
            "multi_select": {
                "options": [
                    {"name": "Power Capacity Planning", "color": "red"},
                    {"name": "Uptime Pressure", "color": "orange"},
                    {"name": "Cost Optimization", "color": "yellow"},
                    {"name": "Predictive Maintenance", "color": "green"},
                    {"name": "Energy Efficiency", "color": "blue"},
                    {"name": "Reliability Engineering", "color": "purple"},
                    {"name": "Compliance/Reporting", "color": "pink"},
                    {"name": "Capacity Planning", "color": "brown"}
                ]
            }
        },
        "Content Themes They Value": {
            "multi_select": {
                "options": [
                    {"name": "AI Infrastructure", "color": "purple"},
                    {"name": "Power Optimization", "color": "red"},
                    {"name": "Sustainability", "color": "green"},
                    {"name": "Reliability Engineering", "color": "blue"},
                    {"name": "Cost Reduction", "color": "yellow"},
                    {"name": "Predictive Analytics", "color": "orange"},
                    {"name": "Energy Management", "color": "pink"}
                ]
            }
        },
        "Connection Pathways": {"rich_text": {}},
        "Value-Add Ideas": {"rich_text": {}},
        "Apollo Contact ID": {"rich_text": {}},
        "Apollo Person ID": {"rich_text": {}},
        "Created At": {"created_time": {}}
    }

    # Find missing fields
    missing_fields = {}
    for field_name, field_config in required_fields.items():
        if field_name not in current_props:
            missing_fields[field_name] = field_config
            print(f"   ➕ Will add: {field_name}")

    if not missing_fields:
        print("   ✅ Contacts database already has all required fields")
        return True

    # Update database with missing fields
    try:
        enhanced_props = {**current_props, **missing_fields}

        url = f"https://api.notion.com/v1/databases/{database_id}"
        payload = {"properties": enhanced_props}

        response = requests.patch(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            print(f"   ✅ Added {len(missing_fields)} fields to Contacts database")
            return True
        else:
            print(f"   ❌ Enhancement failed: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def enhance_trigger_events_database(database_id: str, accounts_db_id: str):
    """Enhance Trigger Events database"""

    headers = get_headers()
    current_props = analyze_database_schema(database_id, "Trigger Events")

    print(f"\n⚡ ENHANCING TRIGGER EVENTS DATABASE")
    print("-" * 40)

    required_fields = {
        "Event Description": {"title": {}},
        "Account": {"relation": {"database_id": accounts_db_id}},
        "Event Type": {
            "select": {
                "options": [
                    {"name": "Expansion", "color": "green"},
                    {"name": "Leadership Change", "color": "blue"},
                    {"name": "AI Workload", "color": "purple"},
                    {"name": "Energy Pressure", "color": "red"},
                    {"name": "Incident", "color": "orange"},
                    {"name": "Sustainability", "color": "yellow"}
                ]
            }
        },
        "Confidence": {
            "select": {
                "options": [
                    {"name": "High", "color": "green"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "red"}
                ]
            }
        },
        "Confidence Score": {"number": {"format": "number"}},
        "Relevance Score": {"number": {"format": "number"}},
        "Detected Date": {"date": {}},
        "Source URL": {"url": {}},
        "Source Type": {
            "select": {
                "options": [
                    {"name": "News Article", "color": "blue"},
                    {"name": "Company Website", "color": "green"},
                    {"name": "LinkedIn", "color": "purple"},
                    {"name": "Press Release", "color": "orange"},
                    {"name": "Industry Report", "color": "yellow"}
                ]
            }
        },
        "Created At": {"created_time": {}}
    }

    # Find missing fields
    missing_fields = {}
    for field_name, field_config in required_fields.items():
        if field_name not in current_props:
            missing_fields[field_name] = field_config
            print(f"   ➕ Will add: {field_name}")

    if not missing_fields:
        print("   ✅ Trigger Events database already has all required fields")
        return True

    # Update database with missing fields
    try:
        enhanced_props = {**current_props, **missing_fields}

        url = f"https://api.notion.com/v1/databases/{database_id}"
        payload = {"properties": enhanced_props}

        response = requests.patch(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            print(f"   ✅ Added {len(missing_fields)} fields to Trigger Events database")
            return True
        else:
            print(f"   ❌ Enhancement failed: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def enhance_partnerships_database(database_id: str, accounts_db_id: str):
    """Enhance Strategic Partnerships database"""

    headers = get_headers()
    current_props = analyze_database_schema(database_id, "Strategic Partnerships")

    print(f"\n🤝 ENHANCING STRATEGIC PARTNERSHIPS DATABASE")
    print("-" * 40)

    required_fields = {
        "Partner Name": {"title": {}},
        "Account": {"relation": {"database_id": accounts_db_id}},
        "Category": {
            "select": {
                "options": [
                    {"name": "DCIM", "color": "blue"},
                    {"name": "EMS", "color": "green"},
                    {"name": "Cooling", "color": "purple"},
                    {"name": "DC Equipment", "color": "orange"},
                    {"name": "Racks", "color": "brown"},
                    {"name": "GPUs", "color": "red"},
                    {"name": "Critical Facilities Contractors", "color": "pink"},
                    {"name": "Professional Services", "color": "gray"}
                ]
            }
        },
        "Confidence": {
            "select": {
                "options": [
                    {"name": "High", "color": "green"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "red"}
                ]
            }
        },
        "Evidence URL": {"url": {}},
        "Relationship Evidence": {"rich_text": {}},
        "Detected Date": {"date": {}},
        "Verdigris Opportunity": {"rich_text": {}},
        "Partnership Action": {
            "select": {
                "options": [
                    {"name": "Investigate", "color": "red"},
                    {"name": "Contact", "color": "orange"},
                    {"name": "Monitor", "color": "yellow"},
                    {"name": "Not Relevant", "color": "gray"}
                ]
            }
        },
        "Priority Score": {"number": {"format": "number"}},
        "Created At": {"created_time": {}}
    }

    # Find missing fields
    missing_fields = {}
    for field_name, field_config in required_fields.items():
        if field_name not in current_props:
            missing_fields[field_name] = field_config
            print(f"   ➕ Will add: {field_name}")

    if not missing_fields:
        print("   ✅ Strategic Partnerships database already has all required fields")
        return True

    # Update database with missing fields
    try:
        enhanced_props = {**current_props, **missing_fields}

        url = f"https://api.notion.com/v1/databases/{database_id}"
        payload = {"properties": enhanced_props}

        response = requests.patch(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            print(f"   ✅ Added {len(missing_fields)} fields to Strategic Partnerships database")
            return True
        else:
            print(f"   ❌ Enhancement failed: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def main():
    """Main function to enhance all existing databases"""

    print("🚀 ENHANCING EXISTING ABM DATABASES")
    print("=" * 60)

    # Use environment variables for database IDs - no more hardcoded values!
    database_ids = {
        'accounts': NOTION_ACCOUNTS_DB_ID,
        'trigger_events': NOTION_TRIGGER_EVENTS_DB_ID,
        'contacts': NOTION_CONTACTS_DB_ID,
        'partnerships': NOTION_PARTNERSHIPS_DB_ID
    }

    # Validate that database IDs are configured
    missing_db_ids = [key for key, value in database_ids.items() if not value]
    if missing_db_ids:
        raise ValueError(f"Missing database ID environment variables: {missing_db_ids}. "
                        f"Please set NOTION_*_DB_ID environment variables in .env file.")

    success_count = 0

    # 1. Enhance Accounts Database first (others depend on it)
    if enhance_accounts_database(database_ids['accounts']):
        success_count += 1

    # 2. Enhance Contacts Database (depends on Accounts)
    if enhance_contacts_database(database_ids['contacts'], database_ids['accounts']):
        success_count += 1

    # 3. Enhance Trigger Events Database (depends on Accounts)
    if enhance_trigger_events_database(database_ids['trigger_events'], database_ids['accounts']):
        success_count += 1

    # 4. Enhance Strategic Partnerships Database (depends on Accounts)
    if enhance_partnerships_database(database_ids['partnerships'], database_ids['accounts']):
        success_count += 1

    # Save enhanced database configuration
    config_content = f"""# Enhanced ABM Database Configuration
# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Parent Page: https://www.notion.so/2b27f5fee5e2801cad6ee1771d29dc48

DATABASE_IDS = {{
    'parent_page': '2b27f5fee5e2801cad6ee1771d29dc48',
    'accounts': '{database_ids["accounts"]}',
    'trigger_events': '{database_ids["trigger_events"]}',
    'contacts': '{database_ids["contacts"]}',
    'partnerships': '{database_ids["partnerships"]}'
}}

# Direct Notion URLs
DATABASE_URLS = {{
    'accounts': 'https://www.notion.so/{database_ids["accounts"].replace("-", "")}',
    'trigger_events': 'https://www.notion.so/{database_ids["trigger_events"].replace("-", "")}',
    'contacts': 'https://www.notion.so/{database_ids["contacts"].replace("-", "")}',
    'partnerships': 'https://www.notion.so/{database_ids["partnerships"].replace("-", "")}'
}}
"""

    with open('enhanced_existing_database_config.py', 'w') as f:
        f.write(config_content)

    print(f"\n🎉 ENHANCEMENT COMPLETE!")
    print("=" * 50)
    print(f"✅ Enhanced {success_count}/4 databases successfully")
    print(f"📊 Accounts: https://www.notion.so/{database_ids['accounts'].replace('-', '')}")
    print(f"👤 Contacts: https://www.notion.so/{database_ids['contacts'].replace('-', '')}")
    print(f"⚡ Trigger Events: https://www.notion.so/{database_ids['trigger_events'].replace('-', '')}")
    print(f"🤝 Partnerships: https://www.notion.so/{database_ids['partnerships'].replace('-', '')}")

    print(f"\n✨ ENHANCED FEATURES:")
    print(f"   📊 Accounts: Complete firmographics + ICP scoring + business model classification")
    print(f"   👤 Contacts: Verdigris Signals MEDDIC framework + transparent lead scoring")
    print(f"   ⚡ Trigger Events: Confidence scoring + relevance analysis + source tracking")
    print(f"   🤝 Partnerships: Strategic opportunity analysis + priority scoring")

    print(f"\n🔧 Database configuration saved to: enhanced_existing_database_config.py")
    print(f"🚀 Ready to populate with Genesis Cloud intelligence!")

if __name__ == "__main__":
    main()
