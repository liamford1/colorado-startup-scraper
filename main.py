#!/usr/bin/env python3
"""
Investment Research Automation Pipeline
Main orchestration script to run all stages
"""
import sys
import os
from datetime import datetime
import argparse

# Add parent directory to path for .env loading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from stage1_discovery import main as stage1_main
from stage2_scraper import main as stage2_main
from stage3_enrichment import main as stage3_main
from stage4_openai_extract import main as stage4_main


def print_banner(text: str):
    """Print a nice banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_full_pipeline():
    """Run all stages of the pipeline"""
    start_time = datetime.now()

    print_banner("INVESTMENT RESEARCH AUTOMATION PIPELINE")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Stage 1: Discovery
        print_banner("STAGE 1: COMPANY DISCOVERY")
        print("Finding candidate companies using Perplexity API...\n")
        candidates = stage1_main()

        if not candidates:
            print("❌ No candidates found. Exiting.")
            return

        print(f"\n✅ Stage 1 complete: {len(candidates)} candidates found")
        input("\nPress Enter to continue to Stage 2...")

        # Stage 2: Scraping
        print_banner("STAGE 2: WEB SCRAPING")
        print("Scraping company websites for content...\n")
        scraped_data = stage2_main()

        if not scraped_data:
            print("❌ No data scraped. Exiting.")
            return

        print(f"\n✅ Stage 2 complete: {len(scraped_data)} websites scraped")
        input("\nPress Enter to continue to Stage 3...")

        # Stage 3: Enrichment
        print_banner("STAGE 3: DATA ENRICHMENT")
        print("Filling missing data using external sources...\n")
        companies = stage3_main()

        if not companies:
            print("❌ No companies extracted. Exiting.")
            return

        print(f"\n✅ Stage 3 complete: {len(companies)} companies extracted")
        input("\nPress Enter to continue to Stage 4...")

        # Stage 4: OpenAI Extraction
        print_banner("STAGE 4: OPENAI INTELLIGENCE EXTRACTION")
        print("Extracting investment intelligence with OpenAI...\n")
        stage4_main()

        print(f"\n✅ Stage 4 complete: Final report ready")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time

    print_banner("PIPELINE COMPLETE!")
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print("\nOutput Files Generated:")
    print("  • outputs/stage1_candidates.json")
    print("  • outputs/stage2_scraped_data.json")
    print("  • outputs/stage3_enriched.json")
    print("  • outputs/FINAL_Investment_Intelligence.csv")
    print("  • outputs/FINAL_Investment_Intelligence.json")
    print("\n✅ All deliverables ready for review!")


def run_single_stage(stage: int):
    """Run a single stage of the pipeline"""
    stages = {
        1: ("Company Discovery", stage1_main),
        2: ("Web Scraping", stage2_main),
        3: ("AI Data Extraction", stage3_main),
        4: ("Analysis & Ranking", stage4_main)
    }

    if stage not in stages:
        print(f"❌ Invalid stage number: {stage}")
        print("Valid stages: 1, 2, 3, 4")
        return

    stage_name, stage_func = stages[stage]

    print_banner(f"STAGE {stage}: {stage_name.upper()}")

    try:
        stage_func()
        print(f"\n✅ Stage {stage} complete!")
    except Exception as e:
        print(f"\n❌ Stage {stage} failed with error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Investment Research Automation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --full              Run complete pipeline (all stages)
  python main.py --stage 1           Run only Stage 1 (Discovery)
  python main.py --stage 2           Run only Stage 2 (Scraping)
  python main.py --stage 3           Run only Stage 3 (AI Extraction)
  python main.py --stage 4           Run only Stage 4 (Analysis)

Stages:
  1. Discovery     - Find candidate companies using Perplexity API
  2. Scraping      - Scrape company websites for content
  3. Enrichment    - Enrich company data with external sources
  4. OpenAI Extract - Extract investment intelligence with OpenAI
        """
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Run the complete pipeline (all stages)'
    )

    parser.add_argument(
        '--stage',
        type=int,
        choices=[1, 2, 3, 4],
        help='Run a specific stage (1-4)'
    )

    args = parser.parse_args()

    if args.full:
        run_full_pipeline()
    elif args.stage:
        run_single_stage(args.stage)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
