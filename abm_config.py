#!/usr/bin/env python3
"""
ABM Configuration Management
Centralized configuration to prevent API key confusion and ensure consistency
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class ABMConfig:
    """Centralized configuration management for ABM system"""

    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        # API Keys - with validation and clear naming
        self.apollo_api_key = self._get_required_env('APOLLO_API_KEY')
        self.notion_api_key = self._get_required_env('NOTION_ABM_API_KEY')  # This is the correct one!
        self.openai_api_key = self._get_required_env('OPENAI_API_KEY')

        # Configuration validation
        self._validate_configuration()

    def _get_required_env(self, key: str) -> str:
        """Get required environment variable with validation"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"❌ Required environment variable {key} not found")
        return value

    def _validate_configuration(self):
        """Validate all configuration is properly set"""

        # Validate API keys have correct formats
        if not self.apollo_api_key.startswith(('Ol', 'sk-')):
            print(f"⚠️  Apollo API key may be incorrect format: {self.apollo_api_key[:10]}...")

        if not self.notion_api_key.startswith('ntn_'):
            print(f"⚠️  Notion API key may be incorrect format: {self.notion_api_key[:10]}...")

        if not self.openai_api_key.startswith('sk-'):
            print(f"⚠️  OpenAI API key may be incorrect format: {self.openai_api_key[:10]}...")

    def get_notion_headers(self) -> dict:
        """Get Notion API headers for direct API calls"""
        return {
            'Authorization': f'Bearer {self.notion_api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

    def get_apollo_headers(self) -> dict:
        """Get Apollo API headers"""
        return {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': self.apollo_api_key
        }

    def print_config_status(self):
        """Print configuration status for debugging"""
        print("🔧 ABM SYSTEM CONFIGURATION STATUS")
        print("-" * 40)
        print(f"✅ Apollo API Key: {self.apollo_api_key[:15]}...{self.apollo_api_key[-4:]}")
        print(f"✅ Notion API Key: {self.notion_api_key[:15]}...{self.notion_api_key[-4:]}")
        print(f"✅ OpenAI API Key: {self.openai_api_key[:15]}...{self.openai_api_key[-4:]}")
        print("📝 All API keys properly configured")

# Global configuration instance
config = ABMConfig()

if __name__ == "__main__":
    config.print_config_status()