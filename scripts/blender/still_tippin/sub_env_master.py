"""STILL TIPPIN: rough sub envelope from the MASTER (2026-11-16), until the sub stem exists.
Low-pass < 90 Hz (4th-order Butterworth, zero-phase), RMS per video frame (30 fps), log-scaled and
normalised 0..1 on the 5th..99.5th percentile. Writes still_tippin_assets/sub_env_master.json.
    python3 sub_env_master.py
"""
import json, wave
import numpy as np
from scipy.signal import butter, sosfiltfilt

SRC = "/Volumes/music/releases/1_in_progress/flips/still_tippin/audio/still_tippin_master.wav"
OUT = "/Volumes/music/blender/still_tippin_assets/sub_env_master.json"
FPS, CUT = 30, 90.0

w = wave.open(SRC)
sr, n, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
raw = np.frombuffer(w.readframes(n), dtype=np.uint8)
assert sw == 3
b = raw.reshape(-1, 3).astype(np.int32)
x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 2 ** 23
x = x.reshape(-1, ch).mean(1)
lo = sosfiltfilt(butter(4, CUT, btype="low", fs=sr, output="sos"), x)
hop = sr // FPS
nf = int(np.ceil(len(lo) / hop))
rms = np.array([np.sqrt(np.mean(lo[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nf)])
db = 20 * np.log10(rms)
a, z = np.percentile(db, 5), np.percentile(db, 99.5)
env = np.clip((db - a) / (z - a), 0, 1)
json.dump(dict(fps=FPS, cutoff_hz=CUT, src=SRC, frames=len(env), env=[round(float(v), 4) for v in env]),
          open(OUT, "w"))
print("frames", len(env), "dB range", round(a, 1), round(z, 1), "mean", round(float(env.mean()), 3))
for bar in (8, 24, 40, 56, 72, 88, 104, 120):
    f = int((bar - 1) * 60 / 140 * 4 * FPS)
    print("bar", bar, round(float(env[f:f + 51].mean()), 2), "max", round(float(env[f:f + 51].max()), 2))
