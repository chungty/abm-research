#!/usr/bin/env python3
"""
Debug Partnership Classifier Scoring Logic
"""

import sys

sys.path.append("/Users/chungty/Projects/abm-research/src")

from abm_research.utils.partnership_classifier import partnership_classifier

print("🔍 Debugging Partnership Classifier Scoring Logic")
print("=" * 60)

# Test with the exact data from the debug output
company_data = {
    "name": "NVIDIA Corporation",
    "domain": "nvidia.com",
    "business_model": "Unknown",
    "physical_infrastructure": "H100, DGX, NVIDIA, UPS, colo, edge computing, nVent (73% confidence)",
    "tech_stack": "H100, DGX, NVIDIA, UPS, colo, edge computing, nVent (73% confidence)",
    "recent_announcements": "Not found (searched 2 sources, 95% confidence)",
    "employee_count": 0,
    "growth_stage": "Unknown",
}

print("📊 Input Data:")
for key, value in company_data.items():
    print(f"  {key}: '{value}'")
print()

# Create combined text like the classifier does
company_name = company_data.get("name", "").lower()
business_model = company_data.get("business_model", "").lower()
infrastructure = company_data.get("physical_infrastructure", "").lower()
tech_stack = company_data.get("tech_stack", "").lower()
announcements = company_data.get("recent_announcements", "").lower()

combined_text = f"{company_name} {business_model} {infrastructure} {tech_stack} {announcements}"
print("🔤 Combined Text for Analysis:")
print(f"'{combined_text}'")
print(f"Length: {len(combined_text)} characters")
print()

# Test strategic partner scoring manually
print("🎯 Manual Strategic Partner Scoring:")
strategic_indicators = {
    "hardware_vendors": [
        "nvidia",
        "amd",
        "intel",
        "server manufacturer",
        "gpu vendor",
        "storage vendor",
        "networking equipment",
        "data center equipment",
    ]
}

total_score = 0
for category, indicators in strategic_indicators.items():
    category_score = 0
    matches = []
    for indicator in indicators:
        if indicator in combined_text:
            category_score += 25  # hardware vendor score
            matches.append(indicator)

    if matches:
        print(f"  ✅ {category}: +{category_score} points")
        print(f"     Matched indicators: {matches}")
    else:
        print(f"  ❌ {category}: 0 points")

    total_score += category_score

print(f"\n📊 Manual Total Strategic Partner Score: {total_score}")
print("🎯 Threshold for classification: 30 points")

if total_score >= 30:
    print("✅ Should classify as strategic_partner")
else:
    print("❌ Will classify as unknown (below threshold)")

print()

# Now run the actual classifier
print("🧪 Running Actual Classifier:")
classification = partnership_classifier.classify_partnership(company_data)

print(f"  🏷️  Result: {classification.partnership_type.value}")
print(f"  📊 Confidence: {classification.confidence_score:.1f}%")
print(f"  💭 Reasoning: {classification.reasoning}")

# Compare results
if total_score != classification.confidence_score:
    print("\n⚠️  SCORING MISMATCH!")
    print(f"   Manual calculation: {total_score}")
    print(f"   Classifier result: {classification.confidence_score}")
else:
    print("\n✅ Scoring matches manual calculation")
