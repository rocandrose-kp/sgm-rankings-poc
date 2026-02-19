import json
import re
from typing import Dict, List, Any

def parse_tournament_results(api_response: Dict[str, Any], tournament_id: str, tournament_name: str, season: str = "2025") -> Dict[str, Any]:
    """
    Parse the API response and extract tournament data in POC format.
    """
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
                if isinstance(name_field, dict):
                    category_name = name_field.get('en', 'Unknown')
                else:
                    category_name = name_field
                categories[category_id] = category_name
    
    # Extract teams
    teams = {}
    for key, value in responses.items():
        if 'Team({id:' in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict) and entity.get('__typename') == 'Team':
                team_id = str(entity.get('id', ''))
                name_obj = entity.get('name', {})
                if isinstance(name_obj, dict):
                    team_name = name_obj.get('fullName', name_obj.get('en', f'Team {team_id}'))
                    club_name = name_obj.get('clubName', 'Unknown Club')
                else:
                    team_name = str(name_obj)
                    club_name = 'Unknown Club'
                
                teams[team_id] = {
                    'teamName': team_name,
                    'clubName': club_name
                }
    
    # Extract stage types (Cup Final vs Plate Final)
    stage_types = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' not in key and 'entity' in value:
            entity = value['entity']
            if isinstance(entity, dict) and entity.get('__typename') == 'Stage':
                match = re.search(r'categoryId:(\d+)', key)
                if match:
                    category_id = match.group(1)
                    stage_name = entity.get('name', '')
                    stage_type = entity.get('type', '')
                    
                    # Determine stage type
                    if 'Cup' in stage_name or 'Final' in stage_name:
                        stage_types[category_id] = 'CUP_FINAL'
                    elif 'Plate' in stage_name:
                        stage_types[category_id] = 'PLATE_FINAL'
                    else:
                        stage_types[category_id] = 'CUP_FINAL'
    
    # Extract rankings
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' in key:
            match = re.search(r'categoryId:(\d+)', key)
            if not match:
                continue
            
            category_id = match.group(1)
            category_name = categories.get(category_id, f'Category {category_id}')
            stage_type = stage_types.get(category_id, 'CUP_FINAL')
            
            rankings = value.get('entity', [])
            if not isinstance(rankings, list):
                continue
            
            for ranking in rankings:
                if not isinstance(ranking, dict):
                    continue
                
                typename = ranking.get('__typename', '')
                if 'StageRankingPlace' not in typename:
                    continue
                
                rank = ranking.get('rank')
                if rank is None:
                    continue
                
                # Extract team ID from href
                team_href = ranking.get('team', {}).get('href', '')
                team_match = re.search(r'Team\(\{id:(\d+)\}\)', team_href)
                if not team_match:
                    continue
                
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
                
                tournament_data['results'].append(result_entry)
    
    return tournament_data

def combine_tournaments(tournament_files: List[str], output_file: str):
    """
    Combine multiple tournament result files into one.
    """
    all_tournaments = []
    
    for file_path in tournament_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tournament = json.load(f)
                all_tournaments.append(tournament)
                print(f"✓ Loaded {tournament['tournamentName']}: {len(tournament['results'])} results")
        except Exception as e:
            print(f"✗ Error loading {file_path}: {e}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_tournaments, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Combined {len(all_tournaments)} tournaments into {output_file}")
    return all_tournaments

if __name__ == "__main__":
    # Parse the test results we just fetched
    print("Parsing WU Cup results...")
    
    # The test saved to test-result-Tournament.json
    with open('test-result-Tournament.json', 'r', encoding='utf-8') as f:
        wu_cup_data = json.load(f)
    
    # We need the full response, let me check what files were created
    import os
    test_files = [f for f in os.listdir('.') if f.startswith('test-result-')]
    print(f"Found {len(test_files)} test result files")
    
    # We need to reconstruct the full response
    # For now, let's use the sample-results-reponse.json we already have
    print("\nUsing existing Shepparton Cup data...")
    with open('shepparton-cup-parsed.json', 'r', encoding='utf-8') as f:
        shepparton_data = json.load(f)
    
    print(f"✓ Shepparton Cup: {len(shepparton_data['results'])} results")
