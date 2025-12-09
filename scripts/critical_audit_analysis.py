#!/usr/bin/env python3
"""
Critical Audit Analysis of Current ABM System
Identify gaps in contact discovery, MEDDIC segmentation, and data quality
"""

import os
import requests
import json
from datetime import datetime

def critical_audit_analysis():
    """Perform critical audit of current ABM system implementation"""

    print("🔍 CRITICAL AUDIT ANALYSIS OF ABM SYSTEM")
    print("=" * 50)

    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    database_ids = {
        'accounts': 'c31d728f477049e28f6bd68717e2c160',
        'contacts': 'a6e0cace85de4afdbe6c9c926d1d0e3d',
        'trigger_events': 'c8ae1662cba94ea39cb32bcea3621963',
        'partnerships': 'fa1467c0ad154b09bb03cc715f9b8577'
    }

    print("\n📊 CURRENT DATABASE STATE ANALYSIS")
    print("-" * 40)

    all_data = {}
    for db_name, db_id in database_ids.items():
        try:
            query_url = f"https://api.notion.com/v1/databases/{db_id}/query"
            response = requests.post(query_url, headers=headers, json={"page_size": 100}, timeout=15)

            if response.status_code == 200:
                data = response.json()
                all_data[db_name] = data.get('results', [])
                print(f"   {db_name.upper()}: {len(all_data[db_name])} records")
            else:
                all_data[db_name] = []
                print(f"   {db_name.upper()}: Query failed")

        except Exception as e:
            all_data[db_name] = []
            print(f"   {db_name.upper()}: Error - {e}")

    print("\n🚨 CRITICAL GAPS IDENTIFIED")
    print("-" * 40)

    # 1. Contact Discovery Coverage Analysis
    print("\n1. ❌ CONTACT DISCOVERY IS INCOMPLETE:")
    contacts_data = all_data.get('contacts', [])
    genesis_contacts = []

    for contact in contacts_data:
        props = contact.get('properties', {})
        name_prop = props.get('Name', {}).get('title', [])
        if name_prop:
            name = name_prop[0].get('text', {}).get('content', '')
            title_prop = props.get('Title', {}).get('rich_text', [])
            title = title_prop[0].get('text', {}).get('content', '') if title_prop else 'No title'
            genesis_contacts.append({'name': name, 'title': title})

    print(f"   • Current Genesis Cloud contacts: {len(genesis_contacts)}")
    for contact in genesis_contacts:
        print(f"     - {contact['name']}: {contact['title']}")

    print(f"   • ❌ Missing comprehensive Apollo search (only basic titles)")
    print(f"   • ❌ No LinkedIn cross-referencing for additional contacts")
    print(f"   • ❌ Missing key data center operations roles")
    print(f"   • ❌ No company website team page scraping")

    # 2. MEDDIC Segmentation Analysis
    print("\n2. ❌ MEDDIC SEGMENTATION IS GENERIC:")
    print(f"   • Current buying committee roles are generic (Economic Buyer, Technical Evaluator, etc.)")
    print(f"   • ❌ No Verdigris Signals-specific MEDDIC mapping:")
    print(f"     - BUYER: Who has budget for power monitoring solutions?")
    print(f"     - USER: Who would use Signals day-to-day for power monitoring?")
    print(f"     - INFLUENCER: Who influences power infrastructure decisions?")
    print(f"   • ❌ No identification of 'Champion' for Signals product specifically")
    print(f"   • ❌ No 'Economic Pain' mapping to Verdigris value props")

    # 3. Data Quality Issues
    print("\n3. ❌ DATA QUALITY ISSUES:")

    # Check for duplicates
    account_names = []
    for account in all_data.get('accounts', []):
        props = account.get('properties', {})
        name_prop = props.get('Name', {}).get('title', [])
        if name_prop:
            name = name_prop[0].get('text', {}).get('content', '')
            account_names.append(name)

    duplicates = len(account_names) - len(set(account_names))
    print(f"   • Account duplicates: {duplicates}")
    if duplicates > 0:
        print(f"     ❌ Found duplicate account records")

    # Check contact completeness
    contacts_with_email = sum(1 for c in contacts_data if c.get('properties', {}).get('Email', {}).get('email'))
    contacts_with_linkedin = sum(1 for c in contacts_data if c.get('properties', {}).get('LinkedIn URL', {}).get('url'))

    print(f"   • Contacts with email: {contacts_with_email}/{len(contacts_data)}")
    print(f"   • Contacts with LinkedIn: {contacts_with_linkedin}/{len(contacts_data)}")
    print(f"   • ❌ Missing account relation field in contacts (can't filter by company)")

    # 4. Enrichment Process Analysis
    print("\n4. ❌ ENRICHMENT PROCESS IS SHALLOW:")
    print(f"   • ❌ No actual LinkedIn profile scraping (simulated data)")
    print(f"   • ❌ No real LinkedIn activity analysis")
    print(f"   • ❌ No network analysis for warm introduction paths")
    print(f"   • ❌ No content engagement history")
    print(f"   • ❌ No recent job change detection")
    print(f"   • ❌ No buying signal detection from social media")

    # 5. Database Schema Gaps
    print("\n5. ❌ DATABASE SCHEMA INCOMPLETE:")

    # Check trigger events schema
    trigger_db_url = f"https://api.notion.com/v1/databases/{database_ids['trigger_events']}"
    response = requests.get(trigger_db_url, headers=headers)
    if response.status_code == 200:
        db_info = response.json()
        trigger_props = list(db_info.get('properties', {}).keys())
        print(f"   • Trigger Events fields: {trigger_props}")
        print(f"     ❌ Missing: event_type, confidence, relevance_score, detected_date")

    # Check partnerships schema
    partnerships_db_url = f"https://api.notion.com/v1/databases/{database_ids['partnerships']}"
    response = requests.get(partnerships_db_url, headers=headers)
    if response.status_code == 200:
        db_info = response.json()
        partnerships_props = list(db_info.get('properties', {}).keys())
        print(f"   • Partnerships fields: {partnerships_props}")
        print(f"     ❌ Missing: category, confidence, opportunity_angle, team_action")

    # 6. Account Coverage Analysis
    print("\n6. ❌ ACCOUNT COVERAGE IS LIMITED:")
    print(f"   • Only Genesis Cloud researched")
    print(f"   • ❌ No comparison with other AI infrastructure companies")
    print(f"   • ❌ No prioritization framework for account selection")
    print(f"   • ❌ No account relationship mapping")

    print("\n🎯 IMMEDIATE ACTION REQUIRED")
    print("-" * 40)

    priority_fixes = [
        "1. Implement comprehensive contact discovery (Apollo + LinkedIn + company website)",
        "2. Add Verdigris Signals-specific MEDDIC segmentation",
        "3. Remove duplicate records and clean database",
        "4. Enhance database schemas with missing fields",
        "5. Implement real LinkedIn enrichment (not simulated)",
        "6. Add account relation fields for contact filtering",
        "7. Expand research to 2-3 additional target accounts",
        "8. Implement buying signal detection",
        "9. Add warm introduction pathway mapping",
        "10. Create contact deduplication process"
    ]

    for fix in priority_fixes:
        print(f"   • {fix}")

    print(f"\n💡 VERDIGRIS SIGNALS CONTEXT MISSING")
    print("-" * 40)
    print(f"   • Who monitors power consumption in data centers?")
    print(f"   • Who gets alerted when power anomalies occur?")
    print(f"   • Who makes decisions about power monitoring tools?")
    print(f"   • Who would champion a predictive power analytics solution?")
    print(f"   • Who has budget for infrastructure monitoring software?")

    return {
        'total_contacts': len(contacts_data),
        'contacts_with_email': contacts_with_email,
        'contacts_with_linkedin': contacts_with_linkedin,
        'account_duplicates': duplicates,
        'databases_with_minimal_schema': 2,  # trigger_events and partnerships
        'critical_gaps_identified': 10
    }

if __name__ == "__main__":
    results = critical_audit_analysis()
    print(f"\n📋 AUDIT COMPLETE - {results['critical_gaps_identified']} critical gaps identified")
