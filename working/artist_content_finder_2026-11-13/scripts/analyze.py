# Step 3d: tag every read post and compare what the 10k+ posts share vs the artist's weakest posts.
# Input raw/posts_*.json (latest snapshot wins per post id), data/ranking_dedup.json. Output data/content_posts.json,
# CONTENT_POSTS.csv, data/patterns.json. Tags come from caption text and the audio label only (no audio listening).
import json, glob, os, re, csv, statistics
from collections import Counter, defaultdict
from config import RAW, DATA, ROOT
posts = {}
for f in sorted(glob.glob(os.path.join(RAW, 'posts_*.json')), key=os.path.getmtime):
    for p in json.load(open(f)):
        if p.get('status') == 'ok': posts[(p['artist'], p['id'])] = p
rank = {r['artist']: r for r in json.load(open(os.path.join(DATA, 'ranking_dedup.json')))}

def clean(c):
    c = re.sub(r'[\ud800-\udfff]', '', c or '')   # captions were cut at 600 chars, sometimes mid-emoji
    out = []
    for l in (c or '').split('\n'):
        if re.fullmatch(r'[\d.,]+[KM]?', l) or l.startswith(('Liked by', 'View all')) or re.fullmatch(r'\d+ likes?|Reply', l) \
           or re.fullmatch(r'[A-Z][a-z]+ \d+(, \d{4})?', l) or l == 'See translation': break
        out.append(l)
    return '\n'.join(out).strip()

KW = {
    'id_unreleased': r'\b(ids?|unreleased|dubplate|forthcoming|coming soon|soon)\b',
    'release_cta': r'\b(out now|link in bio|pre-?save|pre-?order|available now|stream|spotify|bandcamp|soundcloud)\b',
    'live_show': r'\b(sold ?out|festival|tour|venue|crowd|b2b|set|headline|lost lands|edc|boomtown|webster|tonight|last night|show)\b',
    'studio_process': r'\b(making|made|studio|serum|ableton|sound design|vip|bootleg|flip|remix|patch|synth|instrument|how i|tutorial|sample pack)\b',
    'question_cta': r'\?|\b(comment|let me know|which|thoughts|rate)\b',
    'meme_joke': r'(😂|🤣|😅|💀|🤪|\blmao\b|\blol\b|type shit|\bpov\b|when you|me when)',
    'hype_caps': None,   # first line mostly capitals
}
def tags(p):
    cap = clean(p.get('caption')); first = cap.split('\n')[0] if cap else ''
    low = cap.lower(); t = {}
    for k, rx in KW.items():
        if rx: t[k] = bool(re.search(rx, low))
    letters = [c for c in first if c.isalpha()]
    t['hype_caps'] = len(letters) >= 6 and sum(c.isupper() for c in letters) / len(letters) > 0.8
    t['hashtags'] = len(re.findall(r'#\w+', cap)); t['mentions'] = len(re.findall(r'@\w+', cap))
    t['words'] = len(re.findall(r'\w+', re.sub(r'#\w+|@\w+', '', cap)))
    au = (p.get('audio') or '').strip(); a = p['artist'].lower()
    t['audio'] = ('original' if au.lower() == 'original audio' or not au else
                  'own_id' if re.search(r'\bid\b', au.lower()) else
                  'own_track' if a.split()[0].strip('.!*$') in au.lower() else 'other_track')
    t['own_post'] = p.get('own_post', False); t['collab'] = bool(p.get('collab'))
    return cap, first, t

rows = []
for (artist, pid), p in posts.items():
    cap, first, t = tags(p)
    rows.append({'artist': artist, 'rank': rank.get(artist, {}).get('rank'), 'id': pid, 'url': f'https://www.instagram.com/p/{pid}/',
                 'views': p['views'], 'hit': p['views'] >= 10000, 'date': (p.get('date') or '')[:10], 'owner': p.get('owner'),
                 'collab': p.get('collab'), 'audio_label': re.sub(r'[\ud800-\udfff]', '', p.get('audio') or ''), 'first_line': first, 'caption': cap, **t})
# relative performance: views vs the artist's own median of the last 12 reels (raw/reels_all.json)
reels = {r['name']: r for r in json.load(open(os.path.join(RAW, 'reels_all.json')))}
for r in rows:
    vs = [x['views'] for x in (reels.get(r['artist'], {}).get('reels') or []) if x['views'] is not None and not x.get('pinned')]
    med = statistics.median(vs) if vs else None
    r['artist_median'] = int(med) if med else None
    r['rel'] = round(r['views'] / med, 2) if med else None
    r['breakout'] = bool(med and r['views'] >= 2 * med)
rows.sort(key=lambda r: (r['rank'] or 999, -r['views']))
json.dump(rows, open(os.path.join(DATA, 'content_posts.json'), 'w'), ensure_ascii=False, indent=1)
cols = ['rank', 'artist', 'views', 'rel', 'breakout', 'hit', 'date', 'owner', 'collab', 'audio', 'audio_label', 'first_line', 'hashtags', 'mentions', 'words',
        'id_unreleased', 'release_cta', 'live_show', 'studio_process', 'question_cta', 'meme_joke', 'hype_caps', 'url']
with open(os.path.join(ROOT, 'CONTENT_POSTS.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

# patterns: share of each tag among hits vs misses, and median views per tag
hits = [r for r in rows if r['hit']]; miss = [r for r in rows if not r['hit']]
pat = {'n_posts': len(rows), 'n_hits': len(hits), 'n_miss': len(miss), 'n_artists': len({r['artist'] for r in rows})}
def share(rs, k): return round(100 * sum(1 for r in rs if r[k]) / max(1, len(rs)))
for k in ['id_unreleased', 'release_cta', 'live_show', 'studio_process', 'question_cta', 'meme_joke', 'hype_caps', 'own_post', 'collab']:
    on = [r['views'] for r in rows if r[k]]; off = [r['views'] for r in rows if not r[k]]
    pat[k] = {'hit_pct': share(hits, k), 'miss_pct': share(miss, k), 'median_on': int(statistics.median(on)) if on else None,
              'median_off': int(statistics.median(off)) if off else None, 'n_on': len(on)}
pat['audio'] = {a: {'n': sum(1 for r in rows if r['audio'] == a), 'hit_pct': share([r for r in rows if r['audio'] == a], 'hit'),
                    'median': int(statistics.median([r['views'] for r in rows if r['audio'] == a] or [0]))}
                for a in ['original', 'own_id', 'own_track', 'other_track']}
for k in ['hashtags', 'words']:
    pat[k] = {'hits_median': statistics.median([r[k] for r in hits] or [0]), 'miss_median': statistics.median([r[k] for r in miss] or [0])}
bo = [r for r in rows if r['breakout']]; rest = [r for r in rows if not r['breakout'] and r['rel'] is not None]
pat['breakout'] = {'n': len(bo), 'n_rest': len(rest)}
for k in ['id_unreleased', 'release_cta', 'live_show', 'studio_process', 'question_cta', 'meme_joke', 'hype_caps', 'own_post', 'collab']:
    pat['breakout'][k] = {'breakout_pct': share(bo, k), 'rest_pct': share(rest, k)}
pat['breakout']['audio'] = {a: {'breakout_pct': round(100*sum(1 for r in bo if r['audio']==a)/max(1,len(bo))), 'rest_pct': round(100*sum(1 for r in rest if r['audio']==a)/max(1,len(rest)))} for a in ['original','own_id','own_track','other_track']}
pat['breakout']['words'] = {'bo_median': statistics.median([r['words'] for r in bo] or [0]), 'rest_median': statistics.median([r['words'] for r in rest] or [0])}
json.dump(pat, open(os.path.join(DATA, 'patterns.json'), 'w'), indent=1)
print(json.dumps(pat['breakout'], indent=1))
