#!/usr/bin/env python3
"""
Data Conflict Resolution Engine for ABM Research System

Intelligently merges contact data from multiple sources (Apollo, LinkedIn, manual)
while maintaining data provenance and quality scoring.

Key Features:
- Conflict detection between data sources
- Source confidence scoring (Apollo structured > LinkedIn inferred)
- Smart merging rules prioritizing data quality
- Complete audit trail of all data source conflicts
- Notion-compatible field tracking

Usage:
    resolver = DataConflictResolver()
    merged_contact = resolver.resolve_contact_conflicts(apollo_data, linkedin_data)
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Supported data sources with confidence rankings"""
    APOLLO = "apollo"           # Highest confidence - structured API data
    LINKEDIN = "linkedin"       # Medium confidence - profile inference
    MANUAL = "manual"          # High confidence - human verified
    INFERRED = "inferred"      # Low confidence - algorithm generated
    MERGED = "merged"          # Combination of multiple sources


class FieldType(Enum):
    """Types of contact fields for different merge strategies"""
    IDENTIFIER = "identifier"   # email, linkedin_url - prefer most reliable
    PERSONAL = "personal"      # name, title - prefer most complete
    CONTACT = "contact"        # phone, address - prefer structured data
    METADATA = "metadata"      # scores, dates - use latest/highest quality


@dataclass
class DataConflict:
    """Records a conflict between data sources"""
    field_name: str
    apollo_value: Any
    linkedin_value: Any
    chosen_value: Any
    chosen_source: str
    resolution_reason: str
    conflict_severity: str  # "low", "medium", "high"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class MergeResult:
    """Result of merging contact data from multiple sources"""
    merged_contact: Dict[str, Any]
    conflicts_detected: List[DataConflict]
    data_quality_score: float
    source_summary: Dict[str, int]  # Count of fields from each source
    merge_notes: List[str]


class DataConflictResolver:
    """
    Intelligent data conflict resolution for multi-source contact enrichment

    Prioritizes data quality while maintaining complete audit trails
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Source confidence scoring (higher = more reliable)
        self.source_confidence = {
            DataSource.APOLLO: 85,      # Structured API data
            DataSource.MANUAL: 80,      # Human verified
            DataSource.LINKEDIN: 70,    # Profile inference
            DataSource.INFERRED: 40,    # Algorithm generated
            DataSource.MERGED: 75       # Intelligent combination
        }

        # Field-specific merge strategies
        self.field_strategies = {
            # Contact identifiers - prioritize reliability
            "email": self._merge_email_field,
            "phone": self._merge_phone_field,
            "linkedin_url": self._merge_url_field,

            # Personal information - prioritize completeness
            "name": self._merge_name_field,
            "title": self._merge_title_field,

            # Scores and metadata - use highest quality
            "lead_score": self._merge_score_field,
            "icp_fit_score": self._merge_score_field,
        }

        # Email validation patterns
        self.email_patterns = {
            "valid": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            "placeholder": re.compile(r'(email_not_unlocked|noemail|placeholder)'),
            "generic": re.compile(r'(info|contact|admin|support|sales)@')
        }

    def resolve_contact_conflicts(self, apollo_data: Dict, linkedin_data: Dict,
                                existing_data: Optional[Dict] = None) -> MergeResult:
        """
        Main entry point for resolving conflicts between contact data sources

        Args:
            apollo_data: Contact data from Apollo API
            linkedin_data: Contact data from LinkedIn enrichment
            existing_data: Previously stored data (optional)

        Returns:
            MergeResult with merged contact and conflict details
        """
        self.logger.info("🔍 Resolving contact data conflicts...")

        conflicts = []
        merge_notes = []
        source_counts = {source.value: 0 for source in DataSource}

        # Start with Apollo data as base (highest confidence for structured data)
        merged_contact = apollo_data.copy() if apollo_data else {}

        # Track data sources for each field
        field_sources = {}
        for field in merged_contact.keys():
            field_sources[field] = DataSource.APOLLO.value
            source_counts[DataSource.APOLLO.value] += 1

        # Process LinkedIn data
        if linkedin_data:
            for field, linkedin_value in linkedin_data.items():
                if field in merged_contact:
                    # Potential conflict - check if values differ
                    apollo_value = merged_contact[field]

                    if self._values_differ(apollo_value, linkedin_value):
                        # Resolve conflict using field-specific strategy
                        resolved_value, chosen_source, reason = self._resolve_field_conflict(
                            field, apollo_value, linkedin_value, DataSource.APOLLO, DataSource.LINKEDIN
                        )

                        # Record conflict
                        conflict = DataConflict(
                            field_name=field,
                            apollo_value=apollo_value,
                            linkedin_value=linkedin_value,
                            chosen_value=resolved_value,
                            chosen_source=chosen_source.value,
                            resolution_reason=reason,
                            conflict_severity=self._assess_conflict_severity(field, apollo_value, linkedin_value)
                        )
                        conflicts.append(conflict)

                        # Update contact with resolved value
                        merged_contact[field] = resolved_value
                        field_sources[field] = chosen_source.value

                        # Update source counts
                        if chosen_source != DataSource.APOLLO:
                            source_counts[DataSource.APOLLO.value] -= 1
                            source_counts[chosen_source.value] += 1

                        self.logger.debug(f"⚡ Conflict in {field}: chose {chosen_source.value} - {reason}")

                else:
                    # No conflict - LinkedIn provides additional data
                    merged_contact[field] = linkedin_value
                    field_sources[field] = DataSource.LINKEDIN.value
                    source_counts[DataSource.LINKEDIN.value] += 1

        # Add data provenance fields
        merged_contact.update(self._add_provenance_fields(field_sources))

        # Calculate overall data quality score
        quality_score = self._calculate_data_quality_score(merged_contact, source_counts, conflicts)

        # Add enrichment timestamp
        merged_contact["last_enriched"] = datetime.now().strftime("%Y-%m-%d")

        # Generate summary notes
        if conflicts:
            merge_notes.append(f"Resolved {len(conflicts)} data conflicts")
            high_severity = [c for c in conflicts if c.conflict_severity == "high"]
            if high_severity:
                merge_notes.append(f"⚠️ {len(high_severity)} high-priority conflicts detected")
        else:
            merge_notes.append("No conflicts detected - clean merge")

        result = MergeResult(
            merged_contact=merged_contact,
            conflicts_detected=conflicts,
            data_quality_score=quality_score,
            source_summary=source_counts,
            merge_notes=merge_notes
        )

        self.logger.info(f"✅ Merge complete: {len(conflicts)} conflicts, {quality_score:.1f} quality score")
        return result

    def _values_differ(self, value1: Any, value2: Any) -> bool:
        """Check if two values represent different information"""
        if value1 is None or value2 is None:
            return False

        # Convert to strings for comparison
        str1 = str(value1).strip().lower()
        str2 = str(value2).strip().lower()

        # Consider empty/placeholder values as non-conflicting
        if not str1 or not str2:
            return False

        # Normalize common variations
        str1 = re.sub(r'\s+', ' ', str1)
        str2 = re.sub(r'\s+', ' ', str2)

        return str1 != str2

    def _resolve_field_conflict(self, field_name: str, apollo_value: Any, linkedin_value: Any,
                              apollo_source: DataSource, linkedin_source: DataSource) -> Tuple[Any, DataSource, str]:
        """Resolve conflict for a specific field using field-specific strategy"""

        # Use field-specific strategy if available
        if field_name in self.field_strategies:
            return self.field_strategies[field_name](apollo_value, linkedin_value, apollo_source, linkedin_source)

        # Default strategy: prefer source with higher confidence
        if self.source_confidence[apollo_source] > self.source_confidence[linkedin_source]:
            return apollo_value, apollo_source, f"Apollo has higher confidence ({self.source_confidence[apollo_source]})"
        else:
            return linkedin_value, linkedin_source, f"LinkedIn has higher confidence ({self.source_confidence[linkedin_source]})"

    def _merge_email_field(self, apollo_val: Any, linkedin_val: Any,
                         apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """Email-specific merge strategy prioritizing deliverability"""

        apollo_email = str(apollo_val).strip() if apollo_val else ""
        linkedin_email = str(linkedin_val).strip() if linkedin_val else ""

        # Check for placeholder/invalid emails
        if self.email_patterns["placeholder"].search(apollo_email.lower()):
            return linkedin_val, linkedin_src, "Apollo email is placeholder"

        if self.email_patterns["placeholder"].search(linkedin_email.lower()):
            return apollo_val, apollo_src, "LinkedIn email is placeholder"

        # Prefer structured Apollo data for valid emails
        if self.email_patterns["valid"].match(apollo_email):
            if not self.email_patterns["valid"].match(linkedin_email):
                return apollo_val, apollo_src, "Apollo email is valid, LinkedIn is not"

            # Both valid - prefer Apollo (structured API data)
            return apollo_val, apollo_src, "Both valid, prefer Apollo structured data"

        # Apollo invalid but LinkedIn valid
        if self.email_patterns["valid"].match(linkedin_email):
            return linkedin_val, linkedin_src, "LinkedIn email is valid, Apollo is not"

        # Neither valid - keep Apollo as default
        return apollo_val, apollo_src, "Neither email valid, keeping Apollo"

    def _merge_name_field(self, apollo_val: Any, linkedin_val: Any,
                        apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """Name-specific merge strategy prioritizing completeness"""

        apollo_name = str(apollo_val).strip() if apollo_val else ""
        linkedin_name = str(linkedin_val).strip() if linkedin_val else ""

        # Prefer longer, more complete names
        if len(linkedin_name) > len(apollo_name) + 3:  # Significantly longer
            return linkedin_val, linkedin_src, "LinkedIn name more complete"

        if len(apollo_name) > len(linkedin_name) + 3:  # Significantly longer
            return apollo_val, apollo_src, "Apollo name more complete"

        # Similar length - prefer Apollo structured data
        return apollo_val, apollo_src, "Similar length, prefer Apollo structure"

    def _merge_title_field(self, apollo_val: Any, linkedin_val: Any,
                         apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """Title-specific merge strategy balancing structure and detail"""

        apollo_title = str(apollo_val).strip() if apollo_val else ""
        linkedin_title = str(linkedin_val).strip() if linkedin_val else ""

        # Check for generic Apollo titles
        generic_patterns = ["manager", "engineer", "director"]  # Very broad titles
        apollo_generic = any(pattern in apollo_title.lower() for pattern in generic_patterns)

        # If Apollo is generic but LinkedIn is specific, prefer LinkedIn
        if apollo_generic and len(linkedin_title) > len(apollo_title):
            return linkedin_val, linkedin_src, "LinkedIn title more specific than Apollo generic"

        # Otherwise prefer Apollo structured data
        return apollo_val, apollo_src, "Apollo structured title preferred"

    def _merge_phone_field(self, apollo_val: Any, linkedin_val: Any,
                         apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """Phone-specific merge strategy prioritizing format and validity"""

        # Always prefer Apollo for phone numbers (structured API data)
        return apollo_val, apollo_src, "Apollo phone data more reliable"

    def _merge_url_field(self, apollo_val: Any, linkedin_val: Any,
                       apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """URL-specific merge strategy"""

        # For LinkedIn URLs, both sources should be similar
        # Prefer the more complete/formatted version
        apollo_url = str(apollo_val).strip() if apollo_val else ""
        linkedin_url = str(linkedin_val).strip() if linkedin_val else ""

        # Prefer https and full URLs
        if linkedin_url.startswith("https://") and not apollo_url.startswith("https://"):
            return linkedin_val, linkedin_src, "LinkedIn URL has https"

        if apollo_url.startswith("https://") and not linkedin_url.startswith("https://"):
            return apollo_val, apollo_src, "Apollo URL has https"

        # Default to Apollo
        return apollo_val, apollo_src, "Apollo URL preferred"

    def _merge_score_field(self, apollo_val: Any, linkedin_val: Any,
                         apollo_src: DataSource, linkedin_src: DataSource) -> Tuple[Any, DataSource, str]:
        """Score-specific merge strategy using highest value"""

        try:
            apollo_score = float(apollo_val) if apollo_val else 0
            linkedin_score = float(linkedin_val) if linkedin_val else 0

            # Use highest score (more optimistic for sales engagement)
            if linkedin_score > apollo_score:
                return linkedin_val, linkedin_src, "LinkedIn score higher"
            else:
                return apollo_val, apollo_src, "Apollo score higher or equal"

        except (ValueError, TypeError):
            # Non-numeric scores - prefer Apollo
            return apollo_val, apollo_src, "Non-numeric scores, prefer Apollo"

    def _assess_conflict_severity(self, field_name: str, apollo_val: Any, linkedin_val: Any) -> str:
        """Assess the severity of a data conflict"""

        # High severity conflicts (impact deliverability/contact)
        high_severity_fields = ["email", "phone", "linkedin_url"]
        if field_name in high_severity_fields:
            return "high"

        # Medium severity conflicts (impact personalization)
        medium_severity_fields = ["name", "title", "company"]
        if field_name in medium_severity_fields:
            return "medium"

        # Low severity conflicts (minor differences)
        return "low"

    def _add_provenance_fields(self, field_sources: Dict[str, str]) -> Dict[str, str]:
        """Add enhanced data provenance fields for schema compliance"""

        provenance = {}

        # Enhanced provenance tracking for all key fields
        key_fields = {
            "name": "Name Source",
            "email": "Email Source",
            "title": "Title Source",
            "phone": "Phone Source",
            "linkedin_url": "LinkedIn Source"
        }

        for field_name, notion_field in key_fields.items():
            if field_name in field_sources:
                provenance[notion_field] = field_sources[field_name]
            else:
                provenance[notion_field] = "not_found"

        # Add additional enhanced schema fields
        provenance["Last Enriched"] = datetime.now().isoformat()
        provenance["Enrichment Status"] = "multi_source_resolved"

        return provenance

    def _calculate_data_quality_score(self, contact: Dict, source_counts: Dict,
                                    conflicts: List[DataConflict]) -> float:
        """Calculate overall data quality score for the merged contact"""

        score = 0.0

        # Base score from data completeness
        total_fields = len(contact)
        filled_fields = sum(1 for v in contact.values() if v not in [None, "", 0])
        completeness_score = (filled_fields / max(total_fields, 1)) * 40
        score += completeness_score

        # Source quality bonus (weighted by source confidence)
        total_source_score = sum(
            count * self.source_confidence.get(DataSource(source), 50)
            for source, count in source_counts.items()
            if count > 0
        )
        total_fields_with_sources = sum(source_counts.values())
        if total_fields_with_sources > 0:
            avg_source_confidence = total_source_score / total_fields_with_sources
            score += (avg_source_confidence / 100) * 35  # Max 35 points

        # Conflict penalty (high severity conflicts penalized more)
        conflict_penalty = 0
        for conflict in conflicts:
            if conflict.conflict_severity == "high":
                conflict_penalty += 5
            elif conflict.conflict_severity == "medium":
                conflict_penalty += 3
            else:
                conflict_penalty += 1

        score = max(score - conflict_penalty, 0)

        # Bonus for critical fields
        critical_fields = ["email", "name", "title", "linkedin_url"]
        critical_present = sum(1 for field in critical_fields if contact.get(field))
        score += (critical_present / len(critical_fields)) * 25

        return min(score, 100.0)  # Cap at 100

    def log_conflicts_summary(self, result: MergeResult) -> None:
        """Log a summary of conflicts for debugging and monitoring"""

        if not result.conflicts_detected:
            self.logger.info("✅ No data conflicts detected")
            return

        self.logger.info(f"⚠️  Detected {len(result.conflicts_detected)} data conflicts:")

        for conflict in result.conflicts_detected:
            self.logger.info(
                f"  - {conflict.field_name}: {conflict.chosen_source} "
                f"({conflict.conflict_severity}) - {conflict.resolution_reason}"
            )

        # Source distribution
        source_summary = ", ".join([
            f"{source}: {count}"
            for source, count in result.source_summary.items()
            if count > 0
        ])
        self.logger.info(f"📊 Data sources: {source_summary}")
        self.logger.info(f"🎯 Final quality score: {result.data_quality_score:.1f}/100")


# Export singleton instance for easy importing
data_conflict_resolver = DataConflictResolver()