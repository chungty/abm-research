#!/usr/bin/env python3
"""
QA Verification Agent - Tests Every Claim Before Marking Tasks Complete
Prevents the cycle of claiming success without independent verification
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess

class QAVerificationAgent:
    """Independent verification agent that tests all claims"""

    def __init__(self):
        self.notion_token = os.getenv('NOTION_ABM_API_KEY')
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        } if self.notion_token else None

        # ACTUAL DATABASE IDs PROVIDED BY USER (no dashes!)
        self.actual_database_ids = {
            'accounts': 'c31d728f477049e28f6bd68717e2c160',
            'trigger_events': 'c8ae1662cba94ea39cb32bcea3621963',
            'contacts': 'a6e0cace85de4afdbe6c9c926d1d0e3d',
            'partnerships': 'fa1467c0ad154b09bb03cc715f9b8577'
        }

        self.verification_log = []
        print("🔍 QA Verification Agent initialized")
        print("🎯 Mission: Test every claim, prevent false success reporting")

    def verify_notion_databases_exist_and_accessible(self) -> Dict:
        """Verify that all 4 Notion databases actually exist and are accessible"""

        print("\n🔍 QA TEST: Verifying Notion databases exist and are accessible...")

        if not self.headers:
            return self._fail_test("NOTION_ABM_API_KEY not found")

        results = {
            'test_name': 'notion_databases_accessible',
            'passed': False,
            'details': {},
            'errors': []
        }

        for db_type, db_id in self.actual_database_ids.items():
            print(f"   Testing {db_type} database: {db_id}")

            try:
                # Test 1: Can we retrieve database schema?
                response = requests.get(
                    f"https://api.notion.com/v1/databases/{db_id}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    db_info = response.json()
                    title = db_info.get('title', [{}])[0].get('text', {}).get('content', 'No Title')

                    # Test 2: Can we query for records?
                    query_response = requests.post(
                        f"https://api.notion.com/v1/databases/{db_id}/query",
                        headers=self.headers,
                        json={'page_size': 5}
                    )

                    if query_response.status_code == 200:
                        query_data = query_response.json()
                        record_count = len(query_data.get('results', []))

                        results['details'][db_type] = {
                            'exists': True,
                            'title': title,
                            'record_count': record_count,
                            'queryable': True
                        }
                        print(f"   ✅ {db_type}: EXISTS, '{title}', {record_count} records")

                    else:
                        results['details'][db_type] = {
                            'exists': True,
                            'queryable': False,
                            'error': f"Query failed: {query_response.status_code}"
                        }
                        results['errors'].append(f"{db_type}: Not queryable")
                        print(f"   ❌ {db_type}: EXISTS but NOT QUERYABLE")

                else:
                    results['details'][db_type] = {
                        'exists': False,
                        'error': f"Database not accessible: {response.status_code}"
                    }
                    results['errors'].append(f"{db_type}: Does not exist or not accessible")
                    print(f"   ❌ {db_type}: DOES NOT EXIST OR NOT ACCESSIBLE")

            except Exception as e:
                results['details'][db_type] = {
                    'exists': False,
                    'error': str(e)
                }
                results['errors'].append(f"{db_type}: Exception - {e}")
                print(f"   ❌ {db_type}: ERROR - {e}")

        # Pass test only if all databases exist and are queryable
        all_accessible = all(
            details.get('exists', False) and details.get('queryable', False)
            for details in results['details'].values()
        )

        results['passed'] = all_accessible and len(results['errors']) == 0

        if results['passed']:
            print("   🎉 QA PASS: All databases exist and are queryable")
        else:
            print(f"   ❌ QA FAIL: {len(results['errors'])} database issues found")

        self.verification_log.append(results)
        return results

    def verify_genesis_cloud_data_populated(self) -> Dict:
        """Verify that Genesis Cloud data is actually in all 4 databases"""

        print("\n🔍 QA TEST: Verifying Genesis Cloud data is populated in databases...")

        results = {
            'test_name': 'genesis_cloud_data_populated',
            'passed': False,
            'expected_data': {
                'accounts': 1,  # 1 Genesis Cloud account
                'trigger_events': 1,  # 1 AI workload expansion event
                'contacts': 3,  # Stefan, Eyitayo, Julia
                'partnerships': 1  # 1 NVIDIA DGX partnership
            },
            'actual_data': {},
            'errors': []
        }

        if not self.headers:
            return self._fail_test("NOTION_ABM_API_KEY not found")

        for db_type, db_id in self.actual_database_ids.items():
            print(f"   Checking {db_type} for Genesis Cloud data...")

            try:
                response = requests.post(
                    f"https://api.notion.com/v1/databases/{db_id}/query",
                    headers=self.headers,
                    json={'page_size': 100}
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', [])
                    record_count = len(records)

                    # Check for Genesis Cloud specific data
                    genesis_found = self._verify_genesis_cloud_records(db_type, records)

                    results['actual_data'][db_type] = {
                        'record_count': record_count,
                        'genesis_cloud_found': genesis_found,
                        'sample_records': self._sample_record_data(db_type, records[:2])
                    }

                    expected_count = results['expected_data'][db_type]
                    if record_count >= expected_count and genesis_found:
                        print(f"   ✅ {db_type}: {record_count} records, Genesis Cloud data found")
                    else:
                        print(f"   ❌ {db_type}: {record_count} records (expected {expected_count}), Genesis Cloud: {'found' if genesis_found else 'NOT found'}")
                        results['errors'].append(f"{db_type}: Missing or insufficient Genesis Cloud data")

                else:
                    results['errors'].append(f"{db_type}: Query failed - {response.status_code}")
                    print(f"   ❌ {db_type}: Query failed")

            except Exception as e:
                results['errors'].append(f"{db_type}: Exception - {e}")
                print(f"   ❌ {db_type}: ERROR - {e}")

        # Pass test only if all databases have expected Genesis Cloud data
        results['passed'] = len(results['errors']) == 0

        if results['passed']:
            print("   🎉 QA PASS: Genesis Cloud data found in all databases")
        else:
            print(f"   ❌ QA FAIL: {len(results['errors'])} data population issues")

        self.verification_log.append(results)
        return results

    def verify_dashboard_reads_from_notion(self, dashboard_url: str) -> Dict:
        """Verify that dashboard actually reads data from Notion (not hardcoded)"""

        print(f"\n🔍 QA TEST: Verifying dashboard reads from Notion: {dashboard_url}")

        results = {
            'test_name': 'dashboard_notion_integration',
            'passed': False,
            'dashboard_url': dashboard_url,
            'errors': []
        }

        try:
            # Test dashboard endpoint
            response = requests.get(dashboard_url, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Check for dynamic data vs hardcoded
                if 'Genesis Cloud' in content and 'Julia Bauer' in content:
                    # Could be dynamic or hardcoded - need to check API calls
                    if '/api/' in content or 'notion' in content.lower():
                        results['passed'] = True
                        print("   ✅ Dashboard appears to use API/Notion integration")
                    else:
                        results['errors'].append("Dashboard appears to use hardcoded data")
                        print("   ❌ Dashboard appears to use hardcoded data")
                else:
                    results['errors'].append("Dashboard does not show expected data")
                    print("   ❌ Dashboard does not show expected Genesis Cloud data")

            else:
                results['errors'].append(f"Dashboard not accessible: {response.status_code}")
                print(f"   ❌ Dashboard not accessible: {response.status_code}")

        except Exception as e:
            results['errors'].append(f"Dashboard test error: {e}")
            print(f"   ❌ Dashboard test error: {e}")

        self.verification_log.append(results)
        return results

    def verify_five_phase_workflow_complete(self, research_data_file: str) -> Dict:
        """Verify that research data contains all 5 phases per skill specification"""

        print(f"\n🔍 QA TEST: Verifying 5-phase workflow completeness...")

        results = {
            'test_name': 'five_phase_workflow_complete',
            'passed': False,
            'phases_found': {},
            'errors': []
        }

        try:
            if not os.path.exists(research_data_file):
                return self._fail_test(f"Research data file not found: {research_data_file}")

            with open(research_data_file, 'r') as f:
                research = json.load(f)

            # Check Phase 1: Account Intelligence Baseline
            phase1 = research.get('phase1_account_intelligence', {})
            if phase1.get('icp_fit_score') and phase1.get('trigger_events'):
                results['phases_found']['phase1'] = True
                print("   ✅ Phase 1: Account Intelligence Baseline - Complete")
            else:
                results['phases_found']['phase1'] = False
                results['errors'].append("Phase 1: Missing ICP score or trigger events")
                print("   ❌ Phase 1: Account Intelligence Baseline - Incomplete")

            # Check Phase 2: Contact Discovery & Segmentation
            phase2 = research.get('phase2_contacts', {})
            if phase2.get('contacts') and len(phase2['contacts']) > 0:
                results['phases_found']['phase2'] = True
                print("   ✅ Phase 2: Contact Discovery & Segmentation - Complete")
            else:
                results['phases_found']['phase2'] = False
                results['errors'].append("Phase 2: No contacts discovered")
                print("   ❌ Phase 2: Contact Discovery & Segmentation - Incomplete")

            # Check Phase 3: High-Priority Contact Enrichment
            phase3 = research.get('phase3_enriched_contacts', {})
            if phase3.get('enriched_contacts'):
                results['phases_found']['phase3'] = True
                print("   ✅ Phase 3: High-Priority Contact Enrichment - Complete")
            else:
                results['phases_found']['phase3'] = False
                results['errors'].append("Phase 3: No enriched contacts")
                print("   ❌ Phase 3: High-Priority Contact Enrichment - Incomplete")

            # Check Phase 4: Engagement Intelligence
            phase4 = research.get('phase4_engagement_intelligence', {})
            if phase4.get('engagement_ready_contacts'):
                results['phases_found']['phase4'] = True
                print("   ✅ Phase 4: Engagement Intelligence - Complete")
            else:
                results['phases_found']['phase4'] = False
                results['errors'].append("Phase 4: No engagement intelligence")
                print("   ❌ Phase 4: Engagement Intelligence - Incomplete")

            # Check Phase 5: Strategic Partnership Intelligence
            phase5 = research.get('phase5_partnerships', {})
            if phase5.get('partnerships'):
                results['phases_found']['phase5'] = True
                print("   ✅ Phase 5: Strategic Partnership Intelligence - Complete")
            else:
                results['phases_found']['phase5'] = False
                results['errors'].append("Phase 5: No partnerships detected")
                print("   ❌ Phase 5: Strategic Partnership Intelligence - Incomplete")

            # Pass only if all 5 phases are complete
            results['passed'] = all(results['phases_found'].values())

            if results['passed']:
                print("   🎉 QA PASS: All 5 phases complete per skill specification")
            else:
                print(f"   ❌ QA FAIL: {len(results['errors'])} phase completion issues")

        except Exception as e:
            results['errors'].append(f"Workflow verification error: {e}")
            print(f"   ❌ Workflow verification error: {e}")

        self.verification_log.append(results)
        return results

    def generate_qa_report(self) -> Dict:
        """Generate comprehensive QA report with pass/fail status"""

        total_tests = len(self.verification_log)
        passed_tests = sum(1 for test in self.verification_log if test['passed'])

        report = {
            'qa_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'overall_status': 'PASS' if passed_tests == total_tests else 'FAIL'
            },
            'test_results': self.verification_log,
            'report_timestamp': datetime.now().isoformat()
        }

        print(f"\n📋 QA VERIFICATION REPORT")
        print("=" * 50)
        print(f"Tests Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Overall Status: {report['qa_summary']['overall_status']}")

        if report['qa_summary']['overall_status'] == 'FAIL':
            print("\n❌ CRITICAL: System not ready for production")
            print("🚨 Failed tests must be resolved before proceeding")
        else:
            print("\n✅ All QA tests passed - System verified")

        return report

    def _verify_genesis_cloud_records(self, db_type: str, records: List[Dict]) -> bool:
        """Check if records contain Genesis Cloud specific data"""

        for record in records:
            properties = record.get('properties', {})

            if db_type == 'accounts':
                company_name = properties.get('Company Name', {}).get('title', [])
                if company_name and 'Genesis' in company_name[0].get('text', {}).get('content', ''):
                    return True

            elif db_type == 'contacts':
                name = properties.get('Name', {}).get('title', [])
                if name:
                    contact_name = name[0].get('text', {}).get('content', '')
                    if any(genesis_name in contact_name for genesis_name in ['Stefan', 'Julia', 'Eyitayo']):
                        return True

            elif db_type == 'trigger_events':
                description = properties.get('Event Description', {}).get('title', [])
                if description and 'Genesis' in description[0].get('text', {}).get('content', ''):
                    return True

            elif db_type == 'partnerships':
                partner = properties.get('Partner Name', {}).get('title', [])
                if partner and 'NVIDIA' in partner[0].get('text', {}).get('content', ''):
                    return True

        return False

    def _sample_record_data(self, db_type: str, records: List[Dict]) -> List[str]:
        """Extract sample data from records for verification"""

        samples = []
        for record in records[:2]:  # Sample first 2 records
            properties = record.get('properties', {})

            if db_type == 'accounts':
                title_prop = properties.get('Company Name', {}).get('title', [])
                if title_prop:
                    samples.append(title_prop[0].get('text', {}).get('content', 'No name'))

            elif db_type in ['contacts', 'trigger_events', 'partnerships']:
                # Try to get the title/name field
                for field_name in ['Name', 'Event Description', 'Partner Name']:
                    if field_name in properties:
                        title_prop = properties[field_name].get('title', [])
                        if title_prop:
                            samples.append(title_prop[0].get('text', {}).get('content', 'No title'))
                            break

        return samples

    def _fail_test(self, error_message: str) -> Dict:
        """Helper to create failed test result"""
        return {
            'passed': False,
            'errors': [error_message]
        }


if __name__ == "__main__":
    qa_agent = QAVerificationAgent()

    # Run all verification tests
    qa_agent.verify_notion_databases_exist_and_accessible()
    qa_agent.verify_genesis_cloud_data_populated()
    qa_agent.verify_five_phase_workflow_complete('/Users/chungty/Projects/vdg-clean/abm-research/genesis_cloud_comprehensive_research.json')

    # Generate report
    report = qa_agent.generate_qa_report()