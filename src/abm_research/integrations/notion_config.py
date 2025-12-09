#!/usr/bin/env python3
"""
Unified Notion Configuration for ABM Research System

Merges configuration from:
- abm_config.py (API key management, validation)
- config/settings.py (database IDs, environment management)

Resolves API key naming confusion by standardizing on NOTION_API_KEY
and providing clear migration guidance for legacy NOTION_ABM_API_KEY usage.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class NotionConfiguration:
    """Complete Notion configuration dataclass"""

    api_key: str
    database_ids: Dict[str, Optional[str]]
    rate_limits: Dict[str, float]
    headers: Dict[str, str]
    validation_results: Dict[str, bool]


class NotionConfigManager:
    """
    Unified configuration manager for Notion integration

    Features:
    - Resolves API key naming confusion (NOTION_API_KEY vs NOTION_ABM_API_KEY)
    - Manages all database IDs from environment variables
    - Provides validation and health checking
    - Handles rate limiting configuration
    - Centralizes all Notion-related settings
    """

    def __init__(self, env_file_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            env_file_path: Optional path to .env file (defaults to project root)
        """
        self.setup_logging()
        self._load_environment(env_file_path)
        self._config = self._build_configuration()

    def setup_logging(self):
        """Setup logging for configuration operations"""
        logging.basicConfig(level=logging.INFO)

    def _load_environment(self, env_file_path: Optional[str] = None):
        """Load environment variables from .env file"""
        if env_file_path:
            env_path = Path(env_file_path)
        else:
            # Default to project root
            env_path = Path(__file__).parent / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"✅ Loaded environment from {env_path}")
        else:
            logger.warning(f"⚠️  Environment file not found: {env_path}")

    def _build_configuration(self) -> NotionConfiguration:
        """Build complete configuration from environment"""

        # Resolve API key
        api_key = self._resolve_api_key()

        # Load database IDs
        database_ids = self._load_database_ids()

        # Configure rate limiting
        rate_limits = self._configure_rate_limits()

        # Generate headers
        headers = self._generate_headers(api_key)

        # Validate configuration
        validation_results = self._validate_configuration(api_key, database_ids)

        return NotionConfiguration(
            api_key=api_key,
            database_ids=database_ids,
            rate_limits=rate_limits,
            headers=headers,
            validation_results=validation_results,
        )

    def _resolve_api_key(self) -> str:
        """
        Resolve Notion API key with migration guidance

        Handles the naming confusion between NOTION_API_KEY and NOTION_ABM_API_KEY
        by checking both and providing clear guidance.
        """

        # Check preferred standard name
        standard_key = os.getenv("NOTION_API_KEY")
        legacy_key = os.getenv("NOTION_ABM_API_KEY")

        if standard_key and legacy_key:
            if standard_key == legacy_key:
                logger.info("✅ Both NOTION_API_KEY and NOTION_ABM_API_KEY set to same value")
                logger.info(
                    "💡 Recommendation: Remove NOTION_ABM_API_KEY and use only NOTION_API_KEY"
                )
                return standard_key
            else:
                logger.warning(
                    "⚠️  CONFLICT: Different values for NOTION_API_KEY and NOTION_ABM_API_KEY"
                )
                logger.warning("🔧 Using NOTION_API_KEY (preferred), check your configuration")
                return standard_key

        elif standard_key:
            logger.info("✅ Using NOTION_API_KEY (recommended)")
            return standard_key

        elif legacy_key:
            logger.warning("⚠️  Using legacy NOTION_ABM_API_KEY")
            logger.warning("🔧 Migration: Set NOTION_API_KEY and remove NOTION_ABM_API_KEY")
            return legacy_key

        else:
            raise ValueError(
                "❌ Notion API key not found!\n"
                "Required: Set NOTION_API_KEY in your .env file\n"
                "Legacy: NOTION_ABM_API_KEY is also supported but deprecated"
            )

    def _load_database_ids(self) -> Dict[str, Optional[str]]:
        """Load all database IDs from environment variables"""

        # Standard database ID mappings
        database_mapping = {
            "accounts": ["NOTION_ACCOUNTS_DB_ID"],
            "contacts": ["NOTION_CONTACTS_DB_ID"],
            "trigger_events": [
                "NOTION_TRIGGER_EVENTS_DB_ID",
                "NOTION_EVENTS_DB_ID",
            ],  # Handle both names
            "partnerships": ["NOTION_PARTNERSHIPS_DB_ID"],
            "intelligence": [
                "NOTION_INTELLIGENCE_DB_ID",
                "NOTION_CONTACT_INTELLIGENCE_DB_ID",
            ],  # Handle both names
        }

        database_ids = {}

        for db_name, possible_env_vars in database_mapping.items():
            db_id = None

            # Try each possible environment variable name
            for env_var in possible_env_vars:
                db_id = os.getenv(env_var)
                if db_id:
                    logger.info(f"✅ Found {db_name} database ID from {env_var}")
                    break

            database_ids[db_name] = db_id

            if not db_id:
                logger.warning(
                    f"⚠️  Missing database ID for {db_name} (tried: {', '.join(possible_env_vars)})"
                )

        return database_ids

    def _configure_rate_limits(self) -> Dict[str, float]:
        """Configure rate limiting settings"""
        return {
            "request_delay": float(os.getenv("NOTION_REQUEST_DELAY", "0.5")),  # 500ms default
            "max_retries": int(os.getenv("NOTION_MAX_RETRIES", "3")),
            "timeout": float(os.getenv("NOTION_TIMEOUT", "30.0")),  # 30 seconds
        }

    def _generate_headers(self, api_key: str) -> Dict[str, str]:
        """Generate Notion API headers"""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
            "User-Agent": "ABM-Research-System/1.0",
        }

    def _validate_configuration(
        self, api_key: str, database_ids: Dict[str, Optional[str]]
    ) -> Dict[str, bool]:
        """Validate configuration completeness and format"""

        validation_results = {}

        # Validate API key format
        if api_key.startswith("secret_"):
            validation_results["api_key_format"] = True
            logger.info("✅ API key format appears correct (secret_...)")
        elif api_key.startswith("ntn_"):
            validation_results["api_key_format"] = True
            logger.info("✅ API key format appears correct (ntn_...)")
        else:
            validation_results["api_key_format"] = False
            logger.warning(f"⚠️  API key format may be incorrect: {api_key[:10]}...")

        # Validate database IDs
        configured_dbs = [name for name, db_id in database_ids.items() if db_id]
        missing_dbs = [name for name, db_id in database_ids.items() if not db_id]

        validation_results["databases_configured"] = len(configured_dbs) > 0
        validation_results["all_databases_configured"] = len(missing_dbs) == 0

        if configured_dbs:
            logger.info(f"✅ Configured databases: {', '.join(configured_dbs)}")
        if missing_dbs:
            logger.warning(f"⚠️  Missing database configurations: {', '.join(missing_dbs)}")

        # Overall health check
        validation_results["configuration_healthy"] = (
            validation_results["api_key_format"] and validation_results["databases_configured"]
        )

        return validation_results

    # ═══════════════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════════════════

    @property
    def api_key(self) -> str:
        """Get the resolved API key"""
        return self._config.api_key

    @property
    def database_ids(self) -> Dict[str, Optional[str]]:
        """Get all database IDs"""
        return self._config.database_ids.copy()

    @property
    def headers(self) -> Dict[str, str]:
        """Get Notion API headers"""
        return self._config.headers.copy()

    @property
    def rate_limits(self) -> Dict[str, float]:
        """Get rate limiting configuration"""
        return self._config.rate_limits.copy()

    def get_database_id(self, database_name: str) -> Optional[str]:
        """
        Get specific database ID

        Args:
            database_name: Name of database (accounts, contacts, trigger_events, partnerships, intelligence)

        Returns:
            Database ID if configured, None otherwise
        """
        return self._config.database_ids.get(database_name)

    def is_database_configured(self, database_name: str) -> bool:
        """Check if a specific database is configured"""
        return bool(self.get_database_id(database_name))

    def get_health_status(self) -> Dict[str, Any]:
        """Get complete health status of configuration"""
        return {
            "api_key_configured": bool(self._config.api_key),
            "api_key_format_valid": self._config.validation_results.get("api_key_format", False),
            "databases_configured": self._config.validation_results.get(
                "databases_configured", False
            ),
            "all_databases_configured": self._config.validation_results.get(
                "all_databases_configured", False
            ),
            "configuration_healthy": self._config.validation_results.get(
                "configuration_healthy", False
            ),
            "database_status": {
                name: bool(db_id) for name, db_id in self._config.database_ids.items()
            },
            "missing_databases": [
                name for name, db_id in self._config.database_ids.items() if not db_id
            ],
        }

    def print_configuration_summary(self):
        """Print a human-readable configuration summary"""
        print("\n🔧 NOTION CONFIGURATION SUMMARY")
        print("=" * 50)

        # API Key status
        if self._config.validation_results.get("api_key_format", False):
            print(f"✅ API Key: {self._config.api_key[:15]}...{self._config.api_key[-4:]}")
        else:
            print(f"⚠️  API Key: {self._config.api_key[:15]}... (format warning)")

        # Database status
        print("\n📊 Database Configuration:")
        for db_name, db_id in self._config.database_ids.items():
            if db_id:
                print(f"  ✅ {db_name}: {db_id[:15]}...{db_id[-4:]}")
            else:
                print(f"  ❌ {db_name}: Not configured")

        # Health status
        print(
            f"\n🏥 Overall Health: {'✅ Healthy' if self._config.validation_results.get('configuration_healthy', False) else '⚠️  Issues detected'}"
        )

    def validate_and_migrate(self) -> Dict[str, str]:
        """
        Validate current configuration and provide migration recommendations

        Returns:
            Dictionary of recommendations for improving configuration
        """
        recommendations = {}

        # Check for API key migration
        if os.getenv("NOTION_ABM_API_KEY") and not os.getenv("NOTION_API_KEY"):
            recommendations["api_key_migration"] = (
                "Set NOTION_API_KEY to the value of NOTION_ABM_API_KEY, "
                "then remove NOTION_ABM_API_KEY from your .env file"
            )

        # Check for missing databases
        missing_dbs = [name for name, db_id in self._config.database_ids.items() if not db_id]
        if missing_dbs:
            recommendations["missing_databases"] = (
                f"Configure database IDs for: {', '.join(missing_dbs)}. "
                "Run notion workspace setup or manually set environment variables."
            )

        # Check for duplicate keys
        if os.getenv("NOTION_API_KEY") and os.getenv("NOTION_ABM_API_KEY"):
            if os.getenv("NOTION_API_KEY") != os.getenv("NOTION_ABM_API_KEY"):
                recommendations["duplicate_keys"] = (
                    "You have different values for NOTION_API_KEY and NOTION_ABM_API_KEY. "
                    "Use only NOTION_API_KEY and remove the other."
                )

        return recommendations


# ═══════════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

_config_manager = None


def get_notion_config() -> NotionConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = NotionConfigManager()
    return _config_manager


def get_api_key() -> str:
    """Convenience function to get API key"""
    return get_notion_config().api_key


def get_database_id(database_name: str) -> Optional[str]:
    """Convenience function to get database ID"""
    return get_notion_config().get_database_id(database_name)


def get_headers() -> Dict[str, str]:
    """Convenience function to get API headers"""
    return get_notion_config().headers


if __name__ == "__main__":
    # Test and demonstration script
    try:
        config = NotionConfigManager()
        config.print_configuration_summary()

        # Show migration recommendations
        recommendations = config.validate_and_migrate()
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for area, recommendation in recommendations.items():
                print(f"  {area}: {recommendation}")
        else:
            print(f"\n✅ Configuration is optimal!")

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n🔧 Quick fix:")
        print("1. Copy .env.example to .env")
        print("2. Set NOTION_API_KEY=your_notion_api_key")
        print("3. Set database IDs (NOTION_ACCOUNTS_DB_ID, etc.)")
