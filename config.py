"""
Configuration settings for the festival research pipeline
Adjust these settings without modifying the core code
"""

# STAGE 1: DISCOVERY SETTINGS
# ============================

# Number of results to fetch per search query
SEARCH_RESULTS_PER_QUERY = 10

# Rate limiting delay between searches (seconds)
SEARCH_DELAY = 2.0

# Perplexity API model to use
# Options: "sonar" (faster, cheaper), "sonar-pro" (better quality, more expensive)
PERPLEXITY_MODEL = "sonar-pro"

# Custom search queries
# Import from queries.py for better organization
# You can choose different query sets based on your focus:
#   - ALL_QUERIES: All available queries (most comprehensive)
#   - EARLY_STAGE_FOCUS: Focus on seed/pre-seed companies
#   - DEEPTECH_FOCUS: Focus on deep tech companies
#   - NEWS_FOCUS: Focus on recent funding announcements
# Or create your own custom list below

from queries import (
    ALL_QUERIES,           # All 119 queries
    EARLY_STAGE_FOCUS,     # Focus on early-stage companies
    DEEPTECH_FOCUS,        # Focus on deep tech
    NEWS_FOCUS,            # Focus on recent news
    # Individual categories (if you want to mix and match):
    EARLY_STAGE_QUERIES,
    FUNDED_QUERIES,
    SPECIFIC_VC_QUERIES,
    LEADERBOARD_QUERIES,
    INDUSTRY_QUERIES,
)

# Choose your query set:
# Option 1: Use ALL queries (most comprehensive, takes longer)
CUSTOM_SEARCH_QUERIES = ALL_QUERIES

# Option 2: Use EARLY_STAGE_FOCUS for seed/pre-seed companies
# CUSTOM_SEARCH_QUERIES = EARLY_STAGE_FOCUS

# Option 3: Combine specific categories
# CUSTOM_SEARCH_QUERIES = EARLY_STAGE_QUERIES + SPECIFIC_VC_QUERIES + LEADERBOARD_QUERIES

# Option 4: Create your own custom list
# CUSTOM_SEARCH_QUERIES = [
#     "Your custom query here",
#     "Another custom query",
# ]

# Domains to exclude from discovery
EXCLUDE_DOMAINS = [
    'wikipedia.org',
    'youtube.com',
    'facebook.com',
    'instagram.com',
    'twitter.com',
    'reddit.com'
]

# Keywords that disqualify a candidate
EXCLUDE_KEYWORDS = [
    'publicly traded',
    'public company',
    'nasdaq',
    'nyse',
    'fortune 500',
    'established in 19',  # Avoid very old companies
    'founded in 19',     # Companies older than 2000
    'consulting firm only',
    'law firm',
    'accounting firm',
]


# STAGE 2: SCRAPING SETTINGS
# ===========================

# Maximum number of festivals to scrape
# Set to None or 0 to scrape all discovered candidates
MAX_FESTIVALS_TO_SCRAPE = None  # None = process all festivals

# Request timeout in seconds
SCRAPE_TIMEOUT = 10

# Maximum sponsor pages to scrape per festival
MAX_SPONSOR_PAGES_PER_FESTIVAL = 5

# Maximum PDFs to collect per festival
MAX_PDFS_PER_FESTIVAL = 15

# Rate limiting delay between scrapes (seconds)
SCRAPE_DELAY = 2

# Maximum content size to extract (characters)
MAX_MAIN_CONTENT_SIZE = 50000
MAX_ABOUT_CONTENT_SIZE = 10000


# STAGE 3: AI EXTRACTION SETTINGS
# ================================

# OpenAI model to use
# Options: "gpt-4o-mini" (cheap, fast), "gpt-4o" (more accurate, expensive)
OPENAI_MODEL = "gpt-4o-mini"

# Temperature for AI extraction (0.0 = deterministic, 1.0 = creative)
EXTRACTION_TEMPERATURE = 0.1

# Maximum tokens for AI response
EXTRACTION_MAX_TOKENS = 3000

# Rate limiting delay between AI calls (seconds)
EXTRACTION_DELAY = 0.5

# Maximum content to send to AI (characters)
MAX_CONTENT_FOR_AI = 80000


# STAGE 4: ANALYSIS SETTINGS
# ===========================

# Number of top festivals to include in detailed reports
TOP_N_FESTIVALS = 10

# Minimum frequency for a sponsor to be considered a "top prospect"
MIN_SPONSOR_FREQUENCY = 2

# Sponsor priority scoring weights
SPONSOR_FREQUENCY_WEIGHT = 10  # Points per appearance
TOP_FESTIVAL_BONUS = 5         # Bonus per appearance in top-10 festival
PRESENTING_TIER_BONUS = 15     # Bonus for presenting/title sponsor
PREMIUM_TIER_BONUS = 10        # Bonus for platinum/gold sponsor


# FIT SCORING WEIGHTS (ENDEAVOR CRITERIA)
# ========================================
# Adjust these to change how companies are scored (must sum to 100)

SCORE_WEIGHTS = {
    'business_model': 20,        # Scalable business model (SaaS, platform, etc.)
    'market_alignment': 15,      # Industry/market fit with Endeavor focus
    'stage_fit': 10,             # Seed to Series D (appropriate stage)
    'team_quality': 10,          # Technical founders, co-founder team
    'traction': 20,              # Revenue, customers, growth metrics
    'investor_backing': 15,      # Quality and presence of investors
    'exit_potential': 10,        # High/medium/low exit potential
}

# Endeavor target criteria
TARGET_FOUNDING_YEAR_MIN = 2020  # Ideally founded since 2020
TARGET_FOUNDING_YEAR_MAX = 2025  # Current year
FUNDING_YEAR_MIN = 2019          # Funded in last 5 years (2019-2024)
PREFERRED_STAGES = ['seed', 'series-a', 'series-b', 'series-c', 'series-d']
DEEPTECH_KEYWORDS = ['ai', 'ml', 'robotics', 'biotech', 'cleantech', 'hardware', 'deeptech',
                     'artificial intelligence', 'machine learning', 'deep learning']


# GENERAL SETTINGS
# ================

# Enable verbose logging
VERBOSE = True

# Save intermediate results after each stage
SAVE_INTERMEDIATE_RESULTS = True

# Create backup of results before overwriting
CREATE_BACKUPS = False

# Enable sponsor info searches (searches news/press releases for each festival)
# This adds time but finds sponsor info not on festival websites
ENABLE_SPONSOR_INFO_SEARCHES = True
