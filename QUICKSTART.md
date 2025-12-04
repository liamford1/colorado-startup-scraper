# Quick Start Guide

## TL;DR - Run the Pipeline

### Run Stage 1 Pipeline (Discovery & Preparation)
```bash
cd scripts
python main.py
```

This automatically runs:
1. Stage 1 - Company discovery via Perplexity
2. Deduplication - Remove duplicates and clean names
3. Stage 1b - Find missing URLs
4. Stage 1c - Sort alphabetically

**Time:** ~10-20 minutes
**Output:** `outputs/stage_1.json` (cleaned, deduplicated, sorted)

### Run Remaining Stages

```bash
# Stage 2: Web Scraping
python stage_2.py

# Stage 3: Data Enrichment & Colorado Filter
python stage_3.py

# Stage 4: Investment Intelligence Extraction
python stage_4.py
```

## Monitor Progress (Optional but Useful!)

### Terminal 1: Run the stages
```bash
cd scripts
python main.py
# Then run stage_2.py, stage_3.py, stage_4.py
```

### Terminal 2: Watch live progress
```bash
cd scripts
python monitor_progress.py
```

The monitor refreshes every 5 seconds showing:
- Which stages are complete
- How many companies have been processed
- Latest company being processed
- File counts updating in real-time

## Watch Progress Files Update

**Yes!** You can see the progress CSVs populate as the pipeline runs:

1. Open `outputs/stage_1_progress.csv` in Excel/Google Sheets
2. Run the pipeline in terminal
3. Refresh the CSV every ~30 seconds to see new companies appear
4. Progress is saved incrementally - safe to stop anytime

## Output Files You'll Get

After running all stages:

### Main Deliverable
**`outputs/FINAL_Investment_Intelligence.csv`** ⭐
- Complete investment intelligence report
- Company details, founders, funding, investors
- Business intelligence (industry, model, stage)
- Location, social links, tier-1 VCs

### Supporting Files
- `outputs/stage_1.json` - Discovered companies (deduplicated, sorted)
- `outputs/stage_2.json` - Scraped website content
- `outputs/stage_3.json` - Enriched data (Colorado only)
- `outputs/*.csv` - Progress tracking files for each stage

## Typical Timeline

For **50 companies**:

| Stage | Time | What Happens |
|-------|------|--------------|
| Stage 1 Pipeline | 10-20 min | Discovers, deduplicates, finds URLs, sorts |
| Stage 2 | 30-60 min | Scrapes websites (rate-limited) |
| Stage 3 | 30-60 min | Enriches data, filters to Colorado |
| Stage 4 | 10-15 min | Extracts investment intelligence |
| **Total** | **1.5-3 hours** | Fully automated |

## Cost Estimate

For **50 companies**:

- **Perplexity API:** 150-200 queries (~$2-5)
- **OpenAI API:** ~$7-20 total
- **Total:** ~$10-25

Check [Perplexity pricing](https://www.perplexity.ai/pricing) for current rates.

## If Something Goes Wrong

### Pipeline crashes during any stage
No problem! Progress files are saved incrementally.

```bash
# Check what you have so far
python view_results.py

# Continue from where it stopped
python stage_2.py  # or stage_3.py, stage_4.py
```

### Want to test with fewer companies first
Edit `config.py`:
```python
MAX_FESTIVALS_TO_SCRAPE = 10  # Start with just 10
```

Then run:
```bash
cd scripts
python main.py
```

### Want to discover more companies
Edit search queries in `queries.py`, then:
```bash
cd scripts
python stage_1.py  # Re-run discovery only
```

The new companies will be added to existing data (no duplicates).

### Duplicate companies appearing
```bash
cd scripts
python deduplicate.py  # Clean all stage files
```

This removes duplicates from all output files and creates backups.

## Next Steps After Pipeline Completes

1. **Open Final Report** - Review `FINAL_Investment_Intelligence.csv`
2. **Sort & Filter** - Open in Excel, sort by funding amount or investors
3. **Analyze VCs** - Look for tier-1 VCs and Colorado investors
4. **Validate Data** - Spot-check top companies against their websites
5. **Create Outreach List** - Focus on well-funded Colorado companies

## Tips

- **Run the live monitor** in a second terminal - it's satisfying to watch!
- **Open progress CSVs** in Excel and refresh periodically
- **All stages are resumable** - safe to stop with Ctrl+C anytime
- **Incremental processing** - re-running stages only processes NEW companies
- **Colorado filter** - Stage 3 removes non-Colorado companies

## Common Questions

**Q: Can I stop and resume?**
Yes! Stop with Ctrl+C, then run the next stage when ready.

**Q: Can I process more than 50 companies?**
Yes! Edit `MAX_FESTIVALS_TO_SCRAPE` in `config.py` or set to `None` for all.

**Q: How accurate is the AI extraction?**
Very good for major data points. Spot-check a few companies to verify.

**Q: Why are some companies removed in Stage 3?**
Stage 3 filters to Colorado-only companies. Non-Colorado companies are removed.

**Q: Do I need to keep terminal open?**
Yes, but you can run it in the background or use `screen`/`tmux`.

---

Ready? Run this now:
```bash
cd scripts
python main.py
```

Then open a second terminal and run:
```bash
cd scripts
python monitor_progress.py
```

Watch the magic happen! 🚀✨
