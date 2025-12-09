"""ABM Research System - Production Ready Package

Account-Based Marketing intelligence system with LinkedIn enrichment and Notion integration.
"""

__version__ = "1.0.0"
__author__ = "ABM Research Team"

# Main exports
from .core.abm_system import ComprehensiveABMSystem
from .integrations.notion_client import NotionClient
from .integrations.notion_config import NotionConfigManager

__all__ = ["ComprehensiveABMSystem", "NotionClient", "NotionConfigManager"]
