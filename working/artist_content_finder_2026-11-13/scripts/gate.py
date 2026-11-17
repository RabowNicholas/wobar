# Step 2 final: TikTok reads (raw/tt_all.json) merged into data/handles_merged.json -> data/gate.json + CSVs.
# TikTok accepted when: known handle (h); IG handle on TikTok with matching display name (g); name search with
# music words in the bio (s). Search matches without music words are kept as 'tt_unverified' for Nick, not counted.
import json, os, csv
from collections import Counter
from config import RAW, DATA, ROOT, SOCIAL_MIN
m = json.load(open(os.path.join(DATA, 'handles_merged.json')))
tt = {r['name']: r for r in json.load(open(os.path.join(RAW, 'tt_all.json')))}
NICK = json.load(open(os.path.join(RAW, 'nick_answers_2026-11-16.json')))
IGN = {r['name']: r for r in json.load(open(os.path.join(RAW, 'ig_nick.json')))}
gate = {}
for n, r in m.items():
    if r['band'] not in ('main', 'stretch'): continue
    t = tt.get(n, {}); ok = t.get('st') == 'ok'
    acc = ok and (t['mode'] == 'h' or (t['mode'] == 'g' and t.get('name_match')) or (t['mode'] == 's' and t.get('music')))
    g = {'band': r['band'], 'ml': r['ml'], 'sc': r['sc'], 'ig': r['ig'] if r['ig_status'] == 'ok' else None,
         'ig_followers': r['ig_followers'] if r['ig_status'] == 'ok' else None, 'ig_posts': r['ig_posts'],
         'tt': t.get('handle') if acc else None, 'tt_followers': t.get('followers') if acc else None,
         'tt_likes': t.get('likes') if acc else None, 'tt_views12': t.get('views') if acc else None,
         'tt_how': {'h': 'known', 'g': 'same handle as IG', 's': 'name search + music bio, confirmed by Nick' if n in NICK.get('tt_name_search_confirmed', []) else 'name search + music bio'}.get(t.get('mode')) if acc else None,
         'tt_unverified': [t.get('handle'), t.get('followers')] if ok and not acc else None}
    # Nick's answers 2026-11-16 (raw/nick_answers_2026-11-16.json): confirmed TikToks, Instagram handles he found
    if n in NICK['tt_confirmed'] and t.get('handle') == NICK['tt_confirmed'][n]:
        g.update(tt=t['handle'], tt_followers=t.get('followers'), tt_likes=t.get('likes'), tt_views12=t.get('views'),
                 tt_how='name search, confirmed by Nick', tt_unverified=None)
    elif g['tt_unverified']: g['tt_unverified'] = None          # Nick: every other list-A match is a stranger
    if n in IGN and IGN[n].get('status') == 'ok':
        g.update(ig=IGN[n]['handle'], ig_followers=IGN[n]['followers'], ig_posts=IGN[n]['posts'], ig_how='given by Nick')
    best = max(g['ig_followers'] or 0, g['tt_followers'] or 0)
    g['social_max'] = best; g['pass'] = best >= SOCIAL_MIN
    g['via'] = 'both' if (g['ig_followers'] or 0) >= SOCIAL_MIN and (g['tt_followers'] or 0) >= SOCIAL_MIN else \
               'ig' if (g['ig_followers'] or 0) >= SOCIAL_MIN else 'tt' if (g['tt_followers'] or 0) >= SOCIAL_MIN else None
    g['status'] = 'pass' if g['pass'] else ('no handle' if not g['ig'] and not g['tt'] else 'under 10k')
    gate[n] = g
json.dump(gate, open(os.path.join(DATA, 'gate.json'), 'w'), ensure_ascii=False, indent=1)
print(Counter((g['band'], g['status']) for g in gate.values()))
print('pass via:', Counter(g['via'] for g in gate.values() if g['pass']))
cols = ['artist', 'band', 'spotify_listeners', 'ig', 'ig_followers', 'tt', 'tt_followers', 'tt_how', 'status', 'tt_unverified']
def row(n, g): return [n, g['band'], g['ml'], g['ig'] or '', g['ig_followers'] or '', g['tt'] or '', g['tt_followers'] or '', g['tt_how'] or '', g['status'],
                      '' if not g['tt_unverified'] else f"@{g['tt_unverified'][0]} ({g['tt_unverified'][1]})"]
srt = lambda d: sorted(d.items(), key=lambda x: (x[1]['band'] != 'main', -(x[1]['ml'] or 0)))
with open(os.path.join(ROOT, 'GATE_PASS.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(cols); [w.writerow(row(n, g)) for n, g in srt(gate) if g['pass']]
with open(os.path.join(ROOT, 'GATE_NEEDS_NICK.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(cols); [w.writerow(row(n, g)) for n, g in srt(gate) if not g['pass']]
