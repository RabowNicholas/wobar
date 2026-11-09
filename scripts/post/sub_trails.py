"""Sub-driven feedback trails on the forms layer, offline and frame-exact (replaces the TouchDesigner pass).

    python3 sub_trails.py FORMS_DIR START COUNT OUT_DIR [--beauty BEAUTY_DIR --audio WAV]

Classic feedback loop, run at full resolution in 16-bit:
    loop  = max(fresh, decay * hue(blur(warp(loop_prev))))
    trail = loop - fresh            # the beauty already has this frame's wires
The drive is the sub bass alone (hohlweg_subbass_stem), which is silent in the breakdowns by itself:
more drive = longer trails (decay). Reads forms_#####.png, writes trails_#####.png (16-bit RGB).
With --beauty, also writes preview.mp4: beauty + trails, with the audio.
"""
import argparse
import math
import os
import subprocess

import numpy as np
from scipy import ndimage

SUB = "/Volumes/music/sessions/FINISHED/originals/hohlweg_ep Project/hohlweg_subbass_stem.wav"
FPS = 24
# The sub bass stem (2026-10-15) runs 99 ms early against the stitched master, constant over the whole EP
# (waveform match at +99 ms explains 50-55% of the master's low end, at 0 ms ~2%), so it is read 99 ms back.
SUB_OFFSET = -0.099

LOOK = dict(
    # Afterglow (Nick, 2026-10-15, option 2): the wires leave a short glow where they were, like a
    # long exposure. No swell, no turn, no hue drift. The original feedback look was zoom_hi 1.022,
    # rotate 0.25, hue 2.5, half_hi 1.2 ("they feel really strong").
    half_lo=0.03, half_hi=0.25,      # trail half-life, seconds, at no drive / full drive (exponential between)
    zoom_lo=1.000, zoom_hi=1.000,    # outward swell per frame (eased: drive ** 1.5)
    sub_full=0.85,                   # smoothed sub level that counts as full (typical drop level)
    rotate_deg=0.0,                  # turn per frame
    hue_deg=0.0,                     # hue drift per frame (older trail = further round the wheel)
    blur=0.6,                        # gaussian sigma per frame, px at 1080p
    sub_floor_db=-42.0,              # sub level that counts as none (below the EP's loudest)
    attack=0.05, release=0.30,       # seconds, smoothing of the sub envelope
)


def sub_envelope(frames):
    """0-1 trail drive for each frame number (frame 1 = master 0:00): the smoothed sub bass level."""
    sr = 11025
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SUB, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    win = sr // FPS
    n = len(x) // win
    stem_db = 20 * np.log10(np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1)) + 1e-9)
    stem_db -= stem_db.max()
    out, level = [], 0.0
    for f in frames:
        t = (f - 1) / FPS
        db = stem_db[min(max(int((t + SUB_OFFSET) * FPS), 0), n - 1)]
        target = min(max(1 - db / LOOK["sub_floor_db"], 0.0), 1.0)
        tau = LOOK["attack"] if target > level else LOOK["release"]
        level += (target - level) * (1 - math.exp(-1 / (FPS * tau)))
        out.append(min(level / LOOK["sub_full"], 1.0))
    return out


def half_life(drive):
    return LOOK["half_lo"] * (LOOK["half_hi"] / LOOK["half_lo"]) ** drive


def hue_matrix(deg):
    """Rotate RGB about the grey axis (keeps brightness roughly constant)."""
    a = math.radians(deg)
    c, s, k = math.cos(a), math.sin(a), 1 / 3
    q = math.sqrt(k)
    return np.array([[c + (1 - c) * k, k * (1 - c) - q * s, k * (1 - c) + q * s],
                     [k * (1 - c) + q * s, c + (1 - c) * k, k * (1 - c) - q * s],
                     [k * (1 - c) - q * s, k * (1 - c) + q * s, c + (1 - c) * k]], np.float32)


def warp(img, zoom, rot_deg):
    """Scale up by `zoom` and turn by `rot_deg` about the centre (the trail swells outward)."""
    h, w = img.shape[:2]
    a = math.radians(rot_deg)
    m = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]) / zoom
    centre = np.array([h / 2, w / 2])
    off = centre - m @ centre
    return np.stack([ndimage.affine_transform(img[..., ch], m, offset=off, order=1, mode="constant")
                     for ch in range(3)], -1)


def reader(pattern, start, count, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-start_number", str(start), "-i", pattern,
                          "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"],
                         stdout=subprocess.PIPE)
    size = w * h * 3 * 2
    for _ in range(count):
        buf = p.stdout.read(size)
        yield np.frombuffer(buf, "<u2").reshape(h, w, 3).astype(np.float32) / 65535


def writer(pattern, start, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le",
                             "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-start_number", str(start),
                             "-pix_fmt", "rgb48be", pattern], stdin=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("forms"); ap.add_argument("start", type=int); ap.add_argument("count", type=int)
    ap.add_argument("out"); ap.add_argument("--beauty"); ap.add_argument("--audio")
    ap.add_argument("--beauty-name", default="beauty", help="beauty file prefix (the final is hohlweg)")
    ap.add_argument("--warmup", type=int, default=0, help="run the loop on this many frames before START without writing them (seamless batches)")
    ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w, h, scale = a.w, a.h, max(a.w, a.h) / 1920   # 1 for the square master and both 1080p crops
    wu = min(a.warmup, a.start - 1)
    frames = range(a.start - wu, a.start + a.count)
    sub = sub_envelope(frames)
    hue = hue_matrix(LOOK["hue_deg"])
    tw = writer(os.path.join(a.out, "trails_%05d.png"), a.start, w, h)
    pv = None
    if a.beauty:
        beauty = reader(os.path.join(a.beauty, a.beauty_name + "_%05d.png"), a.start, a.count, w, h)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{w}x{h}",
               "-r", str(FPS), "-i", "-"]
        if a.audio:
            cmd += ["-ss", f"{(a.start - 1) / FPS:.4f}", "-i", a.audio, "-c:a", "aac", "-b:a", "256k", "-shortest"]
        # 10-bit HEVC: an 8-bit preview bands in these shadows
        pv = subprocess.Popen(cmd + ["-c:v", "hevc_videotoolbox", "-profile:v", "main10", "-b:v", "80M",
                                     "-tag:v", "hvc1", "-pix_fmt", "p010le",
                                     os.path.join(a.out, "preview.mp4")], stdin=subprocess.PIPE)
    loop = None
    for i, (f, fresh) in enumerate(zip(frames, reader(os.path.join(a.forms, "forms_%05d.png"),
                                                      a.start - wu, a.count + wu, w, h))):
        s = sub[i]
        if loop is None:
            loop = fresh.copy()          # no history yet: the first frame leaves no trail
        else:
            decay = 0.5 ** (1 / (FPS * half_life(s)))
            zoom = LOOK["zoom_lo"] + (LOOK["zoom_hi"] - LOOK["zoom_lo"]) * s ** 1.5
            prev = warp(loop, zoom, LOOK["rotate_deg"])
            prev = ndimage.gaussian_filter(prev, (LOOK["blur"] * scale, LOOK["blur"] * scale, 0))
            prev = np.clip(prev @ hue.T, 0, None) * decay
            loop = np.maximum(fresh, prev)
        if i < wu:
            continue
        trail = np.clip(loop - fresh, 0, 1)
        tw.stdin.write((trail * 65535 + 0.5).astype("<u2").tobytes())
        if pv:
            b = next(beauty)
            pv.stdin.write((np.clip(b + trail, 0, 1) * 65535 + 0.5).astype("<u2").tobytes())
        if i % 24 == 0:
            print(f"frame {f}  sub {s:.2f}", flush=True)
    tw.stdin.close(); tw.wait()
    if pv:
        pv.stdin.close(); pv.wait()


if __name__ == "__main__":
    main()
