# Step 2 merge: SoundCloud handles (data/handles.json) + Instagram reads (raw/ig_all.json) + bio-link TikToks
# (raw/biolinks_out.tsv) -> data/handles_merged.json, plus data/missing_handles.csv for Nick.
import json, csv, os
from collections import Counter
from config import RAW, DATA, SOCIAL_MIN
h = json.load(open(os.path.join(DATA, 'handles.json')))
ig = {r['handle']: r for r in json.load(open(os.path.join(RAW, 'ig_all.json')))}
bl = {}
for l in open(os.path.join(RAW, 'biolinks_out.tsv')):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 4 and p[3]: bl[p[0]] = p[3].split(',')
beacons = {l.split('\t')[0] for l in open(os.path.join(RAW, 'biolinks_beacons_skipped.tsv'))}
out = {}
for name, v in h.items():
    r = dict(v); i = ig.get(v['ig']) if v['ig'] else None
    r['ig_status'] = i['status'] if i else (None if not v['ig'] else 'not read')
    r['ig_followers'] = i.get('followers') if i else None
    r['ig_posts'] = i.get('posts') if i else None
    r['ig_links'] = i.get('links') if i else None
    if i and i['status'] == 'missing': r['ig'] = None            # dead handle
    tt_src = 'soundcloud' if r['tt'] else None
    if not r['tt'] and i and i.get('tt'): r['tt'], tt_src = i['tt'].lower(), 'ig bio'
    if not r['tt'] and v['ig'] in bl:
        # several TikToks on one page: prefer one that shares a token with the IG handle or artist name
        c = bl[v['ig']]; key = (v['ig'] + name).lower().replace(' ', '')
        r['tt'] = next((t for t in c if t.replace('_', '').replace('.', '') in key or key.find(t[:5]) >= 0), c[0]); tt_src = 'bio link'
    r['tt_src'] = tt_src
    r['beacons'] = v['ig'] in beacons
    r['gate_ig'] = (r['ig_followers'] or 0) >= SOCIAL_MIN
    out[name] = r
json.dump(out, open(os.path.join(DATA, 'handles_merged.json'), 'w'), ensure_ascii=False, indent=1)
inband = {n: r for n, r in out.items() if r['band'] in ('main', 'stretch')}
print('in band:', len(inband))
print('ig ok:', sum(1 for r in inband.values() if r['ig_status'] == 'ok'), ' ig 10k+:', sum(1 for r in inband.values() if r['gate_ig']))
print('tt found:', sum(1 for r in inband.values() if r['tt']), Counter(r['tt_src'] for r in inband.values() if r['tt']))
print('no handle at all:', sum(1 for r in inband.values() if not r['ig'] and not r['tt']))
print('ig under 10k, no tt:', sum(1 for r in inband.values() if r['ig'] and not r['gate_ig'] and not r['tt']))
with open(os.path.join(DATA, 'missing_handles.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['artist', 'band', 'spotify_listeners', 'soundcloud', 'ig_found', 'ig_status', 'why'])
    for n, r in sorted(inband.items(), key=lambda x: -(x[1]['ml'] or 0)):
        if r['tt'] or r['gate_ig']: continue
        why = ('no handle found' if not r['ig'] else 'IG dead' if r['ig_status'] == 'missing' else
               'IG under 10k, no TikTok found')
        w.writerow([n, r['band'], r['ml'], r['sc'] or '', r['ig'] or r.get('ig_sc') or '', r['ig_status'] or '', why])
