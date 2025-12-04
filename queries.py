"""
Search Queries for Colorado Startup Discovery
==============================================
This file contains all search queries used in Stage 1 to discover Colorado companies.
Organized by category for easier management.
"""

# ===== COLORADO STARTUP LEADERBOARDS & DIRECTORIES =====
LEADERBOARD_QUERIES = [
    "Find Colorado tech startups that raised venture capital funding recently",
    "Find Colorado companies with Series A funding rounds in recent years",
    "Find Colorado software companies with venture capital backing",
    "Find emerging Colorado tech companies with venture funding",
    "Find Colorado startups that raised seed funding in the last few years",
    "Find Techstars Boulder alumni companies with venture funding",
]

# ===== ENDEAVOR COLORADO PORTFOLIO =====
ENDEAVOR_QUERIES = [
    "Find Endeavor Colorado entrepreneur companies with founder information",
    "Find companies selected by Endeavor Colorado in recent years",
    "Find high-growth Endeavor Colorado portfolio companies",
]

# ===== EARLY STAGE COLORADO STARTUPS (SEED & PRE-SEED) =====
EARLY_STAGE_QUERIES = [
    # Seed & Pre-Seed Focus
    "Find Colorado pre-seed startups founded in 2023 2024 with angel investors",
    "Find Colorado seed stage companies that raised funding in the last 2 years",
    "Find early-stage Colorado startups in Y Combinator or Techstars programs",
    "Find Colorado startups that graduated from accelerators in 2023 2024",
    "Find newly founded Colorado tech companies with less than 1 million in funding",
    "Find Colorado startups that raised less than 5 million in seed funding",

    # Recent Founding Focus (2022-2024)
    "Find Colorado startups founded in 2024 with technical founders",
    "Find Colorado companies founded in 2023 with seed funding",
    "Find Colorado startups founded in 2022 with recent funding rounds",
    "Find newly launched Colorado tech companies with MVP or beta products",

    # Bootstrapped & Early Revenue
    "Find bootstrapped Colorado startups with early revenue and rapid growth",
    "Find Colorado startups with less than 10 employees and VC interest",
    "Find Colorado tech companies in early growth stage with product-market fit",
    "Find pre-revenue Colorado startups with strong technical teams",

    # Angel & Micro VC Backed
    "Find Colorado startups backed by angel investors and micro VCs",
    "Find Colorado companies that received angel funding in 2023 2024",
    "Find early-stage Colorado startups with backing from Colorado angel networks",
    "Find Colorado startups funded by Rockies Venture Club members",
]

# ===== FUNDED COLORADO STARTUPS (LAST 5 YEARS) =====
FUNDED_QUERIES = [
    "Find Colorado startups that received seed funding in the last 5 years",
    "Find Colorado companies that raised Series A funding since 2020",
    "Find Colorado companies that raised Series B or Series C funding in the last 5 years",
    "Find recently funded Colorado startups with headquarters in Denver, Boulder, Fort Collins",
    "Find Colorado startups founded since 2020 with venture capital backing",
    "Find Colorado companies that announced funding rounds in 2024",
    "Find Colorado startups that closed funding rounds in 2023",
]

# ===== DEEPTECH COLORADO COMPANIES =====
DEEPTECH_QUERIES = [
    "Find DeepTech startups in Colorado with venture capital funding founded since 2020",
    "Find Colorado DeepTech companies with Series A B C funding rounds in the last 5 years",
    "Find Colorado startups in AI, robotics, biotech, cleantech with rapid growth and VC backing",
    "Find Colorado hardware and software technology companies with technical founders",
    "Find Colorado AI and machine learning startups with funding",
    "Find Colorado quantum computing or advanced computing startups",
    "Find Colorado aerospace and aviation tech startups with funding",
]

# ===== COLORADO STARTUP ECOSYSTEMS BY CITY =====
CITY_QUERIES = [
    "Find fast-growing startups in Boulder Colorado with founder names and investors",
    "Find Denver Colorado tech startups founded since 2020 with VC funding",
    "Find Fort Collins Colorado startups with Series A or seed funding",
    "Find Colorado Springs startups with technical founders and investor backing",
    "Find Longmont Colorado startups with rapid growth and funding rounds",
    "Find Aurora Colorado tech companies with funding",
    "Find Broomfield Colorado startups with venture backing",
]

# ===== COLORADO VCS AND THEIR PORTFOLIOS =====
VC_PORTFOLIO_QUERIES = [
    "Find venture capital firms based in Colorado and their portfolio companies",
    "Find Colorado VCs with investments in DeepTech and high-growth startups",
    "Find Denver Boulder venture capital firms and their portfolio company CEOs",
    "Find Colorado venture capital investors and the companies they've funded",
    "Find list of Colorado VC firms with portfolio companies and founder information",
]

# ===== SPECIFIC VC PORTFOLIO SEARCHES =====
SPECIFIC_VC_QUERIES = [
    "Find Boulder Ventures Colorado portfolio companies with founders and CEOs",
    "Find Access Venture Partners Colorado portfolio companies",
    "Find Foundry Group Colorado portfolio companies with founder details",
    "Find Techstars Boulder portfolio companies and their founders",
    "Find Ridgeline Ventures Colorado investments",
    "Find Blackhorn Ventures Colorado portfolio companies",
    "Find Galvanize Ventures Colorado portfolio companies",
    "Find Grotech Ventures Colorado investments",
    "Find Parkview Ventures Colorado portfolio companies",
    "Find V1 Ventures Colorado portfolio companies",
]

# ===== PRIVATELY HELD HIGH-GROWTH COMPANIES =====
GROWTH_QUERIES = [
    "Find privately held Colorado companies with rapid revenue growth since 2020",
    "Find Colorado private companies with strong growth metrics and VC backing",
    "Find Colorado startups that are still private and raising funding rounds",
    "Find Colorado unicorn and near-unicorn startups that are still private",
    "Find Colorado high-growth companies with 100+ employees still private",
]

# ===== FOUNDER AND CEO INFORMATION =====
FOUNDER_QUERIES = [
    "Find Colorado startup founders based in Colorado with company information",
    "Find CEOs of Colorado tech companies with venture capital backing",
    "Find technical founders in Colorado running high-growth startups",
    "Find Colorado entrepreneur profiles with company names and funding details",
    "Find Colorado founders who graduated from top accelerators",
    "Find serial entrepreneurs in Colorado with new startups",
]

# ===== INDUSTRY-SPECIFIC COLORADO SEARCHES =====
INDUSTRY_QUERIES = [
    # Software & SaaS
    "Find Colorado SaaS companies with B2B models and VC funding",
    "Find Colorado enterprise software companies with rapid growth",
    "Find Colorado B2B software startups founded since 2020",
    "Find Colorado developer tools and infrastructure startups",

    # Fintech & Financial Services
    "Find Colorado fintech startups founded since 2020",
    "Find Colorado payments and financial technology companies with funding",
    "Find Colorado cryptocurrency and blockchain startups",
    "Find Colorado insurtech companies with venture backing",

    # Healthcare & Life Sciences
    "Find Colorado healthcare tech companies with Series A funding",
    "Find Colorado digital health startups with VC backing",
    "Find Colorado biotech companies founded since 2020",
    "Find Colorado medtech and medical device startups",
    "Find Colorado telemedicine and telehealth startups",

    # Climate & Sustainability
    "Find Colorado climate tech and sustainability startups with investors",
    "Find Colorado renewable energy startups with funding",
    "Find Colorado cleantech companies with venture backing",
    "Find Colorado carbon capture and climate solution startups",

    # Consumer & E-commerce
    "Find Colorado direct-to-consumer brands with VC funding",
    "Find Colorado e-commerce startups with rapid growth",
    "Find Colorado food and beverage tech startups",

    # Manufacturing & Hardware
    "Find Colorado manufacturing tech and Industry 4.0 startups",
    "Find Colorado robotics and automation companies with funding",
    "Find Colorado hardware startups with venture backing",

    # Other Tech
    "Find Colorado cybersecurity startups with funding",
    "Find Colorado edtech and education technology companies",
    "Find Colorado gaming and entertainment tech startups",
    "Find Colorado space tech and satellite companies in Colorado",
]

# ===== NEWS AND PRESS RELEASE SEARCHES =====
NEWS_QUERIES = [
    "Find news articles about Colorado startup funding rounds in 2024 2023 2022",
    "Find press releases about Colorado companies raising Series A B C funding",
    "Find Colorado startup funding announcements with investor and founder names",
    "Find articles about Colorado ventures and their portfolio companies",
    "Find TechCrunch articles about Colorado startup funding",
    "Find Denver Business Journal articles about Colorado startup funding",
    "Find Built In Colorado news about startup funding rounds",
]

# ===== UNIVERSITY SPINOUTS & RESEARCH =====
UNIVERSITY_QUERIES = [
    "Find University of Colorado Boulder spinout companies with VC funding",
    "Find Colorado State University startup companies with funding",
    "Find Colorado School of Mines spinout companies",
    "Find university research commercialization startups in Colorado",
    "Find SBIR STTR grant recipients in Colorado with follow-on VC funding",
]

# ===== REMOTE-FIRST COLORADO COMPANIES =====
REMOTE_QUERIES = [
    "Find remote-first companies headquartered in Colorado with funding",
    "Find distributed Colorado startups with global teams and VC backing",
]

# ===== ALL QUERIES COMBINED =====
# This is what gets imported by other modules
ALL_QUERIES = (
    LEADERBOARD_QUERIES +
    ENDEAVOR_QUERIES +
    EARLY_STAGE_QUERIES +
    FUNDED_QUERIES +
    DEEPTECH_QUERIES +
    CITY_QUERIES +
    VC_PORTFOLIO_QUERIES +
    SPECIFIC_VC_QUERIES +
    GROWTH_QUERIES +
    FOUNDER_QUERIES +
    INDUSTRY_QUERIES +
    NEWS_QUERIES +
    UNIVERSITY_QUERIES +
    REMOTE_QUERIES
)

# You can also create custom query sets by combining categories:
EARLY_STAGE_FOCUS = EARLY_STAGE_QUERIES + LEADERBOARD_QUERIES + SPECIFIC_VC_QUERIES
DEEPTECH_FOCUS = DEEPTECH_QUERIES + UNIVERSITY_QUERIES + INDUSTRY_QUERIES[:10]
NEWS_FOCUS = NEWS_QUERIES + FUNDED_QUERIES

# Print stats when run directly
if __name__ == "__main__":
    print(f"Total queries available: {len(ALL_QUERIES)}")
    print(f"\nBreakdown by category:")
    print(f"  Leaderboards: {len(LEADERBOARD_QUERIES)}")
    print(f"  Endeavor: {len(ENDEAVOR_QUERIES)}")
    print(f"  Early Stage: {len(EARLY_STAGE_QUERIES)}")
    print(f"  Funded: {len(FUNDED_QUERIES)}")
    print(f"  DeepTech: {len(DEEPTECH_QUERIES)}")
    print(f"  City-based: {len(CITY_QUERIES)}")
    print(f"  VC Portfolios: {len(VC_PORTFOLIO_QUERIES)}")
    print(f"  Specific VCs: {len(SPECIFIC_VC_QUERIES)}")
    print(f"  High-Growth: {len(GROWTH_QUERIES)}")
    print(f"  Founders: {len(FOUNDER_QUERIES)}")
    print(f"  Industry-Specific: {len(INDUSTRY_QUERIES)}")
    print(f"  News: {len(NEWS_QUERIES)}")
    print(f"  University Spinouts: {len(UNIVERSITY_QUERIES)}")
    print(f"  Remote-First: {len(REMOTE_QUERIES)}")
