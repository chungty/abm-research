#!/usr/bin/env python3
"""
Apollo API Usage Monitor and Rate Limiter
Prevents excessive API usage and tracks costs
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ApolloUsageMonitor:
    """Monitor and limit Apollo API usage to control costs"""

    def __init__(self, daily_limit: int = 100, hourly_limit: int = 20):
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
        self.usage_file = '/Users/chungty/Projects/vdg-clean/abm-research/apollo_usage.json'
        self.cache_file = '/Users/chungty/Projects/vdg-clean/abm-research/apollo_cache.json'
        self.load_usage_data()
        self.load_cache_data()

    def load_usage_data(self):
        """Load usage tracking data"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    self.usage_data = json.load(f)
            else:
                self.usage_data = {
                    'daily_usage': {},
                    'hourly_usage': {},
                    'total_calls': 0,
                    'estimated_cost': 0.0
                }
        except:
            self.usage_data = {
                'daily_usage': {},
                'hourly_usage': {},
                'total_calls': 0,
                'estimated_cost': 0.0
            }

    def load_cache_data(self):
        """Load cached API results to avoid duplicate calls"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
            else:
                self.cache_data = {}
        except:
            self.cache_data = {}

    def save_usage_data(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save usage data: {e}")

    def save_cache_data(self):
        """Save cache data to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save cache data: {e}")

    def check_rate_limits(self) -> Dict[str, bool]:
        """Check if we're within rate limits"""
        today = datetime.now().strftime('%Y-%m-%d')
        current_hour = datetime.now().strftime('%Y-%m-%d-%H')

        daily_usage = self.usage_data.get('daily_usage', {}).get(today, 0)
        hourly_usage = self.usage_data.get('hourly_usage', {}).get(current_hour, 0)

        return {
            'can_make_call': daily_usage < self.daily_limit and hourly_usage < self.hourly_limit,
            'daily_remaining': max(0, self.daily_limit - daily_usage),
            'hourly_remaining': max(0, self.hourly_limit - hourly_usage),
            'daily_used': daily_usage,
            'hourly_used': hourly_usage
        }

    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached API result if available and not expired"""
        if cache_key in self.cache_data:
            cached_item = self.cache_data[cache_key]
            cached_time = datetime.fromisoformat(cached_item['timestamp'])

            # Cache expires after 24 hours
            if datetime.now() - cached_time < timedelta(hours=24):
                print(f"🗄️ Using cached result for {cache_key}")
                return cached_item['data']
            else:
                # Remove expired cache
                del self.cache_data[cache_key]
                self.save_cache_data()

        return None

    def cache_result(self, cache_key: str, data: Dict):
        """Cache API result"""
        self.cache_data[cache_key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache_data()

    def record_api_call(self, call_type: str = 'people_search', estimated_cost: float = 0.10):
        """Record an API call for tracking"""
        today = datetime.now().strftime('%Y-%m-%d')
        current_hour = datetime.now().strftime('%Y-%m-%d-%H')

        # Update daily usage
        if today not in self.usage_data['daily_usage']:
            self.usage_data['daily_usage'][today] = 0
        self.usage_data['daily_usage'][today] += 1

        # Update hourly usage
        if current_hour not in self.usage_data['hourly_usage']:
            self.usage_data['hourly_usage'][current_hour] = 0
        self.usage_data['hourly_usage'][current_hour] += 1

        # Update totals
        self.usage_data['total_calls'] += 1
        self.usage_data['estimated_cost'] += estimated_cost

        self.save_usage_data()

        print(f"📊 API Call Recorded: {call_type} (+${estimated_cost:.2f})")

    def get_usage_summary(self) -> Dict:
        """Get usage summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        current_hour = datetime.now().strftime('%Y-%m-%d-%H')

        limits = self.check_rate_limits()

        return {
            'total_calls': self.usage_data['total_calls'],
            'estimated_total_cost': self.usage_data['estimated_cost'],
            'today_usage': self.usage_data.get('daily_usage', {}).get(today, 0),
            'hour_usage': self.usage_data.get('hourly_usage', {}).get(current_hour, 0),
            'daily_limit': self.daily_limit,
            'hourly_limit': self.hourly_limit,
            'daily_remaining': limits['daily_remaining'],
            'hourly_remaining': limits['hourly_remaining'],
            'cache_entries': len(self.cache_data),
            'can_make_calls': limits['can_make_call']
        }

    def clean_old_data(self):
        """Clean old usage and cache data"""
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        # Clean old daily usage
        old_days = [day for day in self.usage_data.get('daily_usage', {}) if day < cutoff_date]
        for day in old_days:
            del self.usage_data['daily_usage'][day]

        # Clean old hourly usage (keep last 7 days)
        cutoff_hour = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d-%H')
        old_hours = [hour for hour in self.usage_data.get('hourly_usage', {}) if hour < cutoff_hour]
        for hour in old_hours:
            del self.usage_data['hourly_usage'][hour]

        # Clean expired cache (older than 24 hours)
        expired_keys = []
        for key, item in self.cache_data.items():
            cached_time = datetime.fromisoformat(item['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=24):
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache_data[key]

        if old_days or old_hours or expired_keys:
            self.save_usage_data()
            self.save_cache_data()
            print(f"🧹 Cleaned {len(old_days)} old days, {len(old_hours)} old hours, {len(expired_keys)} expired cache entries")

class SafeApolloAPI:
    """Apollo API wrapper with usage monitoring and rate limiting"""

    def __init__(self, api_key: str, daily_limit: int = 100):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }
        self.usage_monitor = ApolloUsageMonitor(daily_limit=daily_limit)

    def search_people_safe(self, company_domain: str, limit: int = 25) -> List[Dict]:
        """Safe people search with usage monitoring"""

        # Check rate limits
        limits = self.usage_monitor.check_rate_limits()
        if not limits['can_make_call']:
            print(f"❌ Rate limit exceeded!")
            print(f"   Daily: {limits['daily_used']}/{self.usage_monitor.daily_limit}")
            print(f"   Hourly: {limits['hourly_used']}/{self.usage_monitor.hourly_limit}")
            return []

        # Check cache first
        cache_key = f"people_search_{company_domain}_{limit}"
        cached_result = self.usage_monitor.get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Make API call
        print(f"🔍 Apollo: Making new API call for {company_domain} (Daily: {limits['daily_used']}/{self.usage_monitor.daily_limit})")

        url = f"{self.base_url}/mixed_people/search"
        job_titles = [
            "VP Data Center Operations", "Director Data Center", "VP Infrastructure",
            "Director Infrastructure", "Head of Data Center", "VP Critical Infrastructure",
            "Director Operations", "VP Operations", "Manager Data Center"
        ]

        payload = {
            "api_key": self.api_key,
            "q_organization_domains": company_domain,
            "page": 1,
            "per_page": min(limit, 100),
            "person_titles": job_titles,
            "prospected_by_current_team": ["no"],
            "q_person_seniorities": ["vp", "director", "manager", "head"],
            "include_emails": True,
            "include_phone_numbers": False
        }

        try:
            import requests
            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                contacts = data.get('people', [])

                # Record usage
                self.usage_monitor.record_api_call('people_search', estimated_cost=0.10)

                # Cache result
                self.usage_monitor.cache_result(cache_key, contacts)

                print(f"✅ Apollo: Found {len(contacts)} contacts")
                return contacts

            elif response.status_code == 429:
                print("⏳ Apollo: Rate limit hit by API provider")
                time.sleep(60)
                return []
            else:
                print(f"❌ Apollo: API error {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Apollo: Exception {e}")
            return []

    def get_usage_summary(self) -> Dict:
        """Get current usage summary"""
        return self.usage_monitor.get_usage_summary()

    def clean_old_data(self):
        """Clean old usage data"""
        self.usage_monitor.clean_old_data()

def main():
    """Test usage monitoring"""

    apollo_key = os.getenv('APOLLO_API_KEY')
    if not apollo_key:
        print("❌ APOLLO_API_KEY not found")
        return

    # Initialize safe Apollo API
    safe_apollo = SafeApolloAPI(apollo_key, daily_limit=50)  # Conservative daily limit

    # Show current usage
    usage = safe_apollo.get_usage_summary()
    print(f"📊 Apollo API Usage Summary:")
    print(f"   Total Calls: {usage['total_calls']}")
    print(f"   Estimated Cost: ${usage['estimated_total_cost']:.2f}")
    print(f"   Today: {usage['today_usage']}/{usage['daily_limit']} calls")
    print(f"   This Hour: {usage['hour_usage']}/{usage['hourly_limit']} calls")
    print(f"   Cache Entries: {usage['cache_entries']}")
    print(f"   Can Make Calls: {'✅' if usage['can_make_calls'] else '❌'}")

    # Test search (will use cache if available)
    if usage['can_make_calls']:
        print(f"\n🧪 Testing safe search...")
        results = safe_apollo.search_people_safe('equinix.com', limit=5)
        print(f"✅ Found {len(results)} contacts")
    else:
        print(f"\n⚠️ Rate limit reached - no API calls will be made")

    # Clean old data
    safe_apollo.clean_old_data()

if __name__ == '__main__':
    main()
