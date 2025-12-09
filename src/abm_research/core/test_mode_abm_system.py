#!/usr/bin/env python3
"""
Test Mode ABM System

Extends the ComprehensiveABMSystem to support test mode operation where:
1. All research functionality works normally (API calls, data processing, enrichment)
2. NO data is written to production Notion databases
3. Test results are returned with simulated save status
4. Safe for testing with real company data without database pollution

Usage:
    # For production (normal operation):
    abm = ComprehensiveABMSystem()

    # For testing (no database writes):
    abm = TestModeABMSystem(test_mode=True)
"""

import logging
from typing import Dict, Any, List
from abm_research.core.abm_system import ComprehensiveABMSystem

logger = logging.getLogger(__name__)


class TestModeABMSystem(ComprehensiveABMSystem):
    """
    ABM System with optional test mode that prevents production database writes
    """

    def __init__(self, test_mode: bool = False):
        """
        Initialize ABM system with optional test mode

        Args:
            test_mode: If True, prevents all database writes to production
        """
        super().__init__()
        self.test_mode = test_mode

        if self.test_mode:
            logger.info("🧪 TestModeABMSystem initialized - NO production database writes")
        else:
            logger.info("🚀 TestModeABMSystem initialized - Production mode")

    def save_research_to_notion(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override save method to prevent database writes in test mode

        Args:
            research_results: Complete research results from ABM pipeline

        Returns:
            Dict containing save status (simulated in test mode, real in production)
        """
        if self.test_mode:
            logger.info("🧪 TEST MODE: Simulating Notion database saves (no actual writes)")

            # Simulate realistic save results based on research data
            account = research_results.get("account", {})
            contacts = research_results.get("contacts", [])
            trigger_events = research_results.get("trigger_events", [])
            partnerships = research_results.get("partnerships", [])

            simulated_results = {
                "account_saved": bool(account.get("name")),  # True if account has name
                "contacts_saved": len(contacts),  # Number of contacts processed
                "events_saved": len(trigger_events),  # Number of events processed
                "partnerships_saved": len(partnerships),  # Number of partnerships processed
            }

            logger.info("🧪 Simulated save results:")
            logger.info(f"   📋 Account saved: {simulated_results['account_saved']}")
            logger.info(f"   👥 Contacts saved: {simulated_results['contacts_saved']}")
            logger.info(f"   🎯 Events saved: {simulated_results['events_saved']}")
            logger.info(f"   🤝 Partnerships saved: {simulated_results['partnerships_saved']}")

            return simulated_results
        else:
            # Normal production save
            logger.info("🚀 PRODUCTION MODE: Saving to Notion databases")
            return super().save_research_to_notion(research_results)

    def conduct_complete_account_research(
        self, company_name: str, company_domain: str
    ) -> Dict[str, Any]:
        """
        Override complete research to ensure test mode is applied consistently

        Args:
            company_name: Name of company to research
            company_domain: Domain of company to research

        Returns:
            Complete research results with appropriate save status
        """
        if self.test_mode:
            logger.info(f"🧪 TEST MODE: Researching {company_name} (no database writes)")
        else:
            logger.info(f"🚀 PRODUCTION MODE: Researching {company_name} (with database saves)")

        # Run the normal research pipeline
        results = super().conduct_complete_account_research(company_name, company_domain)

        if self.test_mode:
            # Ensure test mode messaging is clear in results
            results["test_mode"] = True
            results["database_writes_prevented"] = True

        return results

    def _save_complete_research_to_notion(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal save method override - prevents accidental production writes

        This ensures that even if the base class method is called directly,
        test mode is still respected.
        """
        return self.save_research_to_notion(research_results)


# Convenience functions for easy usage
def create_production_abm() -> ComprehensiveABMSystem:
    """Create ABM system for production use (with database writes)"""
    return TestModeABMSystem(test_mode=False)


def create_test_abm() -> TestModeABMSystem:
    """Create ABM system for testing use (no database writes)"""
    return TestModeABMSystem(test_mode=True)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("🧪 Test Mode ABM System Demo")
    print("=" * 40)

    # Test mode example
    print("\n📋 Testing in TEST MODE (no database writes):")
    test_abm = create_test_abm()
    test_result = test_abm.conduct_complete_account_research("Example Test Company", "example.com")

    print(f"✅ Test mode result: {test_result.get('test_mode', False)}")
    print(f"✅ Database writes prevented: {test_result.get('database_writes_prevented', False)}")

    # Production mode example (commented out to prevent accidental production writes)
    # print("\n📋 Testing in PRODUCTION MODE (with database writes):")
    # prod_abm = create_production_abm()
    # prod_result = prod_abm.conduct_complete_account_research("Example Prod Company", "example-prod.com")
