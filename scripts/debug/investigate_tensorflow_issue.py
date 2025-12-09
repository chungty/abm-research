#!/usr/bin/env python3
"""
TensorFlow Data Placement Investigation

Analyzes the specific TensorFlow page that appears as a partnership instead of an account
to understand the database structure issue.
"""

import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

from abm_research.integrations.notion_client import NotionClient
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")


def investigate_tensorflow_page():
    """Investigate the specific TensorFlow page the user identified"""

    print("🔍 TENSORFLOW DATA PLACEMENT INVESTIGATION")
    print("=" * 60)
    print("User reported: TensorFlow appears as 'TensorFlow-Optimization-Partnership'")
    print("Expected: TensorFlow should be properly structured as an account")
    print(
        "URL: https://www.notion.so/verdigris/TensorFlow-Optimization-Partnership-2b27f5fee5e2816c8298e823f1d23f70"
    )
    print()

    # Extract page ID from URL
    page_id = "2b27f5fee5e2816c8298e823f1d23f70"
    print(f"🎯 Investigating Page ID: {page_id}")
    print()

    notion_client = NotionClient()

    # 1. Try to retrieve this specific page
    print("📋 STEP 1: Direct Page Retrieval")
    print("-" * 40)
    try:
        # Format the page ID properly (add hyphens)
        formatted_page_id = (
            f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
        )
        print(f"🔍 Formatted Page ID: {formatted_page_id}")

        response = notion_client._make_request(
            "GET", f"https://api.notion.com/v1/pages/{formatted_page_id}"
        )

        if response.status_code == 200:
            page_data = response.json()
            print(f"✅ Found page: {page_data.get('properties', {}).get('title', {})}")

            # Check which database this belongs to
            parent = page_data.get("parent", {})
            if parent.get("type") == "database_id":
                database_id = parent.get("database_id")
                print(f"📊 Parent Database ID: {database_id}")

                # Check which of our databases this matches
                for db_name, db_id in notion_client.database_ids.items():
                    if db_id == database_id:
                        print(f"🎯 FOUND: This page belongs to '{db_name}' database")
                        break
                else:
                    print("⚠️  This page belongs to an unknown database")

            # Show all properties
            print("\n📋 Page Properties:")
            properties = page_data.get("properties", {})
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get("type", "unknown")
                print(f"   • {prop_name} ({prop_type})")

                # Try to extract the value based on type
                if prop_type == "title" and prop_data.get("title"):
                    title_parts = [t.get("text", {}).get("content", "") for t in prop_data["title"]]
                    value = "".join(title_parts)
                    print(f"     Value: '{value}'")
                elif prop_type == "rich_text" and prop_data.get("rich_text"):
                    text_parts = [
                        t.get("text", {}).get("content", "") for t in prop_data["rich_text"]
                    ]
                    value = "".join(text_parts)
                    if value:
                        print(f"     Value: '{value}'")
                elif prop_type == "select" and prop_data.get("select"):
                    value = prop_data["select"].get("name", "")
                    print(f"     Value: '{value}'")
                elif prop_type == "url" and prop_data.get("url"):
                    print(f"     Value: '{prop_data['url']}'")
        else:
            print(f"❌ Could not retrieve page: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error retrieving page: {e}")

    # 2. Search all databases for TensorFlow entries
    print("\n📋 STEP 2: Search All Databases for TensorFlow")
    print("-" * 50)

    databases_to_search = ["accounts", "contacts", "trigger_events", "partnerships"]
    tensorflow_entries = {}

    for db_name in databases_to_search:
        if db_name not in notion_client.database_ids:
            print(f"⚠️  Skipping {db_name} - database ID not configured")
            continue

        print(f"\n🔍 Searching {db_name} database...")
        try:
            db_id = notion_client.database_ids[db_name]
            url = f"https://api.notion.com/v1/databases/{db_id}/query"

            # Search for TensorFlow
            search_filter = {
                "filter": {
                    "or": [
                        {
                            "property": "Company Name" if db_name == "partnerships" else "Company",
                            "rich_text": {"contains": "TensorFlow"},
                        },
                        {
                            "property": "Company Name" if db_name == "partnerships" else "Company",
                            "rich_text": {"contains": "Tensor"},
                        },
                    ]
                }
            }

            response = notion_client._make_request("POST", url, json=search_filter)
            results = response.json().get("results", [])

            if results:
                tensorflow_entries[db_name] = results
                print(f"   ✅ Found {len(results)} TensorFlow entries in {db_name}")

                for i, entry in enumerate(results, 1):
                    entry_id = entry.get("id", "unknown")
                    props = entry.get("properties", {})

                    # Try to get the company name
                    company_name = "Unknown"
                    company_field_name = "Company Name" if db_name == "partnerships" else "Company"

                    if company_field_name in props:
                        company_prop = props[company_field_name]
                        if company_prop.get("type") == "rich_text":
                            text_parts = [
                                t.get("text", {}).get("content", "")
                                for t in company_prop.get("rich_text", [])
                            ]
                            company_name = "".join(text_parts)
                        elif company_prop.get("type") == "title":
                            text_parts = [
                                t.get("text", {}).get("content", "")
                                for t in company_prop.get("title", [])
                            ]
                            company_name = "".join(text_parts)

                    print(f"     Entry {i}: {company_name} (ID: {entry_id[:8]}...)")

                    # Check if this matches the page we're investigating
                    if entry_id.replace("-", "") == page_id:
                        print(f"     🎯 MATCH: This is the page from your URL!")
            else:
                print(f"   ❌ No TensorFlow entries found in {db_name}")

        except Exception as e:
            print(f"   ❌ Error searching {db_name}: {e}")

    # 3. Analyze the findings
    print("\n📊 STEP 3: Analysis")
    print("-" * 30)

    if tensorflow_entries:
        print("📋 TensorFlow entries found:")
        total_entries = sum(len(entries) for entries in tensorflow_entries.values())
        print(f"   📊 Total entries: {total_entries}")

        for db_name, entries in tensorflow_entries.items():
            print(f"   • {db_name}: {len(entries)} entries")

        print("\n🔍 Issues identified:")
        if len(tensorflow_entries) > 1:
            print("   ⚠️  TensorFlow data is scattered across multiple databases")
            print("   ⚠️  This suggests missing database relationships")

        if (
            "partnerships" in tensorflow_entries
            and len(tensorflow_entries.get("partnerships", [])) > 0
        ):
            print("   ⚠️  TensorFlow appears as partnership instead of account")
            print("   ⚠️  This indicates incorrect data classification")

        if "accounts" not in tensorflow_entries or len(tensorflow_entries.get("accounts", [])) == 0:
            print("   ⚠️  No TensorFlow account entry found")
            print("   ⚠️  Missing primary account record")
    else:
        print("❌ No TensorFlow entries found in any database")
        print("⚠️  This suggests the data may be in a different location or format")

    return tensorflow_entries


def analyze_database_structure():
    """Analyze the overall database structure to understand relation issues"""

    print("\n🏗️  DATABASE STRUCTURE ANALYSIS")
    print("=" * 50)

    notion_client = NotionClient()

    # Get schema for each database
    for db_name in ["accounts", "contacts", "trigger_events", "partnerships"]:
        if db_name not in notion_client.database_ids:
            continue

        print(f"\n📋 {db_name.title()} Database Schema:")
        try:
            db_id = notion_client.database_ids[db_name]
            response = notion_client._make_request(
                "GET", f"https://api.notion.com/v1/databases/{db_id}"
            )

            if response.status_code == 200:
                db_data = response.json()
                properties = db_data.get("properties", {})

                for prop_name, prop_info in properties.items():
                    prop_type = prop_info.get("type", "unknown")
                    print(f"   • {prop_name}: {prop_type}")

                    # Check for relation fields
                    if prop_type == "relation":
                        related_db = prop_info.get("relation", {}).get("database_id")
                        print(f"     → Relations to: {related_db}")
            else:
                print(f"   ❌ Could not retrieve schema: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error getting schema: {e}")


if __name__ == "__main__":
    # Run investigation
    tensorflow_entries = investigate_tensorflow_page()
    analyze_database_structure()

    print("\n🎉 INVESTIGATION COMPLETE")
    print("=" * 30)
    print("Summary of findings will help identify the database structure issue")
    print("and explain why TensorFlow appears as partnership instead of account.")
