#!/usr/bin/env python3
"""
Schema Validation Framework

Comprehensive validation system for the enhanced ABM schema ensuring:
- Proper account relations
- Confidence indicators
- Field purpose separation
- Clean naming conventions
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Comprehensive schema validator for enhanced ABM system
    """

    def __init__(self):
        """Initialize schema validator with enhanced schema requirements"""

        # Define enhanced schema structure
        self.enhanced_schema = {
            "account": {
                "required_fields": ["name", "domain"],
                "strategic_intelligence_fields": [
                    "Physical Infrastructure",
                    "Recent Leadership Changes",
                    "Recent Funding",
                    "Growth Stage",
                    "Hiring Velocity",
                    "Key Decision Makers",
                    "Competitor Tools",
                    "Recent Announcements",
                    "Conversation Triggers",
                ],
                "confidence_required_fields": [
                    "Physical Infrastructure",
                    "Recent Funding",
                    "Key Decision Makers",
                    "Competitor Tools",
                ],
            },
            "contact": {
                "required_fields": ["name", "email"],
                "relation_fields": ["account_id"],  # Must have account relation
                "data_provenance_fields": [
                    "name_source",
                    "email_source",
                    "title_source",
                    "data_quality_score",
                ],
                "enhanced_fields": [
                    "Name Source",
                    "Email Source",
                    "Title Source",
                    "Data Quality Score",
                    "Last Enriched",
                    "Engagement Level",
                ],
            },
            "trigger_event": {
                "required_fields": ["description", "event_type"],
                "relation_fields": ["account_id"],  # Must have account relation
                "tactical_intelligence_fields": [
                    "Follow-up Actions",
                    "Action Deadline",
                    "Peak Relevance Window",
                    "Urgency Level",
                ],
                "scoring_fields": [
                    "Business Impact Score",
                    "Actionability Score",
                    "Timing Urgency Score",
                    "Strategic Fit Score",
                ],
                "time_intelligence_fields": [
                    "Action Deadline",
                    "Peak Relevance Window",
                    "Decay Rate",
                    "Event Stage",
                ],
            },
            "partnership": {
                "required_fields": ["account_name", "partnership_type"],
                "strategic_intelligence_fields": [
                    "Relationship Depth",
                    "Partnership Maturity",
                    "Warm Introduction Path",
                    "Common Partners",
                    "Best Approach",
                    "Decision Timeline",
                    "Success Metrics",
                    "Recommended Next Steps",
                ],
            },
        }

        # Confidence indicator patterns
        self.confidence_patterns = {
            "explicit_confidence": re.compile(r"\((\d+)%\s*confidence\)", re.IGNORECASE),
            "not_found": re.compile(r"not found.*\(.*confidence.*\)", re.IGNORECASE),
            "not_searched": re.compile(r"(n/a|not searched|not attempted)", re.IGNORECASE),
            "high_confidence_terms": ["verified", "confirmed", "validated"],
            "low_confidence_terms": ["likely", "appears", "seems", "possibly"],
        }

    def validate_account_data(self, account_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate account data against enhanced schema

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check required fields
        for field in self.enhanced_schema["account"]["required_fields"]:
            if not account_data.get(field):
                issues.append(f"Missing required field: {field}")

        # Validate clean naming (no test suffixes)
        name = account_data.get("name", "")
        if self._has_test_suffix(name):
            issues.append(f"Account name has test suffix: {name}")

        # Validate strategic intelligence fields have appropriate content
        for field in self.enhanced_schema["account"]["strategic_intelligence_fields"]:
            value = account_data.get(field, "")
            if value and not self._is_strategic_content(value):
                issues.append(f"Field '{field}' contains tactical rather than strategic content")

        # Validate confidence indicators in required fields
        for field in self.enhanced_schema["account"]["confidence_required_fields"]:
            value = account_data.get(field, "")
            if value and not self._has_confidence_indicator(value):
                issues.append(
                    f"Field '{field}' missing confidence indicator (use 'confidence%', 'not found (searched)', or 'N/A - not searched')"
                )

        # Validate ICP fit score is reasonable
        icp_score = account_data.get("icp_fit_score", 0)
        if not isinstance(icp_score, (int, float)) or icp_score < 0 or icp_score > 100:
            issues.append(f"ICP fit score must be between 0-100, got: {icp_score}")

        return len(issues) == 0, issues

    def validate_contact_data(
        self, contact_data: Dict[str, Any], account_name: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Validate contact data against enhanced schema with proper account relations
        """
        issues = []

        # Check required fields
        for field in self.enhanced_schema["contact"]["required_fields"]:
            if not contact_data.get(field):
                issues.append(f"Missing required field: {field}")

        # Validate account relation (should have account_id or account_name for linking)
        if not contact_data.get("account_id") and not account_name:
            issues.append(
                "Contact missing account relation - must have account_id or account_name for proper linking"
            )

        # Validate data provenance fields
        for field in self.enhanced_schema["contact"]["data_provenance_fields"]:
            if field in contact_data:
                value = contact_data[field]
                if field.endswith("_source") and value not in [
                    "apollo",
                    "linkedin",
                    "merged",
                    "manual",
                    "inferred",
                ]:
                    issues.append(
                        f"Invalid {field} value: {value}. Must be one of: apollo, linkedin, merged, manual, inferred"
                    )
                elif field == "data_quality_score" and (
                    not isinstance(value, (int, float)) or value < 0 or value > 100
                ):
                    issues.append(f"Data quality score must be between 0-100, got: {value}")

        # Validate lead score is reasonable
        lead_score = contact_data.get("final_lead_score", contact_data.get("lead_score", 0))
        if lead_score and (not isinstance(lead_score, (int, float)) or lead_score < 0):
            issues.append(f"Lead score must be positive number, got: {lead_score}")

        # Check for proper email format
        email = contact_data.get("email", "")
        if email and "@" not in email:
            issues.append(f"Invalid email format: {email}")

        return len(issues) == 0, issues

    def validate_trigger_event_data(
        self, event_data: Dict[str, Any], account_name: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Validate trigger event data against enhanced schema with tactical intelligence focus
        """
        issues = []

        # Check required fields
        for field in self.enhanced_schema["trigger_event"]["required_fields"]:
            if not event_data.get(field):
                issues.append(f"Missing required field: {field}")

        # Validate account relation
        if not event_data.get("account_id") and not account_name:
            issues.append(
                "Trigger event missing account relation - must have account_id or account_name for proper linking"
            )

        # Validate tactical intelligence fields contain time-bound content
        for field in self.enhanced_schema["trigger_event"]["tactical_intelligence_fields"]:
            value = event_data.get(field, "")
            if value and not self._is_tactical_content(value):
                issues.append(
                    f"Field '{field}' should contain tactical, time-bound content, not strategic content"
                )

        # Validate scoring fields are within proper range
        for field in self.enhanced_schema["trigger_event"]["scoring_fields"]:
            if field in event_data:
                score = event_data[field]
                if not isinstance(score, (int, float)) or score < 0 or score > 100:
                    issues.append(f"{field} must be between 0-100, got: {score}")

        # Validate time intelligence fields
        for field in self.enhanced_schema["trigger_event"]["time_intelligence_fields"]:
            value = event_data.get(field)
            if field.endswith("_deadline") or field.endswith("_window"):
                if value and not self._is_valid_date(value):
                    issues.append(f"{field} must be valid date format, got: {value}")
            elif field == "decay_rate":
                if value and value not in ["Fast", "Medium", "Slow", "Permanent"]:
                    issues.append(
                        f"Decay Rate must be one of: Fast, Medium, Slow, Permanent, got: {value}"
                    )
            elif field == "event_stage":
                if value and value not in ["Rumored", "Announced", "In-Progress", "Completed"]:
                    issues.append(
                        f"Event Stage must be one of: Rumored, Announced, In-Progress, Completed, got: {value}"
                    )

        return len(issues) == 0, issues

    def validate_partnership_data(self, partnership_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate partnership data against enhanced schema with strategic intelligence focus
        """
        issues = []

        # Check required fields
        for field in self.enhanced_schema["partnership"]["required_fields"]:
            if not partnership_data.get(field):
                issues.append(f"Missing required field: {field}")

        # Validate strategic intelligence fields
        strategic_fields_present = sum(
            1
            for field in self.enhanced_schema["partnership"]["strategic_intelligence_fields"]
            if partnership_data.get(field)
        )
        if strategic_fields_present < 3:
            issues.append(
                f"Partnership should have at least 3 strategic intelligence fields populated, found: {strategic_fields_present}"
            )

        # Validate specific strategic intelligence field values
        relationship_depth = partnership_data.get("relationship_depth", "")
        if relationship_depth and relationship_depth not in [
            "Surface Integration",
            "Go-to-Market Alliance",
            "Strategic Investment",
            "Ecosystem Play",
        ]:
            issues.append(f"Invalid Relationship Depth: {relationship_depth}")

        partnership_maturity = partnership_data.get("partnership_maturity", "")
        if partnership_maturity and partnership_maturity not in [
            "Basic",
            "Intermediate",
            "Sophisticated",
        ]:
            issues.append(f"Invalid Partnership Maturity: {partnership_maturity}")

        best_approach = partnership_data.get("best_approach", "")
        if best_approach and best_approach not in [
            "Technical Discussion",
            "Business Development",
            "Channel Partnership",
        ]:
            issues.append(f"Invalid Best Approach: {best_approach}")

        decision_timeline = partnership_data.get("decision_timeline", "")
        if decision_timeline and decision_timeline not in [
            "Fast (weeks)",
            "Medium (months)",
            "Slow (quarters)",
        ]:
            issues.append(f"Invalid Decision Timeline: {decision_timeline}")

        return len(issues) == 0, issues

    def validate_complete_research_result(
        self, result: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete ABM research result against enhanced schema

        Returns:
            Tuple of (is_valid, dict_of_issues_by_category)
        """
        all_issues = {
            "account": [],
            "contacts": [],
            "trigger_events": [],
            "partnerships": [],
            "general": [],
        }

        # Validate account data
        account_data = result.get("account", {})
        if account_data:
            is_valid, issues = self.validate_account_data(account_data)
            all_issues["account"].extend(issues)
        else:
            all_issues["general"].append("Missing account data in research result")

        # Validate contacts
        contacts = result.get("contacts", [])
        account_name = account_data.get("name", "")
        for i, contact in enumerate(contacts):
            is_valid, issues = self.validate_contact_data(contact, account_name)
            all_issues["contacts"].extend([f"Contact {i+1}: {issue}" for issue in issues])

        # Validate trigger events
        events = result.get("trigger_events", [])
        for i, event in enumerate(events):
            is_valid, issues = self.validate_trigger_event_data(event, account_name)
            all_issues["trigger_events"].extend([f"Event {i+1}: {issue}" for issue in issues])

        # Validate partnerships
        partnerships = result.get("partnerships", [])
        for i, partnership in enumerate(partnerships):
            is_valid, issues = self.validate_partnership_data(partnership)
            all_issues["partnerships"].extend([f"Partnership {i+1}: {issue}" for issue in issues])

        # Check overall data consistency
        if account_name and len(contacts) > 0:
            # Validate contact-account consistency
            inconsistent_contacts = [
                contact.get("name", f"Contact {i+1}")
                for i, contact in enumerate(contacts)
                if "account_name" in contact and contact["account_name"] != account_name
            ]
            if inconsistent_contacts:
                all_issues["general"].append(
                    f"Contacts linked to different account than main account: {inconsistent_contacts}"
                )

        total_issues = sum(len(issues) for issues in all_issues.values())
        return total_issues == 0, all_issues

    # Helper methods
    def _has_test_suffix(self, name: str) -> bool:
        """Check if name has test suffixes like (Test), (Enhanced Test), etc."""
        test_suffixes = [
            r"\(test\)",
            r"\(enhanced test\)",
            r"\(relations test\)",
            r"\(demo\)",
            r"\(testing\)",
        ]
        name_lower = name.lower()
        return any(re.search(pattern, name_lower) for pattern in test_suffixes)

    def _has_confidence_indicator(self, value: str) -> bool:
        """Check if value has proper confidence indicator"""
        if not value or not isinstance(value, str):
            return True  # Empty values are OK

        value_lower = value.lower()

        # Check for explicit confidence percentage
        if self.confidence_patterns["explicit_confidence"].search(value):
            return True

        # Check for "not found" with confidence
        if self.confidence_patterns["not_found"].search(value):
            return True

        # Check for "N/A - not searched"
        if self.confidence_patterns["not_searched"].search(value):
            return True

        # Check for high/low confidence terms
        for term in (
            self.confidence_patterns["high_confidence_terms"]
            + self.confidence_patterns["low_confidence_terms"]
        ):
            if term in value_lower:
                return True

        return False

    def _is_strategic_content(self, value: str) -> bool:
        """Check if content is strategic (persistent/long-term) rather than tactical (time-bound)"""
        if not value or not isinstance(value, str):
            return True

        value_lower = value.lower()

        # Tactical indicators (should not be in strategic fields)
        tactical_indicators = [
            "deadline",
            "by next week",
            "urgent",
            "immediate action",
            "follow up",
            "schedule call",
            "contact by",
            "respond within",
        ]

        # If contains tactical indicators, it's not strategic
        if any(indicator in value_lower for indicator in tactical_indicators):
            return False

        return True

    def _is_tactical_content(self, value: str) -> bool:
        """Check if content is tactical (time-bound/actionable) rather than strategic (persistent)"""
        if not value or not isinstance(value, str):
            return True

        value_lower = value.lower()

        # Tactical indicators (good for tactical fields)
        tactical_indicators = [
            "action",
            "deadline",
            "follow up",
            "schedule",
            "contact",
            "next step",
            "within",
            "by",
            "urgent",
            "immediate",
            "call",
            "meeting",
            "demo",
            "proposal",
        ]

        return any(indicator in value_lower for indicator in tactical_indicators)

    def _is_valid_date(self, date_str: str) -> bool:
        """Check if string is valid date format"""
        if not date_str:
            return True  # Empty is OK

        date_formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]

        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue

        return False

    def generate_validation_report(self, result: Dict[str, Any]) -> str:
        """
        Generate comprehensive validation report for ABM research result
        """
        is_valid, issues_by_category = self.validate_complete_research_result(result)

        report = []
        report.append("📋 ENHANCED SCHEMA VALIDATION REPORT")
        report.append("=" * 50)

        if is_valid:
            report.append("✅ SCHEMA COMPLIANCE: PASSED")
            report.append("   All data conforms to enhanced ABM schema")
        else:
            total_issues = sum(len(issues) for issues in issues_by_category.values())
            report.append(f"❌ SCHEMA COMPLIANCE: FAILED ({total_issues} issues)")

        report.append("")

        # Report issues by category
        for category, issues in issues_by_category.items():
            if issues:
                category_emoji = {
                    "account": "🏢",
                    "contacts": "👥",
                    "trigger_events": "⚡",
                    "partnerships": "🤝",
                    "general": "🔍",
                }[category]

                report.append(
                    f"{category_emoji} {category.upper().replace('_', ' ')} ISSUES ({len(issues)}):"
                )
                for issue in issues[:5]:  # Show first 5 issues
                    report.append(f"   ❌ {issue}")
                if len(issues) > 5:
                    report.append(f"   ... and {len(issues) - 5} more issues")
                report.append("")

        if is_valid:
            report.append("🎯 RECOMMENDATIONS:")
            report.append("   ✅ Schema compliance achieved")
            report.append("   ✅ Data ready for production use")
            report.append("   ✅ All enhanced intelligence features operational")
        else:
            report.append("🔧 NEXT STEPS:")
            report.append("   1. Address critical schema compliance issues")
            report.append("   2. Re-run validation after fixes")
            report.append("   3. Test with production data")

        return "\n".join(report)


# Global validator instance
_schema_validator = None


def get_schema_validator() -> SchemaValidator:
    """Get global schema validator instance"""
    global _schema_validator
    if _schema_validator is None:
        _schema_validator = SchemaValidator()
    return _schema_validator


def validate_research_result(result: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to validate complete research result

    Returns:
        Tuple of (is_valid, validation_report)
    """
    validator = get_schema_validator()
    is_valid, issues = validator.validate_complete_research_result(result)
    report = validator.generate_validation_report(result)
    return is_valid, report
