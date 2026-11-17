# Parse data/covers_notes.md (Claude's cover reads) into per-post rows and compare formats / hooks
# relative to each artist's own median (rel = views / artist median of covers read). Output data/covers_stats.json.
import re, json, statistics, os
from collections import defaultdict
from config import DATA
txt = open(os.path.join(DATA, 'covers_notes.md')).read()
rows = []
for block in re.split(r'\n## ', txt)[1:]:
    head = block.split('\n')[0]
    m = re.match(r'(\d+)\s+(.+?)\s*\(', head)
    if not m: continue
    artist = m.group(2)
    for cell in re.findall(r'([\d.,]+[KM]?)\s+([A-Z][A-Z/-]+)([^|]*)', block.split('\n', 1)[1]):
        v, fmt, rest = cell
        n = float(v.replace(',', '').rstrip('KM')) * (1e6 if v.endswith('M') else 1e3 if v.endswith('K') else 1)
        rows.append({'artist': artist, 'views': n, 'format': fmt.split('/')[0].replace('-masked', ''),
                     'hook': '"' in rest, 'pinned': 'pinned' in rest, 'lowest': 'lowest' in rest or 'low)' in rest})
by = defaultdict(list)
for r in rows: by[r['artist']].append(r['views'])
for r in rows: r['rel'] = r['views'] / statistics.median(by[r['artist']])
def summ(rs): return {'n': len(rs), 'median_rel': round(statistics.median([r['rel'] for r in rs]), 2) if rs else None,
                      'share_2x': round(100 * sum(1 for r in rs if r['rel'] >= 2) / len(rs)) if rs else None}
out = {'n_posts': len(rows), 'n_artists': len(by)}
out['format'] = {f: summ([r for r in rows if r['format'] == f]) for f in sorted({r['format'] for r in rows})}
out['hook'] = {'with_hook': summ([r for r in rows if r['hook']]), 'no_hook': summ([r for r in rows if not r['hook']])}
promo = [r for r in rows if r['format'] in ('OTHER', 'ART', 'TEXT') and r['lowest']]
out['lowest_flagged'] = len([r for r in rows if r['lowest']])
json.dump(out, open(os.path.join(DATA, 'covers_stats.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
