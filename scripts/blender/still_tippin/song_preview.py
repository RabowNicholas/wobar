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
BREAK = (65, 81, 4)          # bars, line length in bars
WRING = [(81, 89, 0.42, "snap"), (89, 97, 0.58, "unwind"), (105, 113, -0.75, "snap")]   # v3: harder (Nick: drop 2 needs energy)

PV = dict(R=1.6, n_theta=144, dy=0.08, ahead=45.0, behind=4.0, look=4.5, lens=20,
          kpush=1.6, fill=45.0, fill_ahead=220.0, ahead_d=5.5, glow_k=0.0, snare_k=0.0,      # stretch light OFF for now (Nick)
          grey=0.30, rough=0.38, seed=7,
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
                           "C", "lens", "Boil", "Mut")}
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
                ks = [k for k in kicks if _t(b0) <= k < _t(b1)]
                done = sum(1 for k in ks if k <= t)
                tgt = mx * done / max(1, len(ks))
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
        out["Sq"].append(0.26 * wr * sub)
        out["Tw"].append(tw[0])
        out["Hs"].append(0.007 * P["shiver"] * he)
        out["T"].append(t)
        out["Glow"].append(PV["glow_k"] * P["glow"] * (0.4 + 0.6 * sub))
        out["Snare"].append(PV["snare_k"] * se * (1.0 if P["snare_on"] > 0.5 else 0.0))
        out["lamp"].append(P["lamp"])
        out["speed"].append(P["speed"] + 1.4 * ch)
        kickpart.append(PV["kpush"] * P["kick"] * ke)
        lampflash.append(0.9 * se * P["snare_on"] * min(1.0, P["kick"]))   # snare = light, via the headlamp
        lenspunch.append(-2.5 * ke * max(0.0, P["kick"] - 0.5))           # kick punches the lens in the drops
        out["roll"].append(P["roll"] + ch * (45 + 30 * math.sin(t * 2.3) * math.sin(t * 0.7)))
        out["wander"].append(P["wander"])
    # v3 (Nick: "section transitions end up a little choppy"): smooth the section / chaos
    # driven channels so nothing steps; kicks are added back after so they keep their punch.
    for k, tau in (("speed", 0.25), ("roll", 0.35), ("W", 0.2), ("L", 0.3), ("lens", 0.3),
                   ("Boil", 0.2), ("lamp", 0.3), ("Glow", 0.2), ("wander", 0.5), ("C", 0.2)):
        out[k] = _smooth_series(out[k], tau)
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
    for k in ("W", "L", "Swell", "A2", "A3", "Phi", "Fo", "Hs", "T", "Sq", "Tw", "Ycam", "Mut", "Boil"):
        v = N_("ShaderNodeValue")
        v.name = v.label = k
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
    wgt = M("ADD", 0.25, M("MULTIPLY", patch, 0.75))
    lump = M("ADD", lump, M("MULTIPLY", V["Mut"], M("SUBTRACT", attr("lump2"), lump)))
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
    fold = M("MULTIPLY", fold, wgt)
    stretch = M("ADD", M("ADD", V["Swell"], vow), fold)
    lit = M("MULTIPLY", stretch, patch)          # glow lives in islands, never whole sectors
    s = M("ADD", M("ADD", 1.0, M("MULTIPLY", V["L"], lump)), M("ADD", M("ADD", stretch, shiv), boil))
    rad = M("MULTIPLY", M("MULTIPLY", s, M("MULTIPLY", V["W"], PV["R"])), M("SUBTRACT", 1.0, V["Sq"]))
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
    Lk(st2.outputs[0], go.inputs[0])
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
    for name, e, loc, spec in (("Fill", PV["fill"], (0.0, 0.3, 0.6), 0.3),
                               ("FillAhead", PV["fill_ahead"], (0.0, 0.0, -PV["ahead_d"]), 0.0)):
        ld = bpy.data.lights.new(name, "POINT")
        ld.color = (1.0, 0.97, 0.94)
        ld.specular_factor = spec
        ld.use_shadow = name == "Fill"
        lo = bpy.data.objects.new(name, ld)
        c.objects.link(lo)
        lo.parent = cam
        lo.location = loc
        lights.append((ld, e))
    locs = [[], [], []]
    quats = [[], [], [], []]
    roll, qprev = 0.0, None
    for f in range(nf):
        P_, Nup = at(ycam[f])
        A_, _ = at(ycam[f] + PV["look"])
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
    _bulk(cd, "lens", sig["lens"], -1)
    for k in ("W", "L", "Swell", "A2", "A3", "Phi", "Fo", "Hs", "T", "Sq", "Tw", "Mut", "Boil"):
        _bulk(gn, f'nodes["{k}"].outputs[0].default_value', sig[k], -1)
    _bulk(gn, 'nodes["Ycam"].outputs[0].default_value', ycam, -1)
    for k in ("Glow", "Snare"):
        _bulk(mat.node_tree, f'nodes["{k}"].outputs[0].default_value', sig[k], -1)
    sc.frame_start, sc.frame_end = 1, nf
    print("song preview built:", nf, "frames, travel", round(ycam[-1], 1), "m, rings", len(ys),
          "verts", len(ys) * PV["n_theta"])
