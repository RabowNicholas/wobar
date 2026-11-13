# Beatport-side gates and List A score for every label with a catalogue page.
# Door, identity (SoundCloud) and followers are added later by doors.py.
# Hype points are moved to chart proof (+10) and roster (+10): Beatport runs no Hype chart for either accepted genre.
import json, os, sys, statistics, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *; from config import *

RULES = {
    'genre_min_of_12': 8,
    'act_6m_min': 2, 'act_recent_days_cut': D60,
    'roster_min_artists': 5, 'roster_min_non_owner': 3,
    'rsi_min_nochart': 40,
    'score_min': 50,
}
if len(sys.argv) > 1: RULES.update(json.loads(sys.argv[1]))

U = {l['id']: l for l in json.load(open(os.path.join(DATA, 'universe_labels.json')))}
RS = {r['id']: r for r in json.load(open(os.path.join(DATA, 'rsi_all.json')))}
A = json.load(open(os.path.join(DATA, 'artist_index.json')))
CT = json.load(open(os.path.join(DATA, 'chart_tracks.json')))
SETS = json.load(open(os.path.join(DATA, 'artist_sets.json')))
OWN = {}
p = os.path.join(DATA, 'owners.json')
if os.path.exists(p): OWN = json.load(open(p))  # label id -> {'owner_ids': [...], 'how': '...'}
cats = load_cats()
chart_by_label = collections.defaultdict(list)
for t in CT: chart_by_label[t['label_id']].append(t)
DISTRIB = {r['id'] for r in RS.values() if r['distributor']}

def fp(aid):
    a = A.get(str(aid))
    return len([x for x in a['labels'] if x not in DISTRIB]) if a else 1

def evaluate(lid, cat):
    rs = releases_from_cat(cat)
    last12 = rs[:12]
    acc = len(last12) if lid in GENRE_OVERRIDE else sum(1 for r in last12 if r['genre'] in ACCEPTED)
    r6 = sum(1 for r in rs if r['date'] >= D6M); r60 = sum(1 for r in rs if r['date'] >= RULES['act_recent_days_cut'])
    # roster over 24 months: universe (accepted genres) + catalogue page
    ros = collections.Counter({int(k): v for k, v in U[lid]['artists'].items()}) if lid in U else collections.Counter()
    for r in rs:
        if r['date'] >= D24M:
            for a in r['artists']:
                if lid not in U: ros[a] += 1
    names = {}
    for r in rs:
        names.update(r['artists'])
    # owner: confirmed if in owners.json, else candidate = most credited on last 12 (never a single credit)
    cred = collections.Counter(a for r in last12 for a in r['artists'])
    own = OWN.get(str(lid))
    if own:
        owner_ids = set(own['owner_ids']); owner_status = 'confirmed: ' + own['how']
    else:
        top = cred.most_common(1)
        owner_ids = {top[0][0]} if top and top[0][1] >= 4 else set()
        owner_status = f'candidate ({top[0][1]}/12 credits), unconfirmed' if owner_ids else 'unknown'
    owner_share = max((cred[o] for o in owner_ids), default=0)
    non_owner = [a for a in ros if a not in owner_ids]
    ch = chart_by_label.get(lid, [])
    indep = [t for t in ch if not ({a[0] for a in t['artists']} & owner_ids)]
    ownc = [t for t in ch if ({a[0] for a in t['artists']} & owner_ids)]
    best = min((min(t['pos'].values()) for t in ch), default=None)
    fps = [fp(a) for a in ros]
    med = statistics.median(fps) if fps else 0
    gset = set(SETS['goal_artists']); pset = set(SETS['peer_artists'])
    rsi = RS.get(lid, {})
    g_over = rsi.get('goal_artists', 0); p_over = rsi.get('peer_artists', 0)
    only = sum(1 for x in fps if x == 1) / len(fps) if fps else 0
    repeat = sum(1 for a, n in ros.items() if n > 1) / len(ros) if ros else 0
    # --- score (100) ---
    n_i = len(indep)
    s_chart = (16 if n_i == 1 else 29 if n_i == 2 else 40 if n_i >= 3 else 0) + min(16, 8 * len(ownc))
    s_chart = min(40, s_chart)
    s_ros = (15 if med >= 3 else 9 if med >= 2 else 4 if med >= 1 else 0)
    s_ros += 15 if g_over >= 3 else 9 if g_over >= 1 else (6 if p_over >= 2 else 0)
    s_new = (10 if 0.2 <= only <= 0.6 else 0) + (5 if 0.2 <= repeat <= 0.6 else 0)
    s_fit = 8 if acc >= 11 else 5 if acc >= 8 else 0
    score = s_chart + s_ros + s_new + s_fit  # + reach (0-7) added after followers are read
    gates = {
        'genre': acc >= RULES['genre_min_of_12'],
        'activity': r6 >= RULES['act_6m_min'] and r60 >= 1,
        'roster': len(ros) >= RULES['roster_min_artists'] and len(non_owner) >= RULES['roster_min_non_owner'],
        'chart_or_rsi': bool(ch) or rsi.get('rsi', 0) >= RULES['rsi_min_nochart'],
    }
    flags = []
    if owner_share > 6: flags.append('owner on >half of last 12: manual review')
    if r6 >= 20 and not ch and med <= 1: flags.append('high volume, no chart, median footprint 1: manual review')
    return {'id': lid, 'name': cat.get('name'), 'catalogue_tracks': cat.get('count'), 'last_release': rs[0]['date'] if rs else None,
        'rel_6m': r6, 'rel_recent': r60, 'last12_accepted': f'{acc}/{len(last12)}', 'last12_genres': dict(collections.Counter(r['genre'] for r in last12)),
        'n_artists_24m': len(ros), 'non_owner_artists': len(non_owner), 'owner': [names.get(o, A.get(str(o), {}).get('name')) for o in owner_ids],
        'owner_ids': sorted(owner_ids), 'owner_status': owner_status, 'owner_share_last12': owner_share,
        'chart_indep': len(indep), 'chart_owner': len(ownc), 'chart_best_pos': best,
        'chart_list': [f"{', '.join(a[1] for a in t['artists'])} - {t['name']} ({t['mix']}) {t['pos']}" for t in ch],
        'median_footprint': med, 'goal_overlap': g_over, 'peer_overlap': p_over, 'newcomer_share': round(only, 2), 'repeat_share': round(repeat, 2),
        'rsi': rsi.get('rsi'), 'score_parts': {'chart': s_chart, 'roster': s_ros, 'newcomer': s_new, 'fit': s_fit},
        'score_pre_reach': score, 'gates': gates, 'flags': flags,
        'is_goal': lid in GOAL_IDS, 'is_peer': lid in PEER_IDS}

if __name__ == '__main__':
    res = []
    for k, v in cats.items():
        if v.get('status') != 200 or not v.get('tracks'): continue
        lid = int(k)
        if lid in DISTRIB: continue
        res.append(evaluate(lid, v))
    json.dump(res, open(os.path.join(DATA, 'gates.json'), 'w'), indent=1)
    passed = [r for r in res if all(r['gates'].values())]
    print('evaluated', len(res), 'pass Beatport gates', len(passed))
    for g in ['genre', 'activity', 'roster', 'chart_or_rsi']:
        print(' fail', g, sum(1 for r in res if not r['gates'][g]))
