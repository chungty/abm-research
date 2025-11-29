#!/usr/bin/env python3
"""
Add Enhanced Intelligence Fields to Existing Databases

Phase 1A: Add new fields (safe, non-breaking changes)
This script adds all the enhanced intelligence fields from the approved plan.
"""

import os
import sys
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.integrations.notion_client import NotionClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def add_enhanced_fields():
    """Add enhanced intelligence fields to all databases"""

    print("🚀 ADDING ENHANCED INTELLIGENCE FIELDS")
    print("=" * 60)
    print("Phase 1A: Safe field additions (non-breaking changes)")
    print()

    client = NotionClient()

    # Define all new fields to add
    database_enhancements = {
        'accounts': {
            'name': 'ABM Accounts',
            'new_fields': {
                # Enhanced Intelligence Fields from NotionClient schema
                "Recent Leadership Changes": {"rich_text": {}},
                "Key Decision Makers": {"rich_text": {}},
                "Recent Funding": {"rich_text": {}},
                "Growth Stage": {"select": {"options": [
                    {"name": "Startup", "color": "green"},
                    {"name": "Scale-Up", "color": "blue"},
                    {"name": "Growth", "color": "purple"},
                    {"name": "Mature", "color": "orange"},
                    {"name": "Enterprise", "color": "red"}
                ]}},
                "Hiring Velocity": {"rich_text": {}},
                "Physical Infrastructure": {"rich_text": {}},
                "Competitor Tools": {"rich_text": {}},
                "Recent Announcements": {"rich_text": {}},
                "Conversation Triggers": {"rich_text": {}},
                "Notes": {"rich_text": {}}
            }
        },

        'contacts': {
            'name': 'ABM Contacts',
            'new_fields': {
                # Data Provenance & Quality Fields
                "Name Source": {"select": {"options": [
                    {"name": "apollo", "color": "blue"},
                    {"name": "linkedin", "color": "green"},
                    {"name": "merged", "color": "purple"},
                    {"name": "manual", "color": "gray"}
                ]}},
                "Email Source": {"select": {"options": [
                    {"name": "apollo", "color": "blue"},
                    {"name": "linkedin", "color": "green"},
                    {"name": "inferred", "color": "yellow"},
                    {"name": "manual", "color": "gray"}
                ]}},
                "Title Source": {"select": {"options": [
                    {"name": "apollo", "color": "blue"},
                    {"name": "linkedin", "color": "green"},
                    {"name": "merged", "color": "purple"},
                    {"name": "manual", "color": "gray"}
                ]}},
                "Data Quality Score": {"number": {"format": "number"}},
                "Last Enriched": {"date": {}},
                "Lead Score": {"number": {"format": "number"}},
                "Engagement Level": {"select": {"options": [
                    {"name": "Very High", "color": "red"},
                    {"name": "High", "color": "orange"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]}},
                "Contact Date": {"date": {}},
                "LinkedIn URL": {"url": {}},
                "Notes": {"rich_text": {}}
            }
        },

        'trigger_events': {
            'name': 'ABM Trigger Events',
            'new_fields': {
                # Multi-Dimensional Scoring System
                "Business Impact Score": {"number": {"format": "number"}},
                "Actionability Score": {"number": {"format": "number"}},
                "Timing Urgency Score": {"number": {"format": "number"}},
                "Strategic Fit Score": {"number": {"format": "number"}},

                # Time Intelligence Fields
                "Action Deadline": {"date": {}},
                "Peak Relevance Window": {"date": {}},
                "Decay Rate": {"select": {"options": [
                    {"name": "Fast", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Slow", "color": "blue"},
                    {"name": "Permanent", "color": "green"}
                ]}},

                # Event Lifecycle Tracking
                "Event Stage": {"select": {"options": [
                    {"name": "Rumored", "color": "gray"},
                    {"name": "Announced", "color": "yellow"},
                    {"name": "In-Progress", "color": "blue"},
                    {"name": "Completed", "color": "green"}
                ]}},
                "Follow-up Actions": {"rich_text": {}},
                "Urgency Level": {"select": {"options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]}}
            }
        },

        'partnerships': {
            'name': 'ABM Strategic Partnerships',
            'new_fields': {
                # Partnership Depth & Strategy
                "Relationship Depth": {"select": {"options": [
                    {"name": "Surface Integration", "color": "gray"},
                    {"name": "Go-to-Market Alliance", "color": "blue"},
                    {"name": "Strategic Investment", "color": "green"},
                    {"name": "Ecosystem Play", "color": "purple"}
                ]}},

                # Entry Vector Intelligence
                "Warm Introduction Path": {"rich_text": {}},
                "Common Partners": {"rich_text": {}},
                "Competitive Overlap": {"select": {"options": [
                    {"name": "None", "color": "green"},
                    {"name": "Some", "color": "yellow"},
                    {"name": "High", "color": "red"}
                ]}},
                "Partnership Maturity": {"select": {"options": [
                    {"name": "Basic", "color": "gray"},
                    {"name": "Intermediate", "color": "blue"},
                    {"name": "Sophisticated", "color": "green"}
                ]}},

                # Action Intelligence
                "Best Approach": {"select": {"options": [
                    {"name": "Technical Discussion", "color": "blue"},
                    {"name": "Business Development", "color": "green"},
                    {"name": "Channel Partnership", "color": "purple"}
                ]}},
                "Decision Timeline": {"select": {"options": [
                    {"name": "Fast (weeks)", "color": "red"},
                    {"name": "Medium (months)", "color": "yellow"},
                    {"name": "Slow (quarters)", "color": "gray"}
                ]}},
                "Success Metrics": {"rich_text": {}},
                "Recommended Next Steps": {"rich_text": {}}
            }
        }
    }

    # Process each database
    for db_key, enhancement in database_enhancements.items():
        db_id = client.database_ids.get(db_key)
        if not db_id:
            print(f"❌ {enhancement['name']}: No database ID configured")
            continue

        print(f"\n📊 {enhancement['name'].upper()}")
        print(f"   ID: {db_id}")

        # Get current schema
        try:
            response = client._make_request('GET', f"https://api.notion.com/v1/databases/{db_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get schema: {response.status_code}")
                continue

            current_properties = response.json().get('properties', {})
            current_fields = set(current_properties.keys())

            # Determine which fields need to be added
            new_fields = enhancement['new_fields']
            needed_fields = []
            existing_fields = []

            for field_name in new_fields.keys():
                if field_name in current_fields:
                    existing_fields.append(field_name)
                else:
                    needed_fields.append(field_name)

            print(f"   📋 Current fields: {len(current_fields)}")
            print(f"   ✅ Already exist: {len(existing_fields)}")
            print(f"   ➕ Need to add: {len(needed_fields)}")

            if existing_fields:
                print(f"   🔄 Existing enhanced fields:")
                for field in existing_fields[:3]:  # Show first 3
                    print(f"      • {field}")
                if len(existing_fields) > 3:
                    print(f"      • ... and {len(existing_fields) - 3} more")

            if needed_fields:
                print(f"   🆕 Fields to add:")
                for field in needed_fields:
                    field_type = list(new_fields[field].keys())[0]
                    print(f"      • '{field}' ({field_type})")

                # Try to add fields (this may not work due to API permissions)
                print(f"   🧪 Attempting to add {len(needed_fields)} fields via API...")

                success_count = 0
                for field_name in needed_fields:
                    field_config = new_fields[field_name]

                    # Attempt to add field via API
                    update_data = {
                        "properties": {
                            field_name: field_config
                        }
                    }

                    try:
                        update_response = client._make_request(
                            'PATCH',
                            f"https://api.notion.com/v1/databases/{db_id}",
                            json=update_data
                        )

                        if update_response.status_code == 200:
                            print(f"      ✅ Added '{field_name}'")
                            success_count += 1
                        else:
                            print(f"      ❌ Failed to add '{field_name}': {update_response.status_code}")
                            # Don't show full error to avoid spam

                    except Exception as e:
                        print(f"      ❌ Exception adding '{field_name}': {str(e)[:50]}...")

                print(f"   📊 Successfully added: {success_count}/{len(needed_fields)} fields")

                if success_count < len(needed_fields):
                    print(f"   ⚠️  Manual addition needed for remaining fields")
                    print(f"   💡 Use Notion interface to add missing fields with exact names/types shown above")
            else:
                print(f"   🎉 All enhanced fields already exist!")

        except Exception as e:
            print(f"   ❌ Error processing {enhancement['name']}: {e}")

    print(f"\n🏁 PHASE 1A COMPLETE")
    print(f"   Next: Phase 1B will rename fields to match intended schema")
    print(f"   Then: Phase 2 will update code to use new field names")

if __name__ == "__main__":
    add_enhanced_fields()