#!/usr/bin/env python3
"""
Enrich existing accounts in Notion using new API-based company enrichment service
Replaces hardcoded data with real Apollo API data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from abm_research.utils.company_enrichment_service import company_enrichment_service
from abm_research.integrations.notion_client import NotionClient

def enrich_existing_accounts():
    """
    Retrieve existing accounts from Notion and enrich them with API-based data
    """
    print("🔄 Enriching Existing Accounts with API-based Data")
    print("=" * 60)

    # Known accounts to enrich (from previous audit)
    target_companies = [
        ('Genesis Cloud', 'genesiscloud.com'),
        ('DataCrunch', 'datacrunch.io'),
        ('LeaderGPU', 'leadergpu.com'),
        ('Flex.ai', 'flex.ai'),
        ('EdgeConnex', 'edgeconnex.com'),
        ('Fluidstack', 'fluidstack.io'),
        ('Groq', 'groq.com'),
    ]

    try:
        # Initialize Notion client
        notion_client = NotionClient()
        print(f"✅ Notion client initialized")

        # Get current accounts from Notion
        print(f"\n📋 Retrieving current accounts from Notion...")
        current_accounts = notion_client.query_all_accounts()
        print(f"Found {len(current_accounts)} existing accounts")

        enriched_count = 0
        for company_name, domain in target_companies:
            print(f"\n🏢 Processing: {company_name} ({domain})")

            # Check if CoreWeave and skip (remove mock data)
            if 'coreweave' in domain.lower() or 'coreweave' in company_name.lower():
                print("⚠️  Skipping CoreWeave - removing mock data")
                continue

            try:
                # Use our new API-based enrichment service
                company_data = company_enrichment_service.enrich_company(company_name, domain)

                print(f"  ✓ Employee Count: {company_data.employee_count}")
                print(f"  ✓ Business Model: {company_data.business_model}")
                print(f"  ✓ Industry: {company_data.industry}")
                print(f"  ✓ Apollo Account ID: {company_data.apollo_account_id}")
                print(f"  ✓ Enrichment Source: {company_data.enrichment_source}")

                # Prepare account data for Notion
                account_data = {
                    'name': company_name,
                    'domain': domain,
                    'employee_count': company_data.employee_count or 0,
                    'business_model': company_data.business_model or 'Technology Company',
                    'industry': company_data.industry or 'Technology',
                    'apollo_account_id': company_data.apollo_account_id or '',
                    'apollo_organization_id': company_data.apollo_organization_id or '',
                    'description': company_data.description or '',
                    'linkedin_url': company_data.linkedin_url or '',
                    # Add ICP scoring (simplified for this script)
                    'icp_fit_score': 60,  # Default infrastructure relevance score
                    'title_match_score': 45,
                    'responsibility_keywords_score': 40,
                    'trigger_events_count': 1,
                    'trigger_events_impact': 'Recent infrastructure developments',
                    'icp_calculation_details': f'API enrichment via {company_data.enrichment_source}',
                    'infrastructure_relevance': 'Medium'
                }

                # Check if account already exists in Notion
                existing_account = None
                for account in current_accounts:
                    account_name = account.get('properties', {}).get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                    if account_name.lower() == company_name.lower():
                        existing_account = account
                        break

                if existing_account:
                    print(f"  📝 Updating existing account...")
                    # Update existing account
                    account_id = existing_account['id']
                    success = notion_client._update_account(account_id, account_data)
                    if success:
                        print(f"  ✅ Successfully updated account")
                        enriched_count += 1
                    else:
                        print(f"  ❌ Failed to update account")
                else:
                    print(f"  📝 Creating new account...")
                    # Create new account
                    account_id = notion_client._create_account(account_data)
                    if account_id:
                        print(f"  ✅ Successfully created account: {account_id}")
                        enriched_count += 1
                    else:
                        print(f"  ❌ Failed to create account")

            except ValueError as ve:
                if "CoreWeave is mock data" in str(ve):
                    print("  ⚠️  Skipped CoreWeave mock data")
                    continue
                else:
                    print(f"  ❌ Error: {ve}")
            except Exception as e:
                print(f"  ❌ Error enriching {company_name}: {e}")

        print(f"\n📊 Enrichment Summary:")
        print(f"  Companies processed: {len([c for c in target_companies if 'coreweave' not in c[1].lower()])}")
        print(f"  Successfully enriched: {enriched_count}")

        # Show enrichment statistics
        print(f"\n📈 API Enrichment Statistics:")
        stats = company_enrichment_service.get_enrichment_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    enrich_existing_accounts()
