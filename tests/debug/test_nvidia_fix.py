#!/usr/bin/env python3
"""
Test NVIDIA Partnership Classification Fix
"""

import sys
import os
sys.path.append('/Users/chungty/Projects/abm-research/src')

from abm_research.core.abm_system import ComprehensiveABMSystem

print("🔍 Testing NVIDIA Partnership Classification Fix")
print("=" * 50)

# Initialize ABM system
abm = ComprehensiveABMSystem()

print("🧪 Testing NVIDIA Corporation classification...")
# Test with a simpler call to avoid long intelligence gathering
result = {
    'name': 'NVIDIA Corporation',
    'domain': 'nvidia.com',
    'Physical Infrastructure': 'GPU, NVIDIA, H100, data center infrastructure',
    'Growth Stage': 'Mature',
    'Recent Announcements': 'AI platform announcements',
    'employee_count': 50000
}

# Simulate calling the partnership classification directly
if abm.partnership_classifier:
    company_data = {
        'name': 'NVIDIA Corporation',
        'domain': 'nvidia.com',
        'business_model': 'Mature',
        'physical_infrastructure': 'GPU, NVIDIA, H100, data center infrastructure',
        'tech_stack': 'GPU, NVIDIA, H100, data center infrastructure',
        'recent_announcements': 'AI platform announcements',
        'employee_count': 50000,
        'growth_stage': 'Mature'
    }

    print(f"📊 Input data preview:")
    print(f"  🏷️  Name: '{company_data['name']}'")
    print(f"  🏗️  Infrastructure: '{company_data['physical_infrastructure'][:60]}...'")
    print()

    classification = abm.partnership_classifier.classify_partnership(company_data)

    print(f"✅ Classification Results:")
    print(f"  🏷️  Partnership Type: {classification.partnership_type.value}")
    print(f"  📊 Confidence: {classification.confidence_score:.1f}%")
    print(f"  💭 Reasoning: {classification.reasoning}")
    print(f"  📈 Recommended Approach: {classification.recommended_approach}")
    print()

    # Expected: Should be "strategic_partner" or "direct_icp" with high confidence
    if classification.partnership_type.value == 'unknown':
        print("❌ STILL BROKEN: NVIDIA classified as unknown")
    elif classification.partnership_type.value in ['strategic_partner', 'direct_icp']:
        print(f"✅ SUCCESS: NVIDIA correctly classified as {classification.partnership_type.value}")
    else:
        print(f"⚠️  UNEXPECTED: NVIDIA classified as {classification.partnership_type.value}")

else:
    print("❌ Partnership classifier not available")

print()
print("🔍 Testing with real ABM system call...")
# Test the full system to ensure the fix works end-to-end
full_result = abm.conduct_complete_account_research('NVIDIA Corporation', 'nvidia.com')
account_data = full_result.get('account', {})
classification_type = account_data.get('partnership_classification', 'unknown')
classification_confidence = account_data.get('classification_confidence', 0.0)

print(f"🏢 Full ABM System Result:")
print(f"  🏷️  Partnership Type: {classification_type}")
print(f"  📊 Confidence: {classification_confidence:.1f}%")

if classification_type == 'unknown':
    print("❌ ISSUE PERSISTS: Full system still returns unknown")
elif classification_type in ['strategic_partner', 'direct_icp']:
    print(f"✅ FIXED: Full system correctly classifies as {classification_type}")
else:
    print(f"⚠️  UNEXPECTED: Full system classifies as {classification_type}")