#!/usr/bin/env python3
"""
Flask API Server for ABM Intelligence Dashboard

Serves account and contact data with full scoring breakdowns
for the React frontend.

Run: python -m src.abm_research.api.server
"""

import os
import sys
import json
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Load .env file from project root
env_file = os.path.join(project_root, '.env')
if os.path.exists(env_file):
    logger.info(f"📁 Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
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
        os.path.join(project_root, "src/abm_research/integrations/notion_client.py")
    )
    notion_module = importlib.util.module_from_spec(notion_spec)
    notion_spec.loader.exec_module(notion_module)
    NotionClient = notion_module.NotionClient
    get_notion_client = notion_module.get_notion_client

    # Load unified_lead_scorer directly
    scorer_spec = importlib.util.spec_from_file_location(
        "unified_lead_scorer",
        os.path.join(project_root, "src/abm_research/core/unified_lead_scorer.py")
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

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


# ============================================================================
# Data Layer - Real Notion Integration
# ============================================================================

def get_notion_accounts() -> List[Dict]:
    """Fetch accounts from Notion and transform for API"""
    if not NOTION_AVAILABLE:
        return get_mock_accounts()

    try:
        notion = get_notion_client()
        raw_accounts = notion.query_all_accounts()

        accounts = []
        for idx, page in enumerate(raw_accounts):
            account = transform_notion_account(page, idx)
            if account:
                accounts.append(account)

        logger.info(f"✅ Loaded {len(accounts)} accounts from Notion")
        return accounts

    except Exception as e:
        logger.error(f"❌ Error fetching from Notion: {e}")
        return get_mock_accounts()


def transform_notion_account(page: Dict, idx: int = 0) -> Optional[Dict]:
    """Transform Notion page to API account format with full scoring"""
    try:
        props = page.get('properties', {})

        # Extract title (Name field)
        name = ''
        name_prop = props.get('Name', {})
        if name_prop.get('title'):
            name = name_prop['title'][0]['text']['content'] if name_prop['title'] else ''

        # Extract text fields
        domain = extract_rich_text(props.get('Domain', {}))
        physical_infra = extract_rich_text(props.get('Physical Infrastructure', {}))
        business_model = extract_select(props.get('Business Model', {}))
        growth_stage = extract_select(props.get('Growth Stage', {}))

        # Extract number fields
        employee_count = props.get('Employee Count', {}).get('number', 0) or 0
        icp_fit_score = props.get('ICP Fit Score', {}).get('number', 0) or 0

        # Calculate account score using our scorer
        account_data = {
            'name': name,
            'domain': domain,
            'Physical Infrastructure': physical_infra,
            'business_model': business_model,
            'employee_count': employee_count,
            'industry': extract_select(props.get('Industry', {})),
            'growth_stage': growth_stage,
        }

        # PRIMARY SCORE: Use ICP Fit Score from Notion (single source of truth)
        # This score is calculated during enrichment and stored in Notion
        total_score = icp_fit_score

        # DERIVED DISPLAY: Calculate infrastructure breakdown for visual detail
        # This is derived from Physical Infrastructure field for dashboard display only
        if account_scorer:
            score_obj = account_scorer.calculate_account_score(account_data)
            infra_score = score_obj.infrastructure_fit.score
            infra_breakdown = score_obj.infrastructure_fit.to_dict()
            # Use scorer-calculated business/buying scores for breakdown display
            business_score = score_obj.business_fit.score
            buying_score = score_obj.buying_signals.score
        else:
            infra_score = 0
            business_score = 0
            buying_score = 0
            infra_breakdown = {'score': 0, 'breakdown': {}}

        # Priority level derived from total score
        if total_score >= 80:
            priority_level = "Very High"
        elif total_score >= 65:
            priority_level = "High"
        elif total_score >= 50:
            priority_level = "Medium"
        else:
            priority_level = "Low"

        # Full breakdown for dashboard (informational, not the primary score)
        score_breakdown = {
            'total_score': total_score,  # From Notion ICP Fit Score
            'infrastructure_fit': {
                'score': infra_score,
                'weight': '35%',
                'breakdown': infra_breakdown.get('breakdown', {})
            },
            'business_fit': {
                'score': business_score,
                'weight': '35%',
            },
            'buying_signals': {
                'score': buying_score,
                'weight': '30%',
            },
            'priority_level': priority_level,
            'note': 'Total score from Notion ICP Fit Score (source of truth)'
        }

        return {
            "id": f"acc_{page['id'][:8]}",
            "notion_id": page['id'],
            "name": name or f"Account {idx + 1}",
            "domain": domain,
            "employee_count": employee_count,
            "industry": account_data.get('industry', 'Technology'),
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
            "contacts_count": 0  # Will be populated by separate query
        }

    except Exception as e:
        logger.error(f"Error transforming account: {e}")
        return None


def extract_rich_text(prop: Dict) -> str:
    """Extract text from Notion rich_text property"""
    rich_text = prop.get('rich_text', [])
    if rich_text and len(rich_text) > 0:
        return rich_text[0].get('text', {}).get('content', '')
    return ''


def extract_select(prop: Dict) -> str:
    """Extract value from Notion select property"""
    select = prop.get('select')
    if select:
        return select.get('name', '')
    return ''


def get_notion_contacts(account_id: str) -> List[Dict]:
    """Fetch contacts for account from Notion"""
    # For now, return mock contacts - full implementation would query contacts DB
    # with account relation filter
    return get_mock_contacts(account_id)


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
                        "description": "GPU/AI infrastructure - TARGET ICP"
                    },
                    "target_vendors": {
                        "detected": ["schneider electric"],
                        "points": 30,
                        "max_points": 30,
                        "description": "Target vendor detected"
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu", "power distribution"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected"
                    },
                    "cooling_systems": {
                        "detected": ["liquid cooling", "immersion cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected"
                    },
                    "dcim_software": {
                        "detected": ["dcim", "nlyte"],
                        "points": 15,
                        "max_points": 15,
                        "description": "DCIM software detected"
                    }
                },
                "raw_text": "NVIDIA H100 GPU clusters, DGX systems, liquid cooling..."
            },
            "account_score_breakdown": {
                "total_score": 88.5,
                "infrastructure_fit": {
                    "score": 100.0,
                    "weight": "35%",
                    "breakdown": {}
                },
                "business_fit": {
                    "score": 92.5,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {"detected": "GPU Cloud (Target ICP)", "score": 100, "business_model": "GPU Cloud Provider"},
                        "company_size_fit": {"employee_count": 450, "size_category": "Growth", "score": 70},
                        "geographic_fit": {"us_locations": ["Texas", "Virginia"], "priority": "US Primary", "score": 100}
                    }
                },
                "buying_signals": {
                    "score": 65.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {"high_value_triggers": ["expansion", "funding"], "total_triggers": 3, "score": 75},
                        "expansion_signals": {"detected": ["new data center", "capacity expansion"], "score": 60},
                        "hiring_signals": {"detected": ["hiring GPU engineers"], "score": 50}
                    }
                },
                "priority_level": "Very High"
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 95.0,
            "icp_fit_score": 90,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 8
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
                        "description": "GPU/AI infrastructure - TARGET ICP"
                    },
                    "target_vendors": {
                        "detected": [],
                        "points": 0,
                        "max_points": 30,
                        "description": "Target vendor detected"
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected"
                    },
                    "cooling_systems": {
                        "detected": ["precision cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected"
                    },
                    "dcim_software": {
                        "detected": [],
                        "points": 0,
                        "max_points": 15,
                        "description": "DCIM software detected"
                    }
                },
                "raw_text": "NVIDIA A100 GPU clusters, precision cooling systems..."
            },
            "account_score_breakdown": {
                "total_score": 82.3,
                "infrastructure_fit": {"score": 95.0, "weight": "35%", "breakdown": {}},
                "business_fit": {
                    "score": 85.0,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {"detected": "GPU Cloud (Target ICP)", "score": 100, "business_model": "GPU Cloud Provider"},
                        "company_size_fit": {"employee_count": 200, "size_category": "Growth", "score": 50},
                        "geographic_fit": {"us_locations": ["California"], "priority": "US Primary", "score": 100}
                    }
                },
                "buying_signals": {
                    "score": 60.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {"high_value_triggers": ["product launch"], "total_triggers": 2, "score": 50},
                        "expansion_signals": {"detected": ["growing capacity"], "score": 60},
                        "hiring_signals": {"detected": [], "score": 20}
                    }
                },
                "priority_level": "Very High"
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 90.0,
            "icp_fit_score": 85,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 5
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
                        "description": "GPU/AI infrastructure - TARGET ICP"
                    },
                    "target_vendors": {
                        "detected": ["schneider electric", "eaton"],
                        "points": 30,
                        "max_points": 30,
                        "description": "Target vendor detected"
                    },
                    "power_systems": {
                        "detected": ["ups", "pdu", "power distribution"],
                        "points": 25,
                        "max_points": 25,
                        "description": "Power infrastructure detected"
                    },
                    "cooling_systems": {
                        "detected": ["crac", "precision cooling"],
                        "points": 20,
                        "max_points": 20,
                        "description": "Cooling infrastructure detected"
                    },
                    "dcim_software": {
                        "detected": ["dcim"],
                        "points": 15,
                        "max_points": 15,
                        "description": "DCIM software detected"
                    }
                },
                "raw_text": "Enterprise data center infrastructure, Schneider Electric UPS..."
            },
            "account_score_breakdown": {
                "total_score": 71.5,
                "infrastructure_fit": {"score": 65.0, "weight": "35%", "breakdown": {}},
                "business_fit": {
                    "score": 90.0,
                    "weight": "35%",
                    "breakdown": {
                        "industry_fit": {"detected": "Colocation Provider", "score": 90, "business_model": "Colocation Provider"},
                        "company_size_fit": {"employee_count": 12000, "size_category": "Enterprise", "score": 100},
                        "geographic_fit": {"us_locations": ["Multiple"], "priority": "US Primary", "score": 100}
                    }
                },
                "buying_signals": {
                    "score": 55.0,
                    "weight": "30%",
                    "breakdown": {
                        "trigger_events": {"high_value_triggers": [], "total_triggers": 1, "score": 30},
                        "expansion_signals": {"detected": ["new facility"], "score": 60},
                        "hiring_signals": {"detected": ["hiring facilities"], "score": 50}
                    }
                },
                "priority_level": "High"
            },
            "partnership_classification": "Direct ICP",
            "classification_confidence": 85.0,
            "icp_fit_score": 80,
            "last_updated": datetime.now().isoformat(),
            "contacts_count": 12
        }
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
                    "Very high champion potential - prioritize for first outreach"
                ],
                "meddic_score_breakdown": {
                    "total_score": 85.2,
                    "champion_potential": {"score": 92.0, "weight": "45%", "level": "Very High"},
                    "role_fit": {"score": 95.0, "weight": "30%", "tier": "entry_point", "classification": "Critical Facilities Engineers"},
                    "engagement_potential": {"score": 60.0, "weight": "25%"}
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "high",
                "account_id": "acc_001"
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
                    "Engage via champion referral with business case"
                ],
                "meddic_score_breakdown": {
                    "total_score": 42.5,
                    "champion_potential": {"score": 30.0, "weight": "45%", "level": "Low"},
                    "role_fit": {"score": 65.0, "weight": "30%", "tier": "economic_buyer", "classification": "VP, Infrastructure & Data Centers"},
                    "engagement_potential": {"score": 40.0, "weight": "25%"}
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "medium",
                "account_id": "acc_001"
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
                    "Can validate need and drive tooling selection"
                ],
                "meddic_score_breakdown": {
                    "total_score": 62.8,
                    "champion_potential": {"score": 65.0, "weight": "45%", "level": "Medium"},
                    "role_fit": {"score": 80.0, "weight": "30%", "tier": "middle_decider", "classification": "Director, Data Center Operations"},
                    "engagement_potential": {"score": 55.0, "weight": "25%"}
                },
                "enrichment_status": "enriched",
                "linkedin_activity_level": "high",
                "account_id": "acc_001"
            }
        ]
    }

    return contact_templates.get(account_id, [])


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/accounts', methods=['GET'])
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
    search = request.args.get('search', '').lower()
    if search:
        accounts = [a for a in accounts if search in a['name'].lower() or search in a['domain'].lower()]

    # GPU filter
    gpu_only = request.args.get('gpu_only', '').lower() == 'true'
    if gpu_only:
        accounts = [
            a for a in accounts
            if a.get('infrastructure_breakdown', {}).get('breakdown', {}).get('gpu_infrastructure', {}).get('detected', [])
        ]

    # Priority filter
    priority_filter = request.args.get('priority', '')
    if priority_filter:
        priorities = [p.strip() for p in priority_filter.split(',')]
        accounts = [a for a in accounts if a.get('account_priority_level') in priorities]

    # Sorting
    sort_by = request.args.get('sort_by', 'account_score')
    sort_dir = request.args.get('sort_dir', 'desc')
    reverse = sort_dir == 'desc'

    if sort_by in ['account_score', 'infrastructure_score', 'business_fit_score']:
        accounts.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == 'name':
        accounts.sort(key=lambda x: x.get('name', '').lower(), reverse=reverse)
    elif sort_by == 'contacts_count':
        accounts.sort(key=lambda x: x.get('contacts_count', 0), reverse=reverse)

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    start = (page - 1) * per_page
    end = start + per_page
    paginated = accounts[start:end]

    return jsonify({
        "accounts": paginated,
        "total": len(accounts),
        "page": page,
        "per_page": per_page
    })


@app.route('/api/accounts/<account_id>', methods=['GET'])
def get_account(account_id: str):
    """Get single account with contacts"""
    accounts = get_notion_accounts()
    account = next((a for a in accounts if a['id'] == account_id), None)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    contacts = get_mock_contacts(account_id)

    return jsonify({
        "account": account,
        "contacts": contacts,
        "trigger_events": []
    })


@app.route('/api/accounts/<account_id>/contacts', methods=['GET'])
def get_account_contacts(account_id: str):
    """Get contacts for a specific account"""
    contacts = get_mock_contacts(account_id)
    return jsonify({"contacts": contacts})


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the Flask server"""
    port = int(os.environ.get('PORT', 5001))  # 5001 to avoid macOS AirPlay on 5000
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'

    logger.info(f"🚀 Starting ABM Dashboard API on port {port}")
    logger.info(f"   Debug mode: {debug}")
    logger.info(f"   CORS enabled for frontend development")

    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
