"""
Test script to debug Perplexity API responses
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv('../.env')

# Config
try:
    from config import PERPLEXITY_MODEL
except ImportError:
    PERPLEXITY_MODEL = "sonar-pro"

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
)

# Test with a simple query
test_query = "Find Colorado tech startups founded in 2024 with funding"

system_prompt = """You are a research assistant specializing in finding company websites.

CRITICAL REQUIREMENT: Only include companies where you can find their official website URL.
Do NOT include any company if you cannot find its website URL.

For each company, provide:
1. Company name
2. Official website URL (REQUIRED - must start with http:// or https://)
3. Brief description

Format each company on one line exactly as:
Company Name | https://www.example.com | Brief description

ONLY include companies with valid website URLs. Skip any company if you cannot find its URL."""

user_prompt = f"""Search for companies matching: {test_query}

Find their official websites and provide exactly 10 companies in this format:
Company Name | https://website.com | Description

Requirements:
- Every company MUST have a valid website URL
- Use official company domains, not LinkedIn/Twitter/Crunchbase pages
- If you can't find a company's website, skip it and find another company
- Search thoroughly to ensure you find actual website URLs"""

print("Testing Perplexity API...")
print(f"Model: {PERPLEXITY_MODEL}")
print(f"Query: {test_query}\n")

try:
    response = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=2000
    )

    content = response.choices[0].message.content

    print("=" * 80)
    print("RAW RESPONSE FROM PERPLEXITY:")
    print("=" * 80)
    print(content)
    print("=" * 80)

    # Import the parsing logic from stage_1
    import sys
    sys.path.insert(0, '.')
    from stage_1 import CompanyDiscovery

    discovery = CompanyDiscovery()
    results = discovery._parse_perplexity_response(content, test_query)

    print(f"\n{'='*80}")
    print(f"PARSED RESULTS: Found {len(results)} companies")
    print('='*80)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['link']}")
        print(f"   Snippet: {result['snippet'][:100]}...")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
