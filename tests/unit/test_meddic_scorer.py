"""
Unit tests for MEDDIC Contact Scorer.

Tests the scoring logic that classifies contacts into role tiers
and calculates champion potential, role fit, and engagement scores.

Run with: pytest tests/unit/test_meddic_scorer.py -v
"""

import pytest

from abm_research.core.unified_lead_scorer import (
    MEDDICContactScore,
    MEDDICContactScorer,
    meddic_contact_scorer,
)


class TestRoleTierClassification:
    """Tests for role tier classification logic."""

    def test_vp_infrastructure_is_economic_buyer(self):
        """VP Infrastructure should be classified as economic_buyer tier."""
        contact = {"title": "VP of Infrastructure", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "economic_buyer"
        assert "VP" in result.role_classification

    def test_vp_operations_is_economic_buyer(self):
        """VP Operations should be classified as economic_buyer tier."""
        contact = {"title": "VP, Data Center Operations", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "economic_buyer"

    def test_cio_is_economic_buyer(self):
        """CIO should be classified as economic_buyer tier."""
        contact = {"title": "Chief Information Officer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "economic_buyer"
        assert "C-Suite" in result.role_classification

    def test_cto_is_economic_buyer(self):
        """CTO should be classified as economic_buyer tier."""
        contact = {"title": "CTO", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "economic_buyer"

    def test_sre_is_entry_point(self):
        """SRE should be classified as entry_point tier (Technical Believer)."""
        contact = {"title": "Site Reliability Engineer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "entry_point"
        assert "SRE" in result.role_classification

    def test_infrastructure_engineer_is_entry_point(self):
        """Infrastructure Engineer should be entry_point tier."""
        contact = {"title": "Infrastructure Engineer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "entry_point"

    def test_facilities_manager_is_entry_point(self):
        """Facilities Manager should be entry_point tier."""
        contact = {"title": "Facilities Manager", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "entry_point"

    def test_capacity_engineer_is_entry_point(self):
        """Capacity Engineer should be entry_point tier."""
        contact = {"title": "Capacity & Energy Engineer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "entry_point"

    def test_director_infrastructure_is_middle_decider(self):
        """Director of Infrastructure should be middle_decider tier."""
        contact = {"title": "Director, Infrastructure Engineering", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "middle_decider"
        assert "Director" in result.role_classification

    def test_sre_manager_is_middle_decider(self):
        """SRE Manager should be middle_decider tier (not entry_point)."""
        contact = {"title": "SRE Manager", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.role_tier == "middle_decider"


class TestScoreBreakdown:
    """Tests for score breakdown structure and values."""

    def test_score_breakdown_structure(self):
        """MEDDIC result must include all required breakdown fields."""
        contact = {"title": "SRE", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        # Check all required attributes exist
        assert hasattr(result, "total_score")
        assert hasattr(result, "champion_potential_score")
        assert hasattr(result, "role_fit_score")
        assert hasattr(result, "engagement_potential_score")
        assert hasattr(result, "role_tier")
        assert hasattr(result, "role_classification")
        assert hasattr(result, "champion_potential_level")
        assert hasattr(result, "why_prioritize")
        assert hasattr(result, "recommended_approach")

    def test_get_score_breakdown_returns_dict(self):
        """get_score_breakdown() should return a properly structured dict."""
        contact = {"title": "VP of Infrastructure", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)
        breakdown = result.get_score_breakdown()

        assert isinstance(breakdown, dict)
        assert "total_score" in breakdown
        assert "champion_potential" in breakdown
        assert "role_fit" in breakdown
        assert "engagement_potential" in breakdown

        # Check nested structure
        assert "score" in breakdown["champion_potential"]
        assert "weight" in breakdown["champion_potential"]
        assert "score" in breakdown["role_fit"]
        assert "tier" in breakdown["role_fit"]
        assert "score" in breakdown["engagement_potential"]

    def test_scores_are_within_valid_range(self):
        """All scores should be between 0 and 100."""
        test_titles = [
            "VP of Infrastructure",
            "SRE",
            "Director, Operations",
            "Software Engineer",
            "Intern",
            "",
        ]

        for title in test_titles:
            contact = {"title": title, "name": "Test User"}
            result = meddic_contact_scorer.calculate_contact_score(contact)

            assert 0 <= result.total_score <= 100, f"total_score out of range for '{title}'"
            assert (
                0 <= result.champion_potential_score <= 100
            ), f"champion_potential_score out of range for '{title}'"
            assert 0 <= result.role_fit_score <= 100, f"role_fit_score out of range for '{title}'"
            assert (
                0 <= result.engagement_potential_score <= 100
            ), f"engagement_potential_score out of range for '{title}'"


class TestChampionPotentialLevels:
    """Tests for champion potential level assignment."""

    def test_entry_point_has_high_champion_potential(self):
        """Entry point roles should have High or Very High champion potential."""
        contact = {"title": "Site Reliability Engineer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result.champion_potential_level in ["High", "Very High"]

    def test_economic_buyer_has_lower_champion_potential(self):
        """Economic buyers should have lower champion potential (engage via champion)."""
        contact = {"title": "CIO", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        # Economic buyers are engaged via champion, not as champions
        assert result.champion_potential_level in ["Low", "Medium"]

    def test_valid_champion_levels(self):
        """Champion level should be one of the valid values."""
        valid_levels = ["Very High", "High", "Medium", "Low"]

        test_titles = ["VP", "SRE", "Director", "Manager", "Engineer", ""]
        for title in test_titles:
            contact = {"title": title, "name": "Test User"}
            result = meddic_contact_scorer.calculate_contact_score(contact)
            assert result.champion_potential_level in valid_levels


class TestRecommendedApproach:
    """Tests for recommended engagement approach."""

    def test_entry_point_gets_pain_based_approach(self):
        """Entry points should get pain-based outreach recommendation."""
        contact = {"title": "SRE", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert (
            "pain" in result.recommended_approach.lower() or "Pain" in result.recommended_approach
        )

    def test_economic_buyer_gets_champion_referral_approach(self):
        """Economic buyers should be approached via champion referral."""
        contact = {"title": "VP of Infrastructure", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert "champion" in result.recommended_approach.lower()


class TestWhyPrioritize:
    """Tests for prioritization reasons."""

    def test_why_prioritize_is_list(self):
        """why_prioritize should be a list."""
        contact = {"title": "SRE", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert isinstance(result.why_prioritize, list)

    def test_entry_point_has_prioritization_reasons(self):
        """Entry points should have at least one prioritization reason."""
        contact = {"title": "Site Reliability Engineer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert len(result.why_prioritize) >= 1


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_empty_title(self):
        """Empty title should not crash and return valid result."""
        contact = {"title": "", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result is not None
        assert result.role_tier in ["entry_point", "middle_decider", "economic_buyer"]

    def test_missing_title(self):
        """Missing title field should not crash."""
        contact = {"name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result is not None

    def test_none_contact(self):
        """Empty contact dict should not crash."""
        contact = {}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        assert result is not None

    def test_unusual_title(self):
        """Unusual titles should be handled gracefully."""
        contact = {"title": "Chief Happiness Officer", "name": "Test User"}
        result = meddic_contact_scorer.calculate_contact_score(contact)

        # Should still produce valid output
        assert result is not None
        assert 0 <= result.total_score <= 100


class TestScorerSingleton:
    """Tests for the module-level scorer instance."""

    def test_meddic_contact_scorer_exists(self):
        """Module should export meddic_contact_scorer singleton."""
        assert meddic_contact_scorer is not None
        assert isinstance(meddic_contact_scorer, MEDDICContactScorer)

    def test_scorer_is_consistent(self):
        """Same input should produce same output."""
        contact = {"title": "SRE", "name": "Test User"}

        result1 = meddic_contact_scorer.calculate_contact_score(contact)
        result2 = meddic_contact_scorer.calculate_contact_score(contact)

        assert result1.total_score == result2.total_score
        assert result1.role_tier == result2.role_tier
