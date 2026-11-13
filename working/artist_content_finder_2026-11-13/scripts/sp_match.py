# Pick the right Spotify artist per pool name: title overlap with Beatport (releases, track rows), then size bands.
import json, glob, os, re
from config import *
pool = {p['name']: p for p in json.load(open(os.path.join(DATA, 'pool.json')))}
def nt(s):
    s = s.lower(); s = re.sub(r'\((original|extended|radio|vip|clean|dirty)[^)]*\)', '', s)
    s = re.sub(r'\b(original mix|extended mix|feat\.?.*|ft\..*)$', '', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
recs = []
for f in sorted(glob.glob(os.path.join(RAW, 'sp_*.json'))): recs += json.load(open(f))
# v2 re-run (stale-results fix) replaces v1 records for the same name
recs2 = [r for f in sorted(glob.glob(os.path.join(RAW, 'sp2_*.json'))) for r in json.load(open(f))]
redo = {r['name'] for r in recs2}
recs = [r for r in recs if r['name'] not in redo] + recs2
out = {}
for r in recs:
    p = pool.get(r['name']); bt = {nt(t) for t in (p['titles'] if p else [])} - {''}
    best = None
    for c in r['cands']:
        sp_t = {nt(x) for x in c['rels']} | {nt(row.split(' | ')[1] if ' | ' in row else row) for row in c['rows']}
        c['title_hits'] = len(bt & sp_t)
        if best is None or (c['title_hits'], c['ml'] or 0) > (best['title_hits'], best['ml'] or 0): best = c
    if not best: out[r['name']] = {'status': 'not found'}; continue
    if best['title_hits'] >= 1: status = 'confirmed'
    elif len(r['cands']) == 1 and 'reference' in (p or {}).get('why', []): status = 'reference, single match'
    elif len(r['cands']) == 1: status = 'unconfirmed (single exact name)'
    else: status = 'ambiguous'
    plays = []
    for row in best['rows']:
        parts = row.split(' | ')
        n = next((int(x.replace(',', '')) for x in parts[2:] if re.fullmatch(r'[\d,]{4,}', x)), None)
        plays.append([parts[1] if len(parts) > 1 else row, n])
    ml = best['ml']
    band = None if ml is None else 'main' if ML_MIN <= ml <= ML_MAX else 'stretch' if ML_MAX < ml <= ML_STRETCH_MAX else 'below' if ml < ML_MIN else 'above'
    out[r['name']] = {'status': status, 'sp_id': best['id'], 'ml': ml, 'band': band, 'title_hits': best['title_hits'],
                      'n_cands': len(r['cands']), 'top_tracks': plays, 'fans': best['fans'], 'tour': best['tour'], 'bp_id': (p or {}).get('bp_id')}
json.dump(out, open(os.path.join(DATA, 'sp_matched.json'), 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print(len(out), Counter(v['status'] for v in out.values()))
print(Counter((v.get('band'), v['status'].split(' ')[0]) for v in out.values()))
