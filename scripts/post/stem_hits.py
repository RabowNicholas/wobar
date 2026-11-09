"""Kick and snare hits from the soloed stems (aligned to the stitched master at 0 ms) -> hohlweg_hits.json.

Onset: the 5 ms level crosses -45 dB (re the stem's peak) from below, or jumps 9 dB over the last 30 ms
(a hit landing on a tail). Velocity: RMS of the first 50 ms. Echoes (a hit the previous flash would mask
at fade 0.35) are dropped. Velocities are levelled per song to that song's 90th-percentile hit, clipped at 1.
"""
import json, subprocess, sys
import numpy as np

STEMS = "/Volumes/music/sessions/FINISHED/originals/hohlweg_ep Project/hohlweg_%s_stem.wav"
OUT = "/Volumes/music/blender/hohlweg_assets/audio/hohlweg_hits.json"
SONGS = (0.0, 237.02, 456.2, 1e9)           # ERNSTFALL, ABGRUND, GRUND starts (master seconds)
SR, HOP = 44100, 220                         # 5 ms frames
FADE = 0.35


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def hits(x, floor_db=-45.0, jump_db=9.0, min_gap=0.06):
    n = len(x) // HOP
    db = 10 * np.log10((x[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-14)
    db -= db.max()
    out, last = [], -1.0
    for i in range(6, n):
        t = i * HOP / SR
        rise = db[i] > floor_db and (db[i - 1] <= floor_db or db[i] - db[i - 6:i].min() > jump_db)
        if rise and db[i] > db[i - 1] and t - last >= min_gap:
            # refine to the first sample over 10% of the next 50 ms peak
            s0 = max((i - 1) * HOP, 0); seg = np.abs(x[s0:s0 + int(0.05 * SR)])
            k = int(np.argmax(seg > 0.1 * seg.max())); t0 = (s0 + k) / SR
            vel = float(np.sqrt((x[s0 + k:s0 + k + int(0.05 * SR)] ** 2).mean()))
            out.append([t0, vel]); last = t
    return out


def drop_echoes(h):
    keep = []
    for t, v in h:
        if keep:
            pt, pv = keep[-1]
            if v <= pv * np.exp(-3 * (t - pt) / FADE):
                continue
        keep.append([t, v])
    return keep


def level(h):
    h = np.array(h)
    for lo, hi in zip(SONGS[:-1], SONGS[1:]):
        m = (h[:, 0] >= lo) & (h[:, 0] < hi)
        if m.any():
            h[m, 1] = np.clip(h[m, 1] / np.percentile(h[m, 1], 90), 0, 1)
    return [[round(float(t), 4), round(float(v), 3)] for t, v in h]


if __name__ == "__main__":
    res = {}
    for name in ("kick", "snare"):
        raw = hits(load(STEMS % name))
        res[name] = level(drop_echoes(raw))
        t = np.array([a for a, _ in res[name]])
        per = [int(((t >= lo) & (t < hi)).sum()) for lo, hi in zip(SONGS[:-1], SONGS[1:])]
        print(f"{name}: {len(raw)} onsets -> {len(res[name])} hits  (ERNSTFALL {per[0]}, ABGRUND {per[1]}, GRUND {per[2]})")
    json.dump(res, open(OUT, "w"))
    print("wrote", OUT)
