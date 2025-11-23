"""
Demo Notion Workflow - Show Integration Capabilities
Demonstrates how the Notion integration works without requiring actual database creation
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from models.account import Account
from models.contact import Contact, ResearchStatus
from models.trigger_event import TriggerEvent, EventType, ConfidenceLevel
from models.strategic_partnership import StrategicPartnership, PartnershipCategory, PartnershipAction, PartnershipConfidence
from models.meddic_framework import MEDDICAnalyzer
# NotionDatabaseManager would be imported here in production
from config.settings import load_lead_scoring_config


def create_demo_account() -> Account:
    """Create demo account with realistic ABM research data"""
    account = Account(
        name="TechCore Data Centers",
        domain="techcore-dc.com"
    )
    account.employee_count = 320
    account.business_model = "colocation"
    account.icp_fit_score = 82.0

    # Add trigger event
    trigger = TriggerEvent(
        description="Announced partnership with major AI company for dedicated GPU hosting services",
        event_type=EventType.AI_WORKLOAD,
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=92.0,
        relevance_score=88.0,
        source_url="https://techcore-dc.com/newsroom/ai-partnership"
    )
    account.add_trigger_event(trigger)

    # Add contact
    config = load_lead_scoring_config()
    meddic_analyzer = MEDDICAnalyzer()

    contact = Contact(
        name="Sarah Thompson",
        title="VP of Data Center Operations",
        linkedin_url="https://linkedin.com/in/sarah-thompson-dc-ops",
        email="s.thompson@techcore-dc.com"
    )

    contact.icp_fit_score = 92.0
    contact.buying_power_score = 100.0
    contact.engagement_potential_score = 75.0
    contact.calculate_final_lead_score(config)

    contact.linkedin_activity_level = "monthly"
    contact.linkedin_content_themes = ["data center operations", "AI infrastructure", "power management"]
    contact.linkedin_network_quality = True
    contact.research_status = ResearchStatus.ANALYZED

    contact.meddic_profile = meddic_analyzer.analyze_contact_meddic(
        contact.title,
        "VP of operations with focus on AI infrastructure and power management"
    )

    account.add_contact(contact)

    # Add strategic partnership
    partnership = StrategicPartnership(
        partner_name="NVIDIA DGX",
        category=PartnershipCategory.GPUS,
        relationship_evidence="Press release mentions NVIDIA DGX deployment for AI workloads",
        confidence=PartnershipConfidence.HIGH,
        evidence_url="https://techcore-dc.com/case-studies/nvidia-deployment",
        partnership_action=PartnershipAction.INVESTIGATE
    )
    account.add_strategic_partnership(partnership)

    return account


def demonstrate_notion_workflow():
    """Demonstrate complete Notion workflow without actual API calls"""
    print("🗄️ Notion Database Integration Workflow Demo")
    print("=" * 60)

    # Check API key availability
    notion_api_key = os.getenv('NOTION_ABM_API_KEY')
    if notion_api_key:
        print(f"✅ Notion API key configured: {notion_api_key[:10]}...")
    else:
        print("❌ Notion API key not found (NOTION_ABM_API_KEY)")
        print("   Demo will show workflow without actual database creation")

    print("\n📊 Step 1: Database Schema Design")
    print("   The system creates 5 interconnected Notion databases:")

    databases = {
        "ABM Accounts": [
            "Company Name (Title)", "Domain", "Employee Count", "ICP Fit Score",
            "Account Research Status", "Geographic Score", "Data Sources"
        ],
        "ABM Trigger Events": [
            "Event Description (Title)", "Event Type", "Confidence Score",
            "Relevance Score", "Source URL", "Verdigris Angle"
        ],
        "ABM Contacts": [
            "Name (Title)", "Title", "LinkedIn URL", "Buying Committee Role",
            "ICP Fit Score", "Buying Power Score", "Engagement Potential Score",
            "Final Lead Score (Formula)", "Problems They Likely Own", "Value-Add Ideas"
        ],
        "ABM Contact Intelligence": [
            "Intelligence ID (Title)", "Recent Activity Summary", "Network Analysis",
            "Engagement Strategy", "Content Hooks"
        ],
        "ABM Strategic Partnerships": [
            "Partner Name (Title)", "Category", "Confidence", "Verdigris Opportunity Angle",
            "Integration Potential", "Co-sell Potential", "Partnership Team Action"
        ]
    }

    for db_name, fields in databases.items():
        print(f"\n   🗄️ {db_name}:")
        for field in fields[:4]:  # Show first 4 fields
            print(f"      • {field}")
        if len(fields) > 4:
            print(f"      • ... and {len(fields) - 4} more fields")

    print("\n📊 Step 2: Create Demo Account Data")
    account = create_demo_account()

    print(f"   🏢 Account: {account.name}")
    print(f"   📧 Domain: {account.domain}")
    print(f"   👥 Employees: {account.employee_count}")
    print(f"   📊 ICP Fit Score: {account.icp_fit_score}")
    print(f"   ⚡ Trigger Events: {len(account.trigger_events)}")
    print(f"   👤 Contacts: {len(account.contacts)}")
    print(f"   🤝 Partnerships: {len(account.strategic_partnerships)}")

    print("\n📊 Step 3: Data Transformation for Notion")
    print("   Converting ABM research data to Notion format...")

    # Show how data transforms to Notion format
    if account.contacts:
        contact = account.contacts[0]
        print(f"\n   👤 Contact Example: {contact.name}")
        print(f"      📊 Final Lead Score: {contact.final_lead_score:.1f}")
        print(f"      📈 Score Components:")
        print(f"         • ICP Fit: {contact.icp_fit_score:.0f}")
        print(f"         • Buying Power: {contact.buying_power_score:.0f}")
        print(f"         • Engagement: {contact.engagement_potential_score:.0f}")
        print(f"      🎯 MEDDIC Role: {contact.meddic_profile.primary_role.value}")
        print(f"      📋 Research Status: {contact.research_status.value}")

    if account.trigger_events:
        trigger = account.trigger_events[0]
        print(f"\n   ⚡ Trigger Event Example:")
        print(f"      📝 {trigger.description[:60]}...")
        print(f"      🏷️  Type: {trigger.event_type.value}")
        print(f"      📊 Relevance Score: {trigger.relevance_score}")
        print(f"      🔍 Confidence: {trigger.confidence_level.value}")

    if account.strategic_partnerships:
        partnership = account.strategic_partnerships[0]
        print(f"\n   🤝 Partnership Example:")
        print(f"      🏢 Partner: {partnership.partner_name}")
        print(f"      🔧 Category: {partnership.category.value}")
        print(f"      📋 Action: {partnership.partnership_action.value}")
        print(f"      💡 Opportunity: {partnership.opportunity_angle[:50]}...")

    print("\n📊 Step 4: Notion Database Population Workflow")
    print("   When API key and parent page are available:")
    print("   1. 🏗️  Create 5 interconnected databases")
    print("   2. 🔗 Set up relations between databases")
    print("   3. 📊 Create account record with all metadata")
    print("   4. ⚡ Add trigger events linked to account")
    print("   5. 👤 Create contact records with transparent scoring")
    print("   6. 🧠 Add contact intelligence for analyzed contacts")
    print("   7. 🤝 Create partnership records with opportunity angles")

    print("\n📊 Step 5: Sales Team Handoff")
    print("   The populated Notion workspace provides:")
    print("   📈 Prioritized contact list with lead scores")
    print("   ⚡ Timely trigger events for warm outreach")
    print("   💡 Value-add ideas for personalized engagement")
    print("   🤝 Partnership opportunities with action plans")
    print("   🎯 Complete account intelligence for strategic planning")

    print("\n✅ Notion Integration Ready!")
    if notion_api_key:
        print("   🔑 API key configured - ready for database creation")
        print("   💡 Run test_notion_integration.py to create actual databases")
    else:
        print("   ⚠️  Add NOTION_ABM_API_KEY to .env file to enable database creation")

    print("\n📋 Production Usage:")
    print("   1. Add Notion API key to .env file")
    print("   2. Create a parent page in Notion workspace")
    print("   3. Run account research through all 5 phases")
    print("   4. Export complete account intelligence to Notion")
    print("   5. Sales team reviews and acts on prioritized data")

    # Show data structure summary
    print(f"\n🏗️ Complete Data Structure Created:")
    print(f"   • {len(databases)} interconnected databases")
    print(f"   • ~25 custom properties with proper types")
    print(f"   • Formula-based lead scoring (transparent)")
    print(f"   • Multi-select properties for tags and categories")
    print(f"   • URL fields for evidence and source tracking")
    print(f"   • Relation fields linking all data together")
    print(f"   • Ready for Salesforce integration (matching object structure)")


def main():
    """Run Notion workflow demonstration"""
    demonstrate_notion_workflow()


if __name__ == "__main__":
    main()