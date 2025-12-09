#!/usr/bin/env python3
"""
Consolidated Notion Client for ABM Research System

Merges functionality from:
- src/integrations/notion_database.py (workspace setup, database schemas)
- notion_persistence_manager.py (CRUD operations, deduplication, rate limiting)

Provides unified interface for:
- Complete ABM workspace creation with all 5 databases
- Data persistence with deduplication and rate limiting
- Comprehensive error handling and logging
- EXPLICIT error propagation (no silent failures)
"""

import json
import logging
import os
import time
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import requests

# ═══════════════════════════════════════════════════════════════════════════════════
# EXCEPTION HIERARCHY - No more silent failures!
# ═══════════════════════════════════════════════════════════════════════════════════


class NotionErrorCode(Enum):
    """Error codes for categorizing Notion failures"""

    CONFIG_ERROR = "CONFIG_ERROR"  # Missing API key, database ID, etc.
    API_ERROR = "API_ERROR"  # Notion API returned an error
    VALIDATION_ERROR = "VALIDATION_ERROR"  # Invalid data format
    NOT_FOUND = "NOT_FOUND"  # Resource not found
    PARSE_ERROR = "PARSE_ERROR"  # JSON/response parsing failed
    RATE_LIMITED = "RATE_LIMITED"  # Too many requests
    NETWORK_ERROR = "NETWORK_ERROR"  # Connection failed


class NotionError(Exception):
    """
    Base exception for all Notion-related errors.
    NEVER catch and swallow - always propagate with context.
    """

    def __init__(
        self,
        message: str,
        code: NotionErrorCode = NotionErrorCode.API_ERROR,
        operation: str = "unknown",
        details: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        self.message = message
        self.code = code
        self.operation = operation
        self.details = details or {}
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        msg = f"[{self.code.value}] {self.operation}: {self.message}"
        if self.details:
            msg += f" | Details: {json.dumps(self.details, default=str)}"
        if self.cause:
            msg += f" | Caused by: {type(self.cause).__name__}: {self.cause}"
        return msg

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "error_type": "NotionError",
            "code": self.code.value,
            "operation": self.operation,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }


class NotionConfigError(NotionError):
    """Raised when Notion is misconfigured (missing API key, database ID, etc.)"""

    def __init__(self, message: str, missing_config: str, **kwargs):
        super().__init__(
            message,
            code=NotionErrorCode.CONFIG_ERROR,
            details={"missing_config": missing_config},
            **kwargs,
        )


class NotionAPIError(NotionError):
    """Raised when Notion API returns an error"""

    def __init__(self, message: str, status_code: int, response_text: str, **kwargs):
        super().__init__(
            message,
            code=NotionErrorCode.API_ERROR,
            details={"status_code": status_code, "response": response_text[:500]},
            **kwargs,
        )
        self.status_code = status_code
        self.response_text = response_text


class NotionParseError(NotionError):
    """Raised when response parsing fails"""

    def __init__(self, message: str, raw_response: str, **kwargs):
        super().__init__(
            message,
            code=NotionErrorCode.PARSE_ERROR,
            details={"raw_response": raw_response[:500]},
            **kwargs,
        )


class NotionValidationError(NotionError):
    """Raised when data validation fails before sending to Notion"""

    def __init__(self, message: str, field: str, value: Any, **kwargs):
        super().__init__(
            message,
            code=NotionErrorCode.VALIDATION_ERROR,
            details={"field": field, "invalid_value": str(value)[:100]},
            **kwargs,
        )


class NotionNotFoundError(NotionError):
    """Raised when a resource is not found"""

    def __init__(self, message: str, resource_type: str, resource_id: str, **kwargs):
        super().__init__(
            message,
            code=NotionErrorCode.NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
            **kwargs,
        )


# Try to import notion client for advanced features
try:
    from notion_client import Client

    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    logging.warning("notion-client not available, using direct API calls")

# Try to import models for type validation
try:
    from src.models.account import Account
    from src.models.contact import Contact
    from src.models.strategic_partnership import StrategicPartnership
    from src.models.trigger_event import TriggerEvent

    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    logging.warning("ABM models not available, using dict-based operations")

logger = logging.getLogger(__name__)


class NotionClient:
    """
    Unified Notion client for ABM Research System
    Handles both workspace setup and data operations
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Notion client with unified API key handling

        Resolves API key naming confusion by checking multiple environment variables:
        - NOTION_API_KEY (preferred standard)
        - NOTION_ABM_API_KEY (legacy from abm_config)
        """
        self.setup_logging()

        # Unified API key resolution
        self.api_key = self._resolve_api_key(api_key)

        # Initialize clients
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        # Advanced client if available
        if NOTION_CLIENT_AVAILABLE:
            try:
                self.client = Client(auth=self.api_key)
                logger.info("✅ Advanced Notion client initialized")
            except Exception as e:
                logger.warning(f"Advanced client failed, using direct API: {e}")
                self.client = None
        else:
            self.client = None

        # Database configuration
        self.database_ids = self._load_database_config()

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 0.5  # 500ms between requests

        # Operation tracking for debugging
        self._last_operation = None
        self._operation_count = 0

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DATABASE ID PROPERTIES - Direct access without .get() chains
    # ═══════════════════════════════════════════════════════════════════════════════════

    @property
    def accounts_db(self) -> str:
        """Get accounts database ID or raise if not configured"""
        db_id = self.database_ids.get("accounts")
        if not db_id:
            raise NotionConfigError(
                "Accounts database not configured",
                missing_config="NOTION_ACCOUNTS_DB_ID",
                operation="get_accounts_db",
            )
        return db_id

    @property
    def contacts_db(self) -> str:
        """Get contacts database ID or raise if not configured"""
        db_id = self.database_ids.get("contacts")
        if not db_id:
            raise NotionConfigError(
                "Contacts database not configured",
                missing_config="NOTION_CONTACTS_DB_ID",
                operation="get_contacts_db",
            )
        return db_id

    @property
    def trigger_events_db(self) -> str:
        """Get trigger events database ID or raise if not configured"""
        db_id = self.database_ids.get("trigger_events")
        if not db_id:
            raise NotionConfigError(
                "Trigger events database not configured",
                missing_config="NOTION_TRIGGER_EVENTS_DB_ID",
                operation="get_trigger_events_db",
            )
        return db_id

    @property
    def partnerships_db(self) -> str:
        """Get partnerships database ID or raise if not configured"""
        db_id = self.database_ids.get("partnerships")
        if not db_id:
            raise NotionConfigError(
                "Partnerships database not configured",
                missing_config="NOTION_PARTNERSHIPS_DB_ID",
                operation="get_partnerships_db",
            )
        return db_id

    def require_database(self, db_name: str) -> str:
        """
        Get database ID with explicit requirement - raises if not configured.
        Use this instead of .get() to make failures explicit.
        """
        db_id = self.database_ids.get(db_name)
        if not db_id:
            raise NotionConfigError(
                f"{db_name} database not configured",
                missing_config=f"NOTION_{db_name.upper()}_DB_ID",
                operation=f"require_database({db_name})",
            )
        return db_id

    def _resolve_api_key(self, provided_key: Optional[str]) -> str:
        """Resolve API key from multiple possible sources"""
        if provided_key:
            return provided_key

        # Try standard name first
        api_key = os.getenv("NOTION_API_KEY")
        if api_key:
            logger.info("✅ Using NOTION_API_KEY")
            return api_key

        # Try legacy name
        api_key = os.getenv("NOTION_ABM_API_KEY")
        if api_key:
            logger.warning("⚠️  Using legacy NOTION_ABM_API_KEY, consider using NOTION_API_KEY")
            return api_key

        raise ValueError(
            "❌ Notion API key not found. Set either NOTION_API_KEY or NOTION_ABM_API_KEY"
        )

    def _load_database_config(self) -> dict[str, Optional[str]]:
        """Load database IDs from environment variables"""
        db_config = {
            "accounts": os.getenv("NOTION_ACCOUNTS_DB_ID"),
            "contacts": os.getenv("NOTION_CONTACTS_DB_ID"),
            "trigger_events": os.getenv("NOTION_TRIGGER_EVENTS_DB_ID")
            or os.getenv("NOTION_EVENTS_DB_ID"),
            "partnerships": os.getenv("NOTION_PARTNERSHIPS_DB_ID"),
        }

        # Log configuration status
        configured = [name for name, db_id in db_config.items() if db_id]
        missing = [name for name, db_id in db_config.items() if not db_id]

        if configured:
            logger.info(f"✅ Configured databases: {', '.join(configured)}")
        if missing:
            logger.warning(f"⚠️  Missing database IDs: {', '.join(missing)}")

        return db_config

    def setup_logging(self):
        """Setup logging for Notion operations"""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(
        self, method: str, url: str, operation: str = "api_request", **kwargs
    ) -> requests.Response:
        """
        Make rate-limited request to Notion API with proper error handling.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            url: Full URL to request
            operation: Name of the operation (for error context)
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            NotionAPIError: If the API returns an error response
            NotionError: For network errors or other failures
        """
        self._rate_limit()
        self._last_operation = operation
        self._operation_count += 1

        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", 30)  # 30 second timeout

        try:
            response = requests.request(method, url, **kwargs)
        except requests.exceptions.Timeout as e:
            raise NotionError(
                "Request timed out after 30 seconds",
                code=NotionErrorCode.NETWORK_ERROR,
                operation=operation,
                details={"url": url, "method": method},
                cause=e,
            )
        except requests.exceptions.ConnectionError as e:
            raise NotionError(
                "Failed to connect to Notion API",
                code=NotionErrorCode.NETWORK_ERROR,
                operation=operation,
                details={"url": url},
                cause=e,
            )
        except requests.exceptions.RequestException as e:
            raise NotionError(
                f"Request failed: {str(e)}",
                code=NotionErrorCode.NETWORK_ERROR,
                operation=operation,
                cause=e,
            )

        # Check for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise NotionError(
                f"Rate limited. Retry after {retry_after} seconds",
                code=NotionErrorCode.RATE_LIMITED,
                operation=operation,
                details={"retry_after": retry_after},
            )

        # Check for API errors
        if not response.ok:
            error_msg = f"Notion API returned {response.status_code}"
            logger.error(f"❌ {operation}: {error_msg} - {response.text[:500]}")
            raise NotionAPIError(
                error_msg,
                status_code=response.status_code,
                response_text=response.text,
                operation=operation,
            )

        return response

    def _parse_json_response(
        self, response: requests.Response, operation: str = "parse_response"
    ) -> dict[str, Any]:
        """
        Safely parse JSON from response with proper error handling.

        NEVER silently return empty dict/list on parse failure.
        """
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise NotionParseError(
                f"Failed to parse JSON response: {str(e)}",
                raw_response=response.text[:500],
                operation=operation,
                cause=e,
            )

    def _extract_results(
        self, response: requests.Response, operation: str = "extract_results"
    ) -> list[dict]:
        """
        Extract 'results' array from Notion query response with validation.

        Raises if response doesn't contain expected structure instead of
        silently returning empty list.
        """
        data = self._parse_json_response(response, operation)

        if "results" not in data:
            # Log warning but don't fail - some endpoints don't return results
            logger.warning(
                f"⚠️ {operation}: Response missing 'results' key. "
                f"Keys present: {list(data.keys())}"
            )
            return []

        results = data["results"]
        if not isinstance(results, list):
            raise NotionParseError(
                f"Expected 'results' to be a list, got {type(results).__name__}",
                raw_response=str(results)[:500],
                operation=operation,
            )

        return results

    def _extract_page_id(
        self, response: requests.Response, operation: str = "extract_page_id"
    ) -> str:
        """
        Extract page ID from create/update response with validation.

        NEVER returns None silently - raises on failure.
        """
        data = self._parse_json_response(response, operation)

        page_id = data.get("id")
        if not page_id:
            raise NotionParseError(
                "Response missing 'id' field for created/updated page",
                raw_response=str(data)[:500],
                operation=operation,
            )

        return page_id

    # ═══════════════════════════════════════════════════════════════════════════════════
    # WORKSPACE SETUP (from notion_database.py)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def setup_abm_workspace(self, parent_page_id: str) -> dict[str, str]:
        """
        Create complete ABM research workspace with all 5 databases

        Args:
            parent_page_id: Notion page ID where databases should be created

        Returns:
            Dictionary mapping database names to their IDs
        """
        logger.info("🏗️ Setting up ABM Research workspace in Notion...")

        try:
            databases = {}

            # Create all databases
            databases["accounts"] = self._create_accounts_database(parent_page_id)["id"]
            databases["trigger_events"] = self._create_trigger_events_database(parent_page_id)["id"]
            databases["contacts"] = self._create_contacts_database(parent_page_id)["id"]
            databases["partnerships"] = self._create_partnerships_database(parent_page_id)["id"]

            # Update local configuration
            self.database_ids.update(databases)

            logger.info(f"✅ ABM workspace created successfully with {len(databases)} databases")
            return databases

        except Exception as e:
            logger.error(f"❌ Failed to create ABM workspace: {str(e)}")
            raise

    def _create_accounts_database(self, parent_page_id: str) -> dict[str, Any]:
        """Create Accounts database with complete schema"""
        properties = {
            "Company Name": {"title": {}},
            "Domain": {"rich_text": {}},
            "Employee Count": {"number": {"format": "number"}},
            "Industry": {
                "select": {
                    "options": [
                        {"name": "Technology", "color": "blue"},
                        {"name": "Healthcare", "color": "green"},
                        {"name": "Finance", "color": "yellow"},
                        {"name": "Manufacturing", "color": "orange"},
                        {"name": "Retail", "color": "red"},
                        {"name": "Other", "color": "gray"},
                    ]
                }
            },
            "ICP Fit Score": {"number": {"format": "number"}},
            "Research Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Completed", "color": "green"},
                        {"name": "On Hold", "color": "red"},
                    ]
                }
            },
            "Last Updated": {"date": {}},
            "Notes": {"rich_text": {}},
            # Enhanced Account Intelligence Fields
            "Recent Leadership Changes": {"rich_text": {}},
            "Key Decision Makers": {"rich_text": {}},
            "Recent Funding": {"rich_text": {}},
            "Growth Stage": {
                "select": {
                    "options": [
                        {"name": "Startup", "color": "green"},
                        {"name": "Scale-Up", "color": "blue"},
                        {"name": "Growth", "color": "purple"},
                        {"name": "Mature", "color": "orange"},
                        {"name": "Enterprise", "color": "red"},
                    ]
                }
            },
            "Hiring Velocity": {"rich_text": {}},
            "Physical Infrastructure": {"rich_text": {}},
            "Competitor Tools": {"rich_text": {}},
            "Recent Announcements": {"rich_text": {}},
            "Conversation Triggers": {"rich_text": {}},
        }

        return self._create_database(parent_page_id, "🏢 Accounts", properties)

    def _create_contacts_database(self, parent_page_id: str) -> dict[str, Any]:
        """Create Contacts database with complete schema"""
        properties = {
            "Name": {"title": {}},
            "Company": {"rich_text": {}},
            "Title": {"rich_text": {}},
            "Email": {"email": {}},
            "LinkedIn URL": {"url": {}},
            "Lead Score": {"number": {"format": "number"}},
            "Engagement Level": {
                "select": {
                    "options": [
                        {"name": "Very High", "color": "red"},
                        {"name": "High", "color": "orange"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "gray"},
                    ]
                }
            },
            "Contact Date": {"date": {}},
            "Notes": {"rich_text": {}},
            # Data Provenance & Quality Fields
            "Name Source": {
                "select": {
                    "options": [
                        {"name": "apollo", "color": "blue"},
                        {"name": "linkedin", "color": "green"},
                        {"name": "merged", "color": "purple"},
                        {"name": "manual", "color": "gray"},
                    ]
                }
            },
            "Email Source": {
                "select": {
                    "options": [
                        {"name": "apollo", "color": "blue"},
                        {"name": "linkedin", "color": "green"},
                        {"name": "inferred", "color": "yellow"},
                        {"name": "manual", "color": "gray"},
                    ]
                }
            },
            "Title Source": {
                "select": {
                    "options": [
                        {"name": "apollo", "color": "blue"},
                        {"name": "linkedin", "color": "green"},
                        {"name": "merged", "color": "purple"},
                        {"name": "manual", "color": "gray"},
                    ]
                }
            },
            "Data Quality Score": {"number": {"format": "number"}},
            "Last Enriched": {"date": {}},
        }

        return self._create_database(parent_page_id, "👤 Contacts", properties)

    def _create_trigger_events_database(self, parent_page_id: str) -> dict[str, Any]:
        """Create Trigger Events database with complete schema"""
        properties = {
            "Event Description": {"title": {}},
            "Company": {"rich_text": {}},
            "Event Type": {
                "select": {
                    "options": [
                        {"name": "expansion", "color": "green"},
                        {"name": "leadership_change", "color": "blue"},
                        {"name": "ai_workload", "color": "purple"},
                        {"name": "energy_pressure", "color": "yellow"},
                        {"name": "incident", "color": "red"},
                        {"name": "sustainability", "color": "green"},
                    ]
                }
            },
            "Confidence": {
                "select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"},
                    ]
                }
            },
            "Urgency": {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "gray"},
                    ]
                }
            },
            "Source URL": {"url": {}},
            "Detected Date": {"date": {}},
            "Relevance Score": {"number": {"format": "number"}},
        }

        return self._create_database(parent_page_id, "⚡ Trigger Events", properties)

    def _create_contact_intelligence_database(self, parent_page_id: str) -> dict[str, Any]:
        """Create Contact Intelligence database"""
        properties = {
            "Contact Name": {"title": {}},
            "Analysis Type": {
                "select": {
                    "options": [
                        {"name": "Engagement Intelligence", "color": "blue"},
                        {"name": "Buying Signal", "color": "green"},
                        {"name": "Contact Value", "color": "yellow"},
                    ]
                }
            },
            "Intelligence Data": {"rich_text": {}},
            "Confidence Score": {"number": {"format": "number"}},
            "Generated Date": {"date": {}},
            "Source": {"rich_text": {}},
        }

        return self._create_database(parent_page_id, "🧠 Contact Intelligence", properties)

    def _create_partnerships_database(self, parent_page_id: str) -> dict[str, Any]:
        """Create Strategic Partnerships database"""
        properties = {
            "Partner Name": {"title": {}},
            "Partnership Type": {
                "select": {
                    "options": [
                        {"name": "Technology Integration", "color": "blue"},
                        {"name": "Reseller", "color": "green"},
                        {"name": "Strategic Alliance", "color": "purple"},
                        {"name": "Vendor Relationship", "color": "orange"},
                    ]
                }
            },
            "Relevance Score": {"number": {"format": "number"}},
            "Context": {"rich_text": {}},
            "Source URL": {"url": {}},
            "Discovered Date": {"date": {}},
        }

        return self._create_database(parent_page_id, "🤝 Strategic Partnerships", properties)

    def _create_database(self, parent_page_id: str, title: str, properties: dict) -> dict[str, Any]:
        """Create a database with given properties"""
        data = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties,
        }

        response = self._make_request("POST", "https://api.notion.com/v1/databases", json=data)
        return response.json()

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DATA PERSISTENCE - Fixed to NEVER silently fail
    # ═══════════════════════════════════════════════════════════════════════════════════

    def save_account(self, account: dict[str, Any]) -> str:
        """
        Save account data with deduplication.

        Returns:
            Page ID of created/updated account

        Raises:
            NotionConfigError: If accounts database not configured
            NotionAPIError: If API call fails
            NotionValidationError: If account data is invalid
        """
        # Use property accessor to ensure config - raises if not configured
        _ = self.accounts_db

        account_name = account.get("name", "")
        if not account_name:
            raise NotionValidationError(
                "Account must have a name",
                field="name",
                value=account_name,
                operation="save_account",
            )

        try:
            # Check for existing account
            existing_id = self._find_existing_account(account_name)
            if existing_id:
                logger.info(f"Account {account_name} already exists, updating...")
                result = self._update_account(existing_id, account)
                if not result:
                    raise NotionError(
                        f"Failed to update existing account: {account_name}",
                        operation="save_account",
                    )
                return result
            else:
                result = self._create_account(account)
                if not result:
                    raise NotionError(
                        f"Failed to create account: {account_name}", operation="save_account"
                    )
                return result

        except NotionError:
            raise
        except Exception as e:
            raise NotionError(
                f"Unexpected error saving account: {str(e)}",
                operation="save_account",
                details={"account_name": account_name},
                cause=e,
            )

    def save_contacts(
        self, contacts: list[dict], account_name: str = "", fail_fast: bool = False
    ) -> dict[str, Any]:
        """
        Save enriched contact data with deduplication.

        Args:
            contacts: List of contact dictionaries
            account_name: Name of account to associate contacts with
            fail_fast: If True, raise on first error. If False, collect errors and continue.

        Returns:
            Dict with 'results' (per-contact status), 'saved', 'failed', 'errors'

        Raises:
            NotionConfigError: If contacts database not configured
            NotionError: If fail_fast=True and any contact fails
        """
        logger.info(f"💾 Saving {len(contacts)} contacts to Notion")

        # Use property accessor to ensure config - raises if not configured
        _ = self.contacts_db

        results = {"results": {}, "saved": 0, "failed": 0, "skipped": 0, "errors": []}

        for contact in contacts:
            contact_name = contact.get("name", "unknown")
            try:
                # Skip contacts without lead score (not enriched)
                if not contact.get("final_lead_score") and not contact.get("lead_score"):
                    logger.info(f"Skipping {contact_name} - no lead score")
                    results["skipped"] += 1
                    results["results"][contact_name] = {
                        "status": "skipped",
                        "reason": "no_lead_score",
                    }
                    continue

                # Check for existing contact
                existing_id = self._find_existing_contact(contact.get("linkedin_url", ""))

                if existing_id:
                    page_id = self._update_contact(existing_id, contact)
                else:
                    page_id = self._create_contact(contact, account_name)

                if page_id:
                    results["saved"] += 1
                    results["results"][contact_name] = {"status": "saved", "page_id": page_id}
                else:
                    raise NotionError(
                        f"No page ID returned for {contact_name}", operation="save_contacts"
                    )

            except NotionError as e:
                results["failed"] += 1
                results["errors"].append({"contact": contact_name, "error": e.to_dict()})
                results["results"][contact_name] = {"status": "failed", "error": str(e)}
                logger.error(f"❌ Failed to save contact {contact_name}: {e}")
                if fail_fast:
                    raise
            except Exception as e:
                results["failed"] += 1
                err_info = {
                    "contact": contact_name,
                    "error": {"message": str(e), "type": type(e).__name__},
                }
                results["errors"].append(err_info)
                results["results"][contact_name] = {"status": "failed", "error": str(e)}
                logger.error(f"❌ Unexpected error saving contact {contact_name}: {e}")
                if fail_fast:
                    raise NotionError(
                        f"Failed to save contact: {str(e)}", operation="save_contacts", cause=e
                    )

        logger.info(
            f"✅ Contacts: {results['saved']} saved, {results['failed']} failed, {results['skipped']} skipped"
        )

        # Raise if ALL contacts failed (indicates systemic issue)
        if len(contacts) > 0 and results["saved"] == 0 and results["skipped"] < len(contacts):
            raise NotionError(
                f"All {results['failed']} contact saves failed - check Notion connection",
                operation="save_contacts",
                details={"errors": results["errors"][:5]},  # Include first 5 errors
            )

        return results

    def save_trigger_events(
        self, events: list[dict], account_name: str = "", fail_fast: bool = False
    ) -> dict[str, Any]:
        """
        Save trigger events data.

        Returns:
            Dict with 'results', 'saved', 'failed', 'errors'

        Raises:
            NotionConfigError: If trigger_events database not configured
            NotionError: If fail_fast=True and any event fails, or if ALL events fail
        """
        # Use property accessor to ensure config - raises if not configured
        _ = self.trigger_events_db

        results = {"results": {}, "saved": 0, "failed": 0, "errors": []}

        for event in events:
            event_desc = event.get("description", event.get("event_description", "unknown"))[:50]
            try:
                page_id = self._create_trigger_event(event, account_name)
                if page_id:
                    results["saved"] += 1
                    results["results"][event_desc] = {"status": "saved", "page_id": page_id}
                else:
                    raise NotionError(
                        "No page ID returned for event", operation="save_trigger_events"
                    )

            except NotionError as e:
                results["failed"] += 1
                results["errors"].append({"event": event_desc, "error": e.to_dict()})
                results["results"][event_desc] = {"status": "failed", "error": str(e)}
                if fail_fast:
                    raise
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"event": event_desc, "error": str(e)})
                results["results"][event_desc] = {"status": "failed", "error": str(e)}
                if fail_fast:
                    raise NotionError(
                        f"Failed to save event: {str(e)}", operation="save_trigger_events", cause=e
                    )

        # Raise if ALL events failed
        if len(events) > 0 and results["saved"] == 0:
            raise NotionError(
                f"All {results['failed']} trigger event saves failed",
                operation="save_trigger_events",
                details={"errors": results["errors"][:5]},
            )

        return results

    def save_partnerships(
        self, partnerships: list[dict], account_name: str = "", fail_fast: bool = False
    ) -> dict[str, Any]:
        """
        Save strategic partnerships data.

        Returns:
            Dict with 'results', 'saved', 'failed', 'errors'

        Raises:
            NotionConfigError: If partnerships database not configured
            NotionError: If fail_fast=True and any partnership fails, or if ALL fail
        """
        # Use property accessor to ensure config - raises if not configured
        _ = self.partnerships_db

        results = {"results": {}, "saved": 0, "failed": 0, "errors": []}

        for partnership in partnerships:
            partner_name = partnership.get("partner_name", partnership.get("name", "unknown"))
            try:
                page_id = self._create_partnership(partnership, account_name)
                if page_id:
                    results["saved"] += 1
                    results["results"][partner_name] = {"status": "saved", "page_id": page_id}
                else:
                    raise NotionError(
                        "No page ID returned for partnership", operation="save_partnerships"
                    )

            except NotionError as e:
                results["failed"] += 1
                results["errors"].append({"partner": partner_name, "error": e.to_dict()})
                results["results"][partner_name] = {"status": "failed", "error": str(e)}
                if fail_fast:
                    raise
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"partner": partner_name, "error": str(e)})
                results["results"][partner_name] = {"status": "failed", "error": str(e)}
                if fail_fast:
                    raise NotionError(
                        f"Failed to save partnership: {str(e)}",
                        operation="save_partnerships",
                        cause=e,
                    )

        # Raise if ALL partnerships failed
        if len(partnerships) > 0 and results["saved"] == 0:
            raise NotionError(
                f"All {results['failed']} partnership saves failed",
                operation="save_partnerships",
                details={"errors": results["errors"][:5]},
            )

        return results

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DEDUPLICATION HELPERS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _find_existing_account(self, company_name: str) -> Optional[str]:
        """Find existing account by company name"""
        if not self.database_ids.get("accounts") or not company_name:
            return None

        try:
            query = {"filter": {"property": "Name", "title": {"equals": company_name}}}

            url = f"https://api.notion.com/v1/databases/{self.database_ids['accounts']}/query"
            response = self._make_request("POST", url, json=query)

            results = response.json().get("results", [])
            return results[0]["id"] if results else None

        except Exception as e:
            logger.error(f"Error finding existing account: {e}")
            return None

    def query_all_accounts(self) -> list[dict]:
        """
        Query all accounts from Notion database.

        Raises:
            NotionConfigError: If accounts database not configured
            NotionAPIError: If API call fails
        """
        # Use property accessor to ensure config - raises if not configured
        db_id = self.accounts_db

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = self._make_request("POST", url, json={}, operation="query_all_accounts")

        results = self._extract_results(response, "query_all_accounts")
        logger.info(f"✅ Retrieved {len(results)} accounts from Notion")
        return results

    def query_all_contacts(self, account_id: Optional[str] = None) -> list[dict]:
        """
        Query all contacts from Notion database, optionally filtered by account.

        Raises:
            NotionConfigError: If contacts database not configured
            NotionAPIError: If API call fails
        """
        # Use property accessor to ensure config - raises if not configured
        db_id = self.contacts_db

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        query = {}

        # Filter by account relation if provided
        if account_id:
            query = {"filter": {"property": "Account", "relation": {"contains": account_id}}}

        response = self._make_request("POST", url, json=query, operation="query_all_contacts")

        results = self._extract_results(response, "query_all_contacts")
        logger.info(f"✅ Retrieved {len(results)} contacts from Notion")
        return results

    def query_all_trigger_events(self, account_id: Optional[str] = None) -> list[dict]:
        """
        Query all trigger events from Notion database, optionally filtered by account.

        Raises:
            NotionConfigError: If trigger_events database not configured
            NotionAPIError: If API call fails
        """
        # Use property accessor to ensure config - raises if not configured
        db_id = self.trigger_events_db

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        query = {}

        # Filter by account relation if provided
        if account_id:
            query = {"filter": {"property": "Account", "relation": {"contains": account_id}}}

        response = self._make_request("POST", url, json=query, operation="query_all_trigger_events")

        results = self._extract_results(response, "query_all_trigger_events")
        logger.info(f"✅ Retrieved {len(results)} trigger events from Notion")
        return results

    def query_all_partnerships(self, account_id: Optional[str] = None) -> list[dict]:
        """
        Query all partnerships from Notion database, optionally filtered by account.

        Raises:
            NotionConfigError: If partnerships database not configured
            NotionAPIError: If API call fails
        """
        # Use property accessor to ensure config - raises if not configured
        db_id = self.partnerships_db

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        query = {}

        # Filter by account relation if provided
        if account_id:
            query = {"filter": {"property": "Account", "relation": {"contains": account_id}}}

        response = self._make_request("POST", url, json=query, operation="query_all_partnerships")

        results = self._extract_results(response, "query_all_partnerships")
        logger.info(f"✅ Retrieved {len(results)} partnerships from Notion")
        return results

    def _find_existing_contact(self, linkedin_url: str) -> Optional[str]:
        """
        Find existing contact by LinkedIn URL.

        Returns None for empty linkedin_url (not an error).
        Raises for actual failures.
        """
        if not linkedin_url:
            return None

        # Use property accessor to ensure config - raises if not configured
        db_id = self.contacts_db

        query = {"filter": {"property": "LinkedIn URL", "url": {"equals": linkedin_url}}}

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        response = self._make_request("POST", url, json=query, operation="find_existing_contact")

        results = self._extract_results(response, "find_existing_contact")
        return results[0]["id"] if results else None

    # ═══════════════════════════════════════════════════════════════════════════════════
    # CREATE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _create_account(self, account: dict) -> Optional[str]:
        """Create new account record using actual production database field names"""
        properties = {
            # Core fields (using ACTUAL production field names)
            "Name": {"title": [{"text": {"content": account.get("name", "Unknown")}}]},
            "Domain": {"rich_text": [{"text": {"content": account.get("domain", "")}}]},
            "Business Model": {"select": {"name": account.get("business_model", "Technology")}},
            "Employee Count": {"number": account.get("employee_count", 0)},
            "ICP Fit Score": {"number": account.get("icp_fit_score", 0)},
            "Account Research Status": {"select": {"name": "Research Complete"}},
            "Last Updated": {"date": {"start": datetime.now().isoformat()}},
            # Physical Infrastructure - key field for ICP scoring (displayed in dashboard)
            "Physical Infrastructure": {
                "rich_text": [
                    {"text": {"content": account.get("Physical Infrastructure", "")[:2000]}}
                ]
            }
            # REMOVED per schema cleanup: Recent Leadership Changes, Recent Funding, Growth Stage,
            # Recent Announcements, Hiring Velocity, Conversation Triggers, Key Decision Makers, Competitor Tools
        }

        data = {"parent": {"database_id": self.database_ids["accounts"]}, "properties": properties}

        response = self._make_request("POST", "https://api.notion.com/v1/pages", json=data)
        return response.json().get("id")

    def _create_contact(self, contact: dict, account_name: str = "") -> Optional[str]:
        """Create new contact record with proper Account relation and enhanced fields"""
        # Handle URL field properly - use null instead of empty string
        linkedin_url = contact.get("linkedin_url", "") or None

        # CRITICAL FIX: Find the actual account to create proper relation
        account_id = None
        if account_name:
            account_id = self._find_existing_account(account_name)

        properties = {
            # Core fields using production schema
            "Name": {"title": [{"text": {"content": contact.get("name", "Unknown")}}]},
            "Email": {"email": contact.get("email", "")},
            "Title": {"rich_text": [{"text": {"content": contact.get("title", "")}}]},
            "ICP Fit Score": {
                "number": contact.get("final_lead_score", contact.get("lead_score", 0))
            },
            # New enhanced data provenance fields
            "Name Source": {"select": {"name": contact.get("name_source", "apollo")}},
            "Email Source": {"select": {"name": contact.get("email_source", "apollo")}},
            "Title Source": {"select": {"name": contact.get("title_source", "apollo")}},
            "Data Quality Score": {"number": contact.get("data_quality_score", 80)},
            "Last Enriched": {"date": {"start": datetime.now().isoformat()}},
            "Lead Score": {"number": contact.get("final_lead_score", contact.get("lead_score", 0))},
            "Engagement Level": {"select": {"name": contact.get("engagement_level", "Medium")}},
            "Contact Date": {"date": {"start": datetime.now().isoformat()}},
            "LinkedIn URL": {"url": linkedin_url},
            "Notes": {"rich_text": [{"text": {"content": contact.get("notes", "")}}]},
        }

        # CRITICAL FIX: Use proper Account relation instead of rich_text
        if account_id:
            properties["Account"] = {"relation": [{"id": account_id}]}
        else:
            # Fallback: Add account name as rich_text for manual linking
            properties["Account Name (Fallback)"] = {
                "rich_text": [{"text": {"content": account_name or "Unknown Account"}}]
            }

        data = {"parent": {"database_id": self.database_ids["contacts"]}, "properties": properties}

        response = self._make_request("POST", "https://api.notion.com/v1/pages", json=data)
        return response.json().get("id")

    def _create_trigger_event(self, event: dict, account_name: str = "") -> Optional[str]:
        """Create new trigger event record with proper Account relation and enhanced multi-dimensional intelligence"""
        # Handle URL field properly - use null instead of empty string
        source_url = event.get("source_url", "") or None

        # CRITICAL FIX: Find the actual account to create proper relation
        account_id = None
        if account_name:
            account_id = self._find_existing_account(account_name)

        properties = {
            # Core fields using production schema
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": event.get(
                                "description", event.get("event_description", "Unknown Event")
                            )
                        }
                    }
                ]
            },
            "Event Type": {"select": {"name": event.get("event_type", "other")}},
            "Confidence": {"select": {"name": event.get("confidence", "Medium")}},
            "Source URL": {"url": source_url},
            "Detected Date": {
                "date": {"start": event.get("detected_date", datetime.now().strftime("%Y-%m-%d"))}
            },
            # NEW: Multi-Dimensional Scoring System
            "Business Impact Score": {"number": event.get("business_impact_score", 50)},
            "Actionability Score": {"number": event.get("actionability_score", 50)},
            "Timing Urgency Score": {"number": event.get("timing_urgency_score", 50)},
            "Strategic Fit Score": {"number": event.get("strategic_fit_score", 50)},
            # NEW: Time Intelligence Fields
            "Action Deadline": {
                "date": {"start": event.get("action_deadline", "")}
                if event.get("action_deadline")
                else None
            },
            "Peak Relevance Window": {
                "date": {"start": event.get("peak_relevance_window", "")}
                if event.get("peak_relevance_window")
                else None
            },
            "Decay Rate": {"select": {"name": event.get("decay_rate", "Medium")}},
            # NEW: Event Lifecycle Tracking
            "Event Stage": {"select": {"name": event.get("event_stage", "Announced")}},
            "Follow-up Actions": {
                "rich_text": [{"text": {"content": event.get("follow_up_actions", "")}}]
            },
            "Urgency Level": {"select": {"name": event.get("urgency_level", "Medium")}},
        }

        # CRITICAL FIX: Use proper Account relation instead of rich_text
        if account_id:
            properties["Account"] = {"relation": [{"id": account_id}]}
        else:
            # Fallback: Add account name as rich_text for manual linking
            properties["Account Name (Fallback)"] = {
                "rich_text": [{"text": {"content": account_name or "Unknown Account"}}]
            }

        # Remove None values to avoid API errors
        properties = {k: v for k, v in properties.items() if v is not None}

        data = {
            "parent": {"database_id": self.database_ids["trigger_events"]},
            "properties": properties,
        }

        response = self._make_request("POST", "https://api.notion.com/v1/pages", json=data)
        return response.json().get("id")

    def _create_partnership(self, partnership: dict, account_name: str = "") -> Optional[str]:
        """Create or update partnership record with automatic deduplication.

        If a partnership with the same vendor name already exists, adds the new account
        to its relation list instead of creating a duplicate record.

        Uses the ACTUAL Notion database schema fields:
        - Name (title): Partner/vendor name
        - Category (select): Partnership type
        - Priority Score (number): Confidence/relevance score
        - Relationship Evidence (rich_text): Context/reasoning
        - Evidence URL (url): Source URL
        - Detected Date (date): When discovered
        - Relationship Depth (select): Integration level
        - Partnership Maturity (select): Relationship stage
        - Best Approach (select): Recommended strategy
        - Account (relation): Link to account(s) - supports multiple
        """
        # Get source URL and ensure it's either a valid URL or null (not empty string)
        source_url = partnership.get("source_url", partnership.get("evidence_url", "")) or None

        # Find the account to create proper relation
        account_id = None
        partner_name = partnership.get(
            "partner_name",
            partnership.get("name", partnership.get("account_name", "Unknown Partner")),
        )
        if account_name:
            account_id = self._find_existing_account(account_name)
            if account_id:
                logger.info(f"🔗 Linking partnership '{partner_name}' to account '{account_name}'")
            else:
                logger.warning(
                    f"⚠️ Could not find account '{account_name}' for partnership relation"
                )

        # CHECK FOR EXISTING PARTNERSHIP BY VENDOR NAME (automatic deduplication)
        existing_partnership_id = self._find_existing_partnership(partner_name)
        if existing_partnership_id and account_id:
            # Partnership exists - add this account to its relation list
            logger.info(f"📎 Found existing partnership '{partner_name}', adding account relation")
            return self._add_account_to_partnership(
                existing_partnership_id, account_id, partner_name
            )

        # Use ACTUAL database field names (verified from schema)
        properties = {
            # Core fields using actual schema
            "Name": {"title": [{"text": {"content": partner_name}}]},
            "Category": {
                "select": {
                    "name": partnership.get(
                        "partnership_type", partnership.get("category", "Strategic Alliance")
                    )
                }
            },
            "Priority Score": {
                "number": partnership.get(
                    "confidence_score",
                    partnership.get("relevance_score", partnership.get("priority_score", 0)),
                )
            },
            "Relationship Evidence": {
                "rich_text": [
                    {
                        "text": {
                            "content": partnership.get(
                                "reasoning",
                                partnership.get(
                                    "context", partnership.get("relationship_evidence", "")
                                ),
                            )[:2000]
                        }
                    }
                ]
            },
            "Detected Date": {
                "date": {
                    "start": partnership.get("detected_date", datetime.now().strftime("%Y-%m-%d"))
                }
            },
            # Partnership strategy fields
            "Relationship Depth": {
                "select": {"name": partnership.get("relationship_depth", "Surface Integration")}
            },
            "Partnership Maturity": {
                "select": {"name": partnership.get("partnership_maturity", "Basic")}
            },
            "Best Approach": {
                "select": {"name": partnership.get("best_approach", "Technical Discussion")}
            },
        }

        # Add Evidence URL if provided
        if source_url:
            properties["Evidence URL"] = {"url": source_url}

        # Add Account relation if found
        if account_id:
            properties["Account"] = {"relation": [{"id": account_id}]}

        data = {
            "parent": {"database_id": self.database_ids["partnerships"]},
            "properties": properties,
        }

        response = self._make_request("POST", "https://api.notion.com/v1/pages", json=data)
        return response.json().get("id")

    # ═══════════════════════════════════════════════════════════════════════════════════
    # DEDUPLICATION - _find_existing_partnership
    # ═══════════════════════════════════════════════════════════════════════════════════

    def _find_existing_partnership(
        self, partner_name: str, account_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Find existing partnership by partner name (and optionally account relation).

        Uses "Name" field (the actual title field in the database schema).

        Args:
            partner_name: Name of the partner/vendor to search for
            account_id: Optional account ID to filter by

        Returns:
            Page ID if found, None if not found

        Raises:
            NotionConfigError: If partnerships database not configured
            NotionAPIError: If API call fails
        """
        if not partner_name:
            return None

        # Use property to ensure config is valid (raises if not)
        db_id = self.partnerships_db

        try:
            # Build filter using "Name" (the actual title field in schema)
            filter_condition = {"property": "Name", "title": {"equals": partner_name}}

            # If account_id provided, add compound filter
            if account_id:
                filter_condition = {
                    "and": [
                        {"property": "Name", "title": {"equals": partner_name}},
                        {"property": "Account", "relation": {"contains": account_id}},
                    ]
                }

            query = {"filter": filter_condition}
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            response = self._make_request(
                "POST", url, json=query, operation=f"find_existing_partnership({partner_name})"
            )

            results = self._extract_results(response, "find_existing_partnership")
            if results:
                logger.info(f"🔍 Found existing partnership: {partner_name}")
                return results[0]["id"]

            return None

        except NotionError:
            # Re-raise Notion errors with context intact
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise NotionError(
                f"Unexpected error finding partnership: {str(e)}",
                operation="find_existing_partnership",
                details={"partner_name": partner_name},
                cause=e,
            )

    def _find_existing_partnership_by_vendor(
        self, vendor_name: str, account_id: Optional[str] = None
    ) -> Optional[str]:
        """Alias for _find_existing_partnership for semantic clarity"""
        return self._find_existing_partnership(vendor_name, account_id)

    def _add_account_to_partnership(
        self, partnership_id: str, account_id: str, partner_name: str = ""
    ) -> str:
        """
        Add an account to an existing partnership's relation list.

        This enables the many-to-many relationship where one vendor/partner
        can be associated with multiple target accounts. Instead of creating
        duplicate partnership records, we add new accounts to the existing record.

        Args:
            partnership_id: The Notion page ID of the existing partnership
            account_id: The account ID to add to the relation
            partner_name: Optional name for logging (not used in update)

        Returns:
            The partnership_id (same as input, for consistency with _create_partnership)

        Raises:
            NotionAPIError: If the update fails
        """
        try:
            # First, get the current account relations from the partnership
            url = f"https://api.notion.com/v1/pages/{partnership_id}"
            response = self._make_request(
                "GET", url, operation=f"get_partnership_relations({partner_name or partnership_id})"
            )

            page_data = response.json()
            current_relations = (
                page_data.get("properties", {}).get("Account", {}).get("relation", [])
            )

            # Extract existing account IDs
            existing_account_ids = {rel["id"] for rel in current_relations}

            # Check if account is already linked
            if account_id in existing_account_ids:
                logger.info(f"📎 Account already linked to '{partner_name}', skipping")
                return partnership_id

            # Add new account to the relation list
            updated_relations = list(current_relations) + [{"id": account_id}]

            # Update the partnership with merged relations
            update_url = f"https://api.notion.com/v1/pages/{partnership_id}"
            self._make_request(
                "PATCH",
                update_url,
                json={"properties": {"Account": {"relation": updated_relations}}},
                operation=f"add_account_to_partnership({partner_name or partnership_id})",
            )

            logger.info(
                f"✓ Added account to existing partnership '{partner_name}' (now {len(updated_relations)} accounts)"
            )
            return partnership_id

        except NotionError:
            raise
        except Exception as e:
            raise NotionError(
                f"Failed to add account to partnership: {str(e)}",
                operation="_add_account_to_partnership",
                details={"partnership_id": partnership_id, "account_id": account_id},
                cause=e,
            )

    # ═══════════════════════════════════════════════════════════════════════════════════
    # UPDATE OPERATIONS - Including the critical update_page() method
    # ═══════════════════════════════════════════════════════════════════════════════════

    def update_page(self, page_id: str, properties: dict[str, Any], validate: bool = True) -> str:
        """
        Update a Notion page with new property values.

        This is the CRITICAL method that was missing and causing silent failures
        in email reveal, research pipeline, and other update operations.

        Args:
            page_id: The Notion page ID to update
            properties: Dictionary of properties to update (Notion API format)
            validate: If True, validate properties before sending

        Returns:
            The page ID if successful

        Raises:
            NotionValidationError: If page_id is invalid
            NotionAPIError: If API call fails
            NotionError: For other errors
        """
        if not page_id:
            raise NotionValidationError(
                "Cannot update page without page_id",
                field="page_id",
                value=page_id,
                operation="update_page",
            )

        if not properties:
            logger.warning(f"⚠️ update_page called with empty properties for {page_id}")
            return page_id  # No-op but not an error

        # Convert simple dict format to Notion property format if needed
        formatted_props = self._format_properties_for_update(properties)

        try:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            response = self._make_request(
                "PATCH",
                url,
                json={"properties": formatted_props},
                operation=f"update_page({page_id[:8]}...)",
            )

            result_id = self._extract_page_id(response, "update_page")
            logger.info(f"✅ Updated page {page_id[:8]}... with {len(properties)} properties")
            return result_id

        except NotionError:
            raise
        except Exception as e:
            raise NotionError(
                f"Failed to update page: {str(e)}",
                operation="update_page",
                details={"page_id": page_id, "property_count": len(properties)},
                cause=e,
            )

    def _format_properties_for_update(self, properties: dict[str, Any]) -> dict[str, Any]:
        """
        Format properties for Notion update API.

        Handles both pre-formatted Notion properties and simple key-value pairs.
        """
        formatted = {}

        for key, value in properties.items():
            # If already in Notion format (has type key), use as-is
            if isinstance(value, dict) and any(
                k in value
                for k in [
                    "title",
                    "rich_text",
                    "number",
                    "select",
                    "multi_select",
                    "date",
                    "email",
                    "url",
                    "checkbox",
                    "relation",
                    "phone_number",
                ]
            ):
                formatted[key] = value
            # Simple value - try to infer type
            elif isinstance(value, str):
                # Check if it looks like an email
                if "@" in value and "." in value:
                    formatted[key] = {"email": value}
                # Check if it looks like a URL
                elif value.startswith("http://") or value.startswith("https://"):
                    formatted[key] = {"url": value}
                else:
                    formatted[key] = {"rich_text": [{"text": {"content": value[:2000]}}]}
            elif isinstance(value, (int, float)):
                formatted[key] = {"number": value}
            elif isinstance(value, bool):
                formatted[key] = {"checkbox": value}
            elif isinstance(value, datetime):
                formatted[key] = {"date": {"start": value.isoformat()}}
            elif value is None:
                # Skip None values
                continue
            else:
                # Fallback to rich_text
                formatted[key] = {"rich_text": [{"text": {"content": str(value)[:2000]}}]}

        return formatted

    def _update_account(self, page_id: str, account: dict) -> Optional[str]:
        """Update existing account record"""
        try:
            properties = {
                "Name": {"title": [{"text": {"content": account.get("name", "Unknown")}}]},
                "Domain": {"rich_text": [{"text": {"content": account.get("domain", "")}}]},
                "Business Model": {"select": {"name": account.get("business_model", "Technology")}},
                "Employee Count": {"number": account.get("employee_count", 0)},
                "ICP Fit Score": {"number": account.get("icp_fit_score", 0)},
                "Account Research Status": {"select": {"name": "Research Complete"}},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}},
                # Physical Infrastructure - key field for ICP scoring (displayed in dashboard)
                "Physical Infrastructure": {
                    "rich_text": [
                        {"text": {"content": account.get("Physical Infrastructure", "")[:2000]}}
                    ]
                }
                # REMOVED per schema cleanup: Recent Leadership Changes, Recent Funding, Growth Stage,
                # Recent Announcements, Hiring Velocity, Conversation Triggers, Key Decision Makers, Competitor Tools
            }

            url = f"https://api.notion.com/v1/pages/{page_id}"
            response = self._make_request("PATCH", url, json={"properties": properties})

            logger.info(f"✅ Updated account: {account.get('name', 'unknown')}")
            return page_id  # Return page_id for consistency with _create_account

        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return None

    def _update_contact(self, page_id: str, contact: dict) -> Optional[str]:
        """Update existing contact record"""
        # Implementation similar to create but using PATCH
        logger.info(f"Updating contact {contact.get('name', 'unknown')}")
        return page_id  # Simplified for consolidation

    # ═══════════════════════════════════════════════════════════════════════════════════
    # UTILITY & HEALTH CHECK METHODS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def test_connection(self) -> dict[str, Any]:
        """
        Test actual connectivity to Notion API.

        This performs a real API call to verify:
        1. API key is valid
        2. Network connectivity works
        3. At least one database is accessible

        Returns:
            Dict with connection status and any error details

        This method NEVER raises - it captures errors for reporting.
        """
        result = {
            "connected": False,
            "api_key_valid": False,
            "databases_accessible": {},
            "error": None,
            "latency_ms": None,
        }

        # Test API key by querying user info
        try:
            import time as t

            start = t.time()
            response = self._make_request(
                "GET", "https://api.notion.com/v1/users/me", operation="test_connection"
            )
            result["latency_ms"] = int((t.time() - start) * 1000)
            result["api_key_valid"] = True
            result["connected"] = True
        except NotionError as e:
            result["error"] = e.to_dict()
            return result
        except Exception as e:
            result["error"] = {"message": str(e), "type": type(e).__name__}
            return result

        # Test each configured database
        for db_name, db_id in self.database_ids.items():
            if not db_id:
                result["databases_accessible"][db_name] = {
                    "configured": False,
                    "accessible": False,
                    "error": "Not configured",
                }
                continue

            try:
                url = f"https://api.notion.com/v1/databases/{db_id}"
                self._make_request("GET", url, operation=f"test_db_{db_name}")
                result["databases_accessible"][db_name] = {
                    "configured": True,
                    "accessible": True,
                    "error": None,
                }
            except NotionError as e:
                result["databases_accessible"][db_name] = {
                    "configured": True,
                    "accessible": False,
                    "error": e.message,
                }

        return result

    def get_health_status(self) -> dict[str, Any]:
        """
        Get comprehensive health status of Notion integration.

        Enhanced to track:
        - Operation counts and last operation
        - Database configuration status
        - Missing critical configuration
        """
        # Check which databases are missing
        missing_dbs = [name for name, db_id in self.database_ids.items() if not db_id]

        # Determine overall health
        critical_dbs = ["accounts", "contacts"]  # Must have these
        critical_missing = [db for db in critical_dbs if db in missing_dbs]

        return {
            "healthy": len(critical_missing) == 0 and bool(self.api_key),
            "api_key_configured": bool(self.api_key),
            "advanced_client_available": bool(self.client),
            "database_configuration": {
                name: {
                    "configured": bool(db_id),
                    "id_preview": db_id[:8] + "..." if db_id else None,
                }
                for name, db_id in self.database_ids.items()
            },
            "missing_databases": missing_dbs,
            "critical_missing": critical_missing,
            "operation_count": self._operation_count,
            "last_operation": self._last_operation,
            "last_request_time": self.last_request_time,
        }

    def get_pipeline_status(self) -> dict[str, Any]:
        """
        Get detailed status of the data pipeline for monitoring.

        This is designed to be called from a health check endpoint.
        """
        health = self.get_health_status()

        # Test actual connectivity if we think we're configured
        connection_test = None
        if health["api_key_configured"]:
            connection_test = self.test_connection()

        return {
            "status": "healthy"
            if health["healthy"] and (connection_test and connection_test.get("connected"))
            else "degraded"
            if health["api_key_configured"]
            else "not_configured",
            "health": health,
            "connection_test": connection_test,
            "recommendations": self._get_recommendations(health, connection_test),
        }

    def _get_recommendations(
        self, health: dict[str, Any], connection_test: Optional[dict[str, Any]]
    ) -> list[str]:
        """Generate actionable recommendations based on health status"""
        recs = []

        if not health["api_key_configured"]:
            recs.append("Set NOTION_API_KEY environment variable")

        for db in health.get("critical_missing", []):
            recs.append(f"Configure {db} database ID: NOTION_{db.upper()}_DB_ID")

        if connection_test and not connection_test.get("connected"):
            recs.append("Check Notion API key validity and network connectivity")

        if connection_test:
            for db_name, db_status in connection_test.get("databases_accessible", {}).items():
                if db_status.get("configured") and not db_status.get("accessible"):
                    recs.append(
                        f"Database '{db_name}' is configured but not accessible. "
                        f"Check the database ID and sharing permissions."
                    )

        return recs


# Global instance for convenience (optional)
_notion_client = None


def get_notion_client() -> NotionClient:
    """Get global Notion client instance"""
    global _notion_client
    if _notion_client is None:
        _notion_client = NotionClient()
    return _notion_client


if __name__ == "__main__":
    # Test script
    client = NotionClient()
    status = client.get_health_status()
    print("🔗 Notion Client Health Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
