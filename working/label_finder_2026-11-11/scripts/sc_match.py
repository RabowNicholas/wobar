# Confirm each label's SoundCloud account by matching track titles against its Beatport catalogue,
# then pull demo wording, emails and links from the confirmed account's bio.
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
from common import *

cats = load_cats()
merged = json.load(open(os.path.join(DATA, 'merged_ids.json')))
sc = {}
for f in sorted(glob.glob(os.path.join(RAW, 'sc_*.json'))):
    sc.update(json.load(open(f)))
OVR = {}
p = os.path.join(DATA, 'sc_overrides.json')
if os.path.exists(p): OVR = json.load(open(p))  # label id -> SC user id chosen by hand (with reason)

def norm(s):
    s = (s or '').lower()
    s = re.sub(r'\(.*?\)|\[.*?\]', ' ', s)
    s = re.sub(r'(original mix|extended mix|remix|vip|feat\.?|ft\.?)', ' ', s)
    return re.sub(r'[^a-z0-9]', '', s)

def bp_titles(lid):
    ids = [lid] + next((v for v in merged.values() if lid in v), [])
    t = set()
    for i in ids:
        for tr in cats.get(str(i), {}).get('tracks', []):
            n = norm(tr['n'])
            if len(n) >= 4: t.add(n)
    return t

EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
DOORWORD = re.compile(r'demo|submi|send (us )?(your )?music|unsigned|a&r', re.I)

def door_from(desc, links):
    desc = desc or ''
    lines = [l.strip() for l in re.split(r'[\n\r]+', desc) if l.strip()]
    door_lines = [l for l in lines if DOORWORD.search(l)]
    emails = EMAIL.findall(desc)
    demo_emails = sorted({e for e in emails if any(e in l for l in door_lines) or re.search(r'demo|submi|a&r|music@', e, re.I)})
    other_emails = sorted(set(emails) - set(demo_emails))
    door_links = [l for l in links if re.search(r'demo|submi|labelradar|forms\.gle|docs\.google|typeform|jotform|submithub|label-engine|trackstack', (l[0] or '') + ' ' + (l[1] or ''), re.I)]
    return {'door_lines': door_lines, 'demo_emails': demo_emails, 'other_emails': other_emails, 'door_links': door_links}

out = {}
for lid, v in sc.items():
    lid_i = int(lid); bt = bp_titles(lid_i)
    best = None
    for c in v['cands']:
        m = sum(1 for t in c.get('titles', []) if any(b in norm(t) for b in bt))
        c['matches'] = m
        if best is None or (m, c['followers']) > (best['matches'], best['followers']): best = c
    if lid in OVR:
        best = next((c for c in v['cands'] if c['id'] == OVR[lid]['sc_id']), best)
    if best is None:
        out[lid] = {'name': v['name'], 'sc': None, 'identity': 'no SoundCloud account found', 'search_top': v['users'][:3]}; continue
    ident = 'confirmed' if best['matches'] >= 3 else 'weak' if best['matches'] >= 1 else 'wrong or unmatched'
    out[lid] = {'name': v['name'], 'sc': {'id': best['id'], 'permalink': best['permalink'], 'username': best['username'], 'followers': best['followers'],
        'url': 'https://soundcloud.com/' + best['permalink'], 'country': best.get('country'), 'city': best.get('city')},
        'identity': ident, 'title_matches': best['matches'], 'bio': best.get('desc'), 'links': best.get('links', []),
        'door': door_from(best.get('desc'), best.get('links', [])),
        'other_cands': [(c['permalink'], c['followers'], c.get('matches')) for c in v['cands'] if c is not best]}
json.dump(out, open(os.path.join(DATA, 'sc_matched.json'), 'w'), indent=1)
from collections import Counter
print('labels', len(out), Counter(o['identity'] for o in out.values()))
print('with labelled demo email or demo link in bio:', sum(1 for o in out.values() if o.get('door') and (o['door']['demo_emails'] or o['door']['door_links'])))
