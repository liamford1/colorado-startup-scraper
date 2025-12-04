# Running the Pipeline Step by Step

This guide shows you how to run each stage of the pipeline independently.

## Important Notes

- **No Overwrites**: Each stage automatically checks for existing data and only adds NEW companies
- **No Duplicates**: URLs are used as unique identifiers, so duplicates are automatically filtered
- **Incremental**: You can run stages multiple times - only new companies will be processed
- **Colorado Filter**: Stage 3 removes non-Colorado companies automatically

## Stage 1 Pipeline: Discovery & Preparation

Run the complete Stage 1 pipeline with one command:

```bash
cd scripts
python main.py
```

**What it does:**
1. **Stage 1** - Searches for companies using Perplexity API (119 queries)
2. **Deduplication** - Removes duplicates by URL and company name, cleans names
3. **Stage 1b** - Finds URLs for companies with "URL_NEEDED" placeholder
4. **Stage 1c** - Sorts results alphabetically by company name

**Output:**
- `outputs/stage_1.json` - All discovered companies (deduplicated and sorted)
- `outputs/stage_1_progress.csv` - Easy-to-read progress file

**Features:**
- Creates timestamped backups before deduplication
- Stops if any step fails
- Shows summary of each step

**Time:** ~10-20 minutes

---

## Or Run Stage 1 Components Individually

If you prefer to run Stage 1 components separately:

### Stage 1: Company Discovery

```bash
cd scripts
python stage_1.py
```

**What it does:**
- Runs all search queries defined in `queries.py`
- Filters out duplicates by URL
- Saves candidates to `outputs/stage_1.json`

**Output:**
- `outputs/stage_1.json` - Discovered companies
- `outputs/stage_1_progress.csv` - Progress file

### Deduplication

```bash
cd scripts
python deduplicate.py
```

**What it does:**
- Creates timestamped backups of all stage files
- Removes duplicate companies by URL and company name
- Cleans company names (removes markdown, numbering)
- Prioritizes entries with real URLs over "URL_NEEDED"

**Output:**
- Updates all stage JSON files in place
- Creates backup files with timestamps

### Stage 1b: URL Discovery

```bash
cd scripts
python stage_1b.py
```

**What it does:**
- Finds companies with "URL_NEEDED" placeholder
- Uses Perplexity API to search for official website URLs
- Updates companies with found URLs
- Saves progress every 10 companies

**Output:**
- Updates `outputs/stage_1.json` with found URLs

### Stage 1c: Alphabetical Sorting

```bash
cd scripts
python stage_1c.py
```

**What it does:**
- Sorts `stage_1.json` alphabetically by company name
- Sorts `stage_1_progress.csv` alphabetically

**Output:**
- Updates both files in place (sorted A-Z)

---

## Stage 2: Website Scraping

Scrapes company websites to collect content, investor pages, and PDFs.

```bash
cd scripts
python stage_2.py
```

**What it does:**
- Loads candidates from Stage 1
- **Skips companies already scraped** (checks existing `stage_2.json`)
- Scrapes website content, about pages, investor pages
- Finds and scrapes news articles about funding
- Falls back to Playwright for JavaScript-heavy sites
- Saves progress after each company

**Output:**
- `outputs/stage_2.json` - All scraped data (existing + new)
- `outputs/stage_2_progress.csv` - Easy-to-read progress file

**Features:**
- Rate limiting to avoid blocking
- Incremental saving (won't lose progress if interrupted)
- Skips companies with "URL_NEEDED"

**Time:** ~30-60 minutes for 50 companies

---

## Stage 3: Data Enrichment & Colorado Filter

Enriches company data with AI extraction and filters to Colorado companies only.

```bash
cd scripts
python stage_3.py
```

**What it does:**
- Loads scraped data from Stage 2
- **Skips companies already enriched** (checks existing `stage_3.json`)
- Uses Perplexity to search for missing data (founders, funding, location)
- Uses OpenAI to extract structured information
- **Filters to keep only Colorado companies**
- Saves progress after each company

**Output:**
- `outputs/stage_3.json` - All enriched data (Colorado only)
- `outputs/stage_3_progress.csv` - Easy-to-read progress file

**Colorado Filter:**
- Only keeps companies with Colorado locations
- Removes companies not headquartered in CO
- Shows which companies were removed

**Time:** ~30-60 minutes for 50 companies

---

## Stage 4: Investment Intelligence Extraction

Extracts comprehensive investment intelligence using OpenAI.

```bash
cd scripts
python stage_4.py

# Or test with just 5 companies first:
python stage_4.py --test
```

**What it does:**
- Loads enriched data from Stage 3
- **Skips companies already extracted** (checks existing output)
- Uses OpenAI (gpt-4o-mini) to extract detailed intelligence
- Normalizes funding amounts, parses locations
- Identifies tier-1 VCs and Colorado investors
- Saves progress after each company

**Output:**
- `outputs/FINAL_Investment_Intelligence.json`
- `outputs/FINAL_Investment_Intelligence.csv`

**Extracts:**
- Company details (name, URL, description, founders)
- Location (city, state, headquarters)
- Funding (total, rounds, amounts, dates, progression)
- Investors (lead, tier-1 VCs, Colorado investors, counts)
- Business intelligence (industry, model, stage, tech focus)
- Social links (LinkedIn, Crunchbase)

**Time:** ~10-15 minutes for 50 companies

---

## Customizing Search Queries

All search queries are in `queries.py` for easy management.

### Current Query Categories

```python
# In queries.py
LEADERBOARD_QUERIES      # Colorado Startups leaderboard, Built In CO
ENDEAVOR_QUERIES         # Endeavor Colorado portfolio
EARLY_STAGE_QUERIES      # Seed, pre-seed, newly founded
FUNDED_QUERIES           # Recent funding rounds
DEEPTECH_QUERIES         # AI, robotics, biotech, cleantech
CITY_QUERIES             # Boulder, Denver, Fort Collins, etc.
VC_PORTFOLIO_QUERIES     # General VC portfolio searches
SPECIFIC_VC_QUERIES      # Foundry, Techstars, Boulder Ventures
GROWTH_QUERIES           # High-growth companies
FOUNDER_QUERIES          # Founder and CEO searches
INDUSTRY_QUERIES         # SaaS, fintech, healthcare, climate
NEWS_QUERIES             # News articles about funding
UNIVERSITY_QUERIES       # CU Boulder, CSU, Mines spinouts
REMOTE_QUERIES           # Remote-first Colorado companies

# Use all queries (recommended)
ALL_QUERIES = sum([...all categories...], [])
```

### Add Your Own Queries

```python
# In queries.py
CUSTOM_QUERIES = [
    "Find Colorado startups in [your industry]",
    "Find [specific VC] portfolio companies in Colorado",
]
```

Then in `config.py`:
```python
from queries import CUSTOM_QUERIES
CUSTOM_SEARCH_QUERIES = CUSTOM_QUERIES
```

---

## Monitoring Progress

### View current results:
```bash
cd scripts
python view_results.py
```

### Monitor live progress:
```bash
cd scripts
python monitor_progress.py
```

Shows:
- Which stages are complete
- Current progress of running stages
- Number of companies processed
- Most recently processed company

---

## Example Workflow: Adding More Companies

1. **Add queries** (optional):
   ```bash
   # Edit queries.py to add more queries
   nano queries.py
   ```

2. **Run Stage 1 Pipeline** to discover new companies:
   ```bash
   cd scripts
   python main.py
   # Discovers, deduplicates, finds URLs, sorts
   ```

3. **Run Stage 2** to scrape new websites:
   ```bash
   python stage_2.py
   # Only scrapes NEW companies from Stage 1
   ```

4. **Run Stage 3** to enrich new data:
   ```bash
   python stage_3.py
   # Only enriches NEW companies from Stage 2
   # Filters to Colorado companies only
   ```

5. **Run Stage 4** for final intelligence:
   ```bash
   python stage_4.py
   # Extracts intelligence for all companies
   ```

---

## Processing Limits

Control how many companies to process:

```python
# In config.py
MAX_FESTIVALS_TO_SCRAPE = None  # Process all companies
# or
MAX_FESTIVALS_TO_SCRAPE = 50    # Process first 50 only
```

This limit applies to Stages 2, 3, and 4.

---

## Tips

- **Stage 1 Pipeline** - Run `main.py` for automated discovery, dedup, URL finding, sorting
- **Run stages separately** - You don't need to run all stages at once
- **Stage 1 is fast** - Re-run Stage 1 to discover more companies anytime
- **Stage 2 is slowest** - Scraping takes time due to rate limiting
- **Stage 3 uses APIs** - Make sure you have Perplexity and OpenAI API keys
- **Check progress CSVs** - Easy to open in Excel to see results
- **Interrupt safely** - All stages save progress incrementally, safe to Ctrl+C
- **Deduplication** - Built into Stage 1 pipeline, but can run `deduplicate.py` anytime

---

## Troubleshooting

**No new companies found in Stage 1?**
- Try adding more queries to `queries.py`
- Check if Perplexity API quota is exceeded

**Stage 2 failing to scrape?**
- Some sites block automated scraping (normal)
- Check `outputs/stage_2_progress.csv` to see which succeeded
- Failed scrapes are skipped, pipeline continues

**Stage 3 removing too many companies?**
- Stage 3 filters to Colorado-only companies
- Check `outputs/stage_3_progress.csv` to see removed companies
- Companies without clear Colorado location are removed

**Want to re-process a company?**
- Manually remove it from the output JSON files
- It will be processed again on next run

**Duplicates appearing?**
- Run `python deduplicate.py` to clean all stage files
- Creates backups before cleaning

---

## Cost Management

**To minimize costs:**
1. Start with `MAX_FESTIVALS_TO_SCRAPE = 10` to test
2. Use `python stage_4.py --test` to test Stage 4 with 5 companies
3. Review results before processing all companies
4. Only re-run stages when adding new companies

**Stages use APIs:**
- Stage 1: Perplexity (~119 queries)
- Stage 1b: Perplexity (~1 query per company missing URL)
- Stage 3: Perplexity (2-3 queries per company) + OpenAI (gpt-4o-mini)
- Stage 4: OpenAI (gpt-4o-mini)

---

## Summary

```bash
# Complete workflow
cd scripts

# Stage 1 Pipeline (automated)
python main.py

# Remaining stages
python stage_2.py
python stage_3.py
python stage_4.py

# Optional: Monitor progress
python monitor_progress.py  # In second terminal
```

All stages automatically skip already-processed companies and save progress incrementally!
