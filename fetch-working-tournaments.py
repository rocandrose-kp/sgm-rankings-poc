import json
import requests
import re
from urllib.parse import urlparse
import time

def parse_tournament_results(api_response, tournament_id, tournament_name, season="2025"):
    """Parse API response into POC format."""
    tournament_data = {
        "tournamentId": tournament_id,
        "tournamentName": tournament_name,
        "season": season,
        "results": []
    }
    
    responses = api_response.get('responses', {})
    
    # Extract categories
    categories = {}
    for key, value in responses.items():
        if 'Category({categoryId:' in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict) and entity.get('__typename') == 'Category':
                category_id = str(entity.get('id', ''))
                name_field = entity.get('name', 'Unknown')
                category_name = name_field.get('en', 'Unknown') if isinstance(name_field, dict) else name_field
                categories[category_id] = category_name
    
    # Extract teams and clubs
    teams = {}
    clubs = {}
    
    # First pass: get club names from NameClub entities
    for key, value in responses.items():
        if 'NameClub({id:' in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict):
                club_id = str(entity.get('id', ''))
                name_field = entity.get('name', {})
                if isinstance(name_field, dict):
                    club_name = name_field.get('en', 'Unknown Club')
                else:
                    club_name = str(name_field)
                clubs[club_id] = club_name
    
    # Second pass: get teams and link to clubs
    for key, value in responses.items():
        if 'Team({id:' in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict) and entity.get('__typename') == 'Team':
                team_id = str(entity.get('id', ''))
                name_obj = entity.get('name', {})
                
                # Get team name
                if isinstance(name_obj, dict):
                    team_name = name_obj.get('fullName', name_obj.get('en', f'Team {team_id}'))
                else:
                    team_name = str(name_obj)
                
                # Get club name from club reference
                club_href = entity.get('club', {}).get('href', '')
                club_match = re.search(r'NameClub\(\{id:(\d+)\}\)', club_href)
                
                if club_match and club_match.group(1) in clubs:
                    club_name = clubs[club_match.group(1)]
                elif isinstance(name_obj, dict) and 'clubName' in name_obj:
                    club_name = name_obj.get('clubName', 'Unknown Club')
                else:
                    club_name = 'Unknown Club'
                
                teams[team_id] = {'teamName': team_name, 'clubName': club_name}
    
    # Extract stage types - need to track by both categoryId AND stageId
    stage_types = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' not in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict) and entity.get('__typename') == 'Stage':
                match = re.search(r'categoryId:(\d+),stageId:(\d+)', key)
                if match:
                    category_id = match.group(1)
                    stage_id = match.group(2)
                    stage_name = entity.get('name', '')
                    stage_key = f"{category_id}_{stage_id}"
                    
                    if 'Plate' in stage_name:
                        stage_types[stage_key] = 'PLATE_FINAL'
                    elif 'Cup' in stage_name:
                        stage_types[stage_key] = 'CUP_FINAL'
                    else:
                        # Default to CUP_FINAL for other playoff stages
                        stage_types[stage_key] = 'CUP_FINAL'
    
    # Extract rankings
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' in key:
            match = re.search(r'categoryId:(\d+),stageId:(\d+)', key)
            if not match:
                continue
            
            category_id = match.group(1)
            stage_id = match.group(2)
            stage_key = f"{category_id}_{stage_id}"
            category_name = categories.get(category_id, f'Category {category_id}')
            stage_type = stage_types.get(stage_key, 'CUP_FINAL')
            
            rankings = value.get('entity', [])
            if not isinstance(rankings, list):
                continue
            
            for ranking in rankings:
                if not isinstance(ranking, dict):
                    continue
                
                if 'StageRankingPlace' not in ranking.get('__typename', ''):
                    continue
                
                rank = ranking.get('rank')
                if rank is None:
                    continue
                
                team_href = ranking.get('team', {}).get('href', '')
                team_match = re.search(r'Team\(\{id:(\d+)\}\)', team_href)
                if not team_match:
                    continue
                
                team_id = team_match.group(1)
                team_info = teams.get(team_id, {'teamName': f'Team {team_id}', 'clubName': 'Unknown Club'})
                
                tournament_data['results'].append({
                    "categoryId": category_id,
                    "categoryName": category_name,
                    "stageType": stage_type,
                    "rank": rank,
                    "team": {
                        "teamId": team_id,
                        "teamName": team_info['teamName'],
                        "clubId": team_info['clubName'].replace(' ', '_').lower(),
                        "clubName": team_info['clubName']
                    }
                })
    
    return tournament_data

def fetch_tournament(url, tournament_id, tournament_name):
    """Fetch tournament results from API."""
    try:
        print(f"\nFetching {tournament_name} (ID: {tournament_id})...")
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"  ✗ HTTP {response.status_code}")
            return None
        
        data = response.json()
        
        # Check for errors
        if 'responses' in data:
            for key, value in data['responses'].items():
                if 'error' in value:
                    print(f"  ✗ API Error: {value['error'][:80]}")
                    return None
        
        # Parse the results
        parsed = parse_tournament_results(data, tournament_id, tournament_name)
        print(f"  ✓ Success: {len(parsed['results'])} results")
        return parsed
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:80]}")
        return None

# Known working tournaments
tournaments = [
    {
        "url": "https://sheppartoncup.com/rest/results_api/call?call=Tournament({id:61805002}){finals:[],lotCategories:[{stages:[{rankings:[{...%20on%20Stage$StageRankingPlace_ConferencePlace:{conference:{matches:[{}]}},...%20on%20Stage$StageRankingPlace_MatchStatus:{match:{arena:{},away:{team:{club:{nation:{}}}},home:{team:{club:{nation:{}}}},roundName:{}}},team:{club:{nation:{}}}}]}]}]}&lang=en&tournamentId=61805002",
        "id": "61805002",
        "name": "Shepparton Cup"
    },
    {
        "url": "https://wucup.com.au/rest/results_api/call?call=Tournament({id:60652114}){finals:[],lotCategories:[{stages:[{rankings:[{... on Stage$StageRankingPlace_ConferencePlace:{conference:{matches:[{}]}},... on Stage$StageRankingPlace_MatchStatus:{match:{arena:{},away:{team:{club:{nation:{}}}},home:{team:{club:{nation:{}}}},roundName:{}}},team:{club:{nation:{}}}}]}]}]}&lang=en&tournamentId=60652114",
        "id": "60652114",
        "name": "WU Cup"
    }
]

print("="*60)
print("FETCHING REAL TOURNAMENT DATA FROM APIS")
print("="*60)

all_tournaments = []

for tournament in tournaments:
    result = fetch_tournament(tournament['url'], tournament['id'], tournament['name'])
    if result:
        all_tournaments.append(result)
    time.sleep(2)  # Rate limiting

# Save combined results
output_file = "all-real-tournaments.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_tournaments, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total tournaments fetched: {len(all_tournaments)}")
for t in all_tournaments:
    print(f"  - {t['tournamentName']}: {len(t['results'])} results")
print(f"\n✓ Saved to: {output_file}")
print(f"{'='*60}")
