import json, glob, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'raw'); DATA = os.path.join(HERE, '..', 'data')
TODAY = '2026-11-11'; D6M = '2026-05-11'; D60 = '2026-09-12'; D12M = '2025-11-11'; D24M = '2024-11-11'
ACCEPTED = {'140 / Deep Dubstep / Grime', 'Dubstep'}

def load_cats():
    cat = {}
    for f in sorted(glob.glob(os.path.join(RAW, 'cat_*.json'))):
        cat.update(json.load(open(f)))
    return cat

def releases_from_cat(entry):
    """Group a label catalogue page into releases, newest first, pre-orders removed."""
    rel = collections.OrderedDict()
    for t in entry.get('tracks', []):
        d = t.get('nrd') or ''
        if d > TODAY or t.get('pre'):
            continue
        r = rel.setdefault(t['rid'], {'rid': t['rid'], 'name': t['rn'], 'date': d, 'genres': collections.Counter(), 'artists': {}, 'tracks': []})
        r['genres'][t['g']] += 1
        for a in t['a']: r['artists'][a[0]] = a[1]
        r['tracks'].append(t)
        r['date'] = max(r['date'], d)
    out = sorted(rel.values(), key=lambda r: r['date'], reverse=True)
    for r in out:
        r['genre'] = r['genres'].most_common(1)[0][0]  # release genre = majority track genre
    return out
