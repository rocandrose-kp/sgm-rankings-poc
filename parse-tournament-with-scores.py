import json
import re

def parse_tournament_with_scores(rankings_file, finals_file):
    """
    Parse tournament data combining rankings and match scores.
    """
    # Load both data files
    with open(rankings_file, 'r', encoding='utf-8') as f:
        rankings_data = json.load(f)
    
    with open(finals_file, 'r', encoding='utf-8') as f:
        finals_data = json.load(f)
    
    tournament_data = {
        "tournamentId": "61805002",
        "tournamentName": "Shepparton Cup",
        "season": "2025",
        "results": []
    }
    
    # Parse rankings (same as before)
    responses = rankings_data.get('responses', {})
    
    # Find all categories
    categories = {}
    for key, value in responses.items():
        if 'Category({categoryId:' in key and 'entity' in value:
            entity = value['entity']
            if '__typename' in entity and entity['__typename'] == 'Category':
                category_id = entity.get('id')
                name_field = entity.get('name', 'Unknown')
                if isinstance(name_field, dict):
                    category_name = name_field.get('en', 'Unknown')
                else:
                    category_name = name_field
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
            if '__typename' in entity and entity['__typename'] == 'Stage':
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
            if '__typename' in entity and entity['__typename'] == 'Team':
                team_id = entity.get('id')
                name_obj = entity.get('name', {})
                team_name = name_obj.get('fullName', name_obj.get('en', 'Unknown'))
                club_name = name_obj.get('clubName', 'Unknown Club')
                
                teams[str(team_id)] = {
                    'teamName': team_name,
                    'clubName': club_name
                }
    
    # Parse match scores from finals data
    finals_responses = finals_data.get('responses', {})
    
    # Collect MatchResult entities
    match_results = {}
    for key, value in finals_responses.items():
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
    
    # Collect Match entities with team info
    matches_by_team = {}
    for key, value in finals_responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'Match':
            match_id = str(entity.get('id'))
            home_href = entity.get('home', {}).get('href', '')
            away_href = entity.get('away', {}).get('href', '')
            round_name_href = entity.get('roundName', {}).get('href', '')
            division_href = entity.get('division', {}).get('href', '')
            
            # Store match info
            match_info = {
                'matchId': match_id,
                'homeHref': home_href,
                'awayHref': away_href,
                'roundNameHref': round_name_href,
                'divisionHref': division_href
            }
            
            # Add score if available
            if match_id in match_results:
                match_info.update(match_results[match_id])
            
            # We'll link this to teams later
            if match_id not in matches_by_team:
                matches_by_team[match_id] = match_info
    
    # Resolve team names and IDs from MatchActor entities
    for key, value in finals_responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'MatchActor':
            team_name = entity.get('name', {}).get('en', '')
            team_id = str(entity.get('id'))
            team_href = entity.get('team', {}).get('href', '')
            
            # Extract actual team ID from href
            team_id_match = re.search(r'Team\(\{id:(\d+)\}\)', team_href)
            actual_team_id = team_id_match.group(1) if team_id_match else team_id
            
            # Find matches that reference this actor
            for match_id, match_info in matches_by_team.items():
                if key == match_info.get('homeHref'):
                    match_info['homeTeam'] = team_name
                    match_info['homeTeamId'] = actual_team_id
                elif key == match_info.get('awayHref'):
                    match_info['awayTeam'] = team_name
                    match_info['awayTeamId'] = actual_team_id
    
    # Resolve round names
    for key, value in finals_responses.items():
        if not isinstance(value, dict) or 'entity' not in value:
            continue
        
        entity = value['entity']
        if not isinstance(entity, dict):
            continue
        
        if entity.get('__typename') == 'Match$RoundName':
            round_name = entity.get('name', {}).get('en', '')
            
            for match_id, match_info in matches_by_team.items():
                if key == match_info.get('roundNameHref'):
                    match_info['roundName'] = round_name
    
    # Build team matches mapping
    team_matches_map = {}
    for match_id, match_info in matches_by_team.items():
        if 'homeTeamId' not in match_info or 'awayTeamId' not in match_info:
            continue
        
        home_id = match_info['homeTeamId']
        away_id = match_info['awayTeamId']
        
        # Add match for home team
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
        
        # Add match for away team
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
    
    # Process rankings and add match scores
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

if __name__ == "__main__":
    rankings_file = "sample-results-reponse.json"
    finals_file = "finals-endpoint-response.json"
    output_file = "tournament-rankings-poc/web/src/data/realData.json"
    
    print("Parsing tournament with match scores...")
    print("=" * 80)
    
    tournament_data = parse_tournament_with_scores(rankings_file, finals_file)
    
    # Wrap in array for the frontend
    output_data = [tournament_data]
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Parsed data saved to {output_file}")
    print(f"  Tournament: {tournament_data['tournamentName']}")
    print(f"  Total results: {len(tournament_data['results'])}")
    
    # Count results with matches
    with_matches = sum(1 for r in tournament_data['results'] if 'matches' in r)
    print(f"  Results with match scores: {with_matches}")
    
    # Show sample
    print(f"\nSample results with match scores:")
    count = 0
    for result in tournament_data['results']:
        if 'matches' in result and count < 3:
            print(f"\n  {result['team']['teamName']} (Rank {result['rank']}) in {result['categoryName']}")
            for match in result['matches']:
                score = f"{match['homeGoals']}-{match['awayGoals']}" if match['isHome'] else f"{match['awayGoals']}-{match['homeGoals']}"
                result_text = "Won" if match['result'] == 'won' else "Lost"
                penalties = " (Penalties)" if match['penalties'] else ""
                print(f"    {result_text} {score} vs {match['opponent']} ({match['roundName']}){penalties}")
            count += 1
    
    print("\n" + "=" * 80)
