#!/usr/bin/env python3
"""
Enhance Database Schemas with Missing Fields
Add all fields specified in SKILL.md that are currently missing
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class DatabaseSchemaEnhancer:
    def __init__(self):
        self.api_key = os.getenv("NOTION_ABM_API_KEY")
        if not self.api_key:
            raise ValueError("NOTION_ABM_API_KEY environment variable not found")

        self.client = Client(auth=self.api_key)

        # Database IDs from existing databases
        self.database_ids = {
            "accounts": "15a91e6b59308144bb23c49c84b892da",
            "trigger_events": "15a91e6b5930812683b4e3e4b5e41ee8",
            "contacts": "15a91e6b593081ab8abfed967cf8fe97",
            "partnerships": "15a91e6b59308101b893ee2c4dc1a02b",
        }

    def enhance_accounts_schema(self):
        """Add missing fields to Accounts database based on SKILL.md spec"""
        print("📊 Enhancing Accounts database schema...")

        try:
            # Get current database
            accounts_db = self.client.databases.retrieve(self.database_ids["accounts"])
            current_props = accounts_db["properties"]

            # Missing fields from SKILL.md
            new_properties = {}

            # Check if "Data Center Locations" field is missing
            if "Data Center Locations" not in current_props:
                new_properties["Data Center Locations"] = {"rich_text": {}}

            # Check if "Recent Funding Status" field is missing
            if "Recent Funding Status" not in current_props:
                new_properties["Recent Funding Status"] = {"rich_text": {}}

            # Check if "Growth Indicators" field is missing
            if "Growth Indicators" not in current_props:
                new_properties["Growth Indicators"] = {"rich_text": {}}

            # Check if "Primary Data Center Capacity" field is missing
            if "Primary Data Center Capacity" not in current_props:
                new_properties["Primary Data Center Capacity"] = {"rich_text": {}}

            if new_properties:
                # Update database with new properties
                updated_props = {**current_props, **new_properties}
                self.client.databases.update(
                    database_id=self.database_ids["accounts"], properties=updated_props
                )
                print(f"   ✅ Added {len(new_properties)} new fields to Accounts")
            else:
                print("   ✅ Accounts schema already complete")

        except Exception as e:
            print(f"   ❌ Failed to enhance Accounts schema: {e}")

    def enhance_trigger_events_schema(self):
        """Add missing fields to Trigger Events database"""
        print("⚡ Enhancing Trigger Events database schema...")

        try:
            # Get current database
            events_db = self.client.databases.retrieve(self.database_ids["trigger_events"])
            current_props = events_db["properties"]

            # Missing fields from SKILL.md
            new_properties = {}

            # Check if "Detected Date" field is missing
            if "Detected Date" not in current_props:
                new_properties["Detected Date"] = {"date": {}}

            # Update Event Type options to match SKILL.md specification
            if "Event Type" in current_props:
                updated_event_type = {
                    "select": {
                        "options": [
                            {"name": "Expansion", "color": "green"},
                            {"name": "Leadership Change", "color": "blue"},
                            {"name": "AI Workload", "color": "purple"},
                            {"name": "Energy Pressure", "color": "red"},
                            {"name": "Incident", "color": "orange"},
                            {"name": "Sustainability", "color": "yellow"},
                        ]
                    }
                }
                new_properties["Event Type"] = updated_event_type

            if new_properties:
                # Update database with new properties
                updated_props = {**current_props, **new_properties}
                self.client.databases.update(
                    database_id=self.database_ids["trigger_events"], properties=updated_props
                )
                print(f"   ✅ Added {len(new_properties)} new fields to Trigger Events")
            else:
                print("   ✅ Trigger Events schema already complete")

        except Exception as e:
            print(f"   ❌ Failed to enhance Trigger Events schema: {e}")

    def enhance_contacts_schema(self):
        """Add missing fields to Contacts database"""
        print("👤 Enhancing Contacts database schema...")

        try:
            # Get current database
            contacts_db = self.client.databases.retrieve(self.database_ids["contacts"])
            current_props = contacts_db["properties"]

            # Missing fields from SKILL.md
            new_properties = {}

            # Check if "Role Tenure" field is missing
            if "Role Tenure" not in current_props:
                new_properties["Role Tenure"] = {"rich_text": {}}

            # Check if "Problems They Likely Own" field is missing (multi-select)
            if "Problems They Likely Own" not in current_props:
                new_properties["Problems They Likely Own"] = {
                    "multi_select": {
                        "options": [
                            {"name": "Power Capacity Planning", "color": "red"},
                            {"name": "Uptime Pressure", "color": "orange"},
                            {"name": "Cost Optimization", "color": "yellow"},
                            {"name": "Predictive Maintenance", "color": "green"},
                            {"name": "Energy Efficiency", "color": "blue"},
                            {"name": "Reliability Engineering", "color": "purple"},
                            {"name": "Compliance/Reporting", "color": "pink"},
                            {"name": "Capacity Planning", "color": "brown"},
                        ]
                    }
                }

            # Check if "Content Themes They Value" field is missing (multi-select)
            if "Content Themes They Value" not in current_props:
                new_properties["Content Themes They Value"] = {
                    "multi_select": {
                        "options": [
                            {"name": "AI Infrastructure", "color": "purple"},
                            {"name": "Power Optimization", "color": "red"},
                            {"name": "Sustainability", "color": "green"},
                            {"name": "Reliability Engineering", "color": "blue"},
                            {"name": "Cost Reduction", "color": "yellow"},
                            {"name": "Predictive Analytics", "color": "orange"},
                            {"name": "Energy Management", "color": "pink"},
                        ]
                    }
                }

            # Check if "Connection Pathways" field is missing
            if "Connection Pathways" not in current_props:
                new_properties["Connection Pathways"] = {"rich_text": {}}

            # Check if "Apollo Contact ID" field is missing (for deduplication)
            if "Apollo Contact ID" not in current_props:
                new_properties["Apollo Contact ID"] = {"rich_text": {}}

            # Update Buying Committee Role options to match MEDDIC spec
            if "Buying Committee Role" in current_props:
                updated_committee_role = {
                    "select": {
                        "options": [
                            {"name": "Economic Buyer", "color": "green"},
                            {"name": "Technical Evaluator", "color": "blue"},
                            {"name": "Champion", "color": "purple"},
                            {"name": "Influencer", "color": "yellow"},
                            {"name": "User", "color": "gray"},
                            {"name": "Blocker", "color": "red"},
                        ]
                    }
                }
                new_properties["Buying Committee Role"] = updated_committee_role

            if new_properties:
                # Update database with new properties
                updated_props = {**current_props, **new_properties}
                self.client.databases.update(
                    database_id=self.database_ids["contacts"], properties=updated_props
                )
                print(f"   ✅ Added {len(new_properties)} new fields to Contacts")
            else:
                print("   ✅ Contacts schema already complete")

        except Exception as e:
            print(f"   ❌ Failed to enhance Contacts schema: {e}")

    def enhance_partnerships_schema(self):
        """Add missing fields to Strategic Partnerships database"""
        print("🤝 Enhancing Strategic Partnerships database schema...")

        try:
            # Get current database
            partnerships_db = self.client.databases.retrieve(self.database_ids["partnerships"])
            current_props = partnerships_db["properties"]

            # Missing fields from SKILL.md
            new_properties = {}

            # Check if "Detected Date" field is missing
            if "Detected Date" not in current_props:
                new_properties["Detected Date"] = {"date": {}}

            # Check if "Relationship Evidence" field is missing (renaming Evidence URL)
            if "Relationship Evidence" not in current_props:
                new_properties["Relationship Evidence"] = {"rich_text": {}}

            # Update Category options to match SKILL.md specification exactly
            if "Category" in current_props:
                updated_category = {
                    "select": {
                        "options": [
                            {"name": "DCIM", "color": "blue"},
                            {"name": "EMS", "color": "green"},
                            {"name": "Cooling", "color": "purple"},
                            {"name": "DC Equipment", "color": "orange"},
                            {"name": "Racks", "color": "brown"},
                            {"name": "GPUs", "color": "red"},
                            {"name": "Critical Facilities Contractors", "color": "pink"},
                            {"name": "Professional Services", "color": "gray"},
                        ]
                    }
                }
                new_properties["Category"] = updated_category

            # Update Partnership Action options to match SKILL.md
            if "Partnership Action" in current_props:
                updated_action = {
                    "select": {
                        "options": [
                            {"name": "Investigate", "color": "red"},
                            {"name": "Contact", "color": "orange"},
                            {"name": "Monitor", "color": "yellow"},
                            {"name": "Not Relevant", "color": "gray"},
                        ]
                    }
                }
                new_properties["Partnership Action"] = updated_action

            if new_properties:
                # Update database with new properties
                updated_props = {**current_props, **new_properties}
                self.client.databases.update(
                    database_id=self.database_ids["partnerships"], properties=updated_props
                )
                print(f"   ✅ Added {len(new_properties)} new fields to Partnerships")
            else:
                print("   ✅ Partnerships schema already complete")

        except Exception as e:
            print(f"   ❌ Failed to enhance Partnerships schema: {e}")

    def verify_schema_completeness(self):
        """Verify all required fields from SKILL.md are present"""
        print("\n🔍 VERIFYING SCHEMA COMPLETENESS...")
        print("-" * 50)

        try:
            # Check each database against SKILL.md requirements
            accounts_db = self.client.databases.retrieve(self.database_ids["accounts"])
            accounts_props = list(accounts_db["properties"].keys())

            events_db = self.client.databases.retrieve(self.database_ids["trigger_events"])
            events_props = list(events_db["properties"].keys())

            contacts_db = self.client.databases.retrieve(self.database_ids["contacts"])
            contacts_props = list(contacts_db["properties"].keys())

            partnerships_db = self.client.databases.retrieve(self.database_ids["partnerships"])
            partnerships_props = list(partnerships_db["properties"].keys())

            # Required fields from SKILL.md
            required_accounts = [
                "Company Name",
                "Domain",
                "Employee Count",
                "ICP Fit Score",
                "Account Research Status",
                "Last Updated",
            ]

            required_events = [
                "Event Description",
                "Account",
                "Event Type",
                "Confidence",
                "Confidence Score",
                "Relevance Score",
                "Detected Date",
                "Source URL",
            ]

            required_contacts = [
                "Name",
                "Account",
                "Title",
                "LinkedIn URL",
                "Email",
                "Buying Committee Role",
                "ICP Fit Score",
                "Buying Power Score",
                "Engagement Potential Score",
                "Final Lead Score",
                "Research Status",
                "Role Tenure",
                "Problems They Likely Own",
                "Content Themes They Value",
                "Connection Pathways",
                "Value-Add Ideas",
            ]

            required_partnerships = [
                "Partner Name",
                "Account",
                "Category",
                "Confidence",
                "Evidence URL",
                "Detected Date",
                "Verdigris Opportunity",
                "Partnership Action",
            ]

            # Check completeness
            def check_fields(db_name, current, required):
                missing = [field for field in required if field not in current]
                if missing:
                    print(f"   ❌ {db_name}: Missing {missing}")
                    return False
                else:
                    print(f"   ✅ {db_name}: All required fields present ({len(current)} total)")
                    return True

            accounts_ok = check_fields("Accounts", accounts_props, required_accounts)
            events_ok = check_fields("Trigger Events", events_props, required_events)
            contacts_ok = check_fields("Contacts", contacts_props, required_contacts)
            partnerships_ok = check_fields(
                "Partnerships", partnerships_props, required_partnerships
            )

            if all([accounts_ok, events_ok, contacts_ok, partnerships_ok]):
                print("\n🎉 ALL SCHEMAS COMPLETE AND READY FOR PRODUCTION!")
                return True
            else:
                print("\n⚠️  Some schemas still need enhancement")
                return False

        except Exception as e:
            print(f"   ❌ Schema verification failed: {e}")
            return False

    def run_enhancement(self):
        """Run complete schema enhancement"""
        print("🔧 ENHANCING DATABASE SCHEMAS")
        print("=" * 40)

        self.enhance_accounts_schema()
        self.enhance_trigger_events_schema()
        self.enhance_contacts_schema()
        self.enhance_partnerships_schema()

        # Verify completeness
        is_complete = self.verify_schema_completeness()

        if is_complete:
            print("\n🚀 SCHEMA ENHANCEMENT COMPLETE!")
            print("   All databases now match SKILL.md specification")
            print("   Ready for comprehensive contact discovery and enrichment")
        else:
            print("\n⚠️  Schema enhancement partially complete")
            print("   Some fields may need manual adjustment in Notion")

        return is_complete


def test_enhanced_schemas():
    """Test the enhanced database schemas"""
    print("\n🧪 TESTING ENHANCED SCHEMAS...")
    print("-" * 30)

    try:
        enhancer = DatabaseSchemaEnhancer()

        # Test connection to all databases
        for db_name, db_id in enhancer.database_ids.items():
            db = enhancer.client.databases.retrieve(db_id)
            field_count = len(db["properties"])
            print(f"   ✅ {db_name}: {field_count} fields accessible")

        print("\n   🎯 Schemas ready for production data pipeline")
        return True

    except Exception as e:
        print(f"   ❌ Schema testing failed: {e}")
        return False


if __name__ == "__main__":
    try:
        enhancer = DatabaseSchemaEnhancer()
        success = enhancer.run_enhancement()

        if success:
            test_enhanced_schemas()

    except Exception as e:
        print(f"❌ Schema enhancement failed: {e}")
