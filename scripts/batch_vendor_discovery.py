#!/usr/bin/env python3
"""
Batch Vendor Discovery Script

Runs vendor discovery across all accounts in the system, saving discovered
vendors to Notion's Partnerships database.

Usage:
    python scripts/batch_vendor_discovery.py [--dry-run] [--min-confidence 0.6]

Rate Limiting:
    - 5 second delay between accounts (to respect Brave API limits)
    - Each account discovery takes ~30-60 seconds
    - Full run across 11 accounts: ~10-15 minutes
"""

import requests
import time
import json
import argparse
from datetime import datetime


API_BASE = "http://localhost:5001/api"


def get_all_accounts():
    """Fetch all accounts from the API."""
    response = requests.get(f"{API_BASE}/accounts")
    response.raise_for_status()
    data = response.json()
    return data.get("accounts", [])


def discover_vendors_for_account(
    account_id: str, account_name: str, save_to_notion: bool = True, min_confidence: float = 0.6
) -> dict:
    """Run vendor discovery for a single account."""
    response = requests.post(
        f"{API_BASE}/accounts/{account_id}/discover-unknown-vendors",
        headers={"Content-Type": "application/json"},
        json={"save_to_notion": save_to_notion, "min_confidence": min_confidence},
        timeout=120,  # 2 minute timeout per account
    )
    response.raise_for_status()
    return response.json()


def format_result_summary(result: dict) -> str:
    """Format discovery result for console output."""
    lines = []
    lines.append(f"  Status: {result.get('status', 'unknown')}")
    lines.append(f"  Vendors Discovered: {result.get('new_vendors_count', 0)}")
    lines.append(f"  Saved to Notion: {result.get('saved_to_notion', 0)}")
    lines.append(f"  Known Vendors Found: {result.get('known_vendors_found', 0)}")
    lines.append(f"  Search Results Analyzed: {result.get('search_results_analyzed', 0)}")
    lines.append(f"  Cost Estimate: {result.get('cost_estimate', 'N/A')}")

    # Category breakdown
    categories = result.get("category_summary", {})
    if categories:
        lines.append("  Categories:")
        for cat, count in categories.items():
            if count > 0:
                lines.append(f"    - {cat}: {count}")

    # Top vendors discovered
    vendors = result.get("discovered_vendors", [])[:3]
    if vendors:
        lines.append("  Top Vendors:")
        for v in vendors:
            lines.append(f"    - {v['vendor_name']} ({v['category']}) conf:{v['confidence']:.0%}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Batch vendor discovery across all accounts")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't save to Notion, just preview what would be discovered",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.6,
        help="Minimum confidence threshold (default: 0.6)",
    )
    parser.add_argument(
        "--delay", type=int, default=5, help="Seconds to wait between accounts (default: 5)"
    )
    parser.add_argument("--skip-accounts", nargs="+", default=[], help="Account names to skip")
    args = parser.parse_args()

    save_to_notion = not args.dry_run

    print("=" * 60)
    print("BATCH VENDOR DISCOVERY")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY RUN (not saving)' if args.dry_run else 'LIVE (saving to Notion)'}")
    print(f"Min Confidence: {args.min_confidence:.0%}")
    print(f"Delay Between Accounts: {args.delay}s")
    print("=" * 60)
    print()

    # Get all accounts
    print("Fetching accounts...")
    try:
        accounts = get_all_accounts()
    except Exception as e:
        print(f"ERROR: Failed to fetch accounts: {e}")
        print(
            "Make sure the API server is running: PYTHONPATH=. python3 src/abm_research/api/server.py"
        )
        return 1

    print(f"Found {len(accounts)} accounts")
    print()

    # Filter out skipped accounts
    if args.skip_accounts:
        original_count = len(accounts)
        accounts = [a for a in accounts if a["name"] not in args.skip_accounts]
        print(f"Skipping {original_count - len(accounts)} accounts: {args.skip_accounts}")
        print()

    # Track results
    results = {
        "success": 0,
        "failed": 0,
        "total_vendors": 0,
        "total_saved": 0,
        "total_cost": 0.0,
        "accounts": [],
    }

    for i, account in enumerate(accounts, 1):
        account_name = account.get("name", "Unknown")
        account_id = account.get("id")

        print(f"[{i}/{len(accounts)}] Processing: {account_name}")
        print(f"    ID: {account_id}")

        try:
            result = discover_vendors_for_account(
                account_id=account_id,
                account_name=account_name,
                save_to_notion=save_to_notion,
                min_confidence=args.min_confidence,
            )

            print(format_result_summary(result))

            # Update totals
            results["success"] += 1
            results["total_vendors"] += result.get("new_vendors_count", 0)
            results["total_saved"] += result.get("saved_to_notion", 0)

            # Parse cost estimate (e.g., "~$0.174")
            cost_str = result.get("cost_estimate", "$0")
            try:
                cost = float(cost_str.replace("~$", "").replace("$", ""))
                results["total_cost"] += cost
            except:
                pass

            results["accounts"].append(
                {
                    "name": account_name,
                    "status": "success",
                    "vendors_discovered": result.get("new_vendors_count", 0),
                    "saved_to_notion": result.get("saved_to_notion", 0),
                }
            )

        except requests.exceptions.Timeout:
            print(f"  ERROR: Request timed out (>120s)")
            results["failed"] += 1
            results["accounts"].append(
                {
                    "name": account_name,
                    "status": "timeout",
                    "vendors_discovered": 0,
                    "saved_to_notion": 0,
                }
            )

        except Exception as e:
            print(f"  ERROR: {e}")
            results["failed"] += 1
            results["accounts"].append(
                {
                    "name": account_name,
                    "status": "error",
                    "error": str(e),
                    "vendors_discovered": 0,
                    "saved_to_notion": 0,
                }
            )

        print()

        # Delay between accounts (except for last one)
        if i < len(accounts):
            print(f"    Waiting {args.delay}s before next account...")
            time.sleep(args.delay)

    # Print summary
    print("=" * 60)
    print("BATCH DISCOVERY COMPLETE")
    print("=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Accounts Processed: {results['success'] + results['failed']}")
    print(f"  - Successful: {results['success']}")
    print(f"  - Failed: {results['failed']}")
    print()
    print(f"Total Vendors Discovered: {results['total_vendors']}")
    print(f"Total Saved to Notion: {results['total_saved']}")
    print(f"Estimated Total Cost: ~${results['total_cost']:.3f}")
    print("=" * 60)

    # Save results to file
    output_file = f"/tmp/batch_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
