"""
Account model for ABM Research System
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class AccountResearchStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETE = "Complete"


@dataclass
class Account:
    """Represents a target account for ABM research"""

    # Core identifiers
    name: str
    domain: str

    # Company data
    employee_count: Optional[int] = None
    revenue: Optional[str] = None  # "100M-1B", "$500M", etc.
    business_model: Optional[str] = None  # cloud provider, colocation, hyperscaler, AI infrastructure

    # Geographic and facility data
    data_center_locations: List[str] = field(default_factory=list)
    facility_capacity: Optional[str] = None  # MW, sq ft, etc.

    # Financial and growth indicators
    recent_funding: Optional[str] = None
    growth_indicators: List[str] = field(default_factory=list)  # hiring trends, expansion announcements

    # ICP scoring (legacy)
    icp_fit_score: float = 0.0  # 0-100
    company_type_score: int = 50  # base score from company type
    trigger_alignment_score: int = 0  # bonus from trigger events

    # Account-First Scoring (NEW - with full traceability)
    account_score: float = 0.0  # 0-100 overall account score
    infrastructure_score: float = 0.0  # 0-100 infrastructure fit
    business_fit_score: float = 0.0  # 0-100 business fit
    buying_signals_score: float = 0.0  # 0-100 buying signals

    # Full breakdown for dashboard traceability (JSON serializable)
    infrastructure_breakdown: Dict[str, Any] = field(default_factory=dict)
    account_score_breakdown: Dict[str, Any] = field(default_factory=dict)

    # Research tracking
    research_status: AccountResearchStatus = AccountResearchStatus.NOT_STARTED
    last_updated: datetime = field(default_factory=datetime.now)
    researcher_notes: str = ""

    # Relations (will be populated by research phases)
    trigger_events: List['TriggerEvent'] = field(default_factory=list)
    contacts: List['Contact'] = field(default_factory=list)
    strategic_partnerships: List['StrategicPartnership'] = field(default_factory=list)

    # Metadata
    apollo_company_id: Optional[str] = None
    linkedin_company_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Calculate derived fields after initialization"""
        self.calculate_icp_fit_score()

    def calculate_icp_fit_score(self) -> float:
        """Calculate ICP fit score based on company type and trigger alignment"""
        # Base score from company type
        type_scores = {
            'cloud': 100,
            'colocation': 100,
            'hyperscaler': 100,
            'ai-focused': 90,
            'energy-intensive': 70
        }

        # Get base score
        base_score = type_scores.get(self.business_model, 50)

        # Add trigger alignment bonus (0-20 points)
        trigger_bonus = min(self.trigger_alignment_score, 20)

        self.icp_fit_score = min(base_score + trigger_bonus, 100.0)
        return self.icp_fit_score

    def add_trigger_event(self, event: 'TriggerEvent'):
        """Add a trigger event and update alignment score"""
        self.trigger_events.append(event)

        # Recalculate trigger alignment based on event relevance
        if event.relevance_score >= 80:
            self.trigger_alignment_score = min(self.trigger_alignment_score + 20, 20)
        elif event.relevance_score >= 50:
            self.trigger_alignment_score = min(self.trigger_alignment_score + 10, 20)

        self.calculate_icp_fit_score()

    def add_contact(self, contact: 'Contact'):
        """Add a contact to this account"""
        self.contacts.append(contact)
        contact.account = self

    def add_strategic_partnership(self, partnership: 'StrategicPartnership'):
        """Add a strategic partnership"""
        self.strategic_partnerships.append(partnership)
        partnership.account = self

    def get_high_priority_contacts(self, min_score: float = 70.0) -> List['Contact']:
        """Get contacts with lead score above threshold"""
        return [c for c in self.contacts if c.final_lead_score >= min_score]

    def get_buying_committee(self) -> Dict[str, List['Contact']]:
        """Get contacts organized by buying committee role"""
        committee = {
            'Economic Buyer': [],
            'Technical Evaluator': [],
            'Champion': [],
            'Influencer': []
        }

        for contact in self.contacts:
            if contact.buying_committee_role in committee:
                committee[contact.buying_committee_role].append(contact)

        return committee

    def to_notion_format(self) -> Dict[str, Any]:
        """Convert to Notion database format"""
        return {
            'Company name': {'title': [{'text': {'content': self.name}}]},
            'Domain': {'rich_text': [{'text': {'content': self.domain}}]},
            'Employee count': {'number': self.employee_count},
            'ICP fit score': {'number': self.icp_fit_score},
            'Account research status': {'select': {'name': self.research_status.value}},
            'Last updated': {'date': {'start': self.last_updated.isoformat()}}
        }

    def __str__(self) -> str:
        return f"Account({self.name}, ICP: {self.icp_fit_score:.1f}, Status: {self.research_status.value})"

    def __repr__(self) -> str:
        return f"Account(name='{self.name}', domain='{self.domain}', icp_score={self.icp_fit_score})"