# Quick Start Guide

## TL;DR - Run the Pipeline with Live Monitoring

### Terminal 1: Run the Pipeline
```bash
cd /Users/liamford/Documents/caruso/festivals
python main.py --full
```

### Terminal 2: Watch Live Progress (Optional but Cool!)
```bash
cd /Users/liamford/Documents/caruso/festivals
python monitor_progress.py
```

The monitor refreshes every 5 seconds showing:
- Which stages are complete
- How many festivals have been extracted
- Latest festival being processed
- CSV file sizes updating in real-time

### Watch CSV Files Update

**Yes!** You can see the CSVs populate as the pipeline runs:

1. Open `stage3_festivals_in_progress.csv` in Excel/Google Sheets/Numbers
2. Run the pipeline in terminal
3. Refresh the CSV every ~30 seconds to see new festivals appear
4. Every 5 festivals, the file auto-updates

The pipeline saves results every 5 festivals during Stage 3, so you'll see:
- Festival 1-5 appear
- Then 6-10
- Then 11-15
- etc.

## View Results Without Opening CSV Files

```bash
# See everything (festivals, sponsors, prospects)
python view_results.py

# See just top festivals
python view_results.py festivals

# See sponsor frequency analysis
python view_results.py sponsors

# See prioritized outreach list
python view_results.py prospects

# See pipeline status
python view_results.py summary
```

## Output Files You'll Get

After running the pipeline, these are your deliverables:

### For Your Boss (Main Deliverables)
1. **`stage4_top_sponsor_prospects.csv`** ⭐ - **PRIORITY OUTREACH LIST**
   - Sponsors appearing in 2+ festivals
   - Ranked by priority score
   - Ready for outreach campaign

2. **`stage4_sponsor_frequency_matrix.csv`** - Sponsor analysis
   - Shows which sponsors appear most often
   - Typical tier levels
   - Festival associations

3. **`stage4_comparison_table.csv`** - Festival comparison table
   - All festivals side-by-side
   - Sortable by fit score
   - Key details at a glance

4. **`stage4_top_10_report.txt`** - Detailed top 10 profiles
   - Full analysis of best matches
   - Score breakdowns
   - Sponsor lists

5. **`stage4_festival_profiles.txt`** - One-page profiles
   - Individual festival summaries
   - Format, programming, sponsors
   - Contact information

### Supporting Data
- `stage3_festivals.csv` - All festival data
- `stage3_sponsors.csv` - All sponsor relationships

## Typical Timeline

For **30 festivals** (default setting):

| Stage | Time | What Happens |
|-------|------|--------------|
| Stage 1 | 3-8 min | Finds ~50-80 candidate festivals via Perplexity API search |
| Stage 2 | 30-60 min | Scrapes websites for content |
| Stage 3 | 20-40 min | AI extracts structured data (saves every 5 festivals) |
| Stage 4 | 2-5 min | Analyzes and ranks results |
| **Total** | **1-2 hours** | Fully automated, just wait |

## Cost Estimate

- Perplexity API: ~11 queries (check [Perplexity pricing](https://www.perplexity.ai/pricing) for current rates)
- OpenAI API: ~$0.10-0.30 per festival × 30 = **~$3-9 total**

## If Something Goes Wrong

### Pipeline crashes during Stage 3
No problem! The in-progress CSV files are already saved.

```bash
# Check what you have so far
python view_results.py summary

# Continue from Stage 3
python main.py --stage 3
```

### Want to test with fewer festivals first
Edit `config.py` line 49:
```python
MAX_FESTIVALS_TO_SCRAPE = 5  # Start with just 5
```

Then run:
```bash
python main.py --full
```

### Want to see more/different festivals
Edit search queries in `config.py` lines 14-30, then:
```bash
python main.py --stage 1  # Re-run discovery
```

## Next Steps After Pipeline Completes

1. **Review Top 10** - Read `stage4_top_10_report.txt`
2. **Validate Top Sponsors** - Open `stage4_top_sponsor_prospects.csv`
3. **Compare Festivals** - Open `stage4_comparison_table.csv` in Excel
4. **Plan Outreach** - Use top prospects for sponsor emails
5. **Share with Boss** - Send the 5 main CSV/TXT files

## Tips

- Run the live monitor in a second terminal - it's satisfying to watch!
- Open the in-progress CSVs in Excel and refresh periodically
- The pipeline can run overnight if needed
- All data is saved locally - no cloud uploads
- Re-run any stage individually without redoing previous work

## Common Questions

**Q: Can I stop and resume?**
Yes! Stop with Ctrl+C, then run the next stage when ready.

**Q: Can I process more than 30 festivals?**
Yes! Edit `MAX_FESTIVALS_TO_SCRAPE` in `config.py` (up to ~100 recommended)

**Q: How accurate is the AI extraction?**
Very good for major data points. Spot-check a few festivals to verify.

**Q: Can I adjust the scoring?**
Yes! Edit the scoring weights in `config.py` or `schema.py`

**Q: Do I need to keep terminal open?**
Yes, but you can run it in the background or use `screen`/`tmux`

---

Ready? Run this now:
```bash
python main.py --full
```

Then open a second terminal and run:
```bash
python monitor_progress.py
```

Watch the magic happen! 🎵✨
