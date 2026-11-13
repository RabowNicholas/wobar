# Build the label universe and artist index from the monthly genre release crawls.
# Window: releases live between 2024-11-11 and 2026-11-11. Pre-orders (date after today) excluded.
import json, glob, os, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'raw'); OUT = os.path.join(HERE, '..', 'data')
TODAY = '2026-11-11'; START = '2024-11-11'
GENRE = {'95': '140 / Deep Dubstep / Grime', '18': 'Dubstep'}

rels = {}  # release id -> record (a release can appear in both genre lists)
for f in sorted(glob.glob(os.path.join(RAW, 'rel_g*_*.json'))):
    d = json.load(open(f))
    for r in d['results']:
        live = max(r.get('pd') or '', r.get('nrd') or '')
        rid = r['id']
        if rid not in rels:
            rels[rid] = dict(r, genres=set(), live=live)
        rels[rid]['genres'].add(d['genre_id'])

def norm(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]', '', s)
    s = re.sub(r'\b(records|recordings|music|records llc|llc|ltd|label|audio)\b', '', s)
    return re.sub(r'\s+', ' ', s).strip()

labels = {}
artists = collections.defaultdict(lambda: {'name': None, 'labels': set(), 'releases': 0})
preorders = 0
for r in rels.values():
    if r['live'] > TODAY:
        preorders += 1; continue
    if r['live'] < START: continue
    L = r['label']; lid = L['id']
    lab = labels.setdefault(lid, {'id': lid, 'name': L['name'], 'slug': L['slug'], 'norm': norm(L['name']),
        'releases': 0, 'by_genre': collections.Counter(), 'artists': collections.Counter(), 'first': r['live'], 'last': r['live'],
        'hype_releases': 0, 'rel_6m': 0, 'rel_60d': 0, 'release_ids': []})
    lab['releases'] += 1; lab['release_ids'].append(r['id'])
    for g in r['genres']: lab['by_genre'][GENRE[g]] += 1
    for a in r['artists']:
        lab['artists'][a[0]] += 1
        artists[a[0]]['name'] = a[1]; artists[a[0]]['labels'].add(lid); artists[a[0]]['releases'] += 1
    lab['first'] = min(lab['first'], r['live']); lab['last'] = max(lab['last'], r['live'])
    if r.get('hype'): lab['hype_releases'] += 1
    if r['live'] >= '2026-05-11': lab['rel_6m'] += 1
    if r['live'] >= '2026-09-12': lab['rel_60d'] += 1

out_l = []
for l in labels.values():
    l2 = dict(l); l2['by_genre'] = dict(l['by_genre']); l2['artists'] = {str(k): v for k, v in l['artists'].items()}
    l2['n_artists'] = len(l['artists']); out_l.append(l2)
out_l.sort(key=lambda x: -x['releases'])
json.dump(out_l, open(os.path.join(OUT, 'universe_labels.json'), 'w'))
json.dump({str(k): {'name': v['name'], 'labels': sorted(v['labels']), 'releases': v['releases']} for k, v in artists.items()},
          open(os.path.join(OUT, 'artist_index.json'), 'w'))
dupes = collections.defaultdict(list)
for l in out_l: dupes[l['norm']].append((l['id'], l['name']))
json.dump({k: v for k, v in dupes.items() if len(v) > 1}, open(os.path.join(OUT, 'name_collisions.json'), 'w'), indent=1)
print('releases in window:', sum(l['releases'] for l in out_l), 'pre-orders excluded:', preorders)
print('labels:', len(out_l), 'artists:', len(artists), 'name collisions:', sum(1 for v in dupes.values() if len(v) > 1))
