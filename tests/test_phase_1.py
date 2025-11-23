"""
Test Phase 1: Account Intelligence Baseline
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models import Account
from src.models.trigger_event import TriggerEvent, EventType
from src.phases.phase_1_account_intelligence import AccountIntelligencePhase
from src.data_sources.apollo_client import ApolloClient
from src.data_sources.web_scraper import WebScraper
from config.settings import APOLLO_API_KEY


async def test_phase_1_mock():
    """Test Phase 1 with mock data (no API calls)"""
    print("🧪 Testing Phase 1 with Mock Data")

    # Create test account
    account = Account(
        name="Genesis Cloud",
        domain="genesiscloud.com"
    )

    print(f"📊 Initial Account: {account.name}")
    print(f"   ICP Fit Score: {account.icp_fit_score}")
    print(f"   Business Model: {account.business_model}")

    # Simulate adding firmographics
    account.employee_count = 150
    account.business_model = 'cloud'

    # Simulate adding trigger events
    ai_event = TriggerEvent.from_detection(
        description="Genesis Cloud announces new GPU infrastructure for AI workloads",
        event_type=EventType.AI_WORKLOAD,
        source_url="https://genesiscloud.com/news/ai-infrastructure"
    )

    expansion_event = TriggerEvent.from_detection(
        description="Company expands data center capacity in Europe",
        event_type=EventType.EXPANSION,
        source_url="https://genesiscloud.com/news/expansion"
    )

    account.add_trigger_event(ai_event)
    account.add_trigger_event(expansion_event)

    print(f"\n🎯 After Adding Trigger Events:")
    print(f"   ICP Fit Score: {account.icp_fit_score}")
    print(f"   Trigger Events: {len(account.trigger_events)}")

    for event in account.trigger_events:
        print(f"   • {event.event_type.value}: Relevance {event.relevance_score:.0f}, Confidence {event.confidence_score:.0f}")

    return account


async def test_apollo_connection():
    """Test Apollo API connection (requires valid API key)"""
    if not APOLLO_API_KEY:
        print("⚠️  No Apollo API key found - skipping Apollo test")
        return False

    print("\n🔗 Testing Apollo API Connection")

    try:
        async with ApolloClient(APOLLO_API_KEY) as apollo:
            success = await apollo.test_connection()
            if success:
                print("✅ Apollo API connection successful")
                return True
            else:
                print("❌ Apollo API connection failed")
                return False
    except Exception as e:
        print(f"❌ Apollo API error: {e}")
        return False


async def test_web_scraping():
    """Test web scraping functionality"""
    print("\n🌐 Testing Web Scraping")

    try:
        async with WebScraper() as scraper:
            # Test scraping a company about page
            data = await scraper.scrape_company_about_page("example.com")
            print(f"✅ Web scraping test completed")
            print(f"   Data extracted: {list(data.keys())}")
            return True
    except Exception as e:
        print(f"❌ Web scraping error: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 ABM Research System - Phase 1 Testing")
    print("=" * 50)

    # Test 1: Mock Phase 1 workflow
    account = await test_phase_1_mock()

    # Test 2: Apollo API (if available)
    apollo_works = await test_apollo_connection()

    # Test 3: Web scraping
    web_works = await test_web_scraping()

    print("\n📊 Test Summary:")
    print(f"   Mock Phase 1: ✅ Completed")
    print(f"   Apollo API: {'✅' if apollo_works else '❌'} {'Connected' if apollo_works else 'Not available'}")
    print(f"   Web Scraping: {'✅' if web_works else '❌'} {'Working' if web_works else 'Failed'}")

    if apollo_works:
        print(f"\n🎯 Ready for live Phase 1 testing with: {account.name}")
    else:
        print(f"\n💡 Configure Apollo API key in .env to enable full testing")


if __name__ == "__main__":
    asyncio.run(main())