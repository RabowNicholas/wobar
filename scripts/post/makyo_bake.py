"""MAKYO audio -> per-frame control curves for Blender (30 fps, frame 1 = 0 s).

    python3 scripts/post/makyo_bake.py

Reads the stem survey's hit lists (makyo_stems.py) plus the low stem, writes makyo_curves.json:
  snare      0..1   flash on each snare hit, exp decay over the bar (tau SNARE_TAU)
  kick_acc   hits   cumulative kick surges, alpha-function speed bump (KICK_TAU) (Blender scales to frames)
  vortex_acc s      integral of 808 level x direction (E1 +1, F#1 -1, eased over a bar)
  low        0..1   808 level, smoothed
  kick_idx   int    kick counter (the shard break sim fires when it steps)
  kick_vel   0..1   velocity of the latest kick
  kick_flash 0..1   short light pulse per kick (tau KICK_FLASH_TAU)
  hat_env    0..1   fast flash per hat hit
  hat_idx    int    hat hit counter (re-seeds which dust specks glint)
  hat_bright 0..1   hat spectral centroid 10.8 -> 12.4 kHz, smoothed over 2 bars
"""
import json, subprocess
import numpy as np

A = "/Volumes/music/blender/makyo_assets/"
LOW = "/Volumes/music/sessions/WIP (ACTIVE)/yagami Project/makyo_low_pass_stem.wav"
HATS = "/Volumes/music/sessions/WIP (ACTIVE)/yagami Project/makyo_hats_stem.wav"
FPS, SR = 30, 44100
SNARE_TAU, KICK_TAU, HAT_TAU = 0.42, 0.10, 0.05
SPIN_RISE, SPIN_FALL = 0.5, 1.5
BUILD_BARS, BUILD_PEAK = (48, 57), 4.0
ALWAYS_CW, CW_SIGN = True, 1.0   # +angle about +Y = clockwise on screen (verified 2026-11-03: node angle and screen angle measured in one pass)
KICK_FLASH_TAU = 0.12
DROP_SURGE, DROP_TAU, DROP_FLASH_TAU = 180.0, 0.3, 0.7


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def smooth(x, n):
    if n < 2:
        return x
    w = np.hanning(n); w /= w.sum()
    return np.convolve(np.pad(x, (n // 2, n - n // 2 - 1), mode="edge"), w, "valid")


def main():
    S = json.load(open(A + "makyo_stems.json"))
    bar = S["bar"]
    low = load(LOW)
    dur = len(low) / SR
    nf = int(np.ceil(dur * FPS))
    t = np.arange(nf) / FPS
    hits = {k: [(a, v) for a, v in S["hits"][k] if v > th] for k, th in
            (("snare", 0.2), ("kick", 0.2), ("hats", 0.1))}

    snare = np.zeros(nf)
    for a, v in hits["snare"]:
        m = t >= a
        snare[m] = np.maximum(snare[m], v * np.exp(-(t[m] - a) / SNARE_TAU))

    # each kick = one unit of travel, delivered by an alpha-function speed bump
    # (speed ~ x e^(1-x), x = dt / KICK_TAU): smooth attack peaking at KICK_TAU, long glide out
    kick = np.zeros(nf)
    for a, v in hits["kick"]:
        x = np.clip((t - a) / KICK_TAU, 0, None)
        kick += v * (1 - (1 + x) * np.exp(-x))

    # kick_idx: kicks so far (a step on each hit), kick_vel: velocity of the latest kick
    kick_idx, kick_vel = np.zeros(nf), np.zeros(nf)
    for i, (a, v) in enumerate(hits["kick"]):
        m = t >= a
        kick_idx[m] = i + 1
        kick_vel[m] = v

    # kick_flash: a short real-light pulse on each kick (drives the core alongside the snare)
    kick_flash = np.zeros(nf)
    for a, v in hits["kick"]:
        m = t >= a
        kick_flash[m] = np.maximum(kick_flash[m], v * np.exp(-(t[m] - a) / KICK_FLASH_TAU))

    # camera jolt: per kick, a damped shake (12 Hz, tau 0.07 s) in a random direction, scaled by velocity
    rngj = np.random.default_rng(3)
    jx, jz, jr = np.zeros(nf), np.zeros(nf), np.zeros(nf)
    for a, v in hits["kick"]:
        m = t >= a
        dt_ = t[m] - a
        env = v * np.exp(-dt_ / 0.07) * np.sin(2 * np.pi * 12 * dt_ + np.pi / 2)
        ang = rngj.uniform(0, 2 * np.pi)
        jx[m] += env * np.cos(ang); jz[m] += env * np.sin(ang); jr[m] += env * rngj.choice((-1, 1))

    hat_env, hat_idx = np.zeros(nf), np.zeros(nf)
    for i, (a, v) in enumerate(hits["hats"]):
        m = t >= a
        hat_env[m] = np.maximum(hat_env[m], v * np.exp(-(t[m] - a) / HAT_TAU))
        hat_idx[m] = i + 1

    # 808 level per frame
    spf = SR // FPS
    lp = np.pad(low, (0, nf * spf - len(low))) if nf * spf > len(low) else low[:nf * spf]
    rms = np.sqrt((lp.reshape(nf, spf) ** 2).mean(1) + 1e-14)
    db = 20 * np.log10(rms) - 20 * np.log10(rms.max())
    level = smooth(np.clip((db + 30) / 22, 0, 1), int(0.1 * FPS))

    # 808 note per bar from the low stem: autocorrelation pitch, E1 (41.2) vs F#1 (46.2)
    d = low[::8]; sr = SR / 8
    nbar = int(round(dur / bar))
    direction, cur = np.zeros(nf), 1.0
    for b in range(nbar):
        seg = d[int(b * bar * sr):int((b + 1) * bar * sr)]
        f0s = []
        w, lo, hi = int(0.12 * sr), int(sr / 60), int(sr / 32)
        for s in range(0, len(seg) - w, w // 2):
            fr = seg[s:s + w]
            if (fr ** 2).mean() < 1e-5:
                continue
            ac = np.correlate(fr, fr, "full")[w - 1:]
            k = lo + int(np.argmax(ac[lo:hi]))
            if ac[k] > 0.5 * ac[0]:
                f0s.append(sr / k)
        if len(f0s) >= 3:
            cur = 1.0 if np.median(f0s) < 43.7 else -1.0
        direction[int(b * bar * FPS):int((b + 1) * bar * FPS)] = cur
    direction = smooth(direction, int(bar * FPS))
    if ALWAYS_CW:          # Nick 2026-11-03: the field only ever turns clockwise; the 808 sets speed, not direction
        direction = np.full(nf, CW_SIGN)
    # spin has momentum: one-pole follower on the 808 level (rise SPIN_RISE s, coast SPIN_FALL s),
    # then a short Hann pass so the speed curve has no corners
    spin, y = np.zeros(nf), 0.0
    ar, af = 1 - np.exp(-1 / (SPIN_RISE * FPS)), 1 - np.exp(-1 / (SPIN_FALL * FPS))
    for i in range(nf):
        y += (level[i] - y) * (ar if level[i] > y else af)
        spin[i] = y
    spin = smooth(spin, int(0.3 * FPS))
    # breakdown wind-up: extra spin, cubic (slow then hard) over bars 48-56, peak = BUILD_PEAK x the
    # full-808 spin in total, cut on drop 2's downbeat (bar 57) so the field lurches back to normal
    bt_ = t / bar + 1
    b0, b1 = BUILD_BARS
    build = np.where((bt_ >= b0) & (bt_ < b1), ((bt_ - b0) / (b1 - b0)) ** 3, 0.0) * BUILD_PEAK   # 808 is near-silent here, so the build carries the full 4x
    bdir = CW_SIGN if ALWAYS_CW else (np.sign(direction[int((b0 + (b1 - b0) / 2 - 1) * bar * FPS)]) or 1.0)
    vortex = np.cumsum(spin * direction + build * bdir) / FPS

    hb = np.zeros(nf)
    hx = load(HATS)
    w = 2205
    for i in range(nf):
        s = int(i / FPS * SR)
        fr = hx[s:s + w]
        if len(fr) < w or (fr ** 2).mean() < 1e-7:
            continue
        mag = np.abs(np.fft.rfft(fr * np.hanning(w)))
        f = np.fft.rfftfreq(w, 1 / SR)
        hb[i] = (mag * f).sum() / (mag.sum() + 1e-12)
    hb_on = hb > 0
    hbv = np.where(hb_on, np.clip((hb - 10800) / 1600, 0, 1), np.nan)
    hbv = np.nan_to_num(hbv, nan=0.0)
    hat_bright = smooth(hbv, int(2 * bar * FPS))

    # ---- section controls -------------------------------------------------------------
    # (start bar, density, speed, glow, core, ramp bars into it; 0 = instant cut on the downbeat)
    SECTIONS = [(1, 0.0, 0.5, 0.6, 0.8, 0), (17, 1.0, 1.0, 1.0, 1.0, 0), (48, 1.0, 1.0, 1.0, 1.0, 0),
                (57, 1.0, 1.1, 1.0, 1.0, 0), (89, 1.0, 0.55, 1.0, 1.0, 2), (105, 1.0, 0.3, 0.15, 0.6, 1)]
    FINAL_GROW = (89, 105, 2.4, 1.8)            # bars, glow x, core x: the pull toward the light
    bt = t / bar + 1                             # bar position, 1-based
    sec = np.zeros((4, nf))
    for i, (b0, *vals, ramp) in enumerate(SECTIONS):
        v = np.array(vals)[:, None]
        if i == 0:
            sec[:] = v
            continue
        prev = sec.copy()
        f = np.clip((bt - (b0 - ramp)) / ramp, 0, 1) if ramp else (bt >= b0).astype(float)
        f = f * f * (3 - 2 * f)
        sec = prev * (1 - f) + v * f
    g0, g1, gk, ck = FINAL_GROW
    grow = np.clip((bt - g0) / (g1 - g0), 0, 1) * (bt < g1)
    sec[2] *= 1 + (gk - 1) * grow ** 2
    sec[3] *= 1 + (ck - 1) * grow ** 2
    sec_density, sec_speed, sec_glow, sec_core = sec
    stream_base = 1 + np.concatenate([[0], np.cumsum(sec_speed[:-1])])   # frames of stream travel

    drop_t = 16 * bar                            # bar 17 downbeat: the intact mirror shatters
    # the shatter: one big alpha-function surge of DROP_SURGE stream frames, plus a light flash
    xd = np.clip((t - drop_t) / DROP_TAU, 0, None)
    stream_base = stream_base + DROP_SURGE * (1 - (1 + xd) * np.exp(-xd))
    drop_flash = np.where(t >= drop_t, np.exp(-np.clip(t - drop_t, 0, None) / DROP_FLASH_TAU), 0.0)
    intact = (t < drop_t).astype(float)
    intro_sn = [(a, v) for a, v in hits["snare"] if a < drop_t]
    crack = np.zeros(nf)
    for a, v in intro_sn:
        x = np.clip((t - a) / 0.2, 0, 1)
        crack += x * x * (3 - 2 * x)
    crack = 0.12 + 0.78 * crack / max(len(intro_sn), 1)
    fd = int(np.searchsorted(t, drop_t))
    st_drop = float(stream_base[fd] + 7.5 * kick[fd])   # assumes kick_surge 7.5 (MAKYO_CTRL)

    out = dict(fps=FPS, frames=nf, sec_density=sec_density, sec_speed=sec_speed, sec_glow=sec_glow,
               sec_core=sec_core, stream_base=stream_base, drop_flash=drop_flash, intact=intact, crack=crack, st_drop=st_drop,
               drop_frame=fd + 1, snare=snare, kick_acc=kick, kick_idx=kick_idx, kick_vel=kick_vel, kick_flash=kick_flash, jolt_x=jx, jolt_z=jz, jolt_r=jr, vortex_acc=vortex, low=level,
               hat_env=hat_env, hat_idx=hat_idx, hat_bright=hat_bright)
    out = {k: (np.round(v, 5).tolist() if isinstance(v, np.ndarray) else v) for k, v in out.items()}
    print(f"drop frame {fd + 1}, st_drop {st_drop:.1f}, intro snares {len(intro_sn)}")
    json.dump(out, open(A + "makyo_curves.json", "w"))
    print(f"{nf} frames; hits used: snare {len(hits['snare'])} kick {len(hits['kick'])} hats {len(hits['hats'])}")
    print("808 direction by 8 bars:", " ".join("+" if direction[int(b * bar * FPS)] > 0 else "-" for b in range(0, nbar, 8)))
    print(f"vortex_acc end {vortex[-1]:.1f} s; kick_acc end {kick[-1]:.1f}; hat_bright max {hat_bright.max():.2f}")


main()
