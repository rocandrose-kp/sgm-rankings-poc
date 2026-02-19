import json
import requests
import re
from urllib.parse import urlparse
import time

def load_tournament_list(file_path):
    """Load the tournament list from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_tournament_id_from_url(website_url):
    """
    Try to extract tournament ID from the website URL or by scraping the page.
    CupManager sites typically have the tournament ID embedded in the page source.
    """
    try:
        # Parse the URL to get the domain
        parsed = urlparse(website_url)
        domain = parsed.netloc
        
        # Try multiple pages to find the tournament ID
        urls_to_try = [
            website_url,
            f"{website_url}/2026/result/",
            f"{website_url}/2025/result/",
            f"{website_url.rstrip('/')}/result/",
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Look for tournament ID patterns in the HTML
                tournament_id_patterns = [
                    r'tournamentId["\']?\s*[:=]\s*["\']?(\d{8,})',
                    r'tournament["\']?\s*[:=]\s*["\']?(\d{8,})',
                    r'/tournament/(\d{8,})',
                    r'tid["\']?\s*[:=]\s*["\']?(\d{8,})',
                    r'Tournament\(\{id:(\d{8,})\}\)',
                    r'id["\']?\s*[:=]\s*["\']?(\d{8,})',
                    r'/rest/results_api/call\?.*tournamentId=(\d{8,})',
                    r'data-tournament-id["\']?\s*[:=]\s*["\']?(\d{8,})',
                ]
                
                for pattern in tournament_id_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        # Return the first match that looks like a tournament ID (8+ digits)
                        for match in matches:
                            if len(match) >= 8:
                                return match
                
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        print(f"Error extracting tournament ID from {website_url}: {e}")
        return None

def fetch_tournament_results(website_url, tournament_id):
    """
    Fetch tournament results using the results API.
    """
    try:
        parsed = urlparse(website_url)
        domain = parsed.netloc
        
        # Construct the results API URL
        base_url = f"{parsed.scheme}://{domain}/rest/results_api/call"
        
        # GraphQL-style query for tournament results
        query = f"Tournament({{id:{tournament_id}}}){{finals:[],lotCategories:[{{stages:[{{rankings:[{{...%20on%20Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... %20on%20Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}&lang=en&tournamentId={tournament_id}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"Error fetching results for tournament {tournament_id}: {e}")
        return None

def process_tournaments(tournament_list_file, output_file):
    """
    Process all tournaments from the list and fetch their results.
    """
    # Load tournament list
    data = load_tournament_list(tournament_list_file)
    
    results = {}
    
    # Process all tournament types (local, accommodation, etc.)
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
                tournament_id = extract_tournament_id_from_url(website_url)
                
                if tournament_id:
                    print(f"      ✓ Found tournament ID: {tournament_id}")
                    
                    # Fetch results
                    tournament_results = fetch_tournament_results(website_url, tournament_id)
                    
                    if tournament_results:
                        results[name] = {
                            'tournament_id': tournament_id,
                            'website_url': website_url,
                            'organizer': tournament.get('organizerName', ''),
                            'results': tournament_results
                        }
                        print(f"      ✓ Results fetched successfully")
                    else:
                        print(f"      ✗ Failed to fetch results")
                else:
                    print(f"      ✗ Could not find tournament ID")
                
                # Be respectful with rate limiting
                time.sleep(1)
    
    # Save results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to {output_file}")
    print(f"  Total tournaments processed: {len(results)}")

if __name__ == "__main__":
    tournament_list_file = "sample-tournament-list-reponse.json"
    output_file = "tournament-results-aggregated.json"
    
    print("Starting tournament results fetcher...")
    print("=" * 60)
    
    process_tournaments(tournament_list_file, output_file)
    
    print("\n" + "=" * 60)
    print("Done!")
