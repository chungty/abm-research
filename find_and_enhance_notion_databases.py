#!/usr/bin/env python3
"""
Find and Enhance Existing Notion Databases
Look for existing ABM databases and enhance them with the improved schema
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime
from abm_config import config

def find_existing_databases():
    """Search for existing ABM-related databases"""

    client = config.get_notion_client()

    print("🔍 SEARCHING FOR EXISTING ABM DATABASES...")
    print("-" * 50)

    try:
        # Search for databases
        search_results = client.search(
            query="ABM",
            filter={"property": "object", "value": "database"}
        )

        databases_found = []

        for result in search_results.get('results', []):
            if result['object'] == 'database':
                title = ''
                if result.get('title'):
                    title = ''.join([text['plain_text'] for text in result['title']])

                databases_found.append({
                    'id': result['id'],
                    'title': title,
                    'url': result['url'],
                    'created_time': result['created_time'],
                    'properties': list(result.get('properties', {}).keys())
                })

                print(f"📊 Found database: {title}")
                print(f"   ID: {result['id']}")
                print(f"   Properties: {len(result.get('properties', {}))} fields")
                print(f"   Created: {result['created_time'][:10]}")

        # Also search for more general terms
        for search_term in ['Account', 'Contact', 'Trigger', 'Partnership']:
            search_results = client.search(
                query=search_term,
                filter={"property": "object", "value": "database"}
            )

            for result in search_results.get('results', []):
                if result['object'] == 'database':
                    db_id = result['id']
                    # Avoid duplicates
                    if not any(db['id'] == db_id for db in databases_found):
                        title = ''
                        if result.get('title'):
                            title = ''.join([text['plain_text'] for text in result['title']])

                        if any(keyword in title.lower() for keyword in ['account', 'contact', 'trigger', 'partnership', 'abm']):
                            databases_found.append({
                                'id': result['id'],
                                'title': title,
                                'url': result['url'],
                                'created_time': result['created_time'],
                                'properties': list(result.get('properties', {}).keys())
                            })

                            print(f"📊 Found related database: {title}")

        print(f"\n📋 SUMMARY: Found {len(databases_found)} potentially relevant databases")
        return databases_found

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

def analyze_database_schema(database_id: str, title: str):
    """Analyze existing database schema and identify missing fields"""

    client = config.get_notion_client()

    print(f"\n🔍 ANALYZING DATABASE SCHEMA: {title}")
    print("-" * 40)

    try:
        database = client.databases.retrieve(database_id)
        current_props = database['properties']

        print(f"📊 Current Properties ({len(current_props)}):")
        for prop_name, prop_config in current_props.items():
            prop_type = prop_config['type']
            print(f"   • {prop_name} ({prop_type})")

        # Determine database type and missing fields
        missing_fields = []
        database_type = None

        # Check if it's an Accounts database
        if any(field.lower() in ['company', 'account', 'domain'] for field in current_props.keys()):
            database_type = 'accounts'
            required_fields = {
                'Company Name': {'type': 'title'},
                'Domain': {'type': 'rich_text'},
                'Employee Count': {'type': 'number'},
                'ICP Fit Score': {'type': 'number'},
                'Account Research Status': {'type': 'select'},
                'Business Model': {'type': 'select'},
                'Data Center Locations': {'type': 'rich_text'},
                'Primary Data Center Capacity': {'type': 'rich_text'},
                'Recent Funding Status': {'type': 'rich_text'},
                'Growth Indicators': {'type': 'rich_text'},
                'Last Updated': {'type': 'date'},
                'Created At': {'type': 'created_time'}
            }

        # Check if it's a Contacts database
        elif any(field.lower() in ['name', 'contact', 'title', 'email'] for field in current_props.keys()):
            database_type = 'contacts'
            required_fields = {
                'Name': {'type': 'title'},
                'Account': {'type': 'relation'},
                'Title': {'type': 'rich_text'},
                'LinkedIn URL': {'type': 'url'},
                'Email': {'type': 'email'},
                'Buying Committee Role': {'type': 'select'},
                'ICP Fit Score': {'type': 'number'},
                'Buying Power Score': {'type': 'number'},
                'Engagement Potential Score': {'type': 'number'},
                'Final Lead Score': {'type': 'formula'},
                'Research Status': {'type': 'select'},
                'Role Tenure': {'type': 'rich_text'},
                'LinkedIn Activity Level': {'type': 'select'},
                'Network Quality': {'type': 'select'},
                'Problems They Likely Own': {'type': 'multi_select'},
                'Content Themes They Value': {'type': 'multi_select'},
                'Connection Pathways': {'type': 'rich_text'},
                'Value-Add Ideas': {'type': 'rich_text'},
                'Apollo Contact ID': {'type': 'rich_text'},
                'Created At': {'type': 'created_time'}
            }

        # Check for missing fields
        if database_type and required_fields:
            for field_name, field_config in required_fields.items():
                if field_name not in current_props:
                    missing_fields.append({
                        'name': field_name,
                        'type': field_config['type']
                    })

        print(f"\n📋 Database Type: {database_type or 'Unknown'}")
        print(f"❌ Missing Fields: {len(missing_fields)}")
        for field in missing_fields[:5]:  # Show first 5
            print(f"   • {field['name']} ({field['type']})")

        return {
            'database_id': database_id,
            'title': title,
            'type': database_type,
            'current_properties': current_props,
            'missing_fields': missing_fields,
            'needs_enhancement': len(missing_fields) > 0
        }

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

def enhance_database_with_missing_fields(database_analysis: dict):
    """Add missing fields to existing database"""

    if not database_analysis or not database_analysis['needs_enhancement']:
        return False

    client = config.get_notion_client()
    database_id = database_analysis['database_id']
    title = database_analysis['title']
    missing_fields = database_analysis['missing_fields']

    print(f"\n🔧 ENHANCING DATABASE: {title}")
    print(f"Adding {len(missing_fields)} missing fields...")
    print("-" * 40)

    try:
        # Get current properties
        current_props = database_analysis['current_properties']

        # Add missing fields one by one
        enhanced_props = current_props.copy()

        for field in missing_fields:
            field_name = field['name']
            field_type = field['type']

            print(f"   ➕ Adding {field_name} ({field_type})")

            # Create appropriate field configuration
            if field_type == 'select':
                if 'Status' in field_name:
                    enhanced_props[field_name] = {
                        'select': {
                            'options': [
                                {'name': 'Not Started', 'color': 'gray'},
                                {'name': 'In Progress', 'color': 'yellow'},
                                {'name': 'Complete', 'color': 'green'}
                            ]
                        }
                    }
                elif 'Business Model' in field_name:
                    enhanced_props[field_name] = {
                        'select': {
                            'options': [
                                {'name': 'Cloud Provider', 'color': 'blue'},
                                {'name': 'Colocation', 'color': 'green'},
                                {'name': 'Hyperscaler', 'color': 'purple'},
                                {'name': 'AI-focused DC', 'color': 'orange'}
                            ]
                        }
                    }
                elif 'Buying Committee' in field_name:
                    enhanced_props[field_name] = {
                        'select': {
                            'options': [
                                {'name': 'Economic Buyer', 'color': 'green'},
                                {'name': 'Technical Evaluator', 'color': 'blue'},
                                {'name': 'Champion', 'color': 'purple'},
                                {'name': 'Influencer', 'color': 'yellow'},
                                {'name': 'User', 'color': 'gray'},
                                {'name': 'Blocker', 'color': 'red'}
                            ]
                        }
                    }
                else:
                    enhanced_props[field_name] = {'select': {'options': []}}

            elif field_type == 'multi_select':
                if 'Problems' in field_name:
                    enhanced_props[field_name] = {
                        'multi_select': {
                            'options': [
                                {'name': 'Power Capacity Planning', 'color': 'red'},
                                {'name': 'Uptime Pressure', 'color': 'orange'},
                                {'name': 'Cost Optimization', 'color': 'yellow'},
                                {'name': 'Predictive Maintenance', 'color': 'green'},
                                {'name': 'Energy Efficiency', 'color': 'blue'}
                            ]
                        }
                    }
                elif 'Content Themes' in field_name:
                    enhanced_props[field_name] = {
                        'multi_select': {
                            'options': [
                                {'name': 'AI Infrastructure', 'color': 'purple'},
                                {'name': 'Power Optimization', 'color': 'red'},
                                {'name': 'Sustainability', 'color': 'green'},
                                {'name': 'Reliability Engineering', 'color': 'blue'}
                            ]
                        }
                    }
                else:
                    enhanced_props[field_name] = {'multi_select': {'options': []}}

            elif field_type == 'formula' and 'Lead Score' in field_name:
                enhanced_props[field_name] = {
                    'formula': {
                        'expression': 'round(prop("ICP Fit Score") * 0.4 + prop("Buying Power Score") * 0.3 + prop("Engagement Potential Score") * 0.3)'
                    }
                }

            elif field_type == 'number':
                enhanced_props[field_name] = {'number': {'format': 'number'}}
            elif field_type == 'rich_text':
                enhanced_props[field_name] = {'rich_text': {}}
            elif field_type == 'url':
                enhanced_props[field_name] = {'url': {}}
            elif field_type == 'email':
                enhanced_props[field_name] = {'email': {}}
            elif field_type == 'date':
                enhanced_props[field_name] = {'date': {}}
            elif field_type == 'created_time':
                enhanced_props[field_name] = {'created_time': {}}
            elif field_type == 'title':
                # Can't add title field to existing database
                print(f"      ⚠️ Skipping title field (only one allowed per database)")
                continue

        # Update database with enhanced properties
        updated_db = client.databases.update(
            database_id=database_id,
            properties=enhanced_props
        )

        print(f"   ✅ Successfully enhanced database")
        print(f"   📊 Total fields now: {len(enhanced_props)}")

        return True

    except Exception as e:
        print(f"   ❌ Enhancement failed: {e}")
        return False

def main():
    """Main function to find and enhance databases"""

    print("🚀 FINDING AND ENHANCING NOTION DATABASES")
    print("=" * 60)

    # Step 1: Find existing databases
    existing_databases = find_existing_databases()

    if not existing_databases:
        print("\n❌ No existing ABM databases found")
        print("💡 Recommendation: Use manual database creation instructions")
        return

    # Step 2: Analyze each database
    analyses = []
    for db in existing_databases:
        analysis = analyze_database_schema(db['id'], db['title'])
        if analysis:
            analyses.append(analysis)

    # Step 3: Enhance databases that need it
    enhanced_count = 0
    for analysis in analyses:
        if analysis['needs_enhancement']:
            success = enhance_database_with_missing_fields(analysis)
            if success:
                enhanced_count += 1

    print(f"\n🎉 ENHANCEMENT COMPLETE")
    print(f"   📊 Databases analyzed: {len(analyses)}")
    print(f"   ✅ Databases enhanced: {enhanced_count}")

    if enhanced_count > 0:
        print(f"   🚀 Databases now ready for production ABM system!")

if __name__ == "__main__":
    main()