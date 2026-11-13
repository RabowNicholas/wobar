"""STILL TIPPIN — the wandering tunnel as a seamless VJ loop, grey clay (2026-11-13).
Run after exec(chamber.py) (uses _col, _link, _hex).

Nick on wander v2: roll "one direction continuously", "kill the light", "switch to grey while we
nail this. i want to get this to a good vj loop and then we can start adding in the audio
modulation".

Seamless loop = everything the camera sees repeats with period P along the spine:
  spine      x(y), z(y) are integer harmonics of 2π/P (plus a linear descent: a translation,
             so the view still repeats).
  frame      rotation-minimising frame along the spine, then the holonomy over one period is
             spread linearly along it, so N(y + P) = N(y) exactly. The wall is built in that
             frame (no Curve modifier — its frame does not close).
  wall       radius = integer θ harmonics × integer multiples of 2π/P (a periodic "noise").
             Grey material has no textures (a texture in object space would not repeat).
  camera     moves exactly one period's arc length per loop; rolls exactly roll_turns × 360°.
             Keys run to frame N+1, which must equal frame 1 (checked by render diff).
No core light (Nick: kill it). Lights ride with the camera.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix

VJ = dict(
    loop_s=20.0, fps=30,
    P=36.0,                                   # spine period (m along the main axis)
    wx=((3.2, 1, 0.0), (0.9, 2, 1.3), (0.25, 3, 2.1)),   # (amplitude m, harmonic, phase)
    wz=((2.0, 1, 1.0), (0.6, 2, 0.4)),
    descent=0.12,
    R=1.6, n_theta=192, dy=0.06,
    wall_terms=18, wall_amp=0.08, seed=7,
    lobe2=0.12, lobe3=0.08,
    look=4.5, lens=20,
    roll_turns=1,                             # full turns per loop, one direction
    fill=45.0, fill_ahead=220.0, ahead_d=5.5,
    grey=0.30, rough=0.38,
)


def _spine(y, p):
    w = 2 * math.pi / p["P"]
    x = sum(a * math.sin(k * w * y + ph) for a, k, ph in p["wx"])
    z = sum(a * math.sin(k * w * y + ph) for a, k, ph in p["wz"]) - p["descent"] * y
    return Vector((x, y, z))


def _frames(ys, p):
    C = [_spine(y, p) for y in ys]
    T = []
    for i in range(len(C)):
        a, b = C[max(0, i - 1)], C[min(len(C) - 1, i + 1)]
        T.append((b - a).normalized())
    N = [Vector((1, 0, 0))]
    N[0] = (N[0] - N[0].dot(T[0]) * T[0]).normalized()
    for i in range(1, len(C)):
        n = N[-1] - N[-1].dot(T[i]) * T[i]           # parallel transport (projection)
        N.append(n.normalized())
    # holonomy over one period, measured from y=0 to y=P
    dy = ys[1] - ys[0]
    i0 = round((0.0 - ys[0]) / dy)
    i1 = round((p["P"] - ys[0]) / dy)
    n0, n1, t = N[i0], N[i1], T[i1]
    alpha = math.atan2(t.dot(n0.cross(n1)), n0.dot(n1))
    for i, y in enumerate(ys):
        N[i] = Quaternion(T[i], -alpha * y / p["P"]) @ N[i]
    B = [N[i].cross(T[i]) for i in range(len(C))]   # N×B = -T: matches the inward winding
    return C, T, N, B, alpha


def _wall_terms(p):
    rnd = random.Random(p["seed"])
    terms = [(p["lobe2"], 2, 3, 0.0), (p["lobe3"], 3, -5, 1.0)]   # lobes that twist along the tube
    for _ in range(p["wall_terms"]):
        kt = rnd.choice((1, 2, 3, 4, 5))         # high θ orders made star creases
        ky = rnd.choice((-1, 1)) * rnd.randint(4, 26)              # 1.4 – 9 m lumps
        terms.append((p["wall_amp"] * rnd.uniform(0.4, 1.0), kt, ky, rnd.uniform(0, 6.283)))
    return terms


def _wall(c, ys, C, N, B, p):
    w = 2 * math.pi / p["P"]
    terms = _wall_terms(p)
    me = bpy.data.meshes.new("Tunnel")
    bm = bmesh.new()
    nt = p["n_theta"]
    rows = []
    for j, y in enumerate(ys):
        row = []
        for i in range(nt):
            th = 2 * math.pi * i / nt
            s = 1.0 + sum(a * math.cos(kt * th + ky * w * y + ph) for a, kt, ky, ph in terms)
            r = p["R"] * s
            row.append(bm.verts.new(C[j] + r * (math.cos(th) * N[j] + math.sin(th) * B[j])))
        rows.append(row)
    for j in range(len(ys) - 1):
        for i in range(nt):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nt], rows[j + 1][(i + 1) % nt], rows[j + 1][i]))
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    ob = bpy.data.objects.new("Tunnel", me)
    c.objects.link(ob)
    m = bpy.data.materials.new("GreyClay")
    m.use_nodes = True
    bs = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    g = p["grey"]
    bs.inputs["Base Color"].default_value = (g, g, g, 1)
    bs.inputs["Roughness"].default_value = p["rough"]
    me.materials.append(m)
    return ob


def build_vj(**over):
    p = dict(VJ, **over)
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.fps = p["fps"]
    sc.view_settings.view_transform = "AgX"
    c = _col()
    w = bpy.data.worlds.get("ChamberWorld") or bpy.data.worlds.new("ChamberWorld")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    sc.world = w

    nf = int(p["loop_s"] * p["fps"])
    y_end = p["P"] + 34.0
    ys = [-3.0 + i * p["dy"] for i in range(int((y_end + 3.0) / p["dy"]) + 1)]
    C, T, N, B, alpha = _frames(ys, p)
    _wall(c, ys, C, N, B, p)
    cum = [0.0]
    for i in range(len(C) - 1):
        cum.append(cum[-1] + (C[i + 1] - C[i]).length)
    i0 = round(3.0 / p["dy"])
    i1 = round((p["P"] + 3.0) / p["dy"])
    Lp = cum[i1] - cum[i0]

    def at(s):
        lo, hi = 0, len(cum) - 1
        while hi - lo > 1:
            m_ = (lo + hi) // 2
            lo, hi = (m_, hi) if cum[m_] <= s else (lo, m_)
        u = (s - cum[lo]) / max(1e-9, cum[hi] - cum[lo])
        return C[lo].lerp(C[hi], u), N[lo].lerp(N[hi], u).normalized()

    cd = bpy.data.cameras.new("Cam")
    cd.lens = p["lens"]
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.rotation_mode = "QUATERNION"
    sc.camera = cam
    for name, e, loc, spec in (("Fill", p["fill"], (0.0, 0.3, 0.6), 0.3),
                               ("FillAhead", p["fill_ahead"], (0.0, 0.0, -p["ahead_d"]), 0.0)):
        ld = bpy.data.lights.new(name, "POINT")
        ld.energy = e
        ld.color = (1.0, 0.97, 0.94)
        ld.specular_factor = spec
        ld.use_shadow = name == "Fill"
        lo = bpy.data.objects.new(name, ld)
        c.objects.link(lo)
        lo.parent = cam
        lo.location = loc

    qprev = None
    s0 = cum[i0]
    for f in range(nf + 1):                       # frame nf+1 must equal frame 1
        u = f / nf
        s = s0 + Lp * u
        P_, Nup = at(s)
        A_, _ = at(s + p["look"])
        fwd = (A_ - P_).normalized()
        yc = (Nup - Nup.dot(fwd) * fwd).normalized()
        zc = -fwd
        xc = yc.cross(zc)
        q = Matrix((xc, yc, zc)).transposed().to_quaternion()
        q = q @ Quaternion((0, 0, 1), 2 * math.pi * p["roll_turns"] * u)
        if qprev is not None and q.dot(qprev) < 0:
            q.negate()
        qprev = q
        cam.location = P_
        cam.rotation_quaternion = q
        cam.keyframe_insert("location", frame=f + 1)
        cam.keyframe_insert("rotation_quaternion", frame=f + 1)
    sc.frame_start, sc.frame_end = 1, nf
    print("vj loop built:", nf, "frames, period arc", round(Lp, 2), "m, holonomy fixed",
          round(math.degrees(alpha), 1), "deg, verts", len(ys) * p["n_theta"])
