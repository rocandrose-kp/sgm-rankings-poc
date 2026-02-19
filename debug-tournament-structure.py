import json
import requests
from urllib.parse import urlparse

def get_tournament_id(website_url):
    """Fetch tournament ID."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = "Me({optionalCupId:null}){cups:[{cup:{}}],teams:[{team:{shirt:{}}}]}"
        params = {'call': query}
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cups = data.get('responses', {}).get('Me({optionalCupId:null})$cups', {}).get('entity', [])
        if cups and len(cups) > 0:
            return str(cups[0].get('cupId'))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test with a known tournament that should have data
test_tournaments = [
    ("Shepparton Cup", "https://wucup.com.au", "61805002"),
    ("Pines Cup", "https://pinescup.com.au", None),
]

for name, url, known_id in test_tournaments:
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    # Get ID
    tournament_id = known_id if known_id else get_tournament_id(url)
    
    if not tournament_id:
        print("✗ Could not get tournament ID")
        continue
    
    print(f"Tournament ID: {tournament_id}")
    
    # Fetch rankings
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Save full response
        output_file = f"debug-{name.replace(' ', '-').lower()}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved response to: {output_file}")
        
        # Analyze structure
        responses = data.get('responses', {})
        print(f"\nResponse keys: {len(responses)}")
        
        # Count different entity types
        entity_types = {}
        for key, value in responses.items():
            if isinstance(value, dict) and 'entity' in value:
                entity = value['entity']
                if isinstance(entity, dict):
                    typename = entity.get('__typename', 'Unknown')
                    entity_types[typename] = entity_types.get(typename, 0) + 1
                elif isinstance(entity, list):
                    entity_types['List'] = entity_types.get('List', 0) + 1
        
        print("\nEntity types found:")
        for typename, count in sorted(entity_types.items()):
            print(f"  - {typename}: {count}")
        
        # Check for rankings
        has_rankings = False
        ranking_count = 0
        for key, value in responses.items():
            if '$rankings' in key and isinstance(value, dict):
                entity = value.get('entity', [])
                if entity:
                    has_rankings = True
                    ranking_count += len(entity)
        
        print(f"\nHas rankings: {has_rankings}")
        print(f"Total ranking entries: {ranking_count}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")

print("\n" + "="*80)
