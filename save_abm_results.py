#!/usr/bin/env python3
"""
Save Value-First ABM Results to JSON for Manual Import
"""

import os
import json
from datetime import datetime
from value_first_abm_system import ValueFirstABMSystem

def main():
    """Save enhanced ABM results to JSON file"""

    print("💾 Saving Value-First ABM Results to JSON\n")

    # Initialize system
    abm_system = ValueFirstABMSystem()

    # Research target accounts
    target_accounts = ["genesiscloud.com", "datacrunch.io", "leadergpu.com"]
    all_results = {}

    print(f"🎯 Researching {len(target_accounts)} target accounts...")

    for domain in target_accounts:
        print(f"\n📊 Researching {domain}...")
        results = abm_system.research_account_value_first(domain)

        if results:
            all_results[domain] = results
            print(f"✅ {domain}: {results.get('total_contacts')} contacts, {results.get('high_signal_contacts')} high signal")

    if not all_results:
        print("❌ No ABM results to save")
        return

    # Save to JSON file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/Users/chungty/Projects/vdg-clean/abm-research/abm_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)

        print(f"\n✅ RESULTS SAVED TO: {filename}")

        # Show summary
        total_contacts = sum(r.get('total_contacts', 0) for r in all_results.values())
        total_high_signal = sum(r.get('high_signal_contacts', 0) for r in all_results.values())
        total_medium_signal = sum(r.get('medium_signal_contacts', 0) for r in all_results.values())

        print(f"\n📊 VALUE-FIRST ABM SUMMARY:")
        print(f"   Accounts Researched: {len(all_results)}")
        print(f"   Total Contacts: {total_contacts}")
        print(f"   High Signal (Problem/Solution): {total_high_signal}")
        print(f"   Medium Signal (Industry Insights): {total_medium_signal}")

        # Show sample high-signal intelligence
        print(f"\n🎯 SAMPLE HIGH-SIGNAL INTELLIGENCE:")

        for domain, results in list(all_results.items())[:2]:
            high_contacts = [c for c in results['contacts'] if c.get('signal_level') == 'high']

            if high_contacts:
                contact = high_contacts[0]
                print(f"\n👤 {contact.get('name')} at {results['company_context']['name']}")
                print(f"   Title: {contact.get('title')}")
                print(f"   Score: {contact.get('final_lead_score')}/100")
                print(f"   Signal: {contact.get('signal_level')}")

                if contact.get('problem_statement'):
                    print(f"   🎯 Problem: {contact.get('problem_statement')[:120]}...")

                if contact.get('solution_value'):
                    print(f"   💡 Solution: {contact.get('solution_value')[:120]}...")

                if contact.get('email_subject'):
                    print(f"   📧 Subject: {contact.get('email_subject')}")

        print(f"\n📄 Full results available in: {filename}")

    except Exception as e:
        print(f"❌ Failed to save results: {e}")

if __name__ == '__main__':
    main()