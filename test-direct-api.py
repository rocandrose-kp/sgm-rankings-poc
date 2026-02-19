import requests
import json

# Test the exact URLs provided by the user
test_urls = [
    "https://sheppartoncup.com/rest/results_api/call?call=Tournament({id:61805002}){finals:[],lotCategories:[{stages:[{rankings:[{...%20on%20Stage$StageRankingPlace_ConferencePlace:{conference:{matches:[{}]}},...%20on%20Stage$StageRankingPlace_MatchStatus:{match:{arena:{},away:{team:{club:{nation:{}}}},home:{team:{club:{nation:{}}}},roundName:{}}},team:{club:{nation:{}}}}]}]}]}&lang=en&tournamentId=61805002",
    "https://wucup.com.au/rest/results_api/call?call=Tournament({id:60652114}){finals:[],lotCategories:[{stages:[{rankings:[{... on Stage$StageRankingPlace_ConferencePlace:{conference:{matches:[{}]}},... on Stage$StageRankingPlace_MatchStatus:{match:{arena:{},away:{team:{club:{nation:{}}}},home:{team:{club:{nation:{}}}},roundName:{}}},team:{club:{nation:{}}}}]}]}]}&lang=en&tournamentId=60652114"
]

for url in test_urls:
    print(f"\nTesting: {url[:80]}...")
    try:
        response = requests.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors
            if 'responses' in data:
                for key, value in data['responses'].items():
                    if 'error' in value:
                        print(f"Error: {value['error'][:150]}")
                    else:
                        print(f"Success! Key: {key[:80]}")
                        # Save to file
                        filename = f"test-result-{key.split('(')[0]}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                        print(f"Saved to: {filename}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"Exception: {e}")
