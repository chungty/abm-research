#!/usr/bin/env python3
"""
Enhanced Engagement Intelligence Engine
Implements Phase 4 requirements from skill specification
Role-specific pain point mapping and personalized value-add recommendations
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import openai

@dataclass
class EngagementIntelligence:
    """Complete engagement intelligence for a contact"""
    # Pain point mapping
    problems_owned: List[str]  # From role-to-pain-point mapping
    pain_point_details: Dict[str, str]  # Detailed explanation per pain point

    # Value proposition matching
    value_add_ideas: List[str]  # 2-3 specific, actionable ideas
    verdigris_content_matches: List[Dict]  # Matching content assets

    # Personalized outreach
    email_template: str  # Personalized email template
    linkedin_message: str  # LinkedIn connection/message
    call_script: str  # Phone conversation guide
    conversation_starters: List[str]  # 3-5 specific questions

    # Timing intelligence
    optimal_timing: Dict  # When and why to reach out
    urgency_factors: List[str]  # Reasons for urgency

class EnhancedEngagementIntelligence:
    """Phase 4 implementation: AI-powered engagement intelligence"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Load skill configuration
        self.load_skill_config()
        self.load_pain_point_mapping()
        self.load_content_asset_library()

    def load_skill_config(self):
        """Load ICP pain points from skill specification"""
        try:
            with open('/Users/chungty/Projects/vdg-clean/abm-research/references/lead_scoring_config.json', 'r') as f:
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
                "Cost reduction mandates"
            ],
            "CIO": [
                "Uptime and reliability pressure",
                "Cost reduction mandates",
                "Remote monitoring and troubleshooting"
            ],

            # VP Level - Operational + Strategic
            "VP, Infrastructure & Data Centers": [
                "Power capacity planning and management",
                "AI workload expansion challenges",
                "Energy efficiency and PUE optimization",
                "Sustainability and ESG reporting requirements"
            ],
            "VP of Operations": [
                "Uptime and reliability pressure",
                "Cost reduction mandates",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting"
            ],

            # Director Level - Tactical + Operational
            "Director, Infrastructure Engineering": [
                "Power capacity planning and management",
                "AI workload expansion challenges",
                "Predictive maintenance and risk detection"
            ],
            "Director, Data Center Operations": [
                "Uptime and reliability pressure",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting"
            ],
            "Director, Data Center Facilities": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection"
            ],
            "Director, Cloud Platform & SRE": [
                "Uptime and reliability pressure",
                "Remote monitoring and troubleshooting",
                "Predictive maintenance and risk detection"
            ],

            # Manager Level - Daily operational pain
            "SRE Manager": [
                "Uptime and reliability pressure",
                "Predictive maintenance and risk detection",
                "Remote monitoring and troubleshooting"
            ],
            "Facilities Manager": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "Predictive maintenance and risk detection"
            ],
            "NOC & Operations Team": [
                "Remote monitoring and troubleshooting",
                "Uptime and reliability pressure"
            ],

            # Engineer Level - Technical implementation
            "Capacity & Energy Engineer": [
                "Power capacity planning and management",
                "Energy efficiency and PUE optimization",
                "AI workload expansion challenges"
            ],
            "Critical Facilities Engineers": [
                "Predictive maintenance and risk detection",
                "Power capacity planning and management",
                "Uptime and reliability pressure"
            ],
            "SRE/Infrastructure Engineers": [
                "Remote monitoring and troubleshooting",
                "Uptime and reliability pressure",
                "Predictive maintenance and risk detection"
            ],

            # Product/Program roles
            "Monitoring/DCIM Product Owner": [
                "Remote monitoring and troubleshooting",
                "Predictive maintenance and risk detection",
                "Energy efficiency and PUE optimization"
            ],

            # Finance
            "Finance/FP&A": [
                "Cost reduction mandates",
                "Energy efficiency and PUE optimization",
                "Sustainability and ESG reporting requirements"
            ]
        }

    def load_content_asset_library(self):
        """Library of Verdigris content assets for value-add matching"""
        self.content_assets = {
            "Power capacity planning and management": [
                {
                    "title": "GPU Rack Power Optimization Case Study",
                    "description": "How Lambda Labs reduced power constraints for AI workloads by 40%",
                    "type": "case_study",
                    "relevance": "Direct power planning solution"
                },
                {
                    "title": "Real-time Capacity Planning Whitepaper",
                    "description": "Circuit-level monitoring for predictive capacity management",
                    "type": "whitepaper",
                    "relevance": "Technical implementation guide"
                }
            ],
            "Energy efficiency and PUE optimization": [
                {
                    "title": "PUE Reduction Success Story - 15% Improvement",
                    "description": "Hyperscale data center achieves 1.12 PUE with real-time monitoring",
                    "type": "case_study",
                    "relevance": "Proven efficiency gains"
                },
                {
                    "title": "Energy Analytics Dashboard Demo",
                    "description": "Interactive demo of power analytics and optimization recommendations",
                    "type": "demo",
                    "relevance": "Hands-on experience with solution"
                }
            ],
            "Uptime and reliability pressure": [
                {
                    "title": "Predictive Fault Detection ROI Calculator",
                    "description": "Calculate downtime cost savings from early fault detection",
                    "type": "calculator",
                    "relevance": "Business case quantification"
                },
                {
                    "title": "Critical System Monitoring Best Practices",
                    "description": "Framework for preventing electrical failures in mission-critical systems",
                    "type": "guide",
                    "relevance": "Implementation roadmap"
                }
            ],
            "AI workload expansion challenges": [
                {
                    "title": "High-Density GPU Monitoring Solution",
                    "description": "Real-time power and thermal monitoring for AI/ML infrastructure",
                    "type": "solution_brief",
                    "relevance": "AI-specific power challenges"
                },
                {
                    "title": "NVIDIA Partnership Announcement",
                    "description": "Joint solution for GPU cluster power optimization",
                    "type": "press_release",
                    "relevance": "Industry validation"
                }
            ],
            "Sustainability and ESG reporting requirements": [
                {
                    "title": "Automated Carbon Reporting Dashboard",
                    "description": "Real-time Scope 2 & 3 emissions tracking for ESG compliance",
                    "type": "demo",
                    "relevance": "ESG automation solution"
                },
                {
                    "title": "Sustainability ROI Whitepaper",
                    "description": "How power monitoring drives both cost savings and carbon reduction",
                    "type": "whitepaper",
                    "relevance": "Business and environmental benefits"
                }
            ]
        }

    def generate_engagement_intelligence(self, contact: Dict, trigger_events: List[Dict] = None,
                                       account_context: Dict = None) -> EngagementIntelligence:
        """
        Generate complete engagement intelligence for high-scoring contacts
        Following Phase 4 requirements from skill specification
        """
        if contact.get('final_lead_score', 0) < 70:
            return self._create_basic_intelligence(contact)

        print(f"🧠 Generating engagement intelligence for {contact.get('name')} (Score: {contact.get('final_lead_score')})")

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
            problems_owned=problems_analysis['problems'],
            pain_point_details=problems_analysis['details'],
            value_add_ideas=value_add_analysis['ideas'],
            verdigris_content_matches=value_add_analysis['content_matches'],
            email_template=outreach_templates['email'],
            linkedin_message=outreach_templates['linkedin'],
            call_script=outreach_templates['call_script'],
            conversation_starters=outreach_templates['conversation_starters'],
            optimal_timing=timing_analysis['timing'],
            urgency_factors=timing_analysis['urgency_factors']
        )

    def _map_role_to_pain_points(self, contact: Dict) -> Dict:
        """Map contact's role to specific ICP pain points per skill specification"""
        title = contact.get('title', '')
        role_classification = self._classify_role(title)

        # Get pain points for this role
        role_pain_points = self.role_pain_mapping.get(role_classification, [
            "Power capacity planning and management",
            "Uptime and reliability pressure"  # Default pain points
        ])

        # Generate detailed explanations for each pain point
        pain_point_details = {}
        for pain_point in role_pain_points:
            pain_point_details[pain_point] = self._explain_pain_point_for_role(
                pain_point, role_classification, title
            )

        return {
            'problems': role_pain_points,
            'details': pain_point_details,
            'role_classification': role_classification
        }

    def _classify_role(self, title: str) -> str:
        """Classify role using same logic as lead_scoring_engine.py"""
        title_lower = title.lower()

        # C-Suite
        if any(term in title_lower for term in ['cio', 'cto', 'chief information', 'chief technology']):
            return 'CIO' if 'cio' in title_lower or 'information' in title_lower else 'CTO'

        # VP Level
        if 'vp' in title_lower or 'vice president' in title_lower:
            if any(term in title_lower for term in ['infrastructure', 'data center']):
                return 'VP, Infrastructure & Data Centers'
            elif 'operations' in title_lower:
                return 'VP of Operations'

        # Director Level
        if 'director' in title_lower:
            if any(term in title_lower for term in ['infrastructure', 'engineering']):
                return 'Director, Infrastructure Engineering'
            elif any(term in title_lower for term in ['data center', 'datacenter']) and 'operations' in title_lower:
                return 'Director, Data Center Operations'
            elif 'facilities' in title_lower:
                return 'Director, Data Center Facilities'
            elif any(term in title_lower for term in ['cloud', 'sre', 'platform']):
                return 'Director, Cloud Platform & SRE'

        # Manager Level
        if 'manager' in title_lower:
            if 'sre' in title_lower or 'reliability' in title_lower:
                return 'SRE Manager'
            elif 'facilities' in title_lower:
                return 'Facilities Manager'

        # Engineer Level
        if any(term in title_lower for term in ['engineer', 'engineering']):
            if any(term in title_lower for term in ['capacity', 'energy']):
                return 'Capacity & Energy Engineer'
            elif any(term in title_lower for term in ['facilities', 'critical']):
                return 'Critical Facilities Engineers'
            elif any(term in title_lower for term in ['sre', 'infrastructure', 'reliability']):
                return 'SRE/Infrastructure Engineers'

        # Product/Program roles
        if any(term in title_lower for term in ['product', 'program']) and any(term in title_lower for term in ['monitoring', 'dcim']):
            return 'Monitoring/DCIM Product Owner'

        # Operations
        if any(term in title_lower for term in ['noc', 'operations', 'ops']) and not any(term in title_lower for term in ['director', 'manager', 'vp']):
            return 'NOC & Operations Team'

        # Finance
        if any(term in title_lower for term in ['finance', 'fp&a', 'financial']):
            return 'Finance/FP&A'

        return 'Unknown'

    def _explain_pain_point_for_role(self, pain_point: str, role_classification: str, actual_title: str) -> str:
        """Generate role-specific explanation of how this pain point affects them"""
        explanations = {
            "Power capacity planning and management": {
                "Capacity & Energy Engineer": "Daily struggle with accurate power budgeting for new deployments and rack-level capacity planning",
                "Director, Infrastructure Engineering": "Strategic challenge of ensuring adequate power capacity for business growth while optimizing capital allocation",
                "VP, Infrastructure & Data Centers": "Executive accountability for power infrastructure investments and capacity planning accuracy"
            },
            "Energy efficiency and PUE optimization": {
                "Facilities Manager": "Direct responsibility for achieving energy efficiency targets and reducing operational costs",
                "Director, Data Center Facilities": "KPI ownership for PUE improvement and sustainability metrics",
                "Finance/FP&A": "Budget pressure from rising energy costs and need for efficiency justification"
            },
            "Uptime and reliability pressure": {
                "SRE Manager": "SLA accountability and incident response for reliability targets",
                "Director, Data Center Operations": "Operational excellence mandate for 99.99% uptime requirements",
                "NOC & Operations Team": "Front-line responsibility for maintaining system reliability"
            }
        }

        specific_explanation = explanations.get(pain_point, {}).get(role_classification)
        if specific_explanation:
            return specific_explanation
        else:
            return f"As a {actual_title}, this pain point impacts their daily operational effectiveness and strategic objectives"

    def _generate_value_add_ideas(self, contact: Dict, problems_analysis: Dict) -> Dict:
        """Generate 2-3 specific, actionable value-add ideas per skill specification"""
        problems = problems_analysis['problems']
        role_classification = problems_analysis['role_classification']
        name = contact.get('name', 'Unknown')
        company = contact.get('company', 'your company')

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
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )

            ai_ideas = response.choices[0].message.content.strip().split('\n')
            filtered_ideas = [idea.strip() for idea in ai_ideas if idea.strip() and len(idea.strip()) > 20]

            return {
                'ideas': filtered_ideas[:3],  # Limit to 3 per skill spec
                'content_matches': content_matches[:5]  # Top 5 relevant content pieces
            }

        except Exception as e:
            print(f"⚠️ Error generating value-add ideas: {e}")
            return self._get_fallback_value_add_ideas(role_classification, problems)

    def _generate_outreach_templates(self, contact: Dict, problems_analysis: Dict,
                                   value_add_analysis: Dict, trigger_events: List[Dict] = None,
                                   account_context: Dict = None) -> Dict:
        """Generate personalized outreach templates"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = account_context.get('name', 'your company') if account_context else 'your company'
        role_classification = problems_analysis['role_classification']
        top_pain_point = problems_analysis['problems'][0] if problems_analysis['problems'] else 'operational efficiency'

        # Get most relevant trigger event
        relevant_event = None
        if trigger_events:
            for event in trigger_events:
                if event.get('relevance_score', 0) > 70:
                    relevant_event = event
                    break

        # Generate email template
        email_template = self._generate_email_template(
            name, title, company, top_pain_point, value_add_analysis['ideas'], relevant_event
        )

        # Generate LinkedIn message
        linkedin_message = self._generate_linkedin_message(
            name, title, role_classification, problems_analysis['problems']
        )

        # Generate call script
        call_script = self._generate_call_script(
            name, title, top_pain_point, relevant_event
        )

        # Generate conversation starters
        conversation_starters = self._generate_conversation_starters(
            problems_analysis['problems'], role_classification
        )

        return {
            'email': email_template,
            'linkedin': linkedin_message,
            'call_script': call_script,
            'conversation_starters': conversation_starters
        }

    def _generate_email_template(self, name: str, title: str, company: str,
                               top_pain_point: str, value_ideas: List[str],
                               trigger_event: Dict = None) -> str:
        """Generate personalized email template"""
        subject_hook = ""
        opening_hook = ""

        if trigger_event:
            subject_hook = f"{company}'s {trigger_event.get('event_type', 'infrastructure')} initiative"
            opening_hook = f"I noticed {company}'s {trigger_event.get('description', 'recent infrastructure updates')}."
        else:
            subject_hook = f"{company}'s infrastructure monitoring strategy"
            opening_hook = f"Given your {title} role at {company}, you're likely focused on {top_pain_point.lower()}."

        value_proposition = value_ideas[0] if value_ideas else "reduce energy costs by 15-25% through circuit-level power monitoring"

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

    def _generate_linkedin_message(self, name: str, title: str, role_classification: str,
                                 pain_points: List[str]) -> str:
        """Generate LinkedIn connection message"""
        primary_focus = pain_points[0] if pain_points else "infrastructure optimization"

        message = f"""Hi {name}, I came across your {title} background and was impressed by your experience in infrastructure operations. Given the challenges around {primary_focus.lower()}, I thought you'd be interested in our approach to real-time power monitoring for data centers.

Would you be open to connecting? I'd love to share some insights relevant to {role_classification.lower()} roles."""

        return message

    def _generate_call_script(self, name: str, title: str, top_pain_point: str,
                            trigger_event: Dict = None) -> str:
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

    def _generate_conversation_starters(self, pain_points: List[str], role_classification: str) -> List[str]:
        """Generate role-specific conversation starters"""
        starters = []

        for pain_point in pain_points[:3]:  # Top 3 pain points
            if "power capacity" in pain_point.lower():
                starters.append("What's your current approach to power capacity planning for new deployments?")
            elif "uptime" in pain_point.lower() or "reliability" in pain_point.lower():
                starters.append("How do you currently detect and prevent electrical failures before they impact operations?")
            elif "energy efficiency" in pain_point.lower():
                starters.append("What tools do you use for PUE optimization and energy cost reduction?")
            elif "ai workload" in pain_point.lower():
                starters.append("How are you handling power monitoring for high-density GPU clusters?")
            elif "sustainability" in pain_point.lower():
                starters.append("What's your current process for ESG reporting and carbon metrics collection?")

        # Add role-specific questions
        if 'Engineer' in role_classification:
            starters.append("What monitoring tools are you currently using for circuit-level analysis?")
        elif 'Director' in role_classification or 'Manager' in role_classification:
            starters.append("How do you build business cases for infrastructure monitoring investments?")
        elif 'VP' in role_classification or 'CTO' in role_classification or 'CIO' in role_classification:
            starters.append("What are your key infrastructure KPIs and how do you track them today?")

        return starters[:5]  # Limit to 5 starters

    def _analyze_optimal_timing(self, contact: Dict, trigger_events: List[Dict] = None) -> Dict:
        """Analyze optimal timing for outreach based on trigger events and role"""
        urgency_factors = []
        timing_recommendation = "Medium"
        best_timeframe = "Next 2-3 weeks"
        reasoning = "Good time to explore infrastructure optimization solutions"

        if trigger_events:
            high_relevance_events = [e for e in trigger_events if e.get('relevance_score', 0) > 70]

            if high_relevance_events:
                urgency_factors.extend([
                    f"{event.get('event_type', 'Infrastructure')} event detected with {event.get('confidence', 'medium')} confidence"
                    for event in high_relevance_events[:2]
                ])
                timing_recommendation = "High"
                best_timeframe = "This week"
                reasoning = "Recent trigger events create immediate relevance for power monitoring solutions"

        # Factor in role-based timing
        role_classification = contact.get('role_classification', '')
        if 'Engineer' in role_classification:
            urgency_factors.append("Technical roles often have immediate operational pain points")
        elif 'Director' in role_classification:
            urgency_factors.append("Director-level contacts are often evaluating solutions for quarterly planning")

        # Factor in engagement score
        engagement_score = contact.get('engagement_potential_score', 0)
        if engagement_score > 70:
            urgency_factors.append("High LinkedIn engagement suggests openness to professional conversations")

        return {
            'timing': {
                'urgency': timing_recommendation,
                'best_timeframe': best_timeframe,
                'reasoning': reasoning
            },
            'urgency_factors': urgency_factors
        }

    def _create_basic_intelligence(self, contact: Dict) -> EngagementIntelligence:
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
            optimal_timing={'urgency': 'Low', 'best_timeframe': 'Next month', 'reasoning': 'General timing'},
            urgency_factors=[]
        )

    def _get_fallback_value_add_ideas(self, role_classification: str, problems: List[str]) -> Dict:
        """Fallback value-add ideas when AI generation fails"""
        fallback_ideas = []

        if 'Engineer' in role_classification:
            fallback_ideas = [
                "Action: Share technical whitepaper on circuit-level monitoring - Why: Provides implementation guidance for current projects",
                "Action: Offer demo of real-time power analytics dashboard - Why: Shows immediate visibility into power consumption patterns",
                "Action: Connect with peer engineer at similar company - Why: Enables knowledge sharing on monitoring best practices"
            ]
        elif 'Director' in role_classification or 'Manager' in role_classification:
            fallback_ideas = [
                "Action: Provide ROI calculator for predictive maintenance - Why: Quantifies business impact of early fault detection",
                "Action: Share case study from similar-sized company - Why: Demonstrates proven results in comparable environment",
                "Action: Invite to industry roundtable discussion - Why: Builds relationship while providing peer learning opportunity"
            ]
        else:
            fallback_ideas = [
                "Action: Send industry trend report on power monitoring - Why: Positions Verdigris as thought leader",
                "Action: Offer brief consultation on infrastructure challenges - Why: Provides immediate value while building relationship"
            ]

        return {
            'ideas': fallback_ideas,
            'content_matches': []
        }

    def _get_default_pain_points(self) -> List[str]:
        """Default ICP pain points if config file missing"""
        return [
            "Power capacity planning and management",
            "Uptime and reliability pressure",
            "Energy efficiency and PUE optimization",
            "AI workload expansion challenges",
            "Cost reduction mandates",
            "Sustainability and ESG reporting requirements",
            "Predictive maintenance and risk detection",
            "Remote monitoring and troubleshooting"
        ]


# Export for use by production system
enhanced_engagement_intelligence = EnhancedEngagementIntelligence()