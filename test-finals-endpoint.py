import requests
import json
import re

# Test the finals endpoint suggested by user
TOURNAMENT_ID = "61805002"  # Shepparton Cup
API_URL = f"https://wucup.com.au/rest/results_api/call?call=Tournament({{id:{TOURNAMENT_ID}}}){{finals:[{{...%20on%20Match:{{arena:{{}},away:{{team:{{club:{{nation:{{}}}}}}}},division:{{category:{{}},stage:{{}}}},home:{{team:{{club:{{nation:{{}}}}}}}},protests:[{{}}],result:{{}},roundName:{{}},stage:{{}},video:{{}}}}}}]}}&lang=en&tournamentId={TOURNAMENT_ID}"

print("=" * 80)
print("TESTING FINALS ENDPOINT FOR MATCH SCORES")
print("=" * 80)
print(f"\nTournament ID: {TOURNAMENT_ID}")
print(f"\nFetching from: {API_URL[:100]}...")

try:
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    print(f"\n✓ Successfully fetched data")
    print(f"Response keys: {list(data.keys())}")
    
    if 'responses' in data:
        responses = data['responses']
        print(f"\nResponses type: {type(responses)}")
        
        if isinstance(responses, dict):
            print(f"Number of response entities: {len(responses)}")
            
            # Look for MatchResult entities
            match_results = {}
            matches = {}
            
            for key, value in responses.items():
                if not isinstance(value, dict):
                    continue
                    
                if 'MatchResult({id:' in key:
                    match_id = re.search(r'MatchResult\(\{id:(\d+)\}\)', key)
                    if match_id and 'entity' in value:
                        match_results[match_id.group(1)] = value['entity']
                        
                if 'Match({id:' in key and 'entity' in value:
                    entity = value['entity']
                    if isinstance(entity, dict) and entity.get('__typename') == 'Match':
                        match_id = str(entity.get('id'))
                        matches[match_id] = entity
        elif isinstance(responses, list):
            print(f"Responses is a list with {len(responses)} items")
            print(f"First item type: {type(responses[0]) if responses else 'N/A'}")
            if responses:
                print(f"First item sample: {str(responses[0])[:200]}")
            matches = {}
            match_results = {}
        
        print(f"\nFound {len(matches)} Match entities")
        print(f"Found {len(match_results)} MatchResult entities")
        
        if match_results:
            print("\n" + "=" * 80)
            print("MATCH RESULT ENTITIES FOUND!")
            print("=" * 80)
            for match_id, result in list(match_results.items())[:3]:
                print(f"\nMatch ID: {match_id}")
                print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 80)
            print("NO MATCH RESULT ENTITIES IN RESPONSE")
            print("=" * 80)
            print("\nSample Match entity:")
            if matches:
                sample_match = list(matches.values())[0]
                print(json.dumps(sample_match, indent=2)[:1000])
                
                # Check if result is referenced
                if 'result' in sample_match:
                    print(f"\n⚠️  Match has result reference: {sample_match['result']}")
                    print("    But MatchResult entity is NOT resolved in response")
        
        # Save full response for analysis
        with open('finals-endpoint-response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved full response to: finals-endpoint-response.json")
        
except requests.exceptions.RequestException as e:
    print(f"\n✗ Request failed: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
This endpoint provides finals matches but still uses href references for MatchResult.
To get actual scores, we would need to:
1. Parse MatchResult hrefs from the response
2. Make additional API calls to fetch each MatchResult entity
3. Extract score data from those entities

The endpoint DOES make it easier by filtering to finals only, but doesn't
eliminate the need for additional API calls to get scores.
""")
