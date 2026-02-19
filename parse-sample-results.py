import json

def parse_shepparton_cup_results(results_file):
    """
    Parse the sample-results-reponse.json file and extract tournament data
    in the format needed for the POC.
    """
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tournament_data = {
        "tournamentId": "61805002",
        "tournamentName": "Shepparton Cup",
        "season": "2025",
        "results": []
    }
    
    # Extract categories and their rankings
    responses = data.get('responses', {})
    
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
    
    print(f"Found {len(categories)} categories:")
    for cat_id, cat_name in categories.items():
        print(f"  - {cat_id}: {cat_name}")
    
    # Find all stages with rankings
    stages_with_rankings = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' in key:
            # Extract categoryId from key
            import re
            match = re.search(r'categoryId:(\d+)', key)
            if match:
                category_id = match.group(1)
                rankings = value.get('entity', [])
                if rankings:
                    stages_with_rankings[category_id] = {
                        'key': key,
                        'rankings': rankings
                    }
    
    print(f"\nFound {len(stages_with_rankings)} stages with rankings")
    
    # Get stage information to determine if it's Cup Final or Plate Final
    stage_types = {}
    for key, value in responses.items():
        if 'Stage({categoryId:' in key and '$rankings' not in key and 'entity' in value:
            entity = value['entity']
            if '__typename' in entity and entity['__typename'] == 'Stage':
                import re
                match = re.search(r'categoryId:(\d+)', key)
                if match:
                    category_id = match.group(1)
                    stage_name = entity.get('name', '')
                    stage_type = entity.get('type', '')
                    
                    # Determine if Cup or Plate final
                    if 'Cup' in stage_name or stage_type == 'playoff':
                        stage_types[category_id] = 'CUP_FINAL'
                    elif 'Plate' in stage_name:
                        stage_types[category_id] = 'PLATE_FINAL'
                    else:
                        stage_types[category_id] = 'CUP_FINAL'  # Default
    
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
    
    print(f"Found {len(teams)} teams")
    
    # Process rankings
    result_count = 0
    for category_id, stage_data in stages_with_rankings.items():
        category_name = categories.get(category_id, f"Category {category_id}")
        stage_type = stage_types.get(category_id, 'CUP_FINAL')
        
        rankings = stage_data['rankings']
        
        for ranking in rankings:
            if '__typename' in ranking and 'StageRankingPlace' in ranking['__typename']:
                rank = ranking.get('rank')
                team_href = ranking.get('team', {}).get('href', '')
                
                # Extract team ID from href
                import re
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
                    
                    tournament_data['results'].append(result_entry)
                    result_count += 1
    
    print(f"\nExtracted {result_count} results")
    return tournament_data

if __name__ == "__main__":
    input_file = "sample-results-reponse.json"
    output_file = "shepparton-cup-parsed.json"
    
    print("Parsing Shepparton Cup results...")
    print("=" * 60)
    
    tournament_data = parse_shepparton_cup_results(input_file)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tournament_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Parsed data saved to {output_file}")
    print(f"  Tournament: {tournament_data['tournamentName']}")
    print(f"  Total results: {len(tournament_data['results'])}")
    
    # Show sample results
    print(f"\nSample results:")
    for result in tournament_data['results'][:5]:
        print(f"  - {result['team']['teamName']} (Rank {result['rank']}) in {result['categoryName']}")
