import json
import requests
from urllib.parse import urlparse
import time

def fetch_tournament_finals(website_url, tournament_id):
    """
    Fetch tournament finals with match scores using the finals endpoint.
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        # Use the finals endpoint that includes MatchResult entities with scores
        query = f"Tournament({{id:{tournament_id}}}){{finals:[{{... on Match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},division:{{category:{{}},stage:{{}}}},home:{{team:{{club:{{nation:{{}}}}}}}},protests:[{{}}],result:{{}},roundName:{{}},stage:{{}},video:{{}}}}}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        print(f"      Fetching finals with match scores...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Check for errors
        if 'responses' in result:
            for key, value in result['responses'].items():
                if isinstance(value, dict) and 'error' in value:
                    print(f"      API Error: {value['error'][:100]}")
                    return None
        
        print(f"      ✓ Finals fetched successfully")
        return result
        
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def fetch_tournament_rankings(website_url, tournament_id):
    """
    Fetch tournament rankings (placements).
    """
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        print(f"      Fetching rankings...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"      ✓ Rankings fetched successfully")
        return result
        
    except Exception as e:
        print(f"      Error: {str(e)[:80]}")
        return None

def parse_match_scores(finals_data):
    """
    Parse match scores from the finals endpoint response.
    Returns a dict mapping match_id to score information.
    """
    match_scores = {}
    
    if 'responses' not in finals_data:
        return match_scores
    
    responses = finals_data['responses']
    
    # First, collect all MatchResult entities
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
                'penalties': entity.get('penalties', False),
                'finished': entity.get('finished', False)
            }
    
    # Now collect Match entities and link them to results
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
            
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
            
        if entity.get('__typename') == 'Match':
            match_id = str(entity.get('id'))
            
            # Get home and away team info
            home_href = entity.get('home', {}).get('href', '')
            away_href = entity.get('away', {}).get('href', '')
            
            # Get round name
            round_name_href = entity.get('roundName', {}).get('href', '')
            
            # Get division info
            division_href = entity.get('division', {}).get('href', '')
            
            match_info = {
                'matchId': match_id,
                'homeHref': home_href,
                'awayHref': away_href,
                'roundNameHref': round_name_href,
                'divisionHref': division_href,
                'finished': entity.get('finished', False)
            }
            
            # Add score if available
            if match_id in match_results:
                match_info.update(match_results[match_id])
            
            match_scores[match_id] = match_info
    
    # Resolve team names from MatchActor entities
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
            
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
            
        if entity.get('__typename') == 'MatchActor':
            team_name = entity.get('name', {}).get('en', '')
            team_id = str(entity.get('id'))
            team_href = entity.get('team', {}).get('href', '')
            
            # Find matches that reference this actor
            for match_id, match_info in match_scores.items():
                if key == match_info.get('homeHref'):
                    match_info['homeTeam'] = team_name
                    match_info['homeTeamId'] = team_id
                    match_info['homeTeamHref'] = team_href
                elif key == match_info.get('awayHref'):
                    match_info['awayTeam'] = team_name
                    match_info['awayTeamId'] = team_id
                    match_info['awayTeamHref'] = team_href
    
    # Resolve round names
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
            
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
            
        if entity.get('__typename') == 'Match$RoundName':
            round_name = entity.get('name', {}).get('en', '')
            
            # Find matches that reference this round name
            for match_id, match_info in match_scores.items():
                if key == match_info.get('roundNameHref'):
                    match_info['roundName'] = round_name
    
    # Resolve division names
    for key, value in responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
            
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
            
        if entity.get('__typename') in ['Playoff', 'Division']:
            division_name = entity.get('name', {}).get('en', '')
            
            # Find matches that reference this division
            for match_id, match_info in match_scores.items():
                if key == match_info.get('divisionHref'):
                    match_info['divisionName'] = division_name
    
    return match_scores

def extract_team_id_from_href(href):
    """Extract team ID from Team href."""
    import re
    match = re.search(r'Team\(\{id:(\d+)\}\)', href)
    return match.group(1) if match else None

def link_scores_to_teams(match_scores, rankings_data):
    """
    Link match scores to team results in the rankings data.
    Returns updated rankings with match scores included.
    """
    # Build a mapping of team IDs to their match scores
    team_matches = {}
    
    for match_id, match_info in match_scores.items():
        if not match_info.get('finished'):
            continue
            
        home_team_href = match_info.get('homeTeamHref', '')
        away_team_href = match_info.get('awayTeamHref', '')
        
        home_team_id = extract_team_id_from_href(home_team_href)
        away_team_id = extract_team_id_from_href(away_team_href)
        
        if home_team_id:
            if home_team_id not in team_matches:
                team_matches[home_team_id] = []
            team_matches[home_team_id].append({
                'opponent': match_info.get('awayTeam', ''),
                'homeGoals': match_info.get('homeGoals', 0),
                'awayGoals': match_info.get('awayGoals', 0),
                'isHome': True,
                'result': 'won' if match_info.get('winner') == 'home' else 'lost',
                'roundName': match_info.get('roundName', ''),
                'divisionName': match_info.get('divisionName', ''),
                'penalties': match_info.get('penalties', False)
            })
        
        if away_team_id:
            if away_team_id not in team_matches:
                team_matches[away_team_id] = []
            team_matches[away_team_id].append({
                'opponent': match_info.get('homeTeam', ''),
                'homeGoals': match_info.get('homeGoals', 0),
                'awayGoals': match_info.get('awayGoals', 0),
                'isHome': False,
                'result': 'won' if match_info.get('winner') == 'away' else 'lost',
                'roundName': match_info.get('roundName', ''),
                'divisionName': match_info.get('divisionName', ''),
                'penalties': match_info.get('penalties', False)
            })
    
    return team_matches

# Test with Shepparton Cup
if __name__ == "__main__":
    tournament_id = "61805002"
    website_url = "https://wucup.com.au"
    
    print("\n" + "="*80)
    print("FETCHING TOURNAMENT WITH MATCH SCORES")
    print("="*80)
    print(f"Tournament ID: {tournament_id}")
    print(f"Website: {website_url}")
    print("="*80 + "\n")
    
    # Fetch finals with match scores
    finals_data = fetch_tournament_finals(website_url, tournament_id)
    
    if finals_data:
        # Parse match scores
        print("\n      Parsing match scores...")
        match_scores = parse_match_scores(finals_data)
        print(f"      ✓ Parsed {len(match_scores)} matches with scores")
        
        # Show sample
        print("\n" + "="*80)
        print("SAMPLE MATCH SCORES")
        print("="*80)
        for i, (match_id, match_info) in enumerate(list(match_scores.items())[:3]):
            if 'homeTeam' in match_info and 'awayTeam' in match_info:
                home = match_info.get('homeTeam', 'Unknown')
                away = match_info.get('awayTeam', 'Unknown')
                home_goals = match_info.get('homeGoals', 0)
                away_goals = match_info.get('awayGoals', 0)
                round_name = match_info.get('roundName', 'Unknown')
                division = match_info.get('divisionName', 'Unknown')
                penalties = " (Penalties)" if match_info.get('penalties') else ""
                
                print(f"\n{i+1}. {round_name} - {division}")
                print(f"   {home} {home_goals} - {away_goals} {away}{penalties}")
        
        # Fetch rankings
        print("\n")
        rankings_data = fetch_tournament_rankings(website_url, tournament_id)
        
        if rankings_data:
            # Link scores to teams
            print("\n      Linking scores to teams...")
            team_matches = link_scores_to_teams(match_scores, rankings_data)
            print(f"      ✓ Linked scores for {len(team_matches)} teams")
            
            # Save combined data
            output = {
                'tournamentId': tournament_id,
                'websiteUrl': website_url,
                'matchScores': match_scores,
                'teamMatches': team_matches,
                'rankingsData': rankings_data,
                'finalsData': finals_data
            }
            
            output_file = 'tournament-with-scores.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Saved to: {output_file}")
    
    print("\n" + "="*80)
    print("DONE!")
    print("="*80)
