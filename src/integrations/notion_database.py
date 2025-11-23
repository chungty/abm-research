"""
Notion Database Integration for ABM Research System

Creates and manages Notion databases for ABM research data according to the
specification in SKILL.md
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import date, datetime

from notion_client import Client
from ..models.account import Account
from ..models.contact import Contact, ResearchStatus
from ..models.trigger_event import TriggerEvent, EventType, ConfidenceLevel
from ..models.strategic_partnership import StrategicPartnership, PartnershipCategory, PartnershipAction
from ..utils.data_classification import DataClassification

logger = logging.getLogger(__name__)


class NotionDatabaseManager:
    """Manages Notion databases for ABM research data"""

    def __init__(self, notion_api_key: Optional[str] = None):
        """Initialize Notion client"""
        self.api_key = notion_api_key or os.getenv('NOTION_ABM_API_KEY')
        if not self.api_key:
            raise ValueError("Notion API key not found in environment variables or parameters")

        self.client = Client(auth=self.api_key)
        self.data_classification = DataClassification()

        # Database IDs will be stored here after creation
        self.database_ids = {
            'accounts': None,
            'trigger_events': None,
            'contacts': None,
            'contact_intelligence': None,
            'strategic_partnerships': None
        }

    async def setup_abm_workspace(self, parent_page_id: str) -> Dict[str, str]:
        """
        Create complete ABM research workspace with all databases

        Args:
            parent_page_id: Notion page ID where databases should be created

        Returns:
            Dictionary mapping database names to their IDs
        """
        logger.info("🏗️ Setting up ABM Research workspace in Notion...")

        try:
            # Create all required databases
            databases = {}

            # 1. Create Accounts database (primary)
            accounts_db = await self._create_accounts_database(parent_page_id)
            databases['accounts'] = accounts_db['id']
            self.database_ids['accounts'] = accounts_db['id']

            # 2. Create Trigger Events database
            events_db = await self._create_trigger_events_database(parent_page_id)
            databases['trigger_events'] = events_db['id']
            self.database_ids['trigger_events'] = events_db['id']

            # 3. Create Contacts database
            contacts_db = await self._create_contacts_database(parent_page_id)
            databases['contacts'] = contacts_db['id']
            self.database_ids['contacts'] = contacts_db['id']

            # 4. Create Contact Intelligence database
            intelligence_db = await self._create_contact_intelligence_database(parent_page_id)
            databases['contact_intelligence'] = intelligence_db['id']
            self.database_ids['contact_intelligence'] = intelligence_db['id']

            # 5. Create Strategic Partnerships database
            partnerships_db = await self._create_partnerships_database(parent_page_id)
            databases['strategic_partnerships'] = partnerships_db['id']
            self.database_ids['strategic_partnerships'] = partnerships_db['id']

            logger.info(f"✅ ABM workspace created successfully with {len(databases)} databases")
            return databases

        except Exception as e:
            logger.error(f"❌ Failed to create ABM workspace: {str(e)}")
            raise

    async def _create_accounts_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Accounts database"""
        logger.info("📊 Creating Accounts database...")

        properties = {
            "Company Name": {"title": {}},
            "Domain": {"rich_text": {}},
            "Employee Count": {"number": {"format": "number"}},
            "Business Model": {
                "select": {
                    "options": [
                        {"name": "Cloud Provider", "color": "blue"},
                        {"name": "Colocation", "color": "green"},
                        {"name": "Hyperscaler", "color": "purple"},
                        {"name": "AI-focused DC", "color": "orange"},
                        {"name": "Energy-intensive", "color": "red"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "ICP Fit Score": {
                "number": {
                    "format": "number"
                }
            },
            "Geographic Score": {
                "number": {
                    "format": "number"
                }
            },
            "Account Research Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Complete", "color": "green"}
                    ]
                }
            },
            "Last Updated": {"date": {}},
            "Data Sources": {
                "multi_select": {
                    "options": [
                        {"name": "Apollo API", "color": "blue"},
                        {"name": "Web Research", "color": "green"},
                        {"name": "LinkedIn", "color": "purple"},
                        {"name": "Mock Data", "color": "red"}
                    ]
                }
            },
            "Created At": {"created_time": {}},
            "Trigger Events": {"relation": {"database_id": ""}},  # Will update after creation
            "Contacts": {"relation": {"database_id": ""}},        # Will update after creation
            "Strategic Partnerships": {"relation": {"database_id": ""}}  # Will update after creation
        }

        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "ABM Accounts"}}],
            properties=properties
        )

        return database

    async def _create_trigger_events_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Trigger Events database"""
        logger.info("⚡ Creating Trigger Events database...")

        properties = {
            "Event Description": {"title": {}},
            "Account": {"relation": {"database_id": self.database_ids['accounts']}},
            "Event Type": {
                "select": {
                    "options": [
                        {"name": "Expansion", "color": "green"},
                        {"name": "Inherited Infrastructure", "color": "orange"},
                        {"name": "Leadership Change", "color": "blue"},
                        {"name": "AI Workload", "color": "purple"},
                        {"name": "Energy Pressure", "color": "red"},
                        {"name": "Downtime/Incident", "color": "pink"},
                        {"name": "Sustainability", "color": "yellow"}
                    ]
                }
            },
            "Confidence": {
                "select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"}
                    ]
                }
            },
            "Confidence Score": {"number": {"format": "number"}},
            "Relevance Score": {"number": {"format": "number"}},
            "Detected Date": {"date": {}},
            "Event Date": {"date": {}},
            "Source URL": {"url": {}},
            "Verdigris Angle": {"rich_text": {}},
            "Created At": {"created_time": {}}
        }

        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "ABM Trigger Events"}}],
            properties=properties
        )

        return database

    async def _create_contacts_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Contacts database with transparent lead scoring"""
        logger.info("👤 Creating Contacts database...")

        # ICP pain points for multi-select
        icp_pain_points = [
            "Power capacity planning and management",
            "Uptime and reliability pressure",
            "Energy efficiency and PUE optimization",
            "AI workload expansion challenges",
            "Cost reduction mandates",
            "Sustainability and ESG reporting requirements",
            "Predictive maintenance and risk detection",
            "Remote monitoring and troubleshooting"
        ]

        content_themes = [
            "AI infrastructure",
            "Power optimization",
            "Data center operations",
            "Sustainability",
            "Energy efficiency",
            "Reliability engineering",
            "Cost reduction",
            "GPU computing",
            "Machine learning",
            "System optimization"
        ]

        properties = {
            "Name": {"title": {}},
            "Account": {"relation": {"database_id": self.database_ids['accounts']}},
            "Title": {"rich_text": {}},
            "LinkedIn URL": {"url": {}},
            "Email": {"email": {}},
            "Buying Committee Role": {
                "select": {
                    "options": [
                        {"name": "Economic Buyer", "color": "green"},
                        {"name": "Technical Evaluator", "color": "blue"},
                        {"name": "Champion", "color": "purple"},
                        {"name": "Influencer", "color": "yellow"}
                    ]
                }
            },
            # Transparent lead scoring components
            "ICP Fit Score": {"number": {"format": "number"}},
            "Buying Power Score": {"number": {"format": "number"}},
            "Engagement Potential Score": {"number": {"format": "number"}},
            "Final Lead Score": {
                "formula": {
                    "expression": "round(prop(\"ICP Fit Score\") * 0.4 + prop(\"Buying Power Score\") * 0.3 + prop(\"Engagement Potential Score\") * 0.3)"
                }
            },
            "Research Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "Enriched", "color": "yellow"},
                        {"name": "Analyzed", "color": "green"}
                    ]
                }
            },
            "Role Tenure": {"rich_text": {}},
            "Problems They Likely Own": {
                "multi_select": {
                    "options": [{"name": pain, "color": "blue"} for pain in icp_pain_points]
                }
            },
            "Content Themes They Value": {
                "multi_select": {
                    "options": [{"name": theme, "color": "purple"} for theme in content_themes]
                }
            },
            "Connection Pathways": {"rich_text": {}},
            "Value-Add Ideas": {"rich_text": {}},
            "LinkedIn Activity Level": {
                "select": {
                    "options": [
                        {"name": "Weekly+", "color": "green"},
                        {"name": "Monthly", "color": "yellow"},
                        {"name": "Quarterly", "color": "orange"},
                        {"name": "Inactive", "color": "red"}
                    ]
                }
            },
            "Network Quality": {
                "select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Standard", "color": "yellow"},
                        {"name": "Limited", "color": "red"}
                    ]
                }
            },
            "MEDDIC Role": {"rich_text": {}},
            "Decision Influence": {"number": {"format": "percent"}},
            "Champion Potential": {"number": {"format": "percent"}},
            "Data Sources": {
                "multi_select": {
                    "options": [
                        {"name": "Apollo API", "color": "blue"},
                        {"name": "LinkedIn Enrichment", "color": "purple"},
                        {"name": "Mock Data", "color": "red"}
                    ]
                }
            },
            "Created At": {"created_time": {}},
            "Contact Intelligence": {"relation": {"database_id": ""}}  # Will update after creation
        }

        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "ABM Contacts"}}],
            properties=properties
        )

        return database

    async def _create_contact_intelligence_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Contact Intelligence database for detailed notes"""
        logger.info("🧠 Creating Contact Intelligence database...")

        properties = {
            "Intelligence ID": {"title": {}},
            "Contact": {"relation": {"database_id": self.database_ids['contacts']}},
            "Recent Activity Summary": {"rich_text": {}},
            "Network Analysis": {"rich_text": {}},
            "Engagement Strategy": {"rich_text": {}},
            "Content Hooks": {"rich_text": {}},
            "Mutual Connections": {"number": {"format": "number"}},
            "Shared Groups": {"multi_select": {"options": []}},
            "Last Analysis Date": {"date": {}},
            "Created At": {"created_time": {}}
        }

        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "ABM Contact Intelligence"}}],
            properties=properties
        )

        return database

    async def _create_partnerships_database(self, parent_page_id: str) -> Dict[str, Any]:
        """Create Strategic Partnerships database"""
        logger.info("🤝 Creating Strategic Partnerships database...")

        properties = {
            "Partner Name": {"title": {}},
            "Account": {"relation": {"database_id": self.database_ids['accounts']}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "DCIM", "color": "blue"},
                        {"name": "EMS", "color": "green"},
                        {"name": "Cooling", "color": "purple"},
                        {"name": "DC Equipment", "color": "orange"},
                        {"name": "Racks", "color": "yellow"},
                        {"name": "GPUs", "color": "red"},
                        {"name": "Critical Facilities", "color": "brown"},
                        {"name": "Professional Services", "color": "gray"}
                    ]
                }
            },
            "Relationship Evidence": {"rich_text": {}},
            "Evidence URL": {"url": {}},
            "Detected Date": {"date": {}},
            "Confidence": {
                "select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"}
                    ]
                }
            },
            "Confidence Score": {"number": {"format": "number"}},
            "Verdigris Opportunity Angle": {"rich_text": {}},
            "Integration Potential": {
                "select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"}
                    ]
                }
            },
            "Co-sell Potential": {
                "select": {
                    "options": [
                        {"name": "Excellent", "color": "green"},
                        {"name": "Good", "color": "blue"},
                        {"name": "Fair", "color": "yellow"},
                        {"name": "Limited", "color": "red"}
                    ]
                }
            },
            "Partnership Team Action": {
                "select": {
                    "options": [
                        {"name": "Investigate", "color": "red"},
                        {"name": "Contact", "color": "orange"},
                        {"name": "Monitor", "color": "yellow"},
                        {"name": "Not Relevant", "color": "gray"}
                    ]
                }
            },
            "Priority Score": {"number": {"format": "number"}},
            "Created At": {"created_time": {}}
        }

        database = self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "ABM Strategic Partnerships"}}],
            properties=properties
        )

        return database

    async def update_database_relations(self):
        """Update database relations after all databases are created"""
        logger.info("🔗 Updating database relations...")

        try:
            # Update Accounts database with relations
            if self.database_ids['accounts']:
                self.client.databases.update(
                    database_id=self.database_ids['accounts'],
                    properties={
                        "Trigger Events": {"relation": {"database_id": self.database_ids['trigger_events']}},
                        "Contacts": {"relation": {"database_id": self.database_ids['contacts']}},
                        "Strategic Partnerships": {"relation": {"database_id": self.database_ids['strategic_partnerships']}}
                    }
                )

            # Update Contacts database with Contact Intelligence relation
            if self.database_ids['contacts']:
                self.client.databases.update(
                    database_id=self.database_ids['contacts'],
                    properties={
                        "Contact Intelligence": {"relation": {"database_id": self.database_ids['contact_intelligence']}}
                    }
                )

            logger.info("✅ Database relations updated successfully")

        except Exception as e:
            logger.warning(f"⚠️ Some database relations may not have updated: {str(e)}")

    async def populate_account_data(self, account: Account) -> str:
        """
        Populate Notion databases with complete account research data

        Args:
            account: Account object with all research data

        Returns:
            Account page ID in Notion
        """
        logger.info(f"📝 Populating Notion databases for {account.name}...")

        try:
            # 1. Create account record
            account_page_id = await self._create_account_record(account)

            # 2. Create trigger events
            for trigger_event in account.trigger_events:
                await self._create_trigger_event_record(trigger_event, account_page_id)

            # 3. Create contacts and intelligence
            for contact in account.contacts:
                contact_page_id = await self._create_contact_record(contact, account_page_id)

                # Create contact intelligence if contact is analyzed
                if contact.research_status == ResearchStatus.ANALYZED:
                    await self._create_contact_intelligence_record(contact, contact_page_id)

            # 4. Create strategic partnerships
            for partnership in account.strategic_partnerships:
                await self._create_partnership_record(partnership, account_page_id)

            logger.info(f"✅ Successfully populated Notion databases for {account.name}")
            return account_page_id

        except Exception as e:
            logger.error(f"❌ Failed to populate account data: {str(e)}")
            raise

    async def _create_account_record(self, account: Account) -> str:
        """Create account record in Notion"""

        # Determine data sources
        data_sources = []
        if hasattr(account, 'data_sources'):
            data_sources = [{"name": source} for source in account.data_sources]
        else:
            data_sources = [{"name": "Mock Data"}]  # Default for testing

        properties = {
            "Company Name": {
                "title": [{"text": {"content": account.name}}]
            },
            "Domain": {
                "rich_text": [{"text": {"content": account.domain or ""}}]
            },
            "Employee Count": {
                "number": account.employee_count or 0
            },
            "Business Model": {
                "select": {"name": account.business_model.title() if account.business_model else "Other"}
            },
            "ICP Fit Score": {
                "number": account.icp_fit_score or 0
            },
            "Geographic Score": {
                "number": getattr(account, 'geographic_score', 0)
            },
            "Account Research Status": {
                "select": {"name": "Complete"}  # Assuming complete if we're populating
            },
            "Last Updated": {
                "date": {"start": date.today().isoformat()}
            },
            "Data Sources": {
                "multi_select": data_sources
            }
        }

        response = self.client.pages.create(
            parent={"database_id": self.database_ids['accounts']},
            properties=properties
        )

        return response['id']

    async def _create_trigger_event_record(self, trigger_event: TriggerEvent, account_page_id: str):
        """Create trigger event record"""

        properties = {
            "Event Description": {
                "title": [{"text": {"content": trigger_event.description}}]
            },
            "Account": {
                "relation": [{"id": account_page_id}]
            },
            "Event Type": {
                "select": {"name": trigger_event.event_type.value}
            },
            "Confidence": {
                "select": {"name": trigger_event.confidence_level.value}
            },
            "Confidence Score": {
                "number": trigger_event.confidence_score
            },
            "Relevance Score": {
                "number": trigger_event.relevance_score
            },
            "Detected Date": {
                "date": {"start": trigger_event.detected_date.isoformat()}
            },
            "Source URL": {
                "url": trigger_event.source_url
            } if trigger_event.source_url else None,
            "Verdigris Angle": {
                "rich_text": [{"text": {"content": trigger_event.get_verdigris_angle()}}]
            }
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        self.client.pages.create(
            parent={"database_id": self.database_ids['trigger_events']},
            properties=properties
        )

    async def _create_contact_record(self, contact: Contact, account_page_id: str) -> str:
        """Create contact record"""

        # Convert problems and content themes to multi-select format
        problems_multiselect = []
        if hasattr(contact, 'likely_problems') and contact.likely_problems:
            problems_multiselect = [{"name": problem} for problem in contact.likely_problems]

        themes_multiselect = []
        if hasattr(contact, 'content_themes') and contact.content_themes:
            themes_multiselect = [{"name": theme} for theme in contact.content_themes]
        elif hasattr(contact, 'linkedin_content_themes') and contact.linkedin_content_themes:
            themes_multiselect = [{"name": theme} for theme in contact.linkedin_content_themes]

        # Data sources
        data_sources = [{"name": "Mock Data"}]  # Default for testing
        if hasattr(contact, 'data_sources'):
            data_sources = [{"name": source} for source in contact.data_sources]

        properties = {
            "Name": {
                "title": [{"text": {"content": contact.name}}]
            },
            "Account": {
                "relation": [{"id": account_page_id}]
            },
            "Title": {
                "rich_text": [{"text": {"content": contact.title}}]
            },
            "LinkedIn URL": {
                "url": contact.linkedin_url
            } if contact.linkedin_url else None,
            "Email": {
                "email": contact.email
            } if contact.email else None,
            "Buying Committee Role": {
                "select": {"name": contact.meddic_profile.primary_role.value if contact.meddic_profile else "Champion"}
            },
            "ICP Fit Score": {
                "number": contact.icp_fit_score or 0
            },
            "Buying Power Score": {
                "number": contact.buying_power_score or 0
            },
            "Engagement Potential Score": {
                "number": contact.engagement_potential_score or 0
            },
            "Research Status": {
                "select": {"name": contact.research_status.value if contact.research_status else "Not Started"}
            },
            "Role Tenure": {
                "rich_text": [{"text": {"content": contact.role_tenure or ""}}]
            },
            "Problems They Likely Own": {
                "multi_select": problems_multiselect
            },
            "Content Themes They Value": {
                "multi_select": themes_multiselect
            },
            "Connection Pathways": {
                "rich_text": [{"text": {"content": getattr(contact, 'connection_pathways', 'Not analyzed')}}]
            },
            "Value-Add Ideas": {
                "rich_text": [{"text": {"content": getattr(contact, 'value_add_ideas', 'Not generated')}}]
            },
            "LinkedIn Activity Level": {
                "select": {"name": getattr(contact, 'linkedin_activity_level', 'Unknown').title()}
            } if hasattr(contact, 'linkedin_activity_level') else None,
            "Network Quality": {
                "select": {"name": "High" if getattr(contact, 'linkedin_network_quality', False) else "Standard"}
            },
            "MEDDIC Role": {
                "rich_text": [{"text": {"content": contact.meddic_profile.primary_role.value if contact.meddic_profile else "Not analyzed"}}]
            },
            "Decision Influence": {
                "number": (contact.meddic_profile.decision_influence / 100) if contact.meddic_profile else 0
            },
            "Champion Potential": {
                "number": (contact.meddic_profile.champion_potential / 100) if contact.meddic_profile else 0
            },
            "Data Sources": {
                "multi_select": data_sources
            }
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        response = self.client.pages.create(
            parent={"database_id": self.database_ids['contacts']},
            properties=properties
        )

        return response['id']

    async def _create_contact_intelligence_record(self, contact: Contact, contact_page_id: str):
        """Create contact intelligence record for analyzed contacts"""

        properties = {
            "Intelligence ID": {
                "title": [{"text": {"content": f"{contact.name} - Intelligence Analysis"}}]
            },
            "Contact": {
                "relation": [{"id": contact_page_id}]
            },
            "Recent Activity Summary": {
                "rich_text": [{"text": {"content": getattr(contact, 'recent_activity_summary', 'Mock LinkedIn activity analysis - weekly posts about infrastructure optimization')}}]
            },
            "Network Analysis": {
                "rich_text": [{"text": {"content": getattr(contact, 'network_analysis', 'Quality LinkedIn network with industry connections')}}]
            },
            "Engagement Strategy": {
                "rich_text": [{"text": {"content": getattr(contact, 'engagement_strategy', 'LinkedIn social selling approach with technical content focus')}}]
            },
            "Content Hooks": {
                "rich_text": [{"text": {"content": getattr(contact, 'content_hooks', 'Recent posts about power efficiency and AI infrastructure challenges')}}]
            },
            "Mutual Connections": {
                "number": getattr(contact, 'mutual_connections', 5)  # Mock data
            },
            "Last Analysis Date": {
                "date": {"start": date.today().isoformat()}
            }
        }

        self.client.pages.create(
            parent={"database_id": self.database_ids['contact_intelligence']},
            properties=properties
        )

    async def _create_partnership_record(self, partnership: StrategicPartnership, account_page_id: str):
        """Create strategic partnership record"""

        # Determine integration and co-sell potential
        integration_potential = "High" if partnership.category in [PartnershipCategory.DCIM, PartnershipCategory.GPUS, PartnershipCategory.DC_EQUIPMENT] else "Medium"
        cosell_potential = "Excellent" if partnership.category in [PartnershipCategory.DCIM, PartnershipCategory.GPUS, PartnershipCategory.DC_EQUIPMENT] else "Good"

        properties = {
            "Partner Name": {
                "title": [{"text": {"content": partnership.partner_name}}]
            },
            "Account": {
                "relation": [{"id": account_page_id}]
            },
            "Category": {
                "select": {"name": partnership.category.value}
            },
            "Relationship Evidence": {
                "rich_text": [{"text": {"content": partnership.relationship_evidence}}]
            },
            "Evidence URL": {
                "url": partnership.evidence_url
            } if partnership.evidence_url else None,
            "Detected Date": {
                "date": {"start": partnership.detected_date.isoformat()}
            },
            "Confidence": {
                "select": {"name": partnership.confidence.value}
            },
            "Confidence Score": {
                "number": getattr(partnership, 'confidence_score', 70.0)
            },
            "Verdigris Opportunity Angle": {
                "rich_text": [{"text": {"content": partnership.opportunity_angle}}]
            },
            "Integration Potential": {
                "select": {"name": integration_potential}
            },
            "Co-sell Potential": {
                "select": {"name": cosell_potential}
            },
            "Partnership Team Action": {
                "select": {"name": partnership.partnership_action.value}
            },
            "Priority Score": {
                "number": partnership.get_priority_score()
            }
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        self.client.pages.create(
            parent={"database_id": self.database_ids['strategic_partnerships']},
            properties=properties
        )

    def get_database_urls(self) -> Dict[str, str]:
        """Get URLs for created databases"""
        urls = {}
        for db_name, db_id in self.database_ids.items():
            if db_id:
                urls[db_name] = f"https://www.notion.so/{db_id.replace('-', '')}"
        return urls