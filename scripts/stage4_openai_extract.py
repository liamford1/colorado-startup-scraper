#!/usr/bin/env python3
"""
Stage 4: OpenAI-Powered Data Extraction & Summarization
Uses OpenAI to intelligently extract and summarize investment data
"""
import json
import csv
import os
import sys
from datetime import datetime
from openai import OpenAI
from tqdm import tqdm

# Load API key from parent .env
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def extract_company_intelligence(company_data: dict) -> dict:
    """
    Use OpenAI to extract comprehensive intelligence from company data
    Reuses existing stage3 data where available to avoid redundant API calls
    """

    # First, extract what we already have from stage3 (no OpenAI needed)
    existing_data = {
        'company_name': company_data.get('company_name', ''),
        'url': company_data.get('url', ''),
        'description': company_data.get('description', ''),
        'founders': company_data.get('founders', ''),
        'location': company_data.get('location', ''),
        'headquarters': company_data.get('headquarters', ''),
        'latest_funding_date': company_data.get('latest_funding_date', ''),
        'total_funding': company_data.get('total_funding', ''),
        'key_investors': company_data.get('key_investors', ''),
    }

    # Parse social links from stage3
    social_links = company_data.get('social_links', '')
    linkedin = ''
    crunchbase = ''
    if social_links:
        for link in social_links.split(','):
            link = link.strip()
            if 'linkedin' in link.lower():
                linkedin = link.split(': ')[-1] if ': ' in link else link
                if linkedin and linkedin != 'Not found':
                    existing_data['linkedin_url'] = linkedin
            elif 'crunchbase' in link.lower():
                crunchbase = link.split(': ')[-1] if ': ' in link else link
                if crunchbase and crunchbase != 'Not found':
                    existing_data['crunchbase_url'] = crunchbase

    # Prepare the data for OpenAI (remove massive scraped content to save tokens)
    simplified_data = {
        'company_name': company_data.get('company_name', ''),
        'description': company_data.get('description', ''),
        'snippet': company_data.get('snippet', ''),
        'founders': company_data.get('founders', ''),
        'funding_info': company_data.get('funding_info', []),
        'location': company_data.get('location', ''),
        'headquarters': company_data.get('headquarters', ''),
        'latest_funding_date': company_data.get('latest_funding_date', ''),
        'total_funding': company_data.get('total_funding', ''),
        'key_investors': company_data.get('key_investors', ''),
    }

    # If scraped content exists and is reasonable size, include a sample
    scraped = company_data.get('scraped_content', {})
    if scraped and scraped.get('main_content'):
        main_content = scraped['main_content'][:1500]  # First 1500 chars only
        simplified_data['content_sample'] = main_content

    prompt = f"""You are a venture capital analyst extracting structured data from company information.

Analyze the following company data and extract comprehensive intelligence in JSON format.

COMPANY DATA:
{json.dumps(simplified_data, indent=2)}

Extract and return a JSON object with the following fields:

NOTE: Some fields may already be provided in the data (founders, description, location, etc.).
If they exist and look good, keep them. Only extract/improve if missing or unclear.

{{
  "location_city": "City only (extract from location field)",
  "location_state": "State abbreviation (e.g., CO, CA)",

  "total_funding_normalized": "Total funding as clean number with unit (e.g., '$221M', '$1.2B'), or 'Unknown'",
  "num_funding_rounds": "Number of funding rounds (integer)",
  "funding_stage_progression": "Funding progression (e.g., 'Seed → Series A → Series C'), or 'Unknown'",
  "latest_round": "Latest funding round name (e.g., 'Series C'), or 'Unknown'",
  "latest_round_amount": "Latest round amount normalized (e.g., '$140M'), or 'Unknown'",
  "latest_round_date": "Latest round date (YYYY-MM or YYYY format), or 'Unknown'",
  "years_since_last_funding": "Years since last funding (integer, or -1 if unknown)",

  "total_investor_count": "Total number of unique investors (integer)",
  "lead_investors": "Top 3-5 lead investors (comma-separated)",
  "all_investors": "All investors mentioned (comma-separated)",
  "notable_tier1_investors": "Notable tier-1 VCs (Sequoia, a16z, Kleiner Perkins, etc.), comma-separated, or empty",
  "has_colorado_investors": "Yes/No - are any investors Colorado-based?",

  "industry_categories": "2-4 industry categories (e.g., 'AI, Enterprise Software, SaaS')",
  "business_model": "Business model type (e.g., 'B2B SaaS', 'Hardware', 'Marketplace', 'Consumer', etc.)",
  "company_stage": "Company stage (e.g., 'Seed', 'Early Growth', 'Growth', 'Late Stage', 'Mature')",
  "technology_focus": "Technology focus areas (e.g., 'DeepTech, AI/ML', 'CleanTech', 'Biotech', 'FinTech', etc.)",
  "target_market": "Target market (e.g., 'Enterprise', 'SMB', 'Consumer', 'Government', etc.)",
  "colorado_connection": "High/Medium/Low based on Colorado HQ + Colorado founders",

  "has_funding_info": "Yes/No",
  "has_founders": "Yes/No",
  "has_location": "Yes/No",
  "data_completeness": "Score 1-10 based on data quality"
}}

IMPORTANT INSTRUCTIONS:
- Normalize all funding amounts to consistent format with M/B suffix (e.g., $45M, $1.2B)
- Parse funding_info array carefully to extract all rounds, investors, and amounts
- Identify tier-1 VCs: Sequoia, a16z, Accel, Kleiner Perkins, Benchmark, Greylock, Lightspeed, etc.
- Colorado investors include: Foundry Group, Access Venture Partners, Boulder Ventures, Ridgeline, Blackhorn, etc.
- For funding progression, show the sequence (e.g., "Seed → Series A → Series B → Series C")
- Calculate years_since_last_funding from latest_round_date to current year (2025)
- Focus on extracting NEW insights (industry, business model, stage, etc.) from the data
- Return ONLY valid JSON, no additional text

Return the JSON object:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Merge with existing data (prefer existing if available)
        final_result = existing_data.copy()
        final_result.update(result)

        # Clean company name (remove numbering)
        if final_result.get('company_name'):
            name = final_result['company_name']
            # Remove leading numbers and dots
            import re
            name = re.sub(r'^\d+\.\s*', '', name)
            final_result['company_name'] = name

        return final_result

    except Exception as e:
        print(f"Error processing {company_data.get('company_name', 'Unknown')}: {e}")
        # Return existing data on error
        existing_data['error'] = str(e)
        return existing_data


def process_all_companies(input_file: str, output_file: str, test_mode: bool = False):
    """
    Process all companies and extract intelligence
    Saves incrementally so you can stop anytime
    """
    print("=" * 70)
    print("STAGE 4: OPENAI-POWERED DATA EXTRACTION")
    print("=" * 70)

    # Load companies
    print(f"\nLoading companies from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print(f"Found {len(companies)} companies")

    # Filter to successful scrapes only
    companies = [c for c in companies if c.get('success') == 'Yes']
    print(f"Filtered to {len(companies)} successful companies")

    # Test mode: only process first 5
    if test_mode:
        companies = companies[:5]
        print(f"\n⚠️  TEST MODE: Processing only {len(companies)} companies")

    # Check if we have existing progress to resume from
    results = []
    processed_urls = set()
    processed_names = set()

    json_output = output_file.replace('.csv', '.json')
    if os.path.exists(json_output):
        print(f"\n📁 Found existing progress file: {json_output}")
        with open(json_output, 'r', encoding='utf-8') as f:
            results = json.load(f)
        # Track both URLs and company names to avoid duplicates
        processed_urls = {r.get('url', '') for r in results}
        processed_names = {r.get('company_name', '').lower().strip() for r in results}
        print(f"   Loaded {len(results)} existing companies")

    # Filter out already processed companies (by URL and name)
    new_companies = []
    for company in companies:
        url = company.get('url', '')
        name = company.get('company_name', '').lower().strip()

        # Skip if already processed (by URL or name)
        if url in processed_urls or name in processed_names:
            continue

        new_companies.append(company)

    print(f"\n🔍 Found {len(new_companies)} NEW companies to process")
    print(f"   Skipping {len(companies) - len(new_companies)} already processed companies")

    if not new_companies:
        print("⚠️  No new companies to process! All have already been extracted.")
        return

    # Process each company
    print(f"\nExtracting intelligence with OpenAI...")
    print(f"Will save progress after every company to: {json_output}\n")

    for i, company in enumerate(tqdm(new_companies,
                                     desc="Processing companies")):
        try:
            extracted = extract_company_intelligence(company)
            results.append(extracted)

            # Track this company to avoid duplicates
            processed_urls.add(extracted.get('url', ''))
            processed_names.add(extracted.get('company_name', '').lower().strip())

            # SAVE AFTER EACH COMPANY (incremental save)
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user! Progress saved.")
            print(f"   Processed {len(results)} total companies ({len(results) - len(new_companies)} existing + {len(new_companies)} new)")
            print(f"   Resume anytime by running the script again")
            break
        except Exception as e:
            print(f"\n❌ Error on company {i}: {e}")
            # Save progress even on error
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            continue

    # Save final CSV
    print(f"\n💾 Saving final CSV to {output_file}...")

    # Define field order for CSV
    fieldnames = [
        # Core Info
        'company_name', 'url', 'description', 'founders',

        # Location
        'location_city', 'location_state', 'location', 'headquarters',

        # Social Links
        'linkedin_url', 'crunchbase_url',

        # Funding Summary
        'total_funding_normalized', 'total_funding', 'num_funding_rounds', 'funding_stage_progression',
        'latest_round', 'latest_round_amount', 'latest_round_date', 'latest_funding_date', 'years_since_last_funding',

        # Investors
        'total_investor_count', 'lead_investors', 'all_investors', 'key_investors',
        'notable_tier1_investors', 'has_colorado_investors',

        # Company Intelligence
        'industry_categories', 'business_model', 'company_stage',
        'technology_focus', 'target_market', 'colorado_connection',

        # Data Quality
        'has_funding_info', 'has_founders', 'has_location', 'data_completeness'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Extraction complete!")
    print(f"✅ CSV saved to: {output_file}")
    print(f"✅ JSON saved to: {json_output}")
    print(f"\n📊 Summary:")
    print(f"   - Total companies processed: {len(results)}")

    # Calculate stats
    with_funding = sum(1 for r in results if r.get('has_funding_info') == 'Yes')
    with_founders = sum(1 for r in results if r.get('has_founders') == 'Yes')
    with_tier1 = sum(1 for r in results if r.get('notable_tier1_investors', '').strip())
    with_co_investors = sum(1 for r in results if r.get('has_colorado_investors') == 'Yes')

    print(f"   - Companies with funding info: {with_funding}")
    print(f"   - Companies with founders: {with_founders}")
    print(f"   - Companies with tier-1 VCs: {with_tier1}")
    print(f"   - Companies with Colorado investors: {with_co_investors}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenAI-powered company data extraction")
    parser.add_argument('--test', action='store_true', help='Test mode: only process 5 companies')
    args = parser.parse_args()

    input_file = '../outputs/stage3_enriched.json'
    output_file = '../outputs/FINAL_Investment_Intelligence.csv'

    if args.test:
        output_file = '../outputs/TEST_Investment_Intelligence.csv'

    process_all_companies(input_file, output_file, test_mode=args.test)

    print("\n" + "=" * 70)
    print("✅ COMPLETE! Ready to analyze your investment intelligence.")
    print("=" * 70)


if __name__ == '__main__':
    main()
