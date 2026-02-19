import json
import requests
from urllib.parse import urlparse
import time
import re

def fetch_tournament_rankings(website_url, tournament_id):
    """Fetch tournament rankings (placements)."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def fetch_tournament_finals(website_url, tournament_id):
    """Fetch tournament finals with match scores."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{finals:[{{... on Match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},division:{{category:{{}},stage:{{}}}},home:{{team:{{club:{{nation:{{}}}}}}}},protests:[{{}}],result:{{}},roundName:{{}},stage:{{}},video:{{}}}}}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def parse_match_scores(finals_data):
    """Parse match scores from finals data."""
    match_scores = {}
    
    if 'responses' not in finals_data:
        return match_scores
    
    responses = finals_data['responses']
    
    # Collect MatchResult entities
    match_results = {}
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'MatchResult':
            match_id = str(entity.get('id'))
            match_results[match_id] = {
                'homeGoals': entity.get('homeGoals', 0),
                'awayGoals': entity.get('awayGoals', 0),
                'winner': entity.get('winner', ''),
                'penalties': entity.get('penalties', False)
            }
    
    # Collect Match entities
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'Match':
            match_id = str(entity.get('id'))
            match_info = {
                'matchId': match_id,
                'homeHref': entity.get('home', {}).get('href', ''),
                'awayHref': entity.get('away', {}).get('href', ''),
                'roundNameHref': entity.get('roundName', {}).get('href', '')
            }
            
            if match_id in match_results:
                match_info.update(match_results[match_id])
            
            match_scores[match_id] = match_info
    
    # Resolve team names
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'MatchActor':
            team_name = entity.get('name', {}).get('en', '')
            team_href = entity.get('team', {}).get('href', '')
            team_id_match = re.search(r'Team\(\{id:(\d+)\}\)', team_href)
            actual_team_id = team_id_match.group(1) if team_id_match else None
            
            for match_id, match_info in match_scores.items():
                if key == match_info.get('homeHref'):
                    match_info['homeTeam'] = team_name
                    match_info['homeTeamId'] = actual_team_id
                elif key == match_info.get('awayHref'):
                    match_info['awayTeam'] = team_name
                    match_info['awayTeamId'] = actual_team_id
    
    # Resolve round names
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'Match$RoundName':
            round_name = entity.get('name', {}).get('en', '')
            for match_id, match_info in match_scores.items():
                if key == match_info.get('roundNameHref'):
                    match_info['roundName'] = round_name
    
    return match_scores

def link_scores_to_teams(match_scores):
    """Build team matches mapping."""
    team_matches_map = {}
    
    for match_id, match_info in match_scores.items():
        if 'homeTeamId' not in match_info or 'awayTeamId' not in match_info:
            continue
        
        home_id = match_info['homeTeamId']
        away_id = match_info['awayTeamId']
        
        if home_id:
            if home_id not in team_matches_map:
                team_matches_map[home_id] = []
            team_matches_map[home_id].append({
                'opponent': match_info.get('awayTeam', ''),
                'opponentId': away_id,
                'homeGoals': match_info.get('homeGoals', 0),
                'awayGoals': match_info.get('awayGoals', 0),
                'isHome': True,
                'result': 'won' if match_info.get('winner') == 'home' else 'lost',
                'roundName': match_info.get('roundName', ''),
                'penalties': match_info.get('penalties', False)
            })
        
        if away_id:
            if away_id not in team_matches_map:
                team_matches_map[away_id] = []
            team_matches_map[away_id].append({
                'opponent': match_info.get('homeTeam', ''),
                'opponentId': home_id,
                'homeGoals': match_info.get('homeGoals', 0),
                'awayGoals': match_info.get('awayGoals', 0),
                'isHome': False,
                'result': 'won' if match_info.get('winner') == 'away' else 'lost',
                'roundName': match_info.get('roundName', ''),
                'penalties': match_info.get('penalties', False)
            })
    
    return team_matches_map

def parse_tournament_data(rankings_data, team_matches_map, tournament_name, tournament_id):
    """Parse tournament rankings and add match scores."""
    tournament_data = {
        "tournamentId": tournament_id,
        "tournamentName": tournament_name,
        "season": "2025",
        "results": []
    }
    
    responses = rankings_data.get('responses', {})
    
    # Find categories
    categories = {}
    for key, value in responses.items():
        if 'Category({categoryId:' in key and 'entity' in value:
            entity = value['entity']
            if entity.get('__typename') == 'Category':
                category_id = entity.get('id')
                name_field = entity.get('name', 'Unknown')
                category_name = name_field.get('en', 'Unknown') if isinstance(name_field, dict) else name_field
                categories[str(category_id)] = category_name
    
    # Find stages with rankings
    stages_with_rankings = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' in key:
            match = re.search(r'categoryId:(\d+)', key)
            if match:
                category_id = match.group(1)
                rankings = value.get('entity', [])
                if rankings:
                    stages_with_rankings[category_id] = rankings
    
    # Get stage types
    stage_types = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' not in key and 'entity' in value:
            entity = value['entity']
            if entity.get('__typename') == 'Stage':
                match = re.search(r'categoryId:(\d+)', key)
                if match:
                    category_id = match.group(1)
                    stage_name = entity.get('name', '')
                    if 'Cup' in stage_name:
                        stage_types[category_id] = 'CUP_FINAL'
                    elif 'Plate' in stage_name:
                        stage_types[category_id] = 'PLATE_FINAL'
                    else:
                        stage_types[category_id] = 'CUP_FINAL'
    
    # Get team information
    teams = {}
    for key, value in responses.items():
        if 'Team({id:' in key and 'entity' in value:
            entity = value['entity']
            if entity.get('__typename') == 'Team':
                team_id = entity.get('id')
                name_obj = entity.get('name', {})
                team_name = name_obj.get('fullName', name_obj.get('en', 'Unknown'))
                club_name = name_obj.get('clubName', 'Unknown Club')
                teams[str(team_id)] = {
                    'teamName': team_name,
                    'clubName': club_name
                }
    
    # Process rankings
    for category_id, rankings in stages_with_rankings.items():
        category_name = categories.get(category_id, f"Category {category_id}")
        stage_type = stage_types.get(category_id, 'CUP_FINAL')
        
        for ranking in rankings:
            if '__typename' in ranking and 'StageRankingPlace' in ranking['__typename']:
                rank = ranking.get('rank')
                team_href = ranking.get('team', {}).get('href', '')
                
                team_match = re.search(r'Team\(\{id:(\d+)\}\)', team_href)
                if team_match:
                    team_id = team_match.group(1)
                    team_info = teams.get(team_id, {
                        'teamName': f'Team {team_id}',
                        'clubName': 'Unknown Club'
                    })
                    
                    result_entry = {
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
                    }
                    
                    # Add match scores if available
                    if team_id in team_matches_map:
                        result_entry['matches'] = team_matches_map[team_id]
                    
                    tournament_data['results'].append(result_entry)
    
    return tournament_data

# Load existing tournaments
with open('all-real-tournaments.json', 'r', encoding='utf-8') as f:
    existing_tournaments = json.load(f)

existing_ids = {t['tournamentId'] for t in existing_tournaments}

# Load tournament mapping
with open('tournament-ids-mapping.json', 'r', encoding='utf-8') as f:
    tournament_mapping = json.load(f)

print("\n" + "="*80)
print("FETCHING ADDITIONAL TOURNAMENTS")
print("="*80 + "\n")

all_tournaments = list(existing_tournaments)
new_count = 0

for name, info in tournament_mapping.items():
    tournament_id = info['tournament_id']
    website_url = info['website_url']
    
    if tournament_id in existing_ids:
        print(f"✓ {name}: Already fetched")
        continue
    
    print(f"\n{name} (ID: {tournament_id})")
    print(f"   URL: {website_url}")
    
    # Fetch rankings
    print(f"   Fetching rankings...")
    rankings_data = fetch_tournament_rankings(website_url, tournament_id)
    
    if not rankings_data:
        print(f"   ✗ Failed to fetch rankings")
        continue
    
    print(f"   ✓ Rankings fetched")
    
    # Fetch finals
    print(f"   Fetching match scores...")
    finals_data = fetch_tournament_finals(website_url, tournament_id)
    
    if finals_data:
        print(f"   ✓ Match scores fetched")
        match_scores = parse_match_scores(finals_data)
        team_matches_map = link_scores_to_teams(match_scores)
        print(f"   ✓ Parsed {len(match_scores)} matches")
    else:
        print(f"   ⚠ No match scores available")
        team_matches_map = {}
    
    # Parse tournament data
    tournament_data = parse_tournament_data(rankings_data, team_matches_map, name, tournament_id)
    
    if tournament_data['results']:
        all_tournaments.append(tournament_data)
        new_count += 1
        results_with_matches = sum(1 for r in tournament_data['results'] if 'matches' in r)
        print(f"   ✓ Added {len(tournament_data['results'])} results ({results_with_matches} with match scores)")
    else:
        print(f"   ✗ No results found")
    
    # Rate limiting
    time.sleep(1)

# Save all tournaments
output_file = 'tournament-rankings-poc/web/src/data/realData.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_tournaments, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Existing tournaments: {len(existing_tournaments)}")
print(f"New tournaments added: {new_count}")
print(f"Total tournaments: {len(all_tournaments)}")
print(f"\n✓ Saved to: {output_file}")

print(f"\nAll Tournaments:")
for t in all_tournaments:
    results_with_matches = sum(1 for r in t['results'] if 'matches' in r)
    print(f"  - {t['tournamentName']}: {len(t['results'])} results ({results_with_matches} with match scores)")

print("\n" + "="*80)
