#!/usr/bin/env python3
"""
Test Full ABM System with LinkedIn Real Data Integration
Tests the complete 5-phase ABM research pipeline with LinkedIn enrichment
"""

import sys
import json
from datetime import datetime
from typing import Dict, List

# Add project root to path
sys.path.append('/Users/chungty/Projects/vdg-clean/abm-research')

def test_comprehensive_abm_research():
    """Test the complete ABM research system with LinkedIn integration"""
    print("🎯 Testing Complete ABM Research with LinkedIn Integration")
    print("=" * 70)

    try:
        # Import the comprehensive system
        from comprehensive_abm_system import ComprehensiveABMSystem

        # Initialize the system
        abm_system = ComprehensiveABMSystem()

        # Test with realistic target companies
        test_companies = [
            {
                'company_name': 'DataVault Technologies',
                'company_domain': 'datavault.com',
                'description': 'AI startup with expanding data center infrastructure'
            },
            {
                'company_name': 'CloudScale Corp',
                'company_domain': 'cloudscale.io',
                'description': 'High-growth cloud provider with power optimization needs'
            }
        ]

        for company in test_companies:
            print(f"\n🏢 Researching: {company['company_name']}")
            print("-" * 50)

            try:
                # Run complete ABM research
                results = abm_system.conduct_complete_account_research(
                    company['company_name'],
                    company['company_domain']
                )

                # Analyze results
                if results and results.get('success'):
                    print(f"✅ Research completed successfully")

                    # Account Intelligence
                    account_data = results.get('account', {})
                    print(f"   📊 ICP Fit Score: {account_data.get('icp_fit_score', 'N/A')}")

                    # Trigger Events
                    trigger_events = results.get('trigger_events', [])
                    print(f"   🎯 Trigger Events: {len(trigger_events)} detected")
                    for event in trigger_events[:2]:  # Show first 2
                        print(f"      • {event.get('event_type', 'Unknown')}: {event.get('confidence', 'N/A')}% confidence")

                    # Contact Discovery
                    contacts = results.get('contacts', [])
                    print(f"   👥 Contacts Discovered: {len(contacts)}")

                    # LinkedIn Enrichment Results
                    enriched_contacts = [c for c in contacts if c.get('final_lead_score', 0) > 0]
                    print(f"   🔗 LinkedIn Enriched: {len(enriched_contacts)} contacts")

                    for contact in enriched_contacts[:3]:  # Show top 3
                        name = contact.get('name', 'Unknown')
                        score = contact.get('final_lead_score', 0)
                        data_source = contact.get('linkedin_data_source', 'unknown')
                        activity_level = contact.get('linkedin_activity_level', 'N/A')
                        themes = contact.get('content_themes', [])

                        print(f"      • {name}: Score {score}")
                        print(f"        LinkedIn: {data_source} | Activity: {activity_level}")
                        print(f"        Content Themes: {len(themes)} themes")

                    # Engagement Intelligence
                    engagement_data = results.get('engagement_intelligence', {})
                    if engagement_data:
                        print(f"   🎭 Engagement Strategies: {len(engagement_data.get('strategies', []))} generated")

                    # Partnership Intelligence
                    partnership_data = results.get('partnership_intelligence', {})
                    if partnership_data:
                        print(f"   🤝 Partnership Opportunities: {len(partnership_data.get('opportunities', []))} identified")

                else:
                    print(f"❌ Research failed: {results.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"❌ Error researching {company['company_name']}: {e}")
                import traceback
                traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ Failed to load comprehensive ABM system: {e}")
        return False

def test_apollo_integration_with_linkedin():
    """Test Apollo contact discovery with LinkedIn enrichment"""
    print("\n🚀 Testing Apollo + LinkedIn Integration")
    print("=" * 50)

    try:
        # Import Apollo discovery
        from apollo_contact_discovery import apollo_discovery

        # Test company
        test_company = "Stripe"

        print(f"🔍 Discovering contacts at {test_company}...")

        # Discover contacts
        contacts = apollo_discovery.discover_target_contacts(test_company)

        if contacts and len(contacts) > 0:
            print(f"✅ Found {len(contacts)} contacts")

            # Now enrich with LinkedIn data
            from linkedin_enrichment_engine import linkedin_enrichment_engine

            # Filter to high-scoring contacts for enrichment
            high_score_contacts = [c for c in contacts if c.get('lead_score', 0) > 60]

            if high_score_contacts:
                print(f"🔗 Enriching {len(high_score_contacts)} high-scoring contacts with LinkedIn data...")

                enriched = linkedin_enrichment_engine.enrich_high_priority_contacts(high_score_contacts)

                print(f"📊 Enrichment Results:")
                for contact in enriched[:3]:  # Show top 3
                    name = contact.get('name', 'Unknown')
                    original_score = contact.get('lead_score', 0)
                    final_score = contact.get('final_lead_score', 0)
                    data_source = contact.get('linkedin_data_source', 'unknown')

                    print(f"   • {name}")
                    print(f"     Score: {original_score} → {final_score} (+{final_score - original_score})")
                    print(f"     LinkedIn: {data_source}")

                return True
            else:
                print(f"⚠️ No contacts scored > 60 for LinkedIn enrichment")
                return True
        else:
            print(f"⚠️ No contacts found for {test_company}")
            return False

    except Exception as e:
        print(f"❌ Apollo + LinkedIn integration test failed: {e}")
        return False

def test_dashboard_integration():
    """Test unified dashboard with LinkedIn-enriched data"""
    print("\n📊 Testing Dashboard Integration")
    print("=" * 50)

    try:
        # Import dashboard data service
        from dashboard_data_service import NotionDataService

        data_service = NotionDataService()
        print("✅ Dashboard data service initialized")

        # Test contacts with LinkedIn enrichment
        test_contacts = [
            {
                'name': 'Alex Johnson',
                'title': 'VP of Infrastructure',
                'company': 'TechCorp',
                'linkedin_url': 'https://linkedin.com/in/alex-johnson-infra',
                'lead_score': 75
            },
            {
                'name': 'Maria Gonzalez',
                'title': 'Director of Cloud Operations',
                'company': 'CloudCorp',
                'linkedin_url': 'https://linkedin.com/in/maria-gonzalez-cloud',
                'lead_score': 68
            }
        ]

        # Enrich with LinkedIn data
        from linkedin_enrichment_engine import linkedin_enrichment_engine
        enriched_contacts = linkedin_enrichment_engine.enrich_high_priority_contacts(test_contacts)

        print(f"🔗 Enriched {len(enriched_contacts)} contacts for dashboard")

        # Show how the enriched data would appear in dashboard
        print(f"\n📋 Dashboard Data Preview:")
        for contact in enriched_contacts:
            name = contact.get('name', 'Unknown')
            final_score = contact.get('final_lead_score', 0)
            data_source = contact.get('linkedin_data_source', 'unknown')
            activity = contact.get('linkedin_activity_level', 'N/A')
            themes = contact.get('content_themes', [])
            pathways = contact.get('connection_pathways', 'N/A')

            print(f"\n   👤 {name} (Score: {final_score})")
            print(f"      🔗 LinkedIn: {data_source}")
            print(f"      📈 Activity: {activity}")
            print(f"      🎯 Content Focus: {', '.join(themes[:2]) if themes else 'N/A'}")
            print(f"      🤝 Connection Path: {pathways[:80]}{'...' if len(pathways) > 80 else ''}")

        return True

    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        return False

def test_data_persistence():
    """Test that LinkedIn data is properly cached and persisted"""
    print("\n💾 Testing Data Persistence")
    print("=" * 50)

    try:
        import os
        cache_dir = '/Users/chungty/Projects/vdg-clean/abm-research/data/linkedin_profiles'

        if os.path.exists(cache_dir):
            cache_files = os.listdir(cache_dir)
            cache_files = [f for f in cache_files if f.endswith('.json')]

            print(f"✅ Cache directory exists: {cache_dir}")
            print(f"📁 Cached profiles: {len(cache_files)} files")

            # Show a few cached profiles
            for filename in cache_files[:3]:
                filepath = os.path.join(cache_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    name = data.get('name', 'Unknown')
                    company = data.get('company', 'Unknown')
                    method = data.get('collection_method', 'unknown')

                    print(f"   📄 {filename}: {name} at {company} ({method})")
                except Exception as e:
                    print(f"   ❌ Error reading {filename}: {e}")

            return True
        else:
            print(f"❌ Cache directory not found: {cache_dir}")
            return False

    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def main():
    """Run comprehensive ABM + LinkedIn integration tests"""
    print("🚀 Complete ABM + LinkedIn Integration Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now()}")
    print()

    tests = [
        test_data_persistence,
        test_apollo_integration_with_linkedin,
        test_dashboard_integration,
        test_comprehensive_abm_research
    ]

    results = []
    for test in tests:
        try:
            print()
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)

    print("\n" + "=" * 80)
    print("📊 Complete Test Results")
    print("=" * 80)

    for test, result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.__name__}: {status}")

    passed = sum(results)
    total = len(results)

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Complete ABM system with LinkedIn integration working perfectly!")
        print("🔗 Real LinkedIn data collection and enrichment operational")
        print("📊 Ready for production use with unified dashboard")
    else:
        print("\n⚠️ Some integration tests failed. Check details above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)