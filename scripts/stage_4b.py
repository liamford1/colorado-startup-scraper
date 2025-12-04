#!/usr/bin/env python3
"""
Stage 4b: Colorado Filter for Final Output
Removes any non-Colorado companies from the final investment intelligence report
"""
import os
import json
import csv
from datetime import datetime
from typing import List, Dict


def backup_file(filepath: str) -> str:
    """Create a timestamped backup of a file"""
    if not os.path.exists(filepath):
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = filepath.replace('.json', f'_backup_{timestamp}.json').replace('.csv', f'_backup_{timestamp}.csv')

    # Copy file content
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

    print(f"  ✓ Backup created: {os.path.basename(backup_path)}")
    return backup_path


def is_colorado_company(company: Dict) -> bool:
    """Check if a company is based in Colorado"""
    # Check all location-related fields
    location_state = str(company.get('location_state', '')).strip().upper()
    location_city = str(company.get('location_city', '')).lower()
    location = str(company.get('location', '')).lower()
    headquarters = str(company.get('headquarters', '')).lower()

    # Check if Colorado/CO is mentioned in any field
    is_colorado = (
        location_state == 'CO' or
        'colorado' in location or
        'colorado' in headquarters or
        ', co' in location or
        location.endswith(' co')
    )

    return is_colorado


def filter_colorado_companies(companies: List[Dict]) -> tuple[List[Dict], List[str]]:
    """
    Filter to only keep companies headquartered in Colorado.
    Returns (colorado_companies, removed_company_names)
    """
    colorado_companies = []
    removed = []

    for company in companies:
        if is_colorado_company(company):
            colorado_companies.append(company)
        else:
            company_name = company.get('company_name', 'Unknown')
            location = company.get('location', company.get('location_city', 'Unknown'))
            removed.append(f"{company_name} ({location})")

    return colorado_companies, removed


def main():
    """Filter final output to Colorado companies only"""
    print("=" * 70)
    print("STAGE 4B: COLORADO FILTER FOR FINAL OUTPUT")
    print("=" * 70)

    # File paths
    json_file = '../outputs/FINAL_Investment_Intelligence.json'
    csv_file = '../outputs/FINAL_Investment_Intelligence.csv'

    # Check if files exist
    if not os.path.exists(json_file):
        print(f"\n❌ Error: {json_file} not found.")
        print("   Run stage_4.py first to generate the final output.")
        return

    print("\n📁 Loading final output files...")

    # Create backups
    print("\n💾 Creating backups...")
    backup_file(json_file)
    if os.path.exists(csv_file):
        backup_file(csv_file)

    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    original_count = len(companies)
    print(f"\n📊 Original count: {original_count} companies")

    # Filter to Colorado companies
    print("\n🔍 Filtering to Colorado companies only...")
    colorado_companies, removed = filter_colorado_companies(companies)

    final_count = len(colorado_companies)
    removed_count = original_count - final_count

    print(f"\n✅ Colorado companies: {final_count}")
    print(f"🗑️  Non-Colorado companies removed: {removed_count}")

    if removed:
        print(f"\n📋 Removed companies:")
        for i, name in enumerate(removed[:20], 1):  # Show first 20
            print(f"     {i}. {name}")
        if len(removed) > 20:
            print(f"     ... and {len(removed) - 20} more")

    # Save filtered JSON
    print(f"\n💾 Saving filtered results...")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(colorado_companies, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: {json_file}")

    # Save filtered CSV if it exists
    if os.path.exists(csv_file):
        # Read CSV to get fieldnames
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        # Write filtered data
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(colorado_companies)
        print(f"  ✓ Saved: {csv_file}")

    print("\n" + "=" * 70)
    print("COLORADO FILTERING COMPLETE")
    print("=" * 70)
    print(f"\n✅ Final output contains {final_count} Colorado companies")

    if removed_count == 0:
        print("✅ No non-Colorado companies found - all companies are already in Colorado!")
    else:
        print(f"✅ Removed {removed_count} non-Colorado companies")
        print("\n💡 Tip: Check the backup files if you need to restore the original data")

    # Show some stats
    if colorado_companies:
        print(f"\n📍 Colorado cities represented:")
        cities = set()
        for company in colorado_companies:
            city = company.get('location_city', '').strip()
            if city and city != 'Unknown':
                cities.add(city)

        city_list = sorted(cities)[:10]  # Show top 10 cities
        for city in city_list:
            count = sum(1 for c in colorado_companies if c.get('location_city', '') == city)
            print(f"     - {city}: {count} companies")

        if len(cities) > 10:
            print(f"     ... and {len(cities) - 10} more cities")


if __name__ == '__main__':
    main()
