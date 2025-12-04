# Running the Pipeline Step by Step

This guide shows you how to run each stage of the pipeline independently to add more companies to your list.

## Important Notes

- **No Overwrites**: Each stage automatically checks for existing data and only adds NEW companies
- **No Duplicates**: URLs are used as unique identifiers, so duplicates are automatically filtered
- **Incremental**: You can run stages multiple times - only new companies will be processed

## Stage 1: Company Discovery

Searches for companies using Perplexity API based on queries in `queries.py`.

```bash
cd scripts
python stage_1.py
```

**What it does:**
- Runs all search queries defined in your config
- Filters out duplicates by URL
- Saves new candidates to `outputs/stage_1.json`
- Creates progress CSV at `outputs/stage_1_progress.csv`

**Output:**
- `outputs/stage_1.json` - All discovered companies (existing + new)
- `outputs/stage_1_progress.csv` - Easy-to-read progress file

**Current queries:** 119 queries focused on early-stage Colorado startups

---

## Stage 2: Website Scraping

Scrapes company websites to collect content, investor pages, PDFs, etc.

```bash
cd scripts
python stage_2.py
```

**What it does:**
- Loads candidates from Stage 1
- Skips companies already scraped
- Scrapes website content, about pages, investor pages
- Collects PDFs and news articles about funding
- Saves progress after each company

**Output:**
- `outputs/stage_2.json` - All scraped data (existing + new)
- `outputs/stage_2_progress.csv` - Easy-to-read progress file

**Features:**
- Falls back to Playwright for JavaScript-heavy sites
- Rate limiting to avoid blocking
- Incremental saving (won't lose progress if interrupted)

---

## Stage 3: Data Enrichment

Enriches company data with AI extraction and external searches.

```bash
cd scripts
python stage_3.py
```

**What it does:**
- Loads scraped data from Stage 2
- Skips companies already enriched
- Uses Perplexity to fill missing data (founders, funding, location)
- Uses OpenAI to extract structured information
- Filters to keep only Colorado companies
- Saves progress after each company

**Output:**
- `outputs/stage_3.json` - All enriched data (existing + new)
- `outputs/stage_3_progress.csv` - Easy-to-read progress file

**Colorado Filter:**
- Only keeps companies with Colorado locations
- Removes companies not headquartered in CO

---

## Stage 4: Final Analysis (Optional)

Analyzes and scores companies based on Endeavor criteria.

```bash
cd scripts
python stage_4.py
```

**What it does:**
- Loads enriched data from Stage 3
- Scores companies on business model, traction, investors, etc.
- Generates final CSV with scores
- Creates detailed reports

**Output:**
- `outputs/FINAL_Investment_Intelligence.json`
- `outputs/FINAL_Investment_Intelligence.csv`

---

## Customizing Search Queries

All search queries are now in `queries.py` for easy management.

### Option 1: Use all queries (most comprehensive)
In `config.py`:
```python
CUSTOM_SEARCH_QUERIES = ALL_QUERIES  # 119 queries
```

### Option 2: Focus on early-stage companies
In `config.py`:
```python
CUSTOM_SEARCH_QUERIES = EARLY_STAGE_FOCUS  # Seed/pre-seed focus
```

### Option 3: Mix and match categories
In `config.py`:
```python
CUSTOM_SEARCH_QUERIES = EARLY_STAGE_QUERIES + SPECIFIC_VC_QUERIES + NEWS_QUERIES
```

### Option 4: Add your own queries
In `queries.py`, add to any category or create a new one:
```python
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

## Query Categories in queries.py

- **LEADERBOARD_QUERIES** - Colorado Startups leaderboard, Built In CO, etc.
- **ENDEAVOR_QUERIES** - Endeavor Colorado portfolio companies
- **EARLY_STAGE_QUERIES** - Seed, pre-seed, newly founded (2022-2024)
- **FUNDED_QUERIES** - Recent funding rounds (last 5 years)
- **DEEPTECH_QUERIES** - AI, robotics, biotech, cleantech
- **CITY_QUERIES** - Boulder, Denver, Fort Collins, etc.
- **VC_PORTFOLIO_QUERIES** - General VC portfolio searches
- **SPECIFIC_VC_QUERIES** - Foundry, Techstars, Boulder Ventures, etc.
- **GROWTH_QUERIES** - High-growth, unicorns, rapid revenue growth
- **FOUNDER_QUERIES** - Founder and CEO searches
- **INDUSTRY_QUERIES** - SaaS, fintech, healthcare, climate, etc.
- **NEWS_QUERIES** - News articles and press releases about funding
- **UNIVERSITY_QUERIES** - CU Boulder, CSU, Mines spinouts
- **REMOTE_QUERIES** - Remote-first Colorado companies

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

### Check query count:
```bash
python queries.py
```

---

## Example Workflow: Adding More Companies

1. **Customize queries** (optional):
   ```bash
   # Edit queries.py to add more queries
   nano queries.py

   # Or edit config.py to change which query set to use
   nano config.py
   ```

2. **Run Stage 1** to discover new companies:
   ```bash
   cd scripts
   python stage_1.py
   # Will add new companies to outputs/stage_1.json
   ```

3. **Run Stage 2** to scrape new websites:
   ```bash
   python stage_2.py
   # Will only scrape NEW companies from Stage 1
   ```

4. **Run Stage 3** to enrich new data:
   ```bash
   python stage_3.py
   # Will only enrich NEW companies from Stage 2
   # Filters to Colorado companies only
   ```

5. **Run Stage 4** (optional) for final analysis:
   ```bash
   python stage_4.py
   # Analyzes all companies and generates final reports
   ```

---

## Tips

- **Run stages separately** - You don't need to run all stages at once
- **Stage 1 is fast** - Re-run Stage 1 anytime to discover more companies
- **Stage 2 is slowest** - Scraping takes time due to rate limiting
- **Stage 3 uses APIs** - Make sure you have Perplexity and OpenAI API keys
- **Check progress files** - `.csv` files in `outputs/` are easy to open in Excel
- **Interrupt safely** - All stages save progress incrementally, safe to Ctrl+C

---

## Troubleshooting

**No new companies found in Stage 1?**
- Try adding more queries to `queries.py`
- Or change the query set in `config.py`

**Stage 2 failing to scrape?**
- Some sites block automated scraping
- Check `outputs/stage_2_progress.csv` to see which succeeded

**Stage 3 not finding Colorado companies?**
- Some companies may not have clear location data
- Check `outputs/stage_3_progress.csv` to see what was found

**Want to re-process a company?**
- Manually remove it from the output JSON files
- It will be processed again on next run
