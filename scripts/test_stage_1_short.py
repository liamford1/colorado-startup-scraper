"""
Quick test of Stage 1 with improved prompts - runs only first 5 queries
"""
import os
import sys

# Import directly from current directory
from stage_1 import CompanyDiscovery

# Test the updated approach (allowing companies without URLs)
test_queries = [
    "Find Colorado tech startups that raised venture capital funding recently",
    "Find Colorado companies with Series A funding rounds in recent years",
    "Find Endeavor Colorado portfolio companies",
]

discovery = CompanyDiscovery()

print(f"Testing with {len(test_queries)} queries:\n")

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"[{i}/{len(test_queries)}] Query: {query}")
    print('='*80)

    results = discovery.search(query, num_results=10)

    print(f"\nResults: Found {len(results)} companies")
    for j, result in enumerate(results[:3], 1):  # Show first 3
        print(f"  {j}. {result['title']}")
        print(f"     {result['link']}")

    if len(results) > 3:
        print(f"  ... and {len(results) - 3} more")

    if i < len(test_queries):
        print("\nWaiting 2 seconds before next query...")
        import time
        time.sleep(2)

print(f"\n{'='*80}")
print("Test complete!")
print('='*80)
