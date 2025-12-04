#!/usr/bin/env python3
"""
Reset Incomplete Entries from Stage 3 AND Stage 4
Identifies companies with "Unknown" or blank data and removes them from:
- stage_3.json (so Stage 3 can reprocess them)
- stage_3_progress.csv
- FINAL_Investment_Intelligence.json (so Stage 4 can reprocess them)
- FINAL_Investment_Intelligence.csv
"""
import os
import json
import csv
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


def backup_file(filepath):
    """Create timestamped backup of a file"""
    if not os.path.exists(filepath):
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.basename(filepath)
    backup_path = filepath.replace(filename, f'{filename.rsplit(".", 1)[0]}_backup_{timestamp}.{filename.rsplit(".", 1)[1]}')

    if filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif filepath.endswith('.csv'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return backup_path


def main():
    print("=" * 70)
    print("RESET INCOMPLETE ENTRIES FROM ALL STAGES")
    print("=" * 70)

    # Files to check and clean
    stage3_json = '../outputs/stage_3.json'
    stage3_csv = '../outputs/stage_3_progress.csv'
    stage4_json = '../outputs/FINAL_Investment_Intelligence.json'
    stage4_csv = '../outputs/FINAL_Investment_Intelligence.csv'

    if not os.path.exists(stage3_json):
        print(f"\n❌ Error: {stage3_json} not found.")
        return

    # Load Stage 3 data
    print(f"\n📁 Loading Stage 3 data...")
    with open(stage3_json, 'r', encoding='utf-8') as f:
        stage3_companies = json.load(f)

    print(f"   Loaded {len(stage3_companies)} companies from Stage 3")

    # Identify incomplete companies
    print(f"\n🔍 Analyzing companies for incomplete data...")

    complete_companies = []
    incomplete_companies = []
    incomplete_urls = set()

    for company in stage3_companies:
        if is_incomplete(company):
            incomplete_companies.append(company)
            incomplete_urls.add(company.get('url', ''))
        else:
            complete_companies.append(company)

    print(f"\n📊 Results:")
    print(f"   ✅ Complete companies: {len(complete_companies)}")
    print(f"   ⚠️  Incomplete companies: {len(incomplete_companies)}")

    if not incomplete_companies:
        print("\n🎉 All companies have complete data! Nothing to reset.")
        return

    # Show examples
    print(f"\n📋 Incomplete companies (first 20):")
    for i, company in enumerate(incomplete_companies[:20], 1):
        name = company.get('company_name', 'Unknown')

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
        print(f"     {i}. {name} - Missing: {missing_str}")

    if len(incomplete_companies) > 20:
        print(f"     ... and {len(incomplete_companies) - 20} more")

    # Create backups
    print(f"\n💾 Creating backups...")
    backups = []

    backup = backup_file(stage3_json)
    if backup:
        backups.append(os.path.basename(backup))
        print(f"   ✓ {os.path.basename(backup)}")

    if os.path.exists(stage3_csv):
        backup = backup_file(stage3_csv)
        if backup:
            backups.append(os.path.basename(backup))
            print(f"   ✓ {os.path.basename(backup)}")

    if os.path.exists(stage4_json):
        backup = backup_file(stage4_json)
        if backup:
            backups.append(os.path.basename(backup))
            print(f"   ✓ {os.path.basename(backup)}")

    if os.path.exists(stage4_csv):
        backup = backup_file(stage4_csv)
        if backup:
            backups.append(os.path.basename(backup))
            print(f"   ✓ {os.path.basename(backup)}")

    # Confirm
    print(f"\n⚠️  This will remove {len(incomplete_companies)} incomplete companies from:")
    print(f"   - Stage 3 JSON and CSV")
    if os.path.exists(stage4_json):
        print(f"   - Stage 4 final output (JSON and CSV)")
    print(f"\n   They will be reprocessed when you run stage_3.py and stage_4.py again.")

    response = input("\n❓ Continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Cancelled. No changes made.")
        return

    # Clean Stage 3 JSON
    print(f"\n💾 Cleaning Stage 3 JSON...")
    with open(stage3_json, 'w', encoding='utf-8') as f:
        json.dump(complete_companies, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved {len(complete_companies)} complete companies")

    # Clean Stage 3 CSV
    if os.path.exists(stage3_csv):
        print(f"\n💾 Cleaning Stage 3 CSV...")
        with open(stage3_csv, 'w', newline='', encoding='utf-8') as f:
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

    # Clean Stage 4 files
    if os.path.exists(stage4_json):
        print(f"\n💾 Cleaning Stage 4 JSON...")
        with open(stage4_json, 'r', encoding='utf-8') as f:
            stage4_companies = json.load(f)

        # Remove companies with URLs in incomplete list
        stage4_complete = [c for c in stage4_companies if c.get('url', '') not in incomplete_urls]
        removed_from_stage4 = len(stage4_companies) - len(stage4_complete)

        with open(stage4_json, 'w', encoding='utf-8') as f:
            json.dump(stage4_complete, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Removed {removed_from_stage4} incomplete companies")
        print(f"   ✓ Saved {len(stage4_complete)} complete companies")

    # Clean Stage 4 CSV
    if os.path.exists(stage4_csv):
        print(f"\n💾 Cleaning Stage 4 CSV...")

        # Read existing CSV to get fieldnames
        with open(stage4_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            stage4_csv_companies = list(reader)

        # Remove incomplete companies
        stage4_csv_complete = [c for c in stage4_csv_companies if c.get('url', '') not in incomplete_urls]
        removed_from_csv = len(stage4_csv_companies) - len(stage4_csv_complete)

        # Write updated CSV
        with open(stage4_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(stage4_csv_complete)
        print(f"   ✓ Removed {removed_from_csv} incomplete companies")
        print(f"   ✓ Saved {len(stage4_csv_complete)} complete companies")

    print("\n" + "=" * 70)
    print("RESET COMPLETE")
    print("=" * 70)
    print(f"\n✅ Removed {len(incomplete_companies)} incomplete companies from all stages")
    print(f"\n💡 Next steps:")
    print(f"   1. Make sure you have Perplexity credits")
    print(f"   2. Run: python stage_3.py")
    print(f"   3. Run: python stage_4.py")
    print(f"   4. Run: python stage_4b.py (optional - Colorado filter)")
    print(f"\n📁 Backups created:")
    for backup in backups:
        print(f"   - {backup}")


if __name__ == '__main__':
    main()
