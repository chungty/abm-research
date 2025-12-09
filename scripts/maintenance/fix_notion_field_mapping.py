#!/usr/bin/env python3
"""
Fix Notion Field Mapping

Updates NotionClient to use the correct field names that actually exist in the databases.
"""

import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

# Get the actual field mappings from database schema
CORRECT_FIELD_MAPPINGS = {
    'accounts': {
        # Code expects → Actual field name
        'Company Name': 'Name',  # title field
        'Industry': 'Business Model',  # select field
        'Research Status': 'Account Research Status',  # select field
        # Enhanced intelligence fields don't exist yet - we'll add them as rich_text
    },
    'contacts': {
        # Code expects → Actual field name
        'Company': 'Account',  # This should be a relation, not rich_text
        'Lead Score': 'Final Lead Score',  # This is a formula field, can't write to it
        # Will need to use ICP Fit Score instead
    },
    'trigger_events': {
        'Event Description': 'Name',  # title field
        'Company': 'Account',  # This should be a relation, not rich_text
    },
    'partnerships': {
        # This database uses different field names
        'Partner Name': 'Name',  # title field
        'Partnership Type': 'Category',  # select field
        'Context': 'Relationship Evidence',  # rich_text field
        'Relevance Score': 'Priority Score',  # number field
        'Source URL': 'Evidence URL',  # url field
        'Discovered Date': 'Detected Date',  # date field
    }
}

def create_field_mapping_fix():
    """Create the fixes needed for NotionClient field mappings"""

    print("🔧 NOTION FIELD MAPPING FIXES")
    print("=" * 50)
    print("Based on actual database schema, here are the required fixes:")
    print()

    print("📊 ACCOUNTS DATABASE FIXES:")
    print(f"   ❌ 'Company Name' → ✅ 'Name' (title)")
    print(f"   ❌ 'Industry' → ✅ 'Business Model' (select)")
    print(f"   ❌ 'Research Status' → ✅ 'Account Research Status' (select)")
    print(f"   ❌ Enhanced intelligence fields → Need to be added or mapped to existing")
    print()

    print("👤 CONTACTS DATABASE FIXES:")
    print(f"   ❌ 'Company' (rich_text) → ✅ 'Account' (relation)")
    print(f"   ❌ 'Lead Score' (number) → ✅ Use 'ICP Fit Score' (Final Lead Score is formula)")
    print(f"   ❌ 'Engagement Level' → Doesn't exist, skip or add")
    print(f"   ❌ 'Contact Date' → Doesn't exist, use 'Created At'")
    print()

    print("⚡ TRIGGER EVENTS DATABASE FIXES:")
    print(f"   ❌ 'Event Description' → ✅ 'Name' (title)")
    print(f"   ❌ 'Company' (rich_text) → ✅ 'Account' (relation)")
    print(f"   ❌ 'Urgency' → Doesn't exist, skip")
    print()

    print("🤝 PARTNERSHIPS DATABASE FIXES:")
    print(f"   ❌ 'Partner Name' → ✅ 'Name' (title)")
    print(f"   ❌ 'Partnership Type' → ✅ 'Category' (select)")
    print(f"   ❌ 'Context' → ✅ 'Relationship Evidence' (rich_text)")
    print(f"   ❌ 'Relevance Score' → ✅ 'Priority Score' (number)")
    print(f"   ❌ 'Source URL' → ✅ 'Evidence URL' (url)")
    print(f"   ❌ 'Discovered Date' → ✅ 'Detected Date' (date)")
    print()

    print("🔗 CRITICAL: Relations Fix Needed")
    print("   • Contacts and Trigger Events should link to Accounts via 'Account' relation")
    print("   • Not using rich_text fields for company names")
    print("   • This will enable proper database relationships")
    print()

    print("📋 IMPLEMENTATION PLAN:")
    print("   1. Update _create_account() method field names")
    print("   2. Update _create_contact() to use Account relation")
    print("   3. Update _create_trigger_event() to use Account relation")
    print("   4. Update _create_partnership() field names")
    print("   5. Add enhanced intelligence fields to accounts database")
    print("   6. Test with Groq to verify fixes")

if __name__ == "__main__":
    create_field_mapping_fix()
