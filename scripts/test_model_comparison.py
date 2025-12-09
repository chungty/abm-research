#!/usr/bin/env python3
"""
Model Comparison Test: GPT-4 vs GPT-4o-mini for Extraction Tasks

This script compares the quality of GPT-4 and GPT-4o-mini for:
1. Trigger event extraction from news articles
2. Partnership extraction from company pages
3. LinkedIn content theme analysis

Run with: PYTHONPATH=. python3 scripts/test_model_comparison.py
"""
import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Test data - representative samples from actual usage
TEST_CASES = {
    "trigger_events": {
        "prompt_template": """Extract trigger events from this news content about {company_name}.
Return format: EventType|Description|ConfidenceScore|RelevanceScore
Event types: expansion, hiring, funding, partnership, ai_workload, leadership, incident

Content:
{content}""",
        "samples": [
            {
                "company_name": "Groq",
                "content": """Groq, the AI inference chip company, announced a major expansion of its datacenter
operations with a new 50MW facility in Texas. The company raised $640M in Series D funding and is hiring
200 new engineers across its infrastructure and cloud teams. CEO Jonathan Ross stated the expansion will
support 10x more inference workloads by Q4.""",
            },
            {
                "company_name": "FlexAI",
                "content": """FlexAI has partnered with NVIDIA to deploy next-generation H100 clusters for
enterprise AI training. The company also announced a new Chief Technology Officer, Dr. Sarah Chen, who
previously led Google's TPU infrastructure team. FlexAI's new platform promises 40% lower latency for
inference workloads.""",
            },
            {
                "company_name": "DataCrunch",
                "content": """Cloud GPU provider DataCrunch experienced a brief outage in their EU region
yesterday due to cooling system issues. The company quickly resolved the incident and announced they are
investing $30M in redundant cooling infrastructure. DataCrunch continues to expand their H100 availability
with new datacenter partnerships in Amsterdam and Frankfurt.""",
            },
        ],
    },
    "partnerships": {
        "prompt_template": """Extract technology partnerships from this content about {company_name}.
Return format: PartnerName|Category|RelationshipEvidence|ConfidenceScore
Categories: GPU/AI, Power Systems, Cooling, DCIM, Cloud, Storage

Content:
{content}""",
        "samples": [
            {
                "company_name": "Genesis Cloud",
                "content": """Genesis Cloud powers its GPU infrastructure with NVIDIA A100 and H100 accelerators,
partnering with Schneider Electric for power distribution and Vertiv for precision cooling. Their new facility
features Nlyte DCIM software for capacity management and uses Equinix for global connectivity.""",
            },
            {
                "company_name": "EdgeConnex",
                "content": """EdgeConnex datacenters utilize AMD EPYC processors alongside NVIDIA GPUs for
hybrid workloads. The company has deployed Delta Electronics UPS systems and Eaton PDUs throughout their
facilities. Cooling is handled by CoolIT direct-to-chip liquid cooling solutions for high-density racks.""",
            },
        ],
    },
    "linkedin_themes": {
        "prompt_template": """Analyze this LinkedIn content for themes relevant to datacenter infrastructure.
Return format: Theme1,Theme2,Theme3|RelevanceLevel|Points

Themes to detect: power efficiency, AI infrastructure, cooling, capacity planning, sustainability,
energy management, GPU computing

Content:
{content}""",
        "samples": [
            {
                "content": """Excited to share our latest achievement - we've reduced datacenter PUE from 1.6 to
1.2 through innovative cooling strategies. Our team deployed liquid cooling for our GPU clusters, resulting
in 30% energy savings. Sustainability isn't just good for the planet - it's good for business."""
            },
            {
                "content": """Just returned from Data Center World where I spoke about capacity planning challenges
for AI workloads. Key insight: traditional provisioning models don't work for GPU-intensive applications.
We need real-time power monitoring at the rack level."""
            },
        ],
    },
}


def test_model(model: str, prompt: str) -> dict:
    """Test a single model call and return results with timing."""
    start = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a B2B sales intelligence analyst. Extract structured data from text.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    elapsed = time.time() - start
    result = response.choices[0].message.content

    # Calculate cost
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    if model == "gpt-4":
        cost = (input_tokens * 0.03 / 1000) + (output_tokens * 0.06 / 1000)
    else:  # gpt-4o-mini
        cost = (input_tokens * 0.00015 / 1000) + (output_tokens * 0.0006 / 1000)

    return {
        "model": model,
        "response": result,
        "elapsed_ms": round(elapsed * 1000),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
    }


def count_extractions(response: str) -> int:
    """Count number of extractions in a response."""
    lines = [l.strip() for l in response.strip().split("\n") if l.strip() and "|" in l]
    return len(lines)


def run_comparison():
    """Run the full model comparison."""
    print("=" * 70)
    print("MODEL COMPARISON: GPT-4 vs GPT-4o-mini")
    print("=" * 70)
    print()

    all_results = []

    for task_name, task_data in TEST_CASES.items():
        print(f"\n{'='*60}")
        print(f"TASK: {task_name.upper()}")
        print(f"{'='*60}")

        for i, sample in enumerate(task_data["samples"]):
            print(f"\n--- Sample {i+1} ---")

            # Build prompt
            if "company_name" in sample:
                prompt = task_data["prompt_template"].format(
                    company_name=sample["company_name"], content=sample["content"]
                )
            else:
                prompt = task_data["prompt_template"].format(content=sample["content"])

            # Test both models
            results = {}
            for model in ["gpt-4", "gpt-4o-mini"]:
                try:
                    result = test_model(model, prompt)
                    results[model] = result
                    print(f"\n{model}:")
                    print(f"  Time: {result['elapsed_ms']}ms")
                    print(f"  Cost: ${result['cost_usd']:.6f}")
                    print(f"  Extractions: {count_extractions(result['response'])}")
                    print(f"  Response preview: {result['response'][:200]}...")
                except Exception as e:
                    print(f"\n{model}: ERROR - {e}")
                    results[model] = {"error": str(e)}

                time.sleep(0.5)  # Rate limit

            all_results.append({"task": task_name, "sample_index": i, "results": results})

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    gpt4_total_cost = 0
    mini_total_cost = 0
    gpt4_total_time = 0
    mini_total_time = 0
    extraction_matches = 0
    total_samples = 0

    for r in all_results:
        if "gpt-4" in r["results"] and "gpt-4o-mini" in r["results"]:
            gpt4 = r["results"]["gpt-4"]
            mini = r["results"]["gpt-4o-mini"]

            if "cost_usd" in gpt4 and "cost_usd" in mini:
                gpt4_total_cost += gpt4["cost_usd"]
                mini_total_cost += mini["cost_usd"]
                gpt4_total_time += gpt4["elapsed_ms"]
                mini_total_time += mini["elapsed_ms"]

                # Check if extraction counts match (quality proxy)
                gpt4_count = count_extractions(gpt4.get("response", ""))
                mini_count = count_extractions(mini.get("response", ""))
                if abs(gpt4_count - mini_count) <= 1:  # Within 1 extraction
                    extraction_matches += 1
                total_samples += 1

    print(f"\n{'Metric':<30} {'GPT-4':<15} {'GPT-4o-mini':<15} {'Savings':<15}")
    print("-" * 75)
    print(
        f"{'Total Cost':<30} ${gpt4_total_cost:.6f}     ${mini_total_cost:.6f}     {(1 - mini_total_cost/gpt4_total_cost)*100:.1f}%"
    )
    print(
        f"{'Avg Response Time (ms)':<30} {gpt4_total_time/total_samples:.0f}           {mini_total_time/total_samples:.0f}           {(1 - mini_total_time/gpt4_total_time)*100:.1f}%"
    )
    print(
        f"{'Quality Match Rate':<30} {'baseline':<15} {extraction_matches/total_samples*100:.0f}%"
    )

    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    quality_threshold = 0.8  # 80% match rate
    match_rate = extraction_matches / total_samples if total_samples > 0 else 0

    if match_rate >= quality_threshold:
        print(
            f"""
RECOMMENDATION: SWITCH TO GPT-4o-mini

Quality Match Rate: {match_rate*100:.0f}% (threshold: {quality_threshold*100:.0f}%)
Cost Savings: {(1 - mini_total_cost/gpt4_total_cost)*100:.1f}%
Speed Improvement: {(1 - mini_total_time/gpt4_total_time)*100:.1f}%

The extraction quality is comparable. Proceed with model switch.
"""
        )
    else:
        print(
            f"""
RECOMMENDATION: KEEP GPT-4 (or investigate further)

Quality Match Rate: {match_rate*100:.0f}% (threshold: {quality_threshold*100:.0f}%)

GPT-4o-mini may not produce comparable results for these extraction tasks.
Consider reviewing the specific cases where quality differs.
"""
        )

    # Save detailed results
    output_file = f'/tmp/model_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Detailed results saved to: {output_file}")

    return {
        "match_rate": match_rate,
        "cost_savings": (1 - mini_total_cost / gpt4_total_cost) if gpt4_total_cost > 0 else 0,
        "speed_improvement": (1 - mini_total_time / gpt4_total_time) if gpt4_total_time > 0 else 0,
        "recommendation": "SWITCH" if match_rate >= quality_threshold else "KEEP_GPT4",
    }


if __name__ == "__main__":
    result = run_comparison()
    print(f"\nFinal recommendation: {result['recommendation']}")
