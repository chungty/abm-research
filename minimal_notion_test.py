"""
Minimal Notion Database Test
Test the absolute basics of database creation
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def minimal_test():
    """Test minimal database creation"""
    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return

    client = Client(auth=api_key)
    parent_page_id = "2b27f5fee5e2801cad6ee1771d29dc48"

    print("🧪 Testing minimal database creation...")

    # Test 1: Create database with just a title property
    print("📝 Test 1: Database with only title property...")

    try:
        response = client.databases.create(
            parent={
                "type": "page_id",
                "page_id": parent_page_id
            },
            title=[{
                "type": "text",
                "text": {"content": "Minimal Test Database"}
            }],
            properties={
                "Name": {"title": {}}
            }
        )

        db_id = response['id']
        print(f"✅ Database created: {db_id}")

        # Immediately check what was actually created
        check = client.databases.retrieve(database_id=db_id)
        props = check.get('properties', {})
        print(f"📋 Properties found: {len(props)}")

        for prop_name, prop_info in props.items():
            print(f"   • {prop_name} ({prop_info.get('type', 'unknown')})")

        # Test creating a simple page in this database
        print("📄 Test 2: Creating a page...")
        page = client.pages.create(
            parent={"type": "database_id", "database_id": db_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": "Test Entry"}}]
                }
            }
        )
        print(f"✅ Page created: {page['id']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()