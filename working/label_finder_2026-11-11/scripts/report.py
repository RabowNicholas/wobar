# Write LIST_A.csv, LIST_B.csv, SIDE_LISTS.csv and route-plan data from data/lists.json.
import json, os, sys, csv, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import *
L = json.load(open(os.path.join(DATA, 'lists.json')))
cats = load_cats()
U = {l['id']: l for l in json.load(open(os.path.join(DATA, 'universe_labels.json')))}
A = json.load(open(os.path.join(DATA, 'artist_index.json')))
OUT = os.path.join(DATA, '..')

def bp_url(r):
    slug = cats.get(str(r['id']), {}).get('slug') or 'x'
    return f"https://www.beatport.com/label/{slug}/{r['id']}"

def door_text(d):
    if d['type'] in ('email', 'form', 'portal'): return f"{d['type']}: {d.get('address','')}"
    return d['type'] + (': ' + d.get('wording', '') if d.get('wording') else '')

def owner_text(r):
    if r.get('owner_how'): return f"{', '.join(r['owner'])} (confirmed, {r['owner_how']})"
    if r['owner']: return f"{', '.join(r['owner'])} ({r['owner_status']})"
    return 'not stated by label'

COLS_A = ['rank', 'label', 'beatport_ids', 'tag', 'score', 'score_parts', 'reach_pts', 'independent_chart_tracks', 'owner_credited_chart_tracks', 'best_chart_pos',
          'releases_6m', 'releases_since_2026-09-12', 'last12_in_genre', 'distinct_artists_24m', 'newcomer_share', 'median_footprint', 'goal_label_artists',
          'peer_label_artists', 'rsi', 'sc_followers', 'owner', 'door', 'door_wording', 'door_where', 'door_rules', 'soundcloud_identity', 'flags', 'beatport', 'soundcloud', 'checked']
def row_a(i, r):
    d = r['door']
    return [i, r['name'], ' '.join(map(str, r['ids'])), r.get('tag', ''), r['score'], json.dumps(r['score_parts']), r['reach'], r['chart_indep'], r['chart_owner'], r['chart_best_pos'] or '',
            r['rel_6m'], r['rel_recent'], r['last12_accepted'], r['n_artists_24m'], r['newcomer_share'], r['median_footprint'], r['goal_overlap'], r['peer_overlap'],
            r['rsi'], r['sc_followers'] or '', owner_text(r), door_text(d), d.get('wording', ''), d.get('where', ''), d.get('rules', ''), r['sc_identity'],
            '; '.join(r.get('review') or r.get('flags') or []), bp_url(r), r['sc_url'] or '', L['snapshot']]
with open(os.path.join(OUT, 'LIST_A.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(COLS_A)
    for i, r in enumerate(L['listA'], 1): w.writerow(row_a(i, r))

# route plans: roster artists of a closed Dream label who also release on a List A / reserve label
stepping = {r['id']: r['name'] for r in L['listA'] + L['reserve']}
def route(r):
    ros = set(U.get(r['id'], {}).get('artists', {}).keys())
    hits = collections.Counter()
    who = collections.defaultdict(list)
    for a in ros:
        for lid in A[a]['labels']:
            if lid in stepping:
                hits[stepping[lid]] += 1; who[stepping[lid]].append(A[a]['name'])
    top = hits.most_common(3)
    return '; '.join(f"{n} ({c} shared artists: {', '.join(sorted(who[n])[:4])})" for n, c in top) or 'no List A label shares artists with this roster'

from config import SEND_SET_EXCLUDE
openB = [r for r in L['listB'] if r['access'] in ('OPEN', 'NARROW') and r['id'] not in SEND_SET_EXCLUDE]
openB.sort(key=lambda r: -r['b_rank'])
X = min(10, len(openB)); in_x = {r['id'] for r in openB[:X]}
COLS_B = ['label', 'goal_label', 'beatport_ids', 'rank_score', 'reach', 'fit', 'access', 'in_send_set_X', 'qualified_by', 'independent_chart_tracks', 'last12_in_genre',
          'releases_6m', 'last_release', 'sc_followers', 'newcomers_2y', 'owner', 'door', 'door_wording', 'door_where', 'door_rules', 'route_plan_if_closed', 'soundcloud_identity', 'beatport', 'soundcloud', 'checked']
with open(os.path.join(OUT, 'LIST_B.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(COLS_B)
    for r in sorted(L['listB'], key=lambda r: (r['access'] == 'CLOSED', -r['b_rank'])):
        d = r['door']
        w.writerow([r['name'], 'yes' if r['goal'] else 'no', ' '.join(map(str, r['ids'])), r['b_rank'], r['b_reach'], r['b_fit'], r['access'], 'yes' if r['id'] in in_x else '',
                    ', '.join(x for x in r['b_criteria'] if x) or 'goal label', r['chart_indep'], r['last12_accepted'], r['rel_6m'], r['last_release'], r['sc_followers'] or '',
                    r['newcomers_2y'], owner_text(r), door_text(d), d.get('wording', ''), d.get('where', ''), d.get('rules', ''),
                    route(r) if r['access'] == 'CLOSED' else '', r['sc_identity'], bp_url(r), r['sc_url'] or '', L['snapshot']])

with open(os.path.join(OUT, 'SIDE_LISTS.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['list', 'label', 'beatport_ids', 'reason', 'score', 'rsi', 'last12_in_genre', 'releases_6m', 'door', 'soundcloud_identity', 'beatport'])
    for name, key, why in [('relationship reserve', 'reserve', lambda r: r['note']), ('scouting queue', 'scouting', lambda r: 'passes everything except the door'),
                           ('manual review', 'manual', lambda r: '; '.join(r['review'])), ('rejected', 'rejected', lambda r: r['reason'])]:
        for r in L[key]:
            w.writerow([name, r['name'], ' '.join(map(str, r['ids'])), why(r), r['score'], r['rsi'], r['last12_accepted'], r['rel_6m'], door_text(r['door']), r['sc_identity'], bp_url(r)])
    w.writerow(['known ledger', '(none)', '', 'artist reported no sends, no personal contacts', '', '', '', '', '', '', ''])
print('X =', X, [r['name'] for r in openB[:X]])
for r in L['listB']:
    if r['access'] == 'CLOSED': print('ROUTE', r['name'], '->', route(r))
