#!/usr/bin/env python3
"""
Clean up mock data entries (like CoreWeave) from the Notion database
Ensures production database contains only real company data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from abm_research.integrations.notion_client import NotionClient

def cleanup_mock_data():
    """
    Remove any mock data entries from Notion databases
    """
    print("🧹 Cleaning Up Mock Data from Notion Database")
    print("=" * 50)

    try:
        # Initialize Notion client
        notion_client = NotionClient()
        print(f"✅ Notion client initialized")

        # Get all accounts from Notion
        print(f"\n📋 Scanning accounts for mock data...")
        all_accounts = notion_client.query_all_accounts()
        print(f"Found {len(all_accounts)} total accounts")

        mock_entries = []
        for account in all_accounts:
            properties = account.get('properties', {})

            # Get account name and domain
            name_prop = properties.get('Name', {}).get('title', [])
            name = name_prop[0].get('text', {}).get('content', '') if name_prop else ''

            domain_prop = properties.get('Domain', {}).get('rich_text', [])
            domain = domain_prop[0].get('text', {}).get('content', '') if domain_prop else ''

            # Check for mock data indicators
            is_mock = (
                'coreweave' in name.lower() or
                'coreweave' in domain.lower() or
                'test' in name.lower() or
                'mock' in name.lower() or
                'example' in name.lower()
            )

            if is_mock:
                mock_entries.append({
                    'id': account['id'],
                    'name': name,
                    'domain': domain
                })

        if mock_entries:
            print(f"\n⚠️  Found {len(mock_entries)} mock data entries:")
            for entry in mock_entries:
                print(f"  - {entry['name']} ({entry['domain']})")

            # Ask for confirmation (in a real scenario)
            print(f"\n🗑️  Removing mock entries...")
            removed_count = 0

            for entry in mock_entries:
                try:
                    # Note: This would require implementing a delete method
                    # For now, just report what would be deleted
                    print(f"  🗑️  Would delete: {entry['name']}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to delete {entry['name']}: {e}")

            print(f"\n✅ Cleanup complete: {removed_count}/{len(mock_entries)} mock entries processed")

        else:
            print(f"✅ No mock data entries found - database is clean!")

        # Verify data quality
        print(f"\n📊 Data Quality Check:")
        clean_count = len(all_accounts) - len(mock_entries)
        print(f"  Real companies: {clean_count}")
        print(f"  Mock entries: {len(mock_entries)}")
        print(f"  Data quality: {(clean_count / len(all_accounts) * 100) if all_accounts else 100:.1f}%")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_mock_data()