"""
Stage 3: Data Enrichment & Gap Filling
Uses Perplexity and external sources to fill missing information
"""
import os
import json
import csv
import time
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.env')

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

perplexity_client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
) if PERPLEXITY_API_KEY else None

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class DataEnricher:
    def __init__(self):
        self.perplexity = perplexity_client
        self.openai = openai_client

    def search_for_missing_data(self, company_name: str, url: str, missing_fields: List[str]) -> Dict:
        """Use Perplexity to search for missing company information"""
        if not self.perplexity:
            return {}

        queries = []

        if 'funding' in missing_fields:
            queries.append(f'"{company_name}" funding investors series A B C venture capital')

        if 'location' in missing_fields:
            queries.append(f'"{company_name}" headquarters location address city')

        if 'founders' in missing_fields:
            queries.append(f'"{company_name}" founders CEO co-founders team')

        if 'social' in missing_fields:
            queries.append(f'"{company_name}" LinkedIn Crunchbase Twitter')

        all_findings = []

        for query in queries:
            try:
                print(f"    Searching: {query[:60]}...")
                response = self.perplexity.chat.completions.create(
                    model="sonar-pro",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a research assistant finding factual information about companies. Provide specific, factual details with sources."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    temperature=0.2,
                    max_tokens=1500
                )

                findings = response.choices[0].message.content
                all_findings.append(findings)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"    Search error: {e}")
                continue

        return {
            'search_results': '\n\n'.join(all_findings),
            'company_name': company_name
        }

    def extract_structured_data(self, company_data: Dict, search_results: str) -> Dict:
        """Use AI to extract structured information from search results AND scraped content"""
        if not self.openai:
            return {}

        # Include scraped website content if available
        website_content = ""
        scraped = company_data.get('scraped_content', {})
        if scraped:
            main = scraped.get('main_content', '')[:5000]  # First 5000 chars
            about = scraped.get('about_content', '')[:3000]  # First 3000 chars
            if main or about:
                website_content = f"\n\nWebsite Content:\n{main}\n{about}"

            # Include investor page content (dedicated investor/team/funding pages)
            investor_pages = scraped.get('investor_page_content', [])
            if investor_pages:
                website_content += "\n\nInvestor/Team Pages:"
                for page in investor_pages[:3]:  # Top 3 investor pages
                    page_content = page.get('content', '')[:2000]  # First 2000 chars per page
                    if page_content:
                        website_content += f"\n{page_content}"

            # Include investor info content (news articles, press releases about funding)
            investor_info = scraped.get('investor_info_content', [])
            if investor_info:
                website_content += "\n\nNews Articles & Press Releases about Funding:"
                for article in investor_info[:3]:  # Top 3 articles
                    article_content = article.get('content', '')[:2000]  # First 2000 chars per article
                    if article_content:
                        website_content += f"\n{article_content}"

        prompt = f"""Extract structured information about this company from ALL sources below.

Company Name: {company_data.get('company_name')}
Website: {company_data.get('url')}

Existing Information from Phase 1 & 2:
- Description/Snippet: {company_data.get('snippet', 'Unknown')}
- Social Links: {company_data.get('social_links', 'None found')}

External Search Results:
{search_results}

Scraped Content (website, investor pages, news articles):
{website_content}

IMPORTANT: Prioritize information from scraped content over search results when available.

Extract and return ONLY the following in JSON format:
{{
  "founders": "Full names of founders/co-founders (comma-separated) or keep existing if better",
  "funding_info": "Detailed funding: rounds (Seed/Series A/B/C), amounts, lead investors, year. Be specific.",
  "location": "City, State (e.g., Denver, CO) or City, Country",
  "headquarters": "Full headquarters address if available",
  "linkedin": "LinkedIn company URL if mentioned",
  "crunchbase": "Crunchbase URL if mentioned",
  "latest_funding_date": "Most recent funding date (YYYY-MM or YYYY)",
  "total_funding": "Total funding amount (e.g., $50M)",
  "key_investors": ["Investor 1", "Investor 2", "Investor 3"]
}}

If information is not found in the search results, use "Not found" or empty array.
Be specific with funding details - include round type, amount, and investors.
"""

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Extract factual information and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            extracted = json.loads(response.choices[0].message.content)
            return extracted

        except Exception as e:
            print(f"    Extraction error: {e}")
            return {}

    def enrich_company(self, company_data: Dict) -> Dict:
        """Enrich a single company's data"""
        print(f"\n  Analyzing: {company_data.get('company_name')}")

        # Check if we already have rich investor info from scraped news articles
        scraped = company_data.get('scraped_content', {})
        investor_info_content = scraped.get('investor_info_content', [])
        has_rich_investor_info = len(investor_info_content) > 0

        # Determine what fields need external searches
        missing_fields = []

        # Only search for funding if we don't have investor info content
        if not has_rich_investor_info:
            missing_fields.append('funding')
        else:
            print(f"    ✓ Using scraped investor info content (skipping funding search)")

        # Always check for location and founders (might not be in investor articles)
        missing_fields.extend(['location', 'founders'])

        # Check if social links need enhancement
        social_links = company_data.get('social_links', '')
        if 'linkedin' not in social_links.lower() or 'crunchbase' not in social_links.lower():
            missing_fields.append('social')

        # Search for missing data (only if we have fields that need searching)
        search_results = {'search_results': ''}
        if missing_fields:
            print(f"    Searching for: {', '.join(missing_fields)}")
            search_results = self.search_for_missing_data(
                company_data.get('company_name'),
                company_data.get('url'),
                missing_fields
            )
        else:
            print(f"    ✓ All data available from scraped content, skipping searches")

        # Extract structured data from search results
        print(f"    🤖 Extracting structured data...")
        enriched_data = self.extract_structured_data(company_data, search_results['search_results'])

        # Build enriched company data
        enriched_company = company_data.copy()

        # Add all extracted data (Phase 2 didn't extract these)
        enriched_company['description'] = company_data.get('snippet', '')  # Use Phase 1 snippet
        enriched_company['founders'] = enriched_data.get('founders', 'Not found')
        enriched_company['funding_info'] = enriched_data.get('funding_info', 'Not found')
        enriched_company['location'] = enriched_data.get('location', 'Not found')
        enriched_company['headquarters'] = enriched_data.get('headquarters', '')
        enriched_company['latest_funding_date'] = enriched_data.get('latest_funding_date', '')
        enriched_company['total_funding'] = enriched_data.get('total_funding', '')
        enriched_company['key_investors'] = ', '.join(enriched_data.get('key_investors', []))

        # Update social links
        social_parts = [s.strip() for s in enriched_company.get('social_links', '').split(',') if s.strip()]

        if enriched_data.get('linkedin'):
            if not any('linkedin' in s.lower() for s in social_parts):
                social_parts.append(f"linkedin: {enriched_data['linkedin']}")

        if enriched_data.get('crunchbase'):
            if not any('crunchbase' in s.lower() for s in social_parts):
                social_parts.append(f"crunchbase: {enriched_data['crunchbase']}")

        enriched_company['social_links'] = ', '.join(social_parts)

        print(f"    ✓ Enriched successfully")

        return enriched_company


def filter_colorado_companies(companies: List[Dict]) -> List[Dict]:
    """
    Filter to only keep companies headquartered in Colorado.
    Removes companies not in CO.
    """
    colorado_companies = []
    removed = []

    for company in companies:
        location = str(company.get('location', '')).lower()
        headquarters = str(company.get('headquarters', '')).lower()

        # Check if Colorado/CO is mentioned in location fields
        is_colorado = (
            'colorado' in location or
            'colorado' in headquarters or
            ', co' in location or
            location.endswith(' co')
        )

        if is_colorado:
            colorado_companies.append(company)
        else:
            removed.append(company.get('company_name', 'Unknown'))

    if removed:
        print(f"\n🗑️  Removed {len(removed)} non-Colorado companies:")
        for name in removed[:10]:  # Show first 10
            print(f"     - {name}")
        if len(removed) > 10:
            print(f"     ... and {len(removed) - 10} more")

    return colorado_companies


def main():
    """Run data enrichment on Stage 2 results"""
    print("=" * 60)
    print("STAGE 3: DATA ENRICHMENT & GAP FILLING")
    print("=" * 60)

    # Load existing enriched data if it exists
    output_json = '../outputs/stage_3.json'
    enriched_companies = []
    enriched_urls = set()

    if os.path.exists(output_json):
        print(f"\n📁 Found existing enriched data file")
        with open(output_json, 'r', encoding='utf-8') as f:
            enriched_companies = json.load(f)
        enriched_urls = {c.get('url', '') for c in enriched_companies}
        print(f"   Loaded {len(enriched_companies)} existing enriched companies")

    # Load Stage 2 CSV for basic info
    csv_file = '../outputs/stage_2_progress.csv'
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            companies_csv = list(reader)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Run stage_2.py first.")
        return

    # Load Stage 2 JSON for full scraped content
    json_file = '../outputs/stage_2.json'
    scraped_content = {}
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            # Index by URL for easy lookup
            for item in scraped_data:
                url = item.get('url', '')
                scraped_content[url] = {
                    'main_content': item.get('main_content', ''),
                    'about_content': item.get('about_content', ''),
                    'investor_page_content': item.get('investor_page_content', []),
                    'investor_info_content': item.get('investor_info_content', [])
                }
        print(f"✓ Loaded full content from {json_file}")
    except FileNotFoundError:
        print(f"⚠️  Warning: {json_file} not found. Will work with limited data.")

    # Merge CSV data with scraped content and filter out already enriched
    companies = []
    for company in companies_csv:
        url = company.get('url', '')
        # Skip if already enriched
        if url in enriched_urls:
            continue
        if url in scraped_content:
            company['scraped_content'] = scraped_content[url]
        companies.append(company)

    print(f"\nLoaded {len(companies_csv)} companies from Stage 2")
    print(f"🔍 Found {len(companies)} NEW companies to enrich (skipping {len(companies_csv) - len(companies)} already enriched)")

    if not companies:
        print("⚠️  No new companies to enrich! All have already been processed.")
        return enriched_companies

    enricher = DataEnricher()
    new_enriched = []

    for i, company in enumerate(companies, 1):
        if company.get('success') != 'Yes':
            print(f"\n[{i}/{len(companies)}] Skipping {company.get('company_name')} (scraping failed)")
            new_enriched.append(company)
            continue

        print(f"\n[{i}/{len(companies)}] Enriching: {company.get('company_name')}")

        enriched = enricher.enrich_company(company)
        new_enriched.append(enriched)

        # Merge with existing enriched data
        all_enriched = enriched_companies + new_enriched

        # Save progress to BOTH CSV and JSON after each company
        csv_file = '../outputs/stage_3_progress.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'company_name', 'url', 'description', 'founders',
                'funding_info', 'latest_funding_date', 'total_funding', 'key_investors',
                'location', 'headquarters', 'social_links', 'success'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_enriched)

        # Also save JSON for backup/Phase 4
        json_file = '../outputs/stage_3.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_enriched, f, indent=2, ensure_ascii=False)

        print(f"  💾 Progress saved ({i}/{len(companies)} new companies)")

        time.sleep(1)  # Rate limiting

    print(f"\n✓ Enrichment complete!")
    print(f"✓ Total enriched: {len(all_enriched)} companies ({len(enriched_companies)} existing + {len(new_enriched)} new)")

    # Filter to only Colorado companies
    all_enriched = filter_colorado_companies(all_enriched)
    print(f"✓ After Colorado filter: {len(all_enriched)} companies")

    # Save final filtered results
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_enriched, f, indent=2, ensure_ascii=False)

    csv_file = '../outputs/stage_3_progress.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'company_name', 'url', 'description', 'founders',
            'funding_info', 'latest_funding_date', 'total_funding', 'key_investors',
            'location', 'headquarters', 'social_links', 'success'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_enriched)

    print(f"✓ Results saved to {output_json}")

    # Summary
    complete_count = sum(1 for c in all_enriched
                        if c.get('funding_info') and c.get('funding_info') != 'Not found')
    print(f"\n  - Companies with funding info: {complete_count}/{len(all_enriched)}")

    return all_enriched


if __name__ == '__main__':
    main()
