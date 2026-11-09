"""Pluck notes from the two rolling stems -> hohlweg_pluck_notes.json, for the travelling-chain layer.

ABGRUND's stem runs 857 ms late against the stitched master (exactly two beats at 140; checked by
correlation: r 0.81 at -857 ms, ~0 at 0 and +857, and the corrected stem cuts out on the cut 6:05.0
and returns on the drop 6:11.7). GRUND's lines up at 0 ms.

Onset: spectral-flux peak over 1.8 x its local median, 60 ms apart at least, within 40 dB of the
stem's loudest note. Each note gets a cycle and a step: ABGRUND plays one fast burst of 4-6 notes
every half note (a new cycle after a gap > 0.25 s); GRUND plays 16ths accented on every beat (cycles
on a 128 BPM grid phased to the accents; in the final slowdown, a new cycle on each accent). Velocity: the note's 50 ms level, levelled per stem to
its 90th-percentile note, clipped at 1 - so it follows the filter and the fades.

Output: {"abgrund": [[t, vel, cycle, step], ...], "grund": [...]}, t in master seconds.
"""
import json, subprocess
import numpy as np

STEMS = "/Volumes/music/sessions/FINISHED/originals/hohlweg_ep Project/hohlweg_%s_pluck_stem.wav"
OUT = "/Volumes/music/blender/hohlweg_assets/audio/hohlweg_pluck_notes.json"
OFFSET = {"abgrund": 0.857, "grund": 0.0}    # stem runs late by this much
SR, W, H = 22050, 1024, 128


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def notes(x, off):
    n = (len(x) - W) // H
    fr = np.lib.stride_tricks.sliding_window_view(x, W)[::H][:n] * np.hanning(W)
    flux = np.maximum(np.diff(np.log1p(1000 * np.abs(np.fft.rfft(fr, axis=1))), axis=0), 0).sum(1)
    fps = SR / H
    k = int(fps)
    med = np.repeat([np.median(flux[max(0, i - k):i + k]) for i in range(0, len(flux), 8)], 8)[:len(flux)]
    on = []
    for i in range(1, len(flux) - 1):
        if flux[i] > flux[i - 1] and flux[i] >= flux[i + 1] and flux[i] > med[i] * 1.8 + 1:
            if not on or (i - on[-1]) / fps > 0.06:
                on.append(i)
    t = np.array(on) / fps
    lev = np.array([20 * np.log10(np.sqrt((x[int(a * SR):int((a + 0.05) * SR)] ** 2).mean()) + 1e-9) for a in t])
    keep = lev > lev.max() - 40
    return t[keep] - off, lev[keep]


def cycles_by_gap(t, gap=0.25):
    c = np.cumsum(np.r_[0, np.diff(t) > gap])
    return c


def accents(lev, db=3.0):
    acc = np.zeros(len(lev), bool)
    for i in range(len(lev)):
        nb = np.r_[lev[max(0, i - 2):i], lev[i + 1:i + 3]]
        acc[i] = len(nb) and lev[i] >= nb.max() + db
    return acc


def cycles_by_beat(t, lev, bpm=128.0, steady_until=605.0):
    # GRUND holds 128 until the final slowdown: fit the beat grid's phase to the accents and cycle on it;
    # in the slowdown, fall back to the accents themselves
    acc = accents(lev)
    beat = 60.0 / bpm
    ta = t[acc & (t < steady_until)]
    ph = np.angle(np.exp(2j * np.pi * ta / beat).mean()) / (2 * np.pi) * beat   # circular mean phase
    cyc = np.floor((t - ph) / beat + 0.25).astype(int)          # a note just ahead of its beat still belongs to it
    late = t >= steady_until
    if late.any():
        cyc[late] = cyc[~late].max() + 1 + np.cumsum(acc[late]) if (~late).any() else np.cumsum(acc[late])
    return cyc - cyc.min()


out = {}
for name in ("abgrund", "grund"):
    t, lev = notes(load(STEMS % name), OFFSET[name])
    cyc = cycles_by_gap(t) if name == "abgrund" else cycles_by_beat(t, lev)
    step = np.zeros(len(t), int)
    for i in range(1, len(t)):
        step[i] = step[i - 1] + 1 if cyc[i] == cyc[i - 1] else 0
    vel = np.clip(10 ** ((lev - np.percentile(lev, 90)) / 20), 0, 1)
    out[name] = [[round(float(a), 4), round(float(v), 3), int(c), int(s)] for a, v, c, s in zip(t, vel, cyc, step)]
    steps = np.bincount(step)
    print(f"{name}: {len(t)} notes in {cyc[-1] + 1} cycles, {t[0]:.2f}-{t[-1]:.2f} s; "
          f"notes per cycle median {np.median(np.bincount(cyc)):.0f}; step counts {steps[:8].tolist()}")
json.dump(out, open(OUT, "w"))
print("wrote", OUT)
