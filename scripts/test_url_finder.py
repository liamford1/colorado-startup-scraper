"""
Test the URL finder with a few companies
"""
from stage_1b import URLFinder

finder = URLFinder()

# Test companies
test_companies = [
    {
        "name": "JumpCloud",
        "description": "Denver, Colorado-based software company providing directory-as-a-service platform"
    },
    {
        "name": "Ibotta",
        "description": "Colorado-based mobile technology company providing cashback rewards"
    },
    {
        "name": "SonderMind",
        "description": "Denver-based mental health company connecting patients with therapists"
    },
]

print("Testing URL Finder with 3 companies:\n")
print("=" * 60)

for company in test_companies:
    print(f"\nSearching for: {company['name']}")
    print(f"Description: {company['description'][:80]}...")

    url = finder.find_url(company['name'], company['description'])

    if url:
        print(f"✓ Found: {url}")
    else:
        print(f"✗ Not found")

    import time
    time.sleep(2)  # Rate limiting

print("\n" + "=" * 60)
print("Test complete!")
