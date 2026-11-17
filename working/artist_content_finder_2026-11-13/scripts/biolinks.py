# Step 2c: read link-in-bio pages (Linktree, komi, beacons, hoo.be, fanlink, artist sites) for TikTok handles.
# Plain public page reads, ~2 s apart. Stops on 403/429. Input: raw/biolinks_in_*.tsv (ig_handle <TAB> url).
# Output: raw/biolinks_out.tsv (ig_handle, url, http code, tiktok handles found, youtube found). Resumable.
import os, re, sys, time, glob, urllib.request
from config import RAW
OUT = os.path.join(RAW, 'biolinks_out.tsv')
done = set()
if os.path.exists(OUT):
    done = {l.split('\t')[0] for l in open(OUT)}
todo = []
for f in sorted(glob.glob(os.path.join(RAW, 'biolinks_in_*.tsv'))):
    for l in open(f):
        p = l.rstrip('\n').split('\t')
        if len(p) == 2 and p[0] not in done: todo.append(p); done.add(p[0])
TT = re.compile(r'tiktok\.com/@([A-Za-z0-9_.]+)')
YT = re.compile(r'youtube\.com/(@[A-Za-z0-9_.-]+|c/[A-Za-z0-9_.-]+|channel/[A-Za-z0-9_-]+)')
with open(OUT, 'a') as out:
    for h, url in todo:
        code, tts, yts = '', set(), set()
        try:
            req = urllib.request.Request('https://' + url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                code = str(r.status); html = r.read(2_000_000).decode('utf-8', 'ignore')
            tts = {t.rstrip('.').lower() for t in TT.findall(html)}; yts = set(YT.findall(html))
        except urllib.error.HTTPError as e:
            code = str(e.code)
            if e.code in (403, 429) and 'linktr.ee' in url:
                print('blocked by linktr.ee at', url, '- stopping'); break
        except Exception as e:
            code = 'err:' + type(e).__name__
        out.write('\t'.join([h, url, code, ','.join(sorted(tts)), ','.join(sorted(yts))]) + '\n'); out.flush()
        time.sleep(2)
print('done', len(todo))
