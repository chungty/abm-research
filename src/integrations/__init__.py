"""
Integrations package for ABM Research System

External system integrations including Notion, Salesforce, and other platforms.
"""

from .notion_database import NotionDatabaseManager

__all__ = ['NotionDatabaseManager']