#!/usr/bin/env python3
"""
Enrichment Script - Contacts via Apollo + Partnerships via Brave Search
Saves all data to Notion
"""
import asyncio
import os
import time

import aiohttp
import requests

# Load env from file
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key] = val

# Config
APOLLO_API_KEY = os.environ["APOLLO_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
CONTACTS_DB = os.environ["NOTION_CONTACTS_DB_ID"]
PARTNERSHIPS_DB = os.environ["NOTION_PARTNERSHIPS_DB_ID"]

notion_headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# Accounts with their domains
ACCOUNTS = {
    "2b27f5fe-e5e2-81e8-8ee3-e502a738642b": {"name": "Genesis Cloud", "domain": "genesiscloud.com"},
    "2b47f5fe-e5e2-812b-96cf-d940f24bf4c2": {"name": "DataCrunch", "domain": "datacrunch.io"},
    "2b47f5fe-e5e2-8139-8e46-d73ac4ac65d0": {"name": "FlexAI", "domain": "flex.ai"},
    "2b47f5fe-e5e2-813a-986e-f90e42d886f7": {"name": "LeaderGPU", "domain": "leadergpu.com"},
    "2b47f5fe-e5e2-81a6-9c62-ef498b0a7cbd": {"name": "EdgeConnex", "domain": "edgeconnex.com"},
    "2b47f5fe-e5e2-81ef-b180-d74a630da7e3": {"name": "Fluidstack", "domain": "fluidstack.io"},
    "2b47f5fe-e5e2-81fa-9b98-dd0d476324a8": {"name": "Groq", "domain": "groq.com"},
}

TARGET_TITLES = [
    "DevOps",
    "SRE",
    "Infrastructure",
    "Cloud",
    "Platform",
    "Director",
    "Manager",
    "VP",
    "CTO",
    "CFO",
    "CEO",
    "Founder",
    "Head of",
]

# Known vendors for partnership discovery
KNOWN_VENDORS = [
    "NVIDIA",
    "AMD",
    "Intel",
    "Schneider Electric",
    "Vertiv",
    "Equinix",
    "AWS",
    "Google Cloud",
    "Microsoft Azure",
]


def classify_meddic_role(title):
    title_lower = title.lower() if title else ""
    if any(t in title_lower for t in ["cto", "cfo", "ceo", "chief", "founder", "vp", "president"]):
        return "economic_buyer"
    elif any(t in title_lower for t in ["director", "manager", "head of", "lead"]):
        return "middle_decider"
    return "entry_point"


async def search_apollo_contacts(domain, limit=5):
    """Search Apollo for contacts at a company"""
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY,
    }
    payload = {
        "q_organization_domains": domain,
        "page": 1,
        "per_page": limit,
        "person_titles": TARGET_TITLES,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("people", [])
                print(f"  Apollo error: {response.status}")
                return []
    except Exception as e:
        print(f"  Apollo exception: {e}")
        return []


def save_contact_to_notion(contact, account_id, account_name):
    """Save a contact to Notion Contacts database"""
    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
    if not name:
        name = contact.get("name", "Unknown")
    title = contact.get("title", "Unknown")

    properties = {
        "Name": {"title": [{"text": {"content": name[:100]}}]},
        "Title": {"rich_text": [{"text": {"content": title[:200] if title else ""}}]},
        "Account": {"relation": [{"id": account_id}]},
        "Buying committee role": {"select": {"name": classify_meddic_role(title)}},
        "Name Source": {"select": {"name": "Apollo"}},
        "Title Source": {"select": {"name": "Apollo"}},
    }

    if contact.get("email"):
        properties["Email"] = {"email": contact["email"]}
        properties["Email Source"] = {"select": {"name": "Apollo"}}
    if contact.get("linkedin_url"):
        properties["LinkedIn URL"] = {"url": contact["linkedin_url"]}
    if contact.get("id"):
        properties["Apollo Person ID"] = {"rich_text": [{"text": {"content": contact["id"]}}]}

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=notion_headers,
        json={"parent": {"database_id": CONTACTS_DB}, "properties": properties},
    )
    return response.status_code == 200


async def search_brave_vendor(company_name, vendor_name):
    """Search Brave for vendor relationship signals"""
    if not BRAVE_API_KEY:
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"}
    query = f'"{company_name}" "{vendor_name}" partnership OR customer OR using'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, params={"q": query, "count": 5}, timeout=15
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("web", {}).get("results", [])
                elif response.status == 429:
                    print(f"    Rate limited on {vendor_name}")
                    await asyncio.sleep(2)
                return []
    except Exception as e:
        print(f"    Brave exception: {e}")
        return []


def save_partnership_to_notion(vendor_name, account_id, account_name, evidence):
    """Save a partnership to Notion Partnerships database"""
    properties = {
        "Partner Name": {"title": [{"text": {"content": vendor_name[:100]}}]},
        "Account": {"relation": [{"id": account_id}]},
        "Partnership Type": {"select": {"name": "Strategic Partner"}},
        "Relevance Score": {"number": 70},
        "Context": {"rich_text": [{"text": {"content": evidence[:500] if evidence else ""}}]},
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=notion_headers,
        json={"parent": {"database_id": PARTNERSHIPS_DB}, "properties": properties},
    )
    return response.status_code == 200


async def enrich_contacts(account_id, info):
    """Enrich contacts for a single account"""
    print(f"\n📧 Contacts: {info['name']} ({info['domain']})")

    contacts = await search_apollo_contacts(info["domain"], limit=5)
    if not contacts:
        print("  No contacts found")
        return 0

    saved = 0
    for contact in contacts:
        name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        title = contact.get("title", "N/A")
        if save_contact_to_notion(contact, account_id, info["name"]):
            print(f"  ✓ {name} - {title[:40]}")
            saved += 1
        time.sleep(0.3)
    return saved


async def discover_partnerships(account_id, info):
    """Discover partnerships for a single account"""
    print(f"\n🤝 Partnerships: {info['name']}")

    if not BRAVE_API_KEY:
        print("  No Brave API key - skipping")
        return 0

    saved = 0
    for vendor in KNOWN_VENDORS[:5]:  # Limit to first 5 vendors to save API calls
        results = await search_brave_vendor(info["name"], vendor)
        if results:
            evidence = results[0].get("description", "")[:200] if results else ""
            if save_partnership_to_notion(vendor, account_id, info["name"], evidence):
                print(f"  ✓ {vendor}")
                saved += 1
        await asyncio.sleep(1)  # Rate limit

    return saved


async def main():
    print("=" * 50)
    print("NOTION DATA ENRICHMENT")
    print("=" * 50)

    total_contacts = 0
    total_partnerships = 0

    for account_id, info in ACCOUNTS.items():
        # Enrich contacts
        total_contacts += await enrich_contacts(account_id, info)
        time.sleep(1)

        # Discover partnerships
        total_partnerships += await discover_partnerships(account_id, info)
        time.sleep(1)

    print("\n" + "=" * 50)
    print(f"COMPLETE: {total_contacts} contacts, {total_partnerships} partnerships saved")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
