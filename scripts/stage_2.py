"""
Stage 2: Website Scraper & Content Collection
Scrapes company websites and collects PDFs, investor pages, etc.
"""
import os
import json
import csv
import requests
import warnings
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from openai import OpenAI

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

load_dotenv('../.env')

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class CompanyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.timeout = 10
        self.openai_client = openai_client

    def _extract_structured_info(self, scraped_data: Dict) -> Dict:
        """Use AI to extract structured information from scraped content"""
        if not self.openai_client:
            return {
                'description': '',
                'founders': '',
                'funding_info': '',
                'location': '',
                'industry': ''
            }

        # Combine all content
        all_content = f"{scraped_data.get('main_content', '')} {scraped_data.get('about_content', '')}"

        # Add investor page content
        for page in scraped_data.get('investor_page_content', []):
            all_content += f" {page.get('content', '')}"

        # Limit content for API
        all_content = all_content[:20000]

        if len(all_content) < 100:
            return {
                'description': 'No content found',
                'founders': '',
                'funding_info': '',
                'location': '',
                'industry': ''
            }

        prompt = f"""Extract the following information from this company website content. Be concise and specific.

Content:
{all_content}

Extract:
1. Company Description: What does the company do? (1-2 sentences)
2. Founders: Names of founders/co-founders
3. Funding Info: Recent funding rounds (Series A/B/C, amounts, investors, year)
4. Location: City, State/Country where headquartered
5. Industry: Industry/sector (e.g., SaaS, FinTech, Healthcare)

Format your response as JSON:
{{
  "description": "brief description",
  "founders": "founder names or 'Not found'",
  "funding_info": "funding rounds and investors or 'Not found'",
  "location": "city, state or 'Not found'",
  "industry": "industry/sector or 'Not found'"
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a research assistant that extracts structured information from company websites. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            extracted = json.loads(response.choices[0].message.content)
            return extracted

        except Exception as e:
            print(f"    AI extraction error: {e}")
            return {
                'description': 'Extraction failed',
                'founders': '',
                'funding_info': '',
                'location': '',
                'industry': ''
            }

    def _save_progress_csv(self, scraped_data: List[Dict], filename: str):
        """Save scraping progress - just basic info, no AI extraction"""
        if not scraped_data:
            return

        try:
            # Simple CSV - just what we scraped
            fieldnames = [
                'company_name', 'url', 'snippet', 'social_links',
                'content_length', 'scrape_method', 'success'
            ]

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for data in scraped_data:
                    # Extract candidate info
                    candidate = data.get('candidate_info', {})

                    # Format social links
                    social_links = data.get('social_links', {})
                    social_str = ', '.join([f"{k}: {v}" for k, v in social_links.items()])

                    # Calculate total content length
                    content_length = len(data.get('main_content', '')) + len(data.get('about_content', ''))

                    writer.writerow({
                        'company_name': candidate.get('title', 'Unknown'),
                        'url': data.get('url', ''),
                        'snippet': candidate.get('snippet', '')[:300],  # From Phase 1
                        'social_links': social_str[:500],
                        'content_length': content_length,
                        'scrape_method': data.get('scrape_method', 'requests'),
                        'success': 'Yes' if data.get('success') else 'No'
                    })

        except Exception as e:
            print(f"  Warning: Could not save progress CSV: {e}")

    def _scrape_with_playwright(self, url: str) -> tuple[str, BeautifulSoup]:
        """Scrape using Playwright for JavaScript-rendered sites"""
        try:
            print(f"    → Using Playwright (JavaScript rendering)...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    ignore_https_errors=True
                )
                page = context.new_page()

                # Navigate and wait for content to load
                page.goto(url, timeout=15000, wait_until='networkidle')

                # Wait a bit more for dynamic content
                page.wait_for_timeout(2000)

                # Get the rendered HTML
                html = page.content()
                browser.close()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                return html, soup

        except Exception as e:
            print(f"    Playwright error: {e}")
            return None, None

    def scrape_website(self, url: str, use_playwright: bool = False) -> Dict:
        """
        Scrape a company website and collect relevant information
        Falls back to Playwright if content is minimal
        """
        result = {
            'url': url,
            'success': False,
            'main_content': '',
            'investor_pages': [],
            'pdfs': [],
            'about_content': '',
            'about_page_url': '',
            'contact_info': {},
            'social_links': {},
            'scrape_method': 'requests',
            'error': None
        }

        try:
            print(f"  Scraping: {url}")

            # Try standard requests first (unless playwright explicitly requested)
            if not use_playwright:
                response = self.session.get(url, timeout=self.timeout, verify=False)
                response.raise_for_status()
                html = response.content
                soup = BeautifulSoup(html, 'html.parser')
                result['scrape_method'] = 'requests'
            else:
                html, soup = self._scrape_with_playwright(url)
                if soup is None:
                    raise Exception("Playwright scraping failed")
                result['scrape_method'] = 'playwright'

            # Extract main text content
            result['main_content'] = self._extract_text_content(soup)

            # If content is very short, retry with Playwright
            if len(result['main_content']) < 500 and not use_playwright:
                print(f"    ⚠️  Low content ({len(result['main_content'])} chars), retrying with Playwright...")
                html, soup = self._scrape_with_playwright(url)
                if soup:
                    result['main_content'] = self._extract_text_content(soup)
                    result['scrape_method'] = 'playwright'

            # Find investor-related pages
            result['investor_pages'] = self._find_investor_pages(soup, url)

            # Find PDFs (pitch decks, investor materials, etc.)
            result['pdfs'] = self._find_pdfs(soup, url)

            # Look for about/contact pages
            about_data = self._find_about_content_with_url(soup, url)
            result['about_content'] = about_data['content']
            result['about_page_url'] = about_data['url']

            # Extract social media links
            result['social_links'] = self._extract_social_links(soup)

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            print(f"  Error scraping {url}: {e}")

        return result

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()

        # Get text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        # Limit length
        return text[:50000]  # Limit to ~50KB

    def _find_investor_pages(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Find links to investor/partner/team/funding pages"""
        investor_pages = []

        # Expanded keywords for better detection
        investor_keywords = [
            'investor', 'funding', 'partner', 'about', 'team', 'careers',
            'founder', 'leadership', 'company', 'who we are', 'our story',
            'press', 'news', 'newsroom', 'media', 'blog',
            'series a', 'series b', 'series c', 'venture', 'capital',
            'raise', 'investment', 'backed by', 'portfolio'
        ]

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().lower().strip()

            # Check if link text or URL contains investor keywords
            if any(keyword in text or keyword in href.lower() for keyword in investor_keywords):
                full_url = urljoin(base_url, href)

                # Avoid duplicates and external domains
                if self._is_same_domain(base_url, full_url):
                    # Prioritize certain keywords
                    priority = 'high' if any(kw in text or kw in href.lower()
                                            for kw in ['investor', 'funding', 'founder', 'team', 'about', 'press', 'news']) else 'normal'

                    investor_pages.append({
                        'url': full_url,
                        'link_text': link.get_text().strip(),
                        'type': 'investor_page',
                        'priority': priority
                    })

        # Deduplicate
        seen = set()
        unique_pages = []
        for page in investor_pages:
            if page['url'] not in seen:
                seen.add(page['url'])
                unique_pages.append(page)

        # Sort by priority (high priority first)
        unique_pages.sort(key=lambda x: 0 if x.get('priority') == 'high' else 1)

        return unique_pages[:15]  # Increased limit to 15

    def _find_pdfs(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Find PDF links (pitch decks, investor materials, etc.)"""
        pdfs = []

        # Find all links to PDFs
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')

            if '.pdf' in href.lower() or 'issuu.com' in href.lower():
                full_url = urljoin(base_url, href)
                text = link.get_text().strip()

                # Prioritize investor-related PDFs
                investor_terms = ['investor', 'pitch', 'deck', 'funding', 'overview']
                priority = 'high' if any(term in text.lower() or term in href.lower()
                                        for term in investor_terms) else 'normal'

                pdfs.append({
                    'url': full_url,
                    'link_text': text,
                    'priority': priority
                })

        # Sort by priority
        pdfs.sort(key=lambda x: 0 if x['priority'] == 'high' else 1)

        return pdfs[:15]  # Limit to top 15

    def _find_about_content_with_url(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Try to find and scrape about/company/team page, return content and URL"""
        about_keywords = [
            'about', 'mission', 'history', 'our story', 'company',
            'who we are', 'our team', 'leadership', 'founders'
        ]

        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower().strip()

            if any(keyword in href or keyword in text for keyword in about_keywords):
                try:
                    full_url = urljoin(base_url, link.get('href'))
                    if self._is_same_domain(base_url, full_url):
                        response = self.session.get(full_url, timeout=self.timeout, verify=False)
                        about_soup = BeautifulSoup(response.content, 'html.parser')
                        content = self._extract_text_content(about_soup)
                        if len(content) > 200:  # Only return if meaningful content
                            return {
                                'content': content[:15000],  # Increased limit to 15KB
                                'url': full_url
                            }
                except:
                    pass

        return {'content': '', 'url': ''}

    def _extract_social_links(self, soup: BeautifulSoup) -> Dict:
        """Extract social media links"""
        social = {}
        social_platforms = {
            'facebook.com': 'facebook',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'instagram.com': 'instagram',
            'linkedin.com': 'linkedin',
            'youtube.com': 'youtube',
            'crunchbase.com': 'crunchbase'
        }

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for domain, platform in social_platforms.items():
                if domain in href:
                    social[platform] = href
                    break

        return social

    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain"""
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except:
            return False

    def scrape_investor_pages(self, investor_pages: List[Dict]) -> List[Dict]:
        """
        Scrape individual investor pages for detailed information
        """
        results = []

        for page in investor_pages[:8]:  # Increased to top 8 investor pages
            try:
                print(f"    Scraping investor page: {page['url']}")
                response = self.session.get(page['url'], timeout=self.timeout, verify=False)
                soup = BeautifulSoup(response.content, 'html.parser')

                content = self._extract_text_content(soup)

                results.append({
                    'url': page['url'],
                    'content': content,
                    'pdfs': self._find_pdfs(soup, page['url'])
                })

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"    Error scraping investor page: {e}")

        return results


def main():
    """Run web scraping on discovered candidates"""
    print("=" * 60)
    print("STAGE 2: WEB SCRAPING & CONTENT COLLECTION")
    print("=" * 60)

    # Load candidates from Stage 1
    try:
        with open('../outputs/stage_1.json', 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print("Error: stage_1.json not found. Run stage_1.py first.")
        return

    # Load existing scraped data if it exists
    output_file = '../outputs/stage_2.json'
    scraped_data = []
    scraped_urls = set()

    if os.path.exists(output_file):
        print(f"\n📁 Found existing scraped data file")
        with open(output_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        scraped_urls = {d['url'] for d in scraped_data}
        print(f"   Loaded {len(scraped_data)} existing scraped companies")

    scraper = CompanyScraper()

    # Check config for limit, otherwise process all
    try:
        from config import MAX_FESTIVALS_TO_SCRAPE  # Keeping config var name for now
        if MAX_FESTIVALS_TO_SCRAPE is None or MAX_FESTIVALS_TO_SCRAPE == 0:
            limit = None  # Process all
        else:
            limit = MAX_FESTIVALS_TO_SCRAPE
    except ImportError:
        limit = None  # Process all if no config

    candidates_to_process = candidates[:limit] if limit is not None else candidates

    # Filter out already scraped candidates
    new_candidates = [c for c in candidates_to_process if c['url'] not in scraped_urls]
    print(f"\n🔍 Found {len(new_candidates)} NEW companies to scrape (skipping {len(candidates_to_process) - len(new_candidates)} already scraped)")

    if not new_candidates:
        print("⚠️  No new companies to scrape! All candidates have already been processed.")
        return scraped_data

    # CSV progress file
    csv_progress_file = '../outputs/stage_2_progress.csv'

    for i, candidate in enumerate(new_candidates, 1):
        print(f"\n[{i}/{len(new_candidates)}] Processing: {candidate['title']}")

        # Scrape main website
        result = scraper.scrape_website(candidate['url'])
        result['candidate_info'] = candidate

        # If investor pages found, scrape them too
        if result['investor_pages']:
            print(f"  Found {len(result['investor_pages'])} investor pages")
            result['investor_page_content'] = scraper.scrape_investor_pages(result['investor_pages'])

        # If investor info URLs found from news/press releases, scrape those too
        investor_info_urls = candidate.get('investor_info_urls', [])
        if investor_info_urls:
            print(f"  Found {len(investor_info_urls)} investor info sources (news/press releases)")
            result['investor_info_content'] = []
            for info_url in investor_info_urls[:3]:  # Limit to top 3 to avoid too many requests
                try:
                    print(f"    Scraping investor info: {info_url[:60]}...")
                    info_result = scraper.scrape_website(info_url)
                    if info_result['success']:
                        result['investor_info_content'].append({
                            'url': info_url,
                            'content': info_result['main_content'][:10000]  # Limit content size
                        })
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"    Error scraping investor info URL: {e}")
                    continue

        # No AI extraction needed - Phase 3 will handle that
        scraped_data.append(result)

        # Save progress to BOTH CSV and JSON after each company
        scraper._save_progress_csv(scraped_data, csv_progress_file)

        # Also save JSON incrementally so content isn't lost if killed
        json_progress_file = '../outputs/stage_2.json'
        with open(json_progress_file, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Progress saved ({i}/{len(new_candidates)} new companies)")

        time.sleep(2)  # Rate limiting

    # Save final results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Scraping complete!")
    print(f"✓ Total scraped: {len(scraped_data)} websites ({len(scraped_data) - len(new_candidates)} existing + {len(new_candidates)} new)")
    print(f"✓ Results saved to {output_file}")
    print(f"✓ Progress CSV saved to {csv_progress_file}")

    # Summary stats
    successful = sum(1 for d in scraped_data if d['success'])
    with_investors = sum(1 for d in scraped_data if d['investor_pages'])
    with_pdfs = sum(1 for d in scraped_data if d['pdfs'])

    print(f"\n  - Successful scrapes: {successful}")
    print(f"  - Sites with investor pages: {with_investors}")
    print(f"  - Sites with PDFs: {with_pdfs}")

    return scraped_data


if __name__ == '__main__':
    main()
