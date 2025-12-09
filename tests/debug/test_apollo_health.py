#!/usr/bin/env python3
"""
Test Apollo API health and credentials
"""

import os

import requests


def test_apollo_health():
    """Test Apollo API health and credentials"""

    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        print("❌ APOLLO_API_KEY environment variable not set")
        return

    print(f"🔑 Using Apollo API Key: {api_key[:15]}...")

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": api_key,
    }

    try:
        print("🏥 Testing Apollo API health...")
        response = requests.get("https://api.apollo.io/v1/auth/health", headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Apollo API is healthy")
            print(f"Credits remaining: {data.get('credits_remaining', 'Unknown')}")
        else:
            print("❌ Apollo API health check failed")

    except Exception as e:
        print(f"❌ Error testing Apollo API: {e}")


if __name__ == "__main__":
    test_apollo_health()
