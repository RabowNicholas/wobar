"""Full-length walkthrough: stand-in grade + audio + timecode (2026-11-04).

    python3 scripts/post/walk_grade.py --src DIR --out FILE.mp4 [--step 3]

For judging motion and key movement over the whole piece with the music (Nick, 2026-11-04), not the look: the render is
25% / 4 samples, every `step`-th frame (8 fps at step 3), each frame shown for `step` frames of 24 fps so picture and
audio stay locked. Grade = reel_grade's "night" toe curve, fitted per 20 s window (every 6th frame in it) and
interpolated between window centres so it never jumps; ABGRUND (f5689-10944) at ref2's 13/47, the rest 18/60. Dithered
to 8 bits. Burned-in timecode (m:ss.t, bottom left) so cues can be written straight off the screen.
Missing frames hold the previous one, so a partial render still plays in time.
"""
import argparse, bisect, os, subprocess
import numpy as np
from reel_grade import WAV, load, lum, fit, tone

END = 15717


def target(f):
    return (13, 47) if 5689 <= f <= 10944 else (18, 60)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True); p.add_argument("--out", required=True)
    p.add_argument("--step", type=int, default=3); p.add_argument("--window", type=float, default=20.0)
    a = p.parse_args()
    S = a.step
    frames = list(range(1, END + 1, S))
    path = lambda f: os.path.join(a.src, "beauty", f"hohlweg_{f:05d}.png")
    have = [f for f in frames if os.path.exists(path(f))]
    print(f"WALK {len(have)}/{len(frames)} frames present", flush=True)
    # per-window fits
    W = int(a.window * 24)
    cents, A, G = [], [], []
    for w0 in range(1, END + 1, W):
        fs = [f for f in have if w0 <= f < w0 + W]
        if not fs:
            continue
        mid = fs[len(fs) // 2]
        t50, t90 = (v / 255 for v in target(mid))
        ga, gg, p50, p90 = fit([path(f) for f in fs[::6]], t50, t90)
        cents.append(w0 + W / 2); A.append(np.log(ga)); G.append(gg)
        print(f"FIT {w0 / 24 // 60:.0f}:{w0 / 24 % 60:04.1f} p50 {p50 * 255:.2f} p90 {p90 * 255:.2f} -> {target(mid)}", flush=True)

    def params(f):
        la = np.interp(f, cents, A); g = np.interp(f, cents, G)
        return float(np.exp(la)), float(g)

    h, w = load(path(have[0])).shape[:2]
    tc = ("drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=18:fontcolor=white@0.8:box=1:boxcolor=black@0.5:"
          "boxborderw=4:x=10:y=h-th-12:text='%{eif\\:floor(t/60)\\:d}\\:%{eif\\:mod(floor(t*10)\\,600)/10\\:d\\:2}.%{eif\\:mod(floor(t*10)\\,10)\\:d}'")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", f"{24 / S}", "-i", "-", "-i", WAV, "-map", "0:v", "-map", "1:a", "-vf", tc,
                            "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "24",
                            "-c:a", "aac", "-b:a", "256k", "-shortest", a.out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    last = None
    for k, f in enumerate(frames):
        if os.path.exists(path(f)):
            ga, gg = params(f)
            x = tone(load(path(f)), ga, gg) * 255
            d = rng.uniform(-0.5, 0.5, x.shape).astype(np.float32) + rng.uniform(-0.5, 0.5, x.shape).astype(np.float32)
            last = np.clip(x + d, 0, 255).astype(np.uint8).tobytes()
        if last is None:
            last = np.zeros((h, w, 3), np.uint8).tobytes()
        enc.stdin.write(last)
        if k % 500 == 0:
            print(f"ENC {k}/{len(frames)}", flush=True)
    enc.stdin.close(); enc.wait()
    print("WALK DONE", a.out, flush=True)
