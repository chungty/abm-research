#!/usr/bin/env python3
"""
One-time cleanup script to remove duplicate contacts from Notion.

Identifies duplicates by:
1. Apollo Person ID (if present)
2. LinkedIn URL
3. Name (exact match)

Keeps the contact with the most data (highest lead score, most fields filled).
"""
import os
from collections import defaultdict

import requests

# Load env manually
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key] = val

NOTION_API_KEY = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_ABM_API_KEY")
CONTACTS_DB = os.environ.get("NOTION_CONTACTS_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_all_contacts():
    """Fetch all contacts from Notion with pagination."""
    all_contacts = []
    url = f"https://api.notion.com/v1/databases/{CONTACTS_DB}/query"
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        for page in data.get("results", []):
            props = page.get("properties", {})

            # Extract fields
            name_prop = props.get("Name", {})
            name = "".join([t.get("plain_text", "") for t in name_prop.get("title", [])])

            apollo_id_prop = props.get("Apollo Person ID", {})
            apollo_id = "".join(
                [t.get("plain_text", "") for t in apollo_id_prop.get("rich_text", [])]
            )

            linkedin_prop = props.get("LinkedIn URL", {})
            linkedin_url = linkedin_prop.get("url", "")

            lead_score = props.get("Lead Score", {}).get("number", 0) or 0

            email = props.get("Email", {}).get("email", "")

            title_prop = props.get("Title", {})
            title = "".join([t.get("plain_text", "") for t in title_prop.get("rich_text", [])])

            all_contacts.append(
                {
                    "id": page["id"],
                    "name": name,
                    "apollo_id": apollo_id,
                    "linkedin_url": linkedin_url,
                    "lead_score": lead_score,
                    "email": email,
                    "title": title,
                    "created_time": page.get("created_time", ""),
                }
            )

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return all_contacts


def find_duplicates(contacts):
    """Find duplicate contacts by various identifiers."""
    # Group by Apollo Person ID
    by_apollo_id = defaultdict(list)
    # Group by LinkedIn URL
    by_linkedin = defaultdict(list)
    # Group by name
    by_name = defaultdict(list)

    for contact in contacts:
        if contact["apollo_id"]:
            by_apollo_id[contact["apollo_id"]].append(contact)
        if contact["linkedin_url"]:
            by_linkedin[contact["linkedin_url"]].append(contact)
        if contact["name"]:
            by_name[contact["name"]].append(contact)

    duplicates_to_delete = []
    keep_ids = set()

    # Process Apollo ID duplicates first (most reliable)
    for apollo_id, dupes in by_apollo_id.items():
        if len(dupes) > 1:
            # Sort by lead score (highest first), then by created time (oldest first)
            sorted_dupes = sorted(
                dupes, key=lambda x: (-x["lead_score"], x["created_time"])
            )
            # Keep the first one (highest score)
            keep = sorted_dupes[0]
            keep_ids.add(keep["id"])
            for dupe in sorted_dupes[1:]:
                if dupe["id"] not in keep_ids:
                    duplicates_to_delete.append(
                        {
                            "id": dupe["id"],
                            "name": dupe["name"],
                            "reason": f"Duplicate Apollo ID: {apollo_id}",
                            "keep": keep["id"],
                        }
                    )

    # Process LinkedIn duplicates
    for linkedin_url, dupes in by_linkedin.items():
        if len(dupes) > 1:
            sorted_dupes = sorted(
                dupes, key=lambda x: (-x["lead_score"], x["created_time"])
            )
            keep = sorted_dupes[0]
            keep_ids.add(keep["id"])
            for dupe in sorted_dupes[1:]:
                if dupe["id"] not in keep_ids and dupe["id"] not in [
                    d["id"] for d in duplicates_to_delete
                ]:
                    duplicates_to_delete.append(
                        {
                            "id": dupe["id"],
                            "name": dupe["name"],
                            "reason": f"Duplicate LinkedIn: {linkedin_url[:50]}...",
                            "keep": keep["id"],
                        }
                    )

    # Process name duplicates (more conservative - only exact matches)
    for name, dupes in by_name.items():
        if len(dupes) > 1:
            sorted_dupes = sorted(
                dupes, key=lambda x: (-x["lead_score"], x["created_time"])
            )
            keep = sorted_dupes[0]
            keep_ids.add(keep["id"])
            for dupe in sorted_dupes[1:]:
                if dupe["id"] not in keep_ids and dupe["id"] not in [
                    d["id"] for d in duplicates_to_delete
                ]:
                    duplicates_to_delete.append(
                        {
                            "id": dupe["id"],
                            "name": dupe["name"],
                            "reason": f"Duplicate name: {name}",
                            "keep": keep["id"],
                        }
                    )

    return duplicates_to_delete


def archive_page(page_id):
    """Archive (soft delete) a Notion page."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.patch(url, headers=headers, json={"archived": True})
    return response.status_code == 200


def main():
    print("=" * 60)
    print("CONTACT DEDUPLICATION CLEANUP")
    print("=" * 60)

    print("\n1. Fetching all contacts from Notion...")
    contacts = get_all_contacts()
    print(f"   Found {len(contacts)} total contacts")

    print("\n2. Finding duplicates...")
    duplicates = find_duplicates(contacts)
    print(f"   Found {len(duplicates)} duplicates to remove")

    if not duplicates:
        print("\n✅ No duplicates found!")
        return

    print("\n3. Duplicates to be archived:")
    print("-" * 60)
    for dupe in duplicates:
        print(f"   ❌ {dupe['name'][:30]:30} - {dupe['reason'][:40]}")

    print("-" * 60)
    print(f"\nTotal: {len(duplicates)} contacts will be archived")

    # Ask for confirmation
    confirm = input("\nProceed with cleanup? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    print("\n4. Archiving duplicates...")
    success = 0
    failed = 0
    for dupe in duplicates:
        if archive_page(dupe["id"]):
            print(f"   ✓ Archived: {dupe['name']}")
            success += 1
        else:
            print(f"   ✗ Failed: {dupe['name']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"COMPLETE: {success} archived, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
