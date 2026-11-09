"""Per-aspect review sheets from review_kit.py output (2026-11-02).

Two steps, because Blender's Python reads multilayer EXR (OpenImageIO) but has no PIL, and system Python the reverse:
    BP=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
    $BP review_sheets.py extract DIR        -> DIR/x_#####.npz (tiles, crops) + DIR/measure.json
    python3 review_sheets.py sheets DIR     -> DIR/light.png, surfaces.png, forms.png

View: the same stand-in curve as contact_sheet / ab_sheet (clip(x * 5.6) ** 0.6) on the beauty AND on every
component, so components read in proportion to the image they build. Albedo is shown linear -> sRGB, no exposure.

Light       beauty | surfaces lit (Diffuse Direct) | fog lit (Volume Direct) | glow (Emission: forms, stars, motes)
            | sky (Environment) | reflections (Glossy Direct). Shares = each component's mean / their sum.
Surfaces    beauty | albedo | albedo flags (red: brighter than 0.6, nothing natural here is; blue: darker than 0.02;
            magenta: saturation > 0.7) | 1:1 crop of the near ground | 1:1 crop of the most lit surface
Forms       beauty | forms AOV | 1:1 crop where the forms are densest, with the share of form pixels that read white-hot
"""
import os, sys, glob, json
import numpy as np

GAIN, GAM, DS = 5.6, 0.6, 6               # 3840x2160 / 6 = 640x360 tiles
CW, CH = 960, 540
FPS = 24
PASSES = {"beauty": "Composite.Combined", "comb": "ViewLayer.Combined", "diff": "ViewLayer.Diffuse Direct",
          "alb": "ViewLayer.Diffuse Color", "gloss": "ViewLayer.Glossy Direct", "vol": "ViewLayer.Volume Direct",
          "gcol": "ViewLayer.Glossy Color", "emit": "ViewLayer.Emission", "env": "ViewLayer.Environment",
          "forms": "ViewLayer.forms",
          "z": "ViewLayer.Depth"}


def tc(f):
    s = (f - 1) / FPS
    return f"{int(s // 60)}:{s % 60:04.1f}"


def curve(x):
    return (np.clip(x * GAIN, 0, 1) ** GAM * 255).astype(np.uint8)


def srgb(x):
    x = np.clip(x, 0, 1)
    return (np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055) * 255).astype(np.uint8)


def lum(x):
    return x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722


def small(x):
    h, w = x.shape[:2]
    return x[:h // DS * DS, :w // DS * DS].reshape(h // DS, DS, w // DS, DS, *x.shape[2:]).mean((1, 3))


def best_window(score, avoid_bottom=False):
    best, pos = -1, (0, 0)
    H, W = score.shape
    for y in range(0, H - CH + 1, 90):
        if avoid_bottom and y + CH > H - 300:
            continue
        for x in range(0, W - CW + 1, 120):
            s = score[y:y + CH, x:x + CW].sum()
            if s > best:
                best, pos = s, (y, x)
    return pos


def read_exr(path):
    import OpenImageIO as oiio
    inp = oiio.ImageInput.open(path)
    out, i = {}, 0
    while inp.seek_subimage(i, 0):
        spec = inp.spec()
        px = inp.read_image(i, 0, 0, spec.nchannels, "float")
        base = spec.channelnames[0].rsplit(".", 1)[0]
        out[base] = np.asarray(px)[..., :3] if spec.nchannels >= 3 else np.asarray(px)[..., 0]
        i += 1
    inp.close()
    return out


def extract(d):
    meas = {}
    for path in sorted(glob.glob(f"{d}/p_*.exr")):
        f = int(path[-9:-4])
        npz = f"{d}/x_{f:05d}.npz"
        e = read_exr(path)
        P = {k: e[v] for k, v in PASSES.items() if v in e}
        P["diff"] = P["diff"] * P["alb"]          # EEVEE light passes are light before colour: contribution = light x colour
        P["gloss"] = P["gloss"] * P["gcol"]
        b = P["beauty"]; bl = curve(b)
        sky = P["z"] > 1e4
        surf = ~sky
        m = {"t": tc(f)}
        comps = {k: float(P[k].mean()) for k in ("diff", "vol", "emit", "env", "gloss")}
        tot = sum(comps.values()) or 1
        m["share"] = {k: round(v / tot, 3) for k, v in comps.items()}
        m["comb_vs_sum"] = round(float(P["comb"].mean()) / tot, 3)
        m["black"] = round(float((bl.max(2) == 0).mean()), 3)
        m["clip"] = round(float((bl.min(2) >= 254).mean()), 4)
        m["p50"], m["p90"] = [int(v) for v in np.percentile(bl.mean(2), [50, 90])]
        A = P["alb"]; al = lum(A); mx = A.max(2); sat = np.where(mx > 0, (mx - A.min(2)) / np.maximum(mx, 1e-6), 0)
        bright, dark = (al > 0.6) & surf, (al < 0.02) & surf
        oversat = (sat > 0.7) & (al > 0.03) & surf
        n = max(int(surf.sum()), 1)
        m["alb"] = {"median": round(float(np.median(al[surf])), 3) if surf.any() else 0,
                    "bright": round(float(bright.sum()) / n, 4), "dark": round(float(dark.sum()) / n, 4),
                    "oversat": round(float(oversat.sum()) / n, 4)}
        flag = srgb(A).copy()
        flag[bright] = (255, 0, 0); flag[dark] = (0, 90, 255); flag[oversat] = (255, 0, 255)
        fm = lum(P["forms"]) > 1e-3 if "forms" in P else np.zeros(al.shape, bool)
        m["forms_px"] = int(fm.sum())
        m["forms_white"] = round(float((bl.min(2)[fm] >= 230).mean()), 3) if fm.any() else None
        y1, x1 = 2160 - CH, (3840 - CW) // 2                               # near ground
        y2, x2 = best_window(lum(P["diff"]) * surf, avoid_bottom=True)      # most lit surface
        y3, x3 = best_window(fm.astype(np.float32))                         # densest forms
        m["crops"] = {"ground": [x1, y1], "lit": [x2, y2], "forms": [x3, y3]}
        tiles = {"beauty": curve(small(b)), "diff": curve(small(P["diff"])), "vol": curve(small(P["vol"])),
                 "emit": curve(small(P["emit"])), "env": curve(small(P["env"])), "gloss": curve(small(P["gloss"])),
                 "alb": srgb(small(A)), "flag": small(flag.astype(np.float32)).astype(np.uint8),
                 "forms": curve(small(P["forms"])) if "forms" in P else np.zeros_like(curve(small(b))),
                 "c_ground": bl[y1:y1 + CH, x1:x1 + CW], "c_lit": bl[y2:y2 + CH, x2:x2 + CW],
                 "c_forms": bl[y3:y3 + CH, x3:x3 + CW], "c_ground_alb": srgb(A[y1:y1 + CH, x1:x1 + CW])}
        np.savez_compressed(npz, **tiles)
        meas[str(f)] = m
        print(f, json.dumps(m), flush=True)
    old = json.load(open(f"{d}/measure.json")) if os.path.exists(f"{d}/measure.json") else {}
    old.update(meas)
    json.dump(old, open(f"{d}/measure.json", "w"), indent=1)


def sheets(d, frames_light=None, frames_forms=None):
    from PIL import Image, ImageDraw, ImageFont
    meas = json.load(open(f"{d}/measure.json"))
    font = ImageFont.load_default(size=22); small_f = ImageFont.load_default(size=18)
    frames = sorted(int(k) for k in meas)
    forms_frames = frames_forms or frames
    light_frames = frames_light or frames

    def build(name, flist, cols, caption, head):
        rows = []
        for f in flist:
            z = np.load(f"{d}/x_{f:05d}.npz"); m = meas[str(f)]
            ims = [(Image.fromarray(z[k]), lab) for k, lab in cols]
            w = sum(i.width for i, _ in ims) + 8 * (len(ims) - 1)
            h = max(i.height for i, _ in ims)
            row = Image.new("RGB", (w, h + 64), (16, 16, 16)); dr = ImageDraw.Draw(row)
            dr.text((8, 6), f"{m['t']}  (f{f})   " + caption(m), fill=(235, 235, 235), font=font)
            x = 0
            for im, lab in ims:
                row.paste(im, (x, 40)); dr.text((x + 6, 44), lab, fill=(255, 220, 120), font=small_f); x += im.width + 8
            rows.append(row)
        W = max(r.width for r in rows)
        sheet = Image.new("RGB", (W, sum(r.height for r in rows) + 50), (0, 0, 0))
        ImageDraw.Draw(sheet).text((8, 12), head, fill=(255, 255, 255), font=font)
        y = 50
        for r in rows:
            sheet.paste(r, (0, y)); y += r.height
        out = f"{d}/{name}.png"; sheet.save(out); print(out, sheet.size)

    pct = lambda v: f"{v * 100:.0f}%"
    build("light", light_frames,
          [("beauty", "beauty"), ("diff", "surfaces lit"), ("vol", "fog lit"), ("emit", "glow"), ("env", "sky"), ("gloss", "reflections")],
          lambda m: "shares  surf {diff}  fog {vol}  glow {emit}  sky {env}  refl {gloss}".format(**{k: pct(v) for k, v in m["share"].items()})
          + f"   black {pct(m['black'])}  clip {m['clip'] * 100:.2f}%  p50/p90 {m['p50']}/{m['p90']}",
          "LIGHT - every panel on the beauty's view curve, so a panel's brightness is its real contribution")
    build("surfaces", light_frames,
          [("beauty", "beauty"), ("alb", "albedo (colour, no light)"), ("flag", "flags"), ("c_ground", "near ground 1:1"), ("c_ground_alb", "its albedo 1:1"), ("c_lit", "most-lit surface 1:1")],
          lambda m: "albedo median {median}   >0.6 {b}   <0.02 {k}   sat>0.7 {s}".format(
              median=m["alb"]["median"], b=pct(m["alb"]["bright"]), k=pct(m["alb"]["dark"]), s=pct(m["alb"]["oversat"])),
          "SURFACES - flags: red albedo > 0.6 (brighter than anything natural here), blue < 0.02 (darker than charcoal), magenta saturation > 0.7")
    build("forms", forms_frames,
          [("beauty", "beauty"), ("forms", "forms AOV"), ("emit", "glow"), ("c_forms", "densest forms 1:1")],
          lambda m: f"form px {m['forms_px']:,}   white-hot {pct(m['forms_white']) if m['forms_white'] is not None else '-'}",
          "FORMS - hit peaks (kick, snare per song) then the key frames; white-hot = share of form pixels clipped near white")


if __name__ == "__main__":
    mode, d = sys.argv[1], sys.argv[2]
    if mode == "extract":
        extract(d)
    else:
        lf = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
        ff = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
        sheets(d, lf, ff)
