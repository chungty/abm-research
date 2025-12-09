#!/usr/bin/env python3
"""
Populate Real ABM Data for Target Companies
Runs comprehensive ABM research for all 7 specified companies using existing scripts
"""

import sys
import time
from datetime import datetime
from abm_system import ComprehensiveABMSystem


def main():
    print("🚀 REAL ABM DATA POPULATION")
    print("=" * 50)
    print("📊 Populating Notion databases with real data using existing research workflows")
    print()

    # Define the 7 target companies
    target_companies = [
        {"name": "Genesis Cloud", "domain": "genesiscloud.com"},
        {"name": "DataCrunch", "domain": "datacrunch.io"},
        {"name": "LeaderGPU", "domain": "leadergpu.com"},
        {"name": "FlexAI", "domain": "flex.ai"},
        {"name": "EdgeConneX", "domain": "edgeconnex.com"},
        {"name": "Fluidstack", "domain": "fluidstack.io"},
        {"name": "Groq", "domain": "groq.com"},
    ]

    print(f"📋 Target companies ({len(target_companies)}):")
    for i, company in enumerate(target_companies, 1):
        print(f"  {i}. {company['name']} ({company['domain']})")
    print()

    # Initialize the comprehensive ABM system
    try:
        print("🔧 Initializing Comprehensive ABM Research System...")
        abm_system = ComprehensiveABMSystem()
        print("✅ ABM system initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize ABM system: {e}")
        return False

    # Process each company
    overall_start_time = datetime.now()
    successful_researches = 0
    failed_researches = 0

    for i, company in enumerate(target_companies, 1):
        print(f"🎯 [{i}/{len(target_companies)}] Starting research for {company['name']}")
        print(f"🌐 Domain: {company['domain']}")
        print("-" * 40)

        try:
            # Run comprehensive research
            research_start = datetime.now()

            research_results = abm_system.conduct_complete_account_research(
                company["name"], company["domain"]
            )

            research_duration = (datetime.now() - research_start).total_seconds()

            # Check if research was successful
            if research_results.get("research_summary", {}).get("status") == "failed":
                print(
                    f"❌ Research failed for {company['name']}: {research_results['research_summary'].get('error', 'Unknown error')}"
                )
                failed_researches += 1
            else:
                print(
                    f"✅ Research completed for {company['name']} in {research_duration:.1f} seconds"
                )
                successful_researches += 1

                # Show summary stats
                account_data = research_results.get("account", {})
                contacts_count = len(research_results.get("contacts", []))
                events_count = len(research_results.get("events", []))
                partnerships_count = len(research_results.get("partnerships", []))

                print(f"   📊 ICP Fit: {account_data.get('icp_fit_score', 0)}")
                print(f"   👥 Contacts: {contacts_count}")
                print(f"   🔔 Trigger Events: {events_count}")
                print(f"   🤝 Partnerships: {partnerships_count}")

        except Exception as e:
            print(f"❌ Exception during research for {company['name']}: {e}")
            failed_researches += 1

        print()

        # Add delay between companies to be respectful to APIs
        if i < len(target_companies):
            print("⏳ Waiting 30 seconds before next company...")
            time.sleep(30)

    # Final summary
    overall_duration = (datetime.now() - overall_start_time).total_seconds()

    print("🏁 REAL DATA POPULATION COMPLETE")
    print("=" * 50)
    print(f"⏱️  Total Duration: {overall_duration:.1f} seconds")
    print(f"✅ Successful: {successful_researches}/{len(target_companies)}")
    print(f"❌ Failed: {failed_researches}/{len(target_companies)}")
    print()

    if successful_researches > 0:
        print("🎉 Real ABM data has been populated!")
        print("💡 The dashboard should now display authentic data with:")
        print("   • Real company accounts with ICP fit scores")
        print("   • Actual contacts from Apollo API")
        print("   • Live trigger events with source URLs")
        print("   • Strategic partnership intelligence")
        print("   • Genuine lead scoring and analytics")
        print()
        print("🚀 Access the enhanced dashboard at: http://localhost:8001")
    else:
        print("⚠️  No successful research completed. Check API keys and network connection.")

    return successful_researches > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
