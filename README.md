# Colorado Startup & Investor Research Pipeline (Endeavor Criteria)

An automated system to discover, analyze, and rank Colorado startups and their investors based on Endeavor Colorado's selection criteria.

## Overview

This pipeline automates the research of Colorado startups, founders, and investors through multiple stages:

### Stage 1 Pipeline (Discovery & Preparation)
1. **Stage 1** - Uses Perplexity API to find Colorado startups, VCs, and portfolio companies
2. **Deduplication** - Removes duplicates and cleans company names
3. **Stage 1b** - Finds URLs for companies missing website addresses
4. **Stage 1c** - Sorts results alphabetically

### Main Pipeline (Data Collection & Analysis)
5. **Stage 2** - Scrapes website content, investor pages, and funding announcements
6. **Stage 3** - Uses AI to enrich data and filters to Colorado-only companies
7. **Stage 4** - Extracts comprehensive investment intelligence and business metrics

## Endeavor Colorado Criteria

The pipeline specifically looks for companies that match these criteria:

### Core Requirements
- **Funded in last 5 years** (2019-2024)
- **DeepTech focused** - AI, robotics, biotech, cleantech, hardware technologies
- **Founder based in Colorado** (critical requirement)
- **HQ in Colorado** (strongly preferred)
- **Seed to Series D** funding stage
- **Privately held** (not publicly traded)
- **Founded since 2020 ideally** (rapid growth focused)
- **Company still active/running**

### Key Data Points Extracted
- **Company name**
- **Founder names** (with Colorado location verification)
- **CEO name** and contact info
- **All investors** (VCs, angels, funding rounds)
- Business model, stage, industry
- Traction metrics and growth indicators

## Data Sources

The pipeline searches and scrapes:

1. **Colorado Startups Leaderboard** - Top 100 and fastest growing companies at coloradostartups.org
2. **Endeavor Colorado Portfolio** - Current companies at endeavorcolorado.org
3. **Colorado VCs and Portfolios** - Major Colorado venture capital firms:
   - Foundry Group
   - Access Venture Partners
   - Boulder Ventures
   - Techstars Boulder
   - Ridgeline Ventures
   - Blackhorn Ventures
4. **News & Press Releases** - Funding announcements, company profiles

## Requirements

### API Keys Required
All API keys should be in `/Users/liamford/Documents/caruso/.env`:

```bash
OPENAI_API_KEY=your_openai_key          # For AI extraction
PERPLEXITY_API_KEY=your_perplexity_key  # For company discovery/search
```

### Installation

```bash
cd /Users/liamford/Documents/caruso/investments

# Install dependencies
pip install -r requirements.txt

# Make main script executable
chmod +x main.py
```

## Usage

### Option 1: Run Stage 1 Pipeline (Discovery & Preparation)

```bash
cd scripts
python main.py
```

This runs the complete Stage 1 pipeline:
- Stage 1 (Discovery)
- Deduplication
- Stage 1b (URL Finding)
- Stage 1c (Alphabetical Sorting)

**Estimated time:** 10-20 minutes
**Cost estimate:** ~$2-5 in Perplexity API calls

### Option 2: Run Individual Stages

```bash
cd scripts

# Stage 1 Pipeline (automated)
python main.py

# Stage 2: Website Scraping
python stage_2.py

# Stage 3: Data Enrichment & Colorado Filter
python stage_3.py

# Stage 4: Investment Intelligence Extraction
python stage_4.py

# Or run specific Stage 1 components individually:
python stage_1.py      # Discovery only
python deduplicate.py  # Deduplication only
python stage_1b.py     # URL finding only
python stage_1c.py     # Sorting only
```

## Output Files

All output files are saved to the `outputs/` directory.

### Stage 1 Pipeline Output
- `stage_1.json` - Discovered companies (deduplicated and sorted)
- `stage_1_progress.csv` - Progress tracking for Stage 1

### Stage 2 Output
- `stage_2.json` - Scraped website content, investor pages, news articles
- `stage_2_progress.csv` - Progress tracking for Stage 2

### Stage 3 Output
- `stage_3.json` - Enriched data filtered to Colorado companies only
- `stage_3_progress.csv` - Progress tracking for Stage 3

### Stage 4 Output (FINAL DELIVERABLE)
- **`FINAL_Investment_Intelligence.csv`** - Complete investment intelligence report
- **`FINAL_Investment_Intelligence.json`** - JSON version for programmatic access

Stage 4 extracts comprehensive data including:
- Company details (name, URL, description)
- Location (city, state, headquarters)
- Funding details (total funding, rounds, amounts, dates)
- Investor information (lead investors, tier-1 VCs, Colorado investors)
- Business intelligence (industry, business model, company stage, technology focus)
- Social links (LinkedIn, Crunchbase)

## Key Features

### 1. Automated Stage 1 Pipeline
- Runs discovery, deduplication, URL finding, and sorting automatically
- Creates timestamped backups before deduplication
- Skips already-processed companies to save API costs

### 2. Incremental Processing
- All stages check for existing data and only process NEW companies
- Safe to stop and resume at any time
- Progress saved after each company

### 3. Comprehensive Data Extraction
- Extracts founders, funding rounds, and investor details
- Identifies tier-1 VCs (Sequoia, a16z, Accel, etc.)
- Tracks Colorado investors (Foundry Group, Access Venture, etc.)
- Normalizes funding amounts ($45M, $1.2B format)

### 4. Colorado Focus
- Stage 3 filters to only keep Colorado-headquartered companies
- Tracks Colorado connection strength (High/Medium/Low)
- Identifies companies with Colorado investors

## Customization

### Adjust Search Queries
All search queries are defined in `queries.py`. Edit this file to customize discovery:

```python
# In queries.py
CUSTOM_QUERIES = [
    "Find DeepTech startups in Colorado with venture capital funding founded since 2020",
    # Add your own queries here
]
```

Then in `config.py`:
```python
from queries import CUSTOM_QUERIES
CUSTOM_SEARCH_QUERIES = CUSTOM_QUERIES
```

### Adjust Processing Limits
Edit `config.py` to change how many companies to process:

```python
MAX_FESTIVALS_TO_SCRAPE = None  # Process all companies
# or
MAX_FESTIVALS_TO_SCRAPE = 50    # Process only first 50
```

## Monitoring & Progress

### Real-Time Monitoring

In one terminal, run stages:
```bash
cd scripts
python main.py          # Stage 1 pipeline
python stage_2.py       # Stage 2
python stage_3.py       # Stage 3
python stage_4.py       # Stage 4
```

In a **second terminal**, run the live monitor:
```bash
cd scripts
python monitor_progress.py
```

This shows:
- ✅ Which stages are complete
- ⏳ Current progress of running stages
- 📊 Number of companies extracted so far
- 📍 Most recently processed company

### View Results Anytime

```bash
cd scripts
python view_results.py
```

This displays progress and results from all completed stages.

## Example Output

The final CSV (`FINAL_Investment_Intelligence.csv`) includes columns like:

```
company_name, url, description, founders
location_city, location_state, headquarters
total_funding_normalized, num_funding_rounds, funding_stage_progression
latest_round, latest_round_amount, latest_round_date
years_since_last_funding
total_investor_count, lead_investors, all_investors
notable_tier1_investors, has_colorado_investors
industry_categories, business_model, company_stage
technology_focus, target_market, colorado_connection
linkedin_url, crunchbase_url
```

### Sample Company Entry
```
Company: BrightWave AI
Location: Boulder, CO
Founded: 2021
Founders: Jane Smith, John Doe
Total Funding: $45M
Latest Round: Series B ($25M, 2024)
Lead Investors: Foundry Group, Access Venture Partners
Tier-1 VCs: a16z, Sequoia Capital
Industry: AI, Enterprise Software
Business Model: B2B SaaS
Company Stage: Growth
Colorado Connection: High
```

## Tips for Best Results

### Before Running
1. **Review search queries** in `queries.py` to ensure they target your criteria
2. **Check API quotas** - Perplexity and OpenAI have usage limits
3. **Set processing limits** - Start with 10-20 companies to test before processing all

### During Execution
1. **Monitor Stage 1 results** - Check `stage_1.json` to see discovered companies
2. **Review deduplication** - Backup files are created automatically before deduplication
3. **Check URL finding** - Stage 1b will report how many URLs were found
4. **Monitor Stage 2 progress** - Some websites may fail to scrape (normal)
5. **Review Stage 3 filtering** - Companies outside Colorado are removed

### After Completion
1. **Review `FINAL_Investment_Intelligence.csv`** - Final investment intelligence report
2. **Check Colorado companies** - All should be headquartered in Colorado
3. **Verify tier-1 VCs** - Notable investors like Sequoia, a16z, etc.
4. **Identify Colorado investors** - Focus on Foundry Group, Access Venture, etc.

## Troubleshooting

### "No candidates found"
- Check Perplexity API key in `.env`
- Verify Perplexity API quota isn't exceeded
- Review search queries in `queries.py`

### "Scraping failed" errors
- Some websites block scrapers - this is normal
- The pipeline continues with successful scrapes
- Check `stage_2_progress.csv` to see which sites worked

### URL_NEEDED entries remain
- Stage 1b couldn't find URLs for some companies
- These are skipped in Stage 2 (scraping)
- Can manually add URLs to `stage_1.json` and re-run Stage 2

### Not enough Colorado companies
- Stage 3 filters to Colorado only - some companies will be removed
- Add more Colorado-specific queries in `queries.py`
- Search for specific Colorado VCs and their portfolios

### Duplicate companies appearing
- Run `python deduplicate.py` to clean up all stage files
- Deduplication is automatic in Stage 1 pipeline but can be re-run anytime

## Cost & Time Estimates

### For 50 Companies

**Perplexity API:**
- Stage 1: ~119 queries (one per search query)
- Stage 1b: ~1 query per company missing URL
- Stage 3: ~2-3 queries per company (for missing data)
- **Estimated: 150-200 queries total**
- Check [Perplexity pricing](https://www.perplexity.ai/pricing) for current rates

**OpenAI API:**
- Stage 3: ~$0.05-0.10 per company (gpt-4o-mini)
- Stage 4: ~$0.10-0.30 per company (gpt-4o-mini)
- **Estimated: $7-20 total for 50 companies**

**Time:**
- Stage 1 Pipeline: ~10-20 minutes (discovery + dedup + URL finding + sorting)
- Stage 2: ~30-60 minutes (web scraping with rate limiting)
- Stage 3: ~30-60 minutes (enrichment + AI extraction + Colorado filter)
- Stage 4: ~10-15 minutes (intelligence extraction)

**Total: 1.5-3 hours for 50 companies**

## Next Steps After Pipeline Completes

1. **Open Final Report**
   - Review `FINAL_Investment_Intelligence.csv` in Excel/Google Sheets
   - Sort by funding amount, investor quality, or company stage
   - Filter for specific industries or funding stages

2. **Analyze Key Metrics**
   - Identify companies with tier-1 VC backing
   - Find companies with Colorado investors
   - Look for recent funding rounds (2023-2025)

3. **Validate Data**
   - Spot-check top companies against their websites
   - Verify founder names and locations
   - Cross-reference funding info with Crunchbase/LinkedIn

4. **Create Outreach List**
   - Prioritize companies with strong funding and growth
   - Focus on Colorado-connected companies (investors, founders, HQ)
   - Target specific industries (AI, biotech, cleantech, etc.)

5. **Expand Research** (Optional)
   - Add more queries to `queries.py`
   - Re-run Stage 1 pipeline to discover more companies
   - Manually add specific companies to `stage_1.json`

## Support & Modifications

This system is fully customizable. Key files to modify:

- `queries.py` - Search queries for company discovery
- `config.py` - Processing limits and configuration
- `scripts/stage_1.py` - Company discovery logic
- `scripts/stage_2.py` - Web scraping logic
- `scripts/stage_3.py` - Data enrichment and Colorado filtering
- `scripts/stage_4.py` - Intelligence extraction prompts
- `scripts/deduplicate.py` - Deduplication logic
- `scripts/main.py` - Stage 1 pipeline orchestration

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1 PIPELINE (main.py)                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │   Stage 1   │────▶│ Deduplicate │────▶│  Stage 1b   │  │
│  │ (Discovery) │     │   & Clean   │     │ (URL Find)  │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│         │                                         │          │
│         │                                         ▼          │
│         │                                 ┌─────────────┐  │
│         │                                 │  Stage 1c   │  │
│         │                                 │  (Sort A-Z) │  │
│         │                                 └─────────────┘  │
│         ▼                                         │          │
│  • Perplexity searches (119 queries)             │          │
│  • Removes duplicates by URL & name              │          │
│  • Finds missing URLs                            │          │
│  • Sorts alphabetically                          │          │
│                                                              │
│  Output: stage_1.json (cleaned, deduplicated, sorted)      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: WEB SCRAPING                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  Company    │────▶│    Web      │────▶│   Scraped   │  │
│  │    URLs     │     │  Scraper    │     │   Content   │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                              │
│  • Scrapes main page, about page, team page                │
│  • Finds and scrapes investor/funding pages                │
│  • Collects news articles about funding                    │
│  • Falls back to Playwright for JS-heavy sites             │
│  • Skips already-scraped companies                         │
│                                                              │
│  Output: stage_2.json                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: ENRICHMENT & COLORADO FILTER                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │   Scraped   │────▶│ Perplexity  │────▶│   OpenAI    │  │
│  │   Content   │     │  + OpenAI   │     │  Extract    │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                  │            │
│                                                  ▼            │
│                                          ┌─────────────┐    │
│                                          │   Colorado  │    │
│                                          │   Filter    │    │
│                                          └─────────────┘    │
│                                                              │
│  • Searches for missing data (founders, funding, location) │
│  • Extracts structured information with AI                 │
│  • Filters to Colorado companies ONLY                      │
│  • Skips already-enriched companies                        │
│                                                              │
│  Output: stage_3.json (Colorado only)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: INVESTMENT INTELLIGENCE EXTRACTION                │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  Enriched   │────▶│   OpenAI    │────▶│    Final    │  │
│  │    Data     │     │ GPT-4o-mini │     │   Report    │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                              │
│  Extracts:                                                   │
│  • Funding details (rounds, amounts, dates, investors)     │
│  • Business intelligence (model, stage, industry)          │
│  • Investor analysis (tier-1 VCs, Colorado investors)     │
│  • Location parsing (city, state)                         │
│  • Skips already-extracted companies                      │
│                                                              │
│  Output: FINAL_Investment_Intelligence.csv                 │
└─────────────────────────────────────────────────────────────┘
```

## Questions?

This system is designed to automate the discovery of Endeavor-fit companies in Colorado. If you run into issues:

1. Check error messages - they usually indicate the problem
2. Review the intermediate JSON files to debug
3. Adjust parameters in `config.py` to refine results
4. Run stages individually to isolate issues

Good luck with your Colorado startup research for Endeavor! 🚀
