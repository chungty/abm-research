#!/usr/bin/env python3
"""
Test Fixed ABM Account Save Status

Tests ABM system using the correct field name for save status.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.core.abm_system import ComprehensiveABMSystem
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_fixed_abm_saves():
    """Test ABM saves using correct notion_persistence field"""

    print("🔍 Testing Fixed ABM Account Save Status")
    print("=" * 50)

    # Initialize ABM system
    abm_system = ComprehensiveABMSystem()

    # Test with a simple company
    print("🧪 Running ABM research for save status test...")

    try:
        result = abm_system.conduct_complete_account_research('Fixed Test Company', 'fixedtest.com')

        print("📊 ABM Research Results:")
        print(f"   ✅ Research completed: {result.get('success', False)}")

        # Check the CORRECT field name
        notion_persistence = result.get('notion_persistence', {})
        print(f"   📋 Notion persistence data: {notion_persistence}")

        if notion_persistence:
            account_saved = notion_persistence.get('account_saved', False)
            contacts_saved = notion_persistence.get('contacts_saved', 0)
            events_saved = notion_persistence.get('events_saved', 0)

            print(f"   🏢 Account saved: {account_saved} ({'✅ SUCCESS' if account_saved else '❌ FAILED'})")
            print(f"   👥 Contacts saved: {contacts_saved}")
            print(f"   🎯 Events saved: {events_saved}")

            if account_saved:
                print("\n🎉 ISSUE RESOLVED!")
                print("✅ ABM account saves are working correctly")
                print("✅ The problem was using wrong field name 'saved_to_notion' instead of 'notion_persistence'")
                return True
            else:
                print("\n⚠️  Account save still reporting False")
                return False
        else:
            print("   ❌ No notion_persistence data found")
            return False

    except Exception as e:
        print(f"   ❌ ABM research failed: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_abm_saves()
    exit(0 if success else 1)
