import requests
import json
import re

# Test fetching match result data to see if we can get scores
TOURNAMENT_ID = "61805002"  # Shepparton Cup
API_URL = f"https://api.profixio.com/api/v1/query?cupId=13913907&query=Tournament(%7Bid%3A{TOURNAMENT_ID}%7D)%24results"

def fetch_api_data(url):
    """Fetch data from the API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def find_match_results(data):
    """Find MatchResult entities in the response"""
    match_results = {}
    
    if 'responses' not in data:
        return match_results
    
    for key, value in data['responses'].items():
        # Look for MatchResult entities
        if 'MatchResult({id:' in key:
            match_id = re.search(r'MatchResult\(\{id:(\d+)\}\)', key)
            if match_id and 'entity' in value:
                entity = value['entity']
                match_results[match_id.group(1)] = entity
                
        # Also look for MatchActor entities (home/away teams with scores)
        if 'MatchActor({actor:' in key:
            if 'entity' in value:
                entity = value['entity']
                if 'score' in entity or 'goals' in entity:
                    match_results[key] = entity
    
    return match_results

def find_finals_matches(data):
    """Find matches that are finals or semi-finals"""
    finals_matches = []
    
    if 'responses' not in data:
        return finals_matches
    
    for key, value in data['responses'].items():
        if 'Match({id:' in key and 'entity' in value:
            entity = value['entity']
            # Check if this is a knockout/finals match
            if 'round' in entity or 'stage' in entity:
                match_info = {
                    'match_id': entity.get('id'),
                    'finished': entity.get('finished', False),
                    'result_href': entity.get('result', {}).get('href', ''),
                    'home_href': entity.get('home', {}).get('href', ''),
                    'away_href': entity.get('away', {}).get('href', ''),
                    'stage_href': entity.get('stage', {}).get('href', '')
                }
                finals_matches.append(match_info)
    
    return finals_matches

print("=" * 60)
print("TESTING MATCH SCORE DATA AVAILABILITY")
print("=" * 60)

# Fetch tournament data
print(f"\nFetching tournament data from API...")
data = fetch_api_data(API_URL)

if data:
    print(f"✓ Successfully fetched data")
    
    # Find match results
    print(f"\nSearching for MatchResult entities...")
    match_results = find_match_results(data)
    print(f"Found {len(match_results)} match result entities")
    
    if match_results:
        print("\nSample match result entities:")
        for i, (key, entity) in enumerate(list(match_results.items())[:3]):
            print(f"\n  {i+1}. Key: {key}")
            print(f"     Entity: {json.dumps(entity, indent=6)[:500]}...")
    
    # Find finals matches
    print(f"\nSearching for finals/semi-finals matches...")
    finals_matches = find_finals_matches(data)
    print(f"Found {len(finals_matches)} match entities")
    
    if finals_matches:
        print("\nSample match entities:")
        for i, match in enumerate(finals_matches[:3]):
            print(f"\n  {i+1}. Match ID: {match['match_id']}")
            print(f"     Finished: {match['finished']}")
            print(f"     Result: {match['result_href']}")
            print(f"     Home: {match['home_href']}")
            print(f"     Away: {match['away_href']}")
            print(f"     Stage: {match['stage_href']}")
    
    # Save sample data for inspection
    sample_file = 'match-data-sample.json'
    with open(sample_file, 'w', encoding='utf-8') as f:
        sample_data = {
            'match_results': {k: v for k, v in list(match_results.items())[:5]},
            'finals_matches': finals_matches[:10]
        }
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved sample data to: {sample_file}")
    
else:
    print("✗ Failed to fetch data")

print("\n" + "=" * 60)
