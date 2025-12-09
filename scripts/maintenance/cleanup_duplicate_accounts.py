#!/usr/bin/env python3
"""
Cleanup Duplicate Genesis Cloud Entries
Removes the malformed duplicate account entry from Notion
"""


import requests
from abm_config import config
from config.settings import NOTION_ACCOUNTS_DB_ID


def cleanup_duplicate_genesis_cloud():
    """Remove the duplicate Genesis Cloud entry with messy formatting"""

    headers = config.get_notion_headers()
    accounts_db_id = NOTION_ACCOUNTS_DB_ID

    # Validate database ID is configured
    if not accounts_db_id:
        raise ValueError(
            "Missing NOTION_ACCOUNTS_DB_ID environment variable. " "Please set in .env file."
        )

    print("🔍 Searching for Genesis Cloud accounts...")

    # Query all accounts
    url = f"https://api.notion.com/v1/databases/{accounts_db_id}/query"
    payload = {"page_size": 100}
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        print(f"❌ Failed to query accounts: {response.text}")
        return False

    data = response.json()
    genesis_accounts = []

    for result in data.get("results", []):
        props = result.get("properties", {})
        name = ""

        # Extract name
        title_prop = props.get("Name", {})
        if title_prop.get("type") == "title" and title_prop.get("title"):
            name = "".join([item.get("plain_text", "") for item in title_prop["title"]])

        if "genesis" in name.lower() and "cloud" in name.lower():
            genesis_accounts.append(
                {
                    "id": result["id"],
                    "name": name,
                    "created_time": result.get("created_time", ""),
                    "props": props,
                }
            )

    print(f"📋 Found {len(genesis_accounts)} Genesis Cloud accounts:")
    for i, acc in enumerate(genesis_accounts):
        print(f"  {i+1}. {acc['name']} (ID: {acc['id']})")

    if len(genesis_accounts) <= 1:
        print("✅ No duplicates found")
        return True

    # Identify the duplicate to remove (the one with the messy name)
    duplicate_to_remove = None
    clean_account = None

    for acc in genesis_accounts:
        if acc["name"] == "Genesis Cloud":
            clean_account = acc
        elif "genesiscloud.com" in acc["name"] and "ICP:" in acc["name"]:
            duplicate_to_remove = acc

    if not duplicate_to_remove:
        print("❓ Could not identify which account to remove")
        return False

    if not clean_account:
        print("❌ Could not find clean Genesis Cloud account")
        return False

    print(f"\n🎯 Removing duplicate: {duplicate_to_remove['name']}")
    print(f"✅ Keeping clean account: {clean_account['name']}")

    # Archive the duplicate entry (Notion doesn't support deletion, only archiving)
    archive_url = f"https://api.notion.com/v1/pages/{duplicate_to_remove['id']}"
    archive_payload = {"archived": True}
    delete_response = requests.patch(archive_url, headers=headers, json=archive_payload, timeout=30)

    if delete_response.status_code == 200:
        print("✅ Successfully removed duplicate Genesis Cloud account")
        return True
    else:
        print(f"❌ Failed to delete duplicate: {delete_response.text}")
        return False


if __name__ == "__main__":
    print("🧹 GENESIS CLOUD DUPLICATE CLEANUP")
    print("=" * 40)

    success = cleanup_duplicate_genesis_cloud()

    if success:
        print("\n🎉 Cleanup completed successfully!")
        print("💡 The dashboard should now show only one Genesis Cloud account")
    else:
        print("\n❌ Cleanup failed - manual intervention may be required")
