#!/usr/bin/env python3
"""
Batch Research Script - Run research pipeline on all accounts.

This script:
1. Fetches all accounts from Notion
2. Runs the 5-phase research pipeline on each
3. Updates Notion with enriched data (employee count, infrastructure, etc.)

Uses the same API endpoint as the dashboard's "Deep Research" button.
"""
import os
import time
import sys

import requests

# Load env manually
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key] = val

API_BASE = "http://localhost:5001"


def get_accounts():
    """Fetch all accounts from API."""
    response = requests.get(f"{API_BASE}/api/accounts")
    if response.status_code != 200:
        print(f"❌ Failed to fetch accounts: {response.status_code}")
        sys.exit(1)
    return response.json().get("accounts", [])


def run_research(account_id: str, account_name: str, force: bool = False):
    """Run research pipeline for a single account."""
    print(f"\n🔬 Researching: {account_name}")
    print("-" * 50)

    try:
        response = requests.post(
            f"{API_BASE}/api/accounts/{account_id}/research",
            json={"force": force},
            timeout=300,  # 5 minute timeout per account
        )

        if response.status_code == 200:
            data = response.json()
            summary = data.get("research_summary", {})
            account_data = data.get("account_data", {})

            print(f"   ✅ Research completed")
            print(f"   📊 Contacts: {summary.get('contacts_discovered', 0)}")
            print(f"   📅 Events: {summary.get('trigger_events_found', 0)}")
            print(f"   🤝 Partnerships: {summary.get('partnerships_identified', 0)}")
            print(f"   👥 Employees: {account_data.get('employee_count', 'N/A')}")
            print(f"   🏢 Industry: {account_data.get('industry', 'N/A')}")
            print(f"   📈 ICP Score: {account_data.get('icp_fit_score', 'N/A')}")
            return True
        else:
            error = response.json().get("error", "Unknown error")
            print(f"   ❌ Failed: {error}")
            return False

    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - research took too long")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("BATCH RESEARCH - ALL ACCOUNTS")
    print("=" * 60)

    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_BASE}")
        print(f"   Make sure the Flask server is running: python -m src.abm_research.api.server")
        sys.exit(1)

    print("✅ API is running")

    # Fetch accounts
    print("\n1. Fetching accounts...")
    accounts = get_accounts()
    print(f"   Found {len(accounts)} accounts")

    # Show accounts to be researched
    print("\n2. Accounts to research:")
    print("-" * 60)
    for acc in accounts:
        emp = acc.get("employee_count", 0)
        status = "⚠️ Missing data" if emp == 0 else "✓ Has data"
        print(f"   {acc['name']:30} | {acc['domain']:25} | {status}")

    print("-" * 60)

    # Ask for confirmation
    force = "--force" in sys.argv
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv
    if force:
        print("\n⚠️ Force mode enabled - will re-research ALL accounts")
    else:
        print("\n📝 Normal mode - will only research accounts missing data")

    if not auto_yes:
        confirm = input("\nProceed with research? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return
    else:
        print("\n✓ Auto-confirmed via --yes flag")

    # Run research
    print("\n3. Running research pipeline...")
    success = 0
    failed = 0
    skipped = 0

    for acc in accounts:
        # Skip accounts that already have employee data (unless force mode)
        if not force and acc.get("employee_count", 0) > 0:
            print(f"\n⏭️ Skipping {acc['name']} - already has data")
            skipped += 1
            continue

        # Use the synthetic ID format (acc_XXXXXXXX) that the API expects
        account_id = acc.get("id", "")

        if run_research(account_id, acc["name"], force=force):
            success += 1
        else:
            failed += 1

        # Rate limiting - wait between accounts
        time.sleep(2)

    print("\n" + "=" * 60)
    print(f"COMPLETE: {success} succeeded, {failed} failed, {skipped} skipped")
    print("=" * 60)


if __name__ == "__main__":
    main()
