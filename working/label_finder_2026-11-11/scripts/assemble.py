# Build List A, List B and the side lists from gates + SoundCloud + doors. Rules as approved 2026-11-11.
import json, os, sys, statistics, csv
sys.path.insert(0, os.path.dirname(__file__))
from common import *; from config import *

G = {r['id']: r for r in json.load(open(os.path.join(DATA, 'gates.json')))}
S = json.load(open(os.path.join(DATA, 'sc_matched.json')))
M = json.load(open(os.path.join(DATA, 'sc_manual.json')))
D = json.load(open(os.path.join(DATA, 'doors.json')))
OWN = json.load(open(os.path.join(DATA, 'owners.json')))
MERGED = json.load(open(os.path.join(DATA, 'merged_ids.json')))
A = json.load(open(os.path.join(DATA, 'artist_index.json')))
RS = {r['id']: r for r in json.load(open(os.path.join(DATA, 'rsi_all.json')))}
SNAP = '2026-11-11'
OF = json.load(open(os.path.join(DATA, 'owner_followers.json')))
PRIMARY_GOAL = {'Deadbeats': 69987, 'Wormhole Music Group': 68217, 'Bassrush': 65158, 'Jadu Dala': 72037, 'UKF': 18130,
    'Deep Dark & Dangerous': 43229, 'Wakaan': 110315, 'Disciple': 373903, 'Circus Records': 126878, 'Cyclops Recordings': 78866,
    'Drama Club Recordings': 78868, 'Subsidia': 90526, 'Good Society': 113575, 'Memory Palace': 115076, 'Local Void': 129124}
SKIP = {i for ids in GOAL.values() for i in ids} - set(PRIMARY_GOAL.values())
SKIP |= {91973, 105490}  # DUPLOC sub-ids, dormant
for ids in MERGED.values(): SKIP |= set(ids[1:])
DISTRIB = {r['id'] for r in RS.values() if r['distributor']}

def ids_of(lid):
    for g, ids in GOAL.items():
        if lid in ids: return ids
    for g, ids in PEER_GOOD.items():
        if lid in ids: return ids
    return next((v for v in MERGED.values() if lid in v), [lid])

def sc_info(lid):
    k = str(lid); m = M.get(k); s = S.get(k, {})
    if m:
        ident = m['identity']; followers = m.get('followers'); url = 'https://soundcloud.com/' + m['permalink']
    else:
        ident = s.get('identity', 'not searched'); sc = s.get('sc') or {}
        followers = sc.get('followers'); url = sc.get('url')
        if ident == 'confirmed': ident = f"confirmed ({s.get('title_matches')} title matches)"
        elif ident == 'weak': ident = f"weak ({s.get('title_matches')} title matches)"
    return ident, followers, url

def newcomers(lid):
    r = RS.get(lid)
    if not r: return 0
    # roster artists whose only (non-distributor) label in the 2-year universe is this one
    U = json.load(open(os.path.join(DATA, 'universe_labels.json'))) if not hasattr(newcomers, 'U') else newcomers.U
    newcomers.U = U
    lab = next((l for l in U if l['id'] == lid), None)
    if not lab: return 0
    return sum(1 for a in lab['artists'] if len([x for x in A[a]['labels'] if x not in DISTRIB]) == 1)

rows = []
for lid, g in G.items():
    if lid in SKIP or lid in DISTRIB: continue
    ident, followers, sc_url = sc_info(lid)
    door = D.get(str(lid), {'type': 'not checked'})
    has_door = door['type'] in ('email', 'form', 'portal')
    owner_conf = str(lid) in OWN
    # Calibration fix 2026-11-11: owner statement not required (DUPLOC, Trippy Bee failed it). Identity = SoundCloud confirmed by 3+ titles.
    id_ok = ident.startswith('confirmed')
    if not ident.startswith('confirmed'): followers = None  # never use followers from an unconfirmed account
    reach = 7 if (followers or 0) >= 10000 else 4 if (followers or 0) >= 2000 else 1
    score = g['score_pre_reach'] + reach
    ch = g['chart_indep'] + g['chart_owner']
    rows.append(dict(g, ids=ids_of(lid), sc_identity=ident, sc_followers=followers, sc_url=sc_url, door=door, has_door=has_door,
        owner_confirmed=owner_conf, owner_how=OWN.get(str(lid), {}).get('how'), identity_ok=id_ok, reach=reach, score=score,
        has_chart=ch > 0, newcomers_2y=newcomers(lid)))

def b_gate(r):
    return r['gates']['genre'] and r['gates']['activity'] and r['gates']['roster']

goal_followers = [r['sc_followers'] for r in rows if r['id'] in PRIMARY_GOAL.values() and r['sc_followers']]
GOAL_FOLLOWER_BAR = statistics.median(goal_followers)

listA, listB, scouting, manual, rejected = [], [], [], [], []
for r in rows:
    is_goal = r['id'] in PRIMARY_GOAL.values()
    b_hits = [r['chart_indep'] >= 3, (r['sc_followers'] or 0) >= GOAL_FOLLOWER_BAR, r['goal_overlap'] >= 5]
    if is_goal or (sum(b_hits) >= 2 and r['gates']['activity']):
        acc = int(r['last12_accepted'].split('/')[0])
        n_gen = r['chart_indep']
        reach = (45 if n_gen >= 4 else 30 if n_gen >= 2 else 15 if n_gen == 1 else 0)
        f = r['sc_followers'] or 0
        reach += 15 if f >= 100000 else 10 if f >= 50000 else 5 if f >= 20000 else 0
        fit = 40 if acc >= 9 else 25 if acc >= 6 else 10 if acc >= 3 else 0
        if r['door']['type'] == 'closed' or not r['has_door']: access = 'CLOSED'
        elif r['newcomers_2y'] >= 3: access = 'OPEN'
        else: access = 'NARROW'
        listB.append(dict(r, b_rank=reach + fit, b_reach=reach, b_fit=fit, access=access, goal=is_goal,
                          b_criteria=['3+ indep chart' if b_hits[0] else None, 'goal-level followers' if b_hits[1] else None, '5+ goal artists' if b_hits[2] else None]))
        continue
    if r['id'] in ARTIST_REJECT:
        rejected.append(dict(r, reason=ARTIST_REJECT[r['id']])); continue
    reasons = [k for k, v in r['gates'].items() if not v and not (k == 'activity' and r['id'] in ACTIVITY_WAIVE)]
    if reasons:
        rejected.append(dict(r, reason='fails ' + ', '.join(reasons))); continue
    via_chart = r['has_chart']
    if via_chart and r['score'] < 45:
        rejected.append(dict(r, reason=f"score {r['score']} under 45")); continue
    flags = list(r['flags'])
    of = OF.get(str(r['id']))
    if of and (r['sc_followers'] or 0) < 2000 and of['followers'] > 10000: flags.append(f"label under 2k followers, owner {of['owner']} has {of['followers']}")
    if via_chart and 45 <= r['score'] < 50: flags.append('score 45-49')
    if not r['identity_ok']: flags.append('identity unconfirmed: ' + r['sc_identity'])
    if flags:
        manual.append(dict(r, review=flags)); continue
    if not r['has_door']:
        scouting.append(r); continue
    listA.append(dict(r, tag='chart proof' if via_chart else 'relationship, not chart proof', review=flags))

listA.sort(key=lambda r: (-r['score'] if r['has_chart'] else -r['rsi'] / 2, -r['chart_indep'], -r['newcomer_share']))
chartA = [r for r in listA if r['has_chart']]; relA = [r for r in listA if not r['has_chart']]
relA.sort(key=lambda r: -r['rsi'])
# Relationship cap lifted by the artist 2026-11-11: no reserve.
reserve = []
listA = sorted(chartA, key=lambda r: -r['score']) + relA
listB.sort(key=lambda r: (not r['goal'], -r['b_rank']))
out = {'snapshot': SNAP, 'goal_follower_bar': GOAL_FOLLOWER_BAR, 'listA': listA, 'listB': listB, 'scouting': scouting, 'reserve': reserve, 'manual': manual, 'rejected': rejected}
json.dump(out, open(os.path.join(DATA, 'lists.json'), 'w'), indent=1, default=list)
print('A', len(listA), '(chart', len(chartA), 'relationship', len(relA), ') B', len(listB), 'scouting', len(scouting), 'manual', len(manual), 'rejected', len(rejected), 'goal follower bar', GOAL_FOLLOWER_BAR)
for n, L in [('A', listA), ('RESERVE', reserve), ('SCOUT', scouting), ('MANUAL', manual)]:
    print('==', n)
    for r in L:
        print(' ', r['name'], '| score', r['score'], 'rsi', r['rsi'], '| door', r['door']['type'], '|', r.get('access', ''), r.get('b_rank', ''), '|', r['sc_identity'][:30], '| f', r['sc_followers'], '|', r.get('review') or r.get('note') or '')
