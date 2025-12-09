"""Sample test data for ABM Research System tests."""

from datetime import datetime
from typing import Dict, List, Any

# Sample account data
SAMPLE_ACCOUNT = {
    "name": "Genesis Cloud Technologies",
    "domain": "genesiscloud.com",
    "industry": "Cloud Computing",
    "size": "100-500",
    "location": "San Francisco, CA",
    "description": "Leading cloud infrastructure provider",
}

# Sample contact data
SAMPLE_CONTACTS = [
    {
        "name": "Sarah Chen",
        "title": "VP of Engineering",
        "email": "sarah.chen@genesiscloud.com",
        "linkedin_url": "https://linkedin.com/in/sarah-chen-genesis",
        "company": "Genesis Cloud Technologies",
        "lead_score": 85,
        "engagement_level": "High",
    },
    {
        "name": "Michael Rodriguez",
        "title": "CTO",
        "email": "michael.rodriguez@genesiscloud.com",
        "linkedin_url": "https://linkedin.com/in/michael-rodriguez-cto",
        "company": "Genesis Cloud Technologies",
        "lead_score": 92,
        "engagement_level": "Very High",
    }
]

# Sample trigger events
SAMPLE_TRIGGER_EVENTS = [
    {
        "description": "Genesis Cloud announces $50M Series B funding for AI infrastructure expansion",
        "event_type": "expansion",
        "confidence": "High",
        "confidence_score": 95,
        "relevance_score": 88,
        "source_url": "https://techcrunch.com/genesis-cloud-series-b",
        "source_type": "News Article",
        "detected_date": "2024-01-15",
        "urgency_level": "High"
    },
    {
        "description": "New VP of Engineering hire suggests infrastructure scaling plans",
        "event_type": "leadership_change",
        "confidence": "Medium",
        "confidence_score": 75,
        "relevance_score": 70,
        "source_url": "https://linkedin.com/posts/genesis-cloud-vp-hire",
        "source_type": "LinkedIn Post",
        "detected_date": "2024-01-10",
        "urgency_level": "Medium"
    }
]

# Sample partnership data
SAMPLE_PARTNERSHIPS = [
    {
        "partner_name": "AWS",
        "partnership_type": "Technology Integration",
        "relevance_score": 85,
        "context": "Multi-cloud deployment strategy",
        "source_url": "https://aws.amazon.com/partners/genesis-cloud"
    }
]

# Expected dashboard API responses
EXPECTED_DASHBOARD_DATA = {
    "accounts": [SAMPLE_ACCOUNT],
    "contacts": SAMPLE_CONTACTS,
    "trigger_events": SAMPLE_TRIGGER_EVENTS,
    "partnerships": SAMPLE_PARTNERSHIPS,
    "analytics": {
        "total_accounts": 1,
        "total_contacts": 2,
        "high_value_contacts": 2,
        "recent_triggers": 2
    }
}

# Mock API responses for external services
MOCK_APOLLO_RESPONSE = {
    "contacts": [
        {
            "first_name": "Sarah",
            "last_name": "Chen",
            "title": "VP of Engineering",
            "email": "sarah.chen@genesiscloud.com",
            "linkedin_url": "https://linkedin.com/in/sarah-chen-genesis",
            "organization_name": "Genesis Cloud Technologies"
        }
    ]
}

MOCK_OPENAI_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": '{"engagement_intelligence": {"talking_points": ["Discuss cloud infrastructure scaling"], "engagement_level": "High", "next_actions": ["Schedule technical demo"]}}'
            }
        }
    ]
}

MOCK_NOTION_CREATE_RESPONSE = {
    "id": "12345678-1234-1234-1234-123456789abc",
    "created_time": "2024-01-15T10:00:00.000Z",
    "properties": {}
}

# Test configuration
TEST_CONFIG = {
    "api_keys": {
        "apollo": "test-apollo-key",
        "openai": "test-openai-key",
        "notion": "test-notion-key",
        "brave": "test-brave-key"
    },
    "database_ids": {
        "accounts": "test-accounts-db-id",
        "contacts": "test-contacts-db-id",
        "events": "test-events-db-id",
        "partnerships": "test-partnerships-db-id"
    }
}

def get_sample_account() -> Dict[str, Any]:
    """Get sample account data."""
    return SAMPLE_ACCOUNT.copy()

def get_sample_contacts() -> List[Dict[str, Any]]:
    """Get sample contacts data."""
    return [contact.copy() for contact in SAMPLE_CONTACTS]

def get_sample_trigger_events() -> List[Dict[str, Any]]:
    """Get sample trigger events data."""
    return [event.copy() for event in SAMPLE_TRIGGER_EVENTS]

def get_expected_dashboard_data() -> Dict[str, Any]:
    """Get expected dashboard API response data."""
    return EXPECTED_DASHBOARD_DATA.copy()
