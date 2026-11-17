# Identity check, step 2: second signal for names sp_match.py could not confirm by title.
# lane = how many of a candidate's "Fans also like" artists are in the pool (140 / dubstep universe).
# Writes data/identity_review.json: every main/stretch name that is ambiguous, unconfirmed, weakly
# confirmed (1 title hit) or missing a listener count, with all candidates and both signals.
import json, glob, os
from config import *
pool = json.load(open(os.path.join(DATA, 'pool.json')))
pnames = {p['name'].lower() for p in pool}
m = json.load(open(os.path.join(DATA, 'sp_matched.json')))
recs = {}
for f in sorted(glob.glob(os.path.join(RAW, 'sp_*.json'))):
    for r in json.load(open(f)): recs[r['name']] = r
for f in sorted(glob.glob(os.path.join(RAW, 'sp2_*.json'))):
    for r in json.load(open(f)): recs[r['name']] = r          # re-run wins
def band(ml):
    if ml is None: return None
    return 'main' if ML_MIN <= ml <= ML_MAX else 'stretch' if ML_MAX < ml <= ML_STRETCH_MAX else 'below' if ml < ML_MIN else 'above'
from sp_match_nt import nt
pt = {p['name']: {nt(t) for t in p['titles']} - {''} for p in pool}
def hits(name, c):
    sp = {nt(x) for x in c['rels']} | {nt(row.split(' | ')[1] if ' | ' in row else row) for row in c['rows']}
    return len(pt.get(name, set()) & sp)
def lane(c): return sum(1 for f in c['fans'] if f.split('|', 1)[-1].lower() in pnames)
ref = {n.lower() for n in REFERENCE}
review = []
for name, v in m.items():
    r = recs.get(name, {'cands': []})
    cands = [{'id': c['id'], 'hits': hits(name, c), 'ml': c['ml'], 'band': band(c['ml']), 'lane': lane(c), 'n_fans': len(c['fans']),
              'fans': [f.split('|', 1)[-1] for f in c['fans']][:8], 'rels': c['rels'][:6]} for c in r['cands']]
    in_scope = any(c['band'] in ('main', 'stretch') for c in cands) or name.lower() in ref
    st = v['status']
    why = ('ambiguous' if st == 'ambiguous' else 'unconfirmed' if st.startswith(('unconfirmed', 'reference')) else
           'weak' if st == 'confirmed' and v['title_hits'] == 1 else 'no ml' if st == 'confirmed' and v['ml'] is None else None)
    if why and in_scope:
        # auto rules: a candidate is IN if 2+ title hits, or 3+ pool artists in its fans; OUT if 0 hits and 0 lane
        good = [c for c in cands if c['hits'] >= 2 or c['lane'] >= 3]
        live = [c for c in cands if c['hits'] or c['lane']]
        if len(good) == 1 and len(live) == 1: dec, pick = 'auto in', good[0]['id']   # no rival with any signal
        elif not live: dec, pick = 'auto out', None
        else: dec, pick = 'review', None
        review.append({'name': name, 'why': why, 'ref': name.lower() in ref, 'was': v.get('sp_id'), 'decision': dec, 'pick': pick, 'cands': cands})
json.dump(review, open(os.path.join(DATA, 'identity_review.json'), 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(review), Counter((x['why'], x['decision']) for x in review))
print('changed pick:', [x['name'] for x in review if x['pick'] and x['pick'] != x['was']])
