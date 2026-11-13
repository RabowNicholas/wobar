# Move acf_*.json from ~/Downloads into raw/.
import os, glob, shutil, json
from config import RAW
for f in sorted(glob.glob(os.path.expanduser('~/Downloads/acf_*.json'))):
    try: json.load(open(f))
    except Exception as e: print('skip (incomplete?)', f, e); continue
    shutil.move(f, os.path.join(RAW, os.path.basename(f)[4:]))
print(sorted(os.listdir(RAW)))
