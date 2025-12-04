#!/usr/bin/env python3
"""
Main Pipeline Orchestrator
Runs the complete investment intelligence pipeline
"""
import sys
import os
import argparse
from datetime import datetime

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_stage_1():
    """Run Stage 1: Company Discovery"""
    print_header("STEP 1: COMPANY DISCOVERY (Stage 1)")
    try:
        import stage_1
        stage_1.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 1: {e}")
        return False


def run_deduplicate():
    """Run Deduplication (Stage 1 only)"""
    print_header("STEP 2: DEDUPLICATION")
    try:
        import json
        from deduplicate import deduplicate_companies, clean_all_names, backup_file

        filepath = '../outputs/stage_1.json'

        if not os.path.exists(filepath):
            print(f"⚠️  {filepath} not found. Skipping deduplication.")
            return True

        print("Creating backup...")
        backup_file(filepath)

        # Load data
        with open(filepath, 'r', encoding='utf-8') as f:
            companies = json.load(f)

        original_count = len(companies)
        print(f"Original count: {original_count} companies")

        # Clean names
        print("Cleaning company names...")
        companies = clean_all_names(companies)

        # Count URLs before deduplication
        url_needed_before = sum(1 for c in companies if c.get('url') == 'URL_NEEDED')
        real_urls_before = sum(1 for c in companies if c.get('url') and c.get('url') != 'URL_NEEDED')
        print(f"  Before: {real_urls_before} with URLs, {url_needed_before} with URL_NEEDED")

        # Deduplicate
        print("Deduplicating by URL and company name...")
        companies = deduplicate_companies(companies)

        new_count = len(companies)
        duplicates_removed = original_count - new_count

        # Count URLs after deduplication
        url_needed_after = sum(1 for c in companies if c.get('url') == 'URL_NEEDED')
        real_urls_after = sum(1 for c in companies if c.get('url') and c.get('url') != 'URL_NEEDED')
        print(f"  After: {real_urls_after} with URLs, {url_needed_after} with URL_NEEDED")

        if duplicates_removed > 0:
            url_needed_removed = url_needed_before - url_needed_after
            print(f"  ✓ Removed {duplicates_removed} duplicates")
            if url_needed_removed > 0:
                print(f"    ({url_needed_removed} were URL_NEEDED duplicates)")
        else:
            print(f"  ✓ No duplicates found")

        print(f"Final count: {new_count} companies")

        # Save cleaned data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved deduplicated data")
        return True

    except Exception as e:
        print(f"❌ Error in deduplication: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_stage_1b():
    """Run Stage 1b: URL Discovery"""
    print_header("STEP 3: URL DISCOVERY (Stage 1b)")
    try:
        import stage_1b
        stage_1b.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 1b: {e}")
        return False


def run_stage_1c():
    """Run Stage 1c: Alphabetical Sorting"""
    print_header("STEP 4: ALPHABETICAL SORTING (Stage 1c)")
    try:
        import stage_1c
        stage_1c.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 1c: {e}")
        return False


def run_stage_2():
    """Run Stage 2: Website Scraping"""
    print_header("STEP 5: WEBSITE SCRAPING (Stage 2)")
    try:
        import stage_2
        stage_2.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 2: {e}")
        return False


def run_stage_3():
    """Run Stage 3: Data Enrichment & Colorado Filter"""
    print_header("STEP 6: DATA ENRICHMENT & COLORADO FILTER (Stage 3)")
    try:
        import stage_3
        stage_3.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 3: {e}")
        return False


def run_stage_4():
    """Run Stage 4: Investment Intelligence Extraction"""
    print_header("STEP 7: INVESTMENT INTELLIGENCE EXTRACTION (Stage 4)")
    try:
        import stage_4
        stage_4.process_all_companies(
            '../outputs/stage_3.json',
            '../outputs/FINAL_Investment_Intelligence.csv',
            test_mode=False
        )
        return True
    except Exception as e:
        print(f"❌ Error in Stage 4: {e}")
        return False


def run_stage_4b():
    """Run Stage 4b: Colorado Filter for Final Output"""
    print_header("STEP 8: COLORADO FILTER (Stage 4b)")
    try:
        import stage_4b
        stage_4b.main()
        return True
    except Exception as e:
        print(f"❌ Error in Stage 4b: {e}")
        return False


def main():
    """Run the pipeline"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Colorado Startup Investment Intelligence Pipeline"
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run the complete pipeline (Stage 1 through Stage 4b)'
    )
    parser.add_argument(
        '--stage1-only',
        action='store_true',
        help='Run only Stage 1 pipeline (Discovery → Dedup → URL Finding → Sorting)'
    )
    args = parser.parse_args()

    start_time = datetime.now()

    # Determine which pipeline to run
    if args.full:
        print("\n" + "=" * 70)
        print("  COMPLETE PIPELINE ORCHESTRATOR")
        print("  Running ALL stages: 1 → Dedup → 1b → 1c → 2 → 3 → 4 → 4b")
        print("=" * 70)

        steps = [
            ("Stage 1 (Discovery)", run_stage_1),
            ("Deduplication", run_deduplicate),
            ("Stage 1b (URL Finding)", run_stage_1b),
            ("Stage 1c (Sorting)", run_stage_1c),
            ("Stage 2 (Website Scraping)", run_stage_2),
            ("Stage 3 (Data Enrichment & CO Filter)", run_stage_3),
            ("Stage 4 (Investment Intelligence)", run_stage_4),
            ("Stage 4b (Colorado Filter)", run_stage_4b)
        ]
    else:
        # Default: Stage 1 pipeline only
        print("\n" + "=" * 70)
        print("  STAGE 1 PIPELINE ORCHESTRATOR")
        print("  Pipeline: Stage 1 → Deduplicate → Stage 1b → Stage 1c")
        print("=" * 70)

        steps = [
            ("Stage 1 (Discovery)", run_stage_1),
            ("Deduplication", run_deduplicate),
            ("Stage 1b (URL Finding)", run_stage_1b),
            ("Stage 1c (Sorting)", run_stage_1c)
        ]

    results = []

    for step_name, step_func in steps:
        success = step_func()
        results.append((step_name, success))

        if not success:
            print(f"\n⚠️  Pipeline stopped at: {step_name}")
            print("Fix the error and run again to continue.")
            break

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print_header("PIPELINE SUMMARY")

    for step_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {step_name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n✅ PIPELINE COMPLETE!")
        print(f"✅ Total time: {duration.total_seconds():.1f} seconds")

        if args.full:
            print(f"✅ Final output ready at: ../outputs/FINAL_Investment_Intelligence.csv")
            print(f"   (Colorado companies only, sorted alphabetically)")
        else:
            print(f"✅ Stage 1 data ready at: ../outputs/stage_1.json")
            print("\nNext steps:")
            print("  - Run 'python main.py --full' to run the complete pipeline")
            print("  - Or run stage_2.py, stage_3.py, stage_4.py, stage_4b.py individually")
    else:
        print("\n❌ Pipeline incomplete - see errors above")
        print(f"⏱️  Time elapsed: {duration.total_seconds():.1f} seconds")

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
