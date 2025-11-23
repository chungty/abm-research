"""
Phase implementations for ABM Research System
Each phase encapsulates a specific research workflow step
"""
from .phase_1_account_intelligence import AccountIntelligencePhase
from .phase_2_contact_discovery import ContactDiscoveryPhase
from .phase_3_contact_enrichment import ContactEnrichmentPhase
from .phase_4_engagement_intelligence import EngagementIntelligencePhase
from .phase_5_partnership_intelligence import PartnershipIntelligencePhase

__all__ = [
    'AccountIntelligencePhase',
    'ContactDiscoveryPhase',
    'ContactEnrichmentPhase',
    'EngagementIntelligencePhase',
    'PartnershipIntelligencePhase'
]