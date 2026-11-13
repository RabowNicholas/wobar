# Chart labels + Roster Strength Index for every universe label (pre-catalogue pass).
import json, os, sys, statistics, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *; from config import *
U = json.load(open(os.path.join(DATA, 'universe_labels.json')))
A = json.load(open(os.path.join(DATA, 'artist_index.json')))
CH = json.load(open(os.path.join(RAW, 'charts_2026-11-11.json')))['charts']
cats = load_cats()
DISTRIB = {74695, 66449}  # distributors: not counted in footprints
for l in U:
    if 'unitedmasters' in l['name'].lower() or 'distrokid' in l['name'].lower(): DISTRIB.add(l['id'])

# goal / peer artist sets: universe releases + goal catalogue pages
# artist -> set of goal (or peer) label GROUP names they released on (universe + goal catalogue pages)
def artist_groups(groups):
    m = collections.defaultdict(set)
    for gname, ids in groups.items():
        for l in U:
            if l['id'] in ids:
                for a in l['artists']: m[int(a)].add(gname)
        for i in ids:
            e = cats.get(str(i))
            if e and e.get('status') == 200:
                for t in e['tracks']:
                    if (t.get('nrd') or '') >= D24M:
                        for a in t['a']: m[a[0]].add(gname)
    return m
GA = artist_groups(GOAL); PA = artist_groups(PEER_GOOD)
goal_art = set(GA); peer_art = set(PA)
ID2GROUP = {i: g for d in (GOAL, PEER_GOOD) for g, ids in d.items() for i in ids}
def overlap(ros, amap, self_group):
    # artists who released on a goal/peer label OTHER than this label's own group
    return sum(1 for a in ros if amap.get(a, set()) - {self_group})

# chart tracks: last 12 months, count each track once across charts
chart_tracks = {}
for path, lst in CH.items():
    for pos, t in enumerate(lst, 1):
        if t['publish_date'] < D12M: continue
        ct = chart_tracks.setdefault(t['id'], {'id': t['id'], 'name': t['name'], 'mix': t['mix_name'], 'label_id': t['release']['label']['id'],
              'label': t['release']['label']['name'], 'artists': [[a['id'], a['name']] for a in t['artists']], 'pd': t['publish_date'], 'pos': {}})
        ct['pos'][path.split('/')[2]] = pos
charting_artists = {a[0] for t in chart_tracks.values() for a in t['artists']}
by_label = collections.defaultdict(list)
for t in chart_tracks.values(): by_label[t['label_id']].append(t)

def footprint(aid):
    return len([x for x in A[str(aid)]['labels'] if x not in DISTRIB])

rows = []
for l in U:
    ros = [int(a) for a in l['artists']]
    fp = [footprint(a) for a in ros]
    sg = ID2GROUP.get(l['id']); g = overlap(ros, GA, sg); p = overlap(ros, PA, sg); c = len(set(ros) & charting_artists)
    s_goal = 30 if g >= 5 else 22 if g >= 3 else 12 if g >= 1 else 0
    s_goal = min(30, s_goal + (14 if p >= 5 else 8 if p >= 3 else 0))  # scene ties (artist-approved 2026-11-11)
    s_chart = 25 if c >= 5 else 18 if c >= 3 else 10 if c >= 1 else 0
    med = statistics.median(fp) if fp else 0
    s_fp = 15 if med >= 4 else 10 if med >= 3 else 6 if med >= 2 else 0
    s_br = 10 if len(ros) >= 15 else 6 if len(ros) >= 8 else 0
    only_here = sum(1 for x in fp if x == 1) / len(fp) if fp else 0
    rows.append({'id': l['id'], 'name': l['name'], 'releases_24m': l['releases'], 'rel_6m_acc': l['rel_6m'], 'rel_60d_acc': l['rel_60d'],
        'last_acc': l['last'], 'by_genre': l['by_genre'], 'n_artists': len(ros), 'goal_artists': g, 'peer_artists': p, 'charting_artists': c,
        'median_footprint': med, 'newcomer_share': round(only_here, 2), 'rsi': s_goal + s_chart + s_fp + s_br,
        'rsi_parts': [s_goal, s_chart, s_fp, s_br], 'chart_tracks': len(by_label.get(l['id'], [])),
        'is_goal': l['id'] in GOAL_IDS, 'is_peer': l['id'] in PEER_IDS, 'distributor': l['id'] in DISTRIB})
json.dump(rows, open(os.path.join(DATA, 'rsi_all.json'), 'w'))
json.dump(list(chart_tracks.values()), open(os.path.join(DATA, 'chart_tracks.json'), 'w'))
json.dump({'goal_artists': sorted(goal_art), 'peer_artists': sorted(peer_art), 'charting_artists': sorted(charting_artists)}, open(os.path.join(DATA, 'artist_sets.json'), 'w'))
chart_label_ids = set(by_label)
print('chart tracks (12m):', len(chart_tracks), 'chart labels:', len(chart_label_ids))
print('goal artists:', len(goal_art), 'peer artists:', len(peer_art), 'charting artists:', len(charting_artists))
nc = [r for r in rows if r['chart_tracks'] == 0]
for th in (50, 60, 70): print(f'no-chart labels RSI>={th}:', sum(1 for r in nc if r['rsi'] >= th), ' & >=2 acc rel in 6m:', sum(1 for r in nc if r['rsi'] >= th and r['rel_6m_acc'] >= 2))
print('calibration (RSI):')
for r in rows:
    if r['is_goal'] or r['is_peer'] or r['id'] in (131548, 90395, 74695, 66449):
        if r['releases_24m'] >= 1: print(' ', r['name'], r['rsi'], r['rsi_parts'], 'chart', r['chart_tracks'], 'art', r['n_artists'], 'medfp', r['median_footprint'])
