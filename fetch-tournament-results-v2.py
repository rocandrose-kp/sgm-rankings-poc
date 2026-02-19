import json
import requests
import re
from urllib.parse import urlparse
import time

def load_tournament_list(file_path):
    """Load the tournament list from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_tournament_id_from_page(website_url):
    """
    Extract tournament ID by looking for specific patterns in the page source.
    Focus on finding the actual tournament-specific ID, not generic site IDs.
    """
    try:
        parsed = urlparse(website_url)
        
        # Try the results page which is more likely to have the tournament ID
        urls_to_try = [
            f"{website_url.rstrip('/')}/2026/result/",
            f"{website_url.rstrip('/')}/2025/result/",
            website_url,
        ]
        
        for url in urls_to_try:
            try:
                print(f"        Checking: {url}")
                response = requests.get(url, timeout=10, allow_redirects=True)
                response.raise_for_status()
                
                # Look for REST API calls in the page that include tournamentId
                api_call_pattern = r'/rest/results_api/call\?[^"\']*tournamentId=(\d{8,})'
                matches = re.findall(api_call_pattern, response.text)
                if matches:
                    # Get unique IDs
                    unique_ids = list(set(matches))
                    if len(unique_ids) == 1:
                        print(f"        Found via API call pattern: {unique_ids[0]}")
                        return unique_ids[0]
                    elif len(unique_ids) > 1:
                        # Multiple IDs found, use the most common one
                        from collections import Counter
                        most_common = Counter(matches).most_common(1)[0][0]
                        print(f"        Found multiple IDs, using most common: {most_common}")
                        return most_common
                
                # Look for tournament ID in JavaScript variables
                js_patterns = [
                    r'var\s+tournamentId\s*=\s*["\']?(\d{8,})',
                    r'tournamentId:\s*["\']?(\d{8,})',
                    r'"tournamentId":\s*["\']?(\d{8,})',
                ]
                
                for pattern in js_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        print(f"        Found via JS pattern: {matches[0]}")
                        return matches[0]
                
            except Exception as e:
                print(f"        Error checking {url}: {str(e)[:50]}")
                continue
        
        return None
        
    except Exception as e:
        print(f"        Error: {e}")
        return None

def fetch_tournament_results_simple(website_url, tournament_id):
    """
    Fetch tournament results using a simpler API query.
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        # Simpler query - just get basic tournament info first
        query = f"Tournament({{id:{tournament_id}}}){{name,startDate,endDate,lotCategories:[{{name,stages:[{{name}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"        Error fetching results: {str(e)[:100]}")
        return None

def process_tournaments(tournament_list_file, output_file):
    """
    Process all tournaments from the list and fetch their results.
    """
    data = load_tournament_list(tournament_list_file)
    
    results = {}
    tournament_ids = {}
    
    # Process all tournament types
    for sport, categories in data.items():
        print(f"\nProcessing sport: {sport}")
        
        for category_type, tournaments in categories.items():
            print(f"  Category: {category_type}")
            
            for tournament in tournaments:
                name = tournament.get('name', 'Unknown')
                website_url = tournament.get('websiteUrl', '')
                
                if not website_url:
                    print(f"    ⚠️  {name}: No website URL")
                    continue
                
                print(f"    Processing: {name}")
                print(f"      URL: {website_url}")
                
                # Try to extract tournament ID
                tournament_id = extract_tournament_id_from_page(website_url)
                
                if tournament_id:
                    print(f"      ✓ Tournament ID: {tournament_id}")
                    
                    # Store the ID mapping
                    tournament_ids[name] = {
                        'tournament_id': tournament_id,
                        'website_url': website_url,
                        'organizer': tournament.get('organizerName', ''),
                        'organizer_id': tournament.get('organizerId', ''),
                    }
                    
                    # Try to fetch results
                    tournament_results = fetch_tournament_results_simple(website_url, tournament_id)
                    
                    if tournament_results:
                        results[name] = {
                            'tournament_id': tournament_id,
                            'website_url': website_url,
                            'organizer': tournament.get('organizerName', ''),
                            'results': tournament_results
                        }
                        print(f"      ✓ Results fetched")
                    else:
                        print(f"      ✗ Could not fetch results")
                else:
                    print(f"      ✗ Could not find tournament ID")
                
                # Rate limiting
                time.sleep(2)
    
    # Save tournament IDs mapping
    with open('tournament-ids-mapping.json', 'w', encoding='utf-8') as f:
        json.dump(tournament_ids, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Tournament IDs saved to tournament-ids-mapping.json")
    print(f"  Total IDs found: {len(tournament_ids)}")
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Results saved to {output_file}")
    print(f"  Total results fetched: {len(results)}")

if __name__ == "__main__":
    tournament_list_file = "sample-tournament-list-reponse.json"
    output_file = "tournament-results-aggregated.json"
    
    print("Starting tournament results fetcher v2...")
    print("=" * 60)
    
    process_tournaments(tournament_list_file, output_file)
    
    print("\n" + "=" * 60)
    print("Done!")
