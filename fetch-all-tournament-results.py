import json
import requests
from urllib.parse import urlparse
import time

def load_tournament_list(api_url=None, file_path=None):
    """
    Load the tournament list from API URL or JSON file.
    If api_url is provided, fetch from API. Otherwise, load from file.
    """
    if api_url:
        try:
            print(f"Fetching tournament list from API...")
            print(f"URL: {api_url}")
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            print(f"✓ Tournament list fetched successfully\n")
            return response.json()
        except Exception as e:
            print(f"✗ Error fetching tournament list: {e}")
            if file_path:
                print(f"Falling back to local file: {file_path}\n")
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise
    elif file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError("Either api_url or file_path must be provided")

def get_tournament_id_from_me_api(website_url):
    """
    Fetch tournament ID using the Me API endpoint.
    This endpoint returns the cupId which is the tournament ID.
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = "Me({optionalCupId:null}){cups:[{cup:{}}],teams:[{team:{shirt:{}}}]}"
        
        params = {
            'call': query
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract cupId from the response
        cups = data.get('responses', {}).get('Me({optionalCupId:null})$cups', {}).get('entity', [])
        
        if cups and len(cups) > 0:
            cup_id = cups[0].get('cupId')
            if cup_id:
                return str(cup_id)
        
        return None
        
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def fetch_tournament_results(website_url, tournament_id):
    """
    Fetch tournament results using the exact API format from user's examples.
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        # Use the exact query format from the user's examples
        query = f"Tournament({{id:{tournament_id}}}){{finals:[],lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        print(f"      Fetching results...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors in response
        if 'responses' in result:
            for key, value in result['responses'].items():
                if 'error' in value:
                    print(f"      API Error: {value['error'][:100]}")
                    return None
        
        print(f"      ✓ Results fetched successfully")
        return result
        
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def process_tournaments(output_file, api_url=None, tournament_list_file=None):
    """
    Process all tournaments from the list and fetch their results.
    """
    data = load_tournament_list(api_url=api_url, file_path=tournament_list_file)
    
    results = {}
    tournament_ids_mapping = {}
    
    total_tournaments = 0
    successful_ids = 0
    successful_results = 0
    
    # Process all tournament types
    for sport, categories in data.items():
        print(f"\n{'='*60}")
        print(f"Sport: {sport}")
        print('='*60)
        
        for category_type, tournaments in categories.items():
            print(f"\n  Category: {category_type}")
            print(f"  {'-'*56}")
            
            for tournament in tournaments:
                total_tournaments += 1
                name = tournament.get('name', 'Unknown')
                website_url = tournament.get('websiteUrl', '')
                organizer = tournament.get('organizerName', '')
                
                if not website_url:
                    print(f"    ⚠️  {name}: No website URL")
                    continue
                
                print(f"\n    {total_tournaments}. {name}")
                print(f"       Organizer: {organizer}")
                print(f"       URL: {website_url}")
                
                # Get tournament ID
                tournament_id = get_tournament_id_from_me_api(website_url)
                
                if tournament_id:
                    print(f"       ✓ Tournament ID: {tournament_id}")
                    successful_ids += 1
                    
                    # Store the ID mapping
                    tournament_ids_mapping[name] = {
                        'tournament_id': tournament_id,
                        'website_url': website_url,
                        'organizer': organizer,
                        'organizer_id': tournament.get('organizerId', ''),
                    }
                    
                    # Fetch results
                    tournament_results = fetch_tournament_results(website_url, tournament_id)
                    
                    if tournament_results:
                        results[name] = {
                            'tournament_id': tournament_id,
                            'website_url': website_url,
                            'organizer': organizer,
                            'results': tournament_results
                        }
                        print(f"       ✓ Results fetched successfully")
                        successful_results += 1
                    else:
                        print(f"       ✗ Failed to fetch results")
                else:
                    print(f"       ✗ Could not find tournament ID")
                
                # Rate limiting - be respectful
                time.sleep(1)
    
    # Save tournament IDs mapping
    ids_file = 'tournament-ids-mapping.json'
    with open(ids_file, 'w', encoding='utf-8') as f:
        json.dump(tournament_ids_mapping, f, indent=2, ensure_ascii=False)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Total tournaments processed: {total_tournaments}")
    print(f"Tournament IDs found: {successful_ids}")
    print(f"Results fetched: {successful_results}")
    print(f"\n✓ Tournament IDs saved to: {ids_file}")
    print(f"✓ Results saved to: {output_file}")
    print('='*60)

if __name__ == "__main__":
    # API URL to fetch tournament list
    api_url = "https://portal.cupmanager.net/rest/newportal/search?coords=[-38,145]&country=AU&date=2026-02-05&fromDate=2025-11-01&loc=Victoria&regions=[{%22nationId%22:25}]&sport=football"
    
    # Fallback to local file if API fails
    tournament_list_file = "sample-tournament-list-reponse.json"
    output_file = "all-tournament-results.json"
    
    print("\n" + "="*60)
    print("TOURNAMENT RESULTS FETCHER")
    print("="*60)
    print(f"Source: API (with fallback to {tournament_list_file})")
    print(f"Output: {output_file}")
    print("="*60 + "\n")
    
    process_tournaments(output_file, api_url=api_url, tournament_list_file=tournament_list_file)
    
    print("\nDone!")
