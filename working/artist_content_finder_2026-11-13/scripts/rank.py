# Step 3b: rank main-band gate passers by consistency of 10k+ view posts (Nick, 2026-11-16).
# Input data/gate.json + raw/reels_all.json. Output data/ranking.json, RANKING.csv.
import json, os, csv, statistics
from config import RAW, DATA, ROOT
g = json.load(open(os.path.join(DATA, 'gate.json')))
reels = {r['name']: r for r in json.load(open(os.path.join(RAW, 'reels_all.json')))}
rows = []
for n, v in g.items():
    if not v['pass'] or v['band'] != 'main': continue
    plats = []
    r = reels.get(n)
    if r and r.get('reels'):
        vs = [x['views'] for x in r['reels'] if not x.get('pinned') and x['views'] is not None][:12]
        if vs: plats.append(('ig', vs, v['ig_followers']))
    if v.get('tt_views12'):
        vs = [x for x in v['tt_views12'] if x is not None][:12]   # TikTok grid: pinned first, cannot tell; small effect
        if vs: plats.append(('tt', vs, v['tt_followers']))
    if not plats: continue
    best = max(plats, key=lambda p: (sum(1 for x in p[1] if x >= 10000), statistics.median(p[1])))
    plat, vs, fol = best
    med = statistics.median(vs)
    rows.append({'artist': n, 'platform': plat, 'handle': v['ig'] if plat == 'ig' else v['tt'], 'followers': fol, 'spotify': v['ml'],
                 'posts_read': len(vs), 'hits_10k': sum(1 for x in vs if x >= 10000), 'median_views': int(med),
                 'max_views': max(vs), 'reach_ratio': round(med / fol, 2) if fol else None})
rows.sort(key=lambda r: (-r['hits_10k'], -r['median_views']))
for i, r in enumerate(rows): r['rank'] = i + 1
json.dump(rows, open(os.path.join(DATA, 'ranking.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(ROOT, 'RANKING.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), 'ranked. hits_10k distribution:', sorted(Counter(r['hits_10k'] for r in rows).items(), reverse=True))
for r in rows[:35]: print(r['rank'], r['artist'], r['platform'], r['followers'], 'hits', r['hits_10k'], 'med', r['median_views'], 'ratio', r['reach_ratio'])
