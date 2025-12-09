"""
Main entry point for ABM Research System
Orchestrates the 5-phase research workflow for account-based marketing
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import (
    load_lead_scoring_config,
    load_partnership_categories,
    load_trigger_events_config,
    validate_config,
)
from models import Account
from models.lead_scoring import LeadScoringEngine


class ABMResearchOrchestrator:
    """Main orchestrator for ABM research workflow"""

    def __init__(self):
        """Initialize the research system"""
        # Validate configuration
        validate_config()

        # Load configuration
        self.scoring_config = load_lead_scoring_config()
        self.trigger_config = load_trigger_events_config()
        self.partnership_config = load_partnership_categories()

        # Initialize scoring engine
        self.scoring_engine = LeadScoringEngine(self.scoring_config)

        print("ABM Research System initialized successfully")

    def research_account(self, company_name: str, domain: str) -> Account:
        """Execute full 5-phase research workflow for an account"""
        print(f"\n🔍 Starting ABM research for {company_name}")

        # Initialize account
        account = Account(name=company_name, domain=domain)

        # Phase 1: Account Intelligence Baseline
        print("\n📊 Phase 1: Account Intelligence Baseline")
        account = self._phase_1_account_intelligence(account)

        # Phase 2: Contact Discovery & Segmentation
        print("\n👥 Phase 2: Contact Discovery & Segmentation")
        account = self._phase_2_contact_discovery(account)

        # Phase 3: High-Priority Contact Enrichment
        print("\n🔍 Phase 3: High-Priority Contact Enrichment")
        account = self._phase_3_contact_enrichment(account)

        # Phase 4: Engagement Intelligence
        print("\n💡 Phase 4: Engagement Intelligence")
        account = self._phase_4_engagement_intelligence(account)

        # Phase 5: Strategic Partnership Intelligence
        print("\n🤝 Phase 5: Strategic Partnership Intelligence")
        account = self._phase_5_partnership_intelligence(account)

        print(f"\n✅ Research complete for {company_name}")
        return account

    def _phase_1_account_intelligence(self, account: Account) -> Account:
        """Phase 1: Gather firmographics and trigger events"""
        print("  • Gathering company firmographics...")
        print("  • Detecting trigger events...")
        print("  • Calculating ICP fit score...")

        # TODO: Implement Phase 1 logic
        # - Apollo API company lookup
        # - Web scraping for trigger events
        # - ICP scoring

        account.research_status = account.research_status.IN_PROGRESS
        print(f"  ✓ Account baseline established (ICP: {account.icp_fit_score:.1f})")
        return account

    def _phase_2_contact_discovery(self, account: Account) -> Account:
        """Phase 2: Find and score contacts"""
        print("  • Searching contacts via Apollo API...")
        print("  • Calculating initial lead scores...")
        print("  • Segmenting into buying committee roles...")

        # TODO: Implement Phase 2 logic
        # - Apollo API contact search
        # - Initial scoring (ICP fit + buying power)
        # - Buying committee segmentation

        print(f"  ✓ Found {len(account.contacts)} contacts")
        return account

    def _phase_3_contact_enrichment(self, account: Account) -> Account:
        """Phase 3: LinkedIn enrichment for high-scoring contacts"""
        high_priority_contacts = account.get_high_priority_contacts()
        print(f"  • Enriching {len(high_priority_contacts)} high-priority contacts...")

        # TODO: Implement Phase 3 logic
        # - LinkedIn profile scraping
        # - Activity analysis
        # - Final lead score calculation

        print(f"  ✓ Enriched {len(high_priority_contacts)} contacts")
        return account

    def _phase_4_engagement_intelligence(self, account: Account) -> Account:
        """Phase 4: Generate engagement insights"""
        analyzed_contacts = [c for c in account.contacts if c.final_lead_score >= 70]
        print(f"  • Generating engagement intelligence for {len(analyzed_contacts)} contacts...")

        # TODO: Implement Phase 4 logic
        # - Problem mapping
        # - Content theme analysis
        # - Connection pathway identification
        # - Value-add idea generation

        print("  ✓ Generated engagement insights")
        return account

    def _phase_5_partnership_intelligence(self, account: Account) -> Account:
        """Phase 5: Detect strategic partnerships"""
        print("  • Scanning for vendor relationships...")
        print("  • Analyzing co-sell opportunities...")

        # TODO: Implement Phase 5 logic
        # - Web scraping for vendor mentions
        # - Partnership categorization
        # - Opportunity angle generation

        print(f"  ✓ Detected {len(account.strategic_partnerships)} partnerships")
        account.research_status = account.research_status.COMPLETE
        return account

    def generate_report(self, account: Account) -> str:
        """Generate summary report for account research"""
        report = f"""
🎯 ABM Research Report: {account.name}
{'=' * 50}

📊 Account Overview:
• Company: {account.name} ({account.domain})
• ICP Fit Score: {account.icp_fit_score:.1f}/100
• Research Status: {account.research_status.value}

👥 Contacts ({len(account.contacts)} total):
• High Priority (70+): {len([c for c in account.contacts if c.final_lead_score >= 70])}
• Medium Priority (50-69): {len([c for c in account.contacts if 50 <= c.final_lead_score < 70])}
• Low Priority (<50): {len([c for c in account.contacts if c.final_lead_score < 50])}

🚀 Trigger Events ({len(account.trigger_events)} detected):
"""
        for event in account.trigger_events[:3]:  # Show top 3
            report += f"• {event.event_type.value}: {event.description[:100]}...\n"

        report += f"""
🤝 Strategic Partnerships ({len(account.strategic_partnerships)} detected):
"""
        for partnership in account.strategic_partnerships[:3]:  # Show top 3
            report += f"• {partnership.category.value}: {partnership.partner_name}\n"

        return report


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="ABM Research System")
    parser.add_argument("--company", required=True, help="Company name to research")
    parser.add_argument("--domain", required=True, help="Company domain")
    parser.add_argument("--output", help="Output format (console|notion|json)", default="console")

    args = parser.parse_args()

    try:
        # Initialize orchestrator
        orchestrator = ABMResearchOrchestrator()

        # Execute research
        account = orchestrator.research_account(args.company, args.domain)

        # Generate and display report
        if args.output == "console":
            print(orchestrator.generate_report(account))
        elif args.output == "notion":
            # TODO: Export to Notion databases
            print("Notion export not yet implemented")
        elif args.output == "json":
            # TODO: Export to JSON
            print("JSON export not yet implemented")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
