#!/usr/bin/env python3
"""
Enhanced Buying Signals Analyzer
Adds trend analysis and priority explanations to trigger events for more actionable sales intelligence
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

@dataclass
class BuyingSignalTrend:
    """Trend analysis for buying signals"""
    signal_category: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1 scale
    frequency_change: float  # % change in frequency
    recency_factor: float  # How recent the signals are
    market_context: str  # Broader market trend explanation

@dataclass
class BuyingSignalPriority:
    """Priority scoring and explanation"""
    signal_id: str
    priority_score: int  # 1-100 scale
    priority_level: str  # "Critical", "High", "Medium", "Low"
    urgency_factors: List[str]  # List of urgency drivers
    timing_recommendation: str  # When to act
    confidence_reasoning: str  # Why this confidence level
    sales_angle: str  # Recommended approach angle

@dataclass
class EnhancedBuyingSignal:
    """Enhanced buying signal with trend analysis and priority"""
    original_signal: Dict
    trend_analysis: BuyingSignalTrend
    priority_analysis: BuyingSignalPriority
    competitive_context: str  # Market timing considerations
    verdigris_relevance: str  # Specific Verdigris angle
    recommended_actions: List[str]  # Specific next steps

class EnhancedBuyingSignalsAnalyzer:
    """
    Enhanced analyzer for buying signals with trend analysis and priority scoring
    """

    def __init__(self):
        print("🔍 Initializing Enhanced Buying Signals Analyzer")
        print("📊 Adding trend analysis and priority explanations to trigger events")

        # Signal category mappings for trend analysis
        self.signal_categories = {
            'funding': ['funding', 'investment', 'capital', 'series', 'venture'],
            'expansion': ['expansion', 'scaling', 'growth', 'hiring', 'new office'],
            'technology': ['cloud', 'AI', 'infrastructure', 'platform', 'modernization'],
            'partnership': ['partnership', 'acquisition', 'merger', 'collaboration'],
            'leadership': ['CEO', 'CTO', 'VP', 'executive', 'leadership'],
            'product': ['product launch', 'new feature', 'release', 'innovation'],
            'market': ['market entry', 'competitive', 'industry'],
            'compliance': ['compliance', 'regulation', 'security', 'audit']
        }

        # Priority scoring weights
        self.priority_weights = {
            'recency': 0.3,      # How recent the signal is
            'relevance': 0.25,   # Relevance to Verdigris solutions
            'urgency': 0.2,      # Market timing urgency
            'size': 0.15,        # Company/opportunity size
            'confidence': 0.1    # Signal confidence/reliability
        }

        # Verdigris solution mappings
        self.verdigris_solutions = {
            'energy_monitoring': ['energy', 'power', 'consumption', 'efficiency', 'sustainability'],
            'ai_analytics': ['AI', 'analytics', 'machine learning', 'data', 'insights'],
            'iot_platform': ['IoT', 'sensors', 'monitoring', 'devices', 'connected'],
            'cost_optimization': ['cost', 'optimization', 'savings', 'efficiency', 'reduction']
        }

    def analyze_buying_signals(self, trigger_events: List[Dict],
                             account_data: Dict = None) -> List[EnhancedBuyingSignal]:
        """
        Analyze buying signals with enhanced trend analysis and priority scoring
        """
        print(f"\n🔍 Analyzing {len(trigger_events)} buying signals with enhanced intelligence")

        enhanced_signals = []

        # Group signals for trend analysis
        signals_by_category = self._categorize_signals(trigger_events)
        trend_analysis = self._analyze_trends(signals_by_category, trigger_events)

        for event in trigger_events:
            try:
                # Determine signal category
                category = self._categorize_single_signal(event)

                # Generate trend analysis for this signal
                trend = trend_analysis.get(category, self._create_default_trend(category))

                # Calculate priority analysis
                priority = self._calculate_priority_analysis(event, account_data, trend)

                # Generate competitive and market context
                competitive_context = self._analyze_competitive_context(event, category)

                # Determine Verdigris-specific relevance
                verdigris_relevance = self._analyze_verdigris_relevance(event)

                # Generate recommended actions
                recommended_actions = self._generate_recommended_actions(event, priority, trend)

                enhanced_signal = EnhancedBuyingSignal(
                    original_signal=event,
                    trend_analysis=trend,
                    priority_analysis=priority,
                    competitive_context=competitive_context,
                    verdigris_relevance=verdigris_relevance,
                    recommended_actions=recommended_actions
                )

                enhanced_signals.append(enhanced_signal)

            except Exception as e:
                print(f"⚠️ Error analyzing signal {event.get('description', 'Unknown')}: {e}")
                continue

        # Sort by priority score (highest first)
        enhanced_signals.sort(key=lambda x: x.priority_analysis.priority_score, reverse=True)

        print(f"✅ Enhanced analysis complete:")
        print(f"   🔥 Critical signals: {len([s for s in enhanced_signals if s.priority_analysis.priority_level == 'Critical'])}")
        print(f"   📈 High priority: {len([s for s in enhanced_signals if s.priority_analysis.priority_level == 'High'])}")
        print(f"   📊 Medium priority: {len([s for s in enhanced_signals if s.priority_analysis.priority_level == 'Medium'])}")

        return enhanced_signals

    def _categorize_signals(self, events: List[Dict]) -> Dict[str, List[Dict]]:
        """Group signals by category for trend analysis"""
        categorized = defaultdict(list)

        for event in events:
            category = self._categorize_single_signal(event)
            categorized[category].append(event)

        return dict(categorized)

    def _categorize_single_signal(self, event: Dict) -> str:
        """Categorize a single signal based on its content"""
        description = event.get('description', '').lower()

        for category, keywords in self.signal_categories.items():
            if any(keyword.lower() in description for keyword in keywords):
                return category

        return 'general'

    def _analyze_trends(self, signals_by_category: Dict[str, List[Dict]],
                       all_events: List[Dict]) -> Dict[str, BuyingSignalTrend]:
        """Analyze trends across signal categories"""
        trends = {}

        for category, signals in signals_by_category.items():
            if not signals:
                continue

            # Calculate recency factor (more recent = higher score)
            now = datetime.now()
            recency_scores = []

            for signal in signals:
                detected_date = signal.get('detected_date')
                if detected_date:
                    try:
                        if isinstance(detected_date, str):
                            signal_time = datetime.fromisoformat(detected_date.replace('Z', '+00:00'))
                        else:
                            signal_time = detected_date

                        days_old = (now - signal_time.replace(tzinfo=None)).days
                        recency_score = max(0, (30 - days_old) / 30)  # 30-day decay
                        recency_scores.append(recency_score)
                    except:
                        recency_scores.append(0.5)  # Default for unparseable dates
                else:
                    recency_scores.append(0.3)  # Default for missing dates

            avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0

            # Determine trend direction based on frequency and recency
            signal_count = len(signals)
            trend_strength = min(1.0, signal_count / 3.0)  # Normalize to 0-1

            if signal_count >= 3 and avg_recency > 0.6:
                trend_direction = "increasing"
            elif signal_count >= 2 and avg_recency > 0.4:
                trend_direction = "stable"
            else:
                trend_direction = "emerging"

            # Generate market context
            market_context = self._generate_market_context(category, signals)

            trends[category] = BuyingSignalTrend(
                signal_category=category,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                frequency_change=signal_count * 10,  # Simplified frequency metric
                recency_factor=avg_recency,
                market_context=market_context
            )

        return trends

    def _create_default_trend(self, category: str) -> BuyingSignalTrend:
        """Create default trend analysis for uncategorized signals"""
        return BuyingSignalTrend(
            signal_category=category,
            trend_direction="emerging",
            trend_strength=0.3,
            frequency_change=10.0,
            recency_factor=0.5,
            market_context=f"New {category} activity detected - monitor for developing trends"
        )

    def _calculate_priority_analysis(self, event: Dict, account_data: Dict,
                                   trend: BuyingSignalTrend) -> BuyingSignalPriority:
        """Calculate comprehensive priority analysis for a signal"""

        # Base priority components
        recency_score = self._calculate_recency_score(event)
        relevance_score = self._calculate_relevance_score(event)
        urgency_score = self._calculate_urgency_score(event, trend)
        size_score = self._calculate_size_score(event, account_data)
        confidence_score = event.get('confidence_score', 70) / 100

        # Weighted priority calculation
        priority_score = int(
            recency_score * self.priority_weights['recency'] * 100 +
            relevance_score * self.priority_weights['relevance'] * 100 +
            urgency_score * self.priority_weights['urgency'] * 100 +
            size_score * self.priority_weights['size'] * 100 +
            confidence_score * self.priority_weights['confidence'] * 100
        )

        # Determine priority level
        if priority_score >= 85:
            priority_level = "Critical"
        elif priority_score >= 70:
            priority_level = "High"
        elif priority_score >= 50:
            priority_level = "Medium"
        else:
            priority_level = "Low"

        # Generate urgency factors
        urgency_factors = self._identify_urgency_factors(event, trend)

        # Timing recommendation
        timing_recommendation = self._generate_timing_recommendation(priority_level, urgency_factors)

        # Confidence reasoning
        confidence_reasoning = self._explain_confidence_reasoning(event, priority_score)

        # Sales angle
        sales_angle = self._determine_sales_angle(event, trend)

        return BuyingSignalPriority(
            signal_id=event.get('id', 'unknown'),
            priority_score=priority_score,
            priority_level=priority_level,
            urgency_factors=urgency_factors,
            timing_recommendation=timing_recommendation,
            confidence_reasoning=confidence_reasoning,
            sales_angle=sales_angle
        )

    def _calculate_recency_score(self, event: Dict) -> float:
        """Calculate recency score (0-1) based on when signal was detected"""
        detected_date = event.get('detected_date')
        if not detected_date:
            return 0.3  # Default for missing date

        try:
            if isinstance(detected_date, str):
                signal_time = datetime.fromisoformat(detected_date.replace('Z', '+00:00'))
            else:
                signal_time = detected_date

            days_old = (datetime.now() - signal_time.replace(tzinfo=None)).days

            if days_old <= 3:
                return 1.0
            elif days_old <= 7:
                return 0.8
            elif days_old <= 14:
                return 0.6
            elif days_old <= 30:
                return 0.4
            else:
                return 0.2

        except:
            return 0.3

    def _calculate_relevance_score(self, event: Dict) -> float:
        """Calculate relevance score to Verdigris solutions"""
        description = event.get('description', '').lower()

        relevance_score = 0.0
        total_solutions = len(self.verdigris_solutions)

        for solution, keywords in self.verdigris_solutions.items():
            solution_relevance = sum(1 for keyword in keywords if keyword.lower() in description)
            if solution_relevance > 0:
                relevance_score += min(1.0, solution_relevance / 3.0)  # Cap per solution

        return min(1.0, relevance_score / 2.0)  # Normalize

    def _calculate_urgency_score(self, event: Dict, trend: BuyingSignalTrend) -> float:
        """Calculate urgency score based on signal type and trends"""
        base_urgency = 0.5

        # Boost urgency based on trend direction
        if trend.trend_direction == "increasing":
            base_urgency += 0.3
        elif trend.trend_direction == "stable":
            base_urgency += 0.1

        # Boost for time-sensitive signal types
        description = event.get('description', '').lower()
        urgent_keywords = ['funding', 'hiring', 'expansion', 'new', 'launch', 'merger']

        for keyword in urgent_keywords:
            if keyword in description:
                base_urgency += 0.1
                break

        return min(1.0, base_urgency)

    def _calculate_size_score(self, event: Dict, account_data: Dict) -> float:
        """Calculate opportunity size score"""
        if not account_data:
            return 0.5

        employee_count = account_data.get('employee_count', 50)

        if employee_count >= 500:
            return 1.0
        elif employee_count >= 100:
            return 0.8
        elif employee_count >= 50:
            return 0.6
        else:
            return 0.4

    def _identify_urgency_factors(self, event: Dict, trend: BuyingSignalTrend) -> List[str]:
        """Identify specific factors creating urgency"""
        factors = []

        description = event.get('description', '').lower()

        if trend.recency_factor > 0.8:
            factors.append("Very recent activity (within 3 days)")

        if trend.trend_direction == "increasing":
            factors.append(f"Increasing {trend.signal_category} activity trend")

        if 'funding' in description:
            factors.append("New funding creates budget availability")

        if any(word in description for word in ['new', 'launch', 'expansion']):
            factors.append("Growth initiatives indicate infrastructure needs")

        if any(word in description for word in ['hiring', 'team', 'scale']):
            factors.append("Scaling operations require monitoring solutions")

        return factors or ["Standard market timing considerations"]

    def _generate_timing_recommendation(self, priority_level: str, urgency_factors: List[str]) -> str:
        """Generate timing recommendation for outreach"""
        if priority_level == "Critical":
            return "Contact within 24-48 hours - strike while hot"
        elif priority_level == "High":
            return "Reach out within 1 week - good timing window"
        elif priority_level == "Medium":
            return "Contact within 2-3 weeks - steady follow-up"
        else:
            return "Monitor for additional signals before outreach"

    def _explain_confidence_reasoning(self, event: Dict, priority_score: int) -> str:
        """Explain confidence level reasoning"""
        confidence = event.get('confidence', 'Medium')
        source_type = event.get('source_type', 'Unknown')

        if confidence == 'High' and priority_score >= 70:
            return f"High confidence from {source_type} source with strong priority indicators"
        elif confidence == 'High':
            return f"Reliable {source_type} source provides high confidence"
        elif priority_score >= 80:
            return "Multiple priority factors increase confidence despite medium source reliability"
        else:
            return f"Standard confidence level from {source_type} source"

    def _determine_sales_angle(self, event: Dict, trend: BuyingSignalTrend) -> str:
        """Determine recommended sales approach angle"""
        description = event.get('description', '').lower()
        category = trend.signal_category

        if 'funding' in description:
            return "Focus on ROI and scalability - they have budget for infrastructure investment"
        elif category == 'technology':
            return "Lead with technical capabilities and modernization benefits"
        elif category == 'expansion':
            return "Emphasize monitoring and efficiency for new operations"
        elif category == 'leadership':
            return "Executive-level value proposition focusing on strategic outcomes"
        elif 'hiring' in description:
            return "Position as solution for managing increased operational complexity"
        else:
            return "Consultative approach - understand their current challenges first"

    def _analyze_competitive_context(self, event: Dict, category: str) -> str:
        """Analyze competitive timing and market context"""
        contexts = {
            'funding': "Newly funded companies prioritize infrastructure investments - ideal timing before they commit to alternatives",
            'expansion': "Expansion phases create urgency for monitoring solutions - competitors will be targeting this opportunity",
            'technology': "Technology modernization indicates openness to new solutions - window of opportunity before status quo sets",
            'leadership': "Leadership changes create opportunity to introduce new vendor relationships",
            'partnership': "Partnership announcements may indicate increased infrastructure needs or budget availability",
            'product': "New product launches require additional monitoring and optimization capabilities"
        }

        return contexts.get(category, "Standard competitive timing - monitor for additional signals")

    def _analyze_verdigris_relevance(self, event: Dict) -> str:
        """Analyze specific Verdigris solution relevance"""
        description = event.get('description', '').lower()

        if any(word in description for word in ['energy', 'power', 'sustainability']):
            return "Direct energy monitoring opportunity - core Verdigris value proposition"
        elif any(word in description for word in ['AI', 'analytics', 'data']):
            return "AI analytics angle - position advanced monitoring insights"
        elif any(word in description for word in ['iot', 'sensors', 'connected']):
            return "IoT platform opportunity - emphasize connected monitoring ecosystem"
        elif any(word in description for word in ['cost', 'efficiency', 'optimization']):
            return "Cost optimization focus - highlight energy savings and ROI"
        elif any(word in description for word in ['expansion', 'growth', 'scaling']):
            return "Growth enablement - monitoring infrastructure for new facilities"
        else:
            return "General infrastructure opportunity - explore specific monitoring needs"

    def _generate_recommended_actions(self, event: Dict, priority: BuyingSignalPriority,
                                    trend: BuyingSignalTrend) -> List[str]:
        """Generate specific recommended actions"""
        actions = []

        if priority.priority_level == "Critical":
            actions.append("🔥 Immediate: Call within 24 hours")
            actions.append("📧 Send personalized email referencing specific trigger event")

        actions.append(f"🎯 Lead with: {priority.sales_angle}")

        if trend.trend_direction == "increasing":
            actions.append("📈 Emphasize timing and market momentum")

        if event.get('source_url'):
            actions.append("📰 Reference the specific news/source in outreach")

        actions.append("🤝 Research key contacts in relevant departments")
        actions.append("📋 Prepare case studies relevant to their industry/situation")

        return actions

    def _generate_market_context(self, category: str, signals: List[Dict]) -> str:
        """Generate market context explanation"""
        contexts = {
            'funding': f"VC funding activity creates infrastructure investment opportunities ({len(signals)} recent signals)",
            'expansion': f"Market expansion trends indicate growth infrastructure needs ({len(signals)} expansion signals)",
            'technology': f"Technology modernization wave across industry ({len(signals)} tech initiatives)",
            'leadership': f"Leadership transition period creating vendor evaluation opportunities ({len(signals)} changes)",
            'partnership': f"Partnership activity indicates resource availability ({len(signals)} announcements)",
            'product': f"Product innovation cycle creating monitoring needs ({len(signals)} launches)"
        }

        return contexts.get(category, f"General market activity in {category} category ({len(signals)} signals)")

    def generate_buying_signals_report(self, enhanced_signals: List[EnhancedBuyingSignal]) -> str:
        """Generate comprehensive buying signals analysis report"""

        if not enhanced_signals:
            return "No buying signals found for analysis."

        report = f"""
# Enhanced Buying Signals Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Executive Summary
- **Total Signals Analyzed**: {len(enhanced_signals)}
- **Critical Priority**: {len([s for s in enhanced_signals if s.priority_analysis.priority_level == 'Critical'])}
- **High Priority**: {len([s for s in enhanced_signals if s.priority_analysis.priority_level == 'High'])}
- **Immediate Action Required**: {len([s for s in enhanced_signals if 'within 24' in s.priority_analysis.timing_recommendation])}

## 🔥 Critical Priority Signals
"""

        critical_signals = [s for s in enhanced_signals if s.priority_analysis.priority_level == 'Critical']
        for i, signal in enumerate(critical_signals[:3], 1):  # Top 3 critical
            report += f"""
### Signal {i}: {signal.original_signal.get('description', 'Unknown Signal')}
- **Priority Score**: {signal.priority_analysis.priority_score}/100
- **Timing**: {signal.priority_analysis.timing_recommendation}
- **Sales Angle**: {signal.priority_analysis.sales_angle}
- **Verdigris Relevance**: {signal.verdigris_relevance}
- **Next Actions**: {', '.join(signal.recommended_actions[:3])}
"""

        report += f"""
## 📊 Trend Analysis Summary
"""

        # Group by trend categories
        categories = set()
        for signal in enhanced_signals:
            categories.add(signal.trend_analysis.signal_category)

        for category in sorted(categories):
            category_signals = [s for s in enhanced_signals if s.trend_analysis.signal_category == category]
            if category_signals:
                trend = category_signals[0].trend_analysis
                report += f"""
### {category.title()} Signals
- **Trend Direction**: {trend.trend_direction.title()}
- **Strength**: {trend.trend_strength:.1%}
- **Market Context**: {trend.market_context}
- **Signal Count**: {len(category_signals)}
"""

        return report.strip()

    def convert_to_dashboard_format(self, enhanced_signals: List[EnhancedBuyingSignal]) -> List[Dict]:
        """Convert enhanced signals to dashboard-friendly format"""

        dashboard_signals = []

        for signal in enhanced_signals:
            dashboard_signal = {
                'id': signal.original_signal.get('id'),
                'description': signal.original_signal.get('description'),
                'priority_score': signal.priority_analysis.priority_score,
                'priority_level': signal.priority_analysis.priority_level,
                'urgency_factors': signal.priority_analysis.urgency_factors,
                'timing_recommendation': signal.priority_analysis.timing_recommendation,
                'sales_angle': signal.priority_analysis.sales_angle,
                'trend_direction': signal.trend_analysis.trend_direction,
                'trend_strength': signal.trend_analysis.trend_strength,
                'verdigris_relevance': signal.verdigris_relevance,
                'competitive_context': signal.competitive_context,
                'recommended_actions': signal.recommended_actions,
                'source_url': signal.original_signal.get('source_url'),
                'confidence': signal.original_signal.get('confidence'),
                'detected_date': signal.original_signal.get('detected_date'),
                'market_context': signal.trend_analysis.market_context,
                'confidence_reasoning': signal.priority_analysis.confidence_reasoning
            }

            dashboard_signals.append(dashboard_signal)

        return dashboard_signals

# Export for use by other modules
enhanced_buying_signals_analyzer = EnhancedBuyingSignalsAnalyzer()

def main():
    """Test the enhanced buying signals analyzer"""
    # This would be called with real trigger events data
    print("🔍 Enhanced Buying Signals Analyzer initialized")
    print("💡 Use analyze_buying_signals() method to process trigger events")

if __name__ == "__main__":
    main()