# Move lf_*.json from ~/Downloads into raw/, unpacking batch files.
import json, os, glob, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
for f in sorted(glob.glob(os.path.expanduser('~/Downloads/lf_*.json'))):
    try:
        d = json.load(open(f))
    except Exception as e:
        print('skip (incomplete?)', f, e); continue
    base = os.path.basename(f)
    if base.startswith('lf_batch_'):
        for k, v in d.items():
            json.dump(v, open(os.path.join(D, k[3:]), 'w'))
    else:
        name = base[3:]
        if name == 'charts.json': name = 'charts_2026-11-11.json'
        json.dump(d, open(os.path.join(D, name), 'w'))
    os.remove(f)
print(sorted(os.listdir(D)))
