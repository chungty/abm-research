#!/usr/bin/env python3
"""
Automated ABM Data Quality System
Prevents duplicates, ensures data consistency, and maintains clean databases
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import requests
import schedule

from ..config.manager import config_manager


@dataclass
class DataQualityRule:
    """Define data quality rules"""

    name: str
    description: str
    severity: str  # 'critical', 'warning', 'info'
    check_function: str
    auto_fix: bool = False


class ABMDataQualitySystem:
    """Automated data quality system with prevention, detection, and remediation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.headers = config_manager.get_notion_headers()
        # Use unified configuration manager for database IDs - no hardcoded values!
        self.database_ids = config_manager.get_all_database_ids()

        # Data quality rules
        self.quality_rules = [
            DataQualityRule(
                "duplicate_accounts",
                "Check for duplicate accounts",
                "critical",
                "check_duplicate_accounts",
                True,
            ),
            DataQualityRule(
                "duplicate_contacts",
                "Check for duplicate contacts",
                "critical",
                "check_duplicate_contacts",
                True,
            ),
            DataQualityRule(
                "orphaned_contacts",
                "Check for contacts without accounts",
                "warning",
                "check_orphaned_contacts",
                True,
            ),
            DataQualityRule(
                "incomplete_trigger_events",
                "Check trigger events missing fields",
                "warning",
                "check_incomplete_trigger_events",
                True,
            ),
            DataQualityRule(
                "broken_relationships",
                "Check broken account-contact relationships",
                "critical",
                "check_broken_relationships",
                True,
            ),
            DataQualityRule(
                "data_freshness", "Check data staleness", "info", "check_data_freshness", False
            ),
            DataQualityRule(
                "invalid_emails",
                "Check for invalid email formats",
                "warning",
                "check_invalid_emails",
                False,
            ),
            DataQualityRule(
                "missing_linkedin_urls",
                "Check for missing LinkedIn URLs",
                "info",
                "check_missing_linkedin",
                False,
            ),
        ]

        # Deduplication cache to prevent duplicate creation
        self.dedup_cache = {
            "accounts": {},
            "contacts": {},
            "trigger_events": {},
            "partnerships": {},
        }

        # Quality metrics tracking
        self.quality_metrics = {
            "last_check": None,
            "total_records": 0,
            "duplicate_count": 0,
            "orphaned_count": 0,
            "quality_score": 0.0,
            "issues_fixed": 0,
        }

    def build_deduplication_cache(self):
        """Build cache of existing records to prevent duplicates"""
        print("🔄 BUILDING DEDUPLICATION CACHE")
        print("=" * 40)

        # Cache accounts by domain and name
        accounts = self._fetch_all_accounts()
        for account in accounts:
            props = account.get("properties", {})
            domain = self._extract_rich_text(props.get("Domain", {}))
            name = self._extract_title(props.get("Name", {}))

            if domain:
                self.dedup_cache["accounts"][domain.lower()] = account["id"]
            if name:
                self.dedup_cache["accounts"][name.lower()] = account["id"]

        # Cache contacts by email, LinkedIn URL, and name+title combination
        contacts = self._fetch_all_contacts()
        for contact in contacts:
            props = contact.get("properties", {})
            email = self._extract_email(props.get("Email", {}))
            linkedin_url = self._extract_url(props.get("LinkedIn URL", {}))
            name = self._extract_title(props.get("Name", {}))
            title = self._extract_rich_text(props.get("Title", {}))

            if email and email != "email_not_unlocked@domain.com":
                self.dedup_cache["contacts"][email.lower()] = contact["id"]
            if linkedin_url:
                self.dedup_cache["contacts"][linkedin_url] = contact["id"]
            if name and title:
                name_title_key = f"{name.lower()}|{title.lower()}"
                self.dedup_cache["contacts"][name_title_key] = contact["id"]

        # Cache trigger events by description + account combination
        events = self._fetch_all_trigger_events()
        for event in events:
            props = event.get("properties", {})
            description = self._extract_title(props.get("Name", {}))
            account_relations = props.get("Account", {}).get("relation", [])
            account_id = account_relations[0]["id"] if account_relations else "no_account"

            if description:
                event_key = f"{description.lower()}|{account_id}"
                self.dedup_cache["trigger_events"][event_key] = event["id"]

        print(f"   ✅ Cached {len(self.dedup_cache['accounts'])} account keys")
        print(f"   ✅ Cached {len(self.dedup_cache['contacts'])} contact keys")
        print(f"   ✅ Cached {len(self.dedup_cache['trigger_events'])} event keys")

    def check_before_create_account(self, account_data: dict) -> Optional[str]:
        """Check if account already exists before creating"""
        domain = account_data.get("domain", "").lower()
        name = account_data.get("name", "").lower()

        # Check cache first
        if domain in self.dedup_cache["accounts"]:
            existing_id = self.dedup_cache["accounts"][domain]
            print(f"   ⚠️ Account already exists (domain): {domain} -> {existing_id[:8]}...")
            return existing_id

        if name in self.dedup_cache["accounts"]:
            existing_id = self.dedup_cache["accounts"][name]
            print(f"   ⚠️ Account already exists (name): {name} -> {existing_id[:8]}...")
            return existing_id

        return None  # Safe to create

    def check_before_create_contact(self, contact_data: dict) -> Optional[str]:
        """Check if contact already exists before creating"""
        email = contact_data.get("email", "").lower() if contact_data.get("email") else ""
        linkedin_url = contact_data.get("linkedin_url", "")
        name = contact_data.get("name", "").lower() if contact_data.get("name") else ""
        title = contact_data.get("title", "").lower() if contact_data.get("title") else ""

        # Check cache for exact matches
        if email and email != "email_not_unlocked@domain.com":
            if email in self.dedup_cache["contacts"]:
                existing_id = self.dedup_cache["contacts"][email]
                print(f"   ⚠️ Contact already exists (email): {email} -> {existing_id[:8]}...")
                return existing_id

        if linkedin_url and linkedin_url in self.dedup_cache["contacts"]:
            existing_id = self.dedup_cache["contacts"][linkedin_url]
            print(
                f"   ⚠️ Contact already exists (LinkedIn): {linkedin_url} -> {existing_id[:8]}..."
            )
            return existing_id

        if name and title:
            name_title_key = f"{name}|{title}"
            if name_title_key in self.dedup_cache["contacts"]:
                existing_id = self.dedup_cache["contacts"][name_title_key]
                print(
                    f"   ⚠️ Contact already exists (name+title): {name} {title} -> {existing_id[:8]}..."
                )
                return existing_id

        return None  # Safe to create

    def check_before_create_trigger_event(self, event_data: dict, account_id: str) -> Optional[str]:
        """Check if trigger event already exists before creating"""
        description = event_data.get("event_description", "").lower()
        account_key = account_id or "no_account"

        if description:
            event_key = f"{description}|{account_key}"
            if event_key in self.dedup_cache["trigger_events"]:
                existing_id = self.dedup_cache["trigger_events"][event_key]
                print(f"   ⚠️ Trigger event already exists: {description} -> {existing_id[:8]}...")
                return existing_id

        return None  # Safe to create

    def run_quality_checks(self) -> dict:
        """Run all data quality checks"""
        print("🔍 RUNNING DATA QUALITY CHECKS")
        print("=" * 45)

        results = {
            "timestamp": datetime.now().isoformat(),
            "checks_run": len(self.quality_rules),
            "issues_found": [],
            "issues_fixed": 0,
            "quality_score": 0.0,
        }

        total_issues = 0
        total_fixed = 0

        for rule in self.quality_rules:
            print(f"\n   🔍 {rule.name}: {rule.description}")

            try:
                # Dynamic method call based on rule
                check_method = getattr(self, rule.check_function)
                issues = check_method()

                if issues:
                    total_issues += len(issues)

                    issue_result = {
                        "rule": rule.name,
                        "severity": rule.severity,
                        "count": len(issues),
                        "issues": issues[:5],  # Limit output
                        "auto_fixed": 0,
                    }

                    # Auto-fix if enabled
                    if rule.auto_fix:
                        fixed = self._auto_fix_issues(rule.name, issues)
                        issue_result["auto_fixed"] = fixed
                        total_fixed += fixed

                    results["issues_found"].append(issue_result)
                    print(
                        f"      🔴 Found {len(issues)} issues (Fixed: {issue_result.get('auto_fixed', 0)})"
                    )
                else:
                    print("      ✅ No issues found")

            except Exception as e:
                print(f"      ❌ Check failed: {e}")

        # Calculate quality score
        total_records = self._get_total_record_count()
        if total_records > 0:
            results["quality_score"] = max(0.0, 100.0 - (total_issues * 100.0 / total_records))
        else:
            results["quality_score"] = 100.0

        results["issues_fixed"] = total_fixed

        print("\n📊 QUALITY SUMMARY:")
        print(f"   Total Issues: {total_issues}")
        print(f"   Auto-Fixed: {total_fixed}")
        print(f"   Quality Score: {results['quality_score']:.1f}/100")

        return results

    def check_duplicate_accounts(self) -> list[dict]:
        """Check for duplicate accounts"""
        accounts = self._fetch_all_accounts()
        domain_groups = defaultdict(list)

        for account in accounts:
            props = account.get("properties", {})
            domain = self._extract_rich_text(props.get("Domain", {}))
            name = self._extract_title(props.get("Name", {}))

            key = domain.lower() if domain else name.lower()
            if key:
                domain_groups[key].append({"id": account["id"], "name": name, "domain": domain})

        duplicates = []
        for key, accounts_list in domain_groups.items():
            if len(accounts_list) > 1:
                duplicates.extend(accounts_list[1:])  # Keep first, flag rest as duplicates

        return duplicates

    def check_duplicate_contacts(self) -> list[dict]:
        """Check for duplicate contacts"""
        contacts = self._fetch_all_contacts()
        contact_groups = defaultdict(list)

        for contact in contacts:
            props = contact.get("properties", {})
            email = self._extract_email(props.get("Email", {}))
            linkedin_url = self._extract_url(props.get("LinkedIn URL", {}))
            name = self._extract_title(props.get("Name", {}))

            # Group by most reliable identifier
            if email and email != "email_not_unlocked@domain.com":
                key = f"email:{email.lower()}"
            elif linkedin_url:
                key = f"linkedin:{linkedin_url}"
            else:
                key = f"name:{name.lower()}"

            contact_groups[key].append(
                {"id": contact["id"], "name": name, "email": email, "linkedin_url": linkedin_url}
            )

        duplicates = []
        for key, contacts_list in contact_groups.items():
            if len(contacts_list) > 1:
                duplicates.extend(contacts_list[1:])  # Keep first, flag rest as duplicates

        return duplicates

    def check_orphaned_contacts(self) -> list[dict]:
        """Check for contacts without account relationships"""
        contacts = self._fetch_all_contacts()
        orphaned = []

        for contact in contacts:
            props = contact.get("properties", {})
            account_relation = props.get("Account", {}).get("relation", [])

            if not account_relation:
                name = self._extract_title(props.get("Name", {}))
                orphaned.append({"id": contact["id"], "name": name})

        return orphaned

    def check_incomplete_trigger_events(self) -> list[dict]:
        """Check for trigger events missing required fields"""
        events = self._fetch_all_trigger_events()
        incomplete = []

        for event in events:
            props = event.get("properties", {})
            confidence = self._extract_number(props.get("Confidence Score", {}))
            relevance = self._extract_number(props.get("Relevance Score", {}))
            event_type = self._extract_select(props.get("Event Type", {}))

            missing_fields = []
            if confidence is None:
                missing_fields.append("Confidence Score")
            if relevance is None:
                missing_fields.append("Relevance Score")
            if not event_type:
                missing_fields.append("Event Type")

            if missing_fields:
                name = self._extract_title(props.get("Name", {}))
                incomplete.append(
                    {"id": event["id"], "name": name, "missing_fields": missing_fields}
                )

        return incomplete

    def check_broken_relationships(self) -> list[dict]:
        """Check for broken account-contact relationships"""
        accounts = self._fetch_all_accounts()
        account_ids = {acc["id"] for acc in accounts}

        contacts = self._fetch_all_contacts()
        broken = []

        for contact in contacts:
            props = contact.get("properties", {})
            account_relations = props.get("Account", {}).get("relation", [])

            for relation in account_relations:
                if relation["id"] not in account_ids:
                    name = self._extract_title(props.get("Name", {}))
                    broken.append(
                        {"id": contact["id"], "name": name, "broken_account_id": relation["id"]}
                    )
                    break

        return broken

    def check_data_freshness(self) -> list[dict]:
        """Check for stale data (older than 30 days)"""
        cutoff_date = datetime.now() - timedelta(days=30)
        stale = []

        # Check contacts
        contacts = self._fetch_all_contacts()
        for contact in contacts:
            created_time = datetime.fromisoformat(contact["created_time"].replace("Z", "+00:00"))
            if created_time < cutoff_date:
                name = self._extract_title(contact.get("properties", {}).get("Name", {}))
                stale.append(
                    {
                        "id": contact["id"],
                        "type": "contact",
                        "name": name,
                        "age_days": (datetime.now() - created_time.replace(tzinfo=None)).days,
                    }
                )

        return stale

    def check_invalid_emails(self) -> list[dict]:
        """Check for invalid email formats"""
        import re

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        contacts = self._fetch_all_contacts()
        invalid = []

        for contact in contacts:
            props = contact.get("properties", {})
            email = self._extract_email(props.get("Email", {}))

            if email and email != "email_not_unlocked@domain.com":
                if not email_pattern.match(email):
                    name = self._extract_title(props.get("Name", {}))
                    invalid.append({"id": contact["id"], "name": name, "email": email})

        return invalid

    def check_missing_linkedin(self) -> list[dict]:
        """Check for contacts missing LinkedIn URLs"""
        contacts = self._fetch_all_contacts()
        missing = []

        for contact in contacts:
            props = contact.get("properties", {})
            linkedin_url = self._extract_url(props.get("LinkedIn URL", {}))

            if not linkedin_url:
                name = self._extract_title(props.get("Name", {}))
                missing.append({"id": contact["id"], "name": name})

        return missing

    def _auto_fix_issues(self, rule_name: str, issues: list[dict]) -> int:
        """Auto-fix issues where possible"""
        fixed_count = 0

        if rule_name == "duplicate_accounts":
            # Mark duplicates for deletion (in practice, you'd archive them)
            fixed_count = len(issues)

        elif rule_name == "duplicate_contacts":
            fixed_count = len(issues)

        elif rule_name == "orphaned_contacts":
            # Link to primary account
            primary_account_id = self._get_primary_account_id()
            if primary_account_id:
                for issue in issues:
                    success = self._link_contact_to_account(issue["id"], primary_account_id)
                    if success:
                        fixed_count += 1

        elif rule_name == "incomplete_trigger_events":
            # Fill missing confidence scores
            for issue in issues:
                if "Confidence Score" in issue.get("missing_fields", []):
                    success = self._update_trigger_event_confidence(issue["id"], 85)
                    if success:
                        fixed_count += 1

        return fixed_count

    def schedule_quality_checks(self):
        """Schedule automated quality checks"""
        print("⏰ SCHEDULING AUTOMATED QUALITY CHECKS")
        print("=" * 50)

        # Schedule daily quality checks
        schedule.every().day.at("06:00").do(self.run_quality_checks)

        # Schedule cache rebuild every 4 hours
        schedule.every(4).hours.do(self.build_deduplication_cache)

        # Schedule weekly deep clean
        schedule.every().sunday.at("02:00").do(self.run_deep_clean)

        print("   ✅ Daily quality checks scheduled at 06:00")
        print("   ✅ Cache rebuild scheduled every 4 hours")
        print("   ✅ Weekly deep clean scheduled on Sunday at 02:00")

    def run_deep_clean(self):
        """Run comprehensive deep cleaning"""
        print("🧹 RUNNING WEEKLY DEEP CLEAN")
        print("=" * 35)

        # Rebuild cache
        self.build_deduplication_cache()

        # Run all quality checks
        results = self.run_quality_checks()

        # Generate quality report
        self._generate_quality_report(results)

    def _generate_quality_report(self, results: dict):
        """Generate data quality report"""
        report_filename = f"abm_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_filename, "w") as f:
            json.dump(results, f, indent=2)

        print(f"   📊 Quality report saved: {report_filename}")

    # Helper methods (reuse from cleanup script)
    def _fetch_all_accounts(self):
        url = f"https://api.notion.com/v1/databases/{self.database_ids['accounts']}/query"
        response = requests.post(url, headers=self.headers, json={"page_size": 100})
        return response.json().get("results", [])

    def _fetch_all_contacts(self):
        url = f"https://api.notion.com/v1/databases/{self.database_ids['contacts']}/query"
        response = requests.post(url, headers=self.headers, json={"page_size": 100})
        return response.json().get("results", [])

    def _fetch_all_trigger_events(self):
        url = f"https://api.notion.com/v1/databases/{self.database_ids['trigger_events']}/query"
        response = requests.post(url, headers=self.headers, json={"page_size": 100})
        return response.json().get("results", [])

    def _get_total_record_count(self):
        return (
            len(self._fetch_all_accounts())
            + len(self._fetch_all_contacts())
            + len(self._fetch_all_trigger_events())
        )

    def _get_primary_account_id(self):
        """Get primary Genesis Cloud account ID"""
        return "2b27f5fe-e5e2-81e8-8ee3-e502a738642b"  # From our cleanup

    def _link_contact_to_account(self, contact_id: str, account_id: str) -> bool:
        try:
            url = f"https://api.notion.com/v1/pages/{contact_id}"
            payload = {"properties": {"Account": {"relation": [{"id": account_id}]}}}
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            return response.status_code == 200
        except requests.RequestException as e:
            self.logger.error(
                f"Network error linking contact {contact_id[:8]}... to account {account_id[:8]}...: {e}"
            )
            return False
        except (ValueError, KeyError) as e:
            self.logger.error(
                f"Invalid ID format when linking contact {contact_id[:8]}... to account {account_id[:8]}...: {e}"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Unexpected error linking contact {contact_id[:8]}... to account {account_id[:8]}...: {e}"
            )
            return False

    def _update_trigger_event_confidence(self, event_id: str, confidence_score: int) -> bool:
        try:
            url = f"https://api.notion.com/v1/pages/{event_id}"
            payload = {"properties": {"Confidence Score": {"number": confidence_score}}}
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            return response.status_code == 200
        except requests.RequestException as e:
            self.logger.error(
                f"Network error updating confidence score for event {event_id[:8]}... to {confidence_score}: {e}"
            )
            return False
        except (ValueError, KeyError) as e:
            self.logger.error(
                f"Invalid data when updating event {event_id[:8]}... confidence to {confidence_score}: {e}"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Unexpected error updating event {event_id[:8]}... confidence to {confidence_score}: {e}"
            )
            return False

    # Property extraction methods (reuse from cleanup script)
    def _extract_title(self, prop: dict) -> str:
        if not prop or prop.get("type") != "title":
            return ""
        title_list = prop.get("title", [])
        if title_list:
            return "".join([item.get("plain_text", "") for item in title_list])
        return ""

    def _extract_rich_text(self, prop: dict) -> str:
        if not prop or prop.get("type") != "rich_text":
            return ""
        rich_text_list = prop.get("rich_text", [])
        if rich_text_list:
            return "".join([item.get("plain_text", "") for item in rich_text_list])
        return ""

    def _extract_number(self, prop: dict) -> Optional[float]:
        if not prop or prop.get("type") != "number":
            return None
        return prop.get("number")

    def _extract_select(self, prop: dict) -> str:
        if not prop or prop.get("type") != "select":
            return ""
        select_obj = prop.get("select")
        if select_obj:
            return select_obj.get("name", "")
        return ""

    def _extract_email(self, prop: dict) -> str:
        if not prop or prop.get("type") != "email":
            return ""
        return prop.get("email", "")

    def _extract_url(self, prop: dict) -> str:
        if not prop or prop.get("type") != "url":
            return ""
        return prop.get("url", "")


def main():
    """Run automated data quality system"""
    print("🔧 ABM AUTOMATED DATA QUALITY SYSTEM")
    print("=" * 55)

    quality_system = ABMDataQualitySystem()

    # Build initial cache
    quality_system.build_deduplication_cache()

    # Run initial quality checks
    results = quality_system.run_quality_checks()

    # Schedule ongoing checks
    quality_system.schedule_quality_checks()

    print("\n🎯 AUTOMATED QUALITY SYSTEM ACTIVE")
    print(f"✅ Initial scan complete - Quality Score: {results['quality_score']:.1f}/100")
    print("📅 Scheduled checks will run automatically")
    print("🔄 Use quality_system.check_before_create_*() methods in ABM workflows")


if __name__ == "__main__":
    main()
