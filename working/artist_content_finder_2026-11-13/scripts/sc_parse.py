# Step 2: pick each artist's SoundCloud profile and pull TikTok / Instagram handles from it.
# Input raw/sc_*.json (sc_page_crawl.js output). Output data/handles.json.
# Profile pick: SoundCloud track titles overlapping the artist's Beatport titles or Spotify top tracks
# ('sc_conf': 'titles'), else the most-followed exact-name profile ('followers', weaker).
import json, glob, os, re
from config import *
from sp_match_nt import nt
pool = {p['name']: p for p in json.load(open(os.path.join(DATA, 'pool.json')))}
ident = json.load(open(os.path.join(DATA, 'identity.json')))
recs = {}
for f in sorted(glob.glob(os.path.join(RAW, 'sc_*.json'))):
    for r in json.load(open(f)): recs[r['name']] = r
def handle(link, site):
    m = re.match(site + r'\.com/@?([\w.]+)', link)
    return m[1].lower() if m and m[1].lower() not in ('p', 'reel', 'explore', 'share', 'video') else None
def bio_handle(s, site):
    s = s.lower()
    m = re.search(site + r'\.com/@?([\w.]+)', s)
    if m: return m[1]
    if site == 'instagram' and re.match(r'(ig|insta|instagram)\b', s): return s.split('@')[-1]
    if site == 'tiktok' and re.match(r'(tiktok|tt)\b', s): return s.split('@')[-1]
out = {}
for name, r in recs.items():
    v = ident.get(name, {})
    known = {nt(t) for t in pool.get(name, {}).get('titles', [])} | {nt(t[0]) for t in v.get('top_tracks', []) if t and t[0]}
    known -= {''}
    best, conf = None, None
    for c in r['cands']:
        c['hits'] = len(known & {nt(t) for t in c['titles']})
    ranked = sorted(r['cands'], key=lambda c: (c['hits'], c['followers'] or 0), reverse=True)
    if ranked:
        best = ranked[0]; conf = 'titles' if best['hits'] else 'followers'
    rec = {'band': v.get('band'), 'ml': v.get('ml'), 'search': r.get('search'), 'sc': None, 'sc_conf': conf,
           'ig': None, 'tt': None, 'yt': None, 'others': r.get('others', [])}
    if best:
        rec.update(sc=best['path'].strip('/'), sc_followers=best['followers'], sc_hits=best['hits'])
        for l in best['links']:
            rec['ig'] = rec['ig'] or handle(l, 'instagram')
            rec['tt'] = rec['tt'] or handle(l, 'tiktok')
            if l.startswith(('youtube.com', 'youtu.be')): rec['yt'] = rec['yt'] or l
        for b in best['bioHandles']:
            rec['ig'] = rec['ig'] or bio_handle(b, 'instagram')
            rec['tt'] = rec['tt'] or bio_handle(b, 'tiktok')
    # a followers-only pick with under 1k SoundCloud followers, for an artist with 10k+ Spotify listeners,
    # is most likely a same-name stranger: keep the profile for reference but do not trust its handles
    if conf == 'followers' and (rec.get('sc_followers') or 0) < 1000:
        rec['sc_conf'] = 'untrusted'; rec['ig_sc'], rec['tt_sc'] = rec['ig'], rec['tt']; rec['ig'] = rec['tt'] = None
    out[name] = rec
json.dump(out, open(os.path.join(DATA, 'handles.json'), 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), 'sc profile:', Counter(v['sc_conf'] for v in out.values()))
print('ig:', sum(1 for v in out.values() if v['ig']), 'tt:', sum(1 for v in out.values() if v['tt']),
      'neither:', sum(1 for v in out.values() if not v['ig'] and not v['tt']))
