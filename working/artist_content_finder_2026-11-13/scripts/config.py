# Artist content finder, run of 2026-11-13. All rule constants and artist decisions live here.
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..'); RAW = os.path.join(ROOT, 'raw'); DATA = os.path.join(ROOT, 'data')
LF = os.path.join(ROOT, '..', 'label_finder_2026-11-11')   # source universe (read only)
TODAY = '2026-11-13'

# Artist answers 2026-11-13: under 1k everywhere, so copy one tier up.
ML_MIN, ML_MAX = 10_000, 100_000          # main roster (Spotify monthly listeners)
ML_STRETCH_MAX = 500_000                  # stretch tier, reference only
SOCIAL_MIN = 10_000                       # followers on TikTok or Instagram
PLATFORMS = ('tiktok', 'instagram')       # Instagram read through the artist's logged-in Chrome, read only
LANE = 'core+adjacent'                    # adjacent tagged, not mixed

# Pool: artists from the label-finder universe (140 + Dubstep on Beatport, 24 months)
POOL_MIN_RELEASES = 4                     # plus everyone on goal / peer labels or in the charts

# Reference artists from WOBAR_SONIC six-register table (always in pool, by name)
REFERENCE = ['Chmura','Comisar','Super Future','Yoko','Potions','Jungle Rootz','Daggz','Distinct Motive','STVSH','dêtre',
             'Blurrd Vzn','OkayJake','Gunpoint','Quackson','Crucial','Shades','Milano','highrollr','Ero808','Tape B','SAKA',
             'FLY','Coka Cobra','SPOONE','Noctiil','Caspa','Of The Trees','INZO','LSDREAM','Alex Unger']
