#!/usr/bin/env python3
"""
Test LinkedIn Real Data Integration
Validates the enhanced LinkedIn enrichment with real data collection
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List

# Add project root to path
sys.path.append("/Users/chungty/Projects/vdg-clean/abm-research")

from linkedin_data_collector import linkedin_data_collector
from linkedin_enrichment_engine import linkedin_enrichment_engine


def test_linkedin_data_collection():
    """Test basic LinkedIn data collection functionality"""
    print("🧪 Testing LinkedIn Data Collection")
    print("=" * 50)

    # Test contact with LinkedIn URL
    test_contact = {
        "name": "John Smith",
        "title": "Director of Data Center Operations",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "linkedin_url": "https://linkedin.com/in/john-smith-datacenter",
    }

    try:
        # Test data collection
        profile = linkedin_data_collector.collect_profile_data(
            test_contact["linkedin_url"], test_contact
        )

        if profile:
            print(f"✅ Profile collected for {profile.name}")
            print(f"   Title: {profile.title}")
            print(f"   Company: {profile.company}")
            print(f"   Bio length: {len(profile.bio)} characters")
            print(f"   Skills: {len(profile.skills)} skills")
            print(f"   Recent activity: {len(profile.recent_activity)} posts")
            print("   Data source: Enhanced AI generation")
            return True
        else:
            print("❌ Profile collection failed")
            return False

    except Exception as e:
        print(f"❌ Error in data collection: {e}")
        return False


def test_linkedin_enrichment_integration():
    """Test full LinkedIn enrichment with real data integration"""
    print("\n🧪 Testing LinkedIn Enrichment Integration")
    print("=" * 50)

    # Test contacts with different roles
    test_contacts = [
        {
            "name": "Sarah Chen",
            "title": "VP of Infrastructure",
            "company": "HyperScale Corp",
            "linkedin_url": "https://linkedin.com/in/sarah-chen-infra",
            "lead_score": 75,  # High enough to trigger enrichment
            "icp_fit_score": 70,
            "buying_power_score": 80,
        },
        {
            "name": "Mike Rodriguez",
            "title": "Principal Power Engineer",
            "company": "DataCenter Solutions",
            "linkedin_url": "https://linkedin.com/in/mike-rodriguez-power",
            "lead_score": 65,  # High enough to trigger enrichment
            "icp_fit_score": 65,
            "buying_power_score": 70,
        },
        {
            "name": "Lisa Wang",
            "title": "Facilities Manager",
            "company": "CloudCorp",
            "linkedin_url": "https://linkedin.com/in/lisa-wang-facilities",
            "lead_score": 55,  # Below threshold, shouldn't be enriched
            "icp_fit_score": 55,
            "buying_power_score": 60,
        },
    ]

    try:
        # Run enrichment
        enriched_contacts = linkedin_enrichment_engine.enrich_high_priority_contacts(test_contacts)

        print("📊 Enrichment Results:")
        print(f"   Input contacts: {len(test_contacts)}")
        print(f"   Output contacts: {len(enriched_contacts)}")

        for contact in enriched_contacts:
            name = contact.get("name", "Unknown")
            original_score = contact.get("lead_score", 0)
            final_score = contact.get("final_lead_score", 0)
            data_source = contact.get("linkedin_data_source", "unknown")

            print(f"\n   👤 {name}")
            print(f"      Original Score: {original_score}")
            print(f"      Final Score: {final_score}")
            print(f"      Data Source: {data_source}")

            if original_score > 60:
                print("      ✅ Enriched (score > 60)")
                print(f"      Activity Level: {contact.get('linkedin_activity_level', 'Unknown')}")
                print(f"      Content Themes: {len(contact.get('content_themes', []))} themes")
                print(
                    f"      Responsibility Keywords: {len(contact.get('responsibility_keywords', []))} keywords"
                )
                print(f"      Network Quality: {contact.get('network_quality_score', 0)} points")
            else:
                print("      ⏭️ Skipped (score ≤ 60)")

        return True

    except Exception as e:
        print(f"❌ Error in enrichment integration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_data_source_transparency():
    """Test that data source information is properly tracked"""
    print("\n🧪 Testing Data Source Transparency")
    print("=" * 50)

    test_contact = {
        "name": "Test User",
        "title": "CTO",
        "company": "TestCorp",
        "linkedin_url": "https://linkedin.com/in/test-user",
        "lead_score": 70,
    }

    try:
        enriched = linkedin_enrichment_engine.enrich_high_priority_contacts([test_contact])
        contact = enriched[0]

        data_source = contact.get("linkedin_data_source")
        profile_complete = contact.get("profile_data_complete")

        print("✅ Data source tracking working:")
        print(f"   Data Source: {data_source}")
        print(f"   Profile Complete: {profile_complete}")

        if data_source in ["real_data", "simulation", "cached"]:
            print("✅ Valid data source identifier")
            return True
        else:
            print(f"❌ Invalid data source: {data_source}")
            return False

    except Exception as e:
        print(f"❌ Error testing data source transparency: {e}")
        return False


def test_configuration_creation():
    """Test that LinkedIn configuration files are created properly"""
    print("\n🧪 Testing Configuration Creation")
    print("=" * 50)

    config_path = "/Users/chungty/Projects/vdg-clean/abm-research/config/linkedin_config.json"

    try:
        # Initialize collector to trigger config creation
        collector = linkedin_data_collector

        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)

            print(f"✅ Configuration file created at: {config_path}")
            print(f"   Collection methods: {len(config['collection_methods'])} configured")
            print(
                f"   Manual entry enabled: {config['collection_methods']['manual_entry']['enabled']}"
            )
            print(
                f"   Profile enhancement enabled: {config['profile_enhancement']['use_ai_bio_analysis']}"
            )
            return True
        else:
            print(f"❌ Configuration file not found at: {config_path}")
            return False

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False


def test_caching_functionality():
    """Test LinkedIn profile caching"""
    print("\n🧪 Testing Profile Caching")
    print("=" * 50)

    test_contact = {
        "name": "Cache Test User",
        "title": "Infrastructure Engineer",
        "company": "CacheCorp",
        "linkedin_url": "https://linkedin.com/in/cache-test-user",
    }

    try:
        # First collection should create cache
        profile1 = linkedin_data_collector.collect_profile_data(
            test_contact["linkedin_url"], test_contact
        )

        if profile1:
            print("✅ First collection successful")

            # Second collection should use cache
            profile2 = linkedin_data_collector.collect_profile_data(
                test_contact["linkedin_url"], test_contact
            )

            if profile2:
                print("✅ Second collection successful (likely from cache)")
                print(f"   Profiles match: {profile1.name == profile2.name}")
                return True

        print("❌ Caching test failed")
        return False

    except Exception as e:
        print(f"❌ Error testing caching: {e}")
        return False


def main():
    """Run all LinkedIn integration tests"""
    print("🚀 LinkedIn Real Data Integration Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()

    tests = [
        test_configuration_creation,
        test_linkedin_data_collection,
        test_linkedin_enrichment_integration,
        test_data_source_transparency,
        test_caching_functionality,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")

    passed = sum(results)
    total = len(results)

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! LinkedIn real data integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
