# Build the candidate artist pool with Beatport titles for identity matching on Spotify.
import json, glob, os, collections
from config import *
idx = json.load(open(os.path.join(LF, 'data', 'artist_index.json')))
sets = json.load(open(os.path.join(LF, 'data', 'artist_sets.json')))
special = {str(a) for k in ('goal_artists', 'peer_artists', 'charting_artists') for a in sets[k]}
titles = collections.defaultdict(set)
for f in glob.glob(os.path.join(LF, 'raw', 'rel_g*_*.json')):
    for r in json.load(open(f))['results']:
        for a in r['artists']: titles[str(a[0])].add(r['name'])
for f in glob.glob(os.path.join(LF, 'raw', 'cat_*.json')):
    for e in json.load(open(f)).values():
        for t in e.get('tracks', []):
            for a in t['a']: titles[str(a[0])].update([t['n'], t['rn']])
ref = {n.lower() for n in REFERENCE}
pool = []
for aid, v in idx.items():
    why = []
    if v['releases'] >= POOL_MIN_RELEASES: why.append('releases')
    if aid in special: why.append('label/chart')
    if v['name'].lower() in ref: why.append('reference')
    if why:
        pool.append({'bp_id': aid, 'name': v['name'], 'releases': v['releases'], 'why': why, 'titles': sorted(titles[aid])[:40]})
found = {p['name'].lower() for p in pool}
for n in REFERENCE:
    if n.lower() not in found: pool.append({'bp_id': None, 'name': n, 'releases': 0, 'why': ['reference'], 'titles': []})
pool.sort(key=lambda p: (-('reference' in p['why']), -('label/chart' in p['why']), -p['releases']))
json.dump(pool, open(os.path.join(DATA, 'pool.json'), 'w'))
print('pool:', len(pool), collections.Counter(w for p in pool for w in p['why']))
