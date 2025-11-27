# Colorado Startup & Investor Research Pipeline (Endeavor Criteria)

An automated system to discover, analyze, and rank Colorado startups and their investors based on Endeavor Colorado's selection criteria.

## Overview

This pipeline automates the research of Colorado startups, founders, and investors through 4 stages:

1. **Discovery** - Uses Perplexity API to find Colorado startups, VCs, and portfolio companies
2. **Scraping** - Collects website content, investor pages, and funding announcements
3. **AI Extraction** - Uses OpenAI GPT to extract structured data (founders, CEOs, investors)
4. **Analysis** - Scores companies by Endeavor criteria and analyzes investor patterns

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

### Option 1: Run Full Pipeline (Recommended)

```bash
python main.py --full
```

This runs all 4 stages with pauses between each stage for review.

**Estimated time:** 1-2 hours depending on number of companies found
**Cost estimate:** ~$5-15 in API calls

### Option 2: Run Individual Stages

```bash
# Stage 1: Discovery (find companies)
python main.py --stage 1

# Stage 2: Scraping (collect website content)
python main.py --stage 2

# Stage 3: AI Extraction (extract structured data)
python main.py --stage 3

# Stage 4: Analysis (score and analyze)
python main.py --stage 4
```

## Output Files

### Stage 1 Output
- `stage1_candidates.json` - List of company URLs found via search

### Stage 2 Output
- `stage2_scraped_data.json` - Raw website content, investor pages, news articles

### Stage 3 Output
- `stage3_companies.json` - Structured company data with founders, CEOs, investors

### Stage 4 Output (DELIVERABLES)
- **`companies_complete_data.csv`** - Complete company information with all fields
- **`companies_rankings.csv`** - Ranked list with founders, CEOs, and key metrics
- **`investor_prospects.csv`** - Colorado VCs sorted by portfolio size and activity
- **`all_investors.csv`** - All investor relationships across all companies

## Scoring System

Each company is scored 0-100 on fit to Endeavor criteria:

- **Business model (0-20)** - Scalable model (SaaS, platform, marketplace)
- **Market alignment (0-15)** - Industry fit with Endeavor focus areas
- **Stage fit (0-10)** - Appropriate funding stage (Seed to Series D)
- **Team quality (0-10)** - Technical founders, co-founder team
- **Traction (0-20)** - Revenue, customers, growth metrics
- **Investor backing (0-15)** - Quality and presence of investors
- **Exit potential (0-10)** - High/medium/low exit potential

## Customization

### Adjust Search Queries
Edit `config.py` line 22 to modify the `CUSTOM_SEARCH_QUERIES` list:

```python
CUSTOM_SEARCH_QUERIES = [
    "Find DeepTech startups in Colorado with venture capital funding founded since 2020",
    # Add your own queries here
]
```

### Adjust Scoring Weights
Edit `config.py` line 183 to change Endeavor criteria weights:

```python
SCORE_WEIGHTS = {
    'business_model': 20,
    'traction': 20,  # Increase importance of traction
    # ...
}
```

### Adjust Endeavor Target Criteria
Edit `config.py` line 194 to modify target parameters:

```python
TARGET_FOUNDING_YEAR_MIN = 2020  # Only companies founded since 2020
FUNDING_YEAR_MIN = 2019          # Funded in last 5 years
```

## Key Features

### 1. Founder & CEO Extraction
- Extracts all founder names from website and news articles
- Identifies current CEO
- Verifies Colorado location when possible

### 2. Comprehensive Investor Data
- Searches company websites AND news articles for funding info
- Extracts investor names, tiers (Lead, Series A/B/C, etc.)
- Identifies Colorado VCs and their portfolios
- Tracks funding rounds and amounts

### 3. Endeavor Criteria Scoring
- Prioritizes companies founded since 2020
- Emphasizes DeepTech industries
- Scores based on growth indicators
- Flags companies with Colorado founders/HQ

### 4. VC Portfolio Analysis
- Shows which VCs are most active in Colorado
- Lists portfolio companies for each VC
- Identifies VCs investing in multiple companies (higher priority)

## Monitoring & Progress

### Real-Time Monitoring

In one terminal, run the pipeline:
```bash
python main.py --full
```

In a **second terminal**, run the live monitor:
```bash
python monitor_progress.py
```

This shows:
- ✅ Which stages are complete
- ⏳ Current progress of running stages
- 📊 Number of companies/investors extracted so far
- 📍 Most recently extracted company

### View Results Anytime

```bash
# View everything
python view_results.py

# View specific sections
python view_results.py companies   # Top companies by score
python view_results.py investors   # Investor frequency
python view_results.py prospects   # VC outreach priorities
```

## Example Output

### Top Company Report
```
1. Acme AI - Boulder, CO
   Fit Score: 87/100

   Key Details:
     - Founded: 2021
     - Founders: Jane Smith, John Doe
     - CEO: Jane Smith
     - Business Model: SaaS
     - Stage: Series A
     - Industries: AI, Enterprise Software
     - Team Size: 45
     - Funding: $15M
     - Investors: 5

   Top Investors:
     - Foundry Group (Lead)
     - Boulder Ventures (Series-A)
     - Techstars (Angel)
```

### Investor Prospects
```
Top 5 Investor Prospects (Colorado VCs):
  1. Foundry Group (invested in 8 companies, priority: 105)
  2. Access Venture Partners (invested in 6 companies, priority: 85)
  3. Boulder Ventures (invested in 5 companies, priority: 70)
```

## Tips for Best Results

### Before Running
1. **Review search queries** in `config.py` to ensure they target Endeavor criteria
2. **Check API quotas** - Perplexity and OpenAI have usage limits
3. **Estimate costs** - OpenAI charges ~$0.10-0.30 per company analyzed

### During Execution
1. **Monitor Stage 1 results** - If too many irrelevant results, adjust search queries
2. **Review Stage 2 output** - Check if websites are being scraped successfully
3. **Sample Stage 3 extractions** - Verify AI is extracting founder/CEO names correctly

### After Completion
1. **Review `companies_rankings.csv`** - Validate top companies match Endeavor criteria
2. **Check `investor_prospects.csv`** - Focus on Colorado VCs with multiple portfolio companies
3. **Verify founder locations** - Ensure founders are actually based in Colorado
4. **Cross-reference with Endeavor Colorado** - Check if any companies overlap with existing portfolio

## Troubleshooting

### "No candidates found"
- Check Perplexity API key is correct
- Try running Stage 1 directly to see error messages
- Verify Perplexity API quota isn't exceeded

### "Scraping failed" errors
- Some websites block scrapers - this is normal
- The pipeline continues with successful scrapes
- Check `stage2_scraped_data.json` to see which sites worked

### AI extraction not finding founders/CEOs
- Check if company website has "About" or "Team" page
- Review `stage2_scraped_data.json` to see if team info was scraped
- Try using `gpt-4o` instead of `gpt-4o-mini` (more expensive but more accurate)

### Not enough Colorado companies
- Add more Colorado-specific search queries in `config.py`
- Include specific Colorado cities (Denver, Boulder, Fort Collins, etc.)
- Search for specific Colorado VCs and their portfolios

## Cost & Time Estimates

### Perplexity API
- **Stage 1 uses ~40 queries** (one per search query in config)
- Check [Perplexity pricing](https://www.perplexity.ai/pricing) for current rates
- Estimated cost: ~$2-5 for Stage 1

### OpenAI API
- GPT-4o-mini: ~$0.10-0.30 per company extraction
- GPT-4o: ~$1-2 per company (more accurate)
- **Stage 3 cost for 50 companies: ~$5-15** (using gpt-4o-mini)

### Time
- Stage 1: ~5-10 minutes (40+ searches)
- Stage 2: ~30-60 minutes (depends on # of companies)
- Stage 3: ~20-40 minutes (depends on # of companies)
- Stage 4: ~2-5 minutes

**Total: 1-2 hours for 50 companies**

## Next Steps After Pipeline Completes

1. **Review Top Companies** (`companies_rankings.csv`)
   - Verify founders are in Colorado
   - Check if companies match Endeavor's focus areas
   - Validate funding information is accurate

2. **Analyze VCs** (`investor_prospects.csv`)
   - Identify most active Colorado VCs
   - Research their investment thesis and portfolio
   - Consider for Endeavor network/partnerships

3. **Create Outreach Strategy**
   - Prioritize companies with high Endeavor fit scores
   - Focus on companies founded since 2020
   - Target DeepTech companies with strong growth metrics

4. **Validate Data Quality**
   - Spot-check company details against their websites
   - Verify founder/CEO names and locations
   - Update any incorrect information

5. **Expand Research** (Optional)
   - Re-run Stage 1 with different search queries
   - Add specific companies manually to `stage1_candidates.json`
   - Target specific industries (AI, biotech, cleantech)

## Support & Modifications

This system is fully customizable. Key files to modify:

- `config.py` - Search queries, scoring weights, Endeavor criteria
- `stage3_extract.py` - AI extraction prompt (for founder/CEO extraction)
- `schema.py` - Data model and scoring algorithm
- `stage4_analyze.py` - Analysis and reporting

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: DISCOVERY                                         │
│  ┌─────────────┐     ┌─────────────┐                       │
│  │ Perplexity  │────▶│  Candidate  │                       │
│  │     API     │     │  Company    │                       │
│  │  (sonar)    │     │   List      │                       │
│  └─────────────┘     └─────────────┘                       │
│                                                              │
│  Sources:                                                    │
│  • coloradostartups.org leaderboard                         │
│  • endeavorcolorado.org portfolio                           │
│  • Colorado VC portfolios                                   │
│  • News/press releases                                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: SCRAPING                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  Company    │────▶│    Web      │────▶│   Scraped   │  │
│  │    URLs     │     │  Scraper    │     │   Content   │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                              │
│  Collects:                                                   │
│  • Main page, About page, Team page                         │
│  • Investor/funding pages                                   │
│  • News articles about funding                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: AI EXTRACTION                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │   Scraped   │────▶│   OpenAI    │────▶│ Structured  │  │
│  │   Content   │     │  GPT-4o     │     │    Data     │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                              │
│  Extracts:                                                   │
│  • Founder names (with CO location)                         │
│  • CEO name                                                  │
│  • All investors (VCs, angels, rounds)                      │
│  • Business model, stage, traction                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: ANALYSIS                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │ Structured  │────▶│  Endeavor   │────▶│   Reports   │  │
│  │    Data     │     │  Scoring    │     │  & CSVs     │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│                                                              │
│  Outputs:                                                    │
│  • companies_rankings.csv (founders, CEOs)                  │
│  • investor_prospects.csv (Colorado VCs)                    │
│  • all_investors.csv (full VC portfolios)                   │
└─────────────────────────────────────────────────────────────┘
```

## Questions?

This system is designed to automate the discovery of Endeavor-fit companies in Colorado. If you run into issues:

1. Check error messages - they usually indicate the problem
2. Review the intermediate JSON files to debug
3. Adjust parameters in `config.py` to refine results
4. Run stages individually to isolate issues

Good luck with your Colorado startup research for Endeavor! 🚀
