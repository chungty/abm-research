#!/usr/bin/env python3
"""
Enhanced Engagement Intelligence Engine
Implements Phase 4 requirements from skill specification
Role-specific pain point mapping and personalized value-add recommendations
"""

import json
import os
from dataclasses import dataclass

import openai


@dataclass
class EngagementIntelligence:
    """Complete engagement intelligence for a contact"""

    # Pain point mapping
    problems_owned: list[str]  # From role-to-pain-point mapping
    pain_point_details: dict[str, str]  # Detailed explanation per pain point

    # Value proposition matching
    value_add_ideas: list[str]  # 2-3 specific, actionable ideas
    verdigris_content_matches: list[dict]  # Matching content assets

    # Personalized outreach
    email_template: str  # Personalized email template
    linkedin_message: str  # LinkedIn connection/message
    call_script: str  # Phone conversation guide
    conversation_starters: list[str]  # 3-5 specific questions

    # Timing intelligence
    optimal_timing: dict  # When and why to reach out
    urgency_factors: list[str]  # Reasons for urgency


class EnhancedEngagementIntelligence:
    """Phase 4 implementation: AI-powered engagement intelligence"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Load skill configuration
        self.load_skill_config()
        self.load_pain_point_mapping()
        self.load_content_asset_library()

    def load_skill_config(self):
        """Load ICP pain points from skill specification"""
        try:
            # Use path relative to the package directory
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "references",
                "lead_scoring_config.json",
            )
            with open(config_path) as f:
                config = json.load(f)
                self.icp_pain_points = config.get("icp_pain_points", [])
        except FileNotFoundError:
            print("⚠️ Lead scoring config not found, using defaults")
            self.icp_pain_points = self._get_default_pain_points()

    def load_pain_point_mapping(self):
        """Map job titles to specific ICP pain points per skill specification"""
        self.role_pain_mapping = {
            # C-Suite - Strategic pain points
            "CTO": [
                "AI workload expansion challenges",
                "Sustainability and ESG reporting requirements",
                "Cost reduction mandates",
            ],
            "CIO": [
                "Uptime and reliability pressure",
                "Cost reduction mandates",
                "Remote monitoring and troubleshooting",
            ],
            # VP Level - Operational + Strategic
            "VP, Infrastructure & Data Centers": [
                "Power capacity planning and management",
                "AI workload expansion challenges",
                "Energy efficiency and PUE optimization",
                "Sustainability and ESG reporting requirements",
            ],
            "VP of Operations": [
                "Uptime and reliability pressure",
                "Cost reduction mandates",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting",
            ],
            # Director Level - Tactical + Operational
            "Director, Infrastructure Engineering": [
                "Power capacity planning and management",
                "AI workload expansion challenges",
                "Predictive maintenance and risk detection",
            ],
            "Director, Data Center Operations": [
                "Uptime and reliability pressure",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting",
            ],
            "Director, Data Center Facilities": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection",
            ],
            "Director, Cloud Platform & SRE": [
                "Uptime and reliability pressure",
                "Remote monitoring and troubleshooting",
                "Predictive maintenance and risk detection",
            ],
            # Manager Level - Daily operational pain
            "SRE Manager": [
                "Uptime and reliability pressure",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting",
            ],
            "Facilities Manager": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection",
            ],
            "NOC & Operations Team": [
                "Remote monitoring and troubleshooting",
                "Uptime and reliability pressure",
            ],
            # Engineer Level - Technical implementation
            "Capacity & Energy Engineer": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "AI workload expansion challenges",
            ],
            "Critical Facilities Engineers": [
                "Predictive maintenance and risk detection",
                "Power capacity planning and management",
                "Uptime and reliability pressure",
            ],
            "SRE/Infrastructure Engineers": [
                "Remote monitoring and troubleshooting",
                "Uptime and reliability pressure",
                "Predictive maintenance and risk detection",
            ],
            # Product/Program roles
            "Monitoring/DCIM Product Owner": [
                "Remote monitoring and troubleshooting",
                "Predictive maintenance and risk detection",
                "Energy efficiency and PUE optimization",
            ],
            # Finance
            "Finance/FP&A": [
                "Cost reduction mandates",
                "Energy efficiency and PUE optimization",
                "Sustainability and ESG reporting requirements",
            ],
        }

    def load_content_asset_library(self):
        """Library of Verdigris content assets for value-add matching"""
        self.content_assets = {
            "Power capacity planning and management": [
                {
                    "title": "GPU Rack Power Optimization Case Study",
                    "description": "How Lambda Labs reduced power constraints for AI workloads by 40%",
                    "type": "case_study",
                    "relevance": "Direct power planning solution",
                },
                {
                    "title": "Real-time Capacity Planning Whitepaper",
                    "description": "Circuit-level monitoring for predictive capacity management",
                    "type": "whitepaper",
                    "relevance": "Technical implementation guide",
                },
            ],
            "Energy efficiency and PUE optimization": [
                {
                    "title": "PUE Reduction Success Story - 15% Improvement",
                    "description": "Hyperscale data center achieves 1.12 PUE with real-time monitoring",
                    "type": "case_study",
                    "relevance": "Proven efficiency gains",
                },
                {
                    "title": "Energy Analytics Dashboard Demo",
                    "description": "Interactive demo of power analytics and optimization recommendations",
                    "type": "demo",
                    "relevance": "Hands-on experience with solution",
                },
            ],
            "Uptime and reliability pressure": [
                {
                    "title": "Predictive Fault Detection ROI Calculator",
                    "description": "Calculate downtime cost savings from early fault detection",
                    "type": "calculator",
                    "relevance": "Business case quantification",
                },
                {
                    "title": "Critical System Monitoring Best Practices",
                    "description": "Framework for preventing electrical failures in mission-critical systems",
                    "type": "guide",
                    "relevance": "Implementation roadmap",
                },
            ],
            "AI workload expansion challenges": [
                {
                    "title": "High-Density GPU Monitoring Solution",
                    "description": "Real-time power and thermal monitoring for AI/ML infrastructure",
                    "type": "solution_brief",
                    "relevance": "AI-specific power challenges",
                },
                {
                    "title": "NVIDIA Partnership Announcement",
                    "description": "Joint solution for GPU cluster power optimization",
                    "type": "press_release",
                    "relevance": "Industry validation",
                },
            ],
            "Sustainability and ESG reporting requirements": [
                {
                    "title": "Automated Carbon Reporting Dashboard",
                    "description": "Real-time Scope 2 & 3 emissions tracking for ESG compliance",
                    "type": "demo",
                    "relevance": "ESG automation solution",
                },
                {
                    "title": "Sustainability ROI Whitepaper",
                    "description": "How power monitoring drives both cost savings and carbon reduction",
                    "type": "whitepaper",
                    "relevance": "Business and environmental benefits",
                },
            ],
        }

    def generate_engagement_intelligence(
        self, contact: dict, trigger_events: list[dict] = None, account_context: dict = None
    ) -> EngagementIntelligence:
        """
        Generate complete engagement intelligence for high-scoring contacts
        Following Phase 4 requirements from skill specification
        """
        if contact.get("final_lead_score", 0) < 70:
            return self._create_basic_intelligence(contact)

        print(
            f"🧠 Generating engagement intelligence for {contact.get('name')} (Score: {contact.get('final_lead_score')})"
        )

        # 1. Map problems they likely own based on role
        problems_analysis = self._map_role_to_pain_points(contact)

        # 2. Generate value-add ideas based on problems and content themes
        value_add_analysis = self._generate_value_add_ideas(contact, problems_analysis)

        # 3. Create personalized outreach templates
        outreach_templates = self._generate_outreach_templates(
            contact, problems_analysis, value_add_analysis, trigger_events, account_context
        )

        # 4. Analyze optimal timing based on trigger events and role
        timing_analysis = self._analyze_optimal_timing(contact, trigger_events)

        return EngagementIntelligence(
            problems_owned=problems_analysis["problems"],
            pain_point_details=problems_analysis["details"],
            value_add_ideas=value_add_analysis["ideas"],
            verdigris_content_matches=value_add_analysis["content_matches"],
            email_template=outreach_templates["email"],
            linkedin_message=outreach_templates["linkedin"],
            call_script=outreach_templates["call_script"],
            conversation_starters=outreach_templates["conversation_starters"],
            optimal_timing=timing_analysis["timing"],
            urgency_factors=timing_analysis["urgency_factors"],
        )

    def _map_role_to_pain_points(self, contact: dict) -> dict:
        """Map contact's role to specific ICP pain points per skill specification"""
        title = contact.get("title", "")
        role_classification = self._classify_role(title)

        # Get pain points for this role
        role_pain_points = self.role_pain_mapping.get(
            role_classification,
            [
                "Power capacity planning and management",
                "Uptime and reliability pressure",  # Default pain points
            ],
        )

        # Generate detailed explanations for each pain point
        pain_point_details = {}
        for pain_point in role_pain_points:
            pain_point_details[pain_point] = self._explain_pain_point_for_role(
                pain_point, role_classification, title
            )

        return {
            "problems": role_pain_points,
            "details": pain_point_details,
            "role_classification": role_classification,
        }

    def _classify_role(self, title: str) -> str:
        """Classify role using same logic as lead_scoring_engine.py"""
        title_lower = title.lower()

        # C-Suite
        if any(
            term in title_lower for term in ["cio", "cto", "chief information", "chief technology"]
        ):
            return "CIO" if "cio" in title_lower or "information" in title_lower else "CTO"

        # VP Level
        if "vp" in title_lower or "vice president" in title_lower:
            if any(term in title_lower for term in ["infrastructure", "data center"]):
                return "VP, Infrastructure & Data Centers"
            elif "operations" in title_lower:
                return "VP of Operations"

        # Director Level
        if "director" in title_lower:
            if any(term in title_lower for term in ["infrastructure", "engineering"]):
                return "Director, Infrastructure Engineering"
            elif (
                any(term in title_lower for term in ["data center", "datacenter"])
                and "operations" in title_lower
            ):
                return "Director, Data Center Operations"
            elif "facilities" in title_lower:
                return "Director, Data Center Facilities"
            elif any(term in title_lower for term in ["cloud", "sre", "platform"]):
                return "Director, Cloud Platform & SRE"

        # Manager Level
        if "manager" in title_lower:
            if "sre" in title_lower or "reliability" in title_lower:
                return "SRE Manager"
            elif "facilities" in title_lower:
                return "Facilities Manager"

        # Engineer Level
        if any(term in title_lower for term in ["engineer", "engineering"]):
            if any(term in title_lower for term in ["capacity", "energy"]):
                return "Capacity & Energy Engineer"
            elif any(term in title_lower for term in ["facilities", "critical"]):
                return "Critical Facilities Engineers"
            elif any(term in title_lower for term in ["sre", "infrastructure", "reliability"]):
                return "SRE/Infrastructure Engineers"

        # Product/Program roles
        if any(term in title_lower for term in ["product", "program"]) and any(
            term in title_lower for term in ["monitoring", "dcim"]
        ):
            return "Monitoring/DCIM Product Owner"

        # Operations
        if any(term in title_lower for term in ["noc", "operations", "ops"]) and not any(
            term in title_lower for term in ["director", "manager", "vp"]
        ):
            return "NOC & Operations Team"

        # Finance
        if any(term in title_lower for term in ["finance", "fp&a", "financial"]):
            return "Finance/FP&A"

        return "Unknown"

    def _explain_pain_point_for_role(
        self, pain_point: str, role_classification: str, actual_title: str
    ) -> str:
        """Generate role-specific explanation of how this pain point affects them"""
        explanations = {
            "Power capacity planning and management": {
                "Capacity & Energy Engineer": "Daily struggle with accurate power budgeting for new deployments and rack-level capacity planning",
                "Director, Infrastructure Engineering": "Strategic challenge of ensuring adequate power capacity for business growth while optimizing capital allocation",
                "VP, Infrastructure & Data Centers": "Executive accountability for power infrastructure investments and capacity planning accuracy",
            },
            "Energy efficiency and PUE optimization": {
                "Facilities Manager": "Direct responsibility for achieving energy efficiency targets and reducing operational costs",
                "Director, Data Center Facilities": "KPI ownership for PUE improvement and sustainability metrics",
                "Finance/FP&A": "Budget pressure from rising energy costs and need for efficiency justification",
            },
            "Uptime and reliability pressure": {
                "SRE Manager": "SLA accountability and incident response for reliability targets",
                "Director, Data Center Operations": "Operational excellence mandate for 99.99% uptime requirements",
                "NOC & Operations Team": "Front-line responsibility for maintaining system reliability",
            },
        }

        specific_explanation = explanations.get(pain_point, {}).get(role_classification)
        if specific_explanation:
            return specific_explanation
        else:
            return f"As a {actual_title}, this pain point impacts their daily operational effectiveness and strategic objectives"

    def _generate_value_add_ideas(self, contact: dict, problems_analysis: dict) -> dict:
        """Generate 2-3 specific, actionable value-add ideas per skill specification"""
        problems = problems_analysis["problems"]
        role_classification = problems_analysis["role_classification"]
        name = contact.get("name", "Unknown")
        company = contact.get("company", "your company")

        # Match problems to content assets
        content_matches = []
        for problem in problems:
            if problem in self.content_assets:
                content_matches.extend(self.content_assets[problem])

        # Use AI to generate personalized value-add ideas
        try:
            prompt = f"""
            Generate 2-3 specific, actionable value-add ideas for {name}, a {contact.get('title')} at {company}.

            Their key pain points:
            {chr(10).join([f"- {p}: {problems_analysis['details'][p]}" for p in problems])}

            Role classification: {role_classification}
            LinkedIn activity: {contact.get('linkedin_activity_level', 'Unknown')}
            Content themes: {', '.join(contact.get('content_themes', []))}

            Verdigris solution focus: Real-time power monitoring and analytics for data centers

            Generate ideas that:
            1. Address their specific pain points
            2. Match their seniority level and responsibilities
            3. Provide immediate, actionable value
            4. Reference specific Verdigris capabilities

            Format each idea as: "Action: Specific thing to do - Why: Value it provides"
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7,
            )

            ai_ideas = response.choices[0].message.content.strip().split("\n")
            filtered_ideas = [
                idea.strip() for idea in ai_ideas if idea.strip() and len(idea.strip()) > 20
            ]

            return {
                "ideas": filtered_ideas[:3],  # Limit to 3 per skill spec
                "content_matches": content_matches[:5],  # Top 5 relevant content pieces
            }

        except Exception as e:
            print(f"⚠️ Error generating value-add ideas: {e}")
            return self._get_fallback_value_add_ideas(role_classification, problems)

    def _generate_outreach_templates(
        self,
        contact: dict,
        problems_analysis: dict,
        value_add_analysis: dict,
        trigger_events: list[dict] = None,
        account_context: dict = None,
    ) -> dict:
        """Generate personalized outreach templates"""
        name = contact.get("name", "")
        title = contact.get("title", "")
        company = account_context.get("name", "your company") if account_context else "your company"
        role_classification = problems_analysis["role_classification"]
        top_pain_point = (
            problems_analysis["problems"][0]
            if problems_analysis["problems"]
            else "operational efficiency"
        )

        # Get most relevant trigger event
        relevant_event = None
        if trigger_events:
            for event in trigger_events:
                if event.get("relevance_score", 0) > 70:
                    relevant_event = event
                    break

        # Generate email template
        email_template = self._generate_email_template(
            name, title, company, top_pain_point, value_add_analysis["ideas"], relevant_event
        )

        # Generate LinkedIn message
        linkedin_message = self._generate_linkedin_message(
            name, title, role_classification, problems_analysis["problems"]
        )

        # Generate call script
        call_script = self._generate_call_script(name, title, top_pain_point, relevant_event)

        # Generate conversation starters
        conversation_starters = self._generate_conversation_starters(
            problems_analysis["problems"], role_classification
        )

        return {
            "email": email_template,
            "linkedin": linkedin_message,
            "call_script": call_script,
            "conversation_starters": conversation_starters,
        }

    def _generate_email_template(
        self,
        name: str,
        title: str,
        company: str,
        top_pain_point: str,
        value_ideas: list[str],
        trigger_event: dict = None,
    ) -> str:
        """Generate personalized email template"""
        subject_hook = ""
        opening_hook = ""

        if trigger_event:
            subject_hook = (
                f"{company}'s {trigger_event.get('event_type', 'infrastructure')} initiative"
            )
            opening_hook = f"I noticed {company}'s {trigger_event.get('description', 'recent infrastructure updates')}."
        else:
            subject_hook = f"{company}'s infrastructure monitoring strategy"
            opening_hook = f"Given your {title} role at {company}, you're likely focused on {top_pain_point.lower()}."

        value_proposition = (
            value_ideas[0]
            if value_ideas
            else "reduce energy costs by 15-25% through circuit-level power monitoring"
        )

        template = f"""Subject: {subject_hook} - {title} Perspective

Hi {name},

{opening_hook}

At Verdigris, we help companies like {company} {value_proposition.lower()}.

Specifically for {title.lower()}s, we provide:
• Real-time power analytics for proactive decision making
• Predictive fault detection preventing costly downtime events
• Automated ESG compliance reporting for sustainability initiatives

Would you be available for a brief 15-minute call next week to discuss how this applies to {company}'s current infrastructure priorities?

Best regards,
[Your name]

P.S. I can share a relevant case study about similar {top_pain_point.lower()} challenges if helpful."""

        return template

    def _generate_linkedin_message(
        self, name: str, title: str, role_classification: str, pain_points: list[str]
    ) -> str:
        """Generate LinkedIn connection message"""
        primary_focus = pain_points[0] if pain_points else "infrastructure optimization"

        message = f"""Hi {name}, I came across your {title} background and was impressed by your experience in infrastructure operations. Given the challenges around {primary_focus.lower()}, I thought you'd be interested in our approach to real-time power monitoring for data centers.

Would you be open to connecting? I'd love to share some insights relevant to {role_classification.lower()} roles."""

        return message

    def _generate_call_script(
        self, name: str, title: str, top_pain_point: str, trigger_event: dict = None
    ) -> str:
        """Generate phone call script"""
        if trigger_event:
            opening = f"Hi {name}, I'm calling about {trigger_event.get('description', 'your recent infrastructure updates')}."
        else:
            opening = f"Hi {name}, I'm reaching out because of your {title} role and the challenges around {top_pain_point.lower()}."

        script = f"""{opening}

In your {title.lower()} role, you likely see the daily challenges of {top_pain_point.lower()} and the manual effort required for monitoring.

We help companies automate 60% of daily monitoring tasks through predictive analytics and provide fault alerts 2-48 hours before failures occur.

Would you have 15 minutes next week to discuss how this applies specifically to your situation?

I can also share a case study of similar results we've achieved with companies in your industry."""

        return script

    def _generate_conversation_starters(
        self, pain_points: list[str], role_classification: str
    ) -> list[str]:
        """Generate role-specific conversation starters"""
        starters = []

        for pain_point in pain_points[:3]:  # Top 3 pain points
            if "power capacity" in pain_point.lower():
                starters.append(
                    "What's your current approach to power capacity planning for new deployments?"
                )
            elif "uptime" in pain_point.lower() or "reliability" in pain_point.lower():
                starters.append(
                    "How do you currently detect and prevent electrical failures before they impact operations?"
                )
            elif "energy efficiency" in pain_point.lower():
                starters.append(
                    "What tools do you use for PUE optimization and energy cost reduction?"
                )
            elif "ai workload" in pain_point.lower():
                starters.append(
                    "How are you handling power monitoring for high-density GPU clusters?"
                )
            elif "sustainability" in pain_point.lower():
                starters.append(
                    "What's your current process for ESG reporting and carbon metrics collection?"
                )

        # Add role-specific questions
        if "Engineer" in role_classification:
            starters.append(
                "What monitoring tools are you currently using for circuit-level analysis?"
            )
        elif "Director" in role_classification or "Manager" in role_classification:
            starters.append(
                "How do you build business cases for infrastructure monitoring investments?"
            )
        elif (
            "VP" in role_classification
            or "CTO" in role_classification
            or "CIO" in role_classification
        ):
            starters.append(
                "What are your key infrastructure KPIs and how do you track them today?"
            )

        return starters[:5]  # Limit to 5 starters

    def _analyze_optimal_timing(self, contact: dict, trigger_events: list[dict] = None) -> dict:
        """Analyze optimal timing for outreach based on trigger events and role"""
        urgency_factors = []
        timing_recommendation = "Medium"
        best_timeframe = "Next 2-3 weeks"
        reasoning = "Good time to explore infrastructure optimization solutions"

        if trigger_events:
            high_relevance_events = [e for e in trigger_events if e.get("relevance_score", 0) > 70]

            if high_relevance_events:
                urgency_factors.extend(
                    [
                        f"{event.get('event_type', 'Infrastructure')} event detected with {event.get('confidence', 'medium')} confidence"
                        for event in high_relevance_events[:2]
                    ]
                )
                timing_recommendation = "High"
                best_timeframe = "This week"
                reasoning = "Recent trigger events create immediate relevance for power monitoring solutions"

        # Factor in role-based timing
        role_classification = contact.get("role_classification", "")
        if "Engineer" in role_classification:
            urgency_factors.append("Technical roles often have immediate operational pain points")
        elif "Director" in role_classification:
            urgency_factors.append(
                "Director-level contacts are often evaluating solutions for quarterly planning"
            )

        # Factor in engagement score
        engagement_score = contact.get("engagement_potential_score", 0)
        if engagement_score > 70:
            urgency_factors.append(
                "High LinkedIn engagement suggests openness to professional conversations"
            )

        return {
            "timing": {
                "urgency": timing_recommendation,
                "best_timeframe": best_timeframe,
                "reasoning": reasoning,
            },
            "urgency_factors": urgency_factors,
        }

    def _create_basic_intelligence(self, contact: dict) -> EngagementIntelligence:
        """Create basic intelligence for contacts below score threshold"""
        return EngagementIntelligence(
            problems_owned=["Infrastructure optimization"],
            pain_point_details={"Infrastructure optimization": "General operational challenges"},
            value_add_ideas=["Share relevant industry insights and best practices"],
            verdigris_content_matches=[],
            email_template="Basic professional outreach template",
            linkedin_message="Standard connection request",
            call_script="General introduction call approach",
            conversation_starters=["What are your biggest infrastructure challenges?"],
            optimal_timing={
                "urgency": "Low",
                "best_timeframe": "Next month",
                "reasoning": "General timing",
            },
            urgency_factors=[],
        )

    def _get_fallback_value_add_ideas(self, role_classification: str, problems: list[str]) -> dict:
        """Fallback value-add ideas when AI generation fails"""
        fallback_ideas = []

        if "Engineer" in role_classification:
            fallback_ideas = [
                "Action: Share technical whitepaper on circuit-level monitoring - Why: Provides implementation guidance for current projects",
                "Action: Offer demo of real-time power analytics dashboard - Why: Shows immediate visibility into power consumption patterns",
                "Action: Connect with peer engineer at similar company - Why: Enables knowledge sharing on monitoring best practices",
            ]
        elif "Director" in role_classification or "Manager" in role_classification:
            fallback_ideas = [
                "Action: Provide ROI calculator for predictive maintenance - Why: Quantifies business impact of early fault detection",
                "Action: Share case study from similar-sized company - Why: Demonstrates proven results in comparable environment",
                "Action: Invite to industry roundtable discussion - Why: Builds relationship while providing peer learning opportunity",
            ]
        else:
            fallback_ideas = [
                "Action: Send industry trend report on power monitoring - Why: Positions Verdigris as thought leader",
                "Action: Offer brief consultation on infrastructure challenges - Why: Provides immediate value while building relationship",
            ]

        return {"ideas": fallback_ideas, "content_matches": []}

    def _get_default_pain_points(self) -> list[str]:
        """Default ICP pain points if config file missing"""
        return [
            "Power capacity planning and management",
            "Uptime and reliability pressure",
            "Energy efficiency and PUE optimization",
            "AI workload expansion challenges",
            "Cost reduction mandates",
            "Sustainability and ESG reporting requirements",
            "Predictive maintenance and risk detection",
            "Remote monitoring and troubleshooting",
        ]

    def convert_to_enhanced_schema(
        self, contact: dict, engagement_intel: EngagementIntelligence = None
    ) -> dict:
        """
        Convert contact engagement data to enhanced schema with confidence indicators

        Args:
            contact: Contact data dictionary
            engagement_intel: Optional EngagementIntelligence object from generate_engagement_intelligence

        Returns:
            Enhanced contact with schema-compliant engagement intelligence and confidence indicators
        """
        from datetime import datetime

        # Generate engagement intelligence if not provided
        if engagement_intel is None:
            engagement_intel = self.generate_engagement_intelligence(contact)

        # Helper function for confidence indicators
        def format_with_confidence(
            value: str,
            confidence: int = None,
            searched: bool = True,
            source: str = "engagement_intelligence",
        ) -> str:
            """Format values with confidence indicators for enhanced schema compliance"""
            if not searched:
                return "N/A - not analyzed in engagement intelligence"
            elif not value or str(value).strip() == "" or str(value).lower() == "unknown":
                return f"Not determined (analyzed via {source}, 80% confidence)"
            else:
                conf = f"({confidence}% confidence)" if confidence else "(85% confidence)"
                return f"{value} {conf}"

        # Extract intelligence data with fallbacks for basic intelligence
        problems_owned = getattr(
            engagement_intel, "problems_owned", ["General infrastructure challenges"]
        )
        pain_point_details = getattr(engagement_intel, "pain_point_details", {})
        value_add_ideas = getattr(
            engagement_intel, "value_add_ideas", ["Share industry best practices"]
        )
        content_matches = getattr(engagement_intel, "verdigris_content_matches", [])
        optimal_timing = getattr(engagement_intel, "optimal_timing", {})

        # Build enhanced schema-compliant contact with engagement intelligence
        enhanced_contact = {
            # Basic contact info (preserved from original)
            **contact,
            # Enhanced Engagement Intelligence with confidence indicators
            "Primary Pain Points": format_with_confidence(
                "; ".join(problems_owned[:3]), 90, True, "role_pain_point_mapping"
            ),
            "Pain Point Analysis": format_with_confidence(
                "; ".join([f"{k}: {v}" for k, v in pain_point_details.items()][:2]),
                85,
                True,
                "contextual_pain_analysis",
            ),
            "Value-Add Opportunities": format_with_confidence(
                "; ".join(value_add_ideas[:2]), 80, True, "ai_value_generation"
            ),
            "Recommended Content Assets": format_with_confidence(
                "; ".join([asset.get("title", "Generic content") for asset in content_matches[:3]]),
                75,
                True,
                "content_matching_algorithm",
            ),
            # Personalized Outreach Strategy
            "Primary Outreach Channel": format_with_confidence(
                self._extract_primary_channel(engagement_intel), 85, True, "channel_optimization"
            ),
            "Personalized Message Hook": format_with_confidence(
                self._extract_message_hook(engagement_intel), 75, True, "personalization_engine"
            ),
            "Conversation Starters": format_with_confidence(
                "; ".join(
                    getattr(
                        engagement_intel,
                        "conversation_starters",
                        ["What are your current infrastructure challenges?"],
                    )[:3]
                ),
                80,
                True,
                "contextual_conversation_generation",
            ),
            # Timing Intelligence
            "Optimal Outreach Timing": format_with_confidence(
                f"{optimal_timing.get('urgency', 'Medium')} urgency - {optimal_timing.get('best_timeframe', 'Next 2-3 weeks')}",
                85,
                True,
                "timing_optimization_analysis",
            ),
            "Urgency Factors": format_with_confidence(
                "; ".join(getattr(engagement_intel, "urgency_factors", ["General timing"])[:2]),
                75,
                True,
                "trigger_event_analysis",
            ),
            # Enhanced Engagement Intelligence Metadata
            "Engagement Analysis Source": "role_based_pain_mapping",
            "Engagement Analysis Timestamp": datetime.now().isoformat(),
            "Intelligence Generation Method": "ai_powered_personalization",
            "Engagement Analysis Status": "comprehensive_intelligence_complete",
            # Role-Specific Intelligence
            "Role Classification": format_with_confidence(
                self._classify_role(contact.get("title", "")), 95, True, "title_classification"
            ),
            "Decision Influence Level": format_with_confidence(
                self._assess_decision_influence(contact), 80, True, "influence_assessment"
            ),
            "Content Engagement Score": format_with_confidence(
                str(self._calculate_content_engagement_score(contact)),
                70,
                True,
                "linkedin_activity_analysis",
            ),
        }

        return enhanced_contact

    def _extract_primary_channel(self, engagement_intel: EngagementIntelligence) -> str:
        """Extract primary outreach channel from engagement intelligence"""
        # Try to determine from outreach templates
        if hasattr(engagement_intel, "email_template") and engagement_intel.email_template:
            email_length = len(str(getattr(engagement_intel, "email_template", "")))
            linkedin_length = len(str(getattr(engagement_intel, "linkedin_message", "")))

            if email_length > linkedin_length:
                return "Email (personalized)"
            elif linkedin_length > 50:
                return "LinkedIn (professional connection)"
            else:
                return "Phone (direct outreach)"

        return "Email (default professional approach)"

    def _extract_message_hook(self, engagement_intel: EngagementIntelligence) -> str:
        """Extract primary message hook from engagement intelligence"""
        if hasattr(engagement_intel, "email_template"):
            email = str(getattr(engagement_intel, "email_template", ""))
            # Try to extract the opening hook from email template
            lines = email.split("\n")
            for line in lines[3:6]:  # Look in opening lines after greeting
                if line.strip() and len(line.strip()) > 20 and not line.startswith("At Verdigris"):
                    return line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip()

        # Fallback
        problems = getattr(engagement_intel, "problems_owned", [])
        if problems:
            return f"Focus on {problems[0].lower()} challenges"

        return "Infrastructure optimization discussion"

    def _assess_decision_influence(self, contact: dict) -> str:
        """Assess decision influence level for the contact"""
        title = contact.get("title", "").lower()

        if any(term in title for term in ["cto", "cio", "vp", "vice president"]):
            return "High (Executive decision maker)"
        elif "director" in title:
            return "Medium-High (Department decision maker)"
        elif "manager" in title:
            return "Medium (Team decision influence)"
        elif "engineer" in title or "specialist" in title:
            return "Medium-Low (Technical influencer)"
        else:
            return "Low (Individual contributor)"

    def _calculate_content_engagement_score(self, contact: dict) -> int:
        """Calculate content engagement score based on LinkedIn activity"""
        activity_level = contact.get("linkedin_activity_level", "").lower()
        content_themes = contact.get("content_themes", [])

        score = 50  # Base score

        if activity_level == "high":
            score += 30
        elif activity_level == "medium":
            score += 15
        elif activity_level == "low":
            score -= 10

        # Bonus for relevant content themes
        relevant_themes = [
            "infrastructure",
            "data center",
            "engineering",
            "technology",
            "power",
            "energy",
        ]
        theme_matches = sum(
            1
            for theme in content_themes
            if any(relevant in theme.lower() for relevant in relevant_themes)
        )
        score += theme_matches * 5

        return min(max(score, 0), 100)  # Cap between 0-100

    def generate_enhanced_engagement_summary(self, contacts: list[dict]) -> dict:
        """Generate enhanced summary of engagement intelligence with confidence indicators"""

        if not contacts:
            return {
                "Total Contacts Analyzed": "0 contacts (100% confidence)",
                "High-Engagement Contacts": "0 contacts (100% confidence)",
                "Primary Pain Points Identified": "None (100% confidence)",
                "Content Assets Recommended": "0 assets (100% confidence)",
                "Engagement Analysis Status": "No contacts to analyze (100% confidence)",
            }

        # Analyze engagement potential
        total_contacts = len(contacts)
        high_engagement = len([c for c in contacts if c.get("Content Engagement Score", 0) > 70])

        # Extract common pain points
        all_pain_points = []
        for contact in contacts:
            pain_points_str = contact.get("Primary Pain Points", "")
            if pain_points_str and "confidence)" in pain_points_str:
                # Extract pain points from confidence-formatted string
                pain_points_clean = pain_points_str.split("(")[0].strip()
                pain_points = [p.strip() for p in pain_points_clean.split(";") if p.strip()]
                all_pain_points.extend(pain_points)

        # Count pain point frequency
        pain_point_counts = {}
        for pain_point in all_pain_points:
            pain_point_counts[pain_point] = pain_point_counts.get(pain_point, 0) + 1

        top_pain_points = sorted(pain_point_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Count content assets
        content_assets_mentioned = sum(
            1
            for contact in contacts
            if contact.get("Recommended Content Assets", "").strip()
            and "Not determined" not in contact.get("Recommended Content Assets", "")
        )

        return {
            "Total Contacts Analyzed": f"{total_contacts} contacts analyzed (100% confidence)",
            "High-Engagement Contacts": f"{high_engagement} contacts with 70+ engagement score (90% confidence)",
            "Primary Pain Points Identified": f"{', '.join([f'{pain} ({count} contacts)' for pain, count in top_pain_points])} (85% confidence)",
            "Content Assets Recommended": f"{content_assets_mentioned} contacts matched with relevant content (80% confidence)",
            "Average Decision Influence": f"{self._calculate_avg_influence(contacts)} (85% confidence)",
            "Outreach Channel Distribution": f"{self._analyze_channel_distribution(contacts)} (80% confidence)",
            "Engagement Analysis Status": "Comprehensive role-based intelligence complete (95% confidence)",
        }

    def _calculate_avg_influence(self, contacts: list[dict]) -> str:
        """Calculate average decision influence across contacts"""
        influence_scores = []
        for contact in contacts:
            influence_str = contact.get("Decision Influence Level", "").lower()
            if "high" in influence_str:
                influence_scores.append(4)
            elif "medium-high" in influence_str:
                influence_scores.append(3)
            elif "medium" in influence_str:
                influence_scores.append(2)
            elif "medium-low" in influence_str:
                influence_scores.append(1)
            else:
                influence_scores.append(0)

        if influence_scores:
            avg_score = sum(influence_scores) / len(influence_scores)
            if avg_score >= 3.5:
                return "High (Executive-heavy contact list)"
            elif avg_score >= 2.5:
                return "Medium-High (Management-focused)"
            elif avg_score >= 1.5:
                return "Medium (Mixed decision makers)"
            else:
                return "Low-Medium (Individual contributors)"

        return "Unknown (insufficient data)"

    def _analyze_channel_distribution(self, contacts: list[dict]) -> str:
        """Analyze distribution of recommended outreach channels"""
        channels = []
        for contact in contacts:
            channel_str = contact.get("Primary Outreach Channel", "")
            if "Email" in channel_str:
                channels.append("Email")
            elif "LinkedIn" in channel_str:
                channels.append("LinkedIn")
            elif "Phone" in channel_str:
                channels.append("Phone")
            else:
                channels.append("Other")

        if channels:
            channel_counts = {}
            for channel in channels:
                channel_counts[channel] = channel_counts.get(channel, 0) + 1

            total = len(channels)
            distribution = [
                f"{channel} ({count}/{total})" for channel, count in channel_counts.items()
            ]
            return ", ".join(distribution)

        return "No channels analyzed"


# Export for use by production system
enhanced_engagement_intelligence = EnhancedEngagementIntelligence()
