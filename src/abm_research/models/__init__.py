"""
Core data models for ABM Research System
"""
# Lead scoring functionality is now available in core.unified_lead_scorer
# Import the LeadScore dataclass from the unified scorer
from ..core.unified_lead_scorer import LeadScore
from .account import Account
from .contact import Contact
from .strategic_partnership import StrategicPartnership
from .trigger_event import TriggerEvent

__all__ = ["Account", "Contact", "TriggerEvent", "StrategicPartnership", "LeadScore"]
