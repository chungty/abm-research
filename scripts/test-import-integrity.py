#!/usr/bin/env python3
"""
ABM Import Integrity Testing Script
Tests that all critical imports work correctly and dependencies are satisfied
"""

import sys
import os
import traceback
from datetime import datetime

def print_header():
    """Print test header"""
    print("🔍 ABM Import Integrity Testing")
    print("===============================")
    print(f"📅 Test run: {datetime.now().isoformat()[:19]}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"📁 Working directory: {os.getcwd()}")
    print()

def test_core_imports():
    """Test core ABM system imports"""
    print("📋 Step 1: Testing core ABM imports...")

    results = []

    # Test basic Python path setup
    try:
        sys.path.append('.')
        results.append(("Python path setup", "SUCCESS", "Current directory added to path"))
    except Exception as e:
        results.append(("Python path setup", "ERROR", f"Failed to set up path: {e}"))
        return results

    # Test dashboard data service
    try:
        from dashboard_data_service import DashboardDataService, NotionDataService
        results.append(("dashboard_data_service", "SUCCESS", "DashboardDataService and NotionDataService imported"))
    except ImportError as e:
        results.append(("dashboard_data_service", "CRITICAL", f"Import failed: {e}"))
    except Exception as e:
        results.append(("dashboard_data_service", "ERROR", f"Unexpected error: {e}"))

    # Test enhanced buying signals analyzer
    try:
        from enhanced_buying_signals_analyzer import enhanced_buying_signals_analyzer
        results.append(("enhanced_buying_signals_analyzer", "SUCCESS", "Analyzer imported successfully"))
    except ImportError as e:
        results.append(("enhanced_buying_signals_analyzer", "WARNING", f"Import failed: {e}"))
    except Exception as e:
        results.append(("enhanced_buying_signals_analyzer", "ERROR", f"Unexpected error: {e}"))

    # Test contact value analyzer
    try:
        from contact_value_analyzer import contact_value_analyzer
        results.append(("contact_value_analyzer", "SUCCESS", "Analyzer imported successfully"))
    except ImportError as e:
        results.append(("contact_value_analyzer", "WARNING", f"Import failed: {e}"))
    except Exception as e:
        results.append(("contact_value_analyzer", "ERROR", f"Unexpected error: {e}"))

    # Test enhanced account plan generator
    try:
        from enhanced_account_plan_generator import enhanced_account_plan_generator
        results.append(("enhanced_account_plan_generator", "SUCCESS", "Generator imported successfully"))
    except ImportError as e:
        results.append(("enhanced_account_plan_generator", "WARNING", f"Import failed: {e}"))
    except Exception as e:
        results.append(("enhanced_account_plan_generator", "ERROR", f"Unexpected error: {e}"))

    # Test canonical dashboard server
    try:
        import enhanced_dashboard_server
        results.append(("enhanced_dashboard_server", "SUCCESS", "Canonical dashboard server imported"))
    except ImportError as e:
        results.append(("enhanced_dashboard_server", "CRITICAL", f"Import failed: {e}"))
    except Exception as e:
        results.append(("enhanced_dashboard_server", "ERROR", f"Unexpected error: {e}"))

    return results

def test_external_dependencies():
    """Test external library dependencies"""
    print("📋 Step 2: Testing external dependencies...")

    results = []

    # Test Flask (critical for dashboard)
    try:
        import flask
        results.append(("flask", "SUCCESS", f"Version {flask.__version__}"))
    except ImportError:
        results.append(("flask", "CRITICAL", "Flask not installed - dashboard will not work"))

    # Test requests (critical for API calls)
    try:
        import requests
        results.append(("requests", "SUCCESS", f"Version {requests.__version__}"))
    except ImportError:
        results.append(("requests", "CRITICAL", "Requests not installed - API calls will fail"))

    # Test OpenAI (for enhanced features)
    try:
        import openai
        results.append(("openai", "SUCCESS", f"Version {openai.__version__}"))
    except ImportError:
        results.append(("openai", "WARNING", "OpenAI not installed - AI features may be limited"))

    # Test json (built-in, should always work)
    try:
        import json
        results.append(("json", "SUCCESS", "Built-in JSON support"))
    except ImportError:
        results.append(("json", "CRITICAL", "JSON not available - system will not function"))

    # Test datetime (built-in, should always work)
    try:
        from datetime import datetime
        results.append(("datetime", "SUCCESS", "Built-in datetime support"))
    except ImportError:
        results.append(("datetime", "ERROR", "Datetime not available"))

    return results

def test_environment_variables():
    """Test critical environment variables"""
    print("📋 Step 3: Testing environment variables...")

    results = []

    # Test Notion API key
    notion_key = os.getenv('NOTION_API_KEY')
    if notion_key:
        if len(notion_key) > 20:
            results.append(("NOTION_API_KEY", "SUCCESS", f"Set (length: {len(notion_key)})"))
        else:
            results.append(("NOTION_API_KEY", "WARNING", f"Set but looks invalid (length: {len(notion_key)})"))
    else:
        results.append(("NOTION_API_KEY", "CRITICAL", "Not set - real data will not work"))

    # Test Apollo API key
    apollo_key = os.getenv('APOLLO_API_KEY')
    if apollo_key:
        results.append(("APOLLO_API_KEY", "SUCCESS", f"Set (length: {len(apollo_key)})"))
    else:
        results.append(("APOLLO_API_KEY", "WARNING", "Not set - contact enrichment may be limited"))

    # Test OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        results.append(("OPENAI_API_KEY", "SUCCESS", f"Set (length: {len(openai_key)})"))
    else:
        results.append(("OPENAI_API_KEY", "WARNING", "Not set - AI features will not work"))

    return results

def test_critical_files():
    """Test that critical files exist"""
    print("📋 Step 4: Testing critical files...")

    results = []

    critical_files = [
        "enhanced_dashboard_server.py",
        "dashboard_data_service.py",
        "enhanced_buying_signals_analyzer.py",
        "contact_value_analyzer.py",
        "enhanced_account_plan_generator.py",
        "verdigris_sales_dashboard.html"
    ]

    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            results.append((file_path, "SUCCESS", f"Exists ({size} bytes)"))
        else:
            results.append((file_path, "CRITICAL", "File missing"))

    return results

def test_method_availability():
    """Test that critical methods are available"""
    print("📋 Step 5: Testing method availability...")

    results = []

    try:
        from dashboard_data_service import NotionDataService
        service = NotionDataService()

        # Test dashboard methods
        required_methods = [
            'get_accounts_with_contacts',
            'get_contacts_for_account',
            'get_trigger_events_for_account',
            'get_strategic_partnerships',
            'get_account_by_name',
            'get_contact_by_name'
        ]

        for method_name in required_methods:
            if hasattr(service, method_name):
                results.append((f"NotionDataService.{method_name}", "SUCCESS", "Method available"))
            else:
                results.append((f"NotionDataService.{method_name}", "CRITICAL", "Method missing"))

    except Exception as e:
        results.append(("Method testing", "ERROR", f"Could not test methods: {e}"))

    return results

def print_results(results, section_name):
    """Print test results for a section"""
    print(f"  📊 {section_name} Results:")

    success_count = 0
    warning_count = 0
    error_count = 0
    critical_count = 0

    for component, status, message in results:
        if status == "SUCCESS":
            print(f"     ✅ {component}: {message}")
            success_count += 1
        elif status == "WARNING":
            print(f"     ⚠️  {component}: {message}")
            warning_count += 1
        elif status == "ERROR":
            print(f"     ❌ {component}: {message}")
            error_count += 1
        elif status == "CRITICAL":
            print(f"     🚨 {component}: {message}")
            critical_count += 1

    print(f"     Summary: {success_count} OK, {warning_count} warnings, {error_count} errors, {critical_count} critical")
    print()

    return success_count, warning_count, error_count, critical_count

def main():
    """Main test execution"""
    print_header()

    all_results = []

    # Run all tests
    core_results = test_core_imports()
    s1, w1, e1, c1 = print_results(core_results, "Core Imports")
    all_results.extend(core_results)

    dep_results = test_external_dependencies()
    s2, w2, e2, c2 = print_results(dep_results, "External Dependencies")
    all_results.extend(dep_results)

    env_results = test_environment_variables()
    s3, w3, e3, c3 = print_results(env_results, "Environment Variables")
    all_results.extend(env_results)

    file_results = test_critical_files()
    s4, w4, e4, c4 = print_results(file_results, "Critical Files")
    all_results.extend(file_results)

    method_results = test_method_availability()
    s5, w5, e5, c5 = print_results(method_results, "Method Availability")
    all_results.extend(method_results)

    # Overall summary
    total_success = s1 + s2 + s3 + s4 + s5
    total_warnings = w1 + w2 + w3 + w4 + w5
    total_errors = e1 + e2 + e3 + e4 + e5
    total_critical = c1 + c2 + c3 + c4 + c5

    print("🎯 OVERALL IMPORT INTEGRITY RESULTS")
    print("===================================")
    print(f"✅ Success: {total_success}")
    print(f"⚠️  Warnings: {total_warnings}")
    print(f"❌ Errors: {total_errors}")
    print(f"🚨 Critical Issues: {total_critical}")
    print()

    # Recommendations
    if total_critical > 0:
        print("🚨 CRITICAL ISSUES DETECTED")
        print("   The system will NOT function properly!")
        print("   Fix critical issues before starting dashboard.")
        print()
        return 1
    elif total_errors > 0:
        print("⚠️  ERRORS DETECTED")
        print("   Some features may not work correctly.")
        print("   Consider fixing errors for full functionality.")
        print()
        return 1
    elif total_warnings > 0:
        print("⚠️  WARNINGS DETECTED")
        print("   Basic functionality should work.")
        print("   Address warnings for enhanced features.")
        print()
        return 0
    else:
        print("🎉 ALL IMPORTS VERIFIED")
        print("   System ready for development!")
        print()
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)