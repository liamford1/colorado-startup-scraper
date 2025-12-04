#!/usr/bin/env python3
"""
Reset Incomplete Stage 3 Entries
Identifies companies with "Unknown" or blank data and removes them from stage_3.json
so they can be reprocessed when you run stage_3.py again.
"""
import os
import json
from datetime import datetime


def is_incomplete(company):
    """Check if a company has incomplete/missing data"""
    # Fields that shouldn't be Unknown or empty
    check_fields = ['founders', 'funding_info', 'location', 'headquarters', 'key_investors']

    unknown_count = 0
    for field in check_fields:
        value = str(company.get(field, '')).strip()
        if not value or value.lower() in ['unknown', 'n/a', 'none', 'not found']:
            unknown_count += 1

    # Consider incomplete if 3 or more fields are unknown/empty
    return unknown_count >= 3


def main():
    print("=" * 70)
    print("RESET INCOMPLETE STAGE 3 ENTRIES")
    print("=" * 70)

    json_file = '../outputs/stage_3.json'

    if not os.path.exists(json_file):
        print(f"\n❌ Error: {json_file} not found.")
        print("   Run stage_3.py first to create this file.")
        return

    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'../outputs/stage_3_backup_{timestamp}.json'

    print(f"\n💾 Creating backup: {os.path.basename(backup_file)}")
    with open(json_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    print(f"   ✓ Backup created")

    # Identify incomplete companies
    print(f"\n🔍 Analyzing {len(companies)} companies...")

    complete_companies = []
    incomplete_companies = []

    for company in companies:
        if is_incomplete(company):
            incomplete_companies.append(company)
        else:
            complete_companies.append(company)

    print(f"\n📊 Results:")
    print(f"   ✅ Complete companies: {len(complete_companies)}")
    print(f"   ⚠️  Incomplete companies: {len(incomplete_companies)}")

    if not incomplete_companies:
        print("\n🎉 All companies have complete data! Nothing to reset.")
        return

    # Show some examples of incomplete companies
    print(f"\n📋 Incomplete companies (will be reprocessed):")
    for i, company in enumerate(incomplete_companies[:20], 1):
        name = company.get('company_name', 'Unknown')
        url = company.get('url', 'Unknown')

        # Count missing fields
        missing = []
        if not company.get('founders') or str(company.get('founders')).lower() in ['unknown', 'n/a']:
            missing.append('founders')
        if not company.get('funding_info') or str(company.get('funding_info')).lower() in ['unknown', 'n/a']:
            missing.append('funding')
        if not company.get('location') or str(company.get('location')).lower() in ['unknown', 'n/a']:
            missing.append('location')
        if not company.get('headquarters') or str(company.get('headquarters')).lower() in ['unknown', 'n/a']:
            missing.append('HQ')
        if not company.get('key_investors') or str(company.get('key_investors')).lower() in ['unknown', 'n/a']:
            missing.append('investors')

        missing_str = ', '.join(missing) if missing else 'multiple fields'
        print(f"     {i}. {name}")
        print(f"        Missing: {missing_str}")

    if len(incomplete_companies) > 20:
        print(f"     ... and {len(incomplete_companies) - 20} more")

    # Ask for confirmation
    print(f"\n⚠️  These {len(incomplete_companies)} companies will be REMOVED from stage_3.json")
    print("   and will be reprocessed when you run stage_3.py again.")
    print(f"\n   Backup saved to: {os.path.basename(backup_file)}")

    response = input("\n❓ Continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Cancelled. No changes made.")
        return

    # Save only complete companies
    print(f"\n💾 Saving {len(complete_companies)} complete companies to {json_file}...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(complete_companies, f, indent=2, ensure_ascii=False)

    print("   ✓ Saved")

    # Also update the progress CSV to match
    import csv
    csv_file = '../outputs/stage_3_progress.csv'
    if os.path.exists(csv_file):
        print(f"\n💾 Updating {os.path.basename(csv_file)}...")

        # Create CSV backup
        csv_backup = f'../outputs/stage_3_progress_backup_{timestamp}.csv'
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(csv_backup, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✓ Backup: {os.path.basename(csv_backup)}")

        # Write updated CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if complete_companies:
                fieldnames = [
                    'company_name', 'url', 'description', 'founders',
                    'funding_info', 'latest_funding_date', 'total_funding', 'key_investors',
                    'location', 'headquarters', 'social_links', 'success'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(complete_companies)
        print(f"   ✓ Updated")

    print("\n" + "=" * 70)
    print("RESET COMPLETE")
    print("=" * 70)
    print(f"\n✅ Removed {len(incomplete_companies)} incomplete companies")
    print(f"✅ Kept {len(complete_companies)} complete companies")
    print(f"\n💡 Next steps:")
    print(f"   1. Make sure you have Perplexity credits")
    print(f"   2. Run: python stage_3.py")
    print(f"   3. The {len(incomplete_companies)} incomplete companies will be reprocessed")
    print(f"\n📁 Backups created:")
    print(f"   - {os.path.basename(backup_file)}")
    if os.path.exists(csv_file):
        print(f"   - {os.path.basename(csv_backup)}")


if __name__ == '__main__':
    main()
