#!/usr/bin/env python3
"""
Main Pipeline Orchestrator
Runs the complete Stage 1 pipeline: Discovery → Deduplication → URL Finding → Sorting
"""
import sys
import os
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


def main():
    """Run the complete Stage 1 pipeline"""
    start_time = datetime.now()

    print("\n" + "=" * 70)
    print("  STAGE 1 PIPELINE ORCHESTRATOR")
    print("  Pipeline: Stage 1 → Deduplicate → Stage 1b → Stage 1c")
    print("=" * 70)

    # Track success
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
        print(f"✅ Stage 1 data ready at: ../outputs/stage_1.json")
        print("\nNext step: Run stage_2.py to scrape company websites")
    else:
        print("\n❌ Pipeline incomplete - see errors above")
        print(f"⏱️  Time elapsed: {duration.total_seconds():.1f} seconds")

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
