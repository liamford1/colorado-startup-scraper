"""
Data schema and models for investment/startup research project
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import csv
import json


@dataclass
class Investor:
    """Individual investor/partner information"""
    name: str
    normalized_name: str = ""  # Parent company name
    tier: str = ""  # Lead, Series A/B/C, Angel, Strategic, etc.
    tier_rank: int = 0  # Normalized 1-10 scale
    sector: str = ""  # Tech, Finance, Healthcare, etc.
    investor_type: str = "vc"  # vc, angel, strategic, corporate
    evidence_url: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Company:
    """Complete company/startup information"""
    # Basic Info
    name: str
    city: str
    state: str
    year: int  # Year founded
    status: str = "active"  # active, acquired, defunct

    # Business Model & Structure
    business_model: str = ""  # SaaS, marketplace, hardware, etc.
    market_focus: str = ""  # B2B, B2C, B2B2C
    product_categories: List[str] = field(default_factory=list)
    is_remote: bool = False
    has_physical_presence: bool = False

    # Industry & Technology
    industries: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    target_market: str = ""
    value_proposition: str = ""

    # Company Stage & Structure
    company_stage: str = ""  # pre-seed, seed, series-a, series-b, growth, etc.
    company_structure: str = ""  # C-corp, LLC, B-corp, etc.

    # Team & Culture
    founder_names: List[str] = field(default_factory=list)  # CRITICAL: Founder names
    ceo_name: str = ""  # CRITICAL: Current CEO name
    founder_count: int = 0
    team_size: int = 0
    has_technical_founders: bool = False
    culture_keywords: List[str] = field(default_factory=list)

    # Traction & Metrics
    revenue_range: str = ""  # e.g., "$1M-5M ARR"
    growth_rate: str = ""
    customer_count: int = 0
    has_revenue: bool = False

    # Funding & Investment
    investors: List[Investor] = field(default_factory=list)
    has_public_investors: bool = False
    total_funding_raised: str = ""
    last_funding_round: str = ""
    investor_tier_count: int = 0

    # Valuation & Exit Potential
    estimated_valuation: str = ""
    exit_potential: str = ""  # high, medium, low

    # Evidence & Sources
    official_website: str = ""
    evidence_links: List[str] = field(default_factory=list)
    data_collected_date: str = field(default_factory=lambda: datetime.now().isoformat())

    # Scoring
    fit_score: int = 0
    fit_rationale: str = ""
    score_breakdown: dict = field(default_factory=dict)

    # Notes
    notes: str = ""

    def calculate_fit_score(self) -> int:
        """
        Calculate fit score based on investment criteria (0-100)
        Customize these weights based on your specific investment thesis
        """
        score = 0
        breakdown = {}

        # Business model clarity & scalability (0-20)
        business_score = 0
        scalable_models = ["saas", "marketplace", "platform", "subscription"]
        if any(model in self.business_model.lower() for model in scalable_models):
            business_score = 20
        elif self.business_model:
            business_score = 10
        score += business_score
        breakdown["business_model"] = business_score

        # Market & industry alignment (0-15)
        market_score = 0
        if len(self.industries) >= 2:  # Multiple industry exposure
            market_score = 15
        elif len(self.industries) >= 1:
            market_score = 8
        score += market_score
        breakdown["market_alignment"] = market_score

        # Company stage & maturity (0-10)
        stage_score = 0
        target_stages = ["seed", "series-a", "series-b"]
        if any(stage in self.company_stage.lower() for stage in target_stages):
            stage_score = 10
        score += stage_score
        breakdown["stage_fit"] = stage_score

        # Team & founder quality (0-10)
        team_score = 0
        if self.has_technical_founders:
            team_score += 5
        if self.founder_count >= 2:  # Co-founder team
            team_score += 5
        score += team_score
        breakdown["team_quality"] = team_score

        # Traction & validation (0-20)
        traction_score = 0
        if self.has_revenue:
            traction_score += 10
        if self.customer_count > 10:
            traction_score += 5
        if self.growth_rate and "%" in self.growth_rate:
            traction_score += 5
        score += traction_score
        breakdown["traction"] = traction_score

        # Investor quality & backing (0-15)
        investor_score = 0
        if len(self.investors) > 0:
            investor_score += 5
        if self.has_public_investors:
            investor_score += 5
        if self.total_funding_raised:
            investor_score += 5
        score += investor_score
        breakdown["investor_backing"] = investor_score

        # Exit potential (0-10)
        exit_score = 0
        if self.exit_potential == "high":
            exit_score = 10
        elif self.exit_potential == "medium":
            exit_score = 5
        score += exit_score
        breakdown["exit_potential"] = exit_score

        self.fit_score = score
        self.score_breakdown = breakdown
        return score

    def to_dict(self):
        """Convert to dictionary for CSV export"""
        data = asdict(self)
        # Convert lists to JSON strings for CSV
        data['founder_names'] = json.dumps(data['founder_names'])
        data['product_categories'] = json.dumps(data['product_categories'])
        data['industries'] = json.dumps(data['industries'])
        data['technologies'] = json.dumps(data['technologies'])
        data['culture_keywords'] = json.dumps(data['culture_keywords'])
        data['evidence_links'] = json.dumps(data['evidence_links'])
        data['score_breakdown'] = json.dumps(data['score_breakdown'])
        # Convert investors to count
        data['investor_count'] = len(self.investors)
        data.pop('investors')  # Remove investors list from main CSV
        return data

    def to_csv_row(self) -> dict:
        """Prepare company data for CSV export"""
        return self.to_dict()


def save_companies_to_csv(companies: List[Company], filename: str):
    """Save companies to CSV file"""
    if not companies:
        print("No companies to save")
        return

    fieldnames = list(companies[0].to_dict().keys())

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for company in companies:
            writer.writerow(company.to_csv_row())

    print(f"Saved {len(companies)} companies to {filename}")


def save_investors_to_csv(companies: List[Company], filename: str):
    """Save all investors from all companies to CSV"""
    investors_data = []

    for company in companies:
        for investor in company.investors:
            investors_data.append({
                'company_name': company.name,
                'company_year': company.year,
                'investor_name': investor.name,
                'normalized_name': investor.normalized_name,
                'tier': investor.tier,
                'tier_rank': investor.tier_rank,
                'sector': investor.sector,
                'investor_type': investor.investor_type,
                'evidence_url': investor.evidence_url
            })

    if not investors_data:
        print("No investors to save")
        return

    fieldnames = list(investors_data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(investors_data)

    print(f"Saved {len(investors_data)} investor records to {filename}")
