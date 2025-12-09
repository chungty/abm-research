#!/usr/bin/env python3
"""
Test LinkedIn enrichment fix for missing enrich_contact method
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_linkedin_fix():
    """
    Test LinkedIn enrichment engine with the enrich_contact method fix
    """
    print("🧪 Testing LinkedIn Enrichment Fix")
    print("=" * 40)

    try:
        from abm_research.phases.linkedin_enrichment_engine import linkedin_enrichment_engine

        # Test contact data
        test_contact = {
            "name": "Lachlan Donald",
            "title": "VP of Engineering Infrastructure",
            "company": "Groq",
            "linkedin_url": "https://linkedin.com/in/example",
            "lead_score": 85,  # High score to trigger enrichment
        }

        print(f"👤 Testing contact: {test_contact['name']}")
        print(f"📊 Lead score: {test_contact['lead_score']}")

        # Test if the enrich_contact method exists
        if hasattr(linkedin_enrichment_engine, "enrich_contact"):
            print("✅ enrich_contact method found")

            # Test the method call
            print("🔬 Testing enrich_contact method...")
            enriched_contact = linkedin_enrichment_engine.enrich_contact(test_contact)

            print("✅ LinkedIn enrichment successful!")
            print(f"📄 Enriched contact keys: {list(enriched_contact.keys())}")
            print(f"📊 Final lead score: {enriched_contact.get('final_lead_score', 'N/A')}")
            print(f"🔗 Enrichment status: {enriched_contact.get('enrichment_status', 'N/A')}")

        else:
            print("❌ enrich_contact method not found")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_linkedin_fix()
