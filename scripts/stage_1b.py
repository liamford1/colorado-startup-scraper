"""
Stage 1b: URL Discovery
Finds URLs for companies that have URL_NEEDED placeholder
"""
import os
import json
import re
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env')

# Config Settings
try:
    from config import PERPLEXITY_MODEL, SEARCH_DELAY
except ImportError:
    PERPLEXITY_MODEL = "sonar-pro"
    SEARCH_DELAY = 2.0

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')


class URLFinder:
    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        self.model = PERPLEXITY_MODEL

    def find_url(self, company_name: str, description: str = "") -> Optional[str]:
        """
        Search for a company's official website URL using Perplexity
        """
        # Build search query with context from description
        location = ""
        industry = ""

        # Extract location hints from description
        if description:
            if "Colorado" in description or "Denver" in description or "Boulder" in description:
                location = "Colorado"

            # Extract industry hints
            desc_lower = description.lower()
            if any(word in desc_lower for word in ['ai', 'artificial intelligence', 'machine learning']):
                industry = "AI"
            elif any(word in desc_lower for word in ['fintech', 'financial', 'payments']):
                industry = "fintech"
            elif any(word in desc_lower for word in ['healthcare', 'health', 'medical']):
                industry = "healthcare"
            elif any(word in desc_lower for word in ['saas', 'software', 'b2b']):
                industry = "software"

        # Build query with available context
        query_parts = [f'"{company_name}"', "official website"]
        if location:
            query_parts.append(location)
        if industry:
            query_parts.append(industry)

        query = " ".join(query_parts)

        system_prompt = """You are a research assistant finding company websites.

CRITICAL: Only provide the official company website URL. Do not include any other text.

If you find the website, respond with ONLY the URL in this format:
https://www.example.com

If you cannot find a reliable website URL, respond with only:
NOT_FOUND"""

        user_prompt = f"""Find the official website URL for: {company_name}

Context: {description[:200] if description else 'No additional context'}

Respond with ONLY the website URL (e.g., https://www.example.com) or NOT_FOUND if you cannot find it."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=100  # Short response
            )

            content = response.choices[0].message.content.strip()

            # Parse response - look for URL
            url_match = re.search(r'https?://[^\s<>"]+', content)
            if url_match:
                url = url_match.group(0)
                # Clean up URL
                url = url.rstrip('.,;:)')
                return self._normalize_url(url)

            # Check if explicitly not found
            if 'NOT_FOUND' in content.upper():
                return None

            return None

        except Exception as e:
            print(f"    Error searching for URL: {e}")
            return None

    def _normalize_url(self, url: str) -> str:
        """Normalize URL format"""
        url = url.strip()
        # Ensure https protocol
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        elif not url.startswith('https://'):
            url = 'https://' + url
        return url


def main():
    """Find URLs for all URL_NEEDED entries"""
    print("=" * 60)
    print("STAGE 1B: URL DISCOVERY")
    print("=" * 60)

    # Load candidates from Stage 1
    input_file = '../outputs/stage_1.json'
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Run stage_1.py first.")
        return

    # Find candidates needing URLs
    needs_url = [c for c in candidates if c.get('url') == 'URL_NEEDED']
    has_url = [c for c in candidates if c.get('url') != 'URL_NEEDED']

    print(f"\n📊 Status:")
    print(f"   {len(has_url)} companies already have URLs")
    print(f"   {len(needs_url)} companies need URL discovery")

    if not needs_url:
        print("\n✓ All companies already have URLs!")
        return

    # Initialize finder
    finder = URLFinder()

    # Process each company needing a URL
    found_count = 0
    not_found_count = 0

    print(f"\n🔍 Searching for URLs...")

    for i, candidate in enumerate(needs_url, 1):
        company_name = candidate.get('title', 'Unknown')
        description = candidate.get('snippet', '')

        print(f"\n[{i}/{len(needs_url)}] Searching for: {company_name}")

        # Search for URL
        url = finder.find_url(company_name, description)

        if url:
            print(f"  ✓ Found: {url}")
            candidate['url'] = url
            candidate['url_source'] = 'perplexity_search'
            found_count += 1
        else:
            print(f"  ✗ Not found - keeping URL_NEEDED")
            not_found_count += 1

        # Save progress after every 10 companies
        if i % 10 == 0:
            print(f"\n  💾 Saving progress... ({found_count} found, {not_found_count} not found)")
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, indent=2, ensure_ascii=False)

        # Rate limiting
        time.sleep(SEARCH_DELAY)

    # Save final results
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)

    print(f"\n" + "=" * 60)
    print("URL DISCOVERY COMPLETE")
    print("=" * 60)
    print(f"✓ Found URLs: {found_count}/{len(needs_url)}")
    print(f"✗ Not found: {not_found_count}/{len(needs_url)}")
    print(f"✓ Total companies with URLs: {len(has_url) + found_count}/{len(candidates)}")
    print(f"\n✓ Updated results saved to {input_file}")

    if not_found_count > 0:
        print(f"\n⚠️  {not_found_count} companies still have URL_NEEDED")
        print("   These will be skipped in Stage 2 scraping")


if __name__ == '__main__':
    main()
