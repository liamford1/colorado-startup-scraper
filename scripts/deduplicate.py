"""
Temporary Deduplication Script
Removes duplicates and cleans up company names in existing data files
"""
import os
import json
import re
from datetime import datetime
from typing import List, Dict


def normalize_url(url: str) -> str:
    """Normalize URL for comparison"""
    if not url:
        return ""
    # Remove protocol, www, trailing slash
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    return url


def clean_company_name(name: str) -> str:
    """Clean company name - remove markdown formatting, numbered prefixes, extra spaces, etc."""
    if not name:
        return ""

    # Remove numbered list prefixes like "1. ", "2. ", etc.
    name = re.sub(r'^\d+\.\s*', '', name)

    # Remove markdown bold (**text**)
    name = re.sub(r'\*\*(.+?)\*\*', r'\1', name)

    # Remove markdown italic (*text* or _text_)
    name = re.sub(r'\*(.+?)\*', r'\1', name)
    name = re.sub(r'_(.+?)_', r'\1', name)

    # Remove any remaining asterisks
    name = name.replace('*', '')

    # Clean up whitespace
    name = ' '.join(name.split())

    # Remove leading/trailing special characters
    name = name.strip('- •·')

    return name.strip()


def normalize_company_name(name: str) -> str:
    """Normalize company name for duplicate detection"""
    if not name:
        return ""
    # Remove leading numbers (like "1. ")
    name = re.sub(r'^\d+\.\s*', '', name)
    # Convert to lowercase
    name = name.lower().strip()
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name


def get_domain_from_url(url: str) -> str:
    """Extract main domain from URL (without subdomain)"""
    if not url:
        return ""
    # Remove protocol
    domain = re.sub(r'^https?://', '', url.lower().strip())
    # Remove www
    domain = re.sub(r'^www\.', '', domain)
    # Remove path
    domain = domain.split('/')[0]
    # Remove port
    domain = domain.split(':')[0]
    # Get main domain (last 2 parts)
    parts = domain.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return domain


def are_likely_same_company(company1: Dict, company2: Dict) -> bool:
    """Check if two companies are likely the same based on name and domain"""
    # Get normalized names
    name1 = normalize_company_name(company1.get('title') or company1.get('company_name', ''))
    name2 = normalize_company_name(company2.get('title') or company2.get('company_name', ''))

    # Different names = different companies
    if name1 != name2:
        return False

    # Same normalized name - check if domains are similar
    url1 = company1.get('url', '')
    url2 = company2.get('url', '')

    domain1 = get_domain_from_url(url1)
    domain2 = get_domain_from_url(url2)

    # If domains match, definitely same company
    if domain1 == domain2:
        return True

    # If one domain is contained in the other, likely same company
    # (e.g., brightwave.io and brightwaveai.com both contain "brightwave")
    if domain1 and domain2:
        base1 = domain1.split('.')[0]
        base2 = domain2.split('.')[0]
        # Remove common suffixes
        for suffix in ['ai', 'io', 'com', 'co']:
            base1 = base1.replace(suffix, '')
            base2 = base2.replace(suffix, '')

        # If bases are very similar, consider them the same
        if base1 in base2 or base2 in base1:
            return True

    # Same name but very different domains = likely same company with multiple domains
    # (in practice, this is almost always true for startups)
    return True


def deduplicate_companies(companies: List[Dict]) -> List[Dict]:
    """
    Deduplicate companies by normalized URL AND company name
    Keep the entry with the most complete information
    """
    # First pass: deduplicate by exact URL
    url_map = {}
    for company in companies:
        url = company.get('url', '')
        if not url:
            continue

        normalized_url = normalize_url(url)

        if normalized_url not in url_map:
            url_map[normalized_url] = company
        else:
            # Keep the one with more information
            existing = url_map[normalized_url]
            existing_fields = sum(1 for v in existing.values() if v and str(v).strip() and str(v) != 'Not found')
            new_fields = sum(1 for v in company.values() if v and str(v).strip() and str(v) != 'Not found')
            if new_fields > existing_fields:
                url_map[normalized_url] = company

    # Second pass: deduplicate by company name
    name_map = {}
    result = []

    for company in url_map.values():
        name = normalize_company_name(company.get('title') or company.get('company_name', ''))

        if not name:
            result.append(company)
            continue

        if name not in name_map:
            name_map[name] = company
            result.append(company)
        else:
            # Check if they're likely the same company
            existing = name_map[name]
            if are_likely_same_company(existing, company):
                # Same company - keep the one with more complete data
                existing_fields = sum(1 for v in existing.values() if v and str(v).strip() and str(v) != 'Not found')
                new_fields = sum(1 for v in company.values() if v and str(v).strip() and str(v) != 'Not found')

                if new_fields > existing_fields:
                    # Replace with better entry
                    result.remove(existing)
                    name_map[name] = company
                    result.append(company)
            else:
                # Different companies with same name - keep both
                result.append(company)

    return result


def clean_all_names(companies: List[Dict]) -> List[Dict]:
    """Clean company names in all entries"""
    for company in companies:
        # Clean 'title' field (used in stage 1)
        if 'title' in company:
            company['title'] = clean_company_name(company['title'])

        # Clean 'company_name' field (used in stages 2-3)
        if 'company_name' in company:
            company['company_name'] = clean_company_name(company['company_name'])

        # Also clean from candidate_info if present
        if 'candidate_info' in company and isinstance(company['candidate_info'], dict):
            if 'title' in company['candidate_info']:
                company['candidate_info']['title'] = clean_company_name(company['candidate_info']['title'])

    return companies


def backup_file(filepath: str):
    """Create a timestamped backup of a file"""
    if not os.path.exists(filepath):
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = filepath.replace('.json', f'_backup_{timestamp}.json')

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Backup created: {os.path.basename(backup_path)}")


def process_file(filepath: str, file_description: str):
    """Process a single JSON file - deduplicate and clean names"""
    if not os.path.exists(filepath):
        print(f"⚠️  {file_description} not found: {filepath}")
        return

    print(f"\n{'='*60}")
    print(f"Processing: {file_description}")
    print(f"{'='*60}")

    # Backup original
    print("Creating backup...")
    backup_file(filepath)

    # Load data
    with open(filepath, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    original_count = len(companies)
    print(f"Original count: {original_count} companies")

    # Clean names first
    print("Cleaning company names...")
    companies = clean_all_names(companies)

    # Count names that were cleaned
    cleaned_names = 0
    for company in companies:
        name = company.get('title') or company.get('company_name', '')
        if '**' in str(name) or '__' in str(name):
            cleaned_names += 1

    if cleaned_names > 0:
        print(f"  ✓ Cleaned {cleaned_names} company names with markdown formatting")

    # Deduplicate
    print("Deduplicating by URL...")
    companies = deduplicate_companies(companies)

    new_count = len(companies)
    duplicates_removed = original_count - new_count

    if duplicates_removed > 0:
        print(f"  ✓ Removed {duplicates_removed} duplicates")
    else:
        print(f"  ✓ No duplicates found")

    print(f"Final count: {new_count} companies")

    # Save cleaned data
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved cleaned data to {os.path.basename(filepath)}")

    return {
        'file': file_description,
        'original': original_count,
        'final': new_count,
        'removed': duplicates_removed
    }


def main():
    """Run deduplication on all stage files"""
    print("="*60)
    print("DEDUPLICATION & NAME CLEANING SCRIPT")
    print("="*60)
    print("\nThis script will:")
    print("1. Create backups of all files")
    print("2. Remove duplicate companies (by URL)")
    print("3. Clean company names (remove ** and other markdown)")
    print("4. Save cleaned versions")

    # Change to outputs directory
    outputs_dir = '../outputs'

    results = []

    # Process each stage file
    files_to_process = [
        ('stage_1.json', 'Stage 1: Discovery'),
        ('stage_2.json', 'Stage 2: Scraping'),
        ('stage_3.json', 'Stage 3: Enrichment'),
        ('FINAL_Investment_Intelligence.json', 'Final Report'),
    ]

    for filename, description in files_to_process:
        filepath = os.path.join(outputs_dir, filename)
        result = process_file(filepath, description)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")

    for result in results:
        print(f"{result['file']}:")
        print(f"  Original: {result['original']} companies")
        print(f"  Final: {result['final']} companies")
        print(f"  Removed: {result['removed']} duplicates")
        print()

    total_removed = sum(r['removed'] for r in results)
    print(f"Total duplicates removed: {total_removed}")

    print("\n✓ Deduplication complete!")
    print("\nBackup files created with timestamp in outputs directory.")
    print("If you need to restore, rename a backup file to the original name.")


if __name__ == '__main__':
    main()
