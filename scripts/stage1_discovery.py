"""
Stage 1: Company Discovery
Uses Perplexity API to find candidate companies/startups
"""
import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import time
from openai import OpenAI

load_dotenv('../.env')

# Import config settings
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

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Perform Perplexity search and extract company URLs
        """
        system_prompt = """You are a research assistant finding company and startup websites.
For each company you find, provide:
1. The official company website URL
2. The company name
3. A brief description

Format your response as a list with one company per line:
- Company Name | URL | Brief description

Focus on finding official company websites, not social media or job posting pages.
Only include companies that match the search criteria."""

        user_prompt = f"""Find {num_results} company websites that match this search: {query}

Return a list of companies with their official website URLs, names, and brief descriptions.
Format: Company Name | URL | Description"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Use configured model (sonar or sonar-pro)
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            
            # Extract URLs and information from response
            results = self._parse_perplexity_response(content, query)
            
            # Avoid rate limiting
            time.sleep(1)
            
            return results

        except Exception as e:
            print(f"Error during Perplexity search: {e}")
            return []

    def _parse_perplexity_response(self, content: str, query: str) -> List[Dict]:
        """
        Parse Perplexity response to extract company URLs and information
        """
        results = []

        # Extract URLs from the response
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, content)

        # Also try to extract structured format (Name | URL | Description)
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try to parse "Name | URL | Description" format
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    name = parts[0].lstrip('- ').strip()
                    url = parts[1].strip()
                    snippet = parts[2].strip() if len(parts) > 2 else ""

                    # Clean URL
                    url = re.sub(r'[^\w\s:/.-]', '', url)
                    if url.startswith('http'):
                        results.append({
                            'title': name,
                            'link': url,
                            'snippet': snippet or f"Company found via search"
                        })
                        continue

            # Extract URL from line if present
            url_match = re.search(url_pattern, line)
            if url_match:
                url = url_match.group(0)
                # Remove URL from line to get name/description
                name_desc = line.replace(url, '').strip().lstrip('- ').strip()
                results.append({
                    'title': name_desc.split('|')[0].strip() if '|' in name_desc else name_desc,
                    'link': url,
                    'snippet': name_desc if len(name_desc) > 50 else f"Company found via search"
                })

        # If we didn't get structured results, use URLs found in text
        if not results and urls:
            for url in urls[:10]:  # Limit to 10 URLs
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
                        'title': name[:100],  # Limit title length
                        'link': url,
                        'snippet': context[:200] if len(context) > 200 else context
                    })

        return results[:10]  # Limit to 10 results

    def _save_progress_csv(self, candidates: List[Dict], filename: str):
        """Save current progress to CSV"""
        import csv
        import os

        if not candidates:
            return

        try:
            # Define CSV columns
            fieldnames = ['company_name', 'url', 'found_count', 'priority', 'investor_info_count', 'snippet', 'discovery_query']

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for candidate in candidates:
                    writer.writerow({
                        'company_name': candidate.get('title', ''),
                        'url': candidate.get('url', ''),
                        'found_count': candidate.get('found_count', 0),
                        'priority': candidate.get('priority', 'medium'),
                        'investor_info_count': candidate.get('investor_info_count', 0),
                        'snippet': candidate.get('snippet', '')[:200],  # Truncate for readability
                        'discovery_query': candidate.get('discovery_query', '')[:100]
                    })

            # Also save JSON backup
            json_backup = filename.replace('.csv', '_backup.json')
            with open(json_backup, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"  Warning: Could not save progress CSV: {e}")

    def discover_companies(self) -> List[Dict]:
        """
        Discover companies/startups using multiple search strategies
        """
        all_candidates = {}

        # CSV header for incremental saving
        import csv
        csv_file = 'stage1_progress.csv'
        csv_exists = False

        # Try to load queries from config, otherwise use defaults
        try:
            from config import CUSTOM_SEARCH_QUERIES
            search_queries = CUSTOM_SEARCH_QUERIES
        except ImportError:
            # Fallback to default queries if config not available
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

                for result in results:
                    url = result.get('link', '')

                    if not url or not url.startswith('http'):
                        continue

                    # Skip certain domains
                    skip_domains = ['wikipedia.org', 'youtube.com', 'facebook.com',
                                  'instagram.com', 'twitter.com', 'reddit.com',
                                  'linkedin.com', 'tiktok.com']
                    if any(domain in url.lower() for domain in skip_domains):
                        continue

                    # Use URL as unique key (normalize URL)
                    normalized_url = url.rstrip('/').lower()
                    
                    if normalized_url not in all_candidates:
                        all_candidates[normalized_url] = {
                            'url': url,
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', ''),
                            'discovery_query': query,
                            'found_count': 1
                        }
                    else:
                        all_candidates[normalized_url]['found_count'] += 1

                print(f"  Found {len(results)} results ({len(all_candidates)} unique total)")

                # Save progress to CSV after each search
                self._save_progress_csv(list(all_candidates.values()), csv_file)

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
                self._save_progress_csv(enriched_candidates, 'stage1_progress.csv')
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

    output_file = '../outputs/stage1_candidates.json'

    # Load existing candidates if they exist
    existing_candidates = []
    existing_urls = set()
    if os.path.exists(output_file):
        print(f"\n📁 Found existing candidates file")
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_candidates = json.load(f)
        existing_urls = {c['url'] for c in existing_candidates}
        print(f"   Loaded {len(existing_candidates)} existing candidates")

    # Discover companies
    candidates = discovery.discover_companies()

    # Filter candidates
    filtered_candidates = discovery.filter_candidates(candidates)

    # Only keep NEW candidates (not in existing)
    new_candidates = [c for c in filtered_candidates if c['url'] not in existing_urls]
    print(f"\n🔍 Found {len(new_candidates)} NEW candidates (filtered {len(filtered_candidates) - len(new_candidates)} duplicates)")

    # Enrich with investor info searches (optional - can be disabled if too slow)
    if new_candidates:
        try:
            from config import ENABLE_SPONSOR_INFO_SEARCHES  # Keeping same config var name for now
            if ENABLE_SPONSOR_INFO_SEARCHES:
                new_candidates = discovery.enrich_with_investor_searches(new_candidates)
        except ImportError:
            # Default to enabled
            new_candidates = discovery.enrich_with_investor_searches(new_candidates)

    # Merge with existing candidates
    all_candidates = existing_candidates + new_candidates

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to {output_file}")
    print(f"✓ Total candidates: {len(all_candidates)} ({len(existing_candidates)} existing + {len(new_candidates)} new)")
    print(f"  - High priority: {sum(1 for c in all_candidates if c.get('priority') == 'high')}")
    print(f"  - Medium priority: {sum(1 for c in all_candidates if c.get('priority') == 'medium')}")

    # Show top 10 NEW candidates
    if new_candidates:
        print(f"\nTop {min(10, len(new_candidates))} NEW candidates:")
        for i, candidate in enumerate(new_candidates[:10], 1):
            print(f"{i}. {candidate['title']}")
            print(f"   {candidate['url']}")
            print(f"   Found {candidate['found_count']} times\n")
    else:
        print("\n⚠️  No new candidates found (all were duplicates)")

    return all_candidates


if __name__ == '__main__':
    main()
