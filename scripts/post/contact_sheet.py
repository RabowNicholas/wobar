"""Timecoded contact sheets from review stills (2026-10-26).

    python3 contact_sheet.py DIR [--cols 6] [--gain auto|N] [--gamma 0.6]

Reads DIR/s_#####.png (16-bit, via ffmpeg so the low bits survive), applies ONE stand-in view curve to every still
(no grade LUT yet: out = clip(in * gain) ** gamma, gain chosen so the brightest 0.5% of all pixels in the set
lands near white), and writes one sheet per song to DIR/sheets/. The curve is the same for every tile, so
relative brightness between tiles is real; absolute brightness is not the grade.
"""
import os, sys, glob, subprocess, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 24
SONGS = [("1_ERNSTFALL", 1, 5688), ("2_ABGRUND", 5689, 10944), ("3_GRUND", 10945, 99999)]
CUES = {7933: "edge", 8262: "roll", 8756: "cut", 8919: "drop"}  # ABGRUND fall: master seconds x 24 + 1


def load16(path):
    w, h = Image.open(path).size
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint16).reshape(h, w, 3).astype(np.float32) / 65535


def tc(f):
    s = (f - 1) / FPS
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dir")
    p.add_argument("--cols", type=int, default=6)
    p.add_argument("--gain", default="auto")
    p.add_argument("--gamma", type=float, default=0.6)
    a = p.parse_args()
    files = sorted(glob.glob(os.path.join(a.dir, "s_*.png")))
    frames = {int(os.path.basename(f)[2:7]): f for f in files}
    imgs = {f: load16(path) for f, path in frames.items()}
    if a.gain == "auto":
        allpx = np.concatenate([im[::4, ::4].max(2).ravel() for im in imgs.values()])
        gain = 0.9 / max(np.percentile(allpx, 99.5), 1e-6)
    else:
        gain = float(a.gain)
    print(f"gain {gain:.1f} gamma {a.gamma}")
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    out = os.path.join(a.dir, "sheets"); os.makedirs(out, exist_ok=True)
    for name, f0, f1 in SONGS:
        fs = [f for f in sorted(imgs) if f0 <= f <= f1]
        if not fs:
            continue
        h, w, _ = imgs[fs[0]].shape
        tw, th = 480, int(480 * h / w)
        rows = (len(fs) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (a.cols * (tw + 4) + 4, rows * (th + 26) + 4), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(fs):
            v = np.clip(imgs[f] * gain, 0, 1) ** a.gamma
            t = Image.fromarray((v * 255 + .5).astype(np.uint8)).resize((tw, th), Image.LANCZOS)
            x, y = 4 + (i % a.cols) * (tw + 4), 4 + (i // a.cols) * (th + 26)
            sheet.paste(t, (x, y + 22))
            cue = next((c for k, c in CUES.items() if abs(k - f) < 24), "")
            d.text((x + 2, y + 2), f"{tc(f)}  f{f}  {cue}", fill=(255, 220, 120) if cue else (220, 220, 220), font=font)
        path = os.path.join(out, f"{name}.png"); sheet.save(path)
        print(path, len(fs))


if __name__ == "__main__":
    main()
