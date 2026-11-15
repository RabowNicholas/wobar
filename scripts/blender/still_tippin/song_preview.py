"""STILL TIPPIN — full-song structure preview, grey (2026-11-13). Run after exec(chamber.py) (_col).

No audio modulation yet: kick / snare / sub / hats are FAKE signals laid on the bar map read from
the master (130 bars at 140). Agreed with Nick:
  kick = push      camera surge + small swell; in Drop 1 it opens the throat; in Drop 2 each kick
                   adds a step of twist.
  snare = light    wall glow flash, only where the wall is stretched.
  sub = intensity  depth of the section's deformation + baseline glow.
  hats = detail    fine surface shiver, never the shape.
Lighting: headlamp (two lights riding the camera) + the wall lighting itself where stretched.
No core light (Nick, this track).

Sections (bars): intro 1-16 | rap 17-32 (riser leads straight in) | DROP 1 33-64 talking throat |
break 65-80 repeated line + riser | DROP 2 81-112 wring (81 tighten, 89 snap+tighten,
97 long unwind (highs dip), 105 hardest wring other way) | outro 113-128 snap back | end 129-130.

Build: one long tube, RMF frames along a wandering spine whose wander follows the section the
camera is in when it gets there. Static per-vertex attributes (theta, y, C, N, B, lump); a GN tree
rebuilds the radius each frame from keyed Value nodes, culls everything outside the camera window,
and stores 'stretch' for the glow.
"""
import bpy, math, random
from mathutils import Vector, Quaternion, Matrix

BPM = 140.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SONG_S = 222.857
FPS = 30
# v4 (Nick, 2026-11-14: "remove all audio modulation"): False strips every fake beat/riser
# signal (kick, snare, hats, risers/chaos, per-8th vowels). Sections + wring arcs stay.
AUDIO = False

# name, start bar, crossfade-in seconds, params
_B = dict(speed=1.0, roll=8.0, W=1.0, L=0.6, vowel=0.0, glow=0.0, kick=0.0, shiver=0.6,
          lamp=1.0, wander=0.5, sub=0.0, kick_on=0, snare_on=0, hats=8)
SECTIONS = [
    ("intro", 1, 0.0, dict(speed=0.7, roll=6, L=0.45, wander=0.5, shiver=0.6, lamp=0.85)),
    ("pre", 17, BAR, dict(speed=1.2, roll=10, L=0.7, vowel=0.25, glow=0.25, kick=0.4, sub=1,
                          wander=0.6, kick_on=1, snare_on=1, shiver=0.8)),
    ("drop1", 33, 0.12, dict(speed=2.0, roll=18, W=1.05, L=1.0, vowel=1.0, glow=1.0, kick=1.0,
                             sub=1, wander=1.0, kick_on=1, snare_on=1, hats=16, shiver=1.0)),
    # v2 break (Nick: "the same rap line repeated over and over"): the camera passes through the
    # SAME stretch of tunnel once per 4-bar line, roll locked so each pass lines up; the wall
    # mutates slowly across the repeats ("you look back and it's changed"). Riser on top.
    ("break", 65, 0.5 * BAR, dict(speed=1.2, roll=0, W=1.0, L=1.0, glow=0.3, kick=0.3, sub=0.6,
                                  wander=0.55, kick_on=1, snare_on=1, hats=8, shiver=0.9)),
    ("drop2a", 81, 0.12, dict(speed=1.9, roll=0, W=0.95, L=1.0, vowel=0.15, glow=1.0, kick=1.3,
                              sub=1, wander=0.75, kick_on=1, snare_on=1, hats=16, shiver=0.7)),
    ("drop2b", 89, 0.0, dict(speed=1.9, roll=0, W=0.95, L=1.0, vowel=0.15, glow=1.0, kick=1.3,
                             sub=1, wander=0.75, kick_on=1, snare_on=1, hats=16, shiver=0.7)),
    ("drop2c", 97, BAR, dict(speed=1.5, roll=0, W=1.0, L=1.0, vowel=0.1, glow=0.6, kick=1.1,
                             sub=1, wander=0.75, kick_on=1, snare_on=1, hats=0, shiver=0.0)),
    ("drop2d", 105, 0.12, dict(speed=2.1, roll=0, W=0.92, L=1.0, vowel=0.15, glow=1.2, kick=1.4,
                               sub=1, wander=0.75, kick_on=1, snare_on=1, hats=16, shiver=0.8)),
    ("outro", 113, 0.25, dict(speed=1.0, roll=8, L=0.6, glow=0.2, kick=0.4, sub=0.7, wander=0.45,
                              kick_on=1, snare_on=1, hats=8, shiver=0.6)),
    ("end", 129, 1.5 * BAR, dict(speed=0.2, roll=4, L=0.4, lamp=0.0, wander=0.45, shiver=0.2)),
]
SECTIONS = [(n, b, xf, dict(_B, **p)) for n, b, xf, p in SECTIONS]
# wring segments: (start bar, end bar, twist max rad/m, release style at the end)
# fake transitions stem (risers): (start bar, end bar, peak). Ramps up, cuts dead on the downbeat.
CHAOS = [(13, 17, 0.55), (25, 33, 1.0), (77, 81, 1.0), (111, 113, 0.45)]
# ribs B approved (Nick, 2026-11-14)
HYP = dict(LumpK=0.3, Rib=0.06, RibL=0.6, RibK=0.3, RibVarA=0.95, RibVarP=12.0, RibTilt=0.0, RibTiltTw=0.05, Hel=0.0, HelN=2.0, HelP=7.0, HelK=1.0,
           Fac=0.0, FacN=7.0, FacTw=0.08)
CAR = dict(on=True, face=(0.30, 0.008, 0.012), graze=(0.10, 0.008, 0.16), flop_blend=0.45,
           flake_tint=(1.0, 0.55, 0.25), spec_tint=(1.0, 0.75, 0.4), flake_scale=450.0, flake_k=0.12,
           metallic=0.6, rough=0.25, coat_rough=0.04, film_nm=420.0)
# Drop 2 = the liquid-metal melt (Nick, 2026-11-14: "melt in is really good"); v3 behaviour was
# fold_old=1, fold_oval=0, sq_k=1, melt_lump=0.3, melt_rib=0, melt_off=0.7, melt_rmin=0
DROP2 = dict(fold_old=0.0, fold_oval=0.3, sq_k=0.5, melt_lump=1.2, melt_rib=0.7,
             melt_off=0.25, melt_rmin=1.0, melt_eps=0.15)
DROP2_MODES = dict(A=dict(fold_old=0.0, fold_oval=1.0, sq_k=0.5, melt_lump=0.3, melt_rib=0.0),
                   B=dict(fold_old=0.0, fold_oval=0.3, sq_k=0.5, melt_lump=1.2, melt_rib=0.7,
                          melt_off=0.25, melt_rmin=1.0, melt_eps=0.15))
# depth pearl 14 m approved (Nick, 2026-11-14: "14 for sure")
# 2026-11-14 audio mapping test (fake signals until stems): kick = push (travel surge, which also lurches the
# depth pearl), snare = light (sun steps round the coil + flare), sub = intensity (walls breathe), hats = detail
# (flake glints). "tight" vs "swell" = the easing.
AMOD = dict(on=False, sun_step_deg=25.0, snare_tau=0.06, flare=0.5, flare_tau=0.03, hat_tau=0.05,
            glint_frac=0.003, glint_k=3.0, glint_far=6.0, breathe=0.06, sub_release=0.35, sub_attack=0.03, kick_tau=0.0)
AMOD_MODES = dict(tight=dict(on=True),
                  swell=dict(on=True, snare_tau=0.45, flare_tau=0.25, hat_tau=0.15, sub_release=0.9,
                             sub_attack=0.25, kick_tau=0.3))
DEPTH = dict(on=True, period_m=14.0, face_k=0.25,
             stops=[(0.3, (0.07, 0.005, 0.11)), (0.6, (0.30, 0.09, 0.02)), (0.8, (0.28, 0.17, 0.03))])
SUN = dict(on=True, hdri="/Volumes/music/blender/still_tippin_assets/abandoned_tank_farm_03_2k.hdr",
           sky_rot_deg=144.0, coat_k=1.0, fade_m=(6.0, 22.0),
           energy=30.0, angle_deg=3.0, color=(1.0, 0.95, 0.86), sun_az_deg=0.0, sun_elev_deg=39.4,
           exposure=-0.6, glare_thresh=2.0, glare_strength=0.6, glare_size=0.2)
PAINT = dict(BandA=0.0, BandL=3.5, BandN=1.0, BandSoft=0.6, BandSpd=0.0, InvA=0.0, InvP=16.0)
BREAK = (65, 81, 4)          # bars, line length in bars
WRING = [(81, 89, 0.42, "snap"), (89, 97, 0.58, "unwind"), (105, 113, -0.75, "snap")]   # v3: harder (Nick: drop 2 needs energy)

PV = dict(R=1.6, n_theta=144, dy=0.08, ahead=45.0, behind=4.0, look=4.5, lens=20,
          kpush=1.6, fill=45.0, fill_ahead=220.0, ahead_d=5.5, glow_k=0.0, snare_k=0.0,      # stretch light OFF for now (Nick)
          grey=0.30, rough=0.38, seed=7,
          # off-axis ride (2026-11-14, breaks the target symmetry): metres off the centre line, the side
          # drifts one way at off_rate deg/s; off_aim 0 = look parallel to the axis, 1 = aim back at it
          off=0.7, off_rate=6.0, off_phase=40.0, off_aim=0.0,
          wx=((5.2, 10.8, 0.0), (1.4, 5.7, 1.3), (0.4, 3.5, 2.1)),
          wz=((3.0, 13.5, 1.0), (1.0, 6.75, 0.4), (0.3, 4.0, 2.7)), descent=0.12)


def _t(bar, beat=0.0):
    return (bar - 1) * BAR + beat * BEAT


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def params_at(t):
    i = 0
    while i + 1 < len(SECTIONS) and t >= _t(SECTIONS[i + 1][1]):
        i += 1
    n, b, xf, cur = SECTIONS[i]
    if i == 0 or xf <= 0:
        return cur, n
    prev = SECTIONS[i - 1][3]
    u = _smooth((t - _t(b)) / xf)
    return {k: prev[k] + (cur[k] - prev[k]) * u for k in cur}, n


def _section_at_bar(bar):
    s = SECTIONS[0]
    for x in SECTIONS:
        if x[1] <= bar:
            s = x
    return s[3]


def chaos_at(t):
    if not AUDIO:
        return 0.0
    bar = t / BAR + 1
    for b0, b1, pk in CHAOS:
        if b0 <= bar < b1:
            return pk * _smooth((bar - b0) / (b1 - b0)) ** 1.6
        if b1 <= bar < b1 + 1:                       # release tail: momentum, not a cut
            return pk * math.exp(-(bar - b1) * BAR / 0.22)
    return 0.0


def _smooth_series(vals, tau):
    """Critically damped 2-pole smoothing (no steps, no kinks)."""
    a = 1.0 - math.exp(-1.0 / (FPS * tau))
    out, y1, y2 = [], vals[0], vals[0]
    for v in vals:
        y1 += a * (v - y1)
        y2 += a * (y1 - y2)
        out.append(y2)
    return out


def events():
    if not AUDIO:
        return [], [], []
    kicks, snares, hats = [], [], []
    for bar in range(1, 131):
        p = _section_at_bar(bar)
        if p["kick_on"]:
            kicks.append(_t(bar, 0))
            if bar % 2 == 0:
                kicks.append(_t(bar, 2.5))
        if p["snare_on"]:
            snares.append(_t(bar, 2))
        if p["hats"]:
            step = 4.0 / p["hats"]
            hats += [_t(bar, k * step) for k in range(int(p["hats"]))]
    return sorted(kicks), sorted(snares), sorted(hats)


def _env(evts, t, tau):
    v = 0.0
    for e in evts:
        if e > t:
            break
        if t - e < 6 * tau:
            v = max(v, math.exp(-(t - e) / tau))
    return v


def signals(nf):
    """Per-frame control values (everything except the spine)."""
    kicks, snares, hats = events()
    rnd = random.Random(3)
    dt = 1.0 / FPS
    out = {k: [] for k in ("W", "L", "Swell", "A2", "A3", "Phi", "Fo", "Hs", "T", "Sq", "Tw",
                           "Glow", "Snare", "lamp", "speed", "roll", "wander",
                           "C", "lens", "Boil", "Mut", "D2", "SunAz", "Flare", "Glint", "Breath")}
    # vowel targets per 8th, kick 8ths open wide
    eighth = BEAT / 2
    vt = {}
    sp = {k: [0.0, 0.0] for k in ("open", "a2", "a3", "phi")}
    tw = [0.0, 0.0]
    kickpart, lampflash, lenspunch = [], [], []
    for f in range(nf):
        t = f * dt
        P, name = params_at(t)
        ke = _env(kicks, t, 0.22)
        se = _env(snares, t, 0.30)
        he = _env(hats, t, 0.05)
        k8 = int(t / eighth)
        if k8 not in vt:
            on_kick = any(abs(kk - k8 * eighth) < 1e-3 for kk in kicks)
            vt[k8] = dict(open=1.0 if on_kick else rnd.choice((0.05, 0.3, 0.6, 0.9)),
                          a2=rnd.uniform(-1, 1), a3=rnd.uniform(-1, 1), phi=rnd.uniform(0, 6.28))
        if not AUDIO:
            vt[k8] = dict(open=0.0, a2=0.0, a3=0.0, phi=0.0)
        for k in sp:                                          # bouncy spring (overshoot)
            x, v = sp[k]
            for _ in range(4):
                a = 180.0 * (vt[k8][k] - x) - 9.0 * v
                v += a * dt / 4
                x += v * dt / 4
            sp[k] = [x, v]
        # wring target
        bar = t / BAR + 1
        tgt, stiff, damp = 0.0, 150.0, 8.0          # each kick step lands with a jolt
        for b0, b1, mx, style in WRING:
            if b0 <= bar < b1:
                if AUDIO:
                    ks = [k for k in kicks if _t(b0) <= k < _t(b1)]
                    done = sum(1 for k in ks if k <= t)
                    tgt = mx * done / max(1, len(ks))
                else:                                   # no kick steps: smooth wring over the segment
                    tgt = mx * _smooth((bar - b0) / (b1 - b0))
                    stiff, damp = 40.0, 12.0
            elif style == "unwind" and b1 <= bar < b1 + 8:
                tgt = mx * (1 - _smooth((bar - b1) / 8.0))
                stiff, damp = 20.0, 6.0
        x, v = tw
        for _ in range(4):
            a = stiff * (tgt - x) - damp * v
            v += a * dt / 4
            x += v * dt / 4
        tw = [x, v]
        sub = P["sub"]
        ch = chaos_at(t)
        out["C"].append(ch)
        out["lens"].append(PV["lens"] - 9.0 * ch * (0.6 + 0.4 * math.sin(t * 1.9)))
        out["Boil"].append(0.07 * ch)
        b0, b1, _ = BREAK
        out["Mut"].append(0.8 * _smooth((bar - b0) / (b1 - b0)))
        out["W"].append(P["W"])
        out["L"].append(P["L"] * (1 + 0.45 * ch))
        out["Swell"].append(P["vowel"] * 0.16 * sp["open"][0] * sub + 0.035 * P["kick"] * ke)
        out["A2"].append(P["vowel"] * 0.15 * sp["a2"][0] * sub)
        out["A3"].append(P["vowel"] * 0.09 * sp["a3"][0] * sub)
        out["Phi"].append(sp["phi"][0])
        wr = abs(tw[0]) / 0.75
        out["Fo"].append(0.18 * wr)
        out["Sq"].append(0.26 * wr * sub * DROP2["sq_k"])
        out["D2"].append(1.0 if _t(81) <= t < _t(113) else 0.0)
        out["Tw"].append(tw[0])
        out["Hs"].append(0.007 * P["shiver"] * he)
        out["T"].append(t)
        out["Glow"].append(PV["glow_k"] * P["glow"] * (0.4 + 0.6 * sub))
        out["Snare"].append(PV["snare_k"] * se * (1.0 if P["snare_on"] > 0.5 else 0.0))
        out["lamp"].append(P["lamp"])
        out["speed"].append(P["speed"] + 1.4 * ch)
        kickpart.append(PV["kpush"] * P["kick"] * ke)
        if AMOD["on"]:                       # 2026-11-14 mapping: the sun is the light now, not the headlamp
            lampflash.append(0.0)
            out["SunAz"].append(float(sum(1 for x in snares if x <= t)) * (1.0 if P["snare_on"] else 0.0))
            out["Flare"].append(se * P["snare_on"])
            out["Glint"].append(_env(hats, t, AMOD["hat_tau"]) * (1.0 if P["hats"] else 0.0))
            out["Breath"].append(_env(kicks, t, AMOD["sub_release"]) * P["sub"])   # fake sub: long kick tail
        else:
            lampflash.append(0.9 * se * P["snare_on"] * min(1.0, P["kick"]))   # snare = light, via the headlamp
            for k_ in ("SunAz", "Flare", "Glint", "Breath"):
                out[k_].append(0.0)
        lenspunch.append(-2.5 * ke * max(0.0, P["kick"] - 0.5))           # kick punches the lens in the drops
        out["roll"].append(P["roll"] + ch * (45 + 30 * math.sin(t * 2.3) * math.sin(t * 0.7)))
        out["wander"].append(P["wander"])
    # v3 (Nick: "section transitions end up a little choppy"): smooth the section / chaos
    # driven channels so nothing steps; kicks are added back after so they keep their punch.
    for k, tau in (("speed", 0.25), ("roll", 0.35), ("W", 0.2), ("L", 0.3), ("lens", 0.3),
                   ("Boil", 0.2), ("lamp", 0.3), ("Glow", 0.2), ("wander", 0.5), ("C", 0.2), ("D2", 0.3)):
        out[k] = _smooth_series(out[k], tau)
    if AMOD["on"]:
        # snare count eased into sun steps (tight = snap, swell = glide); sub breath and kick push softened
        out["SunAz"] = [AMOD["sun_step_deg"] * v for v in _smooth_series(out["SunAz"], AMOD["snare_tau"])]
        out["Breath"] = _smooth_series(out["Breath"], AMOD["sub_attack"])
        out["Flare"] = _smooth_series(out["Flare"], AMOD["flare_tau"])
        kickpart = _smooth_series(kickpart, AMOD["kick_tau"]) if AMOD["kick_tau"] > 0 else kickpart
        out["W"] = [w * (1 + AMOD["breathe"] * b) for w, b in zip(out["W"], out["Breath"])]
    out["speed"] = [v + kp for v, kp in zip(out["speed"], kickpart)]
    out["lamp"] = [v * (1 + fl) for v, fl in zip(out["lamp"], lampflash)]
    out["lens"] = [v + lp for v, lp in zip(out["lens"], lenspunch)]
    return out


# ------------------------------------------------------------------ geometry
def _y_at_bar(ycam, bar):
    return ycam[min(len(ycam) - 1, int(round(_t(bar) * FPS)))]


def _per_frame_to_y(ys, ycam, vals):
    out, f = [], 0
    for y in ys:
        while f + 1 < len(ycam) and ycam[f] < y:
            f += 1
        out.append(vals[f])
    return out


def _spine(ycam, wander, chaos):
    """y grid, centre line, with wander amplitude following the camera's section at each y."""
    p = PV
    y_end = ycam[-1] + p["ahead"] + 2
    ys = [-p["behind"] - 1 + i * p["dy"] for i in range(int((y_end + p["behind"] + 1) / p["dy"]) + 1)]
    # A(y): wander of the frame when the camera reaches y, then a 10 m moving average
    A, f = [], 0
    for y in ys:
        while f + 1 < len(ycam) and ycam[f] < y:
            f += 1
        A.append(wander[f])
    win = int(5.0 / p["dy"])
    pre = [0.0]
    for a in A:
        pre.append(pre[-1] + a)
    As = [(pre[min(len(A), i + win)] - pre[max(0, i - win)]) / (min(len(A), i + win) - max(0, i - win))
          for i in range(len(A))]
    Cy = _per_frame_to_y(ys, ycam, chaos)
    cw = int(1.5 / p["dy"])
    cpre = [0.0]
    for v in Cy:
        cpre.append(cpre[-1] + v)
    Cy = [(cpre[min(len(Cy), i + cw)] - cpre[max(0, i - cw)]) / (min(len(Cy), i + cw) - max(0, i - cw))
          for i in range(len(Cy))]
    # break: one line = one period P of tunnel (measured from the camera's actual travel)
    b0, b1, lb = BREAK
    yin, yout = _y_at_bar(ycam, b0), _y_at_bar(ycam, b1)
    yref = _y_at_bar(ycam, b0 + lb)
    P = _y_at_bar(ycam, b0 + 2 * lb) - yref
    w = 2 * math.pi / P

    def base(y, a):
        x = a * sum(am * (math.sin(y / per + ph) - math.sin(ph)) for am, per, ph in p["wx"])
        z = a * sum(am * (math.sin(y / per + ph) - math.sin(ph)) for am, per, ph in p["wz"])
        return x, z

    ain = As[min(len(As) - 1, int((yin - ys[0]) / p["dy"]))]
    aout = As[min(len(As) - 1, int((yout - ys[0]) / p["dy"]))]
    xin, zin = base(yin, ain)
    xout, zout = base(yout, aout)
    C, BW = [], []
    for y, a, ch in zip(ys, As, Cy):
        x, z = base(y, a)
        bw = _smooth((y - yin) / 3.0) * (1 - _smooth((y - (yout - 3.0)) / 3.0)) if yin <= y <= yout else 0.0
        if bw > 0:
            u = (y - yin) / (yout - yin)
            q = (y - yref) * w
            xb = xin + (xout - xin) * u + 0.40 * math.sin(q) + 0.08 * math.sin(2 * q + 1.3)
            zb = zin + (zout - zin) * u + 0.30 * math.sin(q + 1.1) + 0.06 * math.sin(2 * q + 0.4)
            x, z = x + (xb - x) * bw, z + (zb - z) * bw
        # riser whip: tighter, faster bends that only exist where the chaos is
        x += ch * (0.55 * math.sin(y / 3.6 + 0.7) + 0.28 * math.sin(y / 2.6 + 2.0))   # bend radius stays > tube
        z += ch * (0.45 * math.sin(y / 3.2 + 1.4) + 0.22 * math.sin(y / 2.4 + 0.3))
        C.append(Vector((x, y, z - p["descent"] * y)))
        BW.append(bw)
    T = [(C[min(len(C) - 1, i + 1)] - C[max(0, i - 1)]).normalized() for i in range(len(C))]
    N = [(Vector((1, 0, 0)) - Vector((1, 0, 0)).dot(T[0]) * T[0]).normalized()]
    for i in range(1, len(C)):
        N.append((N[-1] - N[-1].dot(T[i]) * T[i]).normalized())
    B = [N[i].cross(T[i]) for i in range(len(C))]
    return ys, C, T, N, B, BW, (yref, w)


def _mesh(c, ys, C, N, B, BW, brk):
    p = PV
    rnd = random.Random(p["seed"])
    lumps = [(0.12, 2, 0.17, 0.0), (0.08, 3, -0.29, 1.0)]
    for _ in range(18):
        lumps.append((0.08 * rnd.uniform(0.4, 1.0), rnd.choice((1, 2, 3, 4, 5)),
                      rnd.choice((-1, 1)) * rnd.randint(4, 26) * 2 * math.pi / 36.0,
                      rnd.uniform(0, 6.283)))
    yref, w = brk

    def per_set(seed):
        r = random.Random(seed)
        out = [(0.12, 2, 1, 0.0), (0.08, 3, -2, 1.0)]
        for _ in range(14):
            out.append((0.08 * r.uniform(0.4, 1.0), r.choice((1, 2, 3, 4, 5)),
                        r.choice((-1, 1)) * r.randint(1, 5), r.uniform(0, 6.283)))
        return out
    lb1, lb2 = per_set(11), per_set(23)
    nt = p["n_theta"]
    l2_a = []
    verts, th_a, y_a, C_a, N_a, B_a, lump_a, pa_a = [], [], [], [], [], [], [], []
    for j, y in enumerate(ys):
        for i in range(nt):
            th = 2 * math.pi * i / nt
            verts.append(C[j] + p["R"] * (math.cos(th) * N[j] + math.sin(th) * B[j]))
            th_a.append(th)
            y_a.append(y)
            C_a.extend(C[j]); N_a.extend(N[j]); B_a.extend(B[j])
            ln = sum(a * math.cos(kt * th + ky * y + ph) for a, kt, ky, ph in lumps)
            bw = BW[j]
            if bw > 0:
                q = (y - yref) * w
                l1 = sum(a * math.cos(kt * th + ky * q + ph) for a, kt, ky, ph in lb1)
                l2 = sum(a * math.cos(kt * th + ky * q + ph) for a, kt, ky, ph in lb2)
                lump_a.append(ln + (l1 - ln) * bw)
                l2_a.append(ln + (l2 - ln) * bw)
            else:
                lump_a.append(ln)
                l2_a.append(ln)
            # patch: smooth 0..1 field that breaks vowel / glow into islands (no on-axis sectors)
            pv = (math.sin(th + 0.23 * y + 0.4) * math.cos(2 * th - 0.17 * y + 1.1)
                  + 0.6 * math.sin(3 * th + 0.41 * y + 2.3) + 0.4 * math.cos(th - 0.53 * y))
            pa_a.append(max(0.0, min(1.0, 0.5 + 0.55 * pv)))
    faces = []
    for j in range(len(ys) - 1):
        r0, r1 = j * nt, (j + 1) * nt
        for i in range(nt):
            i1 = (i + 1) % nt
            faces.append((r0 + i, r0 + i1, r1 + i1, r1 + i))
    me = bpy.data.meshes.new("SongTunnel")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    for name, typ, data in (("th", "FLOAT", th_a), ("yy", "FLOAT", y_a), ("lump", "FLOAT", lump_a), ("lump2", "FLOAT", l2_a), ("patch", "FLOAT", pa_a),
                            ("Cc", "FLOAT_VECTOR", C_a), ("Nn", "FLOAT_VECTOR", N_a),
                            ("Bb", "FLOAT_VECTOR", B_a)):
        at = me.attributes.new(name, typ, "POINT")
        at.data.foreach_set("value" if typ == "FLOAT" else "vector", data)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob = bpy.data.objects.new("SongTunnel", me)
    c.objects.link(ob)
    return ob


def _gn(ob):
    nt = bpy.data.node_groups.new("SongWall", "GeometryNodeTree")
    nt.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    nt.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N_, Lk = nt.nodes.new, nt.links.new
    gi, go = N_("NodeGroupInput"), N_("NodeGroupOutput")
    V = {}
    for k in ("W", "L", "Swell", "A2", "A3", "Phi", "Fo", "Hs", "T", "Sq", "Tw", "Ycam", "Mut", "Boil", "D2"):
        v = N_("ShaderNodeValue")
        v.name = v.label = k
        V[k] = v.outputs[0]
    # 2026-11-14 hypnosis tests (Nick: "too organic"): static look switches, neutral by default
    for k, d in HYP.items():
        v = N_("ShaderNodeValue")
        v.name = v.label = k
        v.outputs[0].default_value = d
        V[k] = v.outputs[0]

    def M(op, a, b=None):
        m = N_("ShaderNodeMath")
        m.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                Lk(x, m.inputs[i])
        return m.outputs[0]

    def attr(name, typ="FLOAT"):
        a = N_("GeometryNodeInputNamedAttribute")
        a.data_type = typ
        a.inputs["Name"].default_value = name
        return a.outputs["Attribute"]

    def VM(op, a, b=None, scale=None):
        m = N_("ShaderNodeVectorMath")
        m.operation = op
        Lk(a, m.inputs[0])
        if b is not None:
            Lk(b, m.inputs[1])
        if scale is not None:
            Lk(scale, m.inputs["Scale"])
        return m.outputs[0]

    th, yy, lump, patch = attr("th"), attr("yy"), attr("lump"), attr("patch")
    # Drop 2 mode (2026-11-14): D2 = 0..1 section envelope; melt = lumps flow back in, ribs melt down
    lumpk = M("ADD", V["LumpK"], M("MULTIPLY", V["D2"], M("SUBTRACT", DROP2["melt_lump"], V["LumpK"])))
    lump = M("MULTIPLY", lump, lumpk)
    wgt = M("ADD", 0.25, M("MULTIPLY", patch, 0.75))
    # fix 2026-11-14: the break's mutation set must be scaled by LumpK too (it re-grew full lumps)
    lump = M("ADD", lump, M("MULTIPLY", V["Mut"], M("SUBTRACT", M("MULTIPLY", attr("lump2"), lumpk), lump)))
    boil = M("MULTIPLY", V["Boil"], M("MULTIPLY",
             M("COSINE", M("SUBTRACT", M("ADD", M("MULTIPLY", th, 3.0), M("MULTIPLY", yy, 1.3)), M("MULTIPLY", V["T"], 2.5))),
             M("COSINE", M("ADD", M("SUBTRACT", M("MULTIPLY", th, 2.0), M("MULTIPLY", yy, 0.8)), M("MULTIPLY", V["T"], 1.7)))))
    Cc, Nn, Bb = attr("Cc", "FLOAT_VECTOR"), attr("Nn", "FLOAT_VECTOR"), attr("Bb", "FLOAT_VECTOR")
    # cull outside the camera window
    rel = M("SUBTRACT", yy, V["Ycam"])
    c1 = N_("FunctionNodeCompare"); c1.data_type = "FLOAT"; c1.operation = "LESS_THAN"
    Lk(rel, c1.inputs[0]); c1.inputs[1].default_value = -PV["behind"]
    c2 = N_("FunctionNodeCompare"); c2.data_type = "FLOAT"; c2.operation = "GREATER_THAN"
    Lk(rel, c2.inputs[0]); c2.inputs[1].default_value = PV["ahead"]
    bo = N_("FunctionNodeBooleanMath"); bo.operation = "OR"
    Lk(c1.outputs[0], bo.inputs[0]); Lk(c2.outputs[0], bo.inputs[1])
    dl = N_("GeometryNodeDeleteGeometry"); dl.domain = "POINT"
    Lk(gi.outputs[0], dl.inputs["Geometry"]); Lk(bo.outputs[0], dl.inputs["Selection"])
    # radius
    vow = M("ADD", M("MULTIPLY", V["A2"], M("COSINE", M("ADD", M("MULTIPLY", th, 2.0), V["Phi"]))),
            M("MULTIPLY", V["A3"], M("COSINE", M("SUBTRACT", M("MULTIPLY", th, 3.0), V["Phi"]))))
    # folds: two helices of different order + pitch, so the throat never forms a regular star
    fold = M("MULTIPLY", V["Fo"], M("ADD",
             M("MULTIPLY", 0.6, M("COSINE", M("ADD", M("MULTIPLY", th, 3.0), M("MULTIPLY", yy, 0.9)))),
             M("MULTIPLY", 0.45, M("COSINE", M("ADD", M("SUBTRACT", M("MULTIPLY", th, 4.0), M("MULTIPLY", yy, 0.55)), 1.0)))))
    shiv = M("MULTIPLY", V["Hs"], M("SINE", M("SUBTRACT", M("ADD", M("MULTIPLY", th, 19.0),
                                                              M("MULTIPLY", yy, 7.3)),
                                               M("MULTIPLY", V["T"], 11.0))))
    vow = M("MULTIPLY", vow, wgt)
    # A: the star folds give way to one oval fold, which the wring rotates along the tube (no star)
    fold = M("ADD", M("MULTIPLY", M("MULTIPLY", fold, wgt), DROP2["fold_old"]),
             M("MULTIPLY", M("MULTIPLY", V["Fo"], M("COSINE", M("MULTIPLY", th, 2.0))), DROP2["fold_oval"]))
    stretch = M("ADD", M("ADD", V["Swell"], vow), fold)
    lit = M("MULTIPLY", stretch, patch)          # glow lives in islands, never whole sectors
    s = M("ADD", M("ADD", 1.0, M("MULTIPLY", V["L"], lump)), M("ADD", M("ADD", stretch, shiv), boil))
    # ribs: regular rings along y; helix: n-start spiral ridges (sharpened cosines)
    def sharp(x, k):                      # |cos|^k with sign: k<1 squarer, k>1 thinner ridges
        return M("MULTIPLY", M("SIGN", x), M("POWER", M("ABSOLUTE", x), k))
    # tilt: each ring's plane leans by RibTilt (m of y per unit cos), lean direction turns slowly along y
    # spacing breathes along the tube: local spacing = RibL / (1 + RibVarA*2pi/RibVarP*cos(..))
    yv = M("ADD", yy, M("MULTIPLY", V["RibVarA"], M("SINE", M("MULTIPLY", yy, M("DIVIDE", 6.2831853, V["RibVarP"])))))
    ryy = M("ADD", yv, M("MULTIPLY", V["RibTilt"], M("COSINE", M("SUBTRACT", th, M("MULTIPLY", yy, V["RibTiltTw"])))))
    ribv = sharp(M("COSINE", M("MULTIPLY", ryy, M("DIVIDE", 6.2831853, V["RibL"]))), V["RibK"])
    rib = M("MULTIPLY", M("MULTIPLY", V["Rib"], M("SUBTRACT", 1.0, M("MULTIPLY", V["D2"], DROP2["melt_rib"]))), sharp(M("COSINE", M("MULTIPLY", ryy, M("DIVIDE", 6.2831853, V["RibL"]))), V["RibK"]))
    hel = M("MULTIPLY", V["Hel"], sharp(M("COSINE", M("SUBTRACT", M("MULTIPLY", th, V["HelN"]),
                                                  M("MULTIPLY", yy, M("DIVIDE", 6.2831853, V["HelP"])))), V["HelK"]))
    s = M("ADD", s, M("ADD", rib, hel))
    rad = M("MULTIPLY", M("MULTIPLY", s, M("MULTIPLY", V["W"], PV["R"])), M("SUBTRACT", 1.0, V["Sq"]))
    # facets: polygon cross-section, twisting along y
    seg = M("DIVIDE", 6.2831853, V["FacN"])
    a_ = M("ADD", th, M("MULTIPLY", yy, V["FacTw"]))
    m_ = M("SUBTRACT", M("FLOORED_MODULO", a_, seg), M("MULTIPLY", seg, 0.5))
    poly = M("DIVIDE", M("COSINE", M("MULTIPLY", seg, 0.5)), M("COSINE", m_))
    rad = M("MULTIPLY", rad, M("ADD", 1.0, M("MULTIPLY", V["Fac"], M("SUBTRACT", poly, 1.0))))
    # melt clearance (2026-11-14, camera passed through the wall): soft floor on the radius during
    # Drop 2 only: rad' = 0.5*(rad + Rmin + sqrt((rad - Rmin)^2 + eps^2)), Rmin = D2 * melt_rmin
    rmin = M("MULTIPLY", V["D2"], DROP2["melt_rmin"])
    dr = M("SUBTRACT", rad, rmin)
    rad = M("MULTIPLY", 0.5, M("ADD", M("ADD", rad, rmin),
                               M("SQRT", M("ADD", M("MULTIPLY", dr, dr), DROP2["melt_eps"] ** 2))))
    phi = M("MULTIPLY", V["Tw"], M("MINIMUM", M("MAXIMUM", rel, -4.0), 30.0))
    ang = M("ADD", th, phi)
    dirv = VM("ADD", VM("SCALE", Nn, scale=M("COSINE", ang)), VM("SCALE", Bb, scale=M("SINE", ang)))
    pos = VM("ADD", Cc, VM("SCALE", dirv, scale=rad))
    sp = N_("GeometryNodeSetPosition")
    Lk(dl.outputs[0], sp.inputs["Geometry"]); Lk(pos, sp.inputs["Position"])
    st = N_("GeometryNodeStoreNamedAttribute")
    st.data_type = "FLOAT"; st.domain = "POINT"
    st.inputs["Name"].default_value = "stretch"
    Lk(sp.outputs[0], st.inputs["Geometry"]); Lk(stretch, st.inputs["Value"])
    st2 = N_("GeometryNodeStoreNamedAttribute")
    st2.data_type = "FLOAT"; st2.domain = "POINT"
    st2.inputs["Name"].default_value = "lit"
    Lk(st.outputs[0], st2.inputs["Geometry"]); Lk(lit, st2.inputs["Value"])
    st3 = N_("GeometryNodeStoreNamedAttribute")
    st3.data_type = "FLOAT"; st3.domain = "POINT"
    st3.inputs["Name"].default_value = "ribv"
    Lk(st2.outputs[0], st3.inputs["Geometry"]); Lk(ribv, st3.inputs["Value"])
    ss = N_("GeometryNodeSetShadeSmooth")
    Lk(st3.outputs[0], ss.inputs["Geometry"])
    cf = N_("FunctionNodeCompare"); cf.data_type = "FLOAT"; cf.operation = "LESS_THAN"
    Lk(V["Fac"], cf.inputs[0]); cf.inputs[1].default_value = 0.5
    Lk(cf.outputs[0], ss.inputs["Shade Smooth"])
    Lk(ss.outputs[0], go.inputs[0])
    md = ob.modifiers.new("SongWall", "NODES")
    md.node_group = nt
    return nt


def _mat():
    m = bpy.data.materials.new("GreySelfLit")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N_, Lk = nt.nodes.new, nt.links.new
    out = N_("ShaderNodeOutputMaterial")
    bs = N_("ShaderNodeBsdfPrincipled")
    g = PV["grey"]
    bs.inputs["Base Color"].default_value = (g, g, g, 1)
    # 2026-11-14 paint pass (psychedelia in grey): albedo = grey * band * inversion, all off by default
    def SV(k):
        v = N_("ShaderNodeValue"); v.name = v.label = k
        v.outputs[0].default_value = PAINT[k]
        return v.outputs[0]

    def SM(op, a, b=None):
        m = N_("ShaderNodeMath"); m.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                Lk(x, m.inputs[i])
        return m.outputs[0]

    def SA(name):
        a = N_("ShaderNodeAttribute"); a.attribute_name = name
        return a.outputs["Fac"]
    P = {k: SV(k) for k in PAINT}
    tm = N_("ShaderNodeValue"); tm.name = tm.label = "Tm"
    d = tm.outputs[0].driver_add("default_value")
    d.driver.expression = "frame/30"
    th_s, yy_s, rv = SA("th"), SA("yy"), SA("ribv")
    # broad helical bands, phase drifts with time; smoothstep-sharpened
    bph = SM("ADD", SM("ADD", SM("MULTIPLY", yy_s, SM("DIVIDE", 6.2831853, P["BandL"])),
                       SM("MULTIPLY", th_s, P["BandN"])), SM("MULTIPLY", tm.outputs[0], P["BandSpd"]))
    bc = SM("COSINE", bph)
    bsh = N_("ShaderNodeMapRange"); bsh.interpolation_type = "SMOOTHSTEP"
    Lk(bc, bsh.inputs["Value"]); Lk(SM("MULTIPLY", P["BandSoft"], -1.0), bsh.inputs["From Min"])
    Lk(P["BandSoft"], bsh.inputs["From Max"]); bsh.inputs["To Min"].default_value = -1.0
    band = SM("ADD", 1.0, SM("MULTIPLY", P["BandA"], bsh.outputs[0]))
    # inversion: ridges painted light in some stretches, dark in others (slow sign along y)
    sg = SM("COSINE", SM("MULTIPLY", yy_s, SM("DIVIDE", 6.2831853, P["InvP"])))
    ssh = N_("ShaderNodeMapRange"); ssh.interpolation_type = "SMOOTHSTEP"
    Lk(sg, ssh.inputs["Value"]); ssh.inputs["From Min"].default_value = -0.35
    ssh.inputs["From Max"].default_value = 0.35; ssh.inputs["To Min"].default_value = -1.0
    inv = SM("ADD", 1.0, SM("MULTIPLY", P["InvA"], SM("MULTIPLY", rv, ssh.outputs[0])))
    alb = SM("MAXIMUM", SM("MULTIPLY", g, SM("MULTIPLY", band, inv)), 0.0)
    cmb = N_("ShaderNodeCombineColor")
    for i in range(3):
        Lk(alb, cmb.inputs[i])
    if CAR["on"]:
        # 2026-11-14 candy-pearl car paint (Nick: classic car red, metallic, pearlescent, flake like a
        # real car). Facing = cherry over gold flake, grazing = violet pearl (Layer Weight); the grey
        # paint scalar (alb / grey) still multiplies it. Flake = Voronoi cells on seam-free rest coords
        # (R cos th, R sin th, y) tilting the base normal; clear coat on top keeps the hard highlights.
        lw = N_("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = CAR["flop_blend"]
        mx = N_("ShaderNodeMix"); mx.data_type = "RGBA"; mx.name = "RedFlop"
        fa = tuple(c * t for c, t in zip(CAR["face"], CAR["flake_tint"]))
        mx.inputs["A"].default_value = (*fa, 1); mx.inputs["B"].default_value = (*CAR["graze"], 1)
        Lk(lw.outputs["Facing"], mx.inputs["Factor"])
        ps = SM("DIVIDE", alb, g)
        bc = N_("ShaderNodeVectorMath"); bc.operation = "SCALE"
        if DEPTH["on"]:
            # 2026-11-14 depth pearl (Nick: "psychedelic hyperrealistic but unrealistic"): the paint's
            # hue depends on distance from the viewer, which no paint can do. Cyclic ramp indexed by
            # fract(Facing*face_k + view_distance/period): near walls violet, throat copper/gold; as you
            # travel the colour rolls toward you at travel speed.
            cdp = N_("ShaderNodeCameraData")
            hi = SM("FRACT", SM("ADD", SM("MULTIPLY", lw.outputs["Facing"], DEPTH["face_k"]),
                                SM("DIVIDE", cdp.outputs["View Distance"], DEPTH["period_m"])))
            rp = N_("ShaderNodeValToRGB"); rp.name = "PearlRamp"; cr = rp.color_ramp
            cr.interpolation = "EASE"
            stops = [(0.0, fa)] + [(pp, cc) for pp, cc in DEPTH["stops"]] + [(1.0, fa)]
            cr.elements[0].position = 0.0; cr.elements[0].color = (*stops[0][1], 1)
            cr.elements[1].position = 1.0; cr.elements[1].color = (*stops[-1][1], 1)
            for pp, cc in stops[1:-1]:
                e_ = cr.elements.new(pp); e_.color = (*cc, 1)
            Lk(hi, rp.inputs["Fac"])
            Lk(rp.outputs["Color"], bc.inputs[0])
        else:
            Lk(mx.outputs["Result"], bc.inputs[0])
        Lk(ps, bc.inputs["Scale"])
        Lk(bc.outputs[0], bs.inputs["Base Color"])
        cx = N_("ShaderNodeCombineXYZ")
        Lk(SM("MULTIPLY", SM("COSINE", th_s), PV["R"]), cx.inputs[0])
        Lk(SM("MULTIPLY", SM("SINE", th_s), PV["R"]), cx.inputs[1])
        Lk(yy_s, cx.inputs[2])
        vo = N_("ShaderNodeTexVoronoi"); vo.name = "FlakeVor"; vo.voronoi_dimensions = "3D"
        vo.inputs["Scale"].default_value = CAR["flake_scale"]
        Lk(cx.outputs[0], vo.inputs["Vector"])
        vs = N_("ShaderNodeVectorMath"); vs.operation = "SUBTRACT"
        Lk(vo.outputs["Color"], vs.inputs[0]); vs.inputs[1].default_value = (0.5, 0.5, 0.5)
        vk = N_("ShaderNodeVectorMath"); vk.operation = "SCALE"; vk.name = "FlakeK"
        Lk(vs.outputs[0], vk.inputs[0]); vk.inputs["Scale"].default_value = CAR["flake_k"]
        # hats = detail (2026-11-14): a few random flakes flash warm white on each hat
        sep = N_("ShaderNodeSeparateColor"); Lk(vo.outputs["Color"], sep.inputs[0])
        gm = N_("ShaderNodeMath"); gm.operation = "GREATER_THAN"
        Lk(sep.outputs[0], gm.inputs[0]); gm.inputs[1].default_value = 1.0 - AMOD["glint_frac"]
        gv = N_("ShaderNodeValue"); gv.name = gv.label = "Glint"
        cdg = N_("ShaderNodeCameraData")         # near walls only: glints fade out by glint_far m
        gnear = N_("ShaderNodeMapRange"); gnear.interpolation_type = "SMOOTHSTEP"
        Lk(cdg.outputs["View Distance"], gnear.inputs["Value"])
        gnear.inputs["From Min"].default_value, gnear.inputs["From Max"].default_value = 1.0, AMOD["glint_far"]
        gnear.inputs["To Min"].default_value, gnear.inputs["To Max"].default_value = 1.0, 0.0
        gs = SM("MULTIPLY", SM("MULTIPLY", SM("MULTIPLY", gm.outputs[0], gv.outputs[0]), AMOD["glint_k"]), gnear.outputs[0])
        gem = N_("ShaderNodeEmission"); gem.inputs["Color"].default_value = (1.0, 0.85, 0.6, 1)
        Lk(gs, gem.inputs["Strength"])
        SUN["_glint"] = gem
        geo = N_("ShaderNodeNewGeometry")
        va = N_("ShaderNodeVectorMath"); va.operation = "ADD"
        Lk(geo.outputs["Normal"], va.inputs[0]); Lk(vk.outputs[0], va.inputs[1])
        vn = N_("ShaderNodeVectorMath"); vn.operation = "NORMALIZE"
        Lk(va.outputs[0], vn.inputs[0]); Lk(vn.outputs[0], bs.inputs["Normal"])
        bs.inputs["Metallic"].default_value = CAR["metallic"]
        bs.inputs["Roughness"].default_value = CAR["rough"]
        bs.inputs["Specular Tint"].default_value = (*CAR["spec_tint"], 1)
        bs.inputs["Coat Weight"].default_value = 1.0
        bs.inputs["Coat Roughness"].default_value = CAR["coat_rough"]
        bs.inputs["Thin Film Thickness"].default_value = CAR["film_nm"]
        bs.inputs["Thin Film IOR"].default_value = 1.5
    if SUN["on"]:
        # 2026-11-14 "paint job sitting in the sun": the clear coat reflects a real sunny lot (HDRI) that
        # the camera never sees and that lights nothing. Emission = sky(reflection dir) * Fresnel(1.5) *
        # coat_k, faded out with view distance so the throat stays black (no sky reaches that deep).
        out_ = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        tc = N_("ShaderNodeTexCoord"); mp = N_("ShaderNodeMapping"); mp.name = "CoatSkyRot"
        mp.inputs["Rotation"].default_value[2] = math.radians(SUN["sky_rot_deg"])
        Lk(tc.outputs["Reflection"], mp.inputs["Vector"])
        env = N_("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(SUN["hdri"], check_existing=True)
        Lk(mp.outputs[0], env.inputs["Vector"])
        fr = N_("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.5
        cd = N_("ShaderNodeCameraData")
        fd = N_("ShaderNodeMapRange"); fd.name = "CoatSkyFade"; fd.interpolation_type = "SMOOTHSTEP"
        Lk(cd.outputs["View Distance"], fd.inputs["Value"])
        fd.inputs["From Min"].default_value, fd.inputs["From Max"].default_value = SUN["fade_m"]
        fd.inputs["To Min"].default_value, fd.inputs["To Max"].default_value = 1.0, 0.0
        sf = N_("ShaderNodeValue"); sf.name = sf.label = "SunFade"; sf.outputs[0].default_value = 1.0
        ck = SM("MULTIPLY", SM("MULTIPLY", SM("MULTIPLY", fr.outputs[0], fd.outputs[0]), SUN["coat_k"]), sf.outputs[0])
        em2 = N_("ShaderNodeEmission")
        Lk(env.outputs["Color"], em2.inputs["Color"]); Lk(ck, em2.inputs["Strength"])
        SUN["_coat"] = (em2, out_)
    else:
        Lk(cmb.outputs[0], bs.inputs["Base Color"])
        bs.inputs["Roughness"].default_value = PV["rough"]
    at = N_("ShaderNodeAttribute"); at.attribute_name = "lit"
    gl = N_("ShaderNodeValue"); gl.name = gl.label = "Glow"
    sn = N_("ShaderNodeValue"); sn.name = sn.label = "Snare"
    pos = N_("ShaderNodeMapRange"); pos.interpolation_type = "SMOOTHSTEP"
    Lk(at.outputs["Fac"], pos.inputs["Value"])
    pos.inputs["From Min"].default_value = 0.02; pos.inputs["From Max"].default_value = 0.16
    k = N_("ShaderNodeMath"); k.operation = "ADD"
    Lk(gl.outputs[0], k.inputs[0]); Lk(sn.outputs[0], k.inputs[1])
    st = N_("ShaderNodeMath"); st.operation = "MULTIPLY"
    Lk(pos.outputs[0], st.inputs[0]); Lk(k.outputs[0], st.inputs[1])
    em = N_("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.96, 0.92, 1)
    Lk(st.outputs[0], em.inputs["Strength"])
    add = N_("ShaderNodeAddShader")
    Lk(bs.outputs[0], add.inputs[0]); Lk(em.outputs[0], add.inputs[1])
    if SUN["on"] and CAR["on"]:
        em2, _ = SUN.pop("_coat")
        add2 = N_("ShaderNodeAddShader")
        Lk(add.outputs[0], add2.inputs[0]); Lk(em2.outputs[0], add2.inputs[1])
        gem = SUN.pop("_glint", None)
        if gem is not None:
            add3 = N_("ShaderNodeAddShader")
            Lk(add2.outputs[0], add3.inputs[0]); Lk(gem.outputs[0], add3.inputs[1])
            Lk(add3.outputs[0], out.inputs["Surface"])
        else:
            Lk(add2.outputs[0], out.inputs["Surface"])
    else:
        Lk(add.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ keys
def _bulk(owner, path, vals, index=0):
    """One fcurve with a key per frame, written in one go."""
    owner.keyframe_insert(path, index=index, frame=1) if index >= 0 else owner.keyframe_insert(path, frame=1)
    ad = owner.animation_data
    fc = None
    for l in ad.action.layers:
        for stp in l.strips:
            fc = stp.channelbag(ad.action_slot).fcurves.find(path, index=max(0, index))
            if fc:
                break
    kp = fc.keyframe_points
    kp.clear()
    kp.add(len(vals))
    co = []
    for f, v in enumerate(vals):
        co += [f + 1, v]
    kp.foreach_set("co", co)
    kp.foreach_set("interpolation", [1] * len(vals))     # LINEAR
    fc.update()


def build_song(seconds=SONG_S):
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = FPS
    sc.view_settings.view_transform = "AgX"
    c = _col()
    for ng in list(bpy.data.node_groups):
        if ng.name.startswith("SongWall"):
            bpy.data.node_groups.remove(ng)
    w = bpy.data.worlds.get("ChamberWorld") or bpy.data.worlds.new("ChamberWorld")
    w.use_nodes = True
    next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = w
    nf = int(round(seconds * FPS))
    sig = signals(nf)
    # camera travel
    ycam, y = [], 0.5
    for f in range(nf):
        ycam.append(y)
        y += sig["speed"][f] / FPS
    ys, C, T, N, B, BW, brk = _spine(ycam, sig["wander"], sig["C"])
    ob = _mesh(c, ys, C, N, B, BW, brk)
    print("break line period", round(2 * math.pi / brk[1], 2), "m")
    gn = _gn(ob)
    mat = _mat()
    ob.data.materials.append(mat)
    # camera: on the spine, looking ahead along it, rolling one way
    dy = PV["dy"]

    def at(yq):
        u = (yq - ys[0]) / dy
        i = max(0, min(len(ys) - 2, int(u)))
        fr = u - i
        return C[i].lerp(C[i + 1], fr), N[i].lerp(N[i + 1], fr).normalized()

    cd = bpy.data.cameras.new("Cam")
    cd.lens = PV["lens"]
    cd.clip_start = 0.01
    cd.clip_end = 120
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.rotation_mode = "QUATERNION"
    sc.camera = cam
    lights = []
    for name, e, loc, spec in (("Fill", PV["fill"], (0.0, 0.3, 0.6), 1.0 if CAR["on"] else 0.3),
                               ("FillAhead", PV["fill_ahead"], (0.0, 0.0, -PV["ahead_d"]), 0.0)):
        ld = bpy.data.lights.new(name, "POINT")
        ld.color = (1.0, 0.97, 0.94)
        ld.specular_factor = spec if (name == "Fill" or not CAR["on"]) else 1.0   # car paint needs its highlights
        ld.use_shadow = name == "Fill"
        lo = bpy.data.objects.new(name, ld)
        c.objects.link(lo)
        lo.parent = cam
        lo.location = loc
        lights.append((ld, e))
    if SUN["on"]:
        # sun: specular only (walls stay headlamp-lit, void stays black), no shadow so it reaches inside;
        # aimed where the sun sits in the rotated coat reflection, so lamp and sky agree
        sd = bpy.data.lights.new("Sun", "SUN")
        sd.energy = SUN["energy"]; sd.angle = math.radians(SUN["angle_deg"]); sd.color = SUN["color"]
        sd.diffuse_factor = 0.0; sd.specular_factor = 1.0; sd.volume_factor = 0.0; sd.use_shadow = False
        so = bpy.data.objects.new("Sun", sd); c.objects.link(so)
        e_, a_ = math.radians(SUN["sun_elev_deg"]), math.radians(SUN["sun_az_deg"])
        d_ = Vector((math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_), math.sin(e_)))
        so.rotation_mode = "QUATERNION"; so.rotation_quaternion = (-d_).to_track_quat("-Z", "Y")
        sc.view_settings.exposure = SUN["exposure"]
        old = bpy.data.node_groups.get("TippinComp")
        if old:
            bpy.data.node_groups.remove(old)
        cg = bpy.data.node_groups.new("TippinComp", "CompositorNodeTree")
        cg.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = cg.nodes.new("CompositorNodeRLayers"); gl = cg.nodes.new("CompositorNodeGlare")
        go = cg.nodes.new("NodeGroupOutput")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Threshold"].default_value = SUN["glare_thresh"]
        gl.inputs["Strength"].default_value = SUN["glare_strength"]
        gl.inputs["Size"].default_value = SUN["glare_size"]
        cg.links.new(rl.outputs["Image"], gl.inputs["Image"]); cg.links.new(gl.outputs["Image"], go.inputs[0])
        sc.compositing_node_group = cg
    locs = [[], [], []]
    quats = [[], [], [], []]
    roll, qprev = 0.0, None
    for f in range(nf):
        P_, Nup = at(ycam[f])
        A_, Na = at(ycam[f] + PV["look"])
        if PV["off"]:
            ang = math.radians(PV["off_phase"] + PV["off_rate"] * f / FPS)
            tg = (A_ - P_).normalized()
            Bp = Nup.cross(tg)
            Ba = Na.cross(tg)
            off = PV["off"] + sig["D2"][f] * (DROP2["melt_off"] - PV["off"])   # back toward the axis in the melt
            P_ = P_ + off * (math.cos(ang) * Nup + math.sin(ang) * Bp)
            A_ = A_ + off * (1 - PV["off_aim"]) * (math.cos(ang) * Na + math.sin(ang) * Ba)
        fwd = (A_ - P_).normalized()
        yc = (Nup - Nup.dot(fwd) * fwd).normalized()
        zc = -fwd
        q = Matrix((yc.cross(zc), yc, zc)).transposed().to_quaternion()
        q = q @ Quaternion((0, 0, 1), roll)
        roll += math.radians(sig["roll"][f]) / FPS
        if qprev is not None and q.dot(qprev) < 0:
            q.negate()
        qprev = q
        for i in range(3):
            locs[i].append(P_[i])
        for i in range(4):
            quats[i].append(q[i])
    for i in range(3):
        _bulk(cam, "location", locs[i], i)
    for i in range(4):
        _bulk(cam, "rotation_quaternion", quats[i], i)
    for ld, e in lights:
        _bulk(ld, "energy", [e * v for v in sig["lamp"]], -1)
    if SUN["on"]:
        # fix 2026-11-14: sun + coat sky follow the headlamp fade (the end went to 41 mean, not black);
        # normalised so every section at lamp >= 0.85 keeps the full sun
        fade = [min(1.0, v / 0.85) for v in sig["lamp"]]
        flare = [1.0 + AMOD["flare"] * x for x in sig["Flare"]] if AMOD["on"] else [1.0] * nf
        _bulk(bpy.data.lights["Sun"], "energy", [SUN["energy"] * v * fl for v, fl in zip(fade, flare)], -1)
        if AMOD["on"]:
            # snare = light: each snare steps the sun round the coil; the reflected sky turns with it
            so_ = bpy.data.objects["Sun"]
            e_ = math.radians(SUN["sun_elev_deg"])
            qs = [[], [], [], []]
            for f in range(nf):
                a_ = math.radians(SUN["sun_az_deg"] + sig["SunAz"][f])
                d_ = Vector((math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_), math.sin(e_)))
                q_ = (-d_).to_track_quat("-Z", "Y")
                if f and sum(a * b for a, b in zip(q_, [qs[i][-1] for i in range(4)])) < 0:
                    q_.negate()
                for i in range(4):
                    qs[i].append(q_[i])
            for i in range(4):
                _bulk(so_, "rotation_quaternion", qs[i], i)
            _bulk(mat.node_tree, 'nodes["CoatSkyRot"].inputs[2].default_value',
                  [math.radians(SUN["sky_rot_deg"] - v) for v in sig["SunAz"]], 2)
            _bulk(mat.node_tree, 'nodes["Glint"].outputs[0].default_value', sig["Glint"], -1)
        _bulk(mat.node_tree, 'nodes["SunFade"].outputs[0].default_value', fade, -1)
    _bulk(cd, "lens", sig["lens"], -1)
    for k in ("W", "L", "Swell", "A2", "A3", "Phi", "Fo", "Hs", "T", "Sq", "Tw", "Mut", "Boil", "D2"):
        _bulk(gn, f'nodes["{k}"].outputs[0].default_value', sig[k], -1)
    _bulk(gn, 'nodes["Ycam"].outputs[0].default_value', ycam, -1)
    for k in ("Glow", "Snare"):
        _bulk(mat.node_tree, f'nodes["{k}"].outputs[0].default_value', sig[k], -1)
    sc.frame_start, sc.frame_end = 1, nf
    print("song preview built:", nf, "frames, travel", round(ycam[-1], 1), "m, rings", len(ys),
          "verts", len(ys) * PV["n_theta"])
