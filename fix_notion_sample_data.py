"""
Fix Notion Sample Data Population
Debug and populate the created databases with working sample data
"""
import os
from notion_client import Client
from config.settings import (
    NOTION_ACCOUNTS_DB_ID,
    NOTION_CONTACTS_DB_ID,
    NOTION_TRIGGER_EVENTS_DB_ID,
    NOTION_PARTNERSHIPS_DB_ID
)

def fix_sample_data():
    """Fix and populate sample data in the created databases"""

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

    api_key = os.getenv('NOTION_ABM_API_KEY')
    client = Client(auth=api_key)

    print("🔧 Fixing sample data population...")

    try:
        # First, let's check what properties actually exist in the Accounts database
        print("🔍 Checking Accounts database properties...")
        accounts_db = client.databases.retrieve(database_ids['accounts'])

        print("Available properties:")
        for prop_name, prop_config in accounts_db['properties'].items():
            print(f"   • {prop_name}: {prop_config['type']}")

        # Create sample account with correct property names
        print("\n📊 Creating sample account...")
        account_page = client.pages.create(
            parent={"type": "database_id", "database_id": database_ids['accounts']},
            properties={
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
        )
        account_id = account_page['id']
        print(f"✅ Sample account created: Genesis Cloud Infrastructure")

        # Create sample trigger event
        print("⚡ Creating sample trigger event...")
        client.pages.create(
            parent={"type": "database_id", "database_id": database_ids['trigger_events']},
            properties={
                "Event Description": {
                    "title": [{"text": {"content": "Announced $75M investment in GPU infrastructure for AI workloads"}}]
                },
                "Account": {"relation": [{"id": account_id}]},
                "Event Type": {"select": {"name": "AI Workload"}},
                "Confidence": {"select": {"name": "High"}},
                "Confidence Score": {"number": 95.0},
                "Relevance Score": {"number": 92.0},
                "Source URL": {"url": "https://genesis-cloud.com/newsroom/ai-investment"}
            }
        )
        print(f"✅ Sample trigger event created")

        # Create sample contact
        print("👤 Creating sample contact...")
        client.pages.create(
            parent={"type": "database_id", "database_id": database_ids['contacts']},
            properties={
                "Name": {
                    "title": [{"text": {"content": "Jennifer Martinez"}}]
                },
                "Account": {"relation": [{"id": account_id}]},
                "Title": {
                    "rich_text": [{"text": {"content": "VP of Data Center Operations"}}]
                },
                "LinkedIn URL": {"url": "https://linkedin.com/in/jennifer-martinez-dc-ops"},
                "Email": {"email": "j.martinez@genesis-cloud.com"},
                "Buying Committee Role": {"select": {"name": "Economic Buyer"}},
                "ICP Fit Score": {"number": 95.0},
                "Buying Power Score": {"number": 100.0},
                "Engagement Potential Score": {"number": 85.0},
                "Research Status": {"select": {"name": "Analyzed"}},
                "LinkedIn Activity Level": {"select": {"name": "Monthly"}},
                "Network Quality": {"select": {"name": "High"}},
                "Value-Add Ideas": {
                    "rich_text": [{"text": {"content": "• Share GPU rack optimization case study\n• Provide PUE benchmarking data\n• Reference recent AI expansion and offer capacity planning insights"}}]
                }
            }
        )
        print(f"✅ Sample contact created: Jennifer Martinez (Final Score: 89)")

        # Create sample partnership
        print("🤝 Creating sample partnership...")
        client.pages.create(
            parent={"type": "database_id", "database_id": database_ids['partnerships']},
            properties={
                "Partner Name": {
                    "title": [{"text": {"content": "NVIDIA DGX"}}]
                },
                "Account": {"relation": [{"id": account_id}]},
                "Category": {"select": {"name": "GPUs"}},
                "Confidence": {"select": {"name": "High"}},
                "Evidence URL": {"url": "https://genesis-cloud.com/case-studies/nvidia-dgx"},
                "Verdigris Opportunity": {
                    "rich_text": [{"text": {"content": "High-density monitoring for AI workloads - perfect integration opportunity for GPU thermal and power management"}}]
                },
                "Partnership Action": {"select": {"name": "Investigate"}},
                "Priority Score": {"number": 95.0}
            }
        )
        print(f"✅ Sample partnership created: NVIDIA DGX")

        print(f"\n🎉 Sample data successfully populated!")
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    fix_sample_data()