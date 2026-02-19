import json
import requests
from urllib.parse import urlparse, urlencode

def load_tournament_ids(file_path):
    """Load tournament IDs from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_tournament_results(website_url, tournament_id):
    """
    Fetch tournament results using the results API.
    Uses the same query structure as your sample.
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        # Use the exact query format from your sample
        query = f"Tournament({{id:{tournament_id}}}){{finals:[],lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        print(f"  Fetching from: {base_url}")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def main():
    # Load tournament IDs
    print("Loading tournament IDs...")
    tournament_ids = load_tournament_ids('tournament-ids.json')
    print(f"Found {len(tournament_ids)} tournaments\n")
    
    results = {}
    
    # Fetch results for each tournament
    for name, info in tournament_ids.items():
        print(f"Processing: {name}")
        print(f"  Tournament ID: {info['tournament_id']}")
        print(f"  Website: {info['website_url']}")
        
        tournament_results = fetch_tournament_results(
            info['website_url'],
            info['tournament_id']
        )
        
        if tournament_results:
            results[name] = {
                'tournament_id': info['tournament_id'],
                'website_url': info['website_url'],
                'results': tournament_results
            }
            print(f"  ✓ Results fetched successfully\n")
        else:
            print(f"  ✗ Failed to fetch results\n")
    
    # Save results
    output_file = 'tournament-results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Results saved to {output_file}")
    print(f"  Tournaments processed: {len(tournament_ids)}")
    print(f"  Results fetched: {len(results)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
