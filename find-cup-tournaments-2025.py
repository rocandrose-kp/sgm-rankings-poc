import json
import requests
from urllib.parse import urlparse
import time
import re

def get_tournament_id_from_me_api(website_url):
    """Fetch tournament ID using the Me API endpoint."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = "Me({optionalCupId:null}){cups:[{cup:{}}],teams:[{team:{shirt:{}}}]}"
        params = {'call': query}
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cups = data.get('responses', {}).get('Me({optionalCupId:null})$cups', {}).get('entity', [])
        if cups and len(cups) > 0:
            cup_id = cups[0].get('cupId')
            if cup_id:
                return str(cup_id)
        return None
    except Exception as e:
        return None

def check_tournament_has_finals(website_url, tournament_id):
    """Check if tournament has finals with results."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{finals:[{{... on Match:{{finished,result:{{}}}}}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if there are any finished finals
        responses = data.get('responses', {})
        for key, value in responses.items():
            if 'Match({id:' in key and isinstance(value, dict):
                entity = value.get('entity', {})
                if entity.get('finished') == True:
                    return True
        
        return False
    except Exception as e:
        return False

def check_tournament_has_rankings(website_url, tournament_id):
    """Check if tournament has rankings."""
    try:
        parsed = urlparse(website_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}/rest/results_api/call"
        
        query = f"Tournament({{id:{tournament_id}}}){{lotCategories:[{{stages:[{{rankings:[{{rank}}]}}]}}]}}"
        
        params = {
            'call': query,
            'lang': 'en',
            'tournamentId': tournament_id
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if there are any rankings
        responses = data.get('responses', {})
        for key, value in responses.items():
            if '$rankings' in key and isinstance(value, dict):
                entity = value.get('entity', [])
                if entity and len(entity) > 0:
                    return True
        
        return False
    except Exception as e:
        return False

# Load the monthly search results
print("\n" + "="*80)
print("FINDING CUP TOURNAMENTS WITH COMPLETED FINALS")
print("="*80 + "\n")

# Search for tournaments month by month
from datetime import datetime, timedelta

all_tournaments = []
months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

for month_num in range(1, 13):
    from_date = f"2025-{month_num:02d}-01"
    
    if month_num == 12:
        next_month = datetime(2026, 1, 1)
    else:
        next_month = datetime(2025, month_num + 1, 1)
    
    last_day = (next_month - timedelta(days=1)).day
    to_date = f"2025-{month_num:02d}-{last_day}"
    
    api_url = f'https://portal.cupmanager.net/rest/newportal/search?coords=[-38,145]&country=AU&date={to_date}&fromDate={from_date}&loc=Victoria&regions=[{{"nationId":25}}]&sport=football'
    
    print(f"{months[month_num-1]}: ", end='', flush=True)
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        for sport, categories in data.items():
            for category_type, tournament_list in categories.items():
                for tournament in tournament_list:
                    all_tournaments.append({
                        'name': tournament.get('name', 'Unknown'),
                        'websiteUrl': tournament.get('websiteUrl', ''),
                        'organizer': tournament.get('organizerName', ''),
                    })
        
        print(f"✓")
    except Exception as e:
        print(f"✗")
    
    time.sleep(0.3)

# Deduplicate
unique_tournaments = {}
for t in all_tournaments:
    url = t['websiteUrl']
    if url and url not in unique_tournaments:
        unique_tournaments[url] = t

print(f"\nFound {len(unique_tournaments)} unique tournaments")
print("\nChecking which tournaments have completed finals...\n")

# Check each tournament
cup_tournaments = []
checked = 0

for url, tournament_info in unique_tournaments.items():
    checked += 1
    name = tournament_info['name']
    website_url = tournament_info['websiteUrl']
    
    if not website_url:
        continue
    
    print(f"{checked}/{len(unique_tournaments)}. {name[:50]:<50} ", end='', flush=True)
    
    # Get tournament ID
    tournament_id = get_tournament_id_from_me_api(website_url)
    
    if not tournament_id:
        print("✗ No ID")
        continue
    
    # Check for rankings
    has_rankings = check_tournament_has_rankings(website_url, tournament_id)
    
    if not has_rankings:
        print("✗ No rankings")
        continue
    
    # Check for completed finals
    has_finals = check_tournament_has_finals(website_url, tournament_id)
    
    if has_finals:
        print("✓ CUP TOURNAMENT!")
        cup_tournaments.append({
            'name': name,
            'tournament_id': tournament_id,
            'website_url': website_url,
            'organizer': tournament_info['organizer']
        })
    else:
        print("✗ No finals")
    
    time.sleep(0.5)

# Save the list of cup tournaments
output_file = 'cup-tournaments-2025.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cup_tournaments, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total tournaments checked: {len(unique_tournaments)}")
print(f"Cup tournaments with completed finals: {len(cup_tournaments)}")
print(f"\n✓ Saved to: {output_file}")

if cup_tournaments:
    print(f"\nCup Tournaments Found:")
    for t in cup_tournaments:
        print(f"  - {t['name']} (ID: {t['tournament_id']})")

print("\n" + "="*80)
