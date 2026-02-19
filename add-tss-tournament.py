import json
import requests
from urllib.parse import urlparse
import re

def fetch_tournament_rankings(website_url, tournament_id):
    """Fetch tournament rankings."""
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
        print(f"Error: {e}")
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
            if isinstance(entity, dict) and entity.get('__typename') == 'Category':
                category_id = entity.get('id')
                name_field = entity.get('name', 'Unknown')
                category_name = name_field if isinstance(name_field, str) else name_field.get('en', 'Unknown')
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
                    if 'Cup' in stage_name or 'Playoff' in stage_name:
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
    
    # Process rankings - handle MatchStatus type
    for category_id, rankings in stages_with_rankings.items():
        category_name = categories.get(category_id, f"Category {category_id}")
        stage_type = stage_types.get(category_id, 'CUP_FINAL')
        
        for ranking in rankings:
            if '__typename' not in ranking:
                continue
                
            rank = ranking.get('rank')
            
            # Handle MatchStatus type (has match reference)
            if 'MatchStatus' in ranking['__typename']:
                match_href = ranking.get('match', {}).get('href', '')
                match_id_search = re.search(r'Match\(\{id:(\d+)\}\)', match_href)
                
                if match_id_search:
                    match_id = match_id_search.group(1)
                    # Find the match to get team info
                    match_key = f"Match({{id:{match_id}}})"
                    if match_key in responses:
                        match_entity = responses[match_key]['entity']
                        
                        # Determine which team based on status
                        status = ranking.get('status', '')
                        if status == 'win':
                            team_href = match_entity.get('home', {}).get('href', '')
                        else:
                            team_href = match_entity.get('away', {}).get('href', '')
                        
                        team_match = re.search(r'MatchActor\(\{actor:"(\w+)",id:(\d+)\}\)', team_href)
                        if team_match:
                            actor_type = team_match.group(1)
                            actor_match_id = team_match.group(2)
                            
                            # Get team from MatchActor
                            actor_key = f'MatchActor({{actor:"{actor_type}",id:{actor_match_id}}})'
                            if actor_key in responses:
                                actor_entity = responses[actor_key]['entity']
                                team_id = str(actor_entity.get('id'))
                                
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
            
            # Handle regular team reference
            elif 'team' in ranking:
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

print("\n" + "="*80)
print("ADDING TSS FOOTBALL TOURNAMENT")
print("="*80 + "\n")

tournament_name = "TSS Football Tournament"
tournament_id = "54663955"
website_url = "https://tssfootballtournament.cupmanager.net"

print(f"Fetching {tournament_name}...")

# Fetch rankings
rankings_data = fetch_tournament_rankings(website_url, tournament_id)

if not rankings_data:
    print("✗ Failed to fetch rankings")
    exit(1)

print("✓ Rankings fetched")

# Fetch finals
finals_data = fetch_tournament_finals(website_url, tournament_id)

if finals_data:
    match_scores = parse_match_scores(finals_data)
    team_matches_map = link_scores_to_teams(match_scores)
    print(f"✓ Match scores: {len(match_scores)} matches")
else:
    team_matches_map = {}
    print("⚠ No match scores")

# Parse tournament data
tournament_data = parse_tournament_data(rankings_data, team_matches_map, tournament_name, tournament_id)

if tournament_data['results']:
    existing_tournaments.append(tournament_data)
    results_with_matches = sum(1 for r in tournament_data['results'] if 'matches' in r)
    print(f"✓ {len(tournament_data['results'])} results ({results_with_matches} with match scores)")
else:
    print("✗ No results found")
    exit(1)

# Save all tournaments
output_file = 'tournament-rankings-poc/web/src/data/realData.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(existing_tournaments, f, indent=2, ensure_ascii=False)

print(f"\n✓ Saved to: {output_file}")

print(f"\nAll Tournaments:")
for t in existing_tournaments:
    results_with_matches = sum(1 for r in t['results'] if 'matches' in r)
    score_text = f"{results_with_matches} with scores" if results_with_matches > 0 else "no scores"
    print(f"  - {t['tournamentName']}: {len(t['results'])} results ({score_text})")

print("\n" + "="*80)
