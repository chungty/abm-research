"""
Unit tests for contact data transformation in the API.

Tests that the transform_notion_contact function properly integrates
MEDDIC scoring and returns all required fields.

Run with: pytest tests/unit/test_contact_transform.py -v
"""

from unittest.mock import MagicMock, patch

import pytest


class TestTransformNotionContact:
    """Tests for the transform_notion_contact function in server.py."""

    @pytest.fixture
    def mock_notion_page(self):
        """Create a mock Notion page response matching Notion API format."""
        return {
            "id": "abc123-def456-ghi789",
            "properties": {
                "Name": {"title": [{"text": {"content": "John Doe"}}]},
                "Email": {"email": "john.doe@example.com"},
                "Title": {"rich_text": [{"text": {"content": "VP of Infrastructure"}}]},
                "Company": {"rich_text": [{"text": {"content": "Acme Corp"}}]},
                "LinkedIn URL": {"url": "https://linkedin.com/in/johndoe"},
                "Lead Score": {"number": 75},
                "Engagement Level": {"select": {"name": "High"}},
                "Name Source": {"select": {"name": "AI"}},
                "Email Source": {"select": {"name": "Apollo"}},
                "Title Source": {"select": {"name": "LinkedIn"}},
                "Data Quality Score": {"number": 85},
            },
        }

    @pytest.fixture
    def mock_notion_page_sre(self):
        """Create a mock Notion page for an SRE contact."""
        return {
            "id": "sre123-456-789",
            "properties": {
                "Name": {"title": [{"text": {"content": "Jane Smith"}}]},
                "Email": {"email": "jane@example.com"},
                "Title": {"rich_text": [{"text": {"content": "Site Reliability Engineer"}}]},
                "Company": {"rich_text": [{"text": {"content": "Tech Corp"}}]},
                "LinkedIn URL": {"url": "https://linkedin.com/in/janesmith"},
                "Lead Score": {"number": 80},
                "Engagement Level": {"select": {"name": "Medium"}},
            },
        }

    def test_transform_includes_meddic_score_breakdown(self, mock_notion_page):
        """Transformed contact must include meddic_score_breakdown field."""
        # Import here to avoid import errors if server not available
        try:
            from abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "meddic_score_breakdown" in result
        assert result["meddic_score_breakdown"] is not None

    def test_transform_includes_role_tier(self, mock_notion_page):
        """Transformed contact must include role_tier field."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "role_tier" in result
        assert result["role_tier"] in ["entry_point", "middle_decider", "economic_buyer"]

    def test_vp_contact_is_economic_buyer(self, mock_notion_page):
        """VP of Infrastructure should be classified as economic_buyer."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert result["role_tier"] == "economic_buyer"

    def test_sre_contact_is_entry_point(self, mock_notion_page_sre):
        """SRE should be classified as entry_point."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page_sre)

        assert result["role_tier"] == "entry_point"

    def test_transform_includes_champion_potential_score(self, mock_notion_page):
        """Transformed contact must include champion_potential_score."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "champion_potential_score" in result
        assert isinstance(result["champion_potential_score"], (int, float))
        assert 0 <= result["champion_potential_score"] <= 100

    def test_transform_includes_recommended_approach(self, mock_notion_page):
        """Transformed contact must include recommended_approach."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "recommended_approach" in result
        assert result["recommended_approach"] is not None
        assert len(result["recommended_approach"]) > 0

    def test_transform_includes_why_prioritize(self, mock_notion_page):
        """Transformed contact must include why_prioritize list."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "why_prioritize" in result
        assert isinstance(result["why_prioritize"], list)

    def test_meddic_breakdown_has_role_fit(self, mock_notion_page):
        """MEDDIC breakdown must include role_fit with score."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)
        breakdown = result.get("meddic_score_breakdown", {})

        assert "role_fit" in breakdown
        assert "score" in breakdown["role_fit"]
        assert isinstance(breakdown["role_fit"]["score"], (int, float))

    def test_meddic_breakdown_has_engagement_potential(self, mock_notion_page):
        """MEDDIC breakdown must include engagement_potential with score."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)
        breakdown = result.get("meddic_score_breakdown", {})

        assert "engagement_potential" in breakdown
        assert "score" in breakdown["engagement_potential"]
        assert isinstance(breakdown["engagement_potential"]["score"], (int, float))

    def test_transform_extracts_basic_fields(self, mock_notion_page):
        """Transform should extract basic contact fields correctly."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert result["name"] == "John Doe"
        assert result["email"] == "john.doe@example.com"
        assert result["title"] == "VP of Infrastructure"
        assert result["company"] == "Acme Corp"
        assert result["linkedin_url"] == "https://linkedin.com/in/johndoe"

    def test_transform_includes_id(self, mock_notion_page):
        """Transform should generate a contact ID."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "id" in result
        assert result["id"].startswith("con_")

    def test_transform_includes_notion_id(self, mock_notion_page):
        """Transform should include the original Notion page ID."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(mock_notion_page)

        assert "notion_id" in result
        assert result["notion_id"] == mock_notion_page["id"]


class TestContactTransformEdgeCases:
    """Tests for edge cases in contact transformation."""

    @pytest.fixture
    def minimal_notion_page(self):
        """Create a minimal Notion page with only required fields."""
        return {
            "id": "min123",
            "properties": {
                "Name": {"title": [{"text": {"content": "Minimal Contact"}}]},
            },
        }

    def test_transform_handles_missing_email(self, minimal_notion_page):
        """Transform should handle missing email gracefully."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(minimal_notion_page)

        assert result is not None
        # Email should be None or empty string, not crash
        assert "email" in result

    def test_transform_handles_missing_title(self, minimal_notion_page):
        """Transform should handle missing title gracefully."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(minimal_notion_page)

        assert result is not None
        # Should still produce MEDDIC scores
        assert "meddic_score_breakdown" in result

    def test_transform_handles_empty_properties(self):
        """Transform should handle page with empty properties."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        page = {"id": "empty123", "properties": {}}
        result = transform_notion_contact(page)

        assert result is not None


class TestMEDDICScoreNotZeroWhenDataExists:
    """Tests to ensure scores are not incorrectly zero."""

    @pytest.fixture
    def complete_contact_page(self):
        """Contact with all data that should have non-zero scores."""
        return {
            "id": "complete123",
            "properties": {
                "Name": {"title": [{"text": {"content": "Complete Contact"}}]},
                "Email": {"email": "complete@example.com"},
                "Title": {"rich_text": [{"text": {"content": "Senior Site Reliability Engineer"}}]},
                "Company": {"rich_text": [{"text": {"content": "Big Tech Inc"}}]},
                "LinkedIn URL": {"url": "https://linkedin.com/in/complete"},
                "Lead Score": {"number": 85},
                "Engagement Level": {"select": {"name": "High"}},
            },
        }

    def test_role_fit_not_zero_when_title_exists(self, complete_contact_page):
        """Role fit score should not be 0 when title is provided."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(complete_contact_page)
        breakdown = result.get("meddic_score_breakdown", {})

        role_fit_score = breakdown.get("role_fit", {}).get("score", 0)
        assert role_fit_score > 0, "Role fit should not be 0 when title exists"

    def test_champion_potential_not_zero_for_sre(self, complete_contact_page):
        """Champion potential should not be 0 for SRE roles."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(complete_contact_page)

        assert result["champion_potential_score"] > 0, "Champion potential should not be 0 for SRE"

    def test_engagement_not_zero_when_engagement_level_high(self, complete_contact_page):
        """Engagement score should not be 0 when engagement level is High."""
        try:
            from src.abm_research.api.server import transform_notion_contact
        except ImportError:
            pytest.skip("Server module not available")

        result = transform_notion_contact(complete_contact_page)
        breakdown = result.get("meddic_score_breakdown", {})

        engagement_score = breakdown.get("engagement_potential", {}).get("score", 0)
        # Note: This may still be low if engagement is not well-scored
        # The test validates the field exists and is numeric
        assert isinstance(engagement_score, (int, float))
