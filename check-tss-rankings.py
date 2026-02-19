import json
import requests

# TSS Football Tournament
tournament_id = "54663955"
url = "https://tssfootballtournament.cupmanager.net/rest/results_api/call"

query = f"Tournament({{id:{tournament_id}}}){{lotCategories:[{{stages:[{{rankings:[{{... on Stage$StageRankingPlace_ConferencePlace:{{conference:{{matches:[{{}}]}}}},... on Stage$StageRankingPlace_MatchStatus:{{match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},home:{{team:{{club:{{nation:{{}}}}}}}},roundName:{{}}}}}},team:{{club:{{nation:{{}}}}}}}}]}}]}}]}}"

params = {
    'call': query,
    'lang': 'en',
    'tournamentId': tournament_id
}

print("Fetching TSS Football Tournament data...")
response = requests.get(url, params=params, timeout=30)
data = response.json()

# Save full response
with open('debug-tss-tournament.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✓ Saved to: debug-tss-tournament.json")

# Analyze rankings
responses = data.get('responses', {})
print(f"\nTotal response keys: {len(responses)}")

# Check for rankings
rankings_found = []
for key, value in responses.items():
    if '$rankings' in key and isinstance(value, dict):
        entity = value.get('entity', [])
        if entity and len(entity) > 0:
            rankings_found.append({
                'key': key,
                'count': len(entity)
            })

print(f"\nRankings found: {len(rankings_found)}")
if rankings_found:
    print("\nRanking details:")
    for r in rankings_found:
        print(f"  - {r['key']}: {r['count']} entries")
        
    # Show sample ranking
    first_ranking_key = rankings_found[0]['key']
    first_ranking = responses[first_ranking_key]['entity'][0]
    print(f"\nSample ranking entry:")
    print(json.dumps(first_ranking, indent=2))
else:
    print("✗ No rankings found")

# Count entity types
entity_types = {}
for key, value in responses.items():
    if isinstance(value, dict) and 'entity' in value:
        entity = value['entity']
        if isinstance(entity, dict):
            typename = entity.get('__typename', 'Unknown')
            entity_types[typename] = entity_types.get(typename, 0) + 1
        elif isinstance(entity, list) and len(entity) > 0:
            entity_types['List'] = entity_types.get('List', 0) + 1

print("\nEntity types:")
for typename, count in sorted(entity_types.items()):
    print(f"  - {typename}: {count}")
