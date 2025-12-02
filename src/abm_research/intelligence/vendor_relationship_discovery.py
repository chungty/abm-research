#!/usr/bin/env python3
"""
Vendor Relationship Discovery - Trusted Paths Intelligence

Discovers publicly documented vendor-customer relationships using Brave Search.
Identifies "trusted paths" into target accounts via shared vendor relationships.

Based on the strategy: inputs → actions → outputs with deterministic scoring.
"""

import os
import re
import time
import json
import requests
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

# OpenAI for LLM-powered vendor extraction
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class VendorCustomerSignal:
    """
    A publicly documented relationship signal between a vendor and customer.
    Core data structure for trusted path analysis.
    """
    # Relationship parties
    vendor: str
    customer: str

    # Signal classification
    signal_type: str  # case_study, joint_pr, integration, conference, procurement_record, webinar, logo_mention
    signal_strength: int  # 1-5 per the scoring rubric

    # Evidence
    evidence_url: str
    evidence_title: str
    evidence_snippet: str

    # Metadata
    recency: Optional[str] = None  # Year or date text
    people_involved: List[str] = field(default_factory=list)  # Names/titles if extractable

    # Scoring context
    is_cobranded: bool = False
    is_deployment_story: bool = False
    customer_named_explicitly: bool = False

    # Timestamps
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VendorIntroScore:
    """Aggregated intro power score for a vendor across target accounts."""
    vendor_name: str
    intro_score: float  # CoverageCount * AvgSignalStrength * FitWeight
    coverage_count: int  # Number of distinct customers with signals
    avg_signal_strength: float
    fit_weight: float

    # Details
    customer_signals: Dict[str, List[VendorCustomerSignal]] = field(default_factory=dict)

    # Intro candidates (people from evidence)
    intro_candidates: List[Dict] = field(default_factory=list)


@dataclass
class DiscoveredVendor:
    """
    A vendor discovered through account-centric search.
    Used when we don't know the vendors in advance.

    Now includes strategic purpose metadata for actionable intelligence:
    - strategic_purpose: competitor, channel, intro_path, evaluate
    - recommended_action: What to do when this vendor is discovered
    """
    vendor_name: str
    category: str  # competitors_power, channel_electrical, complementary_compute, etc.
    mention_count: int  # How many times mentioned across searches
    evidence_urls: List[str] = field(default_factory=list)
    evidence_snippets: List[str] = field(default_factory=list)
    relationship_type: str = "unknown"  # customer, partner, integration, competitor
    confidence: float = 0.0  # 0-1 confidence score
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Strategic purpose fields (NEW)
    strategic_purpose: str = "unknown"  # competitor, channel, intro_path, evaluate
    recommended_action: str = ""  # What to do when this vendor is discovered


class VendorRelationshipDiscovery:
    """
    Discovers vendor-customer relationships using public data (Brave Search).

    This powers the "trusted paths" feature:
    - Find which vendors have documented relationships with target accounts
    - Score vendors by their intro power (reach + evidence strength)
    - Identify human intro candidates from evidence
    """

    # Search templates for finding vendor-customer relationships
    SEARCH_TEMPLATES = [
        '"{vendor}" "{customer}" case study',
        '"{vendor}" "{customer}" partnership',
        '"{vendor}" "{customer}" webinar',
        '"{vendor}" "{customer}" contract awarded',
        '"{customer}" "implemented by" "{vendor}"',
        '"{customer}" "selects" "{vendor}"',
        '"{customer}" "deploys" "{vendor}"',
        '"{vendor}" "{customer}" integration',
        '"{vendor}" "{customer}" customer story',
        '"{vendor}" "{customer}" success story',
    ]

    # Signal type detection patterns
    SIGNAL_PATTERNS = {
        "case_study": [
            r"case study", r"customer story", r"success story",
            r"customer spotlight", r"how .* uses"
        ],
        "joint_pr": [
            r"press release", r"announces", r"partnership",
            r"strategic alliance", r"collaboration"
        ],
        "integration": [
            r"integration", r"connector", r"plugin",
            r"api", r"interoperab"
        ],
        "conference": [
            r"conference", r"summit", r"webinar",
            r"keynote", r"panel", r"speaking"
        ],
        "procurement_record": [
            r"contract", r"awarded", r"procurement",
            r"selects", r"chooses", r"deploys"
        ],
        "webinar": [
            r"webinar", r"virtual event", r"online session",
            r"live demo", r"workshop"
        ],
        "logo_mention": [
            r"customer", r"clients include", r"trusted by",
            r"logo", r"portfolio"
        ]
    }

    # Signal strength scoring rubric (1-5)
    STRENGTH_RUBRIC = {
        1: "Logo/mention only; weak evidence",
        2: "Customer name referenced but not formal story",
        3: "Named case study, webinar, or clear narrative",
        4: "Joint press release, integration launch, or multi-party collaboration",
        5: "Multiple assets over time or contract award specifying vendor involvement"
    }

    # ==========================================================================
    # WORKFLOW 2: Account-centric vendor discovery templates
    # REFACTORED: Focused on strategic categories only
    # Removed: Generic consultants, DevOps platforms, investors (wrong buyer personas)
    # ==========================================================================
    VENDOR_DISCOVERY_TEMPLATES = [
        # --- Competitor Intelligence (who is the incumbent?) ---
        '"{account}" power monitoring Schneider Eaton Vertiv',
        '"{account}" energy management system',
        '"{account}" DCIM software Nlyte Sunbird',

        # --- Channel Partners (who serves this account?) ---
        '"{account}" electrical contractor datacenter',
        '"{account}" power installation contractor',
        '"{account}" datacenter construction partner',
        '"{account}" design build data center',
        '"{account}" CDW WWT SHI infrastructure',

        # --- Complementary Vendors (intro path opportunities) ---
        '"{account}" GPU NVIDIA AMD infrastructure',
        '"{account}" cooling Carrier Trane Johnson Controls',
        '"{account}" networking Cisco Arista',
        '"{account}" infrastructure vendors partners',
        '"{account}" datacenter infrastructure',
        '"{account}" powered by deploys',
        # DC Rectifier specific searches
        '"{account}" DC rectifier deployment',
        '"{account}" "48V DC" infrastructure',
        '"{account}" power conversion system',
        '"{account}" rectifier upgrade',
        '"{account}" Delta Electronics OR Eltek OR "Huawei Digital Power"',
    ]

    # ==========================================================================
    # KNOWN_VENDORS - Strategic Purpose-Driven Categories
    # Organized by: Competitors, Channel Partners, Complementary Vendors
    # Each category maps to a strategic purpose and recommended action
    # ==========================================================================
    KNOWN_VENDORS = {
        # === TIER 1: COMPETITORS (Track incumbents to displace) ===
        # Purpose: Know who the incumbent is at target accounts
        # Action: Plan displacement strategy
        "competitors_power": [
            "Schneider Electric",  # Primary competitor in power monitoring
            "ABB",                 # ~41-43% combined market share in DC power
            "Eaton",
            "Vertiv",
            "Siemens",
            "Delta Electronics",
            "Legrand",
            "Emerson",
        ],
        # DCIM/Software - evaluate case-by-case if competitive or complementary
        "software_dcim": [
            "Nlyte",
            "Sunbird",
            "Envizi",        # Carbon/sustainability tracking
            "VMware",        # Virtualization
        ],

        # === TIER 2: CHANNEL PARTNERS (Build relationships) ===
        # Purpose: Find SIs/VARs serving target accounts to build partnerships
        # Action: Build relationships with RIGHT channel partners

        # DC Electrical Contractors (do power installations for data centers)
        "channel_electrical": [
            "Rosendin Electric",
            "Cupertino Electric",
            "Faith Technologies",
            "Interstates",
            "Mass Electric",
            "Bergelectric",
            "MYR Group",
        ],
        # DC Design-Build Firms (construct data centers)
        "channel_design_build": [
            "Holder Construction",
            "Mortenson",
            "DPR Construction",
            "Turner Construction",
            "JE Dunn",
            "Corgan",           # DC architects
            "HDR",
            "Jacobs",
            "Black & Veatch",
            "Burns & McDonnell",
        ],
        # IT VARs with DC Focus (sell infrastructure to data centers)
        "channel_vars": [
            "CDW",
            "WWT",
            "World Wide Technology",
            "SHI",
            "Insight Enterprises",
            "Connection",
            "ePlus",
            "Trace3",
            "Presidio",
        ],

        # === TIER 3: COMPLEMENTARY VENDORS (Intro paths) ===
        # Purpose: Non-competing vendors for warm intros
        # Action: Ask for introduction to shared customers

        # Cooling (non-competing, sell to same facilities buyers)
        "complementary_cooling": [
            "Carrier", "Trane", "Johnson Controls",
            "Daikin", "Munters", "Stulz", "Airedale",
        ],
        # Compute (know which GPU vendors serve target accounts)
        "complementary_compute": [
            "NVIDIA", "AMD", "Intel", "Cerebras",
            "Graphcore", "SambaNova", "Groq",
            "Dell", "HPE", "Supermicro", "Lenovo", "Quanta",
        ],
        # Networking (adjacent to facilities teams)
        "complementary_networking": [
            "Cisco", "Arista", "Juniper", "Mellanox",
        ],
        # DC Rectifier Vendors (TARGET ICP - DC power infrastructure)
        "dc_rectifier_vendors": [
            "Delta Electronics",
            "ABB Power",
            "Vertiv",
            "Eltek",
            "Huawei Digital Power",
            "ZTE Power",
            "Emerson Network Power",
            "Rectifier Technologies",
        ],
    }

    # Strategic purpose metadata for each category
    CATEGORY_METADATA = {
        "competitors_power": {
            "strategic_purpose": "competitor",
            "action": "Plan displacement strategy",
            "description": "Power monitoring competitors - track incumbents",
        },
        "software_dcim": {
            "strategic_purpose": "evaluate",
            "action": "Evaluate if competitive or complementary",
            "description": "DCIM software - may compete with Signals",
        },
        "channel_electrical": {
            "strategic_purpose": "channel",
            "action": "Build relationship for co-sell",
            "description": "DC electrical contractors who could resell Verdigris",
        },
        "channel_design_build": {
            "strategic_purpose": "channel",
            "action": "Build relationship for co-sell",
            "description": "DC design-build firms who could spec Verdigris",
        },
        "channel_vars": {
            "strategic_purpose": "channel",
            "action": "Build relationship for co-sell",
            "description": "IT VARs who sell to data centers",
        },
        "complementary_cooling": {
            "strategic_purpose": "intro_path",
            "action": "Ask for warm introduction",
            "description": "Non-competing cooling vendors with shared customers",
        },
        "complementary_compute": {
            "strategic_purpose": "intro_path",
            "action": "Ask for warm introduction",
            "description": "GPU/compute vendors with shared customers",
        },
        "complementary_networking": {
            "strategic_purpose": "intro_path",
            "action": "Ask for warm introduction",
            "description": "Networking vendors with shared customers",
        },
        "dc_rectifier_vendors": {
            "strategic_purpose": "intro_path",
            "action": "Ask for warm introduction - DC power focus",
            "description": "DC rectifier/power conversion vendors - TARGET ICP for power infrastructure",
        },
    }

    def __init__(self, notion_client=None):
        self.brave_api_key = os.getenv('BRAVE_API_KEY')
        if not self.brave_api_key:
            logger.warning("BRAVE_API_KEY not set - vendor discovery disabled")

        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"

        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 0.5  # 0.5 seconds between requests (faster, with retry on 429)
        self.max_retries = 3  # Max retries on rate limit

        # Cache to avoid duplicate searches
        self._search_cache: Dict[str, List[Dict]] = {}

        # OpenAI client for LLM-powered extraction
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized for vendor extraction")

        # Notion client for persistence (lazy loaded)
        self._notion_client = notion_client

        # Dynamic vendor list (starts with KNOWN_VENDORS, extended by discovered vendors)
        self._dynamic_vendors: Dict[str, List[str]] = {}
        self._init_dynamic_vendors()

    def _init_dynamic_vendors(self):
        """Initialize dynamic vendor list from KNOWN_VENDORS + discovered vendors from Notion."""
        # Start with a copy of KNOWN_VENDORS
        for category, vendors in self.KNOWN_VENDORS.items():
            self._dynamic_vendors[category] = list(vendors)

        # Load discovered vendors from Notion if available
        discovered = self._load_discovered_vendors_from_notion()
        for category, vendors in discovered.items():
            if category in self._dynamic_vendors:
                # Extend existing category, avoiding duplicates
                for vendor in vendors:
                    if vendor not in self._dynamic_vendors[category]:
                        self._dynamic_vendors[category].append(vendor)
            else:
                self._dynamic_vendors[category] = list(vendors)

        total_vendors = sum(len(v) for v in self._dynamic_vendors.values())
        logger.info(f"Dynamic vendor list initialized with {total_vendors} vendors across {len(self._dynamic_vendors)} categories")

    def _load_discovered_vendors_from_notion(self) -> Dict[str, List[str]]:
        """Load discovered vendors from Notion Partnerships database."""
        discovered: Dict[str, List[str]] = {}

        if not self._notion_client:
            return discovered

        try:
            # Query partnerships with is_discovered=true
            partnerships = self._notion_client.query_all_partnerships()

            for p in partnerships:
                props = p.get('properties', {})

                # Check if this is a discovered vendor
                is_discovered = props.get('Is Discovered', {}).get('checkbox', False)
                if not is_discovered:
                    continue

                # Get vendor name
                name_prop = props.get('Name', {}).get('title', [])
                vendor_name = name_prop[0]['text']['content'] if name_prop else None
                if not vendor_name:
                    continue

                # Get category
                category_prop = props.get('Category', {}).get('select', {})
                category = category_prop.get('name', 'discovered_unknown')

                # Add to discovered vendors
                if category not in discovered:
                    discovered[category] = []
                if vendor_name not in discovered[category]:
                    discovered[category].append(vendor_name)

            if discovered:
                total = sum(len(v) for v in discovered.values())
                logger.info(f"Loaded {total} discovered vendors from Notion")

        except Exception as e:
            logger.warning(f"Could not load discovered vendors from Notion: {e}")

        return discovered

    def extract_vendors_from_text(self, text: str, account_name: str) -> List[Dict]:
        """
        WORKFLOW 3 STEP 1: Use LLM to extract company names from text and classify them.

        Uses GPT-4o-mini for cost-effective extraction (~$0.02/account).

        Args:
            text: The search result text to analyze
            account_name: The target account (to avoid extracting the account itself)

        Returns:
            List of dicts: [{"name": str, "category": str, "confidence": float, "evidence": str}]
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available - cannot extract vendors via LLM")
            return []

        # Build the category descriptions for the prompt
        category_descriptions = []
        for cat, meta in self.CATEGORY_METADATA.items():
            category_descriptions.append(f"- {cat}: {meta['description']}")

        prompt = f"""Extract company names from this text that are vendors, partners, or service providers
related to {account_name}'s data center or IT infrastructure.

Do NOT include:
- {account_name} itself
- Generic companies (Google, Microsoft, Amazon) unless clearly acting as a vendor
- News sources or publishers

For each company found, classify into ONE of these categories:
{chr(10).join(category_descriptions)}
- discovered_unknown: Cannot determine category

Return ONLY a JSON array. Each item must have:
- "name": Company name (proper capitalization)
- "category": One of the categories above
- "confidence": 0.0-1.0 (how confident you are this is a real vendor relationship)
- "evidence": Brief quote or reason from the text

Text to analyze:
---
{text[:3000]}
---

Return JSON array only, no markdown:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a B2B sales intelligence analyst extracting vendor relationships from text. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            vendors = json.loads(content)

            # Validate structure
            validated = []
            for v in vendors:
                if isinstance(v, dict) and 'name' in v:
                    validated.append({
                        'name': v.get('name', ''),
                        'category': v.get('category', 'discovered_unknown'),
                        'confidence': float(v.get('confidence', 0.5)),
                        'evidence': v.get('evidence', '')[:200]
                    })

            return validated

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error in LLM vendor extraction: {e}")
            return []

    def extract_vendors_from_texts_batch(
        self,
        texts: List[Dict[str, str]],  # List of {text, url} dicts
        account_name: str,
        batch_size: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Extract vendors from multiple texts in a single LLM call (batch processing).

        This reduces API calls from N to N/batch_size, providing ~80% cost reduction.

        Args:
            texts: List of dicts with 'text' and 'url' keys
            account_name: Target account name
            batch_size: Number of texts per LLM call

        Returns:
            Dict mapping url -> List of extracted vendors
        """
        if not self.openai_client or not texts:
            return {}

        results: Dict[str, List[Dict]] = {}

        # Build category descriptions once
        category_descriptions = []
        for cat, meta in self.CATEGORY_METADATA.items():
            category_descriptions.append(f"- {cat}: {meta['description']}")
        categories_text = chr(10).join(category_descriptions)

        # Process in batches
        for batch_start in range(0, len(texts), batch_size):
            batch = texts[batch_start:batch_start + batch_size]

            # Build numbered batch prompt
            batch_texts = []
            for i, item in enumerate(batch):
                text_preview = item['text'][:1500]  # Smaller per item in batch
                batch_texts.append(f"[TEXT_{i}]\n{text_preview}\n[/TEXT_{i}]")

            combined = "\n\n".join(batch_texts)

            prompt = f"""Extract company names from these {len(batch)} text snippets that are vendors, partners,
or service providers related to {account_name}'s data center or IT infrastructure.

Do NOT include:
- {account_name} itself
- Generic companies (Google, Microsoft, Amazon) unless clearly acting as a vendor
- News sources or publishers

For each company found, classify into ONE of these categories:
{categories_text}
- discovered_unknown: Cannot determine category

Return a JSON object where keys are TEXT_0, TEXT_1, etc. and values are arrays of vendors.
Each vendor must have: name, category, confidence (0-1), evidence (brief quote).

Texts to analyze:
---
{combined}
---

Return JSON object only, no markdown:"""

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a B2B sales intelligence analyst extracting vendor relationships from text. Return only valid JSON objects."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000  # Larger for batch
                )

                content = response.choices[0].message.content.strip()

                # Handle markdown code blocks
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                batch_results = json.loads(content)

                # Map results back to URLs
                for i, item in enumerate(batch):
                    key = f"TEXT_{i}"
                    vendors_raw = batch_results.get(key, [])

                    validated = []
                    for v in vendors_raw:
                        if isinstance(v, dict) and 'name' in v:
                            validated.append({
                                'name': v.get('name', ''),
                                'category': v.get('category', 'discovered_unknown'),
                                'confidence': float(v.get('confidence', 0.5)),
                                'evidence': v.get('evidence', '')[:200]
                            })

                    results[item['url']] = validated

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse batch LLM response as JSON: {e}")
                # Fallback: mark all as empty
                for item in batch:
                    results[item['url']] = []
            except Exception as e:
                logger.warning(f"Error in batch LLM vendor extraction: {e}")
                for item in batch:
                    results[item['url']] = []

        return results

    def discover_unknown_vendors(
        self,
        account_name: str,
        save_to_notion: bool = True,
        min_confidence: float = 0.6
    ) -> Dict:
        """
        WORKFLOW 3: Discover NEW vendors not in KNOWN_VENDORS using LLM extraction.

        This extends Workflow 2 (discover_account_vendors) by:
        1. Running the same account-centric searches
        2. Using LLM to extract ANY company names (not just known vendors)
        3. Filtering out companies already in KNOWN_VENDORS
        4. Classifying and optionally persisting new vendors to Notion

        Args:
            account_name: The target account to research
            save_to_notion: Whether to persist discovered vendors to Notion
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            {
                "account": str,
                "workflow": "discover_unknown_vendors",
                "discovered_vendors": List[DiscoveredVendor],
                "new_vendors_count": int,
                "known_vendors_found": int,
                "saved_to_notion": int,
                "added_to_runtime": int,
                "search_results_analyzed": int
            }
        """
        logger.info(f"WORKFLOW 3: Discovering unknown vendors for {account_name}")

        if not self.brave_api_key:
            return {
                "account": account_name,
                "workflow": "discover_unknown_vendors",
                "error": "No BRAVE_API_KEY configured"
            }

        if not self.openai_client:
            return {
                "account": account_name,
                "workflow": "discover_unknown_vendors",
                "error": "No OpenAI client available - required for LLM extraction"
            }

        # Collect all search results
        all_results: List[Dict] = []
        search_errors: List[Dict] = []  # Track any API errors

        # Run account-centric searches
        for template in self.VENDOR_DISCOVERY_TEMPLATES:
            query = template.format(account=account_name)

            # Check cache
            cache_key = f"discovery:{query.lower()}"
            if cache_key in self._search_cache:
                results = self._search_cache[cache_key]
            else:
                response = self._brave_search(query)
                results = response.get('results', [])
                self._search_cache[cache_key] = results
                # Track errors for surfacing to dashboard
                if response.get('error'):
                    search_errors.append({
                        'query': query,
                        'error': response['error'],
                        'error_code': response.get('error_code'),
                        'retry_after': response.get('retry_after')
                    })

            for r in results:
                r['_search_query'] = query
            all_results.extend(results)

        # Build list of all known vendor names for filtering
        known_vendor_names: Set[str] = set()
        for category, vendors in self._dynamic_vendors.items():
            for v in vendors:
                known_vendor_names.add(v.lower())
                known_vendor_names.add(self._normalize_company(v))

        # Extract vendors via LLM from each result (using BATCH processing)
        llm_extracted: Dict[str, Dict] = {}  # vendor_name -> {count, evidence, category, confidence}
        known_vendors_found: Dict[str, Dict] = {}

        # Step 1: Collect all texts that pass the account name filter
        texts_to_process: List[Dict[str, str]] = []
        for result in all_results:
            title = result.get('title', '')
            description = result.get('description', '')
            url = result.get('url', '')

            # Skip if account not mentioned
            text = f"{title} {description}"
            account_lower = account_name.lower()
            if account_lower not in text.lower():
                continue

            texts_to_process.append({'text': text, 'url': url})

        # Step 2: Extract vendors via BATCH LLM call (reduces 20 calls to 4)
        batch_results = self.extract_vendors_from_texts_batch(
            texts=texts_to_process,
            account_name=account_name,
            batch_size=5
        )

        # Step 3: Process batched results
        for url, extracted in batch_results.items():
            for vendor in extracted:
                vendor_name = vendor['name']
                vendor_lower = vendor_name.lower()
                vendor_normalized = self._normalize_company(vendor_name)

                # Check if this is a known vendor
                is_known = (
                    vendor_lower in known_vendor_names or
                    vendor_normalized in known_vendor_names
                )

                target_dict = known_vendors_found if is_known else llm_extracted

                if vendor_name not in target_dict:
                    target_dict[vendor_name] = {
                        'count': 0,
                        'urls': [],
                        'snippets': [],
                        'category': vendor['category'],
                        'confidence': vendor['confidence'],
                        'evidence': vendor['evidence']
                    }

                target_dict[vendor_name]['count'] += 1
                if url and url not in target_dict[vendor_name]['urls']:
                    target_dict[vendor_name]['urls'].append(url)
                if vendor['evidence'] and vendor['evidence'] not in target_dict[vendor_name]['snippets']:
                    target_dict[vendor_name]['snippets'].append(vendor['evidence'])
                # Update confidence to max seen
                if vendor['confidence'] > target_dict[vendor_name]['confidence']:
                    target_dict[vendor_name]['confidence'] = vendor['confidence']

        # Convert to DiscoveredVendor objects
        discovered_vendors: List[DiscoveredVendor] = []
        saved_to_notion = 0
        added_to_runtime = 0

        for vendor_name, data in llm_extracted.items():
            # Filter by confidence
            if data['confidence'] < min_confidence:
                continue

            # Get strategic metadata
            category_meta = self.CATEGORY_METADATA.get(data['category'], {})

            vendor = DiscoveredVendor(
                vendor_name=vendor_name,
                category=data['category'],
                mention_count=data['count'],
                evidence_urls=data['urls'][:5],
                evidence_snippets=data['snippets'][:3],
                relationship_type=self._detect_relationship_type(
                    account_name, vendor_name, data['snippets']
                ),
                confidence=data['confidence'],
                strategic_purpose=category_meta.get('strategic_purpose', 'unknown'),
                recommended_action=category_meta.get('action', '')
            )

            discovered_vendors.append(vendor)

            # Save to Notion if requested
            if save_to_notion and self._notion_client:
                try:
                    self._save_discovered_vendor_to_notion(vendor, account_name)
                    saved_to_notion += 1
                except Exception as e:
                    logger.warning(f"Failed to save vendor {vendor_name} to Notion: {e}")

            # Add to runtime cache
            if data['category'] not in self._dynamic_vendors:
                self._dynamic_vendors[data['category']] = []
            if vendor_name not in self._dynamic_vendors[data['category']]:
                self._dynamic_vendors[data['category']].append(vendor_name)
                added_to_runtime += 1

        # Sort by confidence
        discovered_vendors.sort(key=lambda x: x.confidence, reverse=True)

        logger.info(
            f"Workflow 3 complete: {len(discovered_vendors)} new vendors discovered, "
            f"{len(known_vendors_found)} known vendors confirmed"
        )

        return {
            "account": account_name,
            "workflow": "discover_unknown_vendors",
            "discovered_vendors": discovered_vendors,
            "new_vendors_count": len(discovered_vendors),
            "known_vendors_found": len(known_vendors_found),
            "known_vendors_detail": list(known_vendors_found.keys()),
            "saved_to_notion": saved_to_notion,
            "added_to_runtime": added_to_runtime,
            "search_results_analyzed": len(all_results),
            "category_summary": self._summarize_by_category(discovered_vendors)
        }

    def _summarize_by_category(self, vendors: List[DiscoveredVendor]) -> Dict[str, int]:
        """Summarize vendors by category."""
        summary: Dict[str, int] = {}
        for v in vendors:
            cat = v.category
            summary[cat] = summary.get(cat, 0) + 1
        return summary

    def _save_discovered_vendor_to_notion(self, vendor: DiscoveredVendor, account_name: str):
        """Save a discovered vendor to Notion Partnerships database."""
        if not self._notion_client:
            return

        partnership_data = {
            'partner_name': vendor.vendor_name,
            'partnership_type': vendor.category,
            'category': vendor.category,
            'relevance_score': int(vendor.confidence * 100),
            'confidence_score': int(vendor.confidence * 100),
            'context': '; '.join(vendor.evidence_snippets[:2]) if vendor.evidence_snippets else '',
            'relationship_evidence': '; '.join(vendor.evidence_snippets[:2]) if vendor.evidence_snippets else '',
            'source_url': vendor.evidence_urls[0] if vendor.evidence_urls else None,
            'evidence_url': vendor.evidence_urls[0] if vendor.evidence_urls else None,
            'is_discovered': True,
            'discovered_from_account': account_name,
            'strategic_purpose': vendor.strategic_purpose,
            'recommended_action': vendor.recommended_action
        }

        self._notion_client.save_partnerships([partnership_data], account_name)

    def get_all_vendors(self) -> Dict[str, List[str]]:
        """Get the complete dynamic vendor list (KNOWN + discovered)."""
        return dict(self._dynamic_vendors)

    def get_vendor_count(self) -> int:
        """Get total count of vendors in dynamic list."""
        return sum(len(v) for v in self._dynamic_vendors.values())

    def discover_relationships(
        self,
        vendors: List[str],
        customers: List[str],
        fit_weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Discover vendor-customer relationships from public data.

        Args:
            vendors: List of vendor company names to check
            customers: List of target account (customer) names
            fit_weights: Optional per-vendor weights (0.5-1.5), default=1.0

        Returns:
            {
                "signals": List[VendorCustomerSignal],
                "vendor_scores": List[VendorIntroScore],
                "search_failures": List[Dict]  # Failed searches
            }
        """
        logger.info(f"Discovering relationships: {len(vendors)} vendors x {len(customers)} customers")

        if not self.brave_api_key:
            return {
                "signals": [],
                "vendor_scores": [],
                "search_failures": [{"reason": "No BRAVE_API_KEY configured"}]
            }

        fit_weights = fit_weights or {}
        all_signals: List[VendorCustomerSignal] = []
        search_failures: List[Dict] = []

        # Search for each vendor-customer pair
        for vendor in vendors:
            for customer in customers:
                try:
                    result = self._search_vendor_customer(vendor, customer)
                    all_signals.extend(result.get('signals', []))
                    # Track any Brave API errors
                    for err in result.get('errors', []):
                        search_failures.append({
                            "vendor": vendor,
                            "customer": customer,
                            "error": err.get('error'),
                            "error_code": err.get('error_code'),
                            "retry_after": err.get('retry_after')
                        })
                except Exception as e:
                    logger.warning(f"Search failed for {vendor}/{customer}: {e}")
                    search_failures.append({
                        "vendor": vendor,
                        "customer": customer,
                        "error": str(e)
                    })

        # Deduplicate signals by URL
        unique_signals = self._deduplicate_signals(all_signals)

        # Calculate vendor intro scores
        vendor_scores = self._calculate_vendor_scores(unique_signals, fit_weights)

        logger.info(f"Found {len(unique_signals)} unique signals across {len(vendor_scores)} vendors")

        return {
            "signals": unique_signals,
            "vendor_scores": vendor_scores,
            "search_failures": search_failures
        }

    def discover_for_account(
        self,
        account_name: str,
        candidate_vendors: Optional[List[str]] = None
    ) -> Dict:
        """
        WORKFLOW 1: Discover vendor relationships for a single target account.
        Uses either provided vendors or default infrastructure/tech vendors.

        Args:
            account_name: The target account to research
            candidate_vendors: Optional list of vendors to check

        Returns:
            Discovery results with signals and vendor scores
        """
        # Default vendor list if not provided (common datacenter/infrastructure vendors)
        if not candidate_vendors:
            candidate_vendors = self._get_default_vendor_list()

        return self.discover_relationships(
            vendors=candidate_vendors,
            customers=[account_name]
        )

    def discover_account_vendors(self, account_name: str) -> Dict:
        """
        WORKFLOW 2: Account-centric vendor discovery.
        Discovers WHO the vendors are for a target account without prior knowledge.

        This is fundamentally different from Workflow 1:
        - Workflow 1: "Does vendor X work with account Y?" (need to know vendors)
        - Workflow 2: "Who are account Y's vendors?" (discover vendors)

        Args:
            account_name: The target account to research

        Returns:
            {
                "account": str,
                "discovered_vendors": List[DiscoveredVendor],
                "vendors_by_category": Dict[str, List[DiscoveredVendor]],
                "search_results_analyzed": int,
                "raw_evidence": List[Dict]  # For debugging/transparency
            }
        """
        logger.info(f"Discovering vendors for account: {account_name}")

        if not self.brave_api_key:
            return {
                "account": account_name,
                "discovered_vendors": [],
                "vendors_by_category": {},
                "search_results_analyzed": 0,
                "error": "No BRAVE_API_KEY configured"
            }

        # Collect all search results
        all_results: List[Dict] = []
        search_errors: List[Dict] = []  # Track any API errors

        # Run account-centric searches
        for template in self.VENDOR_DISCOVERY_TEMPLATES:
            query = template.format(account=account_name)

            # Check cache
            cache_key = f"discovery:{query.lower()}"
            if cache_key in self._search_cache:
                results = self._search_cache[cache_key]
            else:
                response = self._brave_search(query)
                results = response.get('results', [])
                self._search_cache[cache_key] = results
                # Track errors for surfacing to dashboard
                if response.get('error'):
                    search_errors.append({
                        'query': query,
                        'error': response['error'],
                        'error_code': response.get('error_code'),
                        'retry_after': response.get('retry_after')
                    })

            # Tag results with the search query
            for r in results:
                r['_search_query'] = query
            all_results.extend(results)

        # Extract vendors from results
        vendor_mentions: Dict[str, Dict] = {}  # vendor_name -> {count, urls, snippets, category}

        for result in all_results:
            title = result.get('title', '')
            description = result.get('description', '')
            url = result.get('url', '')
            text = f"{title} {description}".lower()

            # Skip if account not mentioned (likely irrelevant)
            account_lower = account_name.lower()
            account_normalized = self._normalize_company(account_name)
            if account_lower not in text and account_normalized not in text:
                continue

            # Extract vendors from known vendor list
            for category, vendors in self.KNOWN_VENDORS.items():
                for vendor in vendors:
                    vendor_lower = vendor.lower()
                    vendor_normalized = self._normalize_company(vendor)

                    # Check if vendor is mentioned
                    if vendor_lower in text or vendor_normalized in text:
                        if vendor not in vendor_mentions:
                            vendor_mentions[vendor] = {
                                'count': 0,
                                'urls': [],
                                'snippets': [],
                                'category': category
                            }

                        vendor_mentions[vendor]['count'] += 1
                        if url and url not in vendor_mentions[vendor]['urls']:
                            vendor_mentions[vendor]['urls'].append(url)
                        if description:
                            snippet = description[:200]
                            if snippet not in vendor_mentions[vendor]['snippets']:
                                vendor_mentions[vendor]['snippets'].append(snippet)

        # Convert to DiscoveredVendor objects
        discovered_vendors: List[DiscoveredVendor] = []
        vendors_by_category: Dict[str, List[DiscoveredVendor]] = {}

        for vendor_name, data in vendor_mentions.items():
            # Calculate confidence based on mention count and evidence quality
            confidence = self._calculate_discovery_confidence(
                mention_count=data['count'],
                url_count=len(data['urls']),
                snippet_count=len(data['snippets'])
            )

            # Detect relationship type from snippets
            relationship_type = self._detect_relationship_type(
                account_name, vendor_name, data['snippets']
            )

            # Get strategic metadata for this category
            category_meta = self.CATEGORY_METADATA.get(data['category'], {})

            vendor = DiscoveredVendor(
                vendor_name=vendor_name,
                category=data['category'],
                mention_count=data['count'],
                evidence_urls=data['urls'][:5],  # Top 5 URLs
                evidence_snippets=data['snippets'][:3],  # Top 3 snippets
                relationship_type=relationship_type,
                confidence=confidence,
                strategic_purpose=category_meta.get('strategic_purpose', 'unknown'),
                recommended_action=category_meta.get('action', '')
            )

            discovered_vendors.append(vendor)

            # Group by category
            if data['category'] not in vendors_by_category:
                vendors_by_category[data['category']] = []
            vendors_by_category[data['category']].append(vendor)

        # Sort by confidence
        discovered_vendors.sort(key=lambda x: x.confidence, reverse=True)

        # Sort each category by confidence
        for category in vendors_by_category:
            vendors_by_category[category].sort(key=lambda x: x.confidence, reverse=True)

        logger.info(f"Discovered {len(discovered_vendors)} vendors for {account_name}")

        return {
            "account": account_name,
            "discovered_vendors": discovered_vendors,
            "vendors_by_category": vendors_by_category,
            "search_results_analyzed": len(all_results),
            "raw_evidence": [
                {"url": r.get('url'), "title": r.get('title')}
                for r in all_results[:20]  # Top 20 for transparency
            ]
        }

    def _calculate_discovery_confidence(
        self,
        mention_count: int,
        url_count: int,
        snippet_count: int
    ) -> float:
        """
        Calculate confidence score (0-1) for a discovered vendor.
        Higher mentions across more sources = higher confidence.
        """
        # Base score from mention count (logarithmic scaling)
        if mention_count == 0:
            return 0.0

        import math
        base_score = min(0.5, math.log10(mention_count + 1) * 0.3)

        # Boost from multiple sources (unique URLs)
        source_boost = min(0.3, url_count * 0.1)

        # Boost from having snippets/context
        snippet_boost = min(0.2, snippet_count * 0.07)

        return min(1.0, base_score + source_boost + snippet_boost)

    def _detect_relationship_type(
        self,
        account: str,
        vendor: str,
        snippets: List[str]
    ) -> str:
        """
        Detect the type of relationship from evidence snippets.
        Returns: customer, partner, integration, competitor, or unknown
        """
        text = " ".join(snippets).lower()
        account_lower = account.lower()
        vendor_lower = vendor.lower()

        # Customer indicators (account uses/buys from vendor)
        customer_patterns = [
            f"{account_lower} uses {vendor_lower}",
            f"{account_lower} deploys {vendor_lower}",
            f"{account_lower} selects {vendor_lower}",
            f"{account_lower} runs on {vendor_lower}",
            f"powered by {vendor_lower}",
            f"{vendor_lower} customer",
            "case study", "success story"
        ]

        # Partner indicators (mutual relationship)
        partner_patterns = [
            "partnership", "partner with", "collaborate",
            "joint", "alliance", "together"
        ]

        # Integration indicators
        integration_patterns = [
            "integration", "integrates with", "connector",
            "plugin", "api", "interoperability"
        ]

        # Check patterns
        for pattern in customer_patterns:
            if pattern in text:
                return "customer"

        for pattern in partner_patterns:
            if pattern in text:
                return "partner"

        for pattern in integration_patterns:
            if pattern in text:
                return "integration"

        return "unknown"

    def _get_default_vendor_list(self) -> List[str]:
        """Default list of vendors relevant to Verdigris ICP."""
        return [
            # Power & Energy
            "Schneider Electric",
            "Eaton",
            "Vertiv",
            "ABB",
            "Siemens",

            # Cooling & HVAC
            "Carrier",
            "Trane",
            "Johnson Controls",
            "Daikin",

            # Infrastructure & Monitoring
            "Nlyte",
            "Sunbird DCIM",
            "Panduit",
            "Raritan",

            # Cloud & Compute
            "NVIDIA",
            "Dell Technologies",
            "HPE",
            "Supermicro",

            # Networking
            "Cisco",
            "Arista",
            "Juniper",

            # Sustainability
            "Envizi",
            "Salesforce Net Zero",
            "Microsoft Sustainability"
        ]

    def _search_vendor_customer(
        self,
        vendor: str,
        customer: str
    ) -> Dict:
        """
        Search for relationship signals between a vendor and customer.

        Returns:
            Dict with:
                - 'signals': List[VendorCustomerSignal] - discovered signals
                - 'errors': List[Dict] - any search errors encountered
        """
        signals = []
        search_errors = []

        # Try multiple search templates
        templates_to_try = self.SEARCH_TEMPLATES[:4]  # Limit to avoid rate limiting

        for template in templates_to_try:
            query = template.format(vendor=vendor, customer=customer)

            # Check cache
            cache_key = query.lower()
            if cache_key in self._search_cache:
                results = self._search_cache[cache_key]
            else:
                response = self._brave_search(query)
                results = response.get('results', [])
                self._search_cache[cache_key] = results
                # Track errors
                if response.get('error'):
                    search_errors.append({
                        'query': query,
                        'error': response['error'],
                        'error_code': response.get('error_code'),
                        'retry_after': response.get('retry_after')
                    })

            # Parse results into signals
            for result in results:
                signal = self._parse_result_to_signal(result, vendor, customer)
                if signal:
                    signals.append(signal)

        return {'signals': signals, 'errors': search_errors}

    def _brave_search(self, query: str) -> Dict:
        """
        Execute Brave Search API request with retry logic for rate limiting.

        Uses exponential backoff when rate limited (429 errors).

        Returns:
            Dict with keys:
                - 'results': List[Dict] - search results (empty if error)
                - 'error': Optional[str] - error message if failed
                - 'error_code': Optional[str] - error code for dashboard display
                - 'retry_after': Optional[int] - seconds to wait before retry (for rate limits)
        """
        last_error = None
        last_error_code = None

        for attempt in range(self.max_retries):
            self._apply_rate_limit()

            try:
                response = requests.get(
                    self.brave_base_url,
                    params={
                        'q': query,
                        'count': 10,
                        'freshness': 'py'  # Past year
                    },
                    headers={
                        'X-Subscription-Token': self.brave_api_key,
                        'Accept': 'application/json'
                    },
                    timeout=15
                )

                if response.status_code == 429:
                    # Rate limited - apply exponential backoff
                    backoff_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                    logger.warning(f"Brave API rate limited (429). Waiting {backoff_time}s before retry {attempt + 1}/{self.max_retries}")
                    last_error = f"Rate limited by Brave API. Retried {attempt + 1}/{self.max_retries} times."
                    last_error_code = "BRAVE_RATE_LIMITED"
                    time.sleep(backoff_time)
                    continue

                if response.status_code != 200:
                    logger.warning(f"Brave search failed: {response.status_code}")
                    return {
                        'results': [],
                        'error': f"Brave API returned status {response.status_code}",
                        'error_code': f"BRAVE_HTTP_{response.status_code}"
                    }

                data = response.json()

                # Combine news and web results
                results = []
                results.extend(data.get('news', {}).get('results', []))
                results.extend(data.get('web', {}).get('results', []))

                return {'results': results, 'error': None, 'error_code': None}

            except requests.exceptions.Timeout:
                logger.warning(f"Brave search timeout for query: {query[:50]}...")
                return {
                    'results': [],
                    'error': "Brave API request timed out after 15 seconds",
                    'error_code': "BRAVE_TIMEOUT"
                }
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Brave search connection error: {e}")
                return {
                    'results': [],
                    'error': "Could not connect to Brave API",
                    'error_code': "BRAVE_CONNECTION_ERROR"
                }
            except Exception as e:
                logger.warning(f"Brave search error: {e}")
                return {
                    'results': [],
                    'error': f"Unexpected error: {str(e)}",
                    'error_code': "BRAVE_UNKNOWN_ERROR"
                }

        # If we exhausted all retries due to rate limiting
        logger.warning(f"Brave search failed after {self.max_retries} retries due to rate limiting")
        return {
            'results': [],
            'error': last_error or f"Search failed after {self.max_retries} retries",
            'error_code': last_error_code or "BRAVE_MAX_RETRIES",
            'retry_after': 60  # Suggest waiting 60 seconds before trying again
        }

    def _parse_result_to_signal(
        self,
        result: Dict,
        vendor: str,
        customer: str
    ) -> Optional[VendorCustomerSignal]:
        """Parse a search result into a VendorCustomerSignal."""
        try:
            title = result.get('title', '')
            description = result.get('description', '')
            url = result.get('url', '')
            age = result.get('age', '')

            if not url:
                return None

            # Combine title and description for analysis
            text = f"{title} {description}".lower()

            # Check if both vendor and customer are mentioned
            vendor_mentioned = vendor.lower() in text or self._normalize_company(vendor) in text
            customer_mentioned = customer.lower() in text or self._normalize_company(customer) in text

            if not (vendor_mentioned and customer_mentioned):
                # Weak signal - only one party mentioned
                return None

            # Detect signal type
            signal_type = self._detect_signal_type(text, url)

            # Calculate signal strength
            signal_strength = self._calculate_signal_strength(
                text=text,
                url=url,
                signal_type=signal_type,
                title=title
            )

            # Check for co-branding and deployment indicators
            is_cobranded = self._check_cobranding(text, vendor, customer)
            is_deployment = self._check_deployment(text)

            # Extract people if mentioned
            people = self._extract_people(description)

            return VendorCustomerSignal(
                vendor=vendor,
                customer=customer,
                signal_type=signal_type,
                signal_strength=signal_strength,
                evidence_url=url,
                evidence_title=title,
                evidence_snippet=description[:300] if description else "",
                recency=age,
                people_involved=people,
                is_cobranded=is_cobranded,
                is_deployment_story=is_deployment,
                customer_named_explicitly=customer_mentioned
            )

        except Exception as e:
            logger.warning(f"Error parsing result: {e}")
            return None

    def _detect_signal_type(self, text: str, url: str) -> str:
        """Detect the type of relationship signal."""
        for signal_type, patterns in self.SIGNAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return signal_type

        # Default based on URL patterns
        url_lower = url.lower()
        if "/case-stud" in url_lower or "/customer" in url_lower:
            return "case_study"
        elif "/press" in url_lower or "/news" in url_lower:
            return "joint_pr"
        elif "/integrat" in url_lower or "/partner" in url_lower:
            return "integration"

        return "logo_mention"  # Default/weakest

    def _calculate_signal_strength(
        self,
        text: str,
        url: str,
        signal_type: str,
        title: str
    ) -> int:
        """
        Calculate signal strength 1-5 per the rubric:
        1: Logo/mention only
        2: Customer referenced but not formal story
        3: Named case study, webinar, clear narrative
        4: Joint PR, integration launch, multi-party collab
        5: Multiple assets or contract award with details
        """
        strength = 1  # Start at logo mention

        # Check for formal story indicators
        formal_story_patterns = [
            r"case study", r"success story", r"customer story",
            r"how .* uses", r"partnership announcement"
        ]

        contract_patterns = [
            r"contract", r"awarded", r"procurement",
            r"million", r"multi-year", r"selected"
        ]

        collab_patterns = [
            r"joint", r"collaboration", r"together",
            r"co-develop", r"alliance"
        ]

        # Check URL for high-value pages
        url_lower = url.lower()
        is_case_study_page = "/case-stud" in url_lower or "/customer-stor" in url_lower
        is_press_page = "/press" in url_lower or "/news" in url_lower or "/announcement" in url_lower

        # Score based on evidence
        if any(re.search(p, text, re.IGNORECASE) for p in contract_patterns):
            strength = 5  # Contract award
        elif is_case_study_page:
            strength = max(strength, 3)  # Named case study page
        elif any(re.search(p, text, re.IGNORECASE) for p in formal_story_patterns):
            strength = max(strength, 3)  # Formal story
        elif is_press_page or any(re.search(p, text, re.IGNORECASE) for p in collab_patterns):
            strength = max(strength, 4)  # Joint PR or collaboration
        elif signal_type in ["case_study", "webinar", "conference"]:
            strength = max(strength, 3)  # Type indicates formal relationship
        elif signal_type in ["joint_pr", "integration"]:
            strength = max(strength, 4)  # Strong signal types
        elif signal_type != "logo_mention":
            strength = max(strength, 2)  # Some evidence beyond logo

        return min(5, strength)

    def _check_cobranding(self, text: str, vendor: str, customer: str) -> bool:
        """Check if content appears co-branded."""
        cobranding_indicators = [
            f"{vendor.lower()} and {customer.lower()}",
            f"{customer.lower()} and {vendor.lower()}",
            "joint", "together", "partnership", "collaboration"
        ]
        return any(ind in text for ind in cobranding_indicators)

    def _check_deployment(self, text: str) -> bool:
        """Check if content describes a deployment."""
        deployment_patterns = [
            r"deploy", r"implement", r"install",
            r"rollout", r"goes live", r"launch"
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in deployment_patterns)

    def _extract_people(self, text: str) -> List[str]:
        """Extract people names/titles from text (basic extraction)."""
        # Look for common title patterns
        title_patterns = [
            r"([A-Z][a-z]+ [A-Z][a-z]+),? (?:CEO|CTO|VP|Director|Manager|Head|Chief)",
            r"(?:CEO|CTO|VP|Director) ([A-Z][a-z]+ [A-Z][a-z]+)",
        ]

        people = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            people.extend(matches)

        return list(set(people))[:5]  # Dedupe and limit

    def _normalize_company(self, name: str) -> str:
        """Normalize company name for matching."""
        # Remove common suffixes
        suffixes = [" inc", " corp", " llc", " ltd", " co", " company"]
        normalized = name.lower()
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        return normalized.strip()

    def _deduplicate_signals(
        self,
        signals: List[VendorCustomerSignal]
    ) -> List[VendorCustomerSignal]:
        """Deduplicate signals by URL, keeping highest strength."""
        url_to_signal: Dict[str, VendorCustomerSignal] = {}

        for signal in signals:
            url = signal.evidence_url
            if url not in url_to_signal:
                url_to_signal[url] = signal
            elif signal.signal_strength > url_to_signal[url].signal_strength:
                url_to_signal[url] = signal

        return list(url_to_signal.values())

    def _calculate_vendor_scores(
        self,
        signals: List[VendorCustomerSignal],
        fit_weights: Dict[str, float]
    ) -> List[VendorIntroScore]:
        """
        Calculate Vendor Intro Power Score:
        IntroScore = CoverageCount * AvgSignalStrength * FitWeight
        """
        # Group signals by vendor
        vendor_signals: Dict[str, Dict[str, List[VendorCustomerSignal]]] = {}

        for signal in signals:
            vendor = signal.vendor
            customer = signal.customer

            if vendor not in vendor_signals:
                vendor_signals[vendor] = {}
            if customer not in vendor_signals[vendor]:
                vendor_signals[vendor][customer] = []

            vendor_signals[vendor][customer].append(signal)

        # Calculate scores
        scores = []
        for vendor, customer_map in vendor_signals.items():
            coverage_count = len(customer_map)

            # Calculate average strength across all signals
            all_strengths = [
                s.signal_strength
                for signals_list in customer_map.values()
                for s in signals_list
            ]
            avg_strength = sum(all_strengths) / len(all_strengths) if all_strengths else 0

            # Get fit weight (default 1.0)
            fit_weight = fit_weights.get(vendor, 1.0)

            # Calculate intro score
            intro_score = coverage_count * avg_strength * fit_weight

            # Collect intro candidates from people mentioned
            intro_candidates = []
            for signals_list in customer_map.values():
                for s in signals_list:
                    for person in s.people_involved:
                        intro_candidates.append({
                            "name": person,
                            "context": s.evidence_title,
                            "url": s.evidence_url
                        })

            scores.append(VendorIntroScore(
                vendor_name=vendor,
                intro_score=round(intro_score, 2),
                coverage_count=coverage_count,
                avg_signal_strength=round(avg_strength, 2),
                fit_weight=fit_weight,
                customer_signals=customer_map,
                intro_candidates=intro_candidates[:10]  # Top 10 candidates
            ))

        # Sort by intro score descending
        scores.sort(key=lambda x: x.intro_score, reverse=True)

        return scores

    def _apply_rate_limit(self):
        """Apply rate limiting between API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def to_partnership_properties(
        self,
        signal: VendorCustomerSignal,
        account_page_id: Optional[str] = None,
        is_verdigris_partner: bool = False
    ) -> Dict:
        """
        Convert a signal to Notion Partnership properties format.
        Ready to save to Partnerships database with Account relation.
        """
        # Map signal strength to relationship depth
        depth_map = {1: "Logo Only", 2: "Mentioned", 3: "Case Study", 4: "Deep Integration", 5: "Contract Award"}

        properties = {
            "Partner Name": {
                "title": [{"text": {"content": signal.vendor}}]
            },
            "Partnership Type": {
                "select": {"name": signal.signal_type.replace("_", " ").title()}
            },
            "Relevance Score": {
                "number": signal.signal_strength * 20  # Convert 1-5 to 20-100
            },
            "Relationship Depth": {
                "select": {"name": depth_map.get(signal.signal_strength, "Mentioned")}
            },
            "Context": {
                "rich_text": [{"text": {"content": signal.evidence_snippet[:500]}}]
            },
            "Evidence URL": {
                "url": signal.evidence_url
            },
            "Is Verdigris Partner": {
                "checkbox": is_verdigris_partner
            }
        }

        # Add account relation if provided
        if account_page_id:
            properties["Account"] = {
                "relation": [{"id": account_page_id}]
            }

        return properties


# Export singleton instance
vendor_relationship_discovery = VendorRelationshipDiscovery()
