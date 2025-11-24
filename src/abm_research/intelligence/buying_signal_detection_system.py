#!/usr/bin/env python3
"""
Automated Buying Signal Detection System
Real-time monitoring of news, website changes, and social signals for trigger events
"""

import os
import requests
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, asdict
import random
from bs4 import BeautifulSoup
import hashlib
import openai

from abm_config import config

@dataclass
class TriggerEvent:
    """Structured trigger event data"""
    event_type: str  # 'Expansion', 'Leadership Change', 'AI Workload', etc.
    event_description: str
    company_name: str
    source_type: str  # 'news', 'website', 'social', 'press_release'
    source_url: str
    detected_date: str
    confidence_score: float  # 0-100
    relevance_score: float  # 0-100 (relevance to Verdigris Signals)
    urgency_level: str  # 'High', 'Medium', 'Low'
    potential_impact: str
    follow_up_actions: List[str]

@dataclass
class BuyingSignal:
    """Buying signal with context"""
    signal_type: str
    strength: float  # 0-100
    description: str
    evidence: List[str]
    timeline: str
    probability: float

class NewsMonitor:
    """Monitor news sources for buying signals"""

    def __init__(self):
        # In production, would use Google News API, NewsAPI, etc.
        self.news_sources = [
            'https://www.datacenterknowledge.com',
            'https://www.datacenterdynamics.com',
            'https://techcrunch.com',
            'https://venturebeat.com'
        ]

        self.power_keywords = [
            'data center', 'power consumption', 'energy efficiency',
            'cooling', 'uptime', 'outage', 'AI infrastructure',
            'GPU cluster', 'cloud expansion', 'sustainability',
            'carbon neutral', 'PUE', 'power monitoring',
            'energy management', 'capacity planning'
        ]

        self.trigger_keywords = {
            'Expansion': [
                'expanding', 'new data center', 'opening', 'facility',
                'building', 'construction', 'capacity increase'
            ],
            'Leadership Change': [
                'appointed', 'hired', 'joins as', 'new CTO',
                'new VP', 'chief technology officer', 'promoted to'
            ],
            'AI Workload': [
                'AI infrastructure', 'machine learning', 'GPU',
                'artificial intelligence', 'ML workload', 'neural network'
            ],
            'Energy Pressure': [
                'power costs', 'energy efficiency', 'sustainability',
                'carbon footprint', 'green initiative', 'renewable energy'
            ],
            'Incident': [
                'outage', 'downtime', 'failure', 'incident',
                'power loss', 'cooling failure', 'service disruption'
            ],
            'Sustainability': [
                'net zero', 'carbon neutral', 'green energy',
                'renewable power', 'sustainability initiative', 'ESG'
            ]
        }

    def monitor_news_for_company(self, company_name: str, domain: str) -> List[TriggerEvent]:
        """Monitor news sources for company-specific trigger events"""

        print(f"   📰 Monitoring news for: {company_name}")

        trigger_events = []

        # Simulate news monitoring (production would use real APIs)
        simulated_news = self._generate_realistic_news_events(company_name, domain)

        for news_item in simulated_news:
            event = self._analyze_news_for_triggers(news_item, company_name)
            if event:
                trigger_events.append(event)

        print(f"      ✅ Found {len(trigger_events)} trigger events")
        return trigger_events

    def _generate_realistic_news_events(self, company_name: str, domain: str) -> List[Dict]:
        """Generate realistic news events for demonstration"""

        # Simulate different types of news events
        news_events = []

        # Expansion event
        if random.random() > 0.3:  # 70% chance
            news_events.append({
                'title': f'{company_name} Announces Major Infrastructure Expansion',
                'content': f'{company_name} today announced plans to expand their cloud infrastructure capacity by 200% over the next 18 months, including new GPU clusters for AI workloads. The expansion will require significant power monitoring and energy management systems.',
                'url': f'https://techcrunch.com/{company_name.lower().replace(" ", "-")}-expansion',
                'date': datetime.now() - timedelta(days=random.randint(1, 7)),
                'source': 'TechCrunch'
            })

        # Leadership change
        if random.random() > 0.5:  # 50% chance
            news_events.append({
                'title': f'{company_name} Appoints New VP of Infrastructure',
                'content': f'{company_name} has appointed Maria Gonzalez as Vice President of Infrastructure, bringing 15 years of experience in data center operations and power management. Gonzalez will oversee the companys growing infrastructure needs.',
                'url': f'https://datacenterknowledge.com/{company_name.lower()}-new-vp',
                'date': datetime.now() - timedelta(days=random.randint(3, 14)),
                'source': 'Data Center Knowledge'
            })

        # AI workload announcement
        if random.random() > 0.4:  # 60% chance
            news_events.append({
                'title': f'{company_name} Launches New AI Infrastructure Services',
                'content': f'{company_name} unveiled new AI-optimized infrastructure services, featuring high-performance GPU clusters and specialized power monitoring for machine learning workloads. The service addresses growing demand for AI compute capacity.',
                'url': f'https://venturebeat.com/{company_name.lower()}-ai-services',
                'date': datetime.now() - timedelta(days=random.randint(5, 21)),
                'source': 'VentureBeat'
            })

        return news_events

    def _analyze_news_for_triggers(self, news_item: Dict, company_name: str) -> Optional[TriggerEvent]:
        """Analyze news item for trigger events"""

        content = f"{news_item['title']} {news_item['content']}".lower()

        # Check for trigger keywords
        detected_triggers = []
        for event_type, keywords in self.trigger_keywords.items():
            if any(keyword in content for keyword in keywords):
                detected_triggers.append(event_type)

        if not detected_triggers:
            return None

        # Use the first (most relevant) trigger type
        event_type = detected_triggers[0]

        # Calculate confidence based on keyword matches
        keyword_matches = sum(1 for keywords in self.trigger_keywords[event_type]
                             if any(kw in content for kw in keywords))
        confidence_score = min(100, keyword_matches * 25 + 50)

        # Calculate relevance to Verdigris Signals
        power_relevance = sum(1 for kw in self.power_keywords if kw in content)
        relevance_score = min(100, power_relevance * 15 + 40)

        # Determine urgency
        urgency_indicators = {
            'immediately': 'High',
            'urgent': 'High',
            'this quarter': 'High',
            'next month': 'Medium',
            'planning': 'Medium',
            'considering': 'Low',
            'future': 'Low'
        }

        urgency_level = 'Medium'  # Default
        for indicator, level in urgency_indicators.items():
            if indicator in content:
                urgency_level = level
                break

        # Generate follow-up actions
        follow_up_actions = self._generate_follow_up_actions(event_type, urgency_level)

        trigger_event = TriggerEvent(
            event_type=event_type,
            event_description=news_item['title'],
            company_name=company_name,
            source_type='news',
            source_url=news_item['url'],
            detected_date=datetime.now().isoformat(),
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            urgency_level=urgency_level,
            potential_impact=f"Potential new {event_type.lower()} opportunity for Verdigris Signals",
            follow_up_actions=follow_up_actions
        )

        return trigger_event

    def _generate_follow_up_actions(self, event_type: str, urgency_level: str) -> List[str]:
        """Generate appropriate follow-up actions"""

        base_actions = {
            'Expansion': [
                'Contact infrastructure team about power monitoring needs',
                'Share case studies of similar expansion projects',
                'Offer energy efficiency assessment'
            ],
            'Leadership Change': [
                'Reach out to new leadership with Verdigris introduction',
                'Share industry best practices and benchmarks',
                'Offer executive briefing on power monitoring ROI'
            ],
            'AI Workload': [
                'Demonstrate AI infrastructure power monitoring capabilities',
                'Share GPU cluster power optimization case studies',
                'Offer pilot program for AI workload monitoring'
            ],
            'Energy Pressure': [
                'Share energy cost reduction success stories',
                'Offer power efficiency audit',
                'Demonstrate sustainability reporting features'
            ],
            'Incident': [
                'Share proactive monitoring value proposition',
                'Offer incident prevention case studies',
                'Demonstrate predictive maintenance capabilities'
            ],
            'Sustainability': [
                'Share carbon footprint reduction case studies',
                'Offer sustainability metrics and reporting demo',
                'Demonstrate ESG compliance features'
            ]
        }

        actions = base_actions.get(event_type, ['Contact relevant stakeholders'])

        # Add urgency-based actions
        if urgency_level == 'High':
            actions.insert(0, 'Schedule immediate executive call')
        elif urgency_level == 'Medium':
            actions.insert(0, 'Schedule discovery call within 2 weeks')

        return actions

class WebsiteChangeDetector:
    """Monitor company websites for changes indicating buying signals"""

    def __init__(self):
        self.monitored_pages = [
            '/careers', '/jobs', '/about', '/news',
            '/press', '/blog', '/technology'
        ]

        self.signal_patterns = {
            'hiring_infrastructure': [
                'infrastructure engineer', 'power engineer',
                'data center', 'facilities manager', 'operations engineer'
            ],
            'technology_adoption': [
                'monitoring system', 'power management',
                'energy efficiency', 'sustainability initiative'
            ],
            'expansion_signals': [
                'new location', 'expanding', 'growth',
                'scaling', 'capacity increase'
            ]
        }

    def monitor_website_changes(self, company_name: str, domain: str) -> List[TriggerEvent]:
        """Monitor website for changes indicating buying signals"""

        print(f"   🌐 Monitoring website changes for: {domain}")

        trigger_events = []

        # Simulate website monitoring (production would track actual changes)
        detected_changes = self._simulate_website_changes(company_name, domain)

        for change in detected_changes:
            event = self._analyze_change_for_signals(change, company_name)
            if event:
                trigger_events.append(event)

        print(f"      ✅ Found {len(trigger_events)} website signals")
        return trigger_events

    def _simulate_website_changes(self, company_name: str, domain: str) -> List[Dict]:
        """Simulate website changes for demonstration"""

        changes = []

        # Simulate job posting changes
        if random.random() > 0.4:  # 60% chance
            changes.append({
                'type': 'new_job_posting',
                'page': '/careers',
                'content': 'Senior Infrastructure Engineer - Data Center Operations. We are seeking an experienced infrastructure engineer to manage our growing data center operations and power monitoring systems.',
                'detected_date': datetime.now() - timedelta(days=random.randint(1, 5)),
                'change_type': 'addition'
            })

        # Simulate technology announcements
        if random.random() > 0.6:  # 40% chance
            changes.append({
                'type': 'technology_update',
                'page': '/technology',
                'content': 'Implementing advanced monitoring systems for our AI infrastructure to optimize power consumption and reduce operational costs.',
                'detected_date': datetime.now() - timedelta(days=random.randint(2, 10)),
                'change_type': 'modification'
            })

        return changes

    def _analyze_change_for_signals(self, change: Dict, company_name: str) -> Optional[TriggerEvent]:
        """Analyze website change for buying signals"""

        content = change['content'].lower()

        # Detect signal type
        signal_type = None
        confidence = 0

        for signal, patterns in self.signal_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in content)
            if matches > 0:
                signal_type = signal
                confidence = matches * 25
                break

        if not signal_type:
            return None

        # Map signal type to event type
        event_type_mapping = {
            'hiring_infrastructure': 'Expansion',
            'technology_adoption': 'AI Workload',
            'expansion_signals': 'Expansion'
        }

        event_type = event_type_mapping.get(signal_type, 'Expansion')

        trigger_event = TriggerEvent(
            event_type=event_type,
            event_description=f"Website change detected: {change['type']}",
            company_name=company_name,
            source_type='website',
            source_url=f"https://{company_name.lower().replace(' ', '')}.com{change['page']}",
            detected_date=datetime.now().isoformat(),
            confidence_score=min(100, confidence + 40),
            relevance_score=70.0,  # Website changes are moderately relevant
            urgency_level='Medium',
            potential_impact=f"Company is actively {signal_type.replace('_', ' ')}",
            follow_up_actions=[
                'Monitor for additional hiring signals',
                'Research specific technology initiatives',
                'Engage with hiring manager or technical lead'
            ]
        )

        return trigger_event

class SocialSignalDetector:
    """Monitor social media for buying signals"""

    def __init__(self):
        self.platforms = ['linkedin', 'twitter']
        self.executive_keywords = [
            'CTO', 'VP Engineering', 'Head of Infrastructure',
            'Director of Operations', 'Chief Technology'
        ]

    def monitor_social_signals(self, company_name: str) -> List[TriggerEvent]:
        """Monitor social media for buying signals"""

        print(f"   📱 Monitoring social signals for: {company_name}")

        trigger_events = []

        # Simulate social media monitoring
        social_posts = self._simulate_social_activity(company_name)

        for post in social_posts:
            event = self._analyze_social_post_for_signals(post, company_name)
            if event:
                trigger_events.append(event)

        print(f"      ✅ Found {len(trigger_events)} social signals")
        return trigger_events

    def _simulate_social_activity(self, company_name: str) -> List[Dict]:
        """Simulate social media activity"""

        posts = []

        # Simulate executive posts about challenges
        if random.random() > 0.5:  # 50% chance
            posts.append({
                'platform': 'linkedin',
                'author': 'Alex Thompson, VP Infrastructure',
                'content': 'Managing power consumption in our growing AI infrastructure is becoming increasingly complex. Looking for better visibility into our energy usage patterns. #DataCenter #AI #Infrastructure',
                'engagement': {'likes': 45, 'comments': 12, 'shares': 8},
                'date': datetime.now() - timedelta(days=random.randint(1, 7)),
                'post_type': 'pain_point'
            })

        return posts

    def _analyze_social_post_for_signals(self, post: Dict, company_name: str) -> Optional[TriggerEvent]:
        """Analyze social post for buying signals"""

        content = post['content'].lower()

        # Check for pain point indicators
        pain_points = [
            'challenging', 'difficult', 'struggling', 'complex',
            'looking for', 'need better', 'seeking', 'problems'
        ]

        has_pain_point = any(point in content for point in pain_points)

        # Check for power/infrastructure keywords
        relevant_keywords = [
            'power', 'energy', 'monitoring', 'infrastructure',
            'data center', 'efficiency', 'consumption'
        ]

        has_relevance = any(keyword in content for keyword in relevant_keywords)

        if not (has_pain_point and has_relevance):
            return None

        # Calculate confidence based on engagement
        engagement_score = post['engagement']['likes'] + post['engagement']['comments'] * 2
        confidence = min(100, engagement_score + 30)

        trigger_event = TriggerEvent(
            event_type='Energy Pressure',
            event_description=f"Executive social post indicates power monitoring challenges",
            company_name=company_name,
            source_type='social',
            source_url=f"https://{post['platform']}.com/posts/example",
            detected_date=datetime.now().isoformat(),
            confidence_score=confidence,
            relevance_score=85.0,  # High relevance for direct pain point expression
            urgency_level='High',  # Executive pain points are urgent
            potential_impact="Executive expressing direct pain point - high conversion probability",
            follow_up_actions=[
                'Engage directly with the executive post',
                'Offer to share relevant case study or solution brief',
                'Schedule executive briefing call',
                'Connect with mutual contacts for warm introduction'
            ]
        )

        return trigger_event

class BuyingSignalDetection:
    """Orchestrate buying signal detection across all sources"""

    def __init__(self):
        self.news_monitor = NewsMonitor()
        self.website_detector = WebsiteChangeDetector()
        self.social_detector = SocialSignalDetector()

    def detect_signals_for_account(self, company_name: str, domain: str) -> Dict:
        """Comprehensive buying signal detection"""

        print(f"⚡ BUYING SIGNAL DETECTION: {company_name}")
        print("=" * 50)

        all_signals = []
        source_stats = {}

        # 1. News Monitoring
        print(f"\n📰 SOURCE 1: NEWS MONITORING")
        print("-" * 30)

        try:
            news_signals = self.news_monitor.monitor_news_for_company(company_name, domain)
            all_signals.extend(news_signals)
            source_stats['news'] = len(news_signals)
            print(f"✅ News: {len(news_signals)} signals")

        except Exception as e:
            print(f"❌ News error: {e}")
            source_stats['news'] = 0

        # 2. Website Change Detection
        print(f"\n🌐 SOURCE 2: WEBSITE MONITORING")
        print("-" * 35)

        try:
            website_signals = self.website_detector.monitor_website_changes(company_name, domain)
            all_signals.extend(website_signals)
            source_stats['website'] = len(website_signals)
            print(f"✅ Website: {len(website_signals)} signals")

        except Exception as e:
            print(f"❌ Website error: {e}")
            source_stats['website'] = 0

        # 3. Social Media Monitoring
        print(f"\n📱 SOURCE 3: SOCIAL MONITORING")
        print("-" * 35)

        try:
            social_signals = self.social_detector.monitor_social_signals(company_name)
            all_signals.extend(social_signals)
            source_stats['social'] = len(social_signals)
            print(f"✅ Social: {len(social_signals)} signals")

        except Exception as e:
            print(f"❌ Social error: {e}")
            source_stats['social'] = 0

        # 4. Signal Analysis and Prioritization
        print(f"\n🎯 SIGNAL ANALYSIS & PRIORITIZATION")
        print("-" * 40)

        prioritized_signals = self._prioritize_signals(all_signals)
        high_priority_signals = [s for s in prioritized_signals if s.urgency_level == 'High']

        print(f"📊 SIGNAL SUMMARY:")
        print(f"   📥 Total signals: {len(all_signals)}")
        print(f"   🚨 High priority: {len(high_priority_signals)}")
        print(f"   📈 Average relevance: {self._calculate_average_relevance(all_signals):.1f}%")

        return {
            'signals': prioritized_signals,
            'source_stats': source_stats,
            'high_priority_count': len(high_priority_signals),
            'total_signals': len(all_signals)
        }

    def _prioritize_signals(self, signals: List[TriggerEvent]) -> List[TriggerEvent]:
        """Prioritize signals by urgency, relevance, and confidence"""

        # Calculate priority score for each signal
        for signal in signals:
            urgency_weight = {'High': 3, 'Medium': 2, 'Low': 1}[signal.urgency_level]
            priority_score = (
                signal.relevance_score * 0.4 +
                signal.confidence_score * 0.3 +
                urgency_weight * 10
            )
            signal.priority_score = priority_score

        # Sort by priority score
        return sorted(signals, key=lambda s: getattr(s, 'priority_score', 0), reverse=True)

    def _calculate_average_relevance(self, signals: List[TriggerEvent]) -> float:
        """Calculate average relevance score"""
        if not signals:
            return 0.0

        total_relevance = sum(s.relevance_score for s in signals)
        return total_relevance / len(signals)

def main():
    """Test buying signal detection system"""

    print("⚡ BUYING SIGNAL DETECTION SYSTEM TEST")
    print("=" * 60)

    # Test with Genesis Cloud
    detector = BuyingSignalDetection()
    results = detector.detect_signals_for_account("Genesis Cloud", "genesiscloud.com")

    print(f"\n🎉 SIGNAL DETECTION COMPLETE!")
    print(f"⚡ Found {results['total_signals']} total signals")
    print(f"🚨 {results['high_priority_count']} high-priority signals")

    print(f"\n📈 Source Breakdown:")
    for source, count in results['source_stats'].items():
        print(f"   {source}: {count} signals")

    # Show top signals
    print(f"\n🚨 TOP PRIORITY SIGNALS:")
    for i, signal in enumerate(results['signals'][:3], 1):
        print(f"   {i}. {signal.event_type}: {signal.event_description}")
        print(f"      Source: {signal.source_type} | Urgency: {signal.urgency_level}")
        print(f"      Relevance: {signal.relevance_score:.0f}% | Confidence: {signal.confidence_score:.0f}%")
        if signal.follow_up_actions:
            print(f"      Next Step: {signal.follow_up_actions[0]}")

if __name__ == "__main__":
    main()