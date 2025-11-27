#!/usr/bin/env python3
"""
Real-time Progress Monitor
Run this in a separate terminal to watch the pipeline progress
"""
import os
import time
import csv
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def count_csv_rows(filename):
    """Count rows in CSV file"""
    try:
        with open(filename, 'r') as f:
            return sum(1 for line in f) - 1  # Subtract header
    except FileNotFoundError:
        return 0

def get_latest_festival(filename):
    """Get the most recent festival from CSV"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                latest = rows[-1]
                return latest.get('name', 'Unknown'), latest.get('sponsor_count', '0')
    except:
        pass
    return None, None

def monitor():
    """Monitor progress in real-time"""
    print("Starting progress monitor...")
    print("Press Ctrl+C to stop\n")

    last_festival_count = 0
    last_sponsor_count = 0
    start_time = datetime.now()

    while True:
        try:
            clear_screen()

            print("=" * 70)
            print("FESTIVAL RESEARCH PIPELINE - LIVE PROGRESS MONITOR")
            print("=" * 70)
            print()

            # Runtime
            runtime = datetime.now() - start_time
            print(f"Runtime: {runtime}")
            print()

            # Stage 1: Discovery
            print("STAGE 1: DISCOVERY")
            if os.path.exists('stage1_candidates.json'):
                import json
                with open('stage1_candidates.json', 'r') as f:
                    candidates = json.load(f)
                print(f"  ✅ Complete - {len(candidates)} candidates found")
            else:
                print(f"  ⏳ Running or not started...")
            print()

            # Stage 2: Scraping
            print("STAGE 2: WEB SCRAPING")
            if os.path.exists('stage2_scraped_data.json'):
                import json
                with open('stage2_scraped_data.json', 'r') as f:
                    scraped = json.load(f)
                print(f"  ✅ Complete - {len(scraped)} websites scraped")
            else:
                print(f"  ⏳ Running or not started...")
            print()

            # Stage 3: AI Extraction (in-progress monitoring)
            print("STAGE 3: AI EXTRACTION")

            # Check in-progress files first
            in_progress_festivals = count_csv_rows('stage3_festivals_in_progress.csv')
            in_progress_sponsors = count_csv_rows('stage3_sponsors_in_progress.csv')

            # Check final files
            final_festivals = count_csv_rows('stage3_festivals.csv')
            final_sponsors = count_csv_rows('stage3_sponsors.csv')

            current_festivals = max(in_progress_festivals, final_festivals)
            current_sponsors = max(in_progress_sponsors, final_sponsors)

            if final_festivals > 0:
                print(f"  ✅ Complete - {final_festivals} festivals, {final_sponsors} sponsors")
            elif in_progress_festivals > 0:
                print(f"  ⏳ Running - {in_progress_festivals} festivals extracted so far...")

                # Show latest festival
                latest_name, sponsor_count = get_latest_festival('stage3_festivals_in_progress.csv')
                if latest_name:
                    print(f"  📍 Latest: {latest_name} ({sponsor_count} sponsors)")

                # Show progress rate
                if current_festivals > last_festival_count:
                    print(f"  📊 New sponsors added: +{current_sponsors - last_sponsor_count}")
            else:
                print(f"  ⏳ Running or not started...")
            print()

            # Stage 4: Analysis
            print("STAGE 4: ANALYSIS & RANKING")
            top_prospects = count_csv_rows('stage4_top_sponsor_prospects.csv')
            if top_prospects > 0:
                print(f"  ✅ Complete - {top_prospects} sponsor prospects identified")
            else:
                print(f"  ⏳ Running or not started...")
            print()

            print("=" * 70)
            print("OUTPUT FILES:")
            print("-" * 70)

            files_to_check = [
                ('stage3_festivals_in_progress.csv', 'Festivals (in-progress)'),
                ('stage3_sponsors_in_progress.csv', 'Sponsors (in-progress)'),
                ('stage3_festivals.csv', 'Festivals (final)'),
                ('stage3_sponsors.csv', 'Sponsors (final)'),
                ('stage4_sponsor_frequency_matrix.csv', 'Sponsor frequency'),
                ('stage4_top_sponsor_prospects.csv', 'Top prospects'),
                ('stage4_comparison_table.csv', 'Festival comparison'),
            ]

            for filename, description in files_to_check:
                if os.path.exists(filename):
                    rows = count_csv_rows(filename)
                    size = os.path.getsize(filename) / 1024  # KB
                    print(f"  ✅ {description:30} {rows:4} rows ({size:.1f} KB)")

            print("=" * 70)
            print("\nRefreshing every 5 seconds... (Press Ctrl+C to stop)")

            # Update tracking variables
            last_festival_count = current_festivals
            last_sponsor_count = current_sponsors

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n\nMonitor stopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor()
