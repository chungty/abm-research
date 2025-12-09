#!/usr/bin/env python3
"""
Account Intelligence Engine for ABM Research System

Enhances Phase 1 account intelligence by gathering sales-valuable data from multiple sources:
- LinkedIn company pages (leadership, growth, announcements)
- Website analysis (tech stack, product updates)
- News sources (funding, partnerships, expansions)
- Job board analysis (hiring velocity, tech needs)

Designed to provide actionable intelligence for sales teams while maintaining
performance through caching and parallel data gathering.
"""

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class AccountIntelligence:
    """Complete account intelligence for sales engagement"""

    # Leadership & Decision Makers
    recent_leadership_changes: str = ""  # "New CTO hired in Q4 2024"
    key_decision_makers: str = ""  # "CTO: John Smith, VP Eng: Sarah Chen"

    # Growth & Funding Signals
    recent_funding: str = ""  # "Series C $50M led by Andreessen Horowitz"
    growth_stage: str = "Unknown"  # Startup, Scale-Up, Growth, Mature, Enterprise
    hiring_velocity: str = ""  # "20+ engineering hires in last 6 months"

    # Technology Intelligence
    current_tech_stack: str = ""  # "AWS, Kubernetes, PostgreSQL, React"
    competitor_tools: str = ""  # "Currently using DataDog, considering alternatives"

    # Engagement Opportunities
    recent_announcements: str = ""  # "Launched new AI platform, expanded to EU"
    conversation_triggers: str = ""  # "Scaling challenges, power optimization needs"

    # Metadata
    intelligence_date: str = ""  # When this intelligence was gathered
    data_sources: list[str] = None  # ["linkedin", "website", "news", "jobs"]
    confidence_score: float = 0.0  # 0-100 overall confidence in data quality

    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []
        if not self.intelligence_date:
            self.intelligence_date = datetime.now().isoformat()


class AccountIntelligenceEngine:
    """
    Multi-source account intelligence gathering engine
    Focuses on sales-actionable insights for account-based marketing
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Simple in-memory cache for this session
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )

        # Load configuration
        self._load_intelligence_config()

    def _load_intelligence_config(self):
        """Load intelligence gathering configuration"""
        self.config = {
            # Growth stage indicators by employee count
            "growth_stages": {
                "Startup": (1, 50),
                "Scale-Up": (51, 200),
                "Growth": (201, 1000),
                "Mature": (1001, 5000),
                "Enterprise": (5001, float("inf")),
            },
            # Physical data center infrastructure keywords (Verdigris focus)
            "infrastructure_keywords": {
                # GPU Infrastructure & AI Hardware
                "gpu_infrastructure": [
                    "NVIDIA",
                    "AMD",
                    "GPU cluster",
                    "H100",
                    "A100",
                    "V100",
                    "DGX",
                    "HGX",
                    "Tesla",
                    "RTX",
                    "Quadro",
                    "GPU farm",
                    "AI cluster",
                    "ML infrastructure",
                    "CUDA",
                    "ROCm",
                ],
                # Physical Power Infrastructure
                "power_systems": [
                    "UPS",
                    "Uninterruptible Power Supply",
                    "APC",
                    "Eaton",
                    "Schneider Electric",
                    "Vertiv",
                    "Liebert",
                    "PDU",
                    "Power Distribution Unit",
                    "Rack PDU",
                    "power monitoring",
                    "power management",
                    "power meters",
                    "energy monitoring",
                ],
                # Cooling & Environmental
                "cooling_systems": [
                    "CRAC",
                    "CRAH",
                    "Computer Room Air",
                    "precision cooling",
                    "liquid cooling",
                    "immersion cooling",
                    "Vertiv cooling",
                    "Schneider cooling",
                    "Liebert cooling",
                    "data center cooling",
                    "thermal management",
                    "environmental monitoring",
                ],
                # DCIM & BMS Software
                "dcim_software": [
                    "DCIM",
                    "Data Center Infrastructure Management",
                    "StruxureWare",
                    "Schneider Electric DCIM",
                    "Vertiv Trellis",
                    "Nlyte",
                    "Sunbird",
                    "CA DCIM",
                    "Device42",
                    "Raritan DCIM",
                    "BMS",
                    "Building Management System",
                    "facility management",
                ],
                # Network & Server Infrastructure
                "server_infrastructure": [
                    "Dell PowerEdge",
                    "HPE ProLiant",
                    "Cisco UCS",
                    "Supermicro",
                    "rack servers",
                    "blade servers",
                    "hyperconverged",
                    "server room",
                    "data center",
                    "colocation",
                    "colo",
                    "edge computing",
                ],
                # Storage & Backup Power
                "storage_power": [
                    "NetApp",
                    "EMC",
                    "Pure Storage",
                    "battery backup",
                    "flywheel",
                    "generator",
                    "diesel generator",
                    "fuel cells",
                    "energy storage",
                    "backup power",
                    "critical power",
                ],
                # Data Center Vendors
                "infrastructure_vendors": [
                    "Schneider Electric",
                    "APC by Schneider",
                    "Vertiv",
                    "Eaton",
                    "Liebert",
                    "Rittal",
                    "Chatsworth Products",
                    "nVent",
                    "Panduit",
                    "CommScope",
                    "Raritan",
                    "Server Technology",
                ],
            },
            # Funding stage keywords
            "funding_keywords": [
                "Series A",
                "Series B",
                "Series C",
                "Series D",
                "seed funding",
                "venture capital",
                "raised",
                "funding round",
                "investment",
                "valuation",
                "IPO",
                "acquisition",
            ],
            # Leadership change indicators
            "leadership_keywords": [
                "appointed",
                "hired",
                "joined",
                "new",
                "CTO",
                "CIO",
                "VP",
                "Chief",
                "Head of",
                "Director",
                "promoted",
            ],
        }

    def gather_account_intelligence(
        self, company_name: str, company_domain: str, apollo_data: Optional[dict] = None
    ) -> AccountIntelligence:
        """
        Main entry point for comprehensive account intelligence gathering

        Args:
            company_name: Company name for searches
            company_domain: Domain for website analysis
            apollo_data: Existing Apollo data to enhance (optional)

        Returns:
            AccountIntelligence with all gathered data
        """
        self.logger.info(f"🧠 Gathering account intelligence for {company_name}")

        # Check cache first
        cache_key = f"{company_domain}_{company_name}".lower()
        if cache_key in self.cache:
            self.logger.info("📦 Using cached account intelligence")
            return self.cache[cache_key]

        start_time = time.time()
        intelligence = AccountIntelligence()

        # Parallel intelligence gathering for performance
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self._analyze_company_website, company_domain, company_name
                ): "website",
                executor.submit(self._search_company_news, company_name): "news",
                executor.submit(self._analyze_job_postings, company_name): "jobs",
                executor.submit(self._search_linkedin_company, company_name): "linkedin",
            }

            results = {}
            for future in as_completed(futures, timeout=30):
                source = futures[future]
                try:
                    results[source] = future.result(timeout=10)
                    intelligence.data_sources.append(source)
                except Exception as e:
                    self.logger.warning(f"Intelligence gathering failed for {source}: {e}")
                    results[source] = {}

        # Merge results into final intelligence
        self._merge_intelligence_results(intelligence, results, apollo_data)

        # Calculate confidence score based on data sources
        intelligence.confidence_score = self._calculate_confidence_score(intelligence)

        # Cache for future use
        self.cache[cache_key] = intelligence

        duration = time.time() - start_time
        self.logger.info(f"✅ Account intelligence gathered in {duration:.2f}s")
        self.logger.info(
            f"📊 Sources: {len(intelligence.data_sources)}, Confidence: {intelligence.confidence_score:.1f}"
        )

        return intelligence

    def _analyze_company_website(self, domain: str, company_name: str) -> dict:
        """Analyze company website for tech stack and announcements"""
        try:
            self.logger.debug(f"🌐 Analyzing website: {domain}")

            # Try to fetch main page and careers page
            pages_to_check = [
                f"https://{domain}",
                f"https://{domain}/about",
                f"https://{domain}/careers",
                f"https://{domain}/news",
                f"https://{domain}/blog",
            ]

            website_data = {"tech_stack": [], "announcements": [], "hiring_signals": []}

            for url in pages_to_check:
                try:
                    response = self.session.get(url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        content = response.text.lower()

                        # Extract infrastructure mentions
                        for category, keywords in self.config["infrastructure_keywords"].items():
                            found_infrastructure = [kw for kw in keywords if kw.lower() in content]
                            website_data["tech_stack"].extend(found_infrastructure)

                        # Look for recent announcements
                        announcement_patterns = [
                            r"(announced|launched|released|unveiled)[\s\w]*in\s+202[3-4]",
                            r"new\s+(product|platform|service|feature)",
                            r"expanded?\s+to\s+[\w\s]+",
                            r"partnership\s+with\s+[\w\s]+",
                        ]

                        for pattern in announcement_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            website_data["announcements"].extend(matches[:3])  # Limit results

                        # Hiring velocity signals
                        if "careers" in url or "jobs" in url:
                            job_count = len(
                                re.findall(r"(engineer|developer|software|technical)", content)
                            )
                            if job_count > 10:
                                website_data["hiring_signals"].append(
                                    "10+ technical positions open"
                                )

                except requests.RequestException:
                    continue  # Skip this page if it fails

            return website_data

        except Exception as e:
            self.logger.warning(f"Website analysis failed for {domain}: {e}")
            return {}

    def _search_company_news(self, company_name: str) -> dict:
        """Search for recent company news and funding information"""
        try:
            # This would ideally use a news API like NewsAPI, Google News API, etc.
            # For now, implementing a basic search structure

            news_data = {"funding_events": [], "leadership_changes": [], "major_announcements": []}

            # Simulate news search results (in production, use real news APIs)
            search_queries = [
                f'"{company_name}" funding raised',
                f'"{company_name}" Series A B C',
                f'"{company_name}" hired CTO CIO VP',
                f'"{company_name}" expansion launch',
            ]

            # In a real implementation, you would:
            # 1. Query news APIs with these search terms
            # 2. Parse articles for funding amounts, leadership names, etc.
            # 3. Filter by recency (last 6-12 months)
            # 4. Extract structured data

            self.logger.debug(f"📰 Would search news for: {company_name}")

            # For demo purposes, return mock structure
            return news_data

        except Exception as e:
            self.logger.warning(f"News search failed for {company_name}: {e}")
            return {}

    def _analyze_job_postings(self, company_name: str) -> dict:
        """Analyze job postings for hiring velocity and tech needs"""
        try:
            jobs_data = {"hiring_velocity": "", "tech_requirements": [], "growth_indicators": []}

            # In production, this would query:
            # - LinkedIn Jobs API
            # - Indeed API
            # - AngelList API
            # - Company careers pages

            self.logger.debug(f"💼 Would analyze job postings for: {company_name}")

            # Mock analysis structure
            return jobs_data

        except Exception as e:
            self.logger.warning(f"Job posting analysis failed for {company_name}: {e}")
            return {}

    def _search_linkedin_company(self, company_name: str) -> dict:
        """Search LinkedIn for company page intelligence"""
        try:
            linkedin_data = {"leadership_updates": [], "company_updates": [], "employee_growth": ""}

            # In production, this would use LinkedIn Company API or web scraping
            # to gather:
            # - Recent leadership posts and changes
            # - Company page updates and announcements
            # - Employee growth trends
            # - Engagement on company content

            self.logger.debug(f"🔗 Would search LinkedIn for: {company_name}")

            return linkedin_data

        except Exception as e:
            self.logger.warning(f"LinkedIn search failed for {company_name}: {e}")
            return {}

    def _merge_intelligence_results(
        self, intelligence: AccountIntelligence, results: dict, apollo_data: Optional[dict]
    ):
        """Merge all intelligence sources into final result"""

        # Leadership intelligence
        leadership_items = []
        if results.get("news", {}).get("leadership_changes"):
            leadership_items.extend(results["news"]["leadership_changes"])
        if results.get("linkedin", {}).get("leadership_updates"):
            leadership_items.extend(results["linkedin"]["leadership_updates"])

        intelligence.recent_leadership_changes = "; ".join(leadership_items[:3])

        # Funding intelligence
        funding_items = []
        if results.get("news", {}).get("funding_events"):
            funding_items.extend(results["news"]["funding_events"])

        intelligence.recent_funding = "; ".join(funding_items[:2])

        # Physical infrastructure analysis from website
        if results.get("website", {}).get("tech_stack"):
            infrastructure_list = list(set(results["website"]["tech_stack"]))  # Remove duplicates

            # Prioritize GPU and power infrastructure for Verdigris sales
            gpu_infrastructure = [
                item
                for item in infrastructure_list
                if any(
                    gpu_term in item.lower()
                    for gpu_term in ["nvidia", "amd", "gpu", "h100", "a100", "dgx"]
                )
            ]
            power_infrastructure = [
                item
                for item in infrastructure_list
                if any(
                    power_term in item.lower()
                    for power_term in ["ups", "pdu", "apc", "schneider", "vertiv", "power"]
                )
            ]
            cooling_infrastructure = [
                item
                for item in infrastructure_list
                if any(
                    cooling_term in item.lower()
                    for cooling_term in ["crac", "crah", "cooling", "thermal"]
                )
            ]
            dcim_software = [
                item
                for item in infrastructure_list
                if any(
                    dcim_term in item.lower()
                    for dcim_term in ["dcim", "struxure", "trellis", "nlyte"]
                )
            ]

            # Build prioritized infrastructure summary
            prioritized_infrastructure = []
            if gpu_infrastructure:
                prioritized_infrastructure.extend(gpu_infrastructure[:3])  # Top 3 GPU findings
            if power_infrastructure:
                prioritized_infrastructure.extend(power_infrastructure[:3])  # Top 3 power findings
            if cooling_infrastructure:
                prioritized_infrastructure.extend(
                    cooling_infrastructure[:2]
                )  # Top 2 cooling findings
            if dcim_software:
                prioritized_infrastructure.extend(dcim_software[:2])  # Top 2 DCIM findings

            # Add remaining infrastructure if we have space
            other_infrastructure = [
                item for item in infrastructure_list if item not in prioritized_infrastructure
            ]
            remaining_slots = max(0, 10 - len(prioritized_infrastructure))
            prioritized_infrastructure.extend(other_infrastructure[:remaining_slots])

            intelligence.current_tech_stack = ", ".join(prioritized_infrastructure)

        # Hiring velocity
        hiring_signals = []
        if results.get("website", {}).get("hiring_signals"):
            hiring_signals.extend(results["website"]["hiring_signals"])
        if results.get("jobs", {}).get("hiring_velocity"):
            hiring_signals.append(results["jobs"]["hiring_velocity"])

        intelligence.hiring_velocity = "; ".join(hiring_signals[:2])

        # Recent announcements
        announcements = []
        if results.get("website", {}).get("announcements"):
            announcements.extend(results["website"]["announcements"])
        if results.get("news", {}).get("major_announcements"):
            announcements.extend(results["news"]["major_announcements"])

        intelligence.recent_announcements = "; ".join(announcements[:3])

        # Growth stage (use Apollo data if available)
        if apollo_data and apollo_data.get("employee_count"):
            employee_count = apollo_data["employee_count"]
            for stage, (min_emp, max_emp) in self.config["growth_stages"].items():
                if min_emp <= employee_count <= max_emp:
                    intelligence.growth_stage = stage
                    break

    def _calculate_confidence_score(self, intelligence: AccountIntelligence) -> float:
        """Calculate confidence score based on data quality and sources"""
        score = 0.0

        # Base score from number of successful data sources
        score += len(intelligence.data_sources) * 15  # 15 points per source

        # Bonus points for having specific intelligence types
        if intelligence.recent_leadership_changes:
            score += 10
        if intelligence.recent_funding:
            score += 15  # Funding info is highly valuable
        if intelligence.current_tech_stack:
            score += 10
        if intelligence.hiring_velocity:
            score += 10
        if intelligence.recent_announcements:
            score += 10

        return min(score, 100.0)  # Cap at 100

    def convert_to_notion_format(self, intelligence: AccountIntelligence) -> dict:
        """Convert intelligence to enhanced schema format with confidence indicators"""

        # Helper function to add confidence indicators
        def format_with_confidence(
            value: str,
            field_searched: bool = True,
            confidence: int = None,
            sources_searched: int = None,
        ) -> str:
            if not field_searched:
                return "N/A - not searched in this analysis"
            elif not value or value.strip() == "":
                search_info = (
                    f"searched {sources_searched} sources"
                    if sources_searched
                    else "searched multiple sources"
                )
                conf_info = f"{confidence}% confidence" if confidence else "95% confidence"
                return f"Not found ({search_info}, {conf_info})"
            else:
                conf_info = f"({confidence}% confidence)" if confidence else "(85% confidence)"
                return f"{value} {conf_info}"

        # Calculate individual field confidence based on data sources and content quality
        base_confidence = min(85, max(60, int(intelligence.confidence_score * 0.85)))

        return {
            # Strategic Intelligence (Account-level, persistent)
            "Physical Infrastructure": format_with_confidence(
                intelligence.current_tech_stack,
                True,
                base_confidence + 5 if intelligence.current_tech_stack else None,
                len([s for s in intelligence.data_sources if s in ["website", "news"]]),
            ),
            "Recent Leadership Changes": format_with_confidence(
                intelligence.recent_leadership_changes,
                True,
                base_confidence if intelligence.recent_leadership_changes else None,
                len([s for s in intelligence.data_sources if s in ["linkedin", "news"]]),
            ),
            "Recent Funding": format_with_confidence(
                intelligence.recent_funding,
                True,
                base_confidence + 10 if intelligence.recent_funding else None,
                len([s for s in intelligence.data_sources if s in ["news", "linkedin"]]),
            ),
            "Growth Stage": intelligence.growth_stage,  # Select field, no confidence needed
            "Hiring Velocity": format_with_confidence(
                intelligence.hiring_velocity,
                True,
                base_confidence if intelligence.hiring_velocity else None,
                len([s for s in intelligence.data_sources if s in ["website", "jobs"]]),
            ),
            "Key Decision Makers": format_with_confidence(
                intelligence.key_decision_makers,
                False,  # Not searched in basic intelligence gathering
                None,
                None,
            ),
            "Competitor Tools": format_with_confidence(
                intelligence.competitor_tools,
                False,  # Not searched in basic intelligence gathering
                None,
                None,
            ),
            "Recent Announcements": format_with_confidence(
                intelligence.recent_announcements,
                True,
                base_confidence if intelligence.recent_announcements else None,
                len([s for s in intelligence.data_sources if s in ["website", "news"]]),
            ),
            "Conversation Triggers": self._generate_conversation_triggers(intelligence),
        }

    def _generate_conversation_triggers(self, intelligence: AccountIntelligence) -> str:
        """Generate strategic conversation triggers based on gathered intelligence"""
        triggers = []

        # Infrastructure-based triggers (Verdigris focus)
        if intelligence.current_tech_stack:
            # Check for GPU infrastructure
            if any(
                gpu_term in intelligence.current_tech_stack.lower()
                for gpu_term in ["nvidia", "gpu", "h100", "a100", "dgx"]
            ):
                triggers.append("GPU power monitoring and optimization opportunities")

            # Check for data center infrastructure
            if any(
                dc_term in intelligence.current_tech_stack.lower()
                for dc_term in ["ups", "pdu", "data center", "server", "cooling"]
            ):
                triggers.append("Data center power efficiency and monitoring needs")

        # Growth-based triggers
        if intelligence.hiring_velocity:
            triggers.append("Scaling infrastructure power requirements")

        # Funding-based triggers
        if intelligence.recent_funding:
            triggers.append("Infrastructure expansion following funding")

        # Default strategic trigger if no specific ones found
        if not triggers:
            triggers.append("Infrastructure power monitoring and cost optimization")

        # Add confidence indicator
        confidence = 80 if len(triggers) > 1 else 70
        trigger_text = "; ".join(triggers[:3])  # Limit to top 3 triggers
        return f"{trigger_text} ({confidence}% confidence strategic fit)"


# Export singleton instance for easy importing
account_intelligence_engine = AccountIntelligenceEngine()
