"""The pre-drop sweep in ABGRUND's cut as a modulation signal, from the stitched master (2026-10-27).

    python3 cut_signal.py MASTER.wav OUT_DIR

The cut (6:04.8-6:11.6) is near-silent except one falling sound: a train of ticks sweeping from ~9 kHz down to
~370 Hz, evenly in octaves, over a quiet low bed. Without a stem, the sweep is tracked through the mix: each STFT
frame looks for the peak inside +-0.7 octave of the expected log-linear path, and only the energy within 1/6
octave of that peak counts, so the low bed under 300 Hz never enters.

Writes OUT_DIR/cut_signal.json: per 24 fps frame (master seconds) -> pitch (Hz), pitch01 (1 at the top of the
sweep, 0 at the bottom), level01 (band energy, dB-normalised), intensity01 (level with a fast attack and a 0.12 s
release, so each tick reads as a pulse) and ticks (onset times with their level).
"""
import sys, os, json, subprocess
import numpy as np

T0, T1 = 360.0, 376.0                      # analysed span (master s)
SWEEP = (365.1, 13.1, 370.5, 8.55)         # expected path: (t, log2 Hz) at both ends
CUT, DROP = 364.8, 371.6
FPS = 24


def load(path, sr=22050):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(T1 - T0), "-i", path,
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32), sr


def main(master, out):
    x, sr = load(master)
    win, hop = 2048, 128
    F = np.fft.rfftfreq(win, 1 / sr); lf = np.log2(np.maximum(F, 1))
    times, pitch, level = [], [], []
    ta, la, tb, lb = SWEEP
    for i in range(0, len(x) - win, hop):
        t = T0 + (i + win / 2) / sr
        e = np.abs(np.fft.rfft(x[i:i + win] * np.hanning(win))) ** 2
        if not (ta - 0.2 <= t <= tb + 0.6):
            times.append(t); pitch.append(np.nan); level.append(-120.0); continue
        exp = la + (lb - la) * np.clip((t - ta) / (tb - ta), 0, 1)
        m = (np.abs(lf - exp) < 0.7) & (F > 300)
        pk = lf[m][np.argmax(e[m])]
        band = np.abs(lf - pk) < 1 / 6
        times.append(t); pitch.append(2 ** pk); level.append(10 * np.log10(e[band].sum() + 1e-12))
    times, pitch, level = map(np.array, (times, pitch, level))
    # level -> 0..1 over a 40 dB window below the sweep's loudest
    top = np.nanpercentile(level[level > -100], 98)
    lev01 = np.clip((level - (top - 40)) / 40, 0, 1)
    # ticks: rises in the band level
    sm = np.convolve(lev01, np.ones(3) / 3, "same")
    rise = np.diff(sm, prepend=sm[0])
    thr = 0.04
    ticks = []
    for k in range(1, len(rise) - 1):
        if rise[k] > thr and rise[k] >= rise[k - 1] and rise[k] >= rise[k + 1] and lev01[k] > 0.15:
            if not ticks or times[k] - ticks[-1][0] > 0.08:
                ticks.append((float(times[k]), float(sm[min(k + 3, len(sm) - 1)])))
    # per video frame
    frames = []
    fps_t = np.arange(T0, T1, 1 / FPS)
    inten, prev = [], 0.0
    rel = np.exp(-1 / (FPS * 0.12))
    for t in fps_t:
        k = np.searchsorted(times, t)
        k0, k1 = max(k - 2, 0), min(k + 2, len(times))
        lv = float(lev01[k0:k1].max()) if k1 > k0 else 0.0
        prev = max(lv, prev * rel); inten.append(prev)
        p = pitch[min(k, len(pitch) - 1)]
        frames.append(dict(t=round(float(t), 4), pitch=None if np.isnan(p) else round(float(p), 1),
                           pitch01=None if np.isnan(p) else round(float(np.clip((np.log2(p) - lb) / (la - lb), 0, 1)), 4),
                           level01=round(lv, 4), intensity01=round(prev, 4)))
    os.makedirs(out, exist_ok=True)
    json.dump(dict(span=[T0, T1], cut=CUT, drop=DROP, fps=FPS, ticks=ticks, frames=frames),
              open(os.path.join(out, "cut_signal.json"), "w"))
    print(f"{len(ticks)} ticks; first {ticks[0][0]:.2f} last {ticks[-1][0]:.2f}" if ticks else "no ticks")
    for t, v in ticks:
        print(f"  {int(t // 60)}:{t % 60:05.2f}  level {v:.2f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
