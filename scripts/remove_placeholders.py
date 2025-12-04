#!/usr/bin/env python3
"""
Remove Placeholder Company Names
Removes entries like [Company 1], Company Name, etc. from stage_1.json
"""
import os
import json
import re
from datetime import datetime


def is_placeholder(title: str) -> bool:
    """Check if a company name is a placeholder"""
    if not title:
        return True

    title_lower = title.lower().strip()

    return (
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
        title_lower in ['startup', 'business', 'firm', 'corp', 'inc']
    )


def main():
    print("=" * 70)
    print("REMOVE PLACEHOLDER COMPANY NAMES")
    print("=" * 70)

    json_file = '../outputs/stage_1.json'

    if not os.path.exists(json_file):
        print(f"\n❌ Error: {json_file} not found.")
        return

    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'../outputs/stage_1_backup_{timestamp}.json'

    print(f"\n💾 Creating backup: {os.path.basename(backup_file)}")
    with open(json_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    print(f"   ✓ Backup created")

    # Filter out placeholders
    print(f"\n🔍 Analyzing {len(companies)} companies...")

    real_companies = []
    placeholders = []

    for company in companies:
        title = company.get('title', '')
        if is_placeholder(title):
            placeholders.append(title)
        else:
            real_companies.append(company)

    print(f"\n📊 Results:")
    print(f"   ✅ Real companies: {len(real_companies)}")
    print(f"   ⚠️  Placeholders: {len(placeholders)}")

    if not placeholders:
        print("\n🎉 No placeholders found! All companies have real names.")
        return

    # Show examples
    print(f"\n📋 Placeholder examples (first 20):")
    for i, placeholder in enumerate(placeholders[:20], 1):
        print(f"     {i}. '{placeholder}'")

    if len(placeholders) > 20:
        print(f"     ... and {len(placeholders) - 20} more")

    # Confirm
    response = input(f"\n❓ Remove {len(placeholders)} placeholders? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Cancelled. No changes made.")
        return

    # Save cleaned data
    print(f"\n💾 Saving {len(real_companies)} real companies...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(real_companies, f, indent=2, ensure_ascii=False)

    print("   ✓ Saved")

    # Also update CSV if it exists
    csv_file = '../outputs/stage_1_progress.csv'
    if os.path.exists(csv_file):
        import csv

        print(f"\n💾 Updating {os.path.basename(csv_file)}...")

        # Create CSV backup
        csv_backup = f'../outputs/stage_1_progress_backup_{timestamp}.csv'
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(csv_backup, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✓ Backup: {os.path.basename(csv_backup)}")

        # Write cleaned CSV
        if real_companies:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['title', 'url', 'found_count', 'priority', 'snippet', 'discovery_query']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(real_companies)
        print(f"   ✓ Updated")

    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"\n✅ Removed {len(placeholders)} placeholder companies")
    print(f"✅ Kept {len(real_companies)} real companies")
    print(f"\n📁 Backup: {os.path.basename(backup_file)}")


if __name__ == '__main__':
    main()
