#!/usr/bin/env python3
"""
Test Apollo bulk enrichment fix for 400 error
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from abm_research.phases.apollo_contact_discovery import apollo_discovery

def test_apollo_fix():
    """
    Test Apollo contact discovery with the bulk enrichment fix
    """
    print("🧪 Testing Apollo Bulk Enrichment Fix")
    print("=" * 40)

    try:
        # Test with a company that has contacts
        print("🔍 Testing contact discovery for Groq...")
        contacts = apollo_discovery.discover_contacts(
            company_name="Groq",
            company_domain="groq.com",
            max_contacts=3  # Small test batch
        )

        print(f"✅ Found {len(contacts)} contacts")

        for i, contact in enumerate(contacts, 1):
            print(f"\n👤 Contact {i}:")
            print(f"  Name: {contact.name}")
            print(f"  Title: {contact.title}")
            print(f"  Company: {contact.company_name}")
            print(f"  Email: {contact.email}")
            print(f"  LinkedIn: {contact.linkedin_url}")
            print(f"  Enriched: {contact.enriched}")

        # Test enrichment specifically
        if contacts:
            print(f"\n🔬 Testing bulk enrichment on {len(contacts)} contacts...")

            # This should now work without 400 errors
            enriched = apollo_discovery._enrich_contact_batch(contacts)

            print(f"✅ Bulk enrichment successful!")
            print(f"📊 Enriched {len(enriched)} contacts")

            enriched_count = sum(1 for c in enriched if c.enriched)
            print(f"📧 Contacts with email data: {enriched_count}/{len(enriched)}")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_apollo_fix()