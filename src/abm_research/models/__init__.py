"""
Core data models for ABM Research System
"""
from .account import Account
from .contact import Contact
from .trigger_event import TriggerEvent
from .strategic_partnership import StrategicPartnership

# Lead scoring functionality is now available in core.unified_lead_scorer
# Import the LeadScore dataclass from the unified scorer
from ..core.unified_lead_scorer import LeadScore

__all__ = [
    'Account',
    'Contact',
    'TriggerEvent',
    'StrategicPartnership',
    'LeadScore'
]
