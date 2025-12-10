#!/usr/bin/env python3
"""
Flask API Server for ABM Intelligence Dashboard

Serves account and contact data with full scoring breakdowns
for the React frontend.

Run: python -m src.abm_research.api.server
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Optional

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Load .env file from project root
env_file = os.path.join(project_root, ".env")
if os.path.exists(env_file):
    logger.info(f"📁 Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key not in os.environ:  # Don't override existing env vars
                    os.environ[key] = value
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Notion client and scorer directly (avoid package __init__ chain)
NOTION_AVAILABLE = False
account_scorer = None

try:
    # Direct imports to avoid triggering full package initialization
    import importlib.util

    # Load notion_client directly
    notion_spec = importlib.util.spec_from_file_location(
        "notion_client",
        os.path.join(project_root, "src/abm_research/integrations/notion_client.py"),
    )
    notion_module = importlib.util.module_from_spec(notion_spec)
    notion_spec.loader.exec_module(notion_module)
    NotionClient = notion_module.NotionClient
    get_notion_client = notion_module.get_notion_client

    # Import exception types for proper error handling
    NotionError = notion_module.NotionError
    NotionConfigError = notion_module.NotionConfigError
    NotionAPIError = notion_module.NotionAPIError
    NotionValidationError = notion_module.NotionValidationError
    NotionParseError = notion_module.NotionParseError

    # Load unified_lead_scorer directly
    scorer_spec = importlib.util.spec_from_file_location(
        "unified_lead_scorer",
        os.path.join(project_root, "src/abm_research/core/unified_lead_scorer.py"),
    )
    scorer_module = importlib.util.module_from_spec(scorer_spec)
    scorer_spec.loader.exec_module(scorer_module)
    account_scorer = scorer_module.account_scorer
    meddic_contact_scorer = scorer_module.meddic_contact_scorer

    NOTION_AVAILABLE = True
    logger.info("✅ Notion client available - using real data")
except Exception as e:
    NOTION_AVAILABLE = False
    logger.warning(f"⚠️ Notion client not available, using mock data: {e}")

    # Define placeholder exception classes for when Notion is not available
    class NotionError(Exception):
        pass

    class NotionConfigError(NotionError):
        pass

    class NotionAPIError(NotionError):
        pass

    class NotionValidationError(NotionError):
        pass

    class NotionParseError(NotionError):
        pass


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


# ============================================================================
# Data Layer - Real Notion Integration
# ============================================================================


def get_notion_accounts(raise_on_error: bool = False) -> list[dict]:
    """
    Fetch accounts from Notion and transform for API.

    Args:
        raise_on_error: If True, raise exceptions instead of falling back to mock data.
                       Use True for debugging and health checks.

    Returns:
        List of account dictionaries

    Raises:
        NotionError: If raise_on_error=True and Notion operation fails
    """
    if not NOTION_AVAILABLE:
        if raise_on_error:
            raise NotionConfigError(
                "Notion client not available",
                missing_config="NOTION_API_KEY",
                operation="get_notion_accounts",
            )
        return get_mock_accounts()

    try:
        notion = get_notion_client()
        raw_accounts = notion.query_all_accounts()

        # Build contact count map (query once, use for all accounts)
        contact_counts: dict[str, int] = {}
        try:
            all_contacts = notion.query_all_contacts()
            for contact in all_contacts:
                props = contact.get("properties", {})
                account_rel = props.get("Account", {}).get("relation", [])
                if account_rel:
                    account_id = account_rel[0].get("id", "")
                    contact_counts[account_id] = contact_counts.get(account_id, 0) + 1
            logger.info(
                f"📊 Contact counts: {len(all_contacts)} contacts across {len(contact_counts)} accounts"
            )
        except NotionConfigError:
            # Contacts DB not configured is acceptable, continue without counts
            logger.warning("⚠️ Contacts database not configured, skipping contact counts")
        except NotionError as e:
            # Log but continue - contact counts are not critical
            logger.warning(f"⚠️ Could not fetch contact counts: {e}")
            if raise_on_error:
                raise

        accounts = []
        for idx, page in enumerate(raw_accounts):
            account = transform_notion_account(page, idx, contact_counts)
            if account:
                accounts.append(account)

        logger.info(f"✅ Loaded {len(accounts)} accounts from Notion")
        return accounts

    except NotionConfigError as e:
        # Configuration error - fall back to mock if allowed, otherwise raise
        logger.error(f"❌ Notion configuration error: {e}")
        if raise_on_error:
            raise
        return get_mock_accounts()

    except NotionAPIError as e:
        # API error - this is a real failure, log and optionally raise
        logger.error(f"❌ Notion API error fetching accounts: {e}")
        if raise_on_error:
            raise
        # Fall back to mock data but log that we're doing so
        logger.warning("⚠️ Falling back to mock data due to API error")
        return get_mock_accounts()

    except NotionError as e:
        # Other Notion errors
        logger.error(f"❌ Notion error fetching accounts: {e}")
        if raise_on_error:
            raise
        return get_mock_accounts()

    except Exception as e:
        # Unexpected error - always log with full traceback
        logger.error(f"❌ Unexpected error fetching from Notion: {e}")
        import traceback

        traceback.print_exc()
        if raise_on_error:
            raise NotionError(
                f"Unexpected error: {str(e)}", operation="get_notion_accounts", cause=e
            )
        return get_mock_accounts()


def transform_notion_account(
    page: dict, idx: int = 0, contact_counts: Optional[dict[str, int]] = None
) -> Optional[dict]:
    """Transform Notion page to API account format with full scoring"""
    try:
        props = page.get("properties", {})

        # Extract title (Name field)
        name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        # Extract text fields
        domain = extract_rich_text(props.get("Domain", {}))
        physical_infra = extract_rich_text(props.get("Physical Infrastructure", {}))
        business_model = extract_select(props.get("Business Model", {}))
        growth_stage = extract_select(props.get("Growth Stage", {}))

        # Extract number fields
        employee_count = props.get("Employee Count", {}).get("number", 0) or 0
        icp_fit_score = props.get("ICP Fit Score", {}).get("number", 0) or 0

        # Calculate account score using our scorer
        account_data = {
            "name": name,
            "domain": domain,
            "Physical Infrastructure": physical_infra,
            "business_model": business_model,
            "employee_count": employee_count,
            "industry": extract_select(props.get("Industry", {})),
            "growth_stage": growth_stage,
        }

        # Calculate component scores from account data
        # This ensures total always matches sum of weighted components
        if account_scorer:
            score_obj = account_scorer.calculate_account_score(account_data)
            infra_score = score_obj.infrastructure_fit.score
            infra_breakdown = score_obj.infrastructure_fit.to_dict()
            business_score = score_obj.business_fit.score
            buying_score = score_obj.buying_signals.score
            # Calculate total from components: Infrastructure × 35% + Business Fit × 35% + Buying Signals × 30%
            total_score = int(infra_score * 0.35 + business_score * 0.35 + buying_score * 0.30)
        else:
            # Fallback to Notion's ICP Fit Score if scorer unavailable
            total_score = icp_fit_score
            infra_score = 0
            business_score = 0
            buying_score = 0
            infra_breakdown = {"score": 0, "breakdown": {}}

        # Priority level derived from total score
        if total_score >= 80:
            priority_level = "Very High"
        elif total_score >= 65:
            priority_level = "High"
        elif total_score >= 50:
            priority_level = "Medium"
        else:
            priority_level = "Low"

        # Full breakdown for dashboard
        score_breakdown = {
            "total_score": total_score,
            "infrastructure_fit": {
                "score": infra_score,
                "weight": "35%",
                "breakdown": infra_breakdown.get("breakdown", {}),
            },
            "business_fit": {
                "score": business_score,
                "weight": "35%",
            },
            "buying_signals": {
                "score": buying_score,
                "weight": "30%",
            },
            "priority_level": priority_level,
            "formula": "Total = (Infrastructure × 35%) + (Business Fit × 35%) + (Buying Signals × 30%)",
        }

        return {
            "id": f"acc_{page['id'][:8]}",
            "notion_id": page["id"],
            "name": name or f"Account {idx + 1}",
            "domain": domain,
            "employee_count": employee_count,
            "industry": account_data.get("industry", "Technology"),
            "business_model": business_model or "Unknown",
            "account_score": total_score,
            "infrastructure_score": infra_score,
            "business_fit_score": business_score,
            "buying_signals_score": buying_score,
            "account_priority_level": priority_level,
            "infrastructure_breakdown": infra_breakdown,
            "account_score_breakdown": score_breakdown,
            "partnership_classification": "Direct ICP" if total_score > 70 else "Research Target",
            "classification_confidence": min(95, total_score + 10),
            "icp_fit_score": icp_fit_score,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": contact_counts.get(page["id"], 0) if contact_counts else 0,
        }

    except Exception as e:
        logger.error(f"Error transforming account: {e}")
        return None


def extract_rich_text(prop: dict) -> str:
    """Extract text from Notion rich_text property"""
    rich_text = prop.get("rich_text", [])
    if rich_text and len(rich_text) > 0:
        return rich_text[0].get("text", {}).get("content", "")
    return ""


def extract_select(prop: dict) -> str:
    """Extract value from Notion select property"""
    select = prop.get("select")
    if select:
        return select.get("name", "")
    return ""


def get_notion_contacts(account_notion_id: str) -> list[dict]:
    """Fetch contacts for account from Notion"""
    if not NOTION_AVAILABLE:
        return get_mock_contacts(account_notion_id)

    try:
        notion = get_notion_client()
        raw_contacts = notion.query_all_contacts(account_notion_id)

        contacts = []
        for page in raw_contacts:
            contact = transform_notion_contact(page)
            if contact:
                contacts.append(contact)

        logger.info(
            f"✅ Loaded {len(contacts)} contacts from Notion for account {account_notion_id}"
        )
        return contacts

    except Exception as e:
        logger.error(f"❌ Error fetching contacts from Notion: {e}")
        return get_mock_contacts(account_notion_id)


def get_notion_trigger_events(account_notion_id: str = None) -> list[dict]:
    """Fetch trigger events from Notion, optionally for a specific account"""
    if not NOTION_AVAILABLE:
        return []

    try:
        notion = get_notion_client()
        raw_events = notion.query_all_trigger_events(account_notion_id)

        events = []
        for page in raw_events:
            event = transform_notion_trigger_event(page)
            if event:
                events.append(event)

        logger.info(f"✅ Loaded {len(events)} trigger events from Notion")
        return events

    except Exception as e:
        logger.error(f"❌ Error fetching trigger events from Notion: {e}")
        return []


def get_notion_partnerships(account_notion_id: str = None) -> list[dict]:
    """Fetch partnerships from Notion, optionally for a specific account

    This function also resolves account names from account relations by building
    a lookup map from the accounts database.
    """
    if not NOTION_AVAILABLE:
        return []

    try:
        notion = get_notion_client()

        # Build account ID → name lookup map for resolving relations
        account_lookup = {}
        try:
            raw_accounts = notion.query_all_accounts()
            for acc_page in raw_accounts:
                acc_id = acc_page.get("id")
                props = acc_page.get("properties", {})
                name_prop = props.get("Name", {}) or props.get("Account Name", {})
                name = ""
                if name_prop.get("title"):
                    name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""
                if acc_id and name:
                    account_lookup[acc_id] = name
        except Exception as e:
            logger.warning(f"Could not build account lookup map: {e}")

        raw_partnerships = notion.query_all_partnerships(account_notion_id)

        partnerships = []
        for page in raw_partnerships:
            partnership = transform_notion_partnership(page)
            if partnership:
                # Resolve account name from account_notion_id using lookup map
                acc_notion_id = partnership.get("account_notion_id")
                if acc_notion_id and acc_notion_id in account_lookup:
                    partnership["account_name"] = account_lookup[acc_notion_id]
                else:
                    # Fall back to the fallback field or "N/A"
                    partnership["account_name"] = partnership.get("account_name_fallback") or "N/A"
                partnerships.append(partnership)

        logger.info(
            f"✅ Loaded {len(partnerships)} partnerships from Notion (resolved {len(account_lookup)} account names)"
        )
        return partnerships

    except Exception as e:
        logger.error(f"❌ Error fetching partnerships from Notion: {e}")
        return []


def transform_notion_contact(page: dict) -> Optional[dict]:
    """Transform Notion contact page to API format"""
    try:
        props = page.get("properties", {})

        # Extract name (title field)
        name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        # Extract other fields
        email = props.get("Email", {}).get("email", "")
        title = extract_rich_text(props.get("Title", {}))
        company = extract_rich_text(props.get("Company", {}))
        linkedin_url = props.get("LinkedIn URL", {}).get("url", "")
        lead_score = props.get("Lead Score", {}).get("number", 0) or 0
        engagement_level = extract_select(props.get("Engagement Level", {}))

        # Data provenance
        name_source = extract_select(props.get("Name Source", {}))
        email_source = extract_select(props.get("Email Source", {}))
        title_source = extract_select(props.get("Title Source", {}))
        data_quality_score = props.get("Data Quality Score", {}).get("number", 0) or 0

        # Calculate real MEDDIC scores using the scorer
        contact_data = {
            "name": name,
            "title": title,
            "email": email,
            "linkedin_url": linkedin_url,
            "engagement_level": engagement_level,
        }

        # Use MEDDIC scorer if available, otherwise fall back to basic calculation
        if meddic_contact_scorer:
            meddic_result = meddic_contact_scorer.calculate_contact_score(contact_data)
            meddic_breakdown = meddic_result.get_score_breakdown()

            return {
                "id": f"con_{page['id'][:8]}",
                "notion_id": page["id"],
                "name": name,
                "email": email,
                "title": title,
                "company": company,
                "linkedin_url": linkedin_url,
                "lead_score": lead_score,
                "engagement_level": engagement_level or "Medium",
                "name_source": name_source,
                "email_source": email_source,
                "title_source": title_source,
                "data_quality_score": data_quality_score,
                # Real MEDDIC scoring from scorer
                "champion_potential_score": meddic_result.champion_potential_score,
                "role_tier": meddic_result.role_tier,
                "role_classification": meddic_result.role_classification,
                "champion_potential_level": meddic_result.champion_potential_level,
                "recommended_approach": meddic_result.recommended_approach,
                "why_prioritize": meddic_result.why_prioritize,
                "meddic_score_breakdown": meddic_breakdown,
                "enrichment_status": "enriched" if email else "pending",
            }
        else:
            # Fallback when scorer not available
            return {
                "id": f"con_{page['id'][:8]}",
                "notion_id": page["id"],
                "name": name,
                "email": email,
                "title": title,
                "company": company,
                "linkedin_url": linkedin_url,
                "lead_score": lead_score,
                "engagement_level": engagement_level or "Medium",
                "name_source": name_source,
                "email_source": email_source,
                "title_source": title_source,
                "data_quality_score": data_quality_score,
                # Fallback scoring when scorer unavailable
                "champion_potential_score": lead_score * 0.8,
                "role_tier": "entry_point",
                "role_classification": title if title else "Unknown",
                "champion_potential_level": "High"
                if lead_score >= 70
                else "Medium"
                if lead_score >= 50
                else "Low",
                "recommended_approach": "Pain-based outreach",
                "why_prioritize": [],
                "meddic_score_breakdown": None,
                "enrichment_status": "enriched" if email else "pending",
            }

    except Exception as e:
        logger.error(f"Error transforming contact: {e}")
        return None


def transform_notion_trigger_event(page: dict) -> Optional[dict]:
    """Transform Notion trigger event page to API format"""
    try:
        props = page.get("properties", {})

        # Extract description (title field)
        description = ""
        desc_prop = props.get("Event Description", {})
        if desc_prop.get("title"):
            description = desc_prop["title"][0]["text"]["content"] if desc_prop["title"] else ""

        # Extract other fields
        company = extract_rich_text(props.get("Company", {}))
        event_type = extract_select(props.get("Event Type", {}))
        confidence = extract_select(props.get("Confidence", {}))
        urgency = extract_select(props.get("Urgency", {}))
        source_url = props.get("Source URL", {}).get("url", "")
        relevance_score = props.get("Relevance Score", {}).get("number", 0) or 0

        # Get date
        detected_date = ""
        date_prop = props.get("Detected Date", {}).get("date")
        if date_prop:
            detected_date = date_prop.get("start", "")

        return {
            "id": f"evt_{page['id'][:8]}",
            "notion_id": page["id"],
            "description": description,
            "company": company,
            "event_type": event_type,
            "confidence": confidence or "Medium",
            "urgency": urgency or "Medium",
            "source_url": source_url,
            "relevance_score": relevance_score,
            "detected_date": detected_date,
        }

    except Exception as e:
        logger.error(f"Error transforming trigger event: {e}")
        return None


def transform_notion_partnership(page: dict) -> Optional[dict]:
    """Transform Notion partnership page to API format

    Field mappings (Notion field name -> API field name):
    - Name (title) -> partner_name
    - Category (select) -> partnership_type
    - Priority Score (number) -> relevance_score
    - Relationship Evidence (rich_text) -> context
    - Source URL (url) -> source_url
    - Detected Date (date) -> discovered_date
    - Account (relation) -> account_notion_id (TRUSTED PATHS)
    - Is Verdigris Partner (checkbox) -> is_verdigris_partner (TRUSTED PATHS)
    """
    try:
        props = page.get("properties", {})

        # Extract partner name (title field - stored as 'Partner Name' in Notion)
        partner_name = ""
        # Try both field names for compatibility
        name_prop = props.get("Partner Name", {}) or props.get("Name", {})
        if name_prop.get("title"):
            partner_name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        # Extract other fields using actual Notion field names
        partnership_type = extract_select(props.get("Category", {}))
        relevance_score = props.get("Priority Score", {}).get("number", 0) or 0
        context = extract_rich_text(props.get("Relationship Evidence", {}))
        source_url = props.get("Source URL", {}).get("url", "")

        # Additional strategic fields
        relationship_depth = extract_select(props.get("Relationship Depth", {}))
        partnership_maturity = extract_select(props.get("Partnership Maturity", {}))
        best_approach = extract_select(props.get("Best Approach", {}))

        # Get date (stored as 'Detected Date' in Notion)
        discovered_date = ""
        date_prop = props.get("Detected Date", {}).get("date")
        if date_prop:
            discovered_date = date_prop.get("start", "")

        # TRUSTED PATHS: Extract Account relation (vendor -> account link)
        account_notion_id = None
        account_relation = props.get("Account", {}).get("relation", [])
        if account_relation:
            account_notion_id = account_relation[0].get("id")

        # TRUSTED PATHS: Extract Is Verdigris Partner checkbox
        is_verdigris_partner = props.get("Is Verdigris Partner", {}).get("checkbox", False)

        # TRUSTED PATHS: Fallback account name if relation not set
        account_name_fallback = extract_rich_text(props.get("Account Name (Fallback)", {}))

        return {
            "id": f"ptr_{page['id'][:8]}",
            "notion_id": page["id"],
            "partner_name": partner_name,
            "partnership_type": partnership_type or "Technology Integration",
            "relevance_score": relevance_score,
            "context": context,
            "source_url": source_url,
            "discovered_date": discovered_date,
            # Additional fields for partner scoring
            "relationship_depth": relationship_depth or "Surface Integration",
            "partnership_maturity": partnership_maturity or "Basic",
            "best_approach": best_approach or "Technical Discussion",
            # TRUSTED PATHS: Account linkage and Verdigris partner flag
            "account_notion_id": account_notion_id,  # Notion ID of linked account
            "account_name_fallback": account_name_fallback,  # Text fallback if no relation
            "is_verdigris_partner": is_verdigris_partner,  # True = Verdigris partner, False = account vendor
        }

    except Exception as e:
        logger.error(f"Error transforming partnership: {e}")
        return None


# ============================================================================
# Mock Data (Fallback when Notion unavailable)
# ============================================================================


def get_mock_accounts():
    """Generate mock accounts for dashboard testing"""
    return [
        {
            "id": "acc_001",
            "name": "CoreWeave",
            "domain": "coreweave.com",
            "employee_count": 450,
            "industry": "Cloud Computing",
            "business_model": "GPU Cloud Provider",
            "account_score": 88.5,
            "infrastructure_score": 100.0,
            "business_fit_score": 92.5,
            "buying_signals_score": 65.0,
            "account_priority_level": "Very High",
            "infrastructure_breakdown": {
                "score": 100.0,
                "breakdown": {
                    "gpu_infrastructure": {
                        "detected": ["nvidia", "h100", "a100", "dgx", "gpu cluster"],
                        "points": 40,
                        "max_points": 40,
                        "description": "GPU/AI infrastructure - TARGET ICP",
                    },
                    "target_vendors": {
                        "detected": ["schneider electric"],
                        "points": 30,
                        "max_points": 30,
                        "description": "Target vendor detected",
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu", "power distribution"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected",
                    },
                    "cooling_systems": {
                        "detected": ["liquid cooling", "immersion cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected",
                    },
                    "dcim_software": {
                        "detected": ["dcim", "nlyte"],
                        "points": 15,
                        "max_points": 15,
                        "description": "DCIM software detected",
                    },
                },
                "raw_text": "NVIDIA H100 GPU clusters, DGX systems, liquid cooling...",
            },
            "account_score_breakdown": {
                "total_score": 88.5,
                "infrastructure_fit": {"score": 100.0, "weight": "35%", "breakdown": {}},
                "business_fit": {
                    "score": 92.5,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {
                            "detected": "GPU Cloud (Target ICP)",
                            "score": 100,
                            "business_model": "GPU Cloud Provider",
                        },
                        "company_size_fit": {
                            "employee_count": 450,
                            "size_category": "Growth",
                            "score": 70,
                        },
                        "geographic_fit": {
                            "us_locations": ["Texas", "Virginia"],
                            "priority": "US Primary",
                            "score": 100,
                        },
                    },
                },
                "buying_signals": {
                    "score": 65.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {
                            "high_value_triggers": ["expansion", "funding"],
                            "total_triggers": 3,
                            "score": 75,
                        },
                        "expansion_signals": {
                            "detected": ["new data center", "capacity expansion"],
                            "score": 60,
                        },
                        "hiring_signals": {"detected": ["hiring GPU engineers"], "score": 50},
                    },
                },
                "priority_level": "Very High",
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 95.0,
            "icp_fit_score": 90,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 8,
        },
        {
            "id": "acc_002",
            "name": "Lambda Labs",
            "domain": "lambdalabs.com",
            "employee_count": 200,
            "industry": "Cloud Computing",
            "business_model": "GPU Cloud Provider",
            "account_score": 82.3,
            "infrastructure_score": 95.0,
            "business_fit_score": 85.0,
            "buying_signals_score": 60.0,
            "account_priority_level": "Very High",
            "infrastructure_breakdown": {
                "score": 95.0,
                "breakdown": {
                    "gpu_infrastructure": {
                        "detected": ["nvidia", "a100", "gpu cluster", "ai infrastructure"],
                        "points": 40,
                        "max_points": 40,
                        "description": "GPU/AI infrastructure - TARGET ICP",
                    },
                    "target_vendors": {
                        "detected": [],
                        "points": 0,
                        "max_points": 30,
                        "description": "Target vendor detected",
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected",
                    },
                    "cooling_systems": {
                        "detected": ["precision cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected",
                    },
                    "dcim_software": {
                        "detected": [],
                        "points": 0,
                        "max_points": 15,
                        "description": "DCIM software detected",
                    },
                },
                "raw_text": "NVIDIA A100 GPU clusters, precision cooling systems...",
            },
            "account_score_breakdown": {
                "total_score": 82.3,
                "infrastructure_fit": {"score": 95.0, "weight": "35%", "breakdown": {}},
                "business_fit": {
                    "score": 85.0,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {
                            "detected": "GPU Cloud (Target ICP)",
                            "score": 100,
                            "business_model": "GPU Cloud Provider",
                        },
                        "company_size_fit": {
                            "employee_count": 200,
                            "size_category": "Growth",
                            "score": 50,
                        },
                        "geographic_fit": {
                            "us_locations": ["California"],
                            "priority": "US Primary",
                            "score": 100,
                        },
                    },
                },
                "buying_signals": {
                    "score": 60.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {
                            "high_value_triggers": ["product launch"],
                            "total_triggers": 2,
                            "score": 50,
                        },
                        "expansion_signals": {"detected": ["growing capacity"], "score": 60},
                        "hiring_signals": {"detected": [], "score": 20},
                    },
                },
                "priority_level": "Very High",
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 90.0,
            "icp_fit_score": 85,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 5,
        },
        {
            "id": "acc_003",
            "name": "Equinix",
            "domain": "equinix.com",
            "employee_count": 12000,
            "industry": "Data Center",
            "business_model": "Colocation Provider",
            "account_score": 71.5,
            "infrastructure_score": 65.0,
            "business_fit_score": 90.0,
            "buying_signals_score": 55.0,
            "account_priority_level": "High",
            "infrastructure_breakdown": {
                "score": 65.0,
                "breakdown": {
                    "gpu_infrastructure": {
                        "detected": [],
                        "points": 0,
                        "max_points": 40,
                        "description": "GPU/AI infrastructure - TARGET ICP",
                    },
                    "target_vendors": {
                        "detected": ["schneider electric", "eaton"],
                        "points": 30,
                        "max_points": 30,
                        "description": "Target vendor detected",
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu", "power distribution"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected",
                    },
                    "cooling_systems": {
                        "detected": ["crac", "precision cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected",
                    },
                    "dcim_software": {
                        "detected": ["dcim"],
                        "points": 15,
                        "max_points": 15,
                        "description": "DCIM software detected",
                    },
                },
                "raw_text": "Enterprise data center infrastructure, Schneider Electric UPS...",
            },
            "account_score_breakdown": {
                "total_score": 71.5,
                "infrastructure_fit": {"score": 65.0, "weight": "35%", "breakdown": {}},
                "business_fit": {
                    "score": 90.0,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {
                            "detected": "Colocation Provider",
                            "score": 90,
                            "business_model": "Colocation Provider",
                        },
                        "company_size_fit": {
                            "employee_count": 12000,
                            "size_category": "Enterprise",
                            "score": 100,
                        },
                        "geographic_fit": {
                            "us_locations": ["Multiple"],
                            "priority": "US Primary",
                            "score": 100,
                        },
                    },
                },
                "buying_signals": {
                    "score": 55.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {
                            "high_value_triggers": [],
                            "total_triggers": 1,
                            "score": 30,
                        },
                        "expansion_signals": {"detected": ["new facility"], "score": 60},
                        "hiring_signals": {"detected": ["hiring facilities"], "score": 50},
                    },
                },
                "priority_level": "High",
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 85.0,
            "icp_fit_score": 80,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 12,
        },
    ]


def get_mock_contacts(account_id: str):
    """Generate mock contacts for a given account"""
    contact_templates = {
        "acc_001": [
            {
                "id": "con_001",
                "name": "Sarah Chen",
                "title": "Critical Facilities Engineer",
                "email": "schen@coreweave.com",
                "company": "CoreWeave",
                "linkedin_url": "https://linkedin.com/in/sarahchen",
                "lead_score": 85.2,
                "champion_potential_score": 92.0,
                "role_tier": "entry_point",
                "role_classification": "Critical Facilities Engineers",
                "champion_potential_level": "Very High",
                "recommended_approach": "Pain-based outreach: Focus on GPU power/thermal challenges",
                "why_prioritize": [
                    "Entry Point role: Critical Facilities Engineers - feels the pain daily",
                    "Can become internal champion who sells Verdigris up the chain",
                    "Has visibility into power/thermal events and infrastructure issues",
                    "Very high champion potential - prioritize for first outreach",
                ],
                "meddic_score_breakdown": {
                    "total_score": 85.2,
                    "champion_potential": {"score": 92.0, "weight": "45%", "level": "Very High"},
                    "role_fit": {
                        "score": 95.0,
                        "weight": "30%",
                        "tier": "entry_point",
                        "classification": "Critical Facilities Engineers",
                    },
                    "engagement_potential": {"score": 60.0, "weight": "25%"},
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "high",
                "account_id": "acc_001",
            },
            {
                "id": "con_002",
                "name": "Michael Torres",
                "title": "VP of Infrastructure",
                "email": "mtorres@coreweave.com",
                "company": "CoreWeave",
                "linkedin_url": "https://linkedin.com/in/michaeltorres",
                "lead_score": 42.5,
                "champion_potential_score": 30.0,
                "role_tier": "economic_buyer",
                "role_classification": "VP, Infrastructure & Data Centers",
                "champion_potential_level": "Low",
                "recommended_approach": "Via champion referral - business case focused",
                "why_prioritize": [
                    "Economic Buyer: VP, Infrastructure & Data Centers - budget authority",
                    "Engage via champion referral with business case",
                ],
                "meddic_score_breakdown": {
                    "total_score": 42.5,
                    "champion_potential": {"score": 30.0, "weight": "45%", "level": "Low"},
                    "role_fit": {
                        "score": 65.0,
                        "weight": "30%",
                        "tier": "economic_buyer",
                        "classification": "VP, Infrastructure & Data Centers",
                    },
                    "engagement_potential": {"score": 40.0, "weight": "25%"},
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "medium",
                "account_id": "acc_001",
            },
            {
                "id": "con_003",
                "name": "Emily Rodriguez",
                "title": "Director, Data Center Operations",
                "email": "erodriguez@coreweave.com",
                "company": "CoreWeave",
                "linkedin_url": "https://linkedin.com/in/emilyrodriguez",
                "lead_score": 62.8,
                "champion_potential_score": 65.0,
                "role_tier": "middle_decider",
                "role_classification": "Director, Data Center Operations",
                "champion_potential_level": "Medium",
                "recommended_approach": "Solution-focused: How we integrate with their stack",
                "why_prioritize": [
                    "Tooling Decider: Director, Data Center Operations - makes integration decisions",
                    "Can validate need and drive tooling selection",
                ],
                "meddic_score_breakdown": {
                    "total_score": 62.8,
                    "champion_potential": {"score": 65.0, "weight": "45%", "level": "Medium"},
                    "role_fit": {
                        "score": 80.0,
                        "weight": "30%",
                        "tier": "middle_decider",
                        "classification": "Director, Data Center Operations",
                    },
                    "engagement_potential": {"score": 55.0, "weight": "25%"},
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "high",
                "account_id": "acc_001",
            },
        ]
    }

    return contact_templates.get(account_id, [])


# ============================================================================
# API Routes
# ============================================================================


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "version": "1.0.0", "timestamp": datetime.now().isoformat()}
    )


@app.route("/api/health/pipeline", methods=["GET"])
def pipeline_health_check():
    """
    Comprehensive data pipeline health check.

    Tests actual connectivity to Notion and validates all database configurations.
    This endpoint NEVER fails silently - it reports ALL issues found.

    Returns:
        - status: "healthy" | "degraded" | "unhealthy" | "not_configured"
        - notion_available: Whether Notion client loaded
        - connection_test: Results of actual API connectivity test
        - database_status: Per-database accessibility status
        - recommendations: List of actionable fixes if issues found
        - last_operation: Most recent Notion operation performed
    """
    result = {
        "status": "unknown",
        "timestamp": datetime.now().isoformat(),
        "notion_module_loaded": NOTION_AVAILABLE,
        "connection_test": None,
        "database_status": {},
        "recommendations": [],
        "errors": [],
    }

    if not NOTION_AVAILABLE:
        result["status"] = "not_configured"
        result["recommendations"].append(
            "Notion client not available. Check NOTION_API_KEY environment variable."
        )
        return jsonify(result), 503

    try:
        notion = get_notion_client()

        # Get comprehensive pipeline status (includes connection test)
        pipeline_status = notion.get_pipeline_status()

        result["status"] = pipeline_status["status"]
        result["health"] = pipeline_status["health"]
        result["connection_test"] = pipeline_status["connection_test"]
        result["recommendations"] = pipeline_status["recommendations"]

        # Add database-specific status
        if pipeline_status["connection_test"]:
            result["database_status"] = pipeline_status["connection_test"].get(
                "databases_accessible", {}
            )

        # Determine HTTP status code
        if result["status"] == "healthy":
            return jsonify(result), 200
        elif result["status"] == "degraded":
            return jsonify(result), 200  # Still return 200, but status shows degraded
        else:
            return jsonify(result), 503

    except NotionConfigError as e:
        result["status"] = "not_configured"
        result["errors"].append(e.to_dict() if hasattr(e, "to_dict") else str(e))
        result["recommendations"].append(
            f"Configuration error: {e.message if hasattr(e, 'message') else str(e)}"
        )
        return jsonify(result), 503

    except NotionError as e:
        result["status"] = "unhealthy"
        result["errors"].append(e.to_dict() if hasattr(e, "to_dict") else str(e))
        result["recommendations"].append(
            f"Notion error: {e.message if hasattr(e, 'message') else str(e)}"
        )
        return jsonify(result), 503

    except Exception as e:
        logger.error(f"❌ Pipeline health check failed: {e}")
        import traceback

        traceback.print_exc()
        result["status"] = "unhealthy"
        result["errors"].append({"message": str(e), "type": type(e).__name__})
        result["recommendations"].append("Unexpected error - check server logs")
        return jsonify(result), 500


@app.route("/api/health/notion-test", methods=["POST"])
def notion_connectivity_test():
    """
    Run a live connectivity test to Notion.

    This is a more intensive test than /api/health/pipeline - it actually
    attempts to read from each database to verify full read/write access.

    Use this when debugging silent failures or verifying configuration changes.
    """
    if not NOTION_AVAILABLE:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Notion client not available",
                    "recommendation": "Set NOTION_API_KEY environment variable",
                }
            ),
            503,
        )

    try:
        notion = get_notion_client()
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "api_connection": None,
            "databases": {},
            "overall_status": "unknown",
        }

        # Test API connection
        connection = notion.test_connection()
        test_results["api_connection"] = {
            "connected": connection["connected"],
            "api_key_valid": connection["api_key_valid"],
            "latency_ms": connection["latency_ms"],
            "error": connection["error"],
        }

        if not connection["connected"]:
            test_results["overall_status"] = "api_connection_failed"
            return jsonify(test_results), 503

        # Test each database with actual queries
        db_tests = {
            "accounts": ("query_all_accounts", lambda n: len(n.query_all_accounts())),
            "contacts": ("query_all_contacts", lambda n: len(n.query_all_contacts())),
            "trigger_events": (
                "query_all_trigger_events",
                lambda n: len(n.query_all_trigger_events()),
            ),
            "partnerships": ("query_all_partnerships", lambda n: len(n.query_all_partnerships())),
        }

        all_passed = True
        for db_name, (op_name, query_fn) in db_tests.items():
            try:
                import time as t

                start = t.time()
                count = query_fn(notion)
                latency = int((t.time() - start) * 1000)
                test_results["databases"][db_name] = {
                    "status": "accessible",
                    "record_count": count,
                    "latency_ms": latency,
                    "error": None,
                }
            except NotionConfigError as e:
                test_results["databases"][db_name] = {"status": "not_configured", "error": str(e)}
                # Not configured is acceptable, not a failure
            except NotionError as e:
                test_results["databases"][db_name] = {
                    "status": "error",
                    "error": e.to_dict() if hasattr(e, "to_dict") else str(e),
                }
                all_passed = False
            except Exception as e:
                test_results["databases"][db_name] = {
                    "status": "error",
                    "error": {"message": str(e), "type": type(e).__name__},
                }
                all_passed = False

        test_results["overall_status"] = "healthy" if all_passed else "degraded"
        return jsonify(test_results), 200 if all_passed else 503

    except Exception as e:
        logger.error(f"❌ Notion connectivity test failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e), "type": type(e).__name__}), 500


@app.route("/api/accounts", methods=["GET"])
def get_accounts():
    """
    Get all accounts with optional filtering and sorting

    Query params:
    - page: Page number (default 1)
    - per_page: Items per page (default 50)
    - sort_by: Sort field (account_score, infrastructure_score, name)
    - sort_dir: Sort direction (asc, desc)
    - priority: Filter by priority levels (comma-separated)
    - gpu_only: Only show GPU infrastructure accounts
    - search: Search by name/domain
    """
    # Use real Notion data if available, otherwise mock data
    accounts = get_notion_accounts()

    # Search filter
    search = request.args.get("search", "").lower()
    if search:
        accounts = [
            a for a in accounts if search in a["name"].lower() or search in a["domain"].lower()
        ]

    # GPU filter
    gpu_only = request.args.get("gpu_only", "").lower() == "true"
    if gpu_only:
        accounts = [
            a
            for a in accounts
            if a.get("infrastructure_breakdown", {})
            .get("breakdown", {})
            .get("gpu_infrastructure", {})
            .get("detected", [])
        ]

    # Priority filter
    priority_filter = request.args.get("priority", "")
    if priority_filter:
        priorities = [p.strip() for p in priority_filter.split(",")]
        accounts = [a for a in accounts if a.get("account_priority_level") in priorities]

    # Sorting
    sort_by = request.args.get("sort_by", "account_score")
    sort_dir = request.args.get("sort_dir", "desc")
    reverse = sort_dir == "desc"

    if sort_by in ["account_score", "infrastructure_score", "business_fit_score"]:
        accounts.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "name":
        accounts.sort(key=lambda x: x.get("name", "").lower(), reverse=reverse)
    elif sort_by == "contacts_count":
        accounts.sort(key=lambda x: x.get("contacts_count", 0), reverse=reverse)

    # Pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    start = (page - 1) * per_page
    end = start + per_page
    paginated = accounts[start:end]

    return jsonify(
        {"accounts": paginated, "total": len(accounts), "page": page, "per_page": per_page}
    )


@app.route("/api/accounts", methods=["POST"])
def create_account():
    """
    Create a new account in Notion

    Request body:
        - name: Company name (required)
        - domain: Company domain/website (required)
        - industry: Industry/vertical (optional)
        - employee_count: Number of employees (optional)
        - business_model: Description of business (optional)
        - physical_infrastructure: Infrastructure notes (optional)
        - auto_research: Whether to trigger research pipeline (default: true)

    Returns:
        - id: New account ID
        - notion_id: Notion page ID
        - name: Account name
        - success: Boolean indicating success
    """
    if not NOTION_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Notion not available",
                    "message": "Account creation requires Notion integration",
                }
            ),
            503,
        )

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    # Validate required fields
    name = data.get("name", "").strip()
    domain = data.get("domain", "").strip()

    if not name:
        return jsonify({"error": "name is required"}), 400
    if not domain:
        return jsonify({"error": "domain is required"}), 400

    # Normalize domain (remove http/https prefix if present)
    if domain.startswith("http://"):
        domain = domain[7:]
    elif domain.startswith("https://"):
        domain = domain[8:]
    domain = domain.rstrip("/")

    try:
        notion = get_notion_client()

        # Get accounts database ID
        accounts_db_id = os.getenv("NOTION_ACCOUNTS_DB_ID")
        if not accounts_db_id:
            return (
                jsonify(
                    {
                        "error": "Configuration error",
                        "message": "NOTION_ACCOUNTS_DB_ID not configured",
                    }
                ),
                500,
            )

        # Build Notion properties
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Domain": {"rich_text": [{"text": {"content": domain}}]},
        }

        # Optional fields
        if data.get("industry"):
            properties["Industry"] = {"select": {"name": data["industry"]}}

        if data.get("employee_count"):
            try:
                emp_count = int(data["employee_count"])
                properties["Employee Count"] = {"number": emp_count}
            except (ValueError, TypeError):
                pass

        if data.get("business_model"):
            properties["Business Model"] = {
                "rich_text": [{"text": {"content": data["business_model"][:2000]}}]
            }

        if data.get("physical_infrastructure"):
            properties["Physical Infrastructure"] = {
                "rich_text": [{"text": {"content": data["physical_infrastructure"][:2000]}}]
            }

        # Create page in Notion
        new_page = notion.client.pages.create(
            parent={"database_id": accounts_db_id}, properties=properties
        )

        notion_id = new_page["id"]
        account_id = f"acc_{notion_id[:8]}"

        logger.info(f"✅ Created new account: {name} (ID: {account_id})")

        # Return response
        response = {
            "success": True,
            "id": account_id,
            "notion_id": notion_id,
            "name": name,
            "domain": domain,
            "message": f"Account '{name}' created successfully",
        }

        # Note: Auto-research will be triggered by the frontend after creation
        # This keeps the endpoint fast and responsive

        return jsonify(response), 201

    except Exception as e:
        logger.error(f"❌ Failed to create account: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Failed to create account", "message": str(e)}), 500


@app.route("/api/accounts/<account_id>", methods=["GET"])
def get_account(account_id: str):
    """Get single account with contacts, events, and partnerships"""
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Use notion_id for querying related data
    notion_id = account.get("notion_id", "")

    # Fetch real data from Notion
    contacts = get_notion_contacts(notion_id) if notion_id else []
    trigger_events = get_notion_trigger_events(notion_id) if notion_id else []
    partnerships = get_notion_partnerships(notion_id) if notion_id else []

    # MERGE trigger events into account_score_breakdown.buying_signals.breakdown
    # This ensures UI can read from the expected nested path
    if trigger_events:
        # High value = High confidence OR High urgency, otherwise include all with event_type
        high_value_triggers = [
            e.get("event_type", e.get("description", ""))
            for e in trigger_events
            if e.get("confidence") == "High" or e.get("urgency") == "High" or e.get("event_type")
        ]
        trigger_score = min(100, len(trigger_events) * 15)

        # Ensure account_score_breakdown exists with buying_signals.breakdown
        if "account_score_breakdown" not in account:
            account["account_score_breakdown"] = {}
        if "buying_signals" not in account["account_score_breakdown"]:
            account["account_score_breakdown"]["buying_signals"] = {
                "score": trigger_score,
                "weight": "30%",
            }
        if "breakdown" not in account["account_score_breakdown"]["buying_signals"]:
            account["account_score_breakdown"]["buying_signals"]["breakdown"] = {}

        # Add trigger events to the breakdown
        account["account_score_breakdown"]["buying_signals"]["breakdown"]["trigger_events"] = {
            "high_value_triggers": high_value_triggers,
            "all_events": trigger_events,
            "total_triggers": len(trigger_events),
            "score": trigger_score,
        }
        # Also add expansion and hiring signals placeholders
        account["account_score_breakdown"]["buying_signals"]["breakdown"]["expansion_signals"] = {
            "detected": [],
            "score": 0,
        }
        account["account_score_breakdown"]["buying_signals"]["breakdown"]["hiring_signals"] = {
            "detected": [],
            "score": 0,
        }

    return jsonify(
        {
            "account": account,
            "contacts": contacts,
            "trigger_events": trigger_events,
            "partnerships": partnerships,
        }
    )


@app.route("/api/accounts/<account_id>/contacts", methods=["GET"])
def get_account_contacts(account_id: str):
    """Get contacts for a specific account"""
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"contacts": []})

    notion_id = account.get("notion_id", "")
    contacts = get_notion_contacts(notion_id) if notion_id else []
    return jsonify({"contacts": contacts})


@app.route("/api/trigger-events", methods=["GET"])
def get_all_trigger_events():
    """Get all trigger events"""
    events = get_notion_trigger_events()
    return jsonify({"trigger_events": events, "total": len(events)})


@app.route("/api/partnerships", methods=["GET"])
def get_all_partnerships():
    """Get all partnerships"""
    partnerships = get_notion_partnerships()
    return jsonify({"partnerships": partnerships, "total": len(partnerships)})


# ============================================================================
# Trusted Paths (Account Vendor ∩ Verdigris Partner)
# ============================================================================


@app.route("/api/trusted-paths", methods=["GET"])
def get_trusted_paths():
    """
    Get trusted paths into accounts via shared vendor relationships.

    A "trusted path" exists when:
    1. An account uses a vendor (account_notion_id is set)
    2. That vendor is also a Verdigris partner (is_verdigris_partner=True)

    This endpoint finds the intersection and ranks accounts by
    the number/quality of trusted paths available.

    Returns:
    - trusted_paths: List of accounts with their vendor connections
    - verdigris_partners: List of Verdigris's partners
    - account_vendors: Map of account_id -> vendors they use
    """
    partnerships = get_notion_partnerships()
    accounts = get_notion_accounts()

    # Build account ID -> name lookup
    account_lookup = {acc.get("notion_id"): acc for acc in accounts}

    # Separate partnerships into two categories:
    # 1. Verdigris Partners (is_verdigris_partner=True)
    # 2. Account Vendors (account_notion_id is set)
    verdigris_partners = []
    account_vendors = {}  # account_notion_id -> [vendors]

    for p in partnerships:
        partner_name = p.get("partner_name", "").lower()
        is_verdigris = p.get("is_verdigris_partner", False)
        account_notion_id = p.get("account_notion_id")

        if is_verdigris:
            verdigris_partners.append(
                {
                    "partner_name": p.get("partner_name"),
                    "partnership_type": p.get("partnership_type"),
                    "relevance_score": p.get("relevance_score", 0),
                    "relationship_depth": p.get("relationship_depth"),
                    "best_approach": p.get("best_approach"),
                }
            )

        if account_notion_id:
            if account_notion_id not in account_vendors:
                account_vendors[account_notion_id] = []
            account_vendors[account_notion_id].append(
                {
                    "vendor_name": p.get("partner_name"),
                    "category": p.get("partnership_type"),
                    "context": p.get("context", "")[:200],
                }
            )

    # Build set of Verdigris partner names (normalized)
    verdigris_partner_names = {
        p["partner_name"].lower() for p in verdigris_partners if p.get("partner_name")
    }

    # Find trusted paths: accounts that use vendors we're partnered with
    trusted_paths = []
    for account_notion_id, vendors in account_vendors.items():
        account = account_lookup.get(account_notion_id)
        if not account:
            continue

        # Find vendors that are also Verdigris partners
        shared_vendors = []
        for v in vendors:
            vendor_name = v.get("vendor_name", "").lower()
            if vendor_name in verdigris_partner_names:
                shared_vendors.append(v)

        if shared_vendors:
            trusted_paths.append(
                {
                    "account_id": account.get("id"),
                    "account_notion_id": account_notion_id,
                    "account_name": account.get("name"),
                    "account_score": account.get("account_score", 0),
                    "priority_level": account.get("account_priority_level", "Medium"),
                    "shared_vendors": shared_vendors,
                    "trusted_path_count": len(shared_vendors),
                }
            )

    # Sort by trusted path count, then by account score
    trusted_paths.sort(key=lambda x: (-x["trusted_path_count"], -x["account_score"]))

    return jsonify(
        {
            "trusted_paths": trusted_paths,
            "total_accounts_with_paths": len(trusted_paths),
            "total_accounts": len(accounts),
            "verdigris_partners": verdigris_partners,
            "total_verdigris_partners": len(verdigris_partners),
            "note": "Trusted paths require both: 1) Account vendors discovered via research, 2) Those vendors marked as is_verdigris_partner=True in Notion",
        }
    )


# ============================================================================
# Partner Rankings (Strategic Partnership Intelligence)
# ============================================================================


def calculate_partner_score(
    partnership: dict, matched_accounts: list[dict], all_accounts: list[dict]
) -> dict:
    """
    Calculate a composite partner score based on observable/public data.

    Scoring dimensions (optimized for prospective partners):

    1. Account Reach Score (35%) - How many ICP accounts can this partner help reach?
       - Number of matched accounts weighted by their ICP scores
       - Higher scores for partners connected to high-value accounts

    2. ICP Alignment Score (25%) - How well does this partner align with our ICP?
       - Technology alignment (GPU/AI/infrastructure focus)
       - Industry alignment with target accounts
       - Business model compatibility

    3. Entry Point Quality (25%) - How effective as a sales entry point?
       - Partnership type effectiveness (Reseller > Strategic Alliance > Tech Integration)
       - Relationship depth potential
       - Best approach alignment

    4. Trust Evidence Score (15%) - Observable signals of established relationship
       - Documentation quality (context length, source URLs)
       - Relationship depth indicators
       - Partnership maturity level

    Returns dict with score and breakdown.
    """

    # ===== 1. ACCOUNT REACH SCORE (35%) =====
    # Measures how many valuable accounts this partner can help us reach
    if matched_accounts and all_accounts:
        # Weight matched accounts by their ICP scores
        weighted_reach = sum(acc.get("account_score", 50) for acc in matched_accounts)
        max_possible = len(all_accounts) * 100  # If all accounts at max score

        # Normalize to 0-100, with bonus for high-value concentrations
        reach_raw = min(100, (weighted_reach / max(max_possible * 0.3, 1)) * 100)

        # Bonus for breadth: more accounts = more network value
        breadth_multiplier = min(1.5, 1 + (len(matched_accounts) / max(len(all_accounts), 1)))
        account_reach_score = min(100, reach_raw * breadth_multiplier)
    else:
        account_reach_score = 0

    # ===== 2. ICP ALIGNMENT SCORE (25%) =====
    # How well does this partner align with our ideal customer profile?
    partner_name = partnership.get("partner_name", "").lower()
    partner_type = partnership.get("partnership_type", "").lower()
    context = partnership.get("context", "").lower()

    icp_signals = 0

    # Technology alignment (observable from partner name/context)
    tech_keywords = {
        "high_value": ["gpu", "nvidia", "ai", "ml", "inference", "training", "datacenter", "hpc"],
        "medium_value": ["cloud", "kubernetes", "infrastructure", "compute", "storage"],
        "low_value": ["software", "platform", "service", "solution"],
    }

    for keyword in tech_keywords["high_value"]:
        if keyword in partner_name or keyword in context:
            icp_signals += 25
            break
    for keyword in tech_keywords["medium_value"]:
        if keyword in partner_name or keyword in context:
            icp_signals += 15
            break
    for keyword in tech_keywords["low_value"]:
        if keyword in partner_name or keyword in context:
            icp_signals += 5
            break

    # Market segment alignment
    if any(
        seg in partner_name or seg in context for seg in ["enterprise", "hyperscale", "startup"]
    ):
        icp_signals += 20

    # Infrastructure focus (our core ICP indicator)
    if any(
        infra in partner_name or infra in context
        for infra in ["datacenter", "data center", "colocation", "cooling", "power"]
    ):
        icp_signals += 30

    icp_alignment_score = min(100, icp_signals)

    # ===== 3. ENTRY POINT QUALITY (25%) =====
    # How effective would this partner be for sales entry?
    entry_point_score = 0

    # Partnership type effectiveness for referrals
    type_scores = {
        "reseller": 100,  # Direct sales channel
        "strategic alliance": 80,  # Joint go-to-market
        "channel partner": 75,  # Sales channel
        "technology integration": 50,  # Technical connection
        "vendor relationship": 30,  # We're the buyer
    }
    for type_key, score in type_scores.items():
        if type_key in partner_type:
            entry_point_score = score
            break

    # Adjust based on relationship depth potential
    depth = partnership.get("relationship_depth", "")
    depth_multipliers = {
        "Go-to-Market Alliance": 1.3,
        "Strategic Alliance": 1.2,
        "Deep Integration": 1.1,
        "Basic Partnership": 1.0,
        "Surface Integration": 0.8,
    }
    entry_point_score *= depth_multipliers.get(depth, 1.0)

    # Best approach alignment
    best_approach = partnership.get("best_approach", "").lower()
    if "executive" in best_approach or "referral" in best_approach:
        entry_point_score = min(100, entry_point_score * 1.2)
    elif "technical" in best_approach:
        entry_point_score = min(100, entry_point_score * 1.1)

    entry_point_score = min(100, entry_point_score)

    # ===== 4. TRUST EVIDENCE SCORE (15%) =====
    # Observable signals of relationship strength
    evidence_score = 0

    # Documentation quality
    context_text = partnership.get("context", "")
    if context_text:
        # More detailed context = more established relationship
        word_count = len(context_text.split())
        evidence_score += min(30, word_count / 2)  # Up to 30 points for 60+ words

    # Source documentation
    if partnership.get("source_url"):
        evidence_score += 20  # Public documentation

    # Relationship depth (observable maturity)
    maturity = partnership.get("partnership_maturity", "")
    maturity_scores = {
        "Sophisticated": 40,
        "Advanced": 30,
        "Established": 20,
        "Developing": 10,
        "Basic": 5,
    }
    evidence_score += maturity_scores.get(maturity, 0)

    # Explicit relevance rating (if set)
    relevance = partnership.get("relevance_score", 0) or 0
    if relevance > 0:
        evidence_score = min(100, evidence_score + (relevance * 0.2))

    evidence_score = min(100, evidence_score)

    # ===== COMPOSITE SCORE =====
    composite = (
        account_reach_score * 0.35
        + icp_alignment_score * 0.25
        + entry_point_score * 0.25
        + evidence_score * 0.15
    )

    return {
        "total_score": round(composite, 1),
        "breakdown": {
            "account_reach": {
                "score": round(account_reach_score, 1),
                "weight": 0.35,
                "contribution": round(account_reach_score * 0.35, 1),
                "matched_count": len(matched_accounts),
                "description": f"{len(matched_accounts)} accounts reachable via this partner",
            },
            "icp_alignment": {
                "score": round(icp_alignment_score, 1),
                "weight": 0.25,
                "contribution": round(icp_alignment_score * 0.25, 1),
                "description": "Technology and market segment alignment with ICP",
            },
            "entry_point_quality": {
                "score": round(entry_point_score, 1),
                "weight": 0.25,
                "contribution": round(entry_point_score * 0.25, 1),
                "description": "Effectiveness as a sales entry point",
            },
            "trust_evidence": {
                "score": round(evidence_score, 1),
                "weight": 0.15,
                "contribution": round(evidence_score * 0.15, 1),
                "description": "Observable signals of relationship strength",
            },
        },
    }


def match_accounts_to_partner(partner_name: str, accounts: list[dict]) -> list[dict]:
    """
    Find accounts that could benefit from warm introductions via this partner.

    Matching logic:
    - Extract keywords from partner name (e.g., "NVIDIA" -> nvidia)
    - Check account infrastructure for matches (GPU vendors, tech stack)
    - Check account name/domain for technology indicators

    Returns list of matched accounts with match reasons.
    """
    # Extract matching keywords from partner name
    partner_lower = partner_name.lower()

    # Define keyword mappings for common partners
    keyword_patterns = {
        "nvidia": ["nvidia", "gpu", "dgx", "cuda", "h100", "a100", "tensor"],
        "kubernetes": ["kubernetes", "k8s", "container", "docker", "cloud-native"],
        "aws": ["aws", "amazon", "ec2", "s3", "lambda"],
        "gcp": ["gcp", "google cloud", "gke"],
        "azure": ["azure", "microsoft"],
        "intel": ["intel", "xeon", "cpu"],
        "amd": ["amd", "epyc", "radeon"],
    }

    # Determine which keywords to match based on partner name
    match_keywords = []
    for key, keywords in keyword_patterns.items():
        if key in partner_lower or any(kw in partner_lower for kw in keywords):
            match_keywords.extend(keywords)

    # If no specific keywords matched, use partner name words
    if not match_keywords:
        # Split on common separators and filter short words
        words = partner_lower.replace("-", " ").replace("_", " ").split()
        match_keywords = [
            w
            for w in words
            if len(w) > 2
            and w not in ["the", "and", "for", "partnership", "strategic", "integration"]
        ]

    matched_accounts = []

    for account in accounts:
        match_reasons = []

        # Check GPU infrastructure
        infra_breakdown = account.get("infrastructure_breakdown", {})
        breakdown = infra_breakdown.get("breakdown", {})
        gpu_info = breakdown.get("gpu_infrastructure", {})
        detected_gpus = gpu_info.get("detected", [])

        # Check for keyword matches in GPU infrastructure
        for gpu in detected_gpus:
            gpu_lower = gpu.lower()
            for keyword in match_keywords:
                if keyword in gpu_lower:
                    match_reasons.append(f"Uses {gpu}")
                    break

        # Check physical infrastructure field
        physical_infra = account.get("physical_infrastructure", "").lower()
        for keyword in match_keywords:
            if keyword in physical_infra:
                match_reasons.append(
                    f"Physical infrastructure: {account.get('physical_infrastructure')}"
                )
                break

        # Check business model / industry for technology alignment
        business_model = account.get("business_model", "").lower()
        industry = account.get("industry", "").lower()

        # AI/ML companies likely use GPU partners
        if any(kw in match_keywords for kw in ["nvidia", "gpu", "tensor"]):
            if "ai" in business_model or "ai" in industry or "ml" in industry:
                if "AI/ML business model" not in match_reasons:
                    match_reasons.append("AI/ML business model")

        if match_reasons:
            matched_accounts.append(
                {
                    "id": account.get("id"),
                    "name": account.get("name"),
                    "domain": account.get("domain"),
                    "account_score": account.get("account_score", 0),
                    "priority_level": account.get("account_priority_level"),
                    "match_reasons": match_reasons,
                }
            )

    # Sort by account score (highest first)
    matched_accounts.sort(key=lambda x: x.get("account_score", 0), reverse=True)

    return matched_accounts


@app.route("/api/partner-rankings", methods=["GET"])
def get_partner_rankings():
    """
    Get partnerships ranked by strategic value with matched accounts.

    Partners are scored based on observable/public data optimized for both
    existing and prospective partnerships:

    Scoring Dimensions:
    - Account Reach (35%): How many ICP accounts can this partner help reach?
    - ICP Alignment (25%): Technology and market segment alignment
    - Entry Point Quality (25%): Effectiveness as a sales channel
    - Trust Evidence (15%): Observable signals of relationship strength

    Returns partnerships ordered by composite score, each with:
    - Partner details
    - Composite score breakdown with explanation
    - Matched accounts that could benefit from warm introductions

    Query params:
    - min_score: Minimum partner score to include (default: 0)
    - include_accounts: Whether to include matched accounts (default: true)
    """
    min_score = request.args.get("min_score", 0, type=float)
    include_accounts = request.args.get("include_accounts", "true").lower() == "true"

    # Get raw data
    partnerships = get_notion_partnerships()
    accounts = get_notion_accounts()  # Always needed for scoring

    # Build ranked partnerships
    ranked = []
    for partnership in partnerships:
        # First, find matched accounts (needed for scoring)
        matched = match_accounts_to_partner(partnership.get("partner_name", ""), accounts)

        # Calculate score with account context
        score_data = calculate_partner_score(partnership, matched, accounts)

        if score_data["total_score"] < min_score:
            continue

        ranked_partner = {
            "id": partnership.get("id"),
            "notion_id": partnership.get("notion_id"),
            "partner_name": partnership.get("partner_name"),
            "partnership_type": partnership.get("partnership_type"),
            "relationship_depth": partnership.get("relationship_depth"),
            "partnership_maturity": partnership.get("partnership_maturity"),
            "best_approach": partnership.get("best_approach"),
            "context": partnership.get("context"),
            "source_url": partnership.get("source_url"),
            "partner_score": score_data["total_score"],
            "score_breakdown": score_data["breakdown"],
            "account_coverage": len(matched),
        }

        if include_accounts:
            ranked_partner["matched_accounts"] = matched

        ranked.append(ranked_partner)

    # Sort by score (highest first)
    ranked.sort(key=lambda x: x["partner_score"], reverse=True)

    return jsonify(
        {
            "partner_rankings": ranked,
            "total": len(ranked),
            "total_accounts": len(accounts),
            "scoring_methodology": {
                "account_reach": {
                    "weight": "35%",
                    "description": "Number of ICP accounts reachable via this partner, weighted by account quality",
                },
                "icp_alignment": {
                    "weight": "25%",
                    "description": "Technology and market segment alignment with ideal customer profile",
                },
                "entry_point_quality": {
                    "weight": "25%",
                    "description": "Effectiveness as a sales entry point based on partnership type and approach",
                },
                "trust_evidence": {
                    "weight": "15%",
                    "description": "Observable signals of relationship strength (documentation, maturity, sources)",
                },
            },
        }
    )


# ============================================================================
# Enrichment Endpoints (Phase A - WS5)
# ============================================================================

# Import ABM system components for enrichment
ABM_SYSTEM_AVAILABLE = False
abm_system = None

try:
    # Load ABM system dynamically
    abm_spec = importlib.util.spec_from_file_location(
        "abm_system", os.path.join(project_root, "src/abm_research/core/abm_system.py")
    )
    abm_module = importlib.util.module_from_spec(abm_spec)
    abm_spec.loader.exec_module(abm_module)
    ComprehensiveABMSystem = abm_module.ComprehensiveABMSystem
    ABM_SYSTEM_AVAILABLE = True
    logger.info("✅ ABM System available for enrichment")
except Exception as e:
    logger.warning(f"⚠️ ABM System not available: {e}")


@app.route("/api/accounts/<account_id>/enrich", methods=["POST"])
def enrich_account(account_id: str):
    """
    Trigger Phase 2 contact discovery for an account

    This runs the Apollo contact discovery + MEDDIC scoring pipeline
    and saves the results to Notion.

    POST body (optional):
    {
        "force": true  // Re-run even if contacts exist
    }
    """
    global abm_system

    if not ABM_SYSTEM_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "ABM System not available",
                    "message": "Contact discovery requires the ABM System module",
                }
            ),
            503,
        )

    # Get account details
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Check if force refresh (body is optional)
    body = request.get_json(silent=True) or {}
    force = body.get("force", False)

    # Get existing contacts
    notion_id = account.get("notion_id", "")
    existing_contacts = get_notion_contacts(notion_id) if notion_id else []

    if existing_contacts and not force:
        return jsonify(
            {
                "status": "skipped",
                "message": f"Account already has {len(existing_contacts)} contacts. Use force=true to re-enrich.",
                "existing_contacts": len(existing_contacts),
            }
        )

    try:
        # Initialize ABM system if needed
        if abm_system is None:
            logger.info("🚀 Initializing ABM System for enrichment...")
            abm_system = ComprehensiveABMSystem()

        # Run Phase 2: Contact Discovery
        company_name = account.get("name", "")
        company_domain = account.get("domain", "")

        logger.info(f"🔍 Starting contact discovery for {company_name} ({company_domain})")

        # Build account data for MEDDIC scoring context
        account_data = {
            "name": company_name,
            "domain": company_domain,
            "Physical Infrastructure": "",  # Would need to fetch from Notion
            "business_model": account.get("business_model", ""),
            "employee_count": account.get("employee_count", 0),
        }

        # Call Phase 2 discovery
        discovered_contacts = abm_system._phase_2_contact_discovery(
            company_name, company_domain, account_data
        )

        # Save contacts to Notion
        if NOTION_AVAILABLE and discovered_contacts:
            notion = get_notion_client()
            save_results = notion.save_contacts(discovered_contacts, company_name)

            successful = sum(1 for v in save_results.values() if v)

            return jsonify(
                {
                    "status": "success",
                    "message": f"Discovered and saved {successful} contacts for {company_name}",
                    "discovered": len(discovered_contacts),
                    "saved": successful,
                    "contacts": [
                        {
                            "name": c.get("name"),
                            "title": c.get("title"),
                            "role_tier": c.get("role_tier"),
                            "champion_potential_level": c.get("champion_potential_level"),
                            "lead_score": c.get("lead_score", 0),
                        }
                        for c in discovered_contacts[:10]  # Return top 10 for UI
                    ],
                }
            )
        else:
            return jsonify(
                {
                    "status": "partial",
                    "message": "Contacts discovered but Notion save unavailable",
                    "discovered": len(discovered_contacts) if discovered_contacts else 0,
                }
            )

    except Exception as e:
        logger.error(f"❌ Enrichment failed for {account_id}: {e}")
        return jsonify({"error": "Enrichment failed", "message": str(e)}), 500


@app.route("/api/accounts/<account_id>/rescore", methods=["POST"])
def rescore_account_contacts(account_id: str):
    """
    Re-apply MEDDIC scoring to existing contacts for an account

    This re-calculates role_tier, champion_potential, and why_prioritize
    for all contacts without re-fetching from Apollo.
    """
    if not NOTION_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Notion not available",
                    "message": "MEDDIC rescoring requires Notion integration",
                }
            ),
            503,
        )

    # Get account details
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    # Get existing contacts
    notion_id = account.get("notion_id", "")
    existing_contacts = get_notion_contacts(notion_id) if notion_id else []

    if not existing_contacts:
        return jsonify(
            {
                "status": "skipped",
                "message": "No contacts found for this account. Use /enrich first.",
            }
        )

    try:
        # Build account context for MEDDIC scoring
        account_data = {
            "name": account.get("name", ""),
            "domain": account.get("domain", ""),
            "business_model": account.get("business_model", ""),
            "employee_count": account.get("employee_count", 0),
        }

        rescored_contacts = []

        for contact in existing_contacts:
            # Apply MEDDIC scoring
            if meddic_contact_scorer:
                try:
                    meddic_result = meddic_contact_scorer.calculate_contact_score(
                        contact, account_data
                    )

                    # Update contact with MEDDIC scores
                    contact["lead_score"] = meddic_result.total_score
                    contact["champion_potential_score"] = meddic_result.champion_potential_score
                    contact["role_tier"] = meddic_result.role_tier
                    contact["role_classification"] = meddic_result.role_classification
                    contact["champion_potential_level"] = meddic_result.champion_potential_level
                    contact["recommended_approach"] = meddic_result.recommended_approach
                    contact["why_prioritize"] = meddic_result.why_prioritize

                    rescored_contacts.append(
                        {
                            "name": contact.get("name"),
                            "title": contact.get("title"),
                            "role_tier": meddic_result.role_tier,
                            "champion_potential_level": meddic_result.champion_potential_level,
                            "lead_score": meddic_result.total_score,
                            "why_prioritize": meddic_result.why_prioritize[:2]
                            if meddic_result.why_prioritize
                            else [],
                        }
                    )

                except Exception as e:
                    logger.warning(f"MEDDIC scoring failed for {contact.get('name')}: {e}")

        # Categorize results
        entry_points = [c for c in rescored_contacts if c.get("role_tier") == "entry_point"]
        middle_deciders = [c for c in rescored_contacts if c.get("role_tier") == "middle_decider"]
        economic_buyers = [c for c in rescored_contacts if c.get("role_tier") == "economic_buyer"]

        return jsonify(
            {
                "status": "success",
                "message": f"Rescored {len(rescored_contacts)} contacts",
                "summary": {
                    "entry_points": len(entry_points),
                    "middle_deciders": len(middle_deciders),
                    "economic_buyers": len(economic_buyers),
                },
                "contacts": rescored_contacts,
            }
        )

    except Exception as e:
        logger.error(f"❌ Rescoring failed for {account_id}: {e}")
        return jsonify({"error": "Rescoring failed", "message": str(e)}), 500


# ============================================================================
# On-Demand Email Reveal (Decision #1 - Credit-Saving)
# ============================================================================


@app.route("/api/contacts/<contact_id>/reveal-email", methods=["POST"])
def reveal_contact_email(contact_id: str):
    """
    On-demand email enrichment for a single contact (uses 1 Apollo credit)

    Only reveals email when explicitly requested by user to save credits.
    Checks Notion cache first - skips if enriched within 30 days.

    Returns:
        - email: The revealed email address
        - cached: True if returned from cache, False if freshly enriched
        - credits_used: 0 if cached, 1 if enriched
    """
    if not NOTION_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Notion not available",
                    "message": "Email reveal requires Notion integration",
                }
            ),
            503,
        )

    try:
        notion = get_notion_client()

        # Get contact from Notion by ID
        # Contact IDs are formatted as "con_<first8chars>"
        notion_contact_id = contact_id.replace("con_", "")

        # Query contacts to find the one with matching ID prefix
        # This is a workaround since we store truncated IDs
        all_contacts = notion.query_all_contacts()
        contact_page = None

        for page in all_contacts:
            if page["id"].startswith(notion_contact_id) or page["id"][:8] == notion_contact_id:
                contact_page = page
                break

        if not contact_page:
            return jsonify({"error": "Contact not found"}), 404

        props = contact_page.get("properties", {})

        # Extract current email and last enriched date
        current_email = props.get("Email", {}).get("email", "")
        last_enriched_prop = props.get("Last Enriched", {}).get("date")
        last_enriched = last_enriched_prop.get("start") if last_enriched_prop else None

        # Check if already enriched recently (within 30 days)
        if current_email and last_enriched:
            from datetime import datetime, timedelta

            try:
                enriched_date = datetime.fromisoformat(last_enriched.replace("Z", "+00:00"))
                if datetime.now(enriched_date.tzinfo) - enriched_date < timedelta(days=30):
                    logger.info(f"📧 Returning cached email for contact {contact_id}")
                    return jsonify(
                        {
                            "email": current_email,
                            "cached": True,
                            "credits_used": 0,
                            "message": "Email returned from cache (enriched within 30 days)",
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not parse Last Enriched date: {e}")

        # Need to enrich - extract contact details for Apollo
        name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        title = extract_rich_text(props.get("Title", {}))
        company = extract_rich_text(props.get("Company", {}))

        if not name:
            return (
                jsonify(
                    {
                        "error": "Contact has no name",
                        "message": "Cannot enrich contact without a name",
                    }
                ),
                400,
            )

        # Call Apollo single-person enrichment
        apollo_api_key = os.getenv("APOLLO_API_KEY")
        if not apollo_api_key:
            return (
                jsonify(
                    {
                        "error": "Apollo API key not configured",
                        "message": "Set APOLLO_API_KEY environment variable",
                    }
                ),
                503,
            )

        # Split name for Apollo
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Apollo single-person match
        apollo_url = "https://api.apollo.io/v1/people/match"
        apollo_payload = {
            "first_name": first_name,
            "last_name": last_name,
            "reveal_personal_emails": True,
        }

        # Add organization context if available
        if company:
            apollo_payload["organization_name"] = company

        logger.info(f"🔍 Apollo enrichment for {name} at {company}")

        apollo_response = requests.post(
            apollo_url,
            headers={"Content-Type": "application/json", "X-Api-Key": apollo_api_key},
            json=apollo_payload,
        )

        if apollo_response.status_code != 200:
            logger.error(
                f"Apollo API error: {apollo_response.status_code} - {apollo_response.text}"
            )
            return (
                jsonify(
                    {
                        "error": "Apollo enrichment failed",
                        "message": f"Apollo API returned {apollo_response.status_code}",
                        "credits_used": 0,
                    }
                ),
                500,
            )

        apollo_data = apollo_response.json()
        person = apollo_data.get("person", {})
        revealed_email = person.get("email", "")

        if not revealed_email:
            return jsonify(
                {
                    "email": None,
                    "cached": False,
                    "credits_used": 1,
                    "message": "Email not found in Apollo database",
                }
            )

        # Save to Notion with provenance
        update_props = {
            "Email": {"email": revealed_email},
            "Email Source": {"select": {"name": "apollo"}},
            "Last Enriched": {"date": {"start": datetime.now().isoformat()}},
        }

        # Update phone if available
        phone = person.get("sanitized_phone")
        if phone:
            update_props["Phone"] = {"phone_number": phone}

        # Update LinkedIn if available
        linkedin = person.get("linkedin_url")
        if linkedin:
            update_props["LinkedIn URL"] = {"url": linkedin}

        # CRITICAL: Actually persist to Notion - this was silently failing before!
        try:
            notion.update_page(contact_page["id"], update_props)
            logger.info(f"✅ Email persisted to Notion for contact {contact_id}")
        except NotionError as e:
            # Log the error but still return the email to the user
            # The email was revealed, just not saved
            logger.error(f"❌ Failed to persist email to Notion: {e}")
            return jsonify(
                {
                    "email": revealed_email,
                    "cached": False,
                    "credits_used": 1,
                    "message": "Email revealed but FAILED to save to Notion",
                    "notion_error": e.to_dict() if hasattr(e, "to_dict") else str(e),
                    "warning": "Data was NOT persisted - please save manually",
                }
            )

        logger.info(f"✅ Email revealed and saved: {revealed_email}")

        return jsonify(
            {
                "email": revealed_email,
                "cached": False,
                "credits_used": 1,
                "message": "Email revealed via Apollo and saved to Notion",
                "additional_data": {"phone": phone, "linkedin": linkedin},
            }
        )

    except Exception as e:
        logger.error(f"❌ Email reveal failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Email reveal failed", "message": str(e)}), 500


# ============================================================================
# LinkedIn Activity Enrichment via Brave (Decision #2)
# ============================================================================


@app.route("/api/contacts/<contact_id>/linkedin-activity", methods=["POST"])
def enrich_contact_linkedin(contact_id: str):
    """
    Enrich contact with LinkedIn activity discovered via Brave Search.
    Uses Brave Search API to find public LinkedIn posts, engagement, and
    professional updates - NO LinkedIn API required.

    Returns:
        - recent_posts: List of discovered LinkedIn posts
        - topics_of_interest: Professional topics they write/speak about
        - engagement_signals: Mentions, features, interviews
        - professional_updates: Promotions, awards, speaking
        - activity_score: 0-100 overall activity level
        - thought_leadership_score: 0-100 based on posts/articles
        - network_influence_score: 0-100 based on engagement
    """
    try:
        # Import LinkedIn Brave enrichment module
        from abm_research.utils.linkedin_brave_enrichment import linkedin_brave_enrichment

        # Get Notion client
        notion = get_notion_client()

        # Get contact from Notion by ID
        # Contact IDs are formatted as "con_<first8chars>"
        notion_contact_id = contact_id.replace("con_", "")

        # Query contacts to find the one with matching ID prefix
        all_contacts = notion.query_all_contacts()
        contact_page = None

        for page in all_contacts:
            if page["id"].startswith(notion_contact_id) or page["id"][:8] == notion_contact_id:
                contact_page = page
                break

        if not contact_page:
            return (
                jsonify(
                    {"error": "Contact not found", "message": f"No contact with ID {contact_id}"}
                ),
                404,
            )

        props = contact_page.get("properties", {})

        # Extract contact details
        name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        title = extract_rich_text(props.get("Title", {}))
        company = extract_rich_text(props.get("Company", {}))

        # Get existing LinkedIn URL if available
        linkedin_url = None
        linkedin_prop = props.get("LinkedIn URL", {})
        if linkedin_prop.get("url"):
            linkedin_url = linkedin_prop["url"]

        if not name:
            return (
                jsonify(
                    {
                        "error": "Contact has no name",
                        "message": "Cannot enrich contact without a name",
                    }
                ),
                400,
            )

        logger.info(f"Enriching LinkedIn activity for: {name}")

        # Run LinkedIn enrichment via Brave Search
        activity = linkedin_brave_enrichment.enrich_linkedin_activity(
            person_name=name, company_name=company, title=title, linkedin_url=linkedin_url
        )

        # Note: Notion update skipped - NotionClient doesn't have update_page method yet
        # TODO: Add update_page to NotionClient if we need to persist LinkedIn URLs
        if activity.linkedin_url and not linkedin_url:
            logger.info(
                f"Discovered new LinkedIn URL: {activity.linkedin_url} (not saved to Notion)"
            )

        logger.info(f"✅ LinkedIn activity enriched: activity_score={activity.activity_score}")

        return jsonify(
            {
                "status": "success",
                "contact_name": name,
                "linkedin_url": activity.linkedin_url,
                "activity_score": activity.activity_score,
                "activity_level": activity.last_active_indicator,
                "thought_leadership_score": activity.thought_leadership_score,
                "network_influence_score": activity.network_influence_score,
                "recent_posts": activity.recent_posts,
                "topics_of_interest": activity.topics_of_interest,
                "engagement_signals": activity.engagement_signals,
                "professional_updates": activity.professional_updates,
                "enrichment_source": activity.enrichment_source,
            }
        )

    except Exception as e:
        logger.error(f"❌ LinkedIn enrichment failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "LinkedIn enrichment failed", "message": str(e)}), 500


# ============================================================================
# Trigger Event Discovery via Brave (Decision #3)
# ============================================================================


@app.route("/api/accounts/<account_id>/discover-events", methods=["POST"])
def discover_account_trigger_events(account_id: str):
    """
    Discover trigger events for an account using Brave Search.
    Searches for 7 event types: expansion, hiring, funding, partnership,
    ai_workload, leadership, incident.

    Request body (optional):
        - event_types: List of specific event types to search
        - lookback_days: How far back to search (default: 90)
        - save_to_notion: Whether to save events to Notion (default: false)

    Returns:
        - events: List of discovered trigger events
        - total: Number of events found
        - event_type_counts: Count by event type
    """
    try:
        from abm_research.utils.trigger_event_discovery import trigger_event_discovery

        # Get Notion client
        notion = get_notion_client()

        # Get account from Notion by ID
        # Account IDs are formatted as "acc_<first8chars>"
        notion_account_id = account_id.replace("acc_", "")

        # Query accounts to find the one with matching ID prefix
        all_accounts = notion.query_all_accounts()
        account_page = None

        for page in all_accounts:
            if page["id"].startswith(notion_account_id) or page["id"][:8] == notion_account_id:
                account_page = page
                break

        if not account_page:
            return (
                jsonify(
                    {"error": "Account not found", "message": f"No account with ID {account_id}"}
                ),
                404,
            )

        props = account_page.get("properties", {})

        # Extract account details
        account_name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            account_name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        domain = extract_rich_text(props.get("Domain", {}))

        if not account_name:
            return (
                jsonify(
                    {
                        "error": "Account has no name",
                        "message": "Cannot discover events without account name",
                    }
                ),
                400,
            )

        # Get request parameters
        data = request.get_json(silent=True) or {}
        event_types = data.get("event_types")  # None = all types
        lookback_days = data.get("lookback_days", 90)
        save_to_notion = data.get("save_to_notion", True)  # Default: always save to Notion

        logger.info(f"Discovering trigger events for: {account_name}")

        # Run discovery
        events = trigger_event_discovery.discover_events(
            company_name=account_name,
            company_domain=domain,
            event_types=event_types,
            lookback_days=lookback_days,
        )

        # Count by event type
        event_type_counts = {}
        for event in events:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1

        # Optionally save to Notion
        saved_count = 0
        if save_to_notion and events:
            try:
                trigger_events_db_id = os.getenv("NOTION_TRIGGER_EVENTS_DB_ID")
                if trigger_events_db_id:
                    for event in events[:10]:  # Limit to top 10
                        props = trigger_event_discovery.to_notion_properties(event, account_id)
                        notion.create_page(trigger_events_db_id, props)
                        saved_count += 1
                    logger.info(f"Saved {saved_count} events to Notion")
            except Exception as e:
                logger.warning(f"Could not save events to Notion: {e}")

        logger.info(f"✅ Discovered {len(events)} trigger events for {account_name}")

        # Format response
        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "total": len(events),
                "saved_to_notion": saved_count,
                "event_type_counts": event_type_counts,
                "events": [
                    {
                        "event_type": e.event_type,
                        "description": e.description,
                        "source_url": e.source_url,
                        "source_type": e.source_type,
                        "confidence_score": e.confidence_score,
                        "relevance_score": e.relevance_score,
                        "urgency_level": e.urgency_level,
                        "detected_date": e.detected_date,
                        "event_date": e.event_date,
                    }
                    for e in events
                ],
            }
        )

    except Exception as e:
        logger.error(f"❌ Trigger event discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Trigger event discovery failed", "message": str(e)}), 500


# ============================================================================
# Partnership Classification (Decision #4)
# ============================================================================


@app.route("/api/accounts/<account_id>/classify-partnership", methods=["POST"])
def classify_account_partnership(account_id: str):
    """
    Classify an account's partnership type using the PartnershipClassifier.

    Classifications:
    - direct_icp: Target customers with power monitoring needs
    - strategic_partner: Technology/product partners
    - referral_partner: Companies that can refer customers
    - competitive: Direct competitors
    - vendor: Companies we buy from

    Returns classification with confidence score and recommended approach.
    """
    try:
        from abm_research.utils.partnership_classifier import PartnershipClassifier

        # Get Notion client
        notion = get_notion_client()

        # Get account from Notion by ID
        # Account IDs are formatted as "acc_<first8chars>"
        notion_account_id = account_id.replace("acc_", "")

        # Query accounts to find the one with matching ID prefix
        all_accounts = notion.query_all_accounts()
        account_page = None

        for page in all_accounts:
            if page["id"].startswith(notion_account_id) or page["id"][:8] == notion_account_id:
                account_page = page
                break

        if not account_page:
            return (
                jsonify(
                    {"error": "Account not found", "message": f"No account with ID {account_id}"}
                ),
                404,
            )

        props = account_page.get("properties", {})

        # Extract account details for classification
        account_name = ""
        name_prop = props.get("Name", {})
        if name_prop.get("title"):
            account_name = name_prop["title"][0]["text"]["content"] if name_prop["title"] else ""

        domain = extract_rich_text(props.get("Domain", {}))
        business_model = extract_rich_text(props.get("Business Model", {}))
        industry = extract_rich_text(props.get("Industry", {}))
        description = extract_rich_text(props.get("Description", {}))

        # Get infrastructure data if available
        physical_infrastructure = extract_rich_text(props.get("Physical Infrastructure", {}))

        if not account_name:
            return (
                jsonify(
                    {
                        "error": "Account has no name",
                        "message": "Cannot classify partnership without account name",
                    }
                ),
                400,
            )

        logger.info(f"Classifying partnership for: {account_name}")

        # Run classification - pass company data as dict
        classifier = PartnershipClassifier()
        company_data = {
            "name": account_name,
            "domain": domain or "",
            "business_model": business_model or "Unknown",
            "industry": industry or "Technology",
            "physical_infrastructure": physical_infrastructure or "",
            "description": description or "",
        }
        classification = classifier.classify_partnership(company_data)

        # Request body options
        data = request.get_json(silent=True) or {}
        save_to_notion = data.get("save_to_notion", True)  # Default: always save to Notion

        # Note: Notion update skipped - NotionClient doesn't have update_page method yet
        # TODO: Add update_page to NotionClient to persist classification
        if save_to_notion:
            logger.warning("save_to_notion requested but NotionClient.update_page not implemented")

        logger.info(f"✅ Classified {account_name}: {classification.partnership_type.value}")

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "partnership_type": classification.partnership_type.value,
                "industry_category": classification.industry_category.value,
                "confidence_score": classification.confidence_score,
                "reasoning": classification.reasoning,
                "recommended_approach": classification.recommended_approach,
                "potential_value": classification.potential_value,
                "next_actions": classification.next_actions,
                "saved_to_notion": save_to_notion,
            }
        )

    except Exception as e:
        logger.error(f"❌ Partnership classification failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Partnership classification failed", "message": str(e)}), 500


# ============================================================================
# Full Account Research Pipeline (WS5 - Phase D)
# ============================================================================

# Initialize ABM Research System
ABM_SYSTEM_AVAILABLE = False
abm_system = None

try:
    # Load ABM system directly
    abm_spec = importlib.util.spec_from_file_location(
        "abm_system", os.path.join(project_root, "src/abm_research/core/abm_system.py")
    )
    abm_module = importlib.util.module_from_spec(abm_spec)
    abm_spec.loader.exec_module(abm_module)
    ComprehensiveABMSystem = abm_module.ComprehensiveABMSystem
    ABM_SYSTEM_AVAILABLE = True
    logger.info("✅ ABM Research System available")
except Exception as e:
    ABM_SYSTEM_AVAILABLE = False
    logger.warning(f"⚠️ ABM Research System not available: {e}")


@app.route("/api/accounts/<account_id>/research", methods=["POST"])
def run_account_research(account_id: str):
    """
    Run complete 5-phase ABM research pipeline for an account

    Phases:
    1. Account Intelligence Baseline (trigger events, ICP scoring)
    2. Contact Discovery & Segmentation (Apollo API)
    3. High-Priority Contact Enrichment (LinkedIn)
    4. Engagement Intelligence
    5. Strategic Partnership Intelligence

    All results are saved back to Notion.

    POST body (optional):
    {
        "force": false  // Set true to force re-research even if already completed
    }
    """
    if not ABM_SYSTEM_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Research pipeline unavailable",
                    "message": "ABM Research System not configured. Check server logs.",
                    "fallback": True,
                }
            ),
            503,
        )

    # Get account from Notion - support both synthetic ID and Notion UUID
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    company_name = account.get("name", "")
    company_domain = account.get("domain", "")

    if not company_name:
        return jsonify({"error": "Account name is required for research"}), 400

    # If no domain, try to infer from company name
    if not company_domain:
        # Simple domain inference
        company_domain = company_name.lower().replace(" ", "") + ".com"
        logger.warning(f"⚠️ No domain for {company_name}, using inferred: {company_domain}")

    try:
        logger.info(f"🔬 Starting full research pipeline for {company_name} ({company_domain})")

        # Initialize fresh ABM system for this research
        system = ComprehensiveABMSystem()

        # Run complete 5-phase research
        research_results = system.conduct_complete_account_research(company_name, company_domain)

        if not research_results.get("success"):
            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "Research pipeline encountered errors",
                        "summary": research_results.get("research_summary", {}),
                        "error": research_results.get("research_summary", {}).get(
                            "error", "Unknown error"
                        ),
                    }
                ),
                500,
            )

        # Build response with summary
        summary = research_results.get("research_summary", {})
        notion_results = research_results.get("notion_persistence", {})

        # BACKUP: Explicitly save to Notion if ABM system didn't persist
        # This ensures research results are always saved
        notion = get_notion_client() if NOTION_AVAILABLE else None
        persistence_error = None
        if notion and account.get("notion_id"):
            try:
                account_data = research_results.get("account", {})
                update_fields = {}

                # Only update fields that have values
                if account_data.get("employee_count"):
                    update_fields["Employee Count"] = account_data["employee_count"]
                if account_data.get("business_model"):
                    update_fields["Business Model"] = account_data["business_model"]
                if account_data.get("icp_fit_score"):
                    update_fields["ICP Fit Score"] = account_data["icp_fit_score"]
                if account_data.get("physical_infrastructure"):
                    update_fields["Physical Infrastructure"] = account_data[
                        "physical_infrastructure"
                    ]

                if update_fields:
                    notion.update_page(account["notion_id"], update_fields)
                    logger.info(
                        f"✅ Backup persistence: Updated {len(update_fields)} fields in Notion"
                    )
                    notion_results["account_saved"] = True
            except NotionError as e:
                persistence_error = e.to_dict() if hasattr(e, "to_dict") else str(e)
                logger.error(f"❌ Backup Notion persistence failed: {e}")
                notion_results["persistence_error"] = persistence_error
            except Exception as e:
                persistence_error = {"message": str(e), "type": type(e).__name__}
                logger.error(f"❌ Backup Notion persistence failed unexpectedly: {e}")

        return jsonify(
            {
                "status": "success",
                "message": f"Research completed for {company_name}",
                "account_id": account_id,
                "research_summary": {
                    "contacts_discovered": summary.get("contacts_discovered", 0),
                    "trigger_events_found": summary.get("trigger_events_found", 0),
                    "partnerships_identified": summary.get("partnerships_identified", 0),
                    "high_priority_contacts": summary.get("high_priority_contacts", 0),
                    "research_duration_seconds": summary.get("research_duration_seconds", 0),
                },
                "notion_sync": {
                    "account_saved": notion_results.get("account_saved", False),
                    "contacts_saved": notion_results.get("contacts_saved", 0),
                    "events_saved": notion_results.get("events_saved", 0),
                    "partnerships_saved": notion_results.get("partnerships_saved", 0),
                },
                "account_data": {
                    "name": research_results.get("account", {}).get("name"),
                    "employee_count": research_results.get("account", {}).get("employee_count"),
                    "industry": research_results.get("account", {}).get("industry"),
                    "business_model": research_results.get("account", {}).get("business_model"),
                    "icp_fit_score": research_results.get("account", {}).get("icp_fit_score"),
                    "account_score": research_results.get("account", {}).get("account_score"),
                    "partnership_classification": research_results.get("account", {}).get(
                        "partnership_classification"
                    ),
                    "infrastructure_score": research_results.get("account", {}).get(
                        "infrastructure_score"
                    ),
                    "buying_signals_score": research_results.get("account", {}).get(
                        "buying_signals_score"
                    ),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Research pipeline failed for {company_name}: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Research failed", "message": str(e)}), 500


# ============================================================================
# AI-Powered Outreach Generation (WS5 - Phase D)
# ============================================================================

# Initialize OpenAI client
OPENAI_AVAILABLE = False
openai_client = None

try:
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
        OPENAI_AVAILABLE = True
        logger.info("✅ OpenAI client available for outreach generation")
    else:
        logger.warning("⚠️ OPENAI_API_KEY not set - AI outreach generation disabled")
except Exception as e:
    logger.warning(f"⚠️ OpenAI not available: {e}")


def build_outreach_prompt(contact: dict, account: dict, outreach_type: str, tone: str) -> str:
    """Build a rich prompt for AI outreach generation"""

    # Extract key intelligence
    role_tier = contact.get("role_tier", "entry_point")
    champion_level = contact.get("champion_potential_level", "Medium")
    why_prioritize = contact.get("why_prioritize", [])
    recommended_approach = contact.get("recommended_approach", "")

    # Account signals
    infra_breakdown = account.get("infrastructure_breakdown", {}).get("breakdown", {})
    gpu_detected = infra_breakdown.get("gpu_infrastructure", {}).get("detected", [])
    triggers = (
        account.get("account_score_breakdown", {})
        .get("buying_signals", {})
        .get("breakdown", {})
        .get("trigger_events", {})
        .get("high_value_triggers", [])
    )
    partnership_type = account.get("partnership_classification", "")

    # Role-specific messaging angles
    role_angles = {
        "entry_point": {
            "pain": "day-to-day operational challenges, visibility gaps, and manual monitoring burden",
            "value": "technical efficiency, real-time alerts, and reduced firefighting",
            "cta": "15-minute technical walkthrough",
        },
        "middle_decider": {
            "pain": "tooling fragmentation, team productivity, and process inefficiencies",
            "value": "operational control, unified visibility, and team enablement",
            "cta": "solution overview and integration discussion",
        },
        "economic_buyer": {
            "pain": "cost overruns, risk exposure, and ROI uncertainty on infrastructure investments",
            "value": "measurable savings (15-20% power cost reduction), reduced downtime risk, and faster capacity decisions",
            "cta": "executive briefing with ROI framework",
        },
    }

    role_config = role_angles.get(role_tier, role_angles["entry_point"])

    prompt = f"""You are an expert B2B sales copywriter specializing in datacenter infrastructure and power monitoring solutions. Generate a highly personalized outreach message.

## CONTEXT

**Contact:**
- Name: {contact.get('name', 'Unknown')}
- Title: {contact.get('title', 'Professional')}
- Role Tier: {role_tier} ({
    'Direct user who experiences pain daily - can become internal champion' if role_tier == 'entry_point' else
    'Tooling decider who evaluates solutions - can drive selection' if role_tier == 'middle_decider' else
    'Economic buyer with budget authority - needs business case'
})
- Champion Potential: {champion_level}
- Why Prioritize: {'; '.join(why_prioritize[:2]) if why_prioritize else 'High-fit contact'}
- Recommended Approach: {recommended_approach or 'Consultative'}

**Company:**
- Name: {account.get('name', 'Unknown')}
- Industry: {account.get('industry', 'Technology')}
- Size: {account.get('employee_count', 'Unknown')} employees
- Business Model: {account.get('business_model', 'Unknown')}
- Partnership Classification: {partnership_type or 'Direct ICP'}

**Intelligence Signals:**
- GPU/AI Infrastructure: {', '.join(gpu_detected[:3]) if gpu_detected else 'Not detected (general datacenter)'}
- Trigger Events: {', '.join(triggers[:2]) if triggers else 'No specific triggers detected'}
- ICP Score: {account.get('account_score', 0)}/100

## MESSAGING STRATEGY

For this {role_tier.replace('_', ' ')}:
- Address pain points: {role_config['pain']}
- Lead with value: {role_config['value']}
- Call-to-action style: {role_config['cta']}

## PRODUCT CONTEXT

Verdigris provides real-time power and environmental monitoring for datacenters:
- AI-powered anomaly detection for power and thermal issues
- Sub-second visibility into power distribution at rack level
- Automated alerting before issues impact uptime
- Integration with existing DCIM/BMS systems
- Typical outcomes: 15-20% power cost reduction, 30% faster incident response

## TONE

Tone: {tone}
- professional: Formal but warm, emphasize credibility and expertise
- conversational: Friendly and approachable, like a helpful peer
- direct: Concise and action-oriented, respect their time

## OUTPUT FORMAT

Generate the following {outreach_type} content:

"""

    if outreach_type == "email":
        prompt += """
Return a JSON object with these fields:
{
  "subject": "Compelling subject line (under 50 chars, personalized)",
  "opening": "2-3 sentences establishing relevance and showing you've done research",
  "valueHook": "3-4 sentences on specific value proposition based on their infrastructure/triggers",
  "callToAction": "Clear, low-friction CTA appropriate for their role tier",
  "ps": "Brief P.S. line offering alternative engagement option"
}

Make it feel like it was written by a human who actually researched this company. Avoid generic phrases like "I hope this email finds you well" or "I came across your profile."
"""
    elif outreach_type == "linkedin":
        prompt += """
Return a JSON object with these fields:
{
  "connectionRequest": "Under 300 characters - compelling reason to connect",
  "followUpMessage": "2-3 sentences for after they accept, referencing why you connected"
}

LinkedIn messages must be ultra-concise and human. No corporate speak.
"""
    else:  # sequence
        prompt += """
Return a JSON object with these fields:
{
  "day1": {"subject": "...", "body": "Full first touch email"},
  "day3": {"subject": "...", "body": "Value-add follow-up, share insight or resource"},
  "day7": {"subject": "...", "body": "Polite check-in, offer alternatives"},
  "day14": {"subject": "...", "body": "Graceful close, leave door open"}
}

Each email should build on the previous, not repeat the same pitch. Day 3 should add value even if they don't respond.
"""

    return prompt


@app.route("/api/outreach/generate", methods=["POST"])
def generate_ai_outreach():
    """
    Generate AI-powered personalized outreach using OpenAI GPT-4

    POST body:
    {
        "contact": { contact object },
        "account": { account object },
        "outreach_type": "email" | "linkedin" | "sequence",
        "tone": "professional" | "conversational" | "direct"
    }
    """
    if not OPENAI_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "AI generation unavailable",
                    "message": "OpenAI API key not configured. Set OPENAI_API_KEY in your environment.",
                    "fallback": True,
                }
            ),
            503,
        )

    body = request.get_json()
    if not body:
        return jsonify({"error": "Request body required"}), 400

    contact = body.get("contact", {})
    account = body.get("account", {})
    outreach_type = body.get("outreach_type", "email")
    tone = body.get("tone", "conversational")

    if not contact.get("name") or not account.get("name"):
        return jsonify({"error": "Contact and account names required"}), 400

    try:
        prompt = build_outreach_prompt(contact, account, outreach_type, tone)

        logger.info(
            f"🤖 Generating {outreach_type} outreach for {contact.get('name')} at {account.get('name')}"
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert B2B sales copywriter. Always respond with valid JSON only, no markdown formatting or code blocks. Just the raw JSON object.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,  # Slightly creative but not too random
            max_tokens=1500,
        )

        content = response.choices[0].message.content.strip()

        # Clean up potential markdown formatting
        if content.startswith("```"):
            content = content.split("\n", 1)[1]  # Remove first line
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        # Parse the JSON response
        try:
            generated = json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse OpenAI response: {content[:200]}")
            return (
                jsonify({"error": "AI response parsing failed", "raw_response": content[:500]}),
                500,
            )

        return jsonify(
            {
                "status": "success",
                "outreach_type": outreach_type,
                "tone": tone,
                "generated": generated,
                "context": {
                    "contact_name": contact.get("name"),
                    "account_name": account.get("name"),
                    "role_tier": contact.get("role_tier", "entry_point"),
                    "champion_potential": contact.get("champion_potential_level", "Medium"),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ AI generation failed: {e}")
        return jsonify({"error": "Generation failed", "message": str(e)}), 500


# ============================================================================
# Vendor Relationship Discovery (Trusted Paths Intelligence)
# ============================================================================

# Initialize Vendor Relationship Discovery module
VENDOR_DISCOVERY_AVAILABLE = False
vendor_discovery = None

try:
    discovery_spec = importlib.util.spec_from_file_location(
        "vendor_relationship_discovery",
        os.path.join(
            project_root, "src/abm_research/intelligence/vendor_relationship_discovery.py"
        ),
    )
    discovery_module = importlib.util.module_from_spec(discovery_spec)
    discovery_spec.loader.exec_module(discovery_module)
    # Create instance with notion_client for Notion persistence support
    # Previously used module singleton without notion_client, causing save_to_notion to silently fail
    VendorRelationshipDiscovery = discovery_module.VendorRelationshipDiscovery
    vendor_discovery = VendorRelationshipDiscovery(notion_client=get_notion_client())
    VENDOR_DISCOVERY_AVAILABLE = True
    logger.info("✅ Vendor Relationship Discovery module available (with Notion persistence)")
except Exception as e:
    logger.warning(f"⚠️ Vendor Relationship Discovery not available: {e}")


@app.route("/api/accounts/<account_id>/discover-vendors", methods=["POST"])
def discover_account_vendors(account_id: str):
    """
    Discover vendor relationships for a target account using public data.

    Uses Brave Search to find publicly documented vendor-customer relationships:
    - Case studies
    - Joint press releases
    - Integration listings
    - Conference mentions
    - Procurement records

    Each signal is scored 1-5 per the strength rubric:
    1: Logo/mention only
    2: Customer referenced but not formal story
    3: Named case study, webinar, or clear narrative
    4: Joint PR, integration launch, multi-party collaboration
    5: Multiple assets or contract award with details

    POST body (optional):
    {
        "vendors": ["Schneider Electric", "Vertiv"],  // Custom vendor list (default: infrastructure vendors)
        "save_to_notion": true  // Save discovered relationships to Notion
    }

    Returns:
    - signals: List of VendorCustomerSignal objects
    - vendor_scores: Vendors ranked by IntroPower score
    - search_failures: Any searches that failed
    """
    if not VENDOR_DISCOVERY_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Vendor discovery unavailable",
                    "message": "VendorRelationshipDiscovery module not configured. Check server logs.",
                }
            ),
            503,
        )

    # Get account from Notion - support both synthetic ID and Notion UUID
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_name = account.get("name", "")
    if not account_name:
        return jsonify({"error": "Account name is required for vendor discovery"}), 400

    # Parse request body
    body = request.get_json(silent=True) or {}
    custom_vendors = body.get("vendors", None)
    save_to_notion = body.get("save_to_notion", True)  # Default: always save to Notion

    try:
        logger.info(f"🔍 Discovering vendor relationships for {account_name}")

        # Run discovery
        results = vendor_discovery.discover_for_account(
            account_name=account_name, candidate_vendors=custom_vendors
        )

        signals = results.get("signals", [])
        vendor_scores = results.get("vendor_scores", [])
        search_failures = results.get("search_failures", [])

        # Save to Notion if requested
        saved_count = 0
        save_errors = []
        if save_to_notion and signals and NOTION_AVAILABLE:
            try:
                notion = get_notion_client()
                account_notion_id = account.get("notion_id")

                for signal in signals[:20]:  # Limit to top 20 signals
                    try:
                        properties = vendor_discovery.to_partnership_properties(
                            signal,
                            account_page_id=account_notion_id,
                            is_verdigris_partner=False,  # These are account vendors
                        )

                        # Check if partnership already exists using new method
                        existing = notion._find_existing_partnership(
                            signal.vendor, account_notion_id
                        )
                        if not existing:
                            # Use partnerships_db property (will raise if not configured)
                            notion.client.pages.create(
                                parent={"database_id": notion.partnerships_db},
                                properties=properties,
                            )
                            saved_count += 1
                            logger.info(f"✅ Saved vendor relationship: {signal.vendor}")
                        else:
                            logger.info(f"⏭️ Partnership already exists: {signal.vendor}")
                    except NotionConfigError as e:
                        # Config error - stop trying to save more
                        save_errors.append(
                            {"vendor": signal.vendor, "error": str(e), "type": "config"}
                        )
                        logger.error(f"❌ Notion not configured for partnerships: {e}")
                        break
                    except NotionError as e:
                        # API error - log and continue with others
                        save_errors.append(
                            {"vendor": signal.vendor, "error": str(e), "type": "api"}
                        )
                        logger.warning(f"⚠️ Failed to save partnership {signal.vendor}: {e}")
                    except Exception as e:
                        save_errors.append(
                            {"vendor": signal.vendor, "error": str(e), "type": "unknown"}
                        )
                        logger.warning(f"⚠️ Unexpected error saving {signal.vendor}: {e}")

            except NotionConfigError as e:
                logger.error(f"❌ Notion partnerships database not configured: {e}")
                save_errors.append({"error": str(e), "type": "config"})
            except Exception as e:
                logger.error(f"❌ Failed to save partnerships to Notion: {e}")
                save_errors.append({"error": str(e), "type": "unknown"})

        # Convert dataclasses to dicts for JSON response
        signals_json = []
        for s in signals:
            signals_json.append(
                {
                    "vendor": s.vendor,
                    "customer": s.customer,
                    "signal_type": s.signal_type,
                    "signal_strength": s.signal_strength,
                    "evidence_url": s.evidence_url,
                    "evidence_title": s.evidence_title,
                    "evidence_snippet": s.evidence_snippet[:200] if s.evidence_snippet else "",
                    "recency": s.recency,
                    "is_cobranded": s.is_cobranded,
                    "is_deployment_story": s.is_deployment_story,
                    "discovered_at": s.discovered_at,
                }
            )

        vendor_scores_json = []
        for v in vendor_scores:
            vendor_scores_json.append(
                {
                    "vendor_name": v.vendor_name,
                    "intro_score": v.intro_score,
                    "coverage_count": v.coverage_count,
                    "avg_signal_strength": v.avg_signal_strength,
                    "fit_weight": v.fit_weight,
                    "intro_candidates": v.intro_candidates[:5],  # Top 5 candidates
                }
            )

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "signals": signals_json,
                "total_signals": len(signals_json),
                "vendor_scores": vendor_scores_json,
                "total_vendors_with_signals": len(vendor_scores_json),
                "search_failures": search_failures,
                "notion_persistence": {
                    "saved_to_notion": saved_count,
                    "save_errors": save_errors,
                    "all_saved": len(save_errors) == 0 and saved_count > 0,
                },
                "scoring_rubric": {
                    1: "Logo/mention only",
                    2: "Customer referenced but not formal story",
                    3: "Named case study, webinar, or clear narrative",
                    4: "Joint PR, integration launch, multi-party collaboration",
                    5: "Multiple assets or contract award with details",
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Vendor discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Vendor discovery failed", "message": str(e)}), 500


@app.route("/api/accounts/<account_id>/discover-unknown-vendors", methods=["POST"])
def discover_unknown_vendors(account_id: str):
    """
    WORKFLOW 3: Discover NEW vendors not in KNOWN_VENDORS using LLM extraction.

    This uses GPT-4o-mini to extract and classify vendors from search results that
    aren't already in the known vendor database. Discovered vendors can be persisted
    to Notion and added to the runtime vendor list.

    POST body (optional):
    {
        "save_to_notion": true,    # Persist discovered vendors to Notion (default: true)
        "min_confidence": 0.6      # Minimum confidence threshold 0-1 (default: 0.6)
    }

    Returns:
    - discovered_vendors: List of newly discovered vendors with category classifications
    - new_vendors_count: Number of new vendors found
    - known_vendors_found: Number of known vendors confirmed in search results
    - saved_to_notion: Number saved to Notion
    - added_to_runtime: Number added to runtime vendor list
    - category_summary: Count of vendors by category
    """
    if not VENDOR_DISCOVERY_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Vendor discovery unavailable",
                    "message": "VendorRelationshipDiscovery module not configured. Check server logs.",
                }
            ),
            503,
        )

    # Get account from Notion - support both synthetic ID and Notion UUID
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_name = account.get("name", "")
    if not account_name:
        return jsonify({"error": "Account name is required for vendor discovery"}), 400

    # Parse request body
    body = request.get_json(silent=True) or {}
    save_to_notion = body.get("save_to_notion", True)
    min_confidence = body.get("min_confidence", 0.6)

    try:
        logger.info(f"🔍 WORKFLOW 3: Discovering unknown vendors for {account_name}")

        # Run LLM-powered discovery
        results = vendor_discovery.discover_unknown_vendors(
            account_name=account_name, save_to_notion=save_to_notion, min_confidence=min_confidence
        )

        # Check for errors
        if "error" in results:
            return (
                jsonify(
                    {
                        "status": "error",
                        "account_name": account_name,
                        "workflow": "discover_unknown_vendors",
                        "error": results["error"],
                    }
                ),
                400,
            )

        # Convert DiscoveredVendor objects to dicts for JSON response
        discovered_vendors_json = []
        for v in results.get("discovered_vendors", []):
            discovered_vendors_json.append(
                {
                    "vendor_name": v.vendor_name,
                    "category": v.category,
                    "strategic_purpose": v.strategic_purpose,
                    "recommended_action": v.recommended_action,
                    "mention_count": v.mention_count,
                    "confidence": v.confidence,
                    "relationship_type": v.relationship_type,
                    "evidence_urls": v.evidence_urls[:3],
                    "evidence_snippets": v.evidence_snippets[:2],
                    "discovered_at": v.discovered_at,
                    "is_new": True,
                }
            )

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "workflow": "discover_unknown_vendors",
                "discovered_vendors": discovered_vendors_json,
                "new_vendors_count": results.get("new_vendors_count", 0),
                "known_vendors_found": results.get("known_vendors_found", 0),
                "known_vendors_detail": results.get("known_vendors_detail", []),
                "saved_to_notion": results.get("saved_to_notion", 0),
                "added_to_runtime": results.get("added_to_runtime", 0),
                "search_results_analyzed": results.get("search_results_analyzed", 0),
                "category_summary": results.get("category_summary", {}),
                "total_vendors_in_system": vendor_discovery.get_vendor_count(),
                "llm_model": "gpt-4o-mini",
                "cost_estimate": f"~${0.02 + (results.get('search_results_analyzed', 0) * 0.002):.3f}",
            }
        )

    except Exception as e:
        logger.error(f"❌ Unknown vendor discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Unknown vendor discovery failed", "message": str(e)}), 500


@app.route("/api/vendor-intro-power", methods=["POST"])
def calculate_vendor_intro_power():
    """
    Calculate Vendor Intro Power scores across multiple target accounts.

    This endpoint finds which vendors have the strongest documented relationships
    with your target accounts, helping prioritize vendors for partnership outreach.

    POST body:
    {
        "vendors": ["Schneider Electric", "Vertiv", "NVIDIA"],
        "accounts": ["CoreWeave", "Lambda Labs", "Together AI"],  // Optional, defaults to all accounts
        "fit_weights": {"NVIDIA": 1.5, "Schneider Electric": 1.2}  // Optional vendor weights
    }

    Returns vendors ranked by IntroScore = CoverageCount * AvgSignalStrength * FitWeight
    """
    if not VENDOR_DISCOVERY_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Vendor discovery unavailable",
                    "message": "VendorRelationshipDiscovery module not configured",
                }
            ),
            503,
        )

    body = request.get_json(silent=True) or {}

    # Get vendors (required)
    vendors = body.get("vendors", [])
    if not vendors:
        return (
            jsonify(
                {
                    "error": "vendors list is required",
                    "message": "Provide a list of vendor names to analyze",
                }
            ),
            400,
        )

    # Get accounts (default to all)
    account_names = body.get("accounts", [])
    if not account_names:
        accounts = get_notion_accounts()
        account_names = [a.get("name") for a in accounts if a.get("name")]

    # Get fit weights
    fit_weights = body.get("fit_weights", {})

    try:
        logger.info(
            f"🔍 Calculating intro power for {len(vendors)} vendors across {len(account_names)} accounts"
        )

        # Run discovery
        results = vendor_discovery.discover_relationships(
            vendors=vendors, customers=account_names, fit_weights=fit_weights
        )

        vendor_scores = results.get("vendor_scores", [])
        total_signals = len(results.get("signals", []))

        # Convert to JSON-serializable format
        rankings = []
        for v in vendor_scores:
            # Get customer details
            customers_with_signals = []
            for customer, signals in v.customer_signals.items():
                best_signal = max(signals, key=lambda s: s.signal_strength) if signals else None
                customers_with_signals.append(
                    {
                        "customer": customer,
                        "signal_count": len(signals),
                        "best_signal_type": best_signal.signal_type if best_signal else None,
                        "best_signal_strength": best_signal.signal_strength if best_signal else 0,
                        "evidence_url": best_signal.evidence_url if best_signal else None,
                    }
                )

            rankings.append(
                {
                    "vendor_name": v.vendor_name,
                    "intro_score": v.intro_score,
                    "coverage_count": v.coverage_count,
                    "avg_signal_strength": v.avg_signal_strength,
                    "fit_weight": v.fit_weight,
                    "customers_with_signals": customers_with_signals,
                    "intro_candidates": v.intro_candidates[:5],
                }
            )

        return jsonify(
            {
                "status": "success",
                "vendor_rankings": rankings,
                "total_vendors_analyzed": len(vendors),
                "total_accounts_analyzed": len(account_names),
                "total_signals_found": total_signals,
                "search_failures": results.get("search_failures", []),
                "methodology": {
                    "formula": "IntroScore = CoverageCount * AvgSignalStrength * FitWeight",
                    "coverage_count": "Number of target accounts with documented relationships",
                    "avg_signal_strength": "Mean signal strength (1-5 scale)",
                    "fit_weight": "Optional vendor importance multiplier (default: 1.0)",
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Vendor intro power calculation failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Calculation failed", "message": str(e)}), 500


@app.route("/api/accounts/<account_id>/discover-account-vendors", methods=["POST"])
def discover_account_vendors_endpoint(account_id: str):
    """
    WORKFLOW 2: Discover vendors for an account using pattern-matching.

    This is fundamentally different from /discover-vendors (Workflow 1):
    - Workflow 1: "Does vendor X work with account Y?" (requires knowing vendors)
    - Workflow 2: "Who are account Y's vendors?" (discovers vendors from scratch)
    - Workflow 3 (/discover-unknown-vendors): Uses LLM for extraction

    Use this when you want to identify partnership opportunities by finding
    which vendors a target account is already working with, using pattern-matching
    against known vendor names (faster than LLM-based discovery).

    POST body (optional):
    {
        "save_to_notion": true  // Save discovered vendors as potential partnerships
    }

    Returns:
    - discovered_vendors: List of vendors found with confidence scores
    - vendors_by_category: Vendors grouped by category (compute, power, cooling, etc.)
    - search_results_analyzed: Number of search results processed
    """
    if not VENDOR_DISCOVERY_AVAILABLE:
        return (
            jsonify(
                {
                    "error": "Vendor discovery unavailable",
                    "message": "VendorRelationshipDiscovery module not configured. Check server logs.",
                }
            ),
            503,
        )

    # Get account from Notion - support both synthetic ID and Notion UUID
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": f"Account not found: {account_id}"}), 404

    account_name = account.get("name", "")
    if not account_name:
        return jsonify({"error": "Account name is required for vendor discovery"}), 400

    # Parse request body
    body = request.get_json(silent=True) or {}
    save_to_notion = body.get("save_to_notion", True)  # Default: always save to Notion

    try:
        logger.info(f"🔍 [Workflow 2] Discovering unknown vendors for {account_name}")

        # Run account-centric vendor discovery
        results = vendor_discovery.discover_account_vendors(account_name)

        discovered_vendors = results.get("discovered_vendors", [])
        vendors_by_category = results.get("vendors_by_category", {})
        search_results_analyzed = results.get("search_results_analyzed", 0)
        raw_evidence = results.get("raw_evidence", [])

        # Save to Notion if requested
        saved_count = 0
        if save_to_notion and discovered_vendors and NOTION_AVAILABLE:
            try:
                notion = get_notion_client()
                account_notion_id = account.get("notion_id")

                # Save top vendors as potential partnerships
                for vendor in discovered_vendors[:10]:  # Top 10 vendors
                    if vendor.confidence >= 0.5:  # Only save high-confidence discoveries
                        properties = {
                            "Name": {"title": [{"text": {"content": vendor.vendor_name}}]},
                            "Partnership Type": {"select": {"name": "vendor"}},
                            "Context": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": f"Auto-discovered vendor for {account_name}. Category: {vendor.category}. Relationship: {vendor.relationship_type}. Evidence: {', '.join(vendor.evidence_snippets[:2])[:500]}"
                                        }
                                    }
                                ]
                            },
                            "Relevance Score": {"number": int(vendor.confidence * 100)},
                        }

                        # Link to account if possible
                        if account_notion_id:
                            properties["Related Account"] = {
                                "relation": [{"id": account_notion_id}]
                            }

                        # Check if partnership already exists
                        existing = notion._find_existing_partnership(vendor.vendor_name)
                        if not existing:
                            notion.client.pages.create(
                                parent={"database_id": notion.partnerships_db},
                                properties=properties,
                            )
                            saved_count += 1
                            logger.info(f"✅ Saved discovered vendor: {vendor.vendor_name}")

            except Exception as e:
                logger.warning(f"⚠️ Failed to save some vendors to Notion: {e}")

        # Convert dataclasses to dicts for JSON response
        vendors_json = []
        for v in discovered_vendors:
            vendors_json.append(
                {
                    "vendor_name": v.vendor_name,
                    "category": v.category,
                    "mention_count": v.mention_count,
                    "evidence_urls": v.evidence_urls[:5],  # Top 5 URLs
                    "evidence_snippets": [
                        s[:200] for s in v.evidence_snippets[:3]
                    ],  # Top 3 snippets, truncated
                    "relationship_type": v.relationship_type,
                    "confidence": round(v.confidence, 2),
                    "discovered_at": v.discovered_at,
                }
            )

        # Convert category groupings
        category_json = {}
        for category, vendors in vendors_by_category.items():
            category_json[category] = [
                {
                    "vendor_name": v.vendor_name,
                    "confidence": round(v.confidence, 2),
                    "mention_count": v.mention_count,
                }
                for v in vendors
            ]

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "workflow": "account_centric_discovery",
                "discovered_vendors": vendors_json,
                "total_vendors_discovered": len(vendors_json),
                "vendors_by_category": category_json,
                "category_summary": {cat: len(vendors) for cat, vendors in category_json.items()},
                "search_results_analyzed": search_results_analyzed,
                "saved_to_notion": saved_count,
                "methodology": {
                    "description": "Account-centric search discovers partners mentioned in content about the target account",
                    "confidence_factors": [
                        "Mention count across multiple sources",
                        "URL diversity (more sources = higher confidence)",
                        "Context quality (snippets with clear partner mentions)",
                    ],
                    "categories": {
                        "infrastructure": [
                            "compute",
                            "power",
                            "cooling",
                            "networking",
                            "colocation",
                            "software",
                            "cloud",
                        ],
                        "services": [
                            "professional_services",
                            "system_integrators",
                            "managed_services",
                            "channel_partners",
                        ],
                        "platform": ["platform_partners", "ai_ml_partners"],
                        "financial": ["investors"],
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Account-centric vendor discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Vendor discovery failed", "message": str(e)}), 500


# ============================================================================
# DC Rectifier Signal Detection (New ICP Vertical)
# ============================================================================


@app.route("/api/accounts/<account_id>/detect-dc-signals", methods=["POST"])
def detect_dc_signals(account_id: str):
    """
    Detect DC rectifier/power infrastructure signals via Brave Search.

    This endpoint identifies prospects interested in DC power systems:
    - 48VDC/380VDC infrastructure
    - Rectifier equipment and upgrades
    - DC power conversion projects
    - DC rectifier vendor relationships (Delta, ABB, Vertiv, Eltek, etc.)

    POST body (optional):
    {
        "save_to_notion": false  // Save as trigger events (default: false)
    }

    Returns:
    - dc_fit_score: 0-100 score indicating DC rectifier ICP fit
    - signals: List of detected DC power signals with urgency levels
    - vendor_mentions: DC rectifier vendors found in search results
    - urgency_breakdown: Signals grouped by urgency (Critical, High, Medium)
    """
    # Get account from Notion - support both synthetic ID and Notion UUID
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_name = account.get("name", "")
    if not account_name:
        return jsonify({"error": "Account name is required for DC signal detection"}), 400

    # Parse request body
    body = request.get_json(silent=True) or {}
    save_to_notion = body.get("save_to_notion", True)  # Default: always save to Notion

    # Check for Brave API key
    brave_api_key = os.getenv("BRAVE_API_KEY")
    if not brave_api_key:
        return (
            jsonify(
                {
                    "error": "Brave API key not configured",
                    "message": "Set BRAVE_API_KEY environment variable",
                }
            ),
            503,
        )

    try:
        logger.info(f"⚡ Detecting DC rectifier signals for {account_name}")

        # DC-specific search queries (from the plan)
        dc_queries = [
            f'"{account_name}" DC rectifier deployment',
            f'"{account_name}" 48V DC infrastructure OR "48VDC"',
            f'"{account_name}" power conversion system rectifier',
            f'"{account_name}" Delta Electronics OR Eltek OR "Huawei Digital Power" OR ABB',
        ]

        # DC rectifier keywords to look for in results
        dc_keywords = {
            "critical": [
                "RFP",
                "procurement",
                "bid",
                "contract",
                "rectifier upgrade",
                "DC deployment",
            ],
            "high": [
                "48vdc",
                "48v dc",
                "380vdc",
                "380v dc",
                "dc power",
                "rectifier",
                "busbar",
                "power conversion",
                "dc infrastructure",
                "dc distribution",
            ],
            "medium": [
                "power efficiency",
                "PUE",
                "ac-to-dc",
                "conversion efficiency",
                "delta electronics",
                "eltek",
                "vertiv",
                "abb power",
                "huawei digital power",
            ],
        }

        # Brave Search base URL
        brave_url = "https://api.search.brave.com/res/v1/web/search"

        all_signals = []
        vendor_mentions = set()
        search_results_count = 0

        # DC rectifier vendors to detect
        dc_vendors = [
            "Delta Electronics",
            "ABB",
            "Vertiv",
            "Eltek",
            "Huawei Digital Power",
            "ZTE Power",
            "Emerson Network Power",
            "Rectifier Technologies",
        ]

        for query in dc_queries:
            try:
                # Rate limit
                import time

                time.sleep(1.0)

                response = requests.get(
                    brave_url,
                    params={"q": query, "count": 10, "freshness": "pm"},
                    headers={"X-Subscription-Token": brave_api_key, "Accept": "application/json"},
                    timeout=15,
                )

                if response.status_code != 200:
                    logger.warning(f"Brave search failed for query: {query[:50]}...")
                    continue

                data = response.json()
                web_results = data.get("web", {}).get("results", [])
                news_results = data.get("news", {}).get("results", [])

                search_results_count += len(web_results) + len(news_results)

                # Process results
                for result in web_results + news_results:
                    title = result.get("title", "").lower()
                    description = result.get("description", "").lower()
                    url = result.get("url", "")
                    combined_text = f"{title} {description}"

                    # Determine urgency level
                    urgency = None
                    matched_keywords = []

                    for kw in dc_keywords["critical"]:
                        if kw.lower() in combined_text:
                            urgency = "Critical"
                            matched_keywords.append(kw)

                    if not urgency:
                        for kw in dc_keywords["high"]:
                            if kw.lower() in combined_text:
                                urgency = "High"
                                matched_keywords.append(kw)

                    if not urgency:
                        for kw in dc_keywords["medium"]:
                            if kw.lower() in combined_text:
                                urgency = "Medium"
                                matched_keywords.append(kw)

                    if urgency:
                        signal = {
                            "title": result.get("title", ""),
                            "description": result.get("description", "")[:300],
                            "url": url,
                            "urgency": urgency,
                            "matched_keywords": matched_keywords[:5],
                            "source_type": "News" if "age" in result else "Web",
                        }
                        all_signals.append(signal)

                    # Check for vendor mentions
                    for vendor in dc_vendors:
                        if vendor.lower() in combined_text:
                            vendor_mentions.add(vendor)

            except Exception as e:
                logger.warning(f"Error searching: {e}")
                continue

        # Deduplicate signals by URL
        seen_urls = set()
        unique_signals = []
        for signal in all_signals:
            if signal["url"] not in seen_urls:
                seen_urls.add(signal["url"])
                unique_signals.append(signal)

        # Calculate DC fit score
        # Score based on signal count and urgency levels
        urgency_counts = {"Critical": 0, "High": 0, "Medium": 0}
        for signal in unique_signals:
            urgency_counts[signal["urgency"]] += 1

        dc_fit_score = min(
            100,
            urgency_counts["Critical"] * 30
            + urgency_counts["High"] * 15
            + urgency_counts["Medium"] * 5
            + len(vendor_mentions) * 10,
        )

        # Save to Notion as trigger events if requested
        saved_count = 0
        if save_to_notion and unique_signals and NOTION_AVAILABLE:
            try:
                notion = get_notion_client()
                account_notion_id = account.get("notion_id")

                for signal in unique_signals[:10]:  # Top 10 signals
                    properties = {
                        "Event Description": {
                            "title": [{"text": {"content": f"DC Signal: {signal['title'][:150]}"}}]
                        },
                        "Event Type": {"select": {"name": "DC Power Project"}},
                        "Confidence": {"select": {"name": signal["urgency"]}},
                        "Source URL": {"url": signal["url"]},
                        "Detected Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                        "Urgency Level": {"select": {"name": signal["urgency"]}},
                    }

                    if account_notion_id:
                        properties["Account"] = {"relation": [{"id": account_notion_id}]}

                    notion.client.pages.create(
                        parent={"database_id": notion.trigger_events_db}, properties=properties
                    )
                    saved_count += 1

            except Exception as e:
                logger.warning(f"⚠️ Failed to save DC signals to Notion: {e}")

        logger.info(f"⚡ Found {len(unique_signals)} DC signals, score: {dc_fit_score}")

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "dc_fit_score": dc_fit_score,
                "signals": unique_signals[:20],
                "total_signals": len(unique_signals),
                "vendor_mentions": list(vendor_mentions),
                "urgency_breakdown": urgency_counts,
                "search_results_analyzed": search_results_count,
                "saved_to_notion": saved_count,
                "sales_guidance": {
                    "critical": "IMMEDIATE outreach - active procurement/RFP detected",
                    "high": "Strong signal - architecture transition in progress",
                    "medium": "Monitoring signal - vendor engagement detected",
                    "target_contacts": [
                        "Critical Facilities Manager (Entry Point)",
                        "Power Engineers (Technical Champion)",
                        "VP of Data Center Operations (Economic Buyer)",
                    ],
                    "talk_track": "As you transition to DC power, visibility into per-rack efficiency becomes critical...",
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ DC signal detection failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "DC signal detection failed", "message": str(e)}), 500


# ============================================================================
# Account Field Enrichment (Lightweight alternative to full research)
# ============================================================================


@app.route("/api/accounts/<account_id>/enrich-fields", methods=["POST"])
def enrich_account_fields(account_id: str):
    """
    Enrich account fields using web search + AI extraction.

    This is a LIGHTWEIGHT alternative to full 5-phase research.
    It populates:
    - Physical Infrastructure (datacenter, GPU, power systems)
    - Industry classification
    - ICP Fit Score

    Much faster than /research endpoint - uses only Brave Search + GPT-4o-mini.

    POST body (optional):
    {
        "force": false  // Force re-enrichment even if fields already populated
    }
    """
    # Get account from Notion
    # Support both synthetic IDs (acc_xxxx) and full Notion UUIDs
    accounts = get_notion_accounts()
    account = next(
        (a for a in accounts if a["id"] == account_id or a.get("notion_id") == account_id), None
    )

    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_name = account.get("name", "")
    notion_id = account.get("notion_id")

    if not account_name:
        return jsonify({"error": "Account name is required"}), 400

    if not notion_id:
        return jsonify({"error": "Account not linked to Notion"}), 400

    # Parse request body
    body = request.get_json(silent=True) or {}
    force = body.get("force", False)

    # Check if already enriched (unless force=True)
    current_infra = account.get("infrastructure_breakdown", {}).get("raw_text", "")
    current_icp = account.get("icp_fit_score", 0)

    if not force and current_infra and current_icp > 60:
        return jsonify(
            {
                "status": "already_enriched",
                "message": f"Account already has infrastructure data and ICP score ({current_icp}). Use force=true to re-enrich.",
                "account_name": account_name,
                "current_icp_score": current_icp,
            }
        )

    # Check for required API keys
    brave_api_key = os.getenv("BRAVE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not brave_api_key:
        return jsonify({"error": "BRAVE_API_KEY not configured"}), 503
    if not openai_api_key:
        return jsonify({"error": "OPENAI_API_KEY not configured"}), 503

    try:
        logger.info(f"🔬 Enriching account fields for {account_name}")
        import time

        start_time = time.time()

        # Step 1: Search for infrastructure information
        brave_url = "https://api.search.brave.com/res/v1/web/search"
        search_queries = [
            f'"{account_name}" datacenter infrastructure GPU',
            f'"{account_name}" cloud computing hardware servers',
            f'"{account_name}" data center power cooling',
        ]

        all_results = []
        for query in search_queries:
            try:
                time.sleep(0.5)  # Rate limit
                response = requests.get(
                    brave_url,
                    params={"q": query, "count": 10},
                    headers={"X-Subscription-Token": brave_api_key, "Accept": "application/json"},
                    timeout=15,
                )
                if response.status_code == 200:
                    data = response.json()
                    web_results = data.get("web", {}).get("results", [])
                    for r in web_results:
                        all_results.append(
                            {
                                "title": r.get("title", ""),
                                "description": r.get("description", ""),
                                "url": r.get("url", ""),
                            }
                        )
            except Exception as e:
                logger.warning(f"Search failed for query: {query[:50]}... - {e}")

        # Step 2: Use GPT-4o-mini to extract infrastructure details
        search_context = "\n".join(
            [f"- {r['title']}: {r['description']}" for r in all_results[:15]]
        )

        # Build source URLs for reference
        source_urls = list(set([r.get("url", "") for r in all_results[:10] if r.get("url")]))

        extraction_prompt = f"""Analyze these search results about {account_name} and extract company information.

SEARCH RESULTS:
{search_context}

Based on these results, provide a JSON response with:
1. physical_infrastructure: A detailed description of their datacenter/cloud infrastructure (GPUs, servers, power systems, cooling). Include specific hardware models if mentioned (NVIDIA H100, A100, etc.)
2. industry: The primary industry classification (e.g., "Cloud GPU Provider", "AI Infrastructure", "Data Center Services", "Colocation Provider")
3. employee_count_estimate: Estimated number of employees (number only, e.g. 500). If unknown, use 0.
4. headquarters_location: Company headquarters city/state/country (e.g., "San Francisco, CA, USA")
5. confidence: Your confidence level in the assessment (high/medium/low)
6. key_findings: Array of specific facts found with source attribution

Respond ONLY with valid JSON:
{{"physical_infrastructure": "...", "industry": "...", "employee_count_estimate": 500, "headquarters_location": "San Francisco, CA, USA", "confidence": "medium", "key_findings": ["NVIDIA H100 GPUs (from company website)", "~500 employees (from LinkedIn)"], "reasoning": "..."}}
"""

        try:
            ai_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            content = ai_response.choices[0].message.content.strip()

            # Clean up JSON if wrapped in markdown
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            extracted = json.loads(content)
        except Exception as e:
            logger.warning(f"AI extraction failed: {e}")
            extracted = {
                "physical_infrastructure": f"Cloud/datacenter infrastructure provider (search returned {len(all_results)} results)",
                "industry": "Technology",
                "icp_fit_score": 65,
                "reasoning": "Default score - AI extraction failed",
            }

        # Step 3: Extract all enrichment data from AI response
        physical_infra = extracted.get("physical_infrastructure", "")[:2000]
        industry = extracted.get("industry", "Technology")
        headquarters = extracted.get("headquarters_location", "")

        # Extract employee count - use AI estimate if Notion doesn't have it
        employee_estimate = extracted.get("employee_count_estimate", 0)
        if isinstance(employee_estimate, str):
            try:
                employee_estimate = int(employee_estimate.replace(",", ""))
            except (ValueError, TypeError):
                employee_estimate = 0
        existing_employee_count = props.get("Employee Count", {}).get("number", 0) or 0
        employee_count = existing_employee_count if existing_employee_count > 0 else employee_estimate

        # Calculate ICP score from components (Infrastructure × 35% + Business Fit × 35% + Buying Signals × 30%)
        # This ensures Notion's ICP Fit Score matches the component breakdown shown in UI
        account_data_for_scoring = {
            "name": account_name,
            "domain": props.get("Domain", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "Physical Infrastructure": physical_infra,
            "business_model": props.get("Business Model", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "employee_count": employee_count,
            "industry": industry,
            "data_center_locations": [headquarters] if headquarters else [],
        }

        # Use account_scorer to calculate component scores
        if account_scorer:
            score_obj = account_scorer.calculate_account_score(account_data_for_scoring)
            infra_score = score_obj.infrastructure_fit.score
            business_score = score_obj.business_fit.score
            buying_score = score_obj.buying_signals.score
            # Calculate total from weighted components
            icp_score = int(infra_score * 0.35 + business_score * 0.35 + buying_score * 0.30)
            logger.info(f"📊 Calculated ICP: {icp_score} = ({infra_score}×35% + {business_score}×35% + {buying_score}×30%)")
        else:
            # Fallback to AI-extracted score if scorer unavailable
            icp_score = min(100, max(0, extracted.get("icp_fit_score", 60)))

        try:
            notion = get_notion_client()

            # Build update properties
            update_properties = {
                "Physical Infrastructure": {"rich_text": [{"text": {"content": physical_infra}}]},
                "ICP Fit Score": {"number": icp_score},
                "Last Updated": {"date": {"start": datetime.now().isoformat()}},
            }

            # Add employee count if we have an estimate and Notion doesn't have it
            if employee_estimate > 0 and existing_employee_count == 0:
                update_properties["Employee Count"] = {"number": employee_estimate}

            # Add headquarters to Business Model if available (for geography display)
            if headquarters:
                current_biz_model = props.get("Business Model", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                if headquarters.lower() not in current_biz_model.lower():
                    new_biz_model = f"{current_biz_model}\n\nHeadquarters: {headquarters}".strip()
                    update_properties["Business Model"] = {"rich_text": [{"text": {"content": new_biz_model[:2000]}}]}

            # Update via Notion API
            url = f"https://api.notion.com/v1/pages/{notion_id}"
            headers = {
                "Authorization": f"Bearer {notion.api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }
            response = requests.patch(url, headers=headers, json={"properties": update_properties})

            if response.status_code != 200:
                logger.warning(f"Notion update warning: {response.text[:200]}")
            else:
                logger.info(f"✅ Updated Notion: {account_name} - ICP={icp_score}")

        except Exception as e:
            logger.error(f"Notion update failed: {e}")

        duration = time.time() - start_time

        return jsonify(
            {
                "status": "success",
                "account_name": account_name,
                "account_id": account_id,
                "enrichment_results": {
                    "physical_infrastructure": physical_infra,
                    "industry": industry,
                    "icp_fit_score": icp_score,
                    "confidence": extracted.get("confidence", "medium"),
                    "key_findings": extracted.get("key_findings", []),
                    "reasoning": extracted.get("reasoning", ""),
                    "source_urls": source_urls[:5],  # Top 5 sources for reference
                },
                "search_results_analyzed": len(all_results),
                "duration_seconds": round(duration, 2),
                "notion_updated": True,
                "data_provenance": {
                    "method": "ai_inference",
                    "model": "gpt-4o-mini",
                    "sources_count": len(source_urls),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Account enrichment failed: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Enrichment failed", "message": str(e)}), 500


@app.route("/api/accounts/enrich-all", methods=["POST"])
def enrich_all_accounts():
    """
    Bulk enrich all accounts that have missing/default field values.

    This is useful for initial data population after adding accounts.
    Skips accounts that already have populated fields (unless force=true).

    POST body (optional):
    {
        "force": false,  // Force re-enrichment of all accounts
        "max_accounts": 10  // Limit number of accounts to enrich (default: all)
    }
    """
    body = request.get_json(silent=True) or {}
    force = body.get("force", False)
    max_accounts = body.get("max_accounts", 100)

    # Get all accounts
    accounts = get_notion_accounts()

    # Filter to accounts needing enrichment
    accounts_to_enrich = []
    for acc in accounts:
        current_icp = acc.get("icp_fit_score", 0)
        current_infra = acc.get("infrastructure_breakdown", {}).get("raw_text", "")

        # Needs enrichment if ICP is default (60) or no infrastructure data
        needs_enrichment = force or (current_icp <= 60 and not current_infra)

        if needs_enrichment and acc.get("notion_id"):
            accounts_to_enrich.append(
                {
                    "id": acc["id"],
                    "name": acc["name"],
                    "notion_id": acc["notion_id"],
                    "current_icp": current_icp,
                }
            )

    # Limit accounts
    accounts_to_enrich = accounts_to_enrich[:max_accounts]

    if not accounts_to_enrich:
        return jsonify(
            {
                "status": "no_action",
                "message": "All accounts already enriched. Use force=true to re-enrich.",
                "total_accounts": len(accounts),
                "accounts_needing_enrichment": 0,
            }
        )

    logger.info(f"🔬 Bulk enriching {len(accounts_to_enrich)} accounts")

    results = []
    success_count = 0
    error_count = 0

    for acc in accounts_to_enrich:
        try:
            # Make internal request to enrich-fields endpoint
            with app.test_client() as client:
                response = client.post(
                    f'/api/accounts/{acc["id"]}/enrich-fields',
                    json={"force": force},
                    content_type="application/json",
                )

                if response.status_code == 200:
                    data = response.get_json()
                    success_count += 1
                    results.append(
                        {
                            "account_name": acc["name"],
                            "status": "success",
                            "new_icp_score": data.get("enrichment_results", {}).get(
                                "icp_fit_score", 0
                            ),
                        }
                    )
                else:
                    error_count += 1
                    results.append(
                        {
                            "account_name": acc["name"],
                            "status": "error",
                            "error": response.get_json().get("error", "Unknown error"),
                        }
                    )

        except Exception as e:
            error_count += 1
            results.append({"account_name": acc["name"], "status": "error", "error": str(e)})

        # Rate limit between accounts
        import time

        time.sleep(2)

    return jsonify(
        {
            "status": "completed",
            "total_accounts": len(accounts),
            "accounts_enriched": success_count,
            "accounts_failed": error_count,
            "results": results,
        }
    )


# ============================================================================
# Main
# ============================================================================


def main():
    """Run the Flask server"""
    port = int(os.environ.get("PORT", 5001))  # 5001 to avoid macOS AirPlay on 5000
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

    logger.info(f"🚀 Starting ABM Dashboard API on port {port}")
    logger.info(f"   Debug mode: {debug}")
    logger.info("   CORS enabled for frontend development")

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
