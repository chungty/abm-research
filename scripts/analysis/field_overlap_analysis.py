#!/usr/bin/env python3
"""
Field Overlap Analysis

Analyze potential field overlaps between Accounts and Events to prevent confusion and data inconsistency.
"""


def analyze_field_overlap():
    """Analyze field overlap between databases"""

    print("🔍 FIELD OVERLAP ANALYSIS")
    print("=" * 50)

    # Current field structure analysis
    field_analysis = {
        "accounts": {
            "core_intelligence": [
                "Physical Infrastructure",
                "Recent Leadership Changes",
                "Recent Funding",
                "Growth Stage",
                "Hiring Velocity",
                "Key Decision Makers",
                "Competitor Tools",
            ],
            "strategic_positioning": [
                "Recent Announcements",
                "Conversation Triggers",
                "Current Tech Stack",
            ],
        },
        "trigger_events": {
            "event_specific": ["Event Type", "Event Description", "Event Stage", "Confidence"],
            "action_intelligence": [
                "Follow-up Actions",
                "Action Deadline",
                "Peak Relevance Window",
                "Decay Rate",
                "Urgency Level",
            ],
            "scoring": [
                "Business Impact Score",
                "Actionability Score",
                "Timing Urgency Score",
                "Strategic Fit Score",
            ],
        },
    }

    # Identify potential overlaps
    overlaps = [
        {
            "issue": "Announcements vs Events",
            "account_field": "Recent Announcements",
            "event_field": "Event Description",
            "problem": "Company announcements could be duplicated between strategic context (account) and specific events",
            "solution": "Account: Strategic impact of announcements, Events: Specific actionable announcements",
            "severity": "Medium",
        },
        {
            "issue": "Action Confusion",
            "account_field": "Conversation Triggers",
            "event_field": "Follow-up Actions",
            "problem": "Both fields suggest actions to take, creating confusion about where to look",
            "solution": "Account: Long-term conversation themes, Events: Immediate time-bound actions",
            "severity": "High",
        },
        {
            "issue": "Stage Naming Confusion",
            "account_field": "Growth Stage",
            "event_field": "Event Stage",
            "problem": "Similar naming but completely different purposes - could confuse users",
            "solution": 'Rename Event Stage to "Event Lifecycle" for clarity',
            "severity": "Low",
        },
        {
            "issue": "Confidence Scoring Inconsistency",
            "account_field": "Various fields with embedded confidence",
            "event_field": "Separate Confidence field",
            "problem": "Mixed approaches to confidence scoring across databases",
            "solution": "Standardize confidence scoring approach across all databases",
            "severity": "Medium",
        },
    ]

    print("⚠️  IDENTIFIED OVERLAPS:")
    print()

    for overlap in overlaps:
        severity_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[overlap["severity"]]
        print(f'{severity_emoji} {overlap["issue"].upper()} ({overlap["severity"]} Priority)')
        print(f'   Account: {overlap["account_field"]}')
        print(f'   Event: {overlap["event_field"]}')
        print(f'   Problem: {overlap["problem"]}')
        print(f'   Solution: {overlap["solution"]}')
        print()

    # Recommended field purpose clarification
    print("📋 RECOMMENDED FIELD PURPOSE CLARIFICATION:")
    print("=" * 55)
    print()

    print("🏢 ACCOUNT FIELDS (Strategic, Persistent):")
    print("   📊 Physical Infrastructure: Long-term tech stack and datacenter setup")
    print("   🎯 Growth Stage: Overall company maturity and scale")
    print("   💡 Conversation Triggers: Ongoing themes and talking points for relationship building")
    print("   📰 Recent Announcements: Strategic context and company direction insights")
    print()

    print("⚡ EVENT FIELDS (Tactical, Time-bound):")
    print(
        "   🎬 Event Lifecycle: Specific event status (Rumored → Announced → In-Progress → Completed)"
    )
    print("   🎯 Follow-up Actions: Immediate tactical steps with deadlines")
    print("   📈 Multi-dimensional Scores: Event-specific impact and urgency ratings")
    print("   ⏰ Time Intelligence: When to act, when relevance peaks, when opportunity expires")
    print()

    print("🔧 CONSOLIDATION RECOMMENDATIONS:")
    print("=" * 40)
    print('1. 🔴 HIGH PRIORITY: Clarify "Conversation Triggers" vs "Follow-up Actions"')
    print("   → Account: Strategic conversation themes")
    print("   → Event: Tactical next steps with deadlines")
    print()
    print("2. 🟡 MEDIUM PRIORITY: Standardize confidence scoring")
    print('   → Use consistent "field name (confidence%)" format')
    print("   → Add confidence tracking to all intelligence fields")
    print()
    print('3. 🟢 LOW PRIORITY: Rename "Event Stage" to "Event Lifecycle"')
    print('   → Eliminates confusion with "Growth Stage"')
    print("   → Makes purpose more explicit")
    print()

    print("📊 FIELD SEPARATION VALIDATION:")
    print(
        "✅ Good separation: Physical Infrastructure (persistent) vs Event-specific scoring (temporal)"
    )
    print("✅ Good separation: Growth Stage (company-wide) vs Event Lifecycle (event-specific)")
    print("⚠️  Needs clarification: Announcements and triggers context vs specific event actions")

    return overlaps


if __name__ == "__main__":
    overlaps = analyze_field_overlap()
    print(f"\\n🎯 Analysis complete. Found {len(overlaps)} potential overlap issues.")
