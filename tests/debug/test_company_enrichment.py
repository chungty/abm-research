#!/usr/bin/env python3
"""
Test script for the new API-based company enrichment service
"""

import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from abm_research.utils.company_enrichment_service import company_enrichment_service

def test_company_enrichment():
    """Test company enrichment with real companies"""

    test_companies = [
        # Test with well-known companies Apollo likely has data for
        ('Slack', 'slack.com'),
        ('Microsoft', 'microsoft.com'),
        # Test with our target companies
        ('Genesis Cloud', 'genesiscloud.com'),
        ('Groq', 'groq.com'),
    ]

    print("🧪 Testing API-based company enrichment...")
    print("=" * 50)

    for company_name, domain in test_companies:
        print(f"\n🏢 Testing: {company_name} ({domain})")
        try:
            company_data = company_enrichment_service.enrich_company(company_name, domain)

            print(f"  ✓ Employee Count: {company_data.employee_count}")
            print(f"  ✓ Business Model: {company_data.business_model}")
            print(f"  ✓ Industry: {company_data.industry}")
            print(f"  ✓ Apollo Account ID: {company_data.apollo_account_id}")
            print(f"  ✓ Enrichment Source: {company_data.enrichment_source}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n📊 Enrichment Statistics:")
    stats = company_enrichment_service.get_enrichment_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_company_enrichment()
