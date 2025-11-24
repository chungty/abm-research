"""
Configuration settings for ABM Research System
Follows VDG monorepo patterns - loads from root .env file
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Get the root directory of the monorepo (parent of parent of config)
ROOT_DIR = Path(__file__).parent.parent.parent

def load_env():
    """Load environment variables from root .env file"""
    env_file = ROOT_DIR / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"\'')

# Load environment variables
load_env()

# API Configuration - Use correct ABM API key from .env file
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')
NOTION_TOKEN = os.getenv('NOTION_API_KEY')  # Use the API key with database access (OKR integration)
NOTION_API_KEY = os.getenv('NOTION_API_KEY')  # Consistent API key usage
LINKEDIN_SESSION_COOKIE = os.getenv('LINKEDIN_SESSION_COOKIE')

# Notion Database IDs (to be configured per deployment)
NOTION_ACCOUNTS_DB_ID = os.getenv('NOTION_ACCOUNTS_DB_ID')
NOTION_CONTACTS_DB_ID = os.getenv('NOTION_CONTACTS_DB_ID')
NOTION_TRIGGER_EVENTS_DB_ID = os.getenv('NOTION_TRIGGER_EVENTS_DB_ID')
NOTION_PARTNERSHIPS_DB_ID = os.getenv('NOTION_PARTNERSHIPS_DB_ID')

# Rate Limiting Settings
LINKEDIN_REQUEST_DELAY = float(os.getenv('LINKEDIN_REQUEST_DELAY', '2.0'))  # seconds between requests
WEB_SCRAPING_DELAY = float(os.getenv('WEB_SCRAPING_DELAY', '1.0'))  # seconds between requests
APOLLO_REQUEST_DELAY = float(os.getenv('APOLLO_REQUEST_DELAY', '0.5'))  # seconds between requests

# Research Configuration
TRIGGER_EVENT_LOOKBACK_DAYS = int(os.getenv('TRIGGER_EVENT_LOOKBACK_DAYS', '90'))
CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', '30'))  # minimum confidence for inclusion
LEAD_SCORE_THRESHOLD = int(os.getenv('LEAD_SCORE_THRESHOLD', '60'))  # threshold for Phase 3 enrichment

# File Paths
CONFIG_DIR = Path(__file__).parent
REFERENCES_DIR = CONFIG_DIR.parent / 'references'
DATA_DIR = CONFIG_DIR.parent / 'data'
TEMP_DIR = DATA_DIR / 'temp'

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def load_lead_scoring_config() -> Dict[str, Any]:
    """Load lead scoring configuration from JSON file"""
    config_file = REFERENCES_DIR / 'lead_scoring_config.json'
    if not config_file.exists():
        raise FileNotFoundError(f"Lead scoring config not found: {config_file}")

    with open(config_file, 'r') as f:
        return json.load(f)

def load_trigger_events_config() -> Dict[str, Any]:
    """Load trigger events configuration"""
    # For now, return basic config - can be expanded to JSON if needed
    return {
        'lookback_days': TRIGGER_EVENT_LOOKBACK_DAYS,
        'confidence_threshold': CONFIDENCE_THRESHOLD,
        'categories': [
            'Expansion/Consolidation',
            'Inherited Infrastructure',
            'Leadership Changes',
            'AI Workload Expansion',
            'Energy/Cost Pressure',
            'Downtime/Incidents',
            'Sustainability Mandates'
        ]
    }

def load_partnership_categories() -> Dict[str, Dict[str, Any]]:
    """Load strategic partnership categories and detection rules"""
    return {
        'DCIM': {
            'examples': ['Schneider Electric EcoStruxure', 'Sunbird DCIM', 'FNT Command', 'nlyte', 'Device42'],
            'opportunity': 'Integration potential for real-time power data',
            'priority': 'High'
        },
        'EMS': {
            'examples': ['Siemens Desigo', 'Honeywell Forge', 'Johnson Controls Metasys'],
            'opportunity': 'Data enrichment with granular circuit-level data',
            'priority': 'Medium'
        },
        'Cooling': {
            'examples': ['Vertiv', 'Schneider Electric APC', 'Stulz', 'Rittal', 'Trane'],
            'opportunity': 'Co-deployment to monitor cooling electrical performance',
            'priority': 'Medium'
        },
        'DC Equipment': {
            'examples': ['Eaton', 'APC by Schneider', 'Vertiv', 'Generac', 'Caterpillar'],
            'opportunity': 'Monitoring integration for critical equipment health',
            'priority': 'Medium'
        },
        'Racks': {
            'examples': ['Chatsworth Products', 'Legrand', 'Panduit', 'Rittal'],
            'opportunity': 'Rack-level monitoring and capacity planning',
            'priority': 'Low'
        },
        'GPUs': {
            'examples': ['NVIDIA DGX', 'AMD Instinct', 'CoreWeave', 'Lambda Labs'],
            'opportunity': 'High-density monitoring for AI workloads',
            'priority': 'High'
        },
        'Critical Facilities': {
            'examples': ['AECOM', 'Turner Construction', 'DPR Construction', 'FORTIS'],
            'opportunity': 'Design-build integration for new facilities',
            'priority': 'High'
        },
        'Professional Services': {
            'examples': ['Cx Associates', 'EYP Mission Critical', 'Stantec', 'Buro Happold'],
            'opportunity': 'Post-commissioning continuous validation',
            'priority': 'Medium'
        }
    }

# Validation
def validate_config():
    """Validate that required configuration is present"""
    required_vars = ['APOLLO_API_KEY', 'NOTION_API_KEY']
    missing = [var for var in required_vars if not globals().get(var)]

    if missing:
        print(f"WARNING: Missing required environment variables: {missing}")
        print("Please ensure these are set in the root .env file")

    # Check if lead scoring config exists
    if not (REFERENCES_DIR / 'lead_scoring_config.json').exists():
        print("WARNING: Lead scoring config file not found in references/")

if __name__ == "__main__":
    validate_config()
    print("ABM Research configuration loaded successfully")