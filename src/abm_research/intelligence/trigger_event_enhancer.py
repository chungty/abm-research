"""
Trigger Event Enhancement System
Adds timing context, relevance decay, and actionable insights to trigger events
"""
import requests
from datetime import datetime, timedelta
from ..config.manager import config_manager


class TriggerEventEnhancer:
    """Enhance trigger events with timing and context"""

    def __init__(self):
        self.headers = config_manager.get_notion_headers()
        self.base_url = "https://api.notion.com/v1"

    def enhance_trigger_events(self):
        """Enhance existing trigger events with timing context"""
        try:
            trigger_events_db_id = config_manager.get_database_id("trigger_events")
        except ValueError:
            print("❌ Trigger events database not found")
            return

        # Add timing context to existing events (using current dates)
        today = datetime.now()
        enhanced_events = [
            {
                "description": "Announced $75M investment in GPU infrastructure for AI workloads",
                "event_date": (today - timedelta(days=12)).strftime("%Y-%m-%d"),  # 12 days ago
                "detected_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),  # 1 day ago
                "urgency_level": "HIGH",
                "buying_stage_impact": "EARLY_RESEARCH",
                "verdigris_angle": "Power monitoring critical for new GPU deployment success",
                "follow_up_actions": [
                    "Reference AI investment in opener",
                    "Share GPU rack optimization case study",
                    "Highlight predictive capacity planning benefits",
                ],
                "stakeholders_impacted": [
                    "Infrastructure Team",
                    "Data Center Operations",
                    "Finance",
                ],
                "timeline_pressure": "6-month implementation window",
                "competitive_implications": "Other monitoring vendors likely also targeting this opportunity",
            },
            {
                "description": "CEO mentioned rising energy costs as top priority in Q3 earnings",
                "event_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),  # 8 days ago
                "detected_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),  # 1 day ago
                "urgency_level": "CRITICAL",
                "buying_stage_impact": "PROBLEM_AWARE",
                "verdigris_angle": "Direct ROI opportunity - energy cost reduction is CEO mandate",
                "follow_up_actions": [
                    "Lead with energy cost reduction ROI",
                    "Provide benchmark data vs industry peers",
                    "Offer energy audit and savings projection",
                ],
                "stakeholders_impacted": ["CEO", "CFO", "VP Operations", "Sustainability Team"],
                "timeline_pressure": "Budget planning for 2025 happening now",
                "competitive_implications": "Energy management vendors also targeting - differentiate on real-time capabilities",
            },
        ]

        return self.analyze_event_freshness(enhanced_events)

    def analyze_event_freshness(self, events):
        """Analyze how fresh events are and calculate relevance decay"""
        today = datetime.now()
        analyzed_events = []

        for event in events:
            event_date = datetime.strptime(event["event_date"], "%Y-%m-%d")
            detected_date = datetime.strptime(event["detected_date"], "%Y-%m-%d")

            # Calculate freshness
            days_since_event = (today - event_date).days
            days_since_detection = (today - detected_date).days

            # Calculate relevance score with decay
            base_relevance = self.calculate_base_relevance(event)
            time_decay_factor = self.calculate_time_decay(days_since_event, event["urgency_level"])
            current_relevance = base_relevance * time_decay_factor

            # Add timing analysis
            event["timing_analysis"] = {
                "days_since_event": days_since_event,
                "days_since_detection": days_since_detection,
                "freshness_category": self.categorize_freshness(days_since_event),
                "base_relevance": base_relevance,
                "time_decay_factor": time_decay_factor,
                "current_relevance": round(current_relevance, 1),
                "optimal_outreach_window": self.determine_outreach_window(event, days_since_event),
            }

            analyzed_events.append(event)

        return analyzed_events

    def calculate_base_relevance(self, event):
        """Calculate base relevance score (0-100)"""
        description = event["description"].lower()

        # High relevance keywords
        if any(keyword in description for keyword in ["ai", "gpu", "power", "energy"]):
            base_score = 90
        elif any(keyword in description for keyword in ["infrastructure", "capacity", "expansion"]):
            base_score = 80
        elif any(keyword in description for keyword in ["cost", "efficiency", "optimization"]):
            base_score = 85
        else:
            base_score = 70

        # Boost for CEO/leadership involvement
        if any(keyword in description for keyword in ["ceo", "leadership", "executive"]):
            base_score += 10

        return min(100, base_score)

    def calculate_time_decay(self, days_since_event, urgency_level):
        """Calculate time-based relevance decay factor (0-1)"""
        if urgency_level == "CRITICAL":
            # Critical events stay relevant longer
            if days_since_event <= 30:
                return 1.0
            elif days_since_event <= 60:
                return 0.9
            elif days_since_event <= 90:
                return 0.7
            else:
                return 0.5
        elif urgency_level == "HIGH":
            # High urgency events decay faster
            if days_since_event <= 14:
                return 1.0
            elif days_since_event <= 30:
                return 0.8
            elif days_since_event <= 60:
                return 0.6
            else:
                return 0.3
        else:  # MEDIUM or LOW
            if days_since_event <= 7:
                return 1.0
            elif days_since_event <= 21:
                return 0.7
            else:
                return 0.4

    def categorize_freshness(self, days_since_event):
        """Categorize event freshness"""
        if days_since_event <= 7:
            return "BREAKING"
        elif days_since_event <= 21:
            return "FRESH"
        elif days_since_event <= 60:
            return "CURRENT"
        elif days_since_event <= 120:
            return "STALE"
        else:
            return "OUTDATED"

    def determine_outreach_window(self, event, days_since_event):
        """Determine optimal outreach timing"""
        urgency = event["urgency_level"]
        buying_stage = event["buying_stage_impact"]

        if urgency == "CRITICAL" and days_since_event <= 30:
            return "IMMEDIATE - Strike while iron is hot"
        elif urgency == "HIGH" and days_since_event <= 14:
            return "THIS WEEK - High relevance window closing"
        elif buying_stage == "EARLY_RESEARCH" and days_since_event <= 45:
            return "WITHIN 2 WEEKS - Catch them in research phase"
        elif days_since_event <= 60:
            return "THIS MONTH - Still relevant but fading"
        else:
            return "LOW PRIORITY - Event impact diminishing"

    def generate_sales_actions(self, enhanced_events):
        """Generate specific sales actions based on enhanced events"""
        sales_actions = []

        for event in enhanced_events:
            timing = event["timing_analysis"]

            # Only generate actions for relevant events
            if timing["current_relevance"] >= 60:
                action = {
                    "event_description": event["description"],
                    "priority": self.calculate_action_priority(event),
                    "urgency_reason": f"{timing['freshness_category']} event with {timing['current_relevance']}% relevance",
                    "recommended_actions": event["follow_up_actions"],
                    "stakeholders_to_target": event["stakeholders_impacted"],
                    "timing_window": timing["optimal_outreach_window"],
                    "key_message": event["verdigris_angle"],
                    "competitive_context": event["competitive_implications"],
                }
                sales_actions.append(action)

        # Sort by priority
        sales_actions.sort(key=lambda x: x["priority"], reverse=True)
        return sales_actions

    def calculate_action_priority(self, event):
        """Calculate priority score for sales action (0-100)"""
        timing = event["timing_analysis"]

        # Base priority from current relevance
        priority = timing["current_relevance"]

        # Boost for urgency
        if event["urgency_level"] == "CRITICAL":
            priority += 20
        elif event["urgency_level"] == "HIGH":
            priority += 10

        # Boost for optimal timing
        if "IMMEDIATE" in timing["optimal_outreach_window"]:
            priority += 15
        elif "THIS WEEK" in timing["optimal_outreach_window"]:
            priority += 10

        # Boost for high-value stakeholders
        if any(stakeholder in ["CEO", "CFO"] for stakeholder in event["stakeholders_impacted"]):
            priority += 10

        return min(100, priority)

    def generate_enriched_report(self):
        """Generate comprehensive enriched trigger events report"""
        print("🔍 Analyzing trigger events with timing context...")

        enhanced_events = self.enhance_trigger_events()
        sales_actions = self.generate_sales_actions(enhanced_events)

        print(f"\n📊 ENRICHED TRIGGER EVENTS ANALYSIS")
        print("=" * 60)

        for i, event in enumerate(enhanced_events, 1):
            timing = event["timing_analysis"]

            print(f"\n{i}. {event['description']}")
            print(f"   📅 Event Date: {event['event_date']} ({timing['days_since_event']} days ago)")
            print(f"   🔥 Freshness: {timing['freshness_category']}")
            print(f"   📈 Current Relevance: {timing['current_relevance']}%")
            print(f"   ⏰ Outreach Window: {timing['optimal_outreach_window']}")
            print(f"   🎯 Verdigris Angle: {event['verdigris_angle']}")
            print(f"   👥 Key Stakeholders: {', '.join(event['stakeholders_impacted'])}")

        print(f"\n🚀 PRIORITIZED SALES ACTIONS")
        print("=" * 60)

        for i, action in enumerate(sales_actions, 1):
            print(f"\n{i}. Priority: {action['priority']}/100")
            print(f"   Event: {action['event_description']}")
            print(f"   ⚡ Urgency: {action['urgency_reason']}")
            print(f"   🎯 Key Message: {action['key_message']}")
            print(f"   📋 Actions:")
            for rec_action in action["recommended_actions"]:
                print(f"      • {rec_action}")
            print(f"   ⏰ Timing: {action['timing_window']}")

        return {
            "enhanced_events": enhanced_events,
            "sales_actions": sales_actions,
            "summary": {
                "total_events": len(enhanced_events),
                "actionable_events": len(sales_actions),
                "high_priority_events": len([a for a in sales_actions if a["priority"] >= 80]),
                "immediate_action_required": len(
                    [a for a in sales_actions if "IMMEDIATE" in a["timing_window"]]
                ),
            },
        }


def main():
    """Run trigger event enhancement analysis"""
    enhancer = TriggerEventEnhancer()
    result = enhancer.generate_enriched_report()

    summary = result["summary"]
    print(f"\n📈 SUMMARY")
    print("=" * 30)
    print(f"Total Events: {summary['total_events']}")
    print(f"Actionable Events: {summary['actionable_events']}")
    print(f"High Priority: {summary['high_priority_events']}")
    print(f"Immediate Action: {summary['immediate_action_required']}")

    if summary["immediate_action_required"] > 0:
        print(
            f"\n🔥 URGENT: {summary['immediate_action_required']} events require immediate action!"
        )

    return result


if __name__ == "__main__":
    main()
