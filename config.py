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

# Custom search queries (modify to refine your search)
# Note: Perplexity works better with natural language queries
# Focus: Colorado startups, VCs, and companies for Endeavor criteria
CUSTOM_SEARCH_QUERIES = [
    # ===== COLORADO STARTUPS LEADERBOARD =====
    "Find the top 100 companies on Colorado Startups leaderboard at coloradostartups.org",
    "Find the top 100 fastest growing companies on Colorado Startups leaderboard",
    "Find companies featured on coloradostartups.org leaderboard with founders and funding",

    # ===== ENDEAVOR COLORADO PORTFOLIO =====
    "Find current Endeavor Colorado entrepreneur companies and their founders",
    "Find companies selected by Endeavor Colorado with founder names and details",
    "Find Endeavor Colorado portfolio companies at endeavorcolorado.org",

    # ===== DEEPTECH COLORADO COMPANIES =====
    "Find DeepTech startups in Colorado with venture capital funding founded since 2020",
    "Find Colorado DeepTech companies with Series A B C funding rounds in the last 5 years",
    "Find Colorado startups in AI, robotics, biotech, cleantech with rapid growth and VC backing",
    "Find Colorado hardware and software technology companies with technical founders",

    # ===== FUNDED COLORADO STARTUPS (Last 5 years) =====
    "Find Colorado startups that received seed funding in the last 5 years",
    "Find Colorado companies that raised Series A funding since 2020",
    "Find Colorado companies that raised Series B or Series C funding in the last 5 years",
    "Find recently funded Colorado startups with headquarters in Denver, Boulder, Fort Collins",
    "Find Colorado startups founded since 2020 with venture capital backing",

    # ===== COLORADO STARTUP ECOSYSTEMS BY CITY =====
    "Find fast-growing startups in Boulder Colorado with founder names and investors",
    "Find Denver Colorado tech startups founded since 2020 with VC funding",
    "Find Fort Collins Colorado startups with Series A or seed funding",
    "Find Colorado Springs startups with technical founders and investor backing",
    "Find Longmont Colorado startups with rapid growth and funding rounds",

    # ===== COLORADO VCS AND THEIR PORTFOLIOS =====
    "Find venture capital firms based in Colorado and their portfolio companies",
    "Find Colorado VCs with investments in DeepTech and high-growth startups",
    "Find Denver Boulder venture capital firms and their portfolio company CEOs",
    "Find Colorado venture capital investors and the companies they've funded",
    "Find list of Colorado VC firms with portfolio companies and founder information",

    # ===== SPECIFIC VC SEARCHES =====
    "Find Boulder Ventures Colorado portfolio companies with founders and CEOs",
    "Find Access Venture Partners Colorado portfolio companies",
    "Find Foundry Group Colorado portfolio companies with founder details",
    "Find Techstars Boulder portfolio companies and their founders",
    "Find Ridgeline Ventures Colorado investments",
    "Find Blackhorn Ventures Colorado portfolio companies",

    # ===== PRIVATELY HELD HIGH-GROWTH COMPANIES =====
    "Find privately held Colorado companies with rapid revenue growth since 2020",
    "Find Colorado private companies with strong growth metrics and VC backing",
    "Find Colorado startups that are still private and raising funding rounds",

    # ===== FOUNDER AND CEO INFORMATION =====
    "Find Colorado startup founders based in Colorado with company information",
    "Find CEOs of Colorado tech companies with venture capital backing",
    "Find technical founders in Colorado running high-growth startups",
    "Find Colorado entrepreneur profiles with company names and funding details",

    # ===== INDUSTRY-SPECIFIC COLORADO SEARCHES =====
    "Find Colorado SaaS companies with B2B models and VC funding",
    "Find Colorado fintech startups founded since 2020",
    "Find Colorado healthcare tech companies with Series A funding",
    "Find Colorado climate tech and sustainability startups with investors",
    "Find Colorado enterprise software companies with rapid growth",
    "Find Colorado AI and machine learning startups with funding",

    # ===== NEWS AND PRESS RELEASE SEARCHES =====
    "Find news articles about Colorado startup funding rounds in 2024 2023 2022",
    "Find press releases about Colorado companies raising Series A B C funding",
    "Find Colorado startup funding announcements with investor and founder names",
    "Find articles about Colorado ventures and their portfolio companies",
]

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
