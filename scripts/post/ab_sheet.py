"""Before/after sheet for review stills (2026-10-26).

    python3 ab_sheet.py BEFORE_DIR AFTER_DIR OUT.png [--gain 5.6] [--gamma 0.6] [--cols 2] [--notes "f:text,..."]

Pairs every s_#####.png in AFTER_DIR with the same frame in BEFORE_DIR, left = before, right = after, with the
same fixed view curve as contact_sheet.py so the two sides compare honestly. Prints mean brightness per side.
"""
import os, sys, glob, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contact_sheet import load16, tc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("before"); p.add_argument("after"); p.add_argument("out")
    p.add_argument("--gain", type=float, default=5.6)
    p.add_argument("--gamma", type=float, default=0.6)
    p.add_argument("--notes", default="")
    a = p.parse_args()
    notes = dict((int(k), v) for k, v in (x.split(":", 1) for x in a.notes.split(",") if x))
    frames = sorted(int(os.path.basename(f)[2:7]) for f in glob.glob(os.path.join(a.after, "s_*.png")))
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
    W, H, LH = 960, 540, 28
    sheet = Image.new("RGB", (2 * W + 12, len(frames) * (H + LH + 6) + 6), (35, 35, 35))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        y = 6 + i * (H + LH + 6)
        means = []
        for j, src in enumerate((a.before, a.after)):
            path = os.path.join(src, f"s_{f:05d}.png")
            if not os.path.exists(path):
                continue
            im = load16(path); means.append(im.mean())
            v = np.clip(im * a.gain, 0, 1) ** a.gamma
            t = Image.fromarray((v * 255 + .5).astype(np.uint8)).resize((W, H), Image.LANCZOS)
            sheet.paste(t, (4 + j * (W + 4), y + LH))
        ratio = f"  x{means[1] / means[0]:.2f}" if len(means) == 2 and means[0] > 0 else ""
        d.text((8, y + 4), f"BEFORE  {tc(f)}  f{f}  {notes.get(f, '')}", fill=(255, 220, 120), font=font)
        d.text((W + 12, y + 4), f"AFTER{ratio}", fill=(160, 230, 160), font=font)
        print(f, tc(f), [f"{m:.5f}" for m in means], ratio)
    sheet.save(a.out); print(a.out)


if __name__ == "__main__":
    main()
