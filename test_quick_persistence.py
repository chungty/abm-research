#!/usr/bin/env python3
"""Quick test of fixed Notion persistence"""

import sys
sys.path.append('/Users/chungty/Projects/vdg-clean/abm-research')

from notion_persistence_manager import notion_persistence_manager

def test_fixed_persistence():
    print("🔧 Testing Fixed Notion Persistence")

    # Create test contact
    test_contact = {
        'name': 'Test User Fixed',
        'title': 'VP of Infrastructure',
        'company': 'TestCorp',
        'email': 'test@testcorp.com',
        'linkedin_url': 'https://linkedin.com/in/test-user-fixed',
        'final_lead_score': 85.5,
        'icp_fit_score': 80,
        'buying_power_score': 90,
        'engagement_potential_score': 85,
        'content_themes': ['Power optimization', 'Infrastructure management'],
        'responsibility_keywords': ['power', 'reliability'],
        'connection_pathways': 'No direct connections - cold outreach required',
        'research_status': 'Analyzed'
    }

    try:
        result = notion_persistence_manager.save_enriched_contacts([test_contact], "TestCorp")

        success = result.get('Test User Fixed', False)
        if success:
            print("✅ SUCCESS: Contact saved to Notion!")
            print(f"   📋 Used API key: {notion_persistence_manager.notion_api_key[:20]}...")
            print(f"   📊 Contact: {test_contact['name']} (Score: {test_contact['final_lead_score']})")
            return True
        else:
            print("❌ FAILED: Contact not saved")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_persistence()
    print(f"\n{'✅ FIXED' if success else '❌ STILL BROKEN'}")