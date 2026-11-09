"""MAKYO stem survey: per-bar map of kick / snare / hats / low end + the master, and hit lists.

    python3 scripts/post/makyo_stems.py [out.json]

140 BPM, 106 bars, stems aligned at 0. Onsets as in stem_hits.py (5 ms level crosses a floor or
jumps over the last 30 ms). Low end: RMS envelope, note lengths (time above -12 dB re its own
running peak), and a pitch track by autocorrelation for glides.
"""
import json, subprocess, sys
import numpy as np

DIR = "/Volumes/music/sessions/WIP (ACTIVE)/yagami Project/"
FILES = dict(master="11326_makyo.wav", kick="makyo_kick_stem.wav", snare="makyo_snare_stem.wav",
             hats="makyo_hats_stem.wav", low="makyo_low_pass_stem.wav")
SR, HOP, BPM = 44100, 220, 140.0
BAR = 4 * 60 / BPM


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def env_db(x):
    n = len(x) // HOP
    return 10 * np.log10((x[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-14)


def hits(x, floor_db=-40.0, jump_db=9.0, min_gap=0.06):
    db = env_db(x)
    db -= db.max()
    out, last = [], -1.0
    for i in range(6, len(db)):
        t = i * HOP / SR
        rise = db[i] > floor_db and (db[i - 1] <= floor_db or db[i] - db[i - 6:i].min() > jump_db)
        if rise and t - last > min_gap:
            seg = x[i * HOP:i * HOP + int(0.05 * SR)]
            out.append((round(t, 3), float(np.sqrt((seg ** 2).mean()))))
            last = t
    if out:
        ref = np.percentile([v for _, v in out], 90)
        out = [(t, round(min(v / ref, 1.0), 3)) for t, v in out]
    return out


def brightness(x):
    """spectral centroid per 50 ms frame (Hz)"""
    w = 2205
    n = len(x) // w
    fr = x[:n * w].reshape(n, w) * np.hanning(w)
    mag = np.abs(np.fft.rfft(fr, axis=1))
    f = np.fft.rfftfreq(w, 1 / SR)
    return (mag * f).sum(1) / (mag.sum(1) + 1e-12)


def pitch_track(x, fmin=25, fmax=180):
    """fundamental per 50 ms by autocorrelation on a 4x-decimated signal"""
    d = x[::4]
    sr = SR / 4
    w = int(0.1 * sr)
    hop = int(0.05 * sr)
    out = []
    lo, hi = int(sr / fmax), int(sr / fmin)
    for s in range(0, len(d) - w, hop):
        fr = d[s:s + w]
        e = (fr ** 2).mean()
        if e < 1e-6:
            out.append(0.0)
            continue
        ac = np.correlate(fr, fr, "full")[w - 1:]
        k = lo + int(np.argmax(ac[lo:hi]))
        out.append(sr / k if ac[k] > 0.3 * ac[0] else 0.0)
    return np.array(out)


def main():
    X = {k: load(DIR + v) for k, v in FILES.items()}
    nbar = int(round(len(X["master"]) / SR / BAR))
    H = {k: hits(X[k]) for k in ("kick", "snare", "hats", "low")}
    E = {k: env_db(x) for k, x in X.items()}
    gpk = {k: E[k].max() for k in E}
    fps = SR / HOP
    lowdb = E["low"] - gpk["low"]
    sustain = lowdb > -12
    hb = brightness(X["hats"])
    p = pitch_track(X["low"])

    print(f"{nbar} bars of {BAR:.4f}s")
    print("bar  time   K  S  H   lowRMS sus%  pitchHz(min-max) hatHz  master")
    rows = []
    for b in range(nbar):
        t0, t1 = b * BAR, (b + 1) * BAR
        cnt = {k: sum(1 for t, _ in H[k] if t0 <= t < t1) for k in ("kick", "snare", "hats")}
        i0, i1 = int(t0 * fps), int(t1 * fps)
        lr = 10 * np.log10(np.mean(10 ** (lowdb[i0:i1] / 10)) + 1e-14)
        sus = sustain[i0:i1].mean() * 100
        pp = p[int(t0 / 0.05):int(t1 / 0.05)]
        pp = pp[pp > 0]
        pr = (f"{np.percentile(pp, 10):4.0f}-{np.percentile(pp, 90):4.0f}" if len(pp) > 4 else "    -    ")
        hbz = hb[int(t0 / 0.05):int(t1 / 0.05)]
        he = E["hats"][i0:i1] - gpk["hats"]
        hz = np.median(hbz) if (he > -40).mean() > 0.1 else 0
        mr = 10 * np.log10(np.mean(10 ** ((E["master"][i0:i1] - gpk["master"]) / 10)))
        rows.append(dict(bar=b + 1, t=round(t0, 2), **cnt, low_db=round(lr, 1), low_sus=round(sus), pitch=pr,
                         hat_hz=round(float(hz)), master_db=round(float(mr), 1)))
        print(f"{b+1:3d} {t0:6.1f}  {cnt['kick']:2d} {cnt['snare']:2d} {cnt['hats']:2d}  {lr:6.1f} {sus:4.0f}  {pr}  {hz:6.0f} {mr:6.1f}")
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out:
        json.dump(dict(bpm=BPM, bar=BAR, bars=rows, hits={k: H[k] for k in H}), open(out, "w"))
        print("wrote", out)


main()
