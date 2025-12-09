#!/usr/bin/env python3
"""
Test the unified configuration manager
"""
import sys

sys.path.append("src")


def test_config_manager():
    """Test the new unified configuration manager"""
    print("🔧 Testing Unified Configuration Manager")
    print("=" * 50)

    try:
        from abm_research.config.manager import config_manager

        print("✅ Configuration manager imported successfully")
        print(f"📊 Manager representation: {config_manager}")

        # Test API key access
        print(f"\n🔑 API Keys Available:")
        try:
            apollo_key = config_manager.get_apollo_api_key()
            print(
                f"   Apollo: {'✓' if apollo_key else '✗'} ({'***' + apollo_key[-4:] if apollo_key else 'missing'})"
            )
        except Exception as e:
            print(f"   Apollo: ✗ ({e})")

        try:
            notion_key = config_manager.get_notion_api_key()
            print(
                f"   Notion: {'✓' if notion_key else '✗'} ({'***' + notion_key[-4:] if notion_key else 'missing'})"
            )
        except Exception as e:
            print(f"   Notion: ✗ ({e})")

        try:
            openai_key = config_manager.get_openai_api_key()
            print(
                f"   OpenAI: {'✓' if openai_key else '✗'} ({'***' + openai_key[-4:] if openai_key else 'missing'})"
            )
        except Exception as e:
            print(f"   OpenAI: ✗ ({e})")

        # Test database IDs
        print(f"\n💾 Database IDs:")
        try:
            db_ids = config_manager.get_all_database_ids()
            for db_type, db_id in db_ids.items():
                print(
                    f"   {db_type}: {db_id[:8]}...{db_id[-8:]} (32 chars: {'✓' if len(db_id) == 32 else '✗'})"
                )
        except Exception as e:
            print(f"   Database IDs: ✗ ({e})")

        # Test specific database ID access
        try:
            accounts_id = config_manager.get_database_id("accounts")
            print(f"   Accounts ID lookup: ✓ ({accounts_id[:8]}...)")
        except Exception as e:
            print(f"   Accounts ID lookup: ✗ ({e})")

        # Test header generation (consolidates duplicate code)
        print(f"\n📄 Header Generation:")
        try:
            notion_headers = config_manager.get_notion_headers()
            print(f"   Notion headers: ✓ ({len(notion_headers)} keys)")
            print(f"      Keys: {list(notion_headers.keys())}")
        except Exception as e:
            print(f"   Notion headers: ✗ ({e})")

        try:
            apollo_headers = config_manager.get_apollo_headers()
            print(f"   Apollo headers: ✓ ({len(apollo_headers)} keys)")
        except Exception as e:
            print(f"   Apollo headers: ✗ ({e})")

        # Test external config loading
        print(f"\n📚 External Configurations:")
        try:
            lead_config = config_manager.get_lead_scoring_config()
            print(
                f"   Lead scoring config: ✓ ({len(lead_config)} items)"
                if lead_config
                else "   Lead scoring config: empty but loaded"
            )
        except Exception as e:
            print(f"   Lead scoring config: ✗ ({e})")

        try:
            partnership_categories = config_manager.get_partnership_categories()
            print(f"   Partnership categories: ✓ ({len(partnership_categories)} categories)")
            for category in partnership_categories.keys():
                print(f"      - {category}")
        except Exception as e:
            print(f"   Partnership categories: ✗ ({e})")

        # Test utility methods
        print(f"\n🛠️ Utility Methods:")
        try:
            is_dev = config_manager.is_development_mode()
            print(f"   Development mode: {is_dev}")
        except Exception as e:
            print(f"   Development mode: ✗ ({e})")

        try:
            log_level = config_manager.get_log_level()
            print(f"   Log level: {log_level}")
        except Exception as e:
            print(f"   Log level: ✗ ({e})")

        print("\n✅ All configuration manager tests completed!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration manager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config_manager()
    exit(0 if success else 1)
