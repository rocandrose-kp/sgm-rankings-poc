import json

with open('tournament-rankings-poc/web/src/data/realData.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total tournaments: {len(data)}\n')
for i, t in enumerate(data):
    with_matches = sum(1 for r in t['results'] if 'matches' in r)
    print(f'{i+1}. {t["tournamentName"]}: {len(t["results"])} results, {with_matches} with match scores')
