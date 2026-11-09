"""YouTube survival tests for the HOHLWEG grade (2026-11-04). Nick: "make sure that i can push this grade where i want and
not worry about the youtube compression stuff". Watched on phone, computer and TV. Every segment is labelled on screen.

    nice -n 19 python3 scripts/post/yt_tests.py --src renders/reel_01 --out renders/reel_01/yt_tests

T1 grain ladder   which grain does YouTube's encode keep? fog / trench / lane (the three hardest: contours, the darkest
                  clip, the biggest lift) x  dither only | grain 1.0 | grain 1.5 | grain 2.5   (sigma in 8-bit codes)
T2 push ladder    how far can the grade go before YouTube breaks it? same clips x  stand-in night curve | pushed bright
                  (p50 30, p90 95) | patina push (stand-in + strong green in the shadows; 4:2:0 chroma is what fails)
                  Dither only, the hardest case: if it holds here it holds with grain.
T3 ramps          a synthetic dark gradient, 0 -> 48/255, in four bands: none | dither | grain 1.5 | grain 2.5.
                  Separates the display's own banding (TV processing) from YouTube's: if the 'none' band bands on
                  the local file too, it is the screen.
Each segment 5 s, no audio. H.264 crf 12, yuv420p, 4K.
"""
import argparse, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import reel_grade as g

CLIPS = [("fog", 13297), ("trench", 8977), ("lane", 721)]
N = int(os.environ.get("YT_N", 120))  # YT_N=6 for a smoke test
GRAINS = [("dither only", 0.0), ("grain 1.0", 1.0), ("grain 1.5", 1.5), ("grain 2.5", 2.5)]
PUSH = ["stand-in", "pushed bright", "patina push"]
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 56)


def label(text):
    """A dark box with white text, as an RGB uint8 patch for the top-left corner."""
    w = int(FONT.getlength(text)) + 48
    im = Image.new("RGB", (w, 90), (0, 0, 0))
    ImageDraw.Draw(im).text((24, 14), text, font=FONT, fill=(235, 235, 235))
    return np.asarray(im)


def stamp(frame, patch, x=40, y=40):
    frame[y:y + patch.shape[0], x:x + patch.shape[1]] = patch
    return frame


def encoder(path, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", "24", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                             "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)


def patina(x):
    """Stand-in for Nick's post push: shadows pulled hard toward green, luminance kept."""
    y = g.lum(x)[..., None]
    mask = np.clip(1 - y / 0.35, 0, 1) ** 1.5
    tinted = x * np.array([0.70, 1.12, 0.78], np.float32)
    tinted *= y / np.maximum(g.lum(tinted)[..., None], 1e-9)
    return np.clip(x + (tinted - x) * mask, 0, 1)


def to8(x, d, gr=None, sigma=0.0):
    v = x * 255 + d
    if sigma:
        v = v + gr * sigma
    return np.clip(v, 0, 255).astype(np.uint8)


def concat(parts, path):
    lst = path + ".txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", path], check=True)
    for p in parts:
        os.remove(p)
    os.remove(lst)
    print("DONE", path, flush=True)


def ramps(out, w=3840, h=2160, rng=None):
    bands = [("no dither", None), ("dither", 0.0), ("grain 1.5", 1.5), ("grain 2.5", 2.5)]
    base = np.tile(np.linspace(0, 48 / 255, w, dtype=np.float32)[None, :, None], (h, 1, 3))
    bh = h // 4
    enc = encoder(os.path.join(out, "T3_ramps.mp4"), w, h)
    patches = [label(f"T3 ramp  |  {name}") for name, _ in bands]
    for _ in range(N * 2):
        d = rng.uniform(-.5, .5, (h, w, 3)).astype(np.float32) + rng.uniform(-.5, .5, (h, w, 3)).astype(np.float32)
        gr = rng.normal(0, 1, (h, w)).astype(np.float32)[..., None]
        f = np.empty((h, w, 3), np.uint8)
        for i, (name, s) in enumerate(bands):
            sl = slice(i * bh, (i + 1) * bh)
            if s is None:
                f[sl] = np.round(base[sl] * 255).astype(np.uint8)
            else:
                f[sl] = to8(base[sl], d[sl], gr[sl], s)
            stamp(f, patches[i], y=i * bh + 30)
        enc.stdin.write(f.tobytes())
    enc.stdin.close(); enc.wait()
    print("DONE", os.path.join(out, "T3_ramps.mp4"), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True); p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(11)
    ramps(a.out, rng=rng)
    t1, t2 = [], []
    for name, f0 in CLIPS:
        paths = [os.path.join(a.src, "beauty", f"hohlweg_{f:05d}.png") for f in range(f0, f0 + N)]
        t50, t90 = (v / 255 for v in g.TARGET[name])
        fit_std = g.fit(paths[::10], t50, t90)
        fit_hi = g.fit(paths[::10], 30 / 255, 95 / 255)
        h, w = g.load(paths[0]).shape[:2]
        segs1 = [(os.path.join(a.out, f"_t1_{name}_{i}.mp4"), label(f"T1  {name}  |  {lab}"), s) for i, (lab, s) in enumerate(GRAINS)]
        segs2 = [(os.path.join(a.out, f"_t2_{name}_{i}.mp4"), label(f"T2  {name}  |  {lab}")) for i, lab in enumerate(PUSH)]
        e1 = [encoder(s[0], w, h) for s in segs1]
        e2 = [encoder(s[0], w, h) for s in segs2]
        for q in paths:
            x = g.load(q)
            std = g.tone(x, *fit_std[:2])
            d = rng.uniform(-.5, .5, x.shape).astype(np.float32) + rng.uniform(-.5, .5, x.shape).astype(np.float32)
            gr = rng.normal(0, 1, x.shape[:2]).astype(np.float32)[..., None]
            for (path, patch, s), e in zip(segs1, e1):
                e.stdin.write(stamp(to8(std, d, gr, s), patch).tobytes())
            for (path, patch), e, im in zip(segs2, e2, (std, g.tone(x, *fit_hi[:2]), patina(std))):
                e.stdin.write(stamp(to8(im, d), patch).tobytes())
        for e in e1 + e2:
            e.stdin.close(); e.wait()
        t1 += [s[0] for s in segs1]; t2 += [s[0] for s in segs2]
        print("CLIP", name, flush=True)
    concat(t1, os.path.join(a.out, "T1_grain.mp4"))
    concat(t2, os.path.join(a.out, "T2_push.mp4"))
