#!/usr/bin/env python3
"""
Unified Configuration Manager for ABM Research System

This module consolidates all configuration management across the codebase,
replacing the fragmented patterns in settings.py, abm_config.py, and notion_config.py.

Provides:
- Single source of truth for all configuration
- Standardized API key management
- Database ID resolution
- Header generation utilities
- Centralized validation
- Environment variable loading
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Unified configuration manager that consolidates all scattered config patterns.

    Replaces:
    - config/settings.py (module-level variables)
    - config/abm_config.py (ABMConfig class)
    - integrations/notion_config.py (NotionConfigManager class)
    """

    _instance: Optional['ConfigManager'] = None
    _initialized: bool = False

    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration manager (only once due to singleton)"""
        if self._initialized:
            return

        self._load_environment()
        self._load_api_keys()
        self._load_database_ids()
        self._load_external_configs()
        self._validate_configuration()

        self._initialized = True
        logger.info("✅ Unified Configuration Manager initialized")

    def _load_environment(self):
        """Load environment variables from .env file"""
        # Find .env file in project root
        current_path = Path(__file__).parent
        while current_path.parent != current_path:
            env_file = current_path / '.env'
            if env_file.exists():
                load_dotenv(env_file)
                logger.info(f"📄 Loaded environment from: {env_file}")
                break
            current_path = current_path.parent
        else:
            logger.warning("⚠️ No .env file found in project hierarchy")

    def _load_api_keys(self):
        """Load and validate API keys with standardized names"""
        # Use STANDARDIZED environment variable names (fixes naming chaos)
        self.apollo_api_key = self._get_required_env('APOLLO_API_KEY')
        self.notion_api_key = self._get_required_env('NOTION_API_KEY')  # NOT NOTION_ABM_API_KEY!
        self.openai_api_key = self._get_required_env('OPENAI_API_KEY')

        # Deprecated variables - log warnings if found
        if os.getenv('NOTION_ABM_API_KEY'):
            logger.warning("⚠️ NOTION_ABM_API_KEY is deprecated. Use NOTION_API_KEY instead.")
        if os.getenv('NOTION_TOKEN'):
            logger.warning("⚠️ NOTION_TOKEN is deprecated. Use NOTION_API_KEY instead.")

    def _load_database_ids(self):
        """Load database IDs from environment (single source of truth)"""
        self.database_ids = {
            'accounts': self._get_required_env('NOTION_ACCOUNTS_DB_ID'),
            'contacts': self._get_required_env('NOTION_CONTACTS_DB_ID'),
            'trigger_events': self._get_required_env('NOTION_TRIGGER_EVENTS_DB_ID'),
            'partnerships': self._get_required_env('NOTION_PARTNERSHIPS_DB_ID')
        }

        # Normalize database IDs (remove dashes for consistency)
        for key, db_id in self.database_ids.items():
            self.database_ids[key] = db_id.replace('-', '')

    def _load_external_configs(self):
        """Load external JSON configuration files"""
        config_dir = Path(__file__).parent
        root_dir = config_dir.parent.parent.parent

        # Load lead scoring configuration
        lead_config_path = root_dir / 'references' / 'lead_scoring_config.json'
        if lead_config_path.exists():
            with open(lead_config_path, 'r') as f:
                self.lead_scoring_config = json.load(f)
        else:
            logger.warning(f"⚠️ Lead scoring config not found: {lead_config_path}")
            self.lead_scoring_config = {}

        # Load partnership categories (currently hardcoded in settings.py)
        self.partnership_categories = {
            'technology_partnerships': {
                'indicators': ['technology', 'tech', 'integration', 'api', 'platform', 'software'],
                'priority': 'high'
            },
            'infrastructure_partnerships': {
                'indicators': ['infrastructure', 'data center', 'cloud', 'hosting', 'aws', 'gcp', 'azure'],
                'priority': 'high'
            },
            'energy_partnerships': {
                'indicators': ['energy', 'power', 'renewable', 'solar', 'efficiency', 'sustainability'],
                'priority': 'very_high'
            },
            'strategic_alliances': {
                'indicators': ['strategic', 'alliance', 'partnership', 'collaboration', 'joint venture'],
                'priority': 'medium'
            },
            'vendor_relationships': {
                'indicators': ['vendor', 'supplier', 'procurement', 'sourcing'],
                'priority': 'low'
            }
        }

    def _get_required_env(self, var_name: str) -> str:
        """Get required environment variable with validation"""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Required environment variable missing: {var_name}")
        return value.strip()

    def _validate_configuration(self):
        """Comprehensive configuration validation"""
        validation_results = {}

        # Validate API key formats
        if self.apollo_api_key and not self.apollo_api_key.startswith(('Ol', 'sk-')):
            logger.warning(f"⚠️ Apollo API key format may be incorrect (starts with: {self.apollo_api_key[:3]}...)")

        if self.notion_api_key and not self.notion_api_key.startswith(('ntn_', 'secret_')):
            logger.warning(f"⚠️ Notion API key format may be incorrect (starts with: {self.notion_api_key[:3]}...)")

        if self.openai_api_key and not self.openai_api_key.startswith('sk-'):
            logger.warning(f"⚠️ OpenAI API key format may be incorrect (starts with: {self.openai_api_key[:3]}...)")

        # Validate database IDs (should be 32 character hex strings)
        for name, db_id in self.database_ids.items():
            if len(db_id) != 32:
                logger.warning(f"⚠️ {name} database ID length incorrect: {len(db_id)} chars (expected 32)")

            if not all(c in '0123456789abcdefABCDEF' for c in db_id):
                logger.warning(f"⚠️ {name} database ID contains non-hex characters")

        logger.info("✅ Configuration validation completed")

    # API Key Access Methods
    def get_apollo_api_key(self) -> str:
        """Get Apollo API key"""
        return self.apollo_api_key

    def get_notion_api_key(self) -> str:
        """Get Notion API key"""
        return self.notion_api_key

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key"""
        return self.openai_api_key

    # Database ID Access Methods
    def get_database_id(self, database_type: str) -> str:
        """
        Get database ID by type

        Args:
            database_type: One of 'accounts', 'contacts', 'trigger_events', 'partnerships'
        """
        if database_type not in self.database_ids:
            raise ValueError(f"Unknown database type: {database_type}")
        return self.database_ids[database_type]

    def get_all_database_ids(self) -> Dict[str, str]:
        """Get all database IDs"""
        return self.database_ids.copy()

    # Header Generation Methods (consolidates duplication)
    def get_notion_headers(self) -> Dict[str, str]:
        """Generate Notion API headers"""
        return {
            'Authorization': f'Bearer {self.notion_api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28',
            'User-Agent': 'ABM-Research-System/1.0'
        }

    def get_apollo_headers(self) -> Dict[str, str]:
        """Generate Apollo API headers"""
        return {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.apollo_api_key
        }

    def get_openai_headers(self) -> Dict[str, str]:
        """Generate OpenAI API headers"""
        return {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }

    # External Configuration Access
    def get_lead_scoring_config(self) -> Dict[str, Any]:
        """Get lead scoring configuration"""
        return self.lead_scoring_config

    def get_partnership_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get partnership categories configuration"""
        return self.partnership_categories

    # Utility Methods
    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'

    def get_log_level(self) -> str:
        """Get configured log level"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (f"ConfigManager(apollo_key={'✓' if self.apollo_api_key else '✗'}, "
                f"notion_key={'✓' if self.notion_api_key else '✗'}, "
                f"openai_key={'✓' if self.openai_api_key else '✗'}, "
                f"databases={list(self.database_ids.keys())})")


# Global singleton instance (replaces all scattered config imports)
config_manager = ConfigManager()

# Convenience aliases for backward compatibility during transition
config = config_manager  # For files using: from config.manager import config