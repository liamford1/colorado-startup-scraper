"""
Stage 1: Company Discovery
Uses Perplexity API to find candidate companies/startups
"""
import os
import csv
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import time
from openai import OpenAI

load_dotenv('../.env')

# Config Settings
try:
    from config import PERPLEXITY_MODEL, SEARCH_DELAY
except ImportError:
    PERPLEXITY_MODEL = "sonar-pro"
    SEARCH_DELAY = 2.0

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')


class CompanyDiscovery:
    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables. Please set it in .env file.")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        self.model = PERPLEXITY_MODEL

    def normalize_company_name_aggressive(self, name: str) -> str:
        """Aggressively normalize company name to catch duplicates like 'BrightWave' vs 'Bright Wave Inc'"""
        if not name:
            return ""

        # Remove leading numbers
        name = re.sub(r'^\d+\.\s*', '', name)
        # Convert to lowercase
        name = name.lower().strip()

        # Remove common suffixes and legal entities (must be at end of string)
        suffixes = ['inc', 'incorporated', 'corporation', 'corp', 'llc', 'ltd',
                   'limited', 'co', 'company', 'pbc', 'pllc', 'lp', 'llp']
        for suffix in suffixes:
            # Remove with word boundary to avoid removing from middle of words
            name = re.sub(rf'\b{suffix}\b\.?$', '', name)

        # Remove all punctuation and special characters
        name = re.sub(r'[^\w\s]', '', name)

        # Remove ALL spaces to catch "BrightWave" vs "Bright Wave"
        name = name.replace(' ', '')

        return name

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Using Perplexity search to extract company URL, Name, and Discription
        """
        system_prompt = """You are a research assistant finding REAL, SPECIFIC companies and startups.

CRITICAL: You must provide ACTUAL company names, not placeholders like "[Company 1]" or "Company Name".

For each company you find, provide:
1. The REAL, SPECIFIC company name (e.g., "Palantir", "Gusto", "Gitlab")
2. Official website URL (if available, otherwise write "URL_NEEDED")
3. Brief description including location, industry, and funding info if available

Format each company on one line exactly as:
Company Name | https://www.example.com | Brief description

OR if website is not available:
Company Name | URL_NEEDED | Brief description with location and funding details

IMPORTANT RULES:
- NEVER use placeholder names like "[Company 1]", "[Company Name]", "Company XYZ"
- ONLY include companies where you know the ACTUAL company name
- If you can't find real company names, return fewer results
- Include as many relevant companies as possible, even if you don't have their website URLs"""

        user_prompt = f"""Find up to {num_results} REAL companies matching this search: {query}

Provide a list in this format:
Company Name | Website URL or URL_NEEDED | Description

CRITICAL REQUIREMENTS:
- Use ACTUAL, SPECIFIC company names only (e.g., "Stripe", "Notion", "Databricks")
- NO placeholders like "[Company 1]", "[Company Name]", "Example Corp"
- Include companies even if you don't know their exact website - we can find that later
- If you can't find real company names, return fewer results rather than using placeholders
- Focus on finding real company names, locations, and funding information"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )

            # Log the raw API response for debugging
            print(f"\n  🔍 RAW API RESPONSE:")
            print(f"  Model: {response.model}")
            print(f"  Finish Reason: {response.choices[0].finish_reason}")

            content = response.choices[0].message.content
            print(f"  Content Length: {len(content) if content else 0} characters")
            print(f"  Content Preview (first 500 chars):")
            print(f"  {'-'*60}")
            print(f"  {content[:500] if content else 'EMPTY CONTENT'}")
            print(f"  {'-'*60}\n")

            # Get results from LLM response
            results = self._parse_perplexity_response(content, query)
            time.sleep(1)

            return results

        except Exception as e:
            print(f"Error during Perplexity search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_perplexity_response(self, content: str, query: str) -> List[Dict]:
        """
        Parse Perplexity response to extract company URLs and information
        """
        results = []
        print(f"  📋 PARSING RESPONSE...")

        def normalize_url(url: str) -> str:
            """Add https:// prefix if missing and clean URL"""
            url = url.strip()
            # Remove common markdown/formatting characters
            url = re.sub(r'[^\w\s:/.-]', '', url)
            # Add https:// if no protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            # Ensure consistent protocol (prefer https)
            url = url.replace('http://', 'https://')
            return url

        # Extract URLs - match both with and without protocol
        url_pattern_with_protocol = r'https?://[^\s\)|\]]+'
        url_pattern_without_protocol = r'(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.[a-zA-Z]{2,}(?:/[^\s\)|\]]*)?'

        urls_with_protocol = re.findall(url_pattern_with_protocol, content)
        print(f"  Found {len(urls_with_protocol)} URLs with protocol: {urls_with_protocol[:3]}")

        # Try to extract structured format (Name | URL | Description)
        lines = content.split('\n')
        print(f"  Parsing {len(lines)} lines for structured format (Name | URL | Description)...")

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try to parse "Name | URL | Description" format
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    name = parts[0].lstrip('- ').strip()
                    # Remove numbered list prefixes like "1. ", "2. ", etc.
                    name = re.sub(r'^\d+\.\s*', '', name)
                    url = parts[1].strip()
                    snippet = parts[2].strip() if len(parts) > 2 else ""

                    # Handle URL_NEEDED placeholder
                    if url.upper() in ['URL_NEEDED', 'NOT PROVIDED', 'N/A', 'UNKNOWN']:
                        results.append({
                            'title': name,
                            'link': 'URL_NEEDED',
                            'snippet': snippet or f"Company found via search - URL to be found later"
                        })
                        continue

                    # Check if this looks like a URL (has domain-like structure)
                    if re.match(r'^(?:https?://)?(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})*\.[a-zA-Z]{2,}', url):
                        url = normalize_url(url)
                        results.append({
                            'title': name,
                            'link': url,
                            'snippet': snippet or f"Company found via search"
                        })
                        continue

            # Try to find URLs with protocol
            url_match = re.search(url_pattern_with_protocol, line)
            if url_match:
                url = normalize_url(url_match.group(0))
                # Remove URL from line to get name/description
                name_desc = line.replace(url_match.group(0), '').strip().lstrip('- ').strip()
                results.append({
                    'title': name_desc.split('|')[0].strip() if '|' in name_desc else name_desc,
                    'link': url,
                    'snippet': name_desc if len(name_desc) > 50 else f"Company found via search"
                })

        # If we didn't get structured results, use URLs found in text
        if not results and urls_with_protocol:
            print(f"  No structured results found, extracting from URLs in text...")
            for url in urls_with_protocol[:10]:
                url = normalize_url(url)
                # Try to find context around URL
                url_index = content.find(url)
                if url_index > 0:
                    context_start = max(0, url_index - 100)
                    context_end = min(len(content), url_index + len(url) + 100)
                    context = content[context_start:context_end]

                    # Extract potential name (text before URL)
                    name_match = re.search(r'([A-Z][^.!?]*?)(?:\s+https?://)', context)
                    name = name_match.group(1).strip() if name_match else "Company"

                    results.append({
                        'title': name[:100],
                        'link': url,
                        'snippet': context[:200] if len(context) > 200 else context
                    })

        print(f"  ✅ Parsed {len(results)} companies from response")
        if results:
            print(f"  First result: {results[0].get('title', 'N/A')} - {results[0].get('link', 'N/A')}")

        return results[:10]

    def _save_progress(self, candidates: List[Dict], csv_filename: str, json_filename: str):
        """Save current progress to both CSV and JSON"""
        if not candidates:
            return

        try:
            # Save CSV
            fieldnames = ['company_name', 'url', 'found_count', 'priority', 'snippet', 'discovery_query']

            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for candidate in candidates:
                    writer.writerow({
                        'company_name': candidate.get('title', ''),
                        'url': candidate.get('url', ''),
                        'found_count': candidate.get('found_count', 0),
                        'priority': candidate.get('priority', 'medium'),
                        'snippet': candidate.get('snippet', '')[:200],  # Truncate for readability
                        'discovery_query': candidate.get('discovery_query', '')[:100]
                    })

            # Save JSON with consistent field order
            normalized_candidates = []
            for candidate in candidates:
                normalized = {
                    'title': candidate.get('title', ''),
                    'url': candidate.get('url', ''),
                    'snippet': candidate.get('snippet', ''),
                    'discovery_query': candidate.get('discovery_query', ''),
                    'found_count': candidate.get('found_count', 1),
                    'priority': candidate.get('priority', 'medium')
                }
                normalized_candidates.append(normalized)

            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(normalized_candidates, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  Warning: Could not save progress: {e}")

    def discover_companies(self) -> List[Dict]:
        """
        Discover companies/startups using multiple search strategies
        """
        # Files for incremental saving
        csv_file = '../outputs/stage_1_progress.csv'
        json_file = '../outputs/stage_1.json'

        # Load existing candidates to merge with new discoveries
        all_candidates = {}
        existing_candidates = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    existing_candidates = json.load(f)
                # Add existing candidates to dict, checking for name-based duplicates
                for candidate in existing_candidates:
                    url = candidate.get('url', '')
                    if url:
                        # Use aggressive normalization for URL_NEEDED entries
                        if url == 'URL_NEEDED':
                            normalized_key = f"name:{self.normalize_company_name_aggressive(candidate.get('title', ''))}"
                        else:
                            # For real URLs, normalize the domain
                            normalized_key = url.lower().rstrip('/')
                            normalized_key = re.sub(r'^https?://', '', normalized_key)
                            normalized_key = re.sub(r'^www\.', '', normalized_key)
                            # Extract just the domain for comparison
                            normalized_key = f"url:{normalized_key.split('/')[0]}"

                        # Check if this company name already exists (prevents loading duplicates)
                        normalized_name = self.normalize_company_name_aggressive(candidate.get('title', ''))
                        name_exists = any(
                            self.normalize_company_name_aggressive(existing.get('title', '')) == normalized_name
                            for existing in all_candidates.values()
                        )

                        if not name_exists and normalized_key not in all_candidates:
                            # Ensure all required fields exist
                            candidate.setdefault('title', candidate.get('title', ''))
                            candidate.setdefault('priority', 'medium')
                            candidate.setdefault('found_count', 1)
                            candidate.setdefault('snippet', '')
                            candidate.setdefault('discovery_query', '')
                            all_candidates[normalized_key] = candidate

                print(f"📁 Loaded {len(all_candidates)} unique existing candidates (from {len(existing_candidates)} total)")
            except Exception as e:
                print(f"⚠️  Could not load existing candidates: {e}")

        # Try to load queries from config, then queries.py, otherwise use defaults
        try:
            from config import CUSTOM_SEARCH_QUERIES
            search_queries = CUSTOM_SEARCH_QUERIES
        except ImportError:
            # Try importing from queries.py
            try:
                import sys
                sys.path.insert(0, '..')
                from queries import ALL_QUERIES
                search_queries = ALL_QUERIES
            except ImportError:
                # Fallback to default queries if neither config nor queries.py available
                search_queries = [
                    # Default company search queries
                    "Find early-stage startups with venture capital funding in technology sector",
                    "Find Series A and Series B companies with strong revenue growth",
                    "Find SaaS companies with B2B business models seeking investment",
                    "Find startups in healthcare tech, fintech, and enterprise software",
                    "Find companies with technical founders and product-market fit",
                    "Find venture-backed startups with public investor information",
                ]

        print(f"Running {len(search_queries)} discovery searches using Perplexity API...")

        for i, query in enumerate(search_queries, 1):
            print(f"\n[{i}/{len(search_queries)}] Searching: {query[:70]}...")

            try:
                results = self.search(query, num_results=10)

                # Track stats for this query
                raw_count = len(results)
                filtered_count = 0
                new_count = 0
                duplicate_count = 0

                for result in results:
                    url = result.get('link', '')
                    title = result.get('title', '')

                    # Filter out placeholder company names and instructions
                    # Check original title and lowercase version
                    title_lower = title.lower().strip()
                    snippet_lower = result.get('snippet', '').lower()

                    # More comprehensive placeholder detection
                    is_placeholder = (
                        # Instructions/Examples
                        title_lower.startswith('if the') or
                        title_lower.startswith('if website') or
                        'short description' in title_lower or
                        'format:' in title_lower or
                        'example:' in title_lower or
                        # Brackets
                        title.startswith('[') or
                        title.startswith('(') or
                        # Generic names
                        title_lower.startswith('company name') or
                        title_lower.startswith('company xyz') or
                        title_lower.startswith('example') or
                        # Numbered companies
                        re.match(r'^company \d+', title_lower) or
                        re.match(r'^\[company', title_lower) or
                        # Backticks or quotes
                        title.startswith('`') or
                        title.startswith('"company') or
                        title.startswith("'company") or
                        # Very short or suspicious
                        len(title.strip()) < 2 or
                        title_lower == 'company' or
                        title_lower in ['startup', 'business', 'firm', 'corp', 'inc'] or
                        # Snippet contains instructions
                        'short description' in snippet_lower
                    )

                    if is_placeholder:
                        filtered_count += 1
                        print(f"    ⚠️ Skipping placeholder: '{title}'")
                        continue

                    # Allow URL_NEEDED as a valid placeholder
                    if not url:
                        filtered_count += 1
                        continue

                    # Accept URL_NEEDED placeholder or valid URLs
                    if url != 'URL_NEEDED' and not url.startswith('http'):
                        filtered_count += 1
                        continue

                    # Skip certain domains (only for actual URLs, not URL_NEEDED)
                    if url != 'URL_NEEDED':
                        skip_domains = ['wikipedia.org', 'youtube.com', 'facebook.com',
                                      'instagram.com', 'twitter.com', 'reddit.com',
                                      'linkedin.com', 'tiktok.com']
                        if any(domain in url.lower() for domain in skip_domains):
                            filtered_count += 1
                            continue

                    # Use URL as unique key (normalize URL for deduplication)
                    # For URL_NEEDED entries, use aggressively normalized company name as key
                    if url == 'URL_NEEDED':
                        # Aggressive normalization to catch "BrightWave" vs "Bright Wave Inc"
                        normalized_name = self.normalize_company_name_aggressive(result.get('title', ''))
                        normalized_key = f"name:{normalized_name}"
                    else:
                        # Remove protocol, www, trailing slash, and lowercase
                        normalized_key = url.lower().rstrip('/')
                        normalized_key = re.sub(r'^https?://', '', normalized_key)
                        normalized_key = re.sub(r'^www\.', '', normalized_key)
                        # Extract just the domain for better deduplication
                        normalized_key = f"url:{normalized_key.split('/')[0]}"

                    # ADDITIONAL CHECK: Also check if normalized NAME exists in any entry
                    # This catches duplicates where one has URL and one has URL_NEEDED
                    normalized_name_for_check = self.normalize_company_name_aggressive(result.get('title', ''))
                    name_exists = any(
                        self.normalize_company_name_aggressive(candidate.get('title', '')) == normalized_name_for_check
                        for candidate in all_candidates.values()
                    )

                    if normalized_key not in all_candidates and not name_exists:
                        all_candidates[normalized_key] = {
                            'title': result.get('title', ''),
                            'url': url,
                            'snippet': result.get('snippet', ''),
                            'discovery_query': query,
                            'found_count': 1,
                            'priority': 'medium'
                        }
                        new_count += 1
                    else:
                        # It's a duplicate - either by key or by name
                        if normalized_key in all_candidates:
                            all_candidates[normalized_key]['found_count'] += 1
                        duplicate_count += 1
                        if name_exists and normalized_key not in all_candidates:
                            print(f"    🔄 Duplicate name detected: {result.get('title', '')} (different URL)")

                # Detailed logging
                print(f"  API returned: {raw_count} results")
                if filtered_count > 0:
                    print(f"  Filtered out: {filtered_count} (invalid URLs or skip_domains)")
                print(f"  New companies: {new_count}")
                if duplicate_count > 0:
                    print(f"  Duplicates: {duplicate_count}")
                print(f"  Total unique: {len(all_candidates)}")

                # Save progress to CSV and JSON after each search
                self._save_progress(list(all_candidates.values()), csv_file, json_file)

            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
                continue

            time.sleep(SEARCH_DELAY)  # Rate limiting for Perplexity API

        # Convert to list and sort by found_count
        candidates = list(all_candidates.values())
        candidates.sort(key=lambda x: x['found_count'], reverse=True)

        print(f"\n✓ Discovery complete: {len(candidates)} unique candidates found")

        return candidates

    def search_investor_info(self, company_name: str, location: str = "") -> List[Dict]:
        """
        Search for investor information about a specific company from news articles, press releases, etc.
        This finds investor info that might not be on the company's website.
        """
        queries = [
            f'"{company_name}" investors',
            f'"{company_name}" funding round',
            f'"{company_name}" Series A B C',
            f'"{company_name}" venture capital',
        ]

        if location:
            queries.append(f'"{company_name}" {location} investors')

        all_results = []

        for query in queries:
            try:
                results = self.search(query, num_results=5)
                for result in results:
                    url = result.get('link', '')
                    # Only include news articles, press releases, and relevant sources
                    if any(domain in url.lower() for domain in [
                        'news', 'press', 'release', 'prnewswire', 'businesswire',
                        'crunchbase', 'techcrunch', 'venturebeat', 'medium',
                        'times', 'tribune', 'herald', 'journal',
                        'gazette', 'post', 'chronicle', 'observer', 'review'
                    ]):
                        all_results.append({
                            'url': url,
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', ''),
                            'query': query,
                            'type': 'investor_info'
                        })
                time.sleep(1)  # Rate limiting
            except Exception as e:
                continue

        return all_results

    def enrich_with_investor_searches(self, candidates: List[Dict]) -> List[Dict]:
        """
        For each discovered company, search for additional investor information from news/press releases
        """
        print(f"\n{'='*60}")
        print("ENRICHING: Searching for investor info from news/press releases")
        print(f"{'='*60}\n")

        enriched_candidates = []

        # Process all candidates (no limit)
        for i, candidate in enumerate(candidates, 1):
            company_name = candidate.get('title', '').split(' - ')[0].split(' | ')[0]
            # Clean up company name (remove common suffixes)
            company_name = re.sub(r'\s+(Inc|LLC|Ltd|Corp|Corporation)\.?$', '', company_name, flags=re.IGNORECASE)

            print(f"[{i}/{len(candidates)}] Searching investor info for: {company_name[:50]}...")

            investor_info = self.search_investor_info(company_name)

            if investor_info:
                candidate['investor_info_urls'] = [info['url'] for info in investor_info]
                candidate['investor_info_count'] = len(investor_info)
                print(f"  ✓ Found {len(investor_info)} investor info sources")
            else:
                candidate['investor_info_urls'] = []
                candidate['investor_info_count'] = 0

            enriched_candidates.append(candidate)

            # Save progress every 10 companies
            if len(enriched_candidates) % 10 == 0:
                self._save_progress(enriched_candidates, '../outputs/stage_1_progress.csv', '../outputs/stage_1.json')
                print(f"  💾 Progress saved ({len(enriched_candidates)}/{len(candidates)} companies enriched)")

            time.sleep(1.5)  # Rate limiting

        return enriched_candidates

    def filter_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Apply initial filtering to remove obvious non-matches
        """
        filtered = []

        exclude_keywords = [
            'consulting firm', 'law firm', 'accounting firm',
            'non-profit only', 'government agency',
            'established enterprise'  # If looking for startups
        ]

        for candidate in candidates:
            snippet_lower = candidate.get('snippet', '').lower()
            title_lower = candidate.get('title', '').lower()
            text = snippet_lower + ' ' + title_lower

            # Skip if contains exclusion keywords
            if any(keyword in text for keyword in exclude_keywords):
                continue

            # Prefer if contains positive keywords
            positive_keywords = ['startup', 'funding', 'investors', 'venture',
                               'saas', 'technology', 'innovation', 'growth']
            if any(keyword in text for keyword in positive_keywords):
                candidate['priority'] = 'high'
            else:
                candidate['priority'] = 'medium'

            filtered.append(candidate)

        print(f"✓ Filtered to {len(filtered)} promising candidates")
        return filtered


def main():
    """Run company discovery"""
    discovery = CompanyDiscovery()

    print("=" * 60)
    print("STAGE 1: COMPANY DISCOVERY")
    print("=" * 60)

    output_file = '../outputs/stage_1.json'

    # Count existing candidates before discovery
    existing_count = 0
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_count = len(json.load(f))
        except:
            pass

    # Discover companies (this now loads existing candidates internally and merges)
    candidates = discovery.discover_companies()

    # Filter candidates
    filtered_candidates = discovery.filter_candidates(candidates)

    # Save final results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_candidates, f, indent=2, ensure_ascii=False)

    # Save final CSV
    csv_file = '../outputs/stage_1_progress.csv'
    discovery._save_progress(filtered_candidates, csv_file, output_file)

    print(f"\n✓ Results saved to {output_file}")
    print(f"✓ Total candidates: {len(filtered_candidates)} ({existing_count} existing + {len(filtered_candidates) - existing_count} new)")
    print(f"  - High priority: {sum(1 for c in filtered_candidates if c.get('priority') == 'high')}")
    print(f"  - Medium priority: {sum(1 for c in filtered_candidates if c.get('priority') == 'medium')}")

    # Show top 10 candidates
    print(f"\nTop {min(10, len(filtered_candidates))} candidates by frequency:")
    sorted_candidates = sorted(filtered_candidates, key=lambda x: x.get('found_count', 0), reverse=True)
    for i, candidate in enumerate(sorted_candidates[:10], 1):
        print(f"{i}. {candidate['title']}")
        print(f"   {candidate['url']}")
        print(f"   Found {candidate['found_count']} times\n")

    return filtered_candidates


if __name__ == '__main__':
    main()
