# Identity check, step 3: hand calls (Claude, 2026-11-16) on the 'review' cases from identity.py,
# then the final identity table: data/identity.json = sp_matched.json with every review case resolved.
# Calls: a Spotify id = right person; None = drop (no candidate is this artist, or the right one is under 10k);
# 'ASK' = waiting on Nick. Pick is by listeners when one candidate is unambiguous.
# OFFLANE = right person, but not a 140 / dubstep / grime artist (on Beatport through a remix or a vocal).
# This is only a flag for the lane-tagging step; nothing is dropped for it here.
import json, os
from config import *
R = json.load(open(os.path.join(DATA, 'identity_review.json')))
m = json.load(open(os.path.join(DATA, 'sp_matched.json')))

def band(ml):
    return 'main' if ML_MIN <= ml <= ML_MAX else 'stretch' if ML_MAX < ml <= ML_STRETCH_MAX else 'below' if ml < ML_MIN else 'above'
def by_ml(name, ml):           # the candidate with this listener count
    x = next(x for x in R if x['name'] == name)
    return next(c['id'] for c in x['cands'] if c['ml'] == ml)

KEEP = {  # name: listener count of the right candidate
    'Splasher!': 74993, 'XI': 91135, 'Darkzy': 174288, 'Lookas': 66820, 'Capo Lee': 302726, 'Bossfight': 270238,
    'Caslow': 67757, 'Opus': 70721, '4B': 182501, 'Emalkay': 51571, 'Wubbaduck': 46624, 'Aether': 103895,
    'Ruby Chase': 215850, 'Slynk': 13179, 'XaeboR': 16653, 'Trinist': 13856, 'King Marino': 10120, 'Top Cat': 172604,
    'Tantron': 46026, 'Bright Lights': 87492, 'Brainrot': 16331, 'Manno': 10977, 'Monika Santucci': 63482,
    'Da Fuchaman': 110226, 'GLNNA': 31633, 'Minke': 158635, 'Matilda Pearl': 10292, 'Lexi Scatena': 450953,
    'The Upbeats': 162506, 'Dead Hippie': 80766, 'Polar Youth': 27721, 'Twin Shadow': 326371, 'Sean Price': 140421,
    'Perry Farrell': 92073, 'Ryster': 33050, 'Deep Notion': 28531, 'ALOTT': 294566, 'Sakshi Chopra': 50191,
    'Danny Byrd': 331722, 'Jolliffe': 58309, 'Lady Leshurr': 219686, 'Lens': 334890, 'Émilie Rachel': 141313,
    'Sworra': 26867, 'Tenebrax': 44968, 'SLPSLIDE': 13360, 'Manga Saint Hilare': 64635, 'Gorillag': 29236,
    'Jammz': 53795, "Shaquille O'Neal": 342584, 'Magnus Deus': 21834, 'Machinedrum': 244928, 'Koherent': 87394,
    'Jianbo': 43349, 'Taelimb': 45249, 'The Great Medicine Show': 24351, 'ZABO': 120808, 'Stooki Sound': 21909,
    'Emerel Gray': 159291, 'Teej': 48128, 'Qua Rush': 10602, 'The Hyphenate': 77431, 'Judo Keys': 62409,
    'vai5000': 27340, 'Mizter Bonezz': 17415, 'Black Sun Empire': 122679, 'DJ Shon': 11882, 'Mark Holiday': 25216,
    'Mad Sam': 72652, 'Brandon Szabo': 13590, 'Reece Rosé': 11759, 'Josh Nor': 13373, 'DJ Hybrid': 82777,
    'Signs of the Swarm': 221660, 'Youthstar': 47740, 'Potions': 31965,
}
DROP = ['Infraction', 'Mani', 'SFY', 'Sukuward', 'Athena (US)', 'Shimmer', 'DJ Astro', 'Recall', 'CXB', 'Kooky', 'Alar3']
# Nick's answers 2026-11-16: Alex Unger = the 52,739 candidate; Fly = a page the search never reached (link from Nick,
# listeners read from the public page 2026-11-16); highrollr out; Noctiil releases on SoundCloud only (no Spotify band,
# stays as a reference for the social read); "don't worry about any of the others" = drop.
KEEP['Alex Unger'] = 52739
MANUAL = {'Fly': {'sp_id': '5uzvRvcTtbA3JqZxglgTda', 'ml': 109700, 'band': 'stretch', 'identity': 'resolved (Nick link)'},
          'Noctiil': {'sp_id': None, 'ml': None, 'band': None, 'identity': 'soundcloud only (Nick)'}}
DROP += ['highrollr', 'UNDY', 'N3ptune', 'Lucid', 'Dusty', 'Ondamike', 'Bsharry', 'Aaron Gillespie']
ASK = []
OFFLANE = ['XI', 'Bossfight', 'Bright Lights', 'Monika Santucci', 'Minke', 'Matilda Pearl', 'Lexi Scatena', 'Twin Shadow',
           'Sean Price', 'Perry Farrell', 'ALOTT', 'Sakshi Chopra', 'Émilie Rachel', "Shaquille O'Neal", 'Magnus Deus',
           'Mark Holiday', 'Emerel Gray', 'Signs of the Swarm', 'Mizter Bonezz', 'Dead Hippie']

out = {}
for x in R:
    n = x['name']
    if n in MANUAL: call = 'MANUAL'
    elif x['decision'] == 'auto in': call = x['pick']
    elif n in KEEP: call = by_ml(n, KEEP[n])
    elif n in DROP: call = None
    elif x['decision'] == 'auto out': call = None
    elif n in KEEP: call = by_ml(n, KEEP[n])
    elif n in DROP: call = None
    elif n in ASK: call = 'ASK'
    else: raise SystemExit('no call for ' + n)
    out[n] = call
ident = {}
for n, v in m.items():
    if n not in out:
        if v['status'] == 'confirmed': ident[n] = {**v, 'identity': 'confirmed'}
        else: ident[n] = {'status': v['status'], 'identity': 'out of scope'}   # unresolved but no in-band candidate
        continue
    call = out[n]
    if n in MANUAL: ident[n] = {'status': v['status'], 'bp_id': v.get('bp_id'), 'reference': True, **MANUAL[n]}; continue
    if call == 'ASK': ident[n] = {**v, 'identity': 'ask nick'}; continue
    if call is None: ident[n] = {'status': v['status'], 'identity': 'dropped'}; continue
    x = next(x for x in R if x['name'] == n); c = next(c for c in x['cands'] if c['id'] == call)
    ident[n] = {**v, 'sp_id': call, 'ml': c['ml'], 'band': c['band'], 'identity': 'resolved' if call != v.get('sp_id') or v['status'] != 'confirmed' else 'confirmed'}
    if n in OFFLANE: ident[n]['offlane'] = True
# 27 confirmed pages loaded without a listener count; re-read 2026-11-16 from the public page's og:description
import re
for line in open(os.path.join(RAW, 'og_ml_2026-11-16.tsv')):
    sid, n, desc = line.rstrip('\n').split('\t')
    mm = re.search(r'([\d.]+)(K|M)? monthly listeners', desc)
    if n in ident and mm:
        ml = int(float(mm[1]) * {'K': 1e3, 'M': 1e6}.get(mm[2], 1))
        ident[n].update(ml=ml, band=band(ml))
json.dump(ident, open(os.path.join(DATA, 'identity.json'), 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print(Counter(v['identity'] for v in ident.values()))
print(Counter(v.get('band') for v in ident.values() if v['identity'] in ('confirmed', 'resolved') and not v.get('offlane')))
