#!/usr/bin/env python3
"""
Quick Results Viewer
View current pipeline results without opening CSV files
"""
import os
import csv
import json
from typing import Optional

def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def view_festivals():
    """View extracted festivals"""
    filename = 'stage3_festivals.csv'
    if not os.path.exists(filename):
        filename = 'stage3_festivals_in_progress.csv'

    if not os.path.exists(filename):
        print("No festival data found yet.")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        festivals = list(reader)

    print_header(f"FESTIVALS ({len(festivals)} total)")

    # Sort by fit score
    festivals.sort(key=lambda x: int(x.get('fit_score', 0)), reverse=True)

    print(f"\n{'Rank':<6}{'Festival':<35}{'City':<20}{'Score':<8}{'Sponsors':<10}")
    print("-" * 80)

    for i, fest in enumerate(festivals[:20], 1):  # Top 20
        name = fest.get('name', 'Unknown')[:33]
        city = f"{fest.get('city', '')}, {fest.get('state', '')}"[:18]
        score = fest.get('fit_score', '0')
        sponsors = fest.get('sponsor_count', '0')

        print(f"{i:<6}{name:<35}{city:<20}{score:<8}{sponsors:<10}")

    if len(festivals) > 20:
        print(f"\n... and {len(festivals) - 20} more festivals")

def view_sponsors():
    """View sponsor frequency"""
    filename = 'stage4_sponsor_frequency_matrix.csv'

    if not os.path.exists(filename):
        print("\nNo sponsor analysis found yet. (Run Stage 4)")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sponsors = list(reader)

    print_header(f"TOP SPONSOR PROSPECTS ({len(sponsors)} unique sponsors)")

    # Already sorted by frequency in the file
    print(f"\n{'Sponsor':<40}{'Freq':<8}{'Tier':<15}{'Priority':<10}")
    print("-" * 80)

    for sponsor in sponsors[:25]:  # Top 25
        name = sponsor.get('Sponsor Name', 'Unknown')[:38]
        freq = sponsor.get('Frequency', '0')
        tier = sponsor.get('Typical Tier', 'Unknown')[:13]
        priority = sponsor.get('Priority', '-')

        print(f"{name:<40}{freq:<8}{tier:<15}{priority:<10}")

    if len(sponsors) > 25:
        print(f"\n... and {len(sponsors) - 25} more sponsors")

def view_top_prospects():
    """View top sponsor prospects for outreach"""
    filename = 'stage4_top_sponsor_prospects.csv'

    if not os.path.exists(filename):
        print("\nNo prospect analysis found yet. (Run Stage 4)")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        prospects = list(reader)

    print_header(f"PRIORITIZED OUTREACH LIST ({len(prospects)} high-priority prospects)")

    print("\nThese sponsors appear in 2+ festivals and are highest priority:\n")
    print(f"{'Sponsor':<40}{'Freq':<8}{'Priority':<12}{'Festivals':<30}")
    print("-" * 100)

    for prospect in prospects[:15]:  # Top 15
        name = prospect.get('sponsor_name', 'Unknown')[:38]
        freq = prospect.get('frequency', '0')
        priority = prospect.get('priority_score', '0')
        festivals = prospect.get('festivals', '')

        # Truncate festival list
        fest_list = festivals.split(', ')
        if len(fest_list) > 2:
            fest_str = ', '.join(fest_list[:2]) + f' +{len(fest_list)-2} more'
        else:
            fest_str = festivals

        fest_str = fest_str[:28]

        print(f"{name:<40}{freq:<8}{priority:<12}{fest_str:<30}")

    if len(prospects) > 15:
        print(f"\n... and {len(prospects) - 15} more prospects")

def view_summary():
    """View overall summary"""
    print_header("PIPELINE SUMMARY")

    # Check which stages are complete
    stages = {
        'Stage 1: Discovery': 'stage1_candidates.json',
        'Stage 2: Scraping': 'stage2_scraped_data.json',
        'Stage 3: Extraction': 'stage3_festivals.csv',
        'Stage 4: Analysis': 'stage4_top_sponsor_prospects.csv'
    }

    print("\nStage Status:")
    for stage_name, filename in stages.items():
        status = "✅ Complete" if os.path.exists(filename) else "⏳ Pending"
        print(f"  {stage_name:<25} {status}")

    # Count results
    print("\nResults:")

    if os.path.exists('stage3_festivals.csv'):
        with open('stage3_festivals.csv', 'r') as f:
            festival_count = sum(1 for line in f) - 1
        print(f"  Festivals analyzed:       {festival_count}")

    if os.path.exists('stage3_sponsors.csv'):
        with open('stage3_sponsors.csv', 'r') as f:
            sponsor_count = sum(1 for line in f) - 1
        print(f"  Sponsor relationships:    {sponsor_count}")

    if os.path.exists('stage4_sponsor_frequency_matrix.csv'):
        with open('stage4_sponsor_frequency_matrix.csv', 'r') as f:
            unique_sponsors = sum(1 for line in f) - 1
        print(f"  Unique sponsors:          {unique_sponsors}")

    if os.path.exists('stage4_top_sponsor_prospects.csv'):
        with open('stage4_top_sponsor_prospects.csv', 'r') as f:
            prospects = sum(1 for line in f) - 1
        print(f"  High-priority prospects:  {prospects}")

    print("\nOutput Files:")
    output_files = [
        'stage4_top_sponsor_prospects.csv',
        'stage4_sponsor_frequency_matrix.csv',
        'stage4_comparison_table.csv',
        'stage4_top_10_report.txt',
        'stage3_festivals.csv',
        'stage3_sponsors.csv'
    ]

    for filename in output_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024
            print(f"  ✅ {filename:<40} ({size:.1f} KB)")

def main():
    """Main viewer"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'festivals':
            view_festivals()
        elif command == 'sponsors':
            view_sponsors()
        elif command == 'prospects':
            view_top_prospects()
        elif command == 'summary':
            view_summary()
        else:
            print("Usage: python view_results.py [festivals|sponsors|prospects|summary]")
    else:
        # Show everything
        view_summary()
        view_festivals()
        view_sponsors()
        view_top_prospects()

    print("\n")

if __name__ == '__main__':
    main()
