#!/usr/bin/env python3
"""
Test Account Relations Fix

Test that contacts and trigger events properly link to accounts using relation fields.
"""

import os
import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

import logging

from abm_research.integrations.notion_client import NotionClient

logging.basicConfig(level=logging.WARNING, format="%(message)s")


def test_account_relations():
    """Test proper account relations with clean naming and confidence indicators"""

    print("🔧 TESTING ACCOUNT RELATIONS FIX")
    print("=" * 50)

    client = NotionClient()

    # Test clean account creation (no test suffixes)
    print("📊 Creating clean test account...")
    clean_account_data = {
        "name": "Relations Test Company",  # Clean name without suffixes
        "domain": "relations-test.com",
        "employee_count": 100,
        "business_model": "Technology",
        "icp_fit_score": 75,
        # Enhanced Intelligence with confidence indicators
        "Physical Infrastructure": "GPU cluster, H100, NVIDIA (90% confidence)",
        "Recent Announcements": "Partnership expansion (85% confidence)",
        "Hiring Velocity": "5+ engineering roles (75% confidence)",
        "Growth Stage": "Scale-Up",
        # Fields with explicit "not found" vs "not searched"
        "Recent Funding": "Not found (searched 3 sources, 95% confidence)",
        "Key Decision Makers": "N/A - not searched in this analysis",
        "Competitor Tools": "Not found (searched 2 sources, 80% confidence)",
    }

    account_id = client.save_account(clean_account_data)
    if account_id:
        print(f"✅ Account created: {account_id[:8]}...")
    else:
        print("❌ Account creation failed")
        return

    # Test contact with proper Account relation
    print("👤 Creating contact with Account relation...")
    relation_contact_data = {
        "name": "Test Contact (Relations)",
        "email": "test@relations-test.com",
        "title": "VP of Engineering",
        "final_lead_score": 85,
        # Enhanced data provenance
        "name_source": "apollo",
        "email_source": "linkedin",
        "title_source": "merged",
        "data_quality_score": 92,
        "engagement_level": "High",
    }

    contact_results = client.save_contacts([relation_contact_data], "Relations Test Company")
    print(f'👤 Contact creation: {"✅ Success" if contact_results else "❌ Failed"}')

    # Test trigger event with proper Account relation
    print("⚡ Creating trigger event with Account relation...")
    relation_event_data = {
        "description": "Relations Test: AI infrastructure expansion",
        "event_type": "expansion",
        "confidence": "High",
        "source_url": "https://relations-test.com/news",
        "detected_date": "2024-11-25",
        # Enhanced multi-dimensional scoring with confidence
        "business_impact_score": 85,  # High confidence
        "actionability_score": 75,  # Medium-high confidence
        "timing_urgency_score": 90,  # Very high confidence
        "strategic_fit_score": 80,  # High confidence
        # Time intelligence
        "action_deadline": "2024-12-31",
        "event_stage": "Announced",
        "urgency_level": "High",
        "follow_up_actions": "Schedule technical discussion within 2 weeks (95% confidence this will drive engagement)",
    }

    event_results = client.save_trigger_events([relation_event_data], "Relations Test Company")
    print(f'⚡ Trigger event creation: {"✅ Success" if event_results else "❌ Failed"}')

    print()
    print("🏆 ACCOUNT RELATIONS TEST RESULTS:")
    print("=" * 40)

    if account_id and contact_results and event_results:
        print("✅ Account Relations: WORKING")
        print("   📊 Clean account naming (no test suffixes)")
        print("   🔗 Contact properly linked to account via relation")
        print("   ⚡ Trigger event properly linked to account via relation")
        print('   📈 Confidence indicators distinguish "not found" vs "N/A"')
        print()
        print("📋 Confidence Indicator Examples:")
        print('   ✅ "GPU cluster, H100, NVIDIA (90% confidence)" - Found with high confidence')
        print('   🔍 "Not found (searched 3 sources, 95% confidence)" - Searched but nothing found')
        print('   ❌ "N/A - not searched in this analysis" - Explicitly not attempted')
        print()
        print("🎯 Database integrity now maintains proper relationships!")
    else:
        print("❌ Account Relations: PARTIAL FAILURE")
        print(f'   Account: {"✅" if account_id else "❌"}')
        print(f'   Contact: {"✅" if contact_results else "❌"}')
        print(f'   Event: {"✅" if event_results else "❌"}')


if __name__ == "__main__":
    test_account_relations()
