"""
Smart Account Conflict Resolution System
Prevents duplicate accounts and intelligently merges data
"""
import requests
from difflib import SequenceMatcher
from ..config.manager import config_manager

class AccountConflictResolver:
    """Smart system for handling account duplicates and conflicts"""

    def __init__(self):
        self.headers = config_manager.get_notion_headers()
        self.base_url = "https://api.notion.com/v1"

    def query_database(self, database_id):
        """Query Notion database using raw API"""
        response = requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json={}
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Database query failed: {response.status_code} - {response.text}")

    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings (0-1)"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def extract_account_data(self, notion_page):
        """Extract account data from Notion page"""
        props = notion_page.get('properties', {})

        name = ''
        if 'Account Name' in props and props['Account Name'].get('title'):
            name = ''.join([t['plain_text'] for t in props['Account Name']['title']])

        domain = ''
        if 'Domain' in props and props['Domain'].get('rich_text'):
            domain = ''.join([t['plain_text'] for t in props['Domain']['rich_text']])

        return {
            'id': notion_page['id'],
            'name': name,
            'domain': domain,
            'employee_count': props.get('Employee Count', {}).get('number', 0),
            'icp_score': props.get('ICP Fit Score', {}).get('number', 0)
        }

    def find_potential_duplicates(self, new_account):
        """Find potential duplicate accounts in Notion"""
        try:
            # Get accounts database ID
            accounts_db_id = config_manager.get_database_id('accounts')
            # Query existing accounts
            accounts_data = self.query_database(accounts_db_id)
        except ValueError:
            return []
        except Exception:
            return []

        try:
            existing_accounts = []

            for page in accounts_data.get('results', []):
                account_data = self.extract_account_data(page)
                existing_accounts.append(account_data)

            # Find matches
            potential_duplicates = []

            for existing in existing_accounts:
                match_score = 0
                match_reasons = []

                # Exact domain match (highest priority)
                if new_account.get('domain') and existing['domain']:
                    if new_account['domain'].lower() == existing['domain'].lower():
                        match_score = 1.0
                        match_reasons.append("Exact domain match")

                # Company name similarity
                if new_account.get('name') and existing['name']:
                    name_similarity = self.calculate_similarity(new_account['name'], existing['name'])
                    if name_similarity >= 0.8:
                        match_score = max(match_score, name_similarity)
                        match_reasons.append(f"Name similarity: {name_similarity:.2f}")

                # Domain similarity (if no exact match)
                if match_score < 1.0 and new_account.get('domain') and existing['domain']:
                    domain_similarity = self.calculate_similarity(new_account['domain'], existing['domain'])
                    if domain_similarity >= 0.7:
                        match_score = max(match_score, domain_similarity * 0.9)  # Slightly lower than exact
                        match_reasons.append(f"Domain similarity: {domain_similarity:.2f}")

                if match_score >= 0.7:  # Threshold for potential duplicate
                    potential_duplicates.append({
                        'existing_account': existing,
                        'match_score': match_score,
                        'match_reasons': match_reasons,
                        'conflict_type': self.classify_conflict_type(match_score, match_reasons)
                    })

            # Sort by match score (highest first)
            potential_duplicates.sort(key=lambda x: x['match_score'], reverse=True)

            return potential_duplicates

        except Exception as e:
            print(f"Error finding duplicates: {str(e)}")
            return []

    def classify_conflict_type(self, match_score, match_reasons):
        """Classify the type of conflict"""
        if match_score >= 1.0:
            return "EXACT_DUPLICATE"
        elif any("Exact domain match" in reason for reason in match_reasons):
            return "DOMAIN_CONFLICT"
        elif match_score >= 0.9:
            return "HIGH_SIMILARITY"
        else:
            return "POTENTIAL_DUPLICATE"

    def resolve_conflict(self, new_account, conflict):
        """Generate conflict resolution strategy"""
        existing = conflict['existing_account']
        conflict_type = conflict['conflict_type']

        resolution = {
            'action': 'unknown',
            'reasoning': '',
            'merge_strategy': None,
            'manual_review': False
        }

        if conflict_type == "EXACT_DUPLICATE":
            resolution.update({
                'action': 'USE_EXISTING',
                'reasoning': f"Account '{existing['name']}' already exists with identical information",
                'existing_account_id': existing['id']
            })

        elif conflict_type == "DOMAIN_CONFLICT":
            resolution.update({
                'action': 'UPDATE_EXISTING',
                'reasoning': f"Same domain ({existing['domain']}) but different company names",
                'merge_strategy': {
                    'keep_existing_id': existing['id'],
                    'update_name': self.choose_better_name(new_account.get('name', ''), existing['name']),
                    'update_employee_count': max(new_account.get('employee_count', 0), existing['employee_count']),
                    'update_icp_score': max(new_account.get('icp_score', 0), existing['icp_score'])
                }
            })

        elif conflict_type == "HIGH_SIMILARITY":
            resolution.update({
                'action': 'MANUAL_REVIEW',
                'reasoning': f"High similarity but not exact - requires human decision",
                'manual_review': True,
                'comparison': {
                    'new': new_account,
                    'existing': existing,
                    'match_score': conflict['match_score']
                }
            })

        else:  # POTENTIAL_DUPLICATE
            resolution.update({
                'action': 'CREATE_NEW',
                'reasoning': f"Similarity below threshold - create new account",
                'note': f"Monitor for potential relationship with {existing['name']}"
            })

        return resolution

    def check_account_conflicts(self, new_account_data):
        """Main function to check for and resolve account conflicts"""
        print(f"🔍 Checking for conflicts: {new_account_data.get('name', 'Unknown')} ({new_account_data.get('domain', 'No domain')})")

        # Find potential duplicates
        duplicates = self.find_potential_duplicates(new_account_data)

        if not duplicates:
            return {
                'conflicts_found': False,
                'action': 'CREATE_NEW',
                'reasoning': 'No conflicts detected - safe to create new account'
            }

        # Process conflicts
        print(f"⚠️ Found {len(duplicates)} potential conflict(s)")

        conflicts_analysis = []
        for i, duplicate in enumerate(duplicates):
            existing = duplicate['existing_account']
            print(f"   {i+1}. {existing['name']} (Score: {duplicate['match_score']:.2f})")
            print(f"      Reasons: {', '.join(duplicate['match_reasons'])}")

            resolution = self.resolve_conflict(new_account_data, duplicate)
            conflicts_analysis.append({
                'duplicate': duplicate,
                'resolution': resolution
            })

        # Return primary recommendation (highest match)
        primary_resolution = conflicts_analysis[0]['resolution'] if conflicts_analysis else None

        return {
            'conflicts_found': True,
            'conflicts_count': len(duplicates),
            'primary_conflict': duplicates[0],
            'recommended_action': primary_resolution['action'],
            'reasoning': primary_resolution['reasoning'],
            'all_conflicts': conflicts_analysis,
            'requires_manual_review': primary_resolution.get('manual_review', False)
        }

    def choose_better_name(self, name1, name2):
        """Choose the better company name (more complete/official)"""
        if not name1:
            return name2
        if not name2:
            return name1

        # Prefer longer, more descriptive names
        if len(name1) > len(name2) * 1.2:
            return name1
        elif len(name2) > len(name1) * 1.2:
            return name2

        # Prefer names with "Inc", "Corp", "LLC" etc.
        corporate_indicators = ['Inc', 'Corp', 'LLC', 'Ltd', 'Company', 'Corporation']
        name1_has_corp = any(indicator in name1 for indicator in corporate_indicators)
        name2_has_corp = any(indicator in name2 for indicator in corporate_indicators)

        if name1_has_corp and not name2_has_corp:
            return name1
        elif name2_has_corp and not name1_has_corp:
            return name2

        # Default to first name if no clear winner
        return name1

    def generate_conflict_report(self, conflict_result):
        """Generate a human-readable conflict report"""
        if not conflict_result['conflicts_found']:
            return "✅ No conflicts found - proceed with account creation"

        report = f"⚠️ ACCOUNT CONFLICT DETECTED\n"
        report += f"Conflicts found: {conflict_result['conflicts_count']}\n"
        report += f"Recommended action: {conflict_result['recommended_action']}\n"
        report += f"Reasoning: {conflict_result['reasoning']}\n\n"

        if conflict_result['requires_manual_review']:
            report += "🔍 MANUAL REVIEW REQUIRED\n"
            report += "Please review the similarities and decide:\n"

            for i, conflict_data in enumerate(conflict_result['all_conflicts']):
                duplicate = conflict_data['duplicate']
                existing = duplicate['existing_account']
                report += f"  Option {i+1}: Existing account '{existing['name']}' (Match: {duplicate['match_score']:.2f})\n"
                report += f"    Domain: {existing['domain']}\n"
                report += f"    Employees: {existing['employee_count']}\n"

        return report

def test_conflict_resolution():
    """Test the conflict resolution system"""
    resolver = AccountConflictResolver()

    # Test case 1: Exact duplicate
    print("🧪 Testing exact duplicate detection...")
    test_account = {
        'name': 'Genesis Cloud Infrastructure',
        'domain': 'genesis-cloud.com',
        'employee_count': 450
    }

    result = resolver.check_account_conflicts(test_account)
    print(resolver.generate_conflict_report(result))
    print()

    # Test case 2: Similar company
    print("🧪 Testing similar company detection...")
    test_account2 = {
        'name': 'Genesis Cloud Inc',
        'domain': 'genesis.cloud',
        'employee_count': 500
    }

    result2 = resolver.check_account_conflicts(test_account2)
    print(resolver.generate_conflict_report(result2))
    print()

    # Test case 3: No conflict
    print("🧪 Testing no conflict scenario...")
    test_account3 = {
        'name': 'Digital Realty',
        'domain': 'digitalrealty.com',
        'employee_count': 2000
    }

    result3 = resolver.check_account_conflicts(test_account3)
    print(resolver.generate_conflict_report(result3))

if __name__ == "__main__":
    test_conflict_resolution()
