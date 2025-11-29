#!/usr/bin/env python3
"""
Debug NVIDIA Partnership Classification Issue
Tests exactly what data the classifier receives and why it fails
"""

import sys
import os
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.utils.partnership_classifier import partnership_classifier
from abm_research.core.abm_system import ComprehensiveABMSystem

print("🔍 NVIDIA Partnership Classification Debug")
print("=" * 50)

# Initialize ABM system to get account intelligence
abm = ComprehensiveABMSystem()

print("1. Getting NVIDIA account intelligence...")
result = abm.conduct_complete_account_research('NVIDIA Corporation', 'nvidia.com')
account_data = result.get('account', {})

print(f"✅ Account intelligence gathered")
print(f"📊 Data keys: {list(account_data.keys())}")
print()

print("2. Data being passed to classifier:")
relevant_fields = [
    ('name', 'Company Name'),
    ('business_model', 'Growth Stage'),
    ('physical_infrastructure', 'Physical Infrastructure'),
    ('recent_announcements', 'Recent Announcements')
]

classifier_input = {}
for field_name, account_field in relevant_fields:
    value = account_data.get(account_field, '')
    classifier_input[field_name] = value
    print(f"  📝 {field_name}: '{value}'")
print()

# Create combined text like the classifier does
company_name = classifier_input.get('name', '').lower()
business_model = classifier_input.get('business_model', '').lower()
infrastructure = classifier_input.get('physical_infrastructure', '').lower()
announcements = classifier_input.get('recent_announcements', '').lower()

combined_text = f"{company_name} {business_model} {infrastructure} {announcements}"
print(f"3. Combined text for classification:")
print(f"  📄 Text: '{combined_text}'")
print(f"  📏 Length: {len(combined_text)} characters")
print()

# Test each scoring method manually
print("4. Manual scoring breakdown:")

# Test strategic partner scoring
print("  🎯 Strategic Partner Indicators:")
strategic_indicators = {
    "hardware_vendors": [
        "nvidia", "amd", "intel", "server manufacturer", "gpu vendor",
        "storage vendor", "networking equipment", "data center equipment"
    ],
    "ai_infrastructure": [
        "ai inference", "gpu as a service", "ml platform", "ai training platform",
        "compute as a service", "ai cloud", "inference api"
    ]
}

total_strategic_score = 0

for category, indicators in strategic_indicators.items():
    category_score = 0
    matches = []
    for indicator in indicators:
        if indicator in combined_text:
            if category == "hardware_vendors":
                category_score += 25
            else:
                category_score += 30
            matches.append(indicator)

    if matches:
        print(f"    ✅ {category}: +{category_score} points (matched: {matches})")
    else:
        print(f"    ❌ {category}: 0 points (no matches)")

    total_strategic_score += category_score

print(f"  📊 Total Strategic Partner Score: {total_strategic_score}")
print()

# Now test the actual classifier
print("5. Running actual classifier:")
classification = partnership_classifier.classify_from_account_intelligence(account_data)
print(f"  🏷️  Type: {classification.partnership_type.value}")
print(f"  📊 Confidence: {classification.confidence_score:.1f}%")
print(f"  💭 Reasoning: {classification.reasoning}")
print()

print("6. Manual company data test:")
# Test with manual data to see if the issue is in data mapping
manual_data = {
    'name': 'NVIDIA Corporation',
    'business_model': 'hardware vendor gpu manufacturer',
    'physical_infrastructure': 'nvidia gpu h100 a100 data center equipment',
    'tech_stack': 'cuda gpu computing ai training',
    'recent_announcements': 'nvidia ai gpu datacenter',
    'employee_count': 50000,
    'growth_stage': 'mature'
}

manual_classification = partnership_classifier.classify_partnership(manual_data)
print(f"  🏷️  Manual Type: {manual_classification.partnership_type.value}")
print(f"  📊 Manual Confidence: {manual_classification.confidence_score:.1f}%")
print(f"  💭 Manual Reasoning: {manual_classification.reasoning}")