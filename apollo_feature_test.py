#!/usr/bin/env python3
"""
Test Apollo API Feature Access
Check which advanced features are available on current plan
"""

import os
import requests
import json
from datetime import datetime

def test_apollo_features():
    """Test all Apollo API features to see what's available"""

    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ APOLLO_API_KEY not found")
        return

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    print("🧪 Testing Apollo API Feature Access\n")

    # Test 1: Basic People Search with Enhanced Features
    print("📊 TEST 1: People Search with Enhanced Features")
    test_people_search_enhanced(headers)

    # Test 2: Bulk People Enrichment
    print("\n📊 TEST 2: Bulk People Enrichment")
    test_bulk_enrichment(headers)

    # Test 3: Individual People Enrichment
    print("\n📊 TEST 3: Individual People Enrichment")
    test_individual_enrichment(headers)

    # Test 4: Organization Search
    print("\n📊 TEST 4: Organization Search")
    test_organization_search(headers)

    # Test 5: Account Information
    print("\n📊 TEST 5: Account Information")
    test_account_info(headers)

def test_people_search_enhanced(headers):
    """Test people search with all advanced parameters"""

    url = "https://api.apollo.io/v1/mixed_people/search"

    payload = {
        "api_key": os.getenv('APOLLO_API_KEY'),
        "q_organization_domains": "genesiscloud.com",
        "page": 1,
        "per_page": 5,  # Small test
        "person_titles": ["CEO", "CTO", "VP"],
        "q_person_seniorities": ["vp", "c_level"],
        "include_emails": True,
        "include_phone_numbers": True,  # Test this
        "reveal_personal_emails": True,  # Test this
        "prospected_by_current_team": ["no"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            people = data.get('people', [])
            print(f"✅ Enhanced Search: Found {len(people)} people")

            if people:
                person = people[0]
                print(f"   Sample person: {person.get('name', 'Unknown')}")
                print(f"   Email: {'✅' if person.get('email') else '❌'}")
                print(f"   Phone Numbers: {'✅' if person.get('phone_numbers') else '❌'}")
                print(f"   Personal Email: {'✅' if person.get('personal_email') else '❌'}")
                print(f"   LinkedIn URL: {'✅' if person.get('linkedin_url') else '❌'}")

        elif response.status_code == 400:
            print(f"❌ Bad Request - Some parameters may not be supported")
            error_data = response.json()
            print(f"   Error: {error_data}")

        elif response.status_code == 402:
            print(f"❌ Payment Required - Feature requires higher tier")

        else:
            print(f"❌ Error {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def test_bulk_enrichment(headers):
    """Test bulk people enrichment"""

    url = "https://api.apollo.io/v1/people/bulk_match"

    # Test with minimal data
    payload = {
        "api_key": os.getenv('APOLLO_API_KEY'),
        "details": [
            {
                "first_name": "Brian",
                "last_name": "Lenz",
                "organization_name": "Genesis Cloud"
            }
        ],
        "reveal_personal_emails": True,
        "reveal_phone_number": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"✅ Bulk Enrichment: Found {len(matches)} matches")

            if matches and matches[0]:
                match = matches[0]
                print(f"   Name: {match.get('name', 'Unknown')}")
                print(f"   Email: {'✅' if match.get('email') else '❌'}")
                print(f"   Personal Email: {'✅' if match.get('personal_email') else '❌'}")
                print(f"   Phone: {'✅' if match.get('phone_numbers') else '❌'}")
        else:
            print(f"❌ Error {response.status_code}")
            if response.status_code == 402:
                print("   Payment Required - Feature requires higher tier")
            elif response.status_code == 400:
                error_data = response.json()
                print(f"   Bad Request: {error_data}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def test_individual_enrichment(headers):
    """Test individual people enrichment"""

    url = "https://api.apollo.io/v1/people/match"

    payload = {
        "api_key": os.getenv('APOLLO_API_KEY'),
        "first_name": "Brian",
        "last_name": "Lenz",
        "organization_name": "Genesis Cloud",
        "reveal_personal_emails": True,
        "reveal_phone_number": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            person = data.get('person', {})

            if person:
                print(f"✅ Individual Enrichment: Found match")
                print(f"   Name: {person.get('name', 'Unknown')}")
                print(f"   Email: {'✅' if person.get('email') else '❌'}")
                print(f"   Personal Email: {'✅' if person.get('personal_email') else '❌'}")
                print(f"   Phone: {'✅' if person.get('phone_numbers') else '❌'}")
                print(f"   Employment History: {'✅' if person.get('employment_history') else '❌'}")
            else:
                print(f"❌ No match found")
        else:
            print(f"❌ Error {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def test_organization_search(headers):
    """Test organization search capabilities"""

    url = "https://api.apollo.io/v1/organizations/search"

    payload = {
        "api_key": os.getenv('APOLLO_API_KEY'),
        "q_organization_domains": "genesiscloud.com",
        "page": 1,
        "per_page": 1
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            orgs = data.get('organizations', [])

            if orgs:
                org = orgs[0]
                print(f"✅ Organization Search: Found {org.get('name', 'Unknown')}")
                print(f"   Employee Count: {org.get('estimated_num_employees', 'Unknown')}")
                print(f"   Industry: {org.get('industry', 'Unknown')}")
                print(f"   LinkedIn: {'✅' if org.get('linkedin_url') else '❌'}")
                print(f"   Technologies: {'✅' if org.get('technologies') else '❌'}")
        else:
            print(f"❌ Error {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def test_account_info(headers):
    """Test account information and credit usage"""

    url = "https://api.apollo.io/v1/auth/health"

    try:
        response = requests.get(url, headers=headers)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ API Health: Connection successful")
        else:
            print(f"❌ API Health: Error {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    test_apollo_features()