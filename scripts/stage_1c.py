"""
Stage 1c: Sort Results Alphabetically
Sorts stage_1.json and stage_1_progress.csv by company name
"""
import json
import csv
import os
from typing import List, Dict


def sort_json_by_company_name(json_file: str) -> int:
    """Sort JSON file alphabetically by company name"""
    if not os.path.exists(json_file):
        print(f"⚠️  File not found: {json_file}")
        return 0

    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    # Sort by title field (company name), case-insensitive
    companies.sort(key=lambda x: (x.get('title', '') or '').lower())

    # Save sorted JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    return len(companies)


def sort_csv_by_company_name(csv_file: str) -> int:
    """Sort CSV file alphabetically by company name"""
    if not os.path.exists(csv_file):
        print(f"⚠️  File not found: {csv_file}")
        return 0

    # Load CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not rows:
        return 0

    # Sort by company_name field, case-insensitive
    rows.sort(key=lambda x: (x.get('company_name', '') or '').lower())

    # Save sorted CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main():
    """Sort Stage 1 output files alphabetically"""
    print("=" * 60)
    print("STAGE 1C: ALPHABETICAL SORTING")
    print("=" * 60)

    outputs_dir = '../outputs'

    # Sort JSON file
    json_file = os.path.join(outputs_dir, 'stage_1.json')
    print(f"\n📄 Sorting {os.path.basename(json_file)}...")
    json_count = sort_json_by_company_name(json_file)
    if json_count > 0:
        print(f"  ✓ Sorted {json_count} companies alphabetically")

    # Sort CSV file
    csv_file = os.path.join(outputs_dir, 'stage_1_progress.csv')
    print(f"\n📄 Sorting {os.path.basename(csv_file)}...")
    csv_count = sort_csv_by_company_name(csv_file)
    if csv_count > 0:
        print(f"  ✓ Sorted {csv_count} companies alphabetically")

    print(f"\n{'=' * 60}")
    print("SORTING COMPLETE")
    print("=" * 60)
    print(f"✓ Both files sorted alphabetically by company name")

    # Show first 10 companies as verification
    if json_count > 0:
        with open(json_file, 'r', encoding='utf-8') as f:
            companies = json.load(f)

        print(f"\n📋 First 10 companies (alphabetically):")
        for i, company in enumerate(companies[:10], 1):
            name = company.get('title', 'Unknown')
            url = company.get('url', 'N/A')
            url_display = 'URL_NEEDED' if url == 'URL_NEEDED' else '✓'
            print(f"  {i:2d}. {name} [{url_display}]")

        if json_count > 10:
            print(f"  ... and {json_count - 10} more")


if __name__ == '__main__':
    main()
