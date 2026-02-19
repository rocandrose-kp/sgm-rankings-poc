import json

with open('all-real-tournaments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Found {len(data)} tournaments:\n')
for i, t in enumerate(data):
    print(f'{i+1}. {t["tournamentName"]} (ID: {t["tournamentId"]}) - {len(t["results"])} results')
