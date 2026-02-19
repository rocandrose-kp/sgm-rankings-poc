import json
import requests
from urllib.parse import urlparse
import re

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

# Tournament URLs
tournament_urls = {
    "61805002": "https://wucup.com.au",  # Shepparton Cup
    "60652114": "https://wucup.com.au",  # WU Cup
    "54663955": "https://tssfootballtournament.cupmanager.net"  # TSS Football Tournament
}

# Load tournaments
with open('tournament-rankings-poc/web/src/data/realData.json', 'r', encoding='utf-8') as f:
    tournaments = json.load(f)

print("Adding match scores to all tournaments...\n")

for tournament in tournaments:
    tournament_id = tournament['tournamentId']
    tournament_name = tournament['tournamentName']
    website_url = tournament_urls.get(tournament_id)
    
    if not website_url:
        print(f"⚠ {tournament_name}: No URL configured")
        continue
    
    # Check if already has match scores
    has_matches = any('matches' in result for result in tournament['results'])
    
    if has_matches:
        print(f"✓ {tournament_name}: Already has match scores")
        continue
    
    print(f"Processing {tournament_name} (ID: {tournament_id})...")
    
    # Fetch finals
    finals_data = fetch_tournament_finals(website_url, tournament_id)
    
    if not finals_data:
        print(f"   ✗ Failed to fetch match scores\n")
        continue
    
    # Parse match scores
    match_scores = parse_match_scores(finals_data)
    team_matches_map = link_scores_to_teams(match_scores)
    
    print(f"   ✓ Parsed {len(match_scores)} matches")
    
    # Add match scores to results
    added_count = 0
    for result in tournament['results']:
        team_id = result['team']['teamId']
        if team_id in team_matches_map:
            result['matches'] = team_matches_map[team_id]
            added_count += 1
    
    print(f"   ✓ Added match scores to {added_count} results\n")

# Save updated data
output_file = 'tournament-rankings-poc/web/src/data/realData.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tournaments, f, indent=2, ensure_ascii=False)

print(f"✓ Saved to: {output_file}")
print(f"\nSummary:")
for t in tournaments:
    results_with_matches = sum(1 for r in t['results'] if 'matches' in r)
    print(f"  - {t['tournamentName']}: {len(t['results'])} results ({results_with_matches} with match scores)")
