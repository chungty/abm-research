#!/usr/bin/env python3
"""
Test ABM system with new API-based company enrichment
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from abm_research.core.abm_system import ComprehensiveABMSystem

def test_abm_with_api_enrichment():
    """Test ABM system end-to-end with API-based company enrichment"""

    print("🧪 Testing ABM System with API-based Company Enrichment")
    print("=" * 60)

    # Test companies
    test_companies = [
        ("Genesis Cloud", "genesiscloud.com"),
        ("Groq", "groq.com")
    ]

    try:
        abm_system = ComprehensiveABMSystem()

        for company_name, domain in test_companies:
            print(f"\n🏢 Processing: {company_name} ({domain})")

            results = abm_system.conduct_complete_account_research(
                company_name=company_name,
                company_domain=domain
            )

            # Check account intelligence results
            account_intel = results.get('account_intelligence', {})
            print(f"✓ Employee Count: {account_intel.get('employee_count')}")
            print(f"✓ Business Model: {account_intel.get('business_model')}")
            print(f"✓ Apollo Account ID: {account_intel.get('apollo_account_id', 'N/A')}")
            print(f"✓ Enrichment Source: {account_intel.get('enrichment_source', 'N/A')}")
            print(f"✓ ICP Fit Score: {account_intel.get('icp_fit_score')}")

            # Verify no hardcoded defaults were used
            if account_intel.get('employee_count') == 500:
                print("❌ WARNING: Hardcoded employee count detected!")
            elif account_intel.get('business_model') == 'B2B Software' and 'Software' not in company_name:
                print("❌ WARNING: Generic business model detected!")
            else:
                print("✅ No hardcoded defaults detected")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_abm_with_api_enrichment()