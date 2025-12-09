#!/usr/bin/env python3
"""
Debug Apollo bulk_match API 400 error
Test the bulk enrichment endpoint to understand the issue
"""

import json
import os
import sys

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def debug_apollo_bulk_match():
    """
    Test Apollo bulk_match endpoint to diagnose 400 error
    """
    print("🔍 Debugging Apollo bulk_match API 400 Error")
    print("=" * 50)

    api_key = os.getenv("APOLLO_API_KEY")
    if not api_key:
        print("❌ APOLLO_API_KEY not found")
        return

    print(f"🔑 Using API Key: {api_key[:15]}...")

    base_url = "https://api.apollo.io/v1"
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json", "Cache-Control": "no-cache", "X-Api-Key": api_key}
    )

    # Test with minimal valid data first
    test_cases = [
        {
            "name": "Minimal Test",
            "payload": {
                "details": [
                    {"first_name": "John", "last_name": "Doe", "organization_name": "Test Company"}
                ]
            },
        },
        {
            "name": "With Email Reveal",
            "payload": {
                "details": [
                    {"first_name": "John", "last_name": "Doe", "organization_name": "Test Company"}
                ],
                "reveal_personal_emails": True,
            },
        },
        {
            "name": "Full Options",
            "payload": {
                "details": [
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "organization_name": "Test Company",
                        "title": "Engineer",
                    }
                ],
                "reveal_personal_emails": True,
                "reveal_phone_number": True,
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print("📤 Request payload:")
        print(json.dumps(test_case["payload"], indent=2))

        try:
            response = session.post(f"{base_url}/people/bulk_match", json=test_case["payload"])

            print(f"📬 Response Status: {response.status_code}")
            print(f"📬 Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                print("✅ Success!")
                data = response.json()
                print(f"📊 Response data keys: {list(data.keys())}")
            else:
                print("❌ Failed!")
                print(f"📄 Response text: {response.text}")

                # Try to parse as JSON for better formatting
                try:
                    error_data = response.json()
                    print("📄 Parsed error:")
                    print(json.dumps(error_data, indent=2))
                except:
                    pass

        except Exception as e:
            print(f"💥 Exception: {e}")

    # Test with actual contact from our system
    print("\n🧪 Testing with Real Contact Data from Groq:")

    real_contact_payload = {
        "details": [
            {
                "first_name": "Lachlan",
                "last_name": "Donald",
                "organization_name": "Groq",
                "title": "VP of Engineering Infrastructure",
            }
        ],
        "reveal_personal_emails": True,
        "reveal_phone_number": True,
    }

    print("📤 Real contact payload:")
    print(json.dumps(real_contact_payload, indent=2))

    try:
        response = session.post(f"{base_url}/people/bulk_match", json=real_contact_payload)

        print(f"📬 Response Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Real contact lookup succeeded!")
            data = response.json()
            print(f"📊 Response structure: {list(data.keys())}")
            if "matches" in data:
                print(f"📊 Found {len(data['matches'])} matches")
        else:
            print("❌ Real contact lookup failed!")
            print(f"📄 Response text: {response.text}")

    except Exception as e:
        print(f"💥 Exception with real contact: {e}")


if __name__ == "__main__":
    debug_apollo_bulk_match()
