"""Stand-in grade + YouTube reel for the 4K every-look test (2026-11-03).

    python3 scripts/post/reel_grade.py --src DIR --out DIR [--clips "name:a:b,..."]

Per clip: the "night" toe curve (Nick, 2026-11-03) fitted ONCE per clip from every 10th frame (a per-frame fit would
flicker), targets per section so the trench stays darkest - ERNSTFALL / GRUND / clearing p50 -> 18/255, p90 -> 60/255;
ABGRUND drop + trench at ref2's darkness, 13 / 47 (HOHLWEG_VISUALIZER §4). Soft shoulder, black floor held, colour kept
(the green-patina push is Nick's, in Resolve - not stood in here). Then two 8-bit versions from the same toned frame:
    A  dither only (triangular, 1 code) - what a careful Resolve export does
    B  dither + fine luminance grain (sigma 1.5/255, ~1 px) - does grain survive YouTube's encode?
Each clip is cut with its audio; clips concatenated into reel_A.mp4 / reel_B.mp4 (4K, H.264 crf 12, yuv420p, AAC 256k),
to upload unlisted and judge on the TV and a phone. Fog banding was found to be made at the 8-bit step, not in the
render (4:34 test, 2026-11-03), which is what this measures.
"""
import argparse, os, subprocess
import numpy as np

WAV = "/Volumes/music/blender/hohlweg_assets/audio/hohlweg_ep_100426_stitched.wav"
TARGET = {"lane": (18, 60), "sprint": (18, 60), "drop": (13, 47), "trench": (13, 47),
          "moon": (18, 60), "grass": (18, 60), "fog": (18, 60), "clearing": (18, 60)}
CLIPS = "lane:721:840,sprint:3457:3576,drop:7177:7296,trench:8977:9096,moon:11041:11160,grass:12241:12360,fog:13297:13416,clearing:15598:15717"


def load(path):
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint16).reshape(h, w, 3).astype(np.float32) / 65535


def lum(x):
    return 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]


def fit(frames, t50, t90):
    ys = np.concatenate([lum(load(p))[::4, ::4].ravel() for p in frames])
    p50, p90 = np.percentile(ys, [50, 90]); p50 = max(p50, 1e-6); p90 = max(p90, p50 * 1.5)
    g = np.log(t90 / t50) / np.log(p90 / p50)
    return t50 / p50 ** g, g, p50, p90


def tone(x, a, g):
    y = lum(x); yo = a * np.maximum(y, 0) ** g; yo = yo / (1 + yo ** 6) ** (1 / 6)
    return np.clip(x * (yo / np.maximum(y, 1e-9))[..., None], 0, 1)


def encoder(path, w, h, a, b):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "24",
                             "-i", "-", "-ss", f"{(a - 1) / 24:.6f}", "-t", f"{(b - a + 1) / 24:.6f}", "-i", WAV,
                             "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", path], stdin=subprocess.PIPE)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True); p.add_argument("--out", required=True); p.add_argument("--clips", default=CLIPS)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(7)
    parts = {"A": [], "B": []}
    for spec in a.clips.split(","):
        name, f0, f1 = spec.split(":"); f0, f1 = int(f0), int(f1)
        paths = [os.path.join(a.src, "beauty", f"hohlweg_{f:05d}.png") for f in range(f0, f1 + 1)]
        paths = [q for q in paths if os.path.exists(q)]
        if not paths:
            print("GRADE", name, "no frames, skipped", flush=True); continue
        f1 = f0 + len(paths) - 1
        t50, t90 = (v / 255 for v in TARGET[name])
        ga, gg, p50, p90 = fit(paths[::10], t50, t90)
        h, w = load(paths[0]).shape[:2]
        enc = {k: encoder(os.path.join(a.out, f"{k}_{name}.mp4"), w, h, f0, f1) for k in "AB"}
        for q in paths:
            x = tone(load(q), ga, gg) * 255
            d = rng.uniform(-0.5, 0.5, x.shape).astype(np.float32) + rng.uniform(-0.5, 0.5, x.shape).astype(np.float32)
            enc["A"].stdin.write(np.clip(x + d, 0, 255).astype(np.uint8).tobytes())
            gr = rng.normal(0, 1.5, x.shape[:2]).astype(np.float32)[..., None]
            enc["B"].stdin.write(np.clip(x + d + gr, 0, 255).astype(np.uint8).tobytes())
        for k, e in enc.items():
            e.stdin.close(); e.wait(); parts[k].append(os.path.join(a.out, f"{k}_{name}.mp4"))
        print(f"GRADE {name} f{f0}-{f1} ({len(paths)}) raw p50 {p50 * 255:.2f} p90 {p90 * 255:.2f} -> {TARGET[name]}", flush=True)
    for k, lst in parts.items():
        if not lst:
            continue
        cat = os.path.join(a.out, f"concat_{k}.txt")
        open(cat, "w").write("".join(f"file '{q}'\n" for q in lst))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", cat, "-c", "copy",
                        os.path.join(a.out, f"reel_{k}.mp4")], check=True)
        print("REEL", os.path.join(a.out, f"reel_{k}.mp4"), flush=True)
