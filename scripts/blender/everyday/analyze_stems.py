"""Everyday stems -> per-frame control curves for WOBAR_CTRL.

usage: python3 analyze_stems.py <stem_dir> <out.json>

Reads everyday_{kick,snare,hat,low_end_no_kick}_stem.wav (same length as the master, aligned at 0).
Writes one value per video frame (30 fps, frame 1 = t 0) for each channel:

  kick_idx / snare_idx / hat_idx   running hit count (int, non-decreasing)
  kick_flash / snare / hat_env     0-1 decay envelopes, attack on the ONSET (not the peak: the kick
                                   body peaks ~71 ms after its onset)
  kick_shove / snare_step / hat_step   eased running counts: each hit adds exactly 1, eased out over a
                                   short window, so a driver can turn "hits" into smooth travel/spin/colour
  low                              0-1 low-end envelope (no kick), normalised to drop level
  low_slow                         the same, smoothed to section level (attack 0.4 s, release 1.5 s)
  low_acc                          integral of the travel base speed (floor + low), in seconds-equivalent

Times are sample-accurate: index * hop / sr. (An earlier analysis multiplied indices by a nominal
0.005 s hop when the real hop was 220/44100 s, which stretched every time by 0.23% and faked a
139.68 BPM tempo. Never convert with a nominal hop.)
"""
import json, os, sys
import numpy as np
import scipy.io.wavfile as wavfile
import scipy.signal as sg

FPS = 30
STEMS = {"kick": "everyday_kick_stem.wav", "snare": "everyday_snare_stem.wav",
         "hat": "everyday_hat_stem.wav", "low": "everyday_low_end_no_kick_stem.wav"}
ONSET = {  # min gap between hits (s), decay time constant (s), eased-step duration (s)
    "kick":  dict(gap=0.12, tau=0.15, ease=0.30),
    "snare": dict(gap=0.12, tau=0.25, ease=0.15),
    "hat":   dict(gap=0.05, tau=0.12, ease=0.08),   # tau 0.12: glints need ~4 frames to read
}
TRAVEL_FLOOR = 0.35   # travel base speed never drops below this share, so the tunnel never stalls


def load(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    peak = np.abs(x).max()
    return sr, x / peak if peak else x


def rms_env(x, sr, hop_s):
    hop = max(1, int(round(sr * hop_s)))
    n = len(x) // hop
    return np.sqrt((x[: n * hop] ** 2).reshape(n, hop).mean(axis=1)), hop


def onsets(x, sr, gap):
    # Pick hits on a 5 ms envelope (a 1 ms one splits the kick's two-stage body into two hits),
    # then back-track on a 1 ms envelope to the rise for an accurate onset time.
    e5, h5 = rms_env(x, sr, 0.005)
    e1, h1 = rms_env(x, sr, 0.001)
    pk = np.percentile(e5, 99.5)
    th = pk * 10 ** (-24 / 20)
    peaks, _ = sg.find_peaks(e5, height=th, distance=max(1, int(gap * sr / h5)), prominence=th * 0.5)
    times, vels = [], []
    for p in peaks:
        j = min(len(e1) - 1, int(p * h5 / h1))
        top = e1[max(0, j - 5): j + 6].max()
        while j > 0 and e1[j] > 0.3 * top:   # back-track to the rise = the onset
            j -= 1
        times.append(j * h1 / sr)
        vels.append(min(1.0, e5[p] / pk))
    return np.array(times), np.array(vels)


def ease_out(u):
    u = np.clip(u, 0.0, 1.0)
    return 1 - (1 - u) ** 3


def main(stem_dir, out):
    data, srs, lens = {}, set(), set()
    for k, f in STEMS.items():
        sr, x = load(os.path.join(stem_dir, f))
        data[k] = x
        srs.add(sr)
        lens.add(len(x))
    assert len(srs) == 1 and len(lens) == 1, f"stems differ: sr {srs} len {lens}"
    sr = srs.pop()
    dur = lens.pop() / sr
    nfr = int(round(dur * FPS))
    t = np.arange(nfr) / FPS                      # frame f (1-based) is t[f-1]
    ch = {}
    hits = {}
    for k, cfg in ONSET.items():
        on, vel = onsets(data[k], sr, cfg["gap"])
        hits[k] = on
        idx = np.searchsorted(on, t, side="right")
        env = np.zeros(nfr)
        step = np.zeros(nfr)
        for ti, v in zip(on, vel):
            m = t >= ti
            env[m] = np.maximum(env[m], v * np.exp(-(t[m] - ti) / cfg["tau"]))
            step += ease_out((t - ti) / cfg["ease"])
        name_env = {"kick": "kick_flash", "snare": "snare", "hat": "hat_env"}[k]
        name_step = {"kick": "kick_shove", "snare": "snare_step", "hat": "hat_step"}[k]
        ch[f"{k}_idx"] = idx.astype(float)
        ch[name_env] = env
        ch[name_step] = step

    # low end: 20 ms RMS -> asymmetric smoothing (attack 30 ms, release 300 ms) -> normalise to drop level
    e, hop = rms_env(data["low"], sr, 0.020)
    et = np.arange(len(e)) * hop / sr
    a_up, a_dn = np.exp(-0.020 / 0.030), np.exp(-0.020 / 0.300)
    sm = np.zeros_like(e)
    for i in range(1, len(e)):
        a = a_up if e[i] > sm[i - 1] else a_dn
        sm[i] = a * sm[i - 1] + (1 - a) * e[i]
    low = np.interp(t, et, sm)
    ref = np.percentile(low, 90)
    low = np.clip(low / ref, 0, 1.2) if ref > 0 else low
    ch["low"] = low
    # section-level energy: the same envelope, slower (attack 0.4 s, release 1.5 s) so it follows
    # the arrangement instead of individual bass notes. Drives psychedelic intensity (colour).
    b_up, b_dn = np.exp(-1 / FPS / 0.4), np.exp(-1 / FPS / 1.5)
    slow = np.zeros(nfr)
    for i in range(1, nfr):
        b = b_up if low[i] > slow[i - 1] else b_dn
        slow[i] = b * slow[i - 1] + (1 - b) * min(low[i], 1.0)
    ch["low_slow"] = slow
    speed = TRAVEL_FLOOR + (1 - TRAVEL_FLOOR) * np.clip(low, 0, 1)
    ch["low_acc"] = np.concatenate([[0.0], np.cumsum(speed[:-1]) / FPS])

    js = {"fps": FPS, "frames": nfr, "duration_s": dur, "bpm": 140, "travel_floor": TRAVEL_FLOOR,
          "onset_cfg": ONSET, "hit_counts": {k: int(len(v)) for k, v in hits.items()},
          "channels": {k: [round(float(v), 5) for v in arr] for k, arr in ch.items()}}
    with open(out, "w") as f:
        json.dump(js, f)
    print(f"wrote {out}: {nfr} frames ({dur:.2f} s), hits {js['hit_counts']}")
    for k, arr in ch.items():
        print(f"  {k:11} min {arr.min():8.3f} max {arr.max():9.3f} mean {arr.mean():8.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
