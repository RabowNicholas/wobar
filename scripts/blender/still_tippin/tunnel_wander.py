"""STILL TIPPIN — the membrane tunnel, wandering camera (2026-11-13).
Run after exec(chamber.py), exec(chamber_motion.py), exec(tunnel.py).

Nick: "keep the tunnel look that we have. i like the wandering and the camera movement of his
[mindsplitter_ RAVERS coil] and i want to emulate that with ours."

What the reference camera does, and how it maps here:
  wandering spine   several incommensurate sines per axis instead of one per axis, so the bends
                    never repeat; curvature radius kept > ~4x tube radius (no wall smear).
  look along it     the camera looks a short way ahead ON the path (not at the light), so the
                    tunnel curves away out of frame and the vanishing point drifts. The light
                    rides further down: it slides off-centre in bends and comes back (L10 kept).
  glide + bank      slow constant travel; the camera banks into each turn and rolls slowly,
                    which is what makes the coil look like it turns around you.
  colour slowed     drift/crawl cut hard so the motion reads from travel, not palette cycling.
"""
import bpy, math
from mathutils import Vector, Quaternion

WAN = dict(
    length=70.0,
    # (amplitude m, period m, phase) per term
    # v2 (Nick: "too gentle"): amplitude x2, period x1.35 -> bigger swings, same bend radius
    wx=((5.2, 10.8, 0.0), (1.4, 5.7, 1.3), (0.4, 3.5, 2.1)),
    wz=((3.0, 13.5, 1.0), (1.0, 6.75, 0.4), (0.3, 4.0, 2.7)),
    descent=0.12,
    speed=1.8,          # m/s (v2: "too slow", was 0.9)
    start=2.0,
    look=4.5,           # camera aims this far ahead along the path
    lead=8.0,           # light this far ahead
    bank=2.0,           # roll into turns (rad per unit lateral turn per metre)
    roll_rate=18.0,      # deg/s continuous roll
    roll_wave=30.0,     # deg slow roll sway
    fill_energy=45.0,   # v2: "too much black" - camera fill up, plus a fill ahead
    fwd_fill=220.0,      # shadowless point light riding ahead of the camera
    fwd_dist=5.5,     # far enough that the near walls do not blow out
    preroll=1.5,        # s of filter history dropped (no black first second)
)


def _wpath(c, p):
    cu = bpy.data.curves.new("TunnelPath", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    ys = [i * 0.25 for i in range(int(p["length"] / 0.25) + 1)]
    sp.points.add(len(ys) - 1)

    def f(terms, y):
        # ramp in over the first 4 m so the tube starts straight behind the camera
        r = min(1.0, y / 4.0)
        return r * sum(a * (math.sin(y / per + ph) - math.sin(ph)) for a, per, ph in terms)

    pts = []
    for i, y in enumerate(ys):
        v = Vector((f(p["wx"], y), y, f(p["wz"], y) - p["descent"] * y))
        sp.points[i].co = (*v, 1)
        pts.append(v)
    ob = bpy.data.objects.new("TunnelPath", cu)
    c.objects.link(ob)
    cum = [0.0]
    for i in range(len(pts) - 1):
        cum.append(cum[-1] + (pts[i + 1] - pts[i]).length)
    # min curvature radius (sanity: tube radius 1.6, breath up to ~2.3)
    rmin = 1e9
    for i in range(4, len(pts) - 4, 2):
        a, b, d = pts[i - 4], pts[i], pts[i + 4]
        t1, t2 = (b - a).normalized(), (d - b).normalized()
        ang = t1.angle(t2, 0.0)
        if ang > 1e-4:
            rmin = min(rmin, ((d - a).length / 2) / ang)
    return ob, pts, cum, rmin


def _at(pts, cum, s):
    """point + unit tangent at arc length s."""
    s = max(0.0, min(cum[-1] - 1e-6, s))
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if cum[m] <= s:
            lo = m
        else:
            hi = m
    u = (s - cum[lo]) / max(1e-9, cum[hi] - cum[lo])
    return pts[lo].lerp(pts[hi], u), (pts[hi] - pts[lo]).normalized()


def build_wander(seconds=8.0, fps=30, **over):
    p = dict(WAN, **over)
    sc = bpy.context.scene
    sc.render.fps = fps
    BRE.update(crawl=0.05, drift=0.008, stiff=90.0, damp=6.0, open_amp=0.45, glow=2.5)
    build("membrane", length=p["length"] - 2.0, n_y=1000, n_theta=192, pinch=0.0, flare=0.0,
          lobe2=0.12, lobe3=0.08, twist=6.0, noise=0.08)
    c = bpy.data.collections["STILL_TIPPIN"]
    for o in list(c.objects):
        if o.name.startswith("Out") or o.name in ("Cam", "Fill", "FillAhead", "Core", "CoreGlow"):
            bpy.data.objects.remove(o, do_unlink=True)
    ob = bpy.data.objects["Chamber"]
    gn = _gn(ob)
    ob.data.materials.clear()
    mat = _band_mat(BRE)
    ob.data.materials.append(mat)
    path, pts, cum, rmin = _wpath(c, p)
    cm = ob.modifiers.new("Wind", "CURVE")
    cm.object = path
    cm.deform_axis = "POS_Y"

    nf = int(seconds * fps)
    sc.frame_start, sc.frame_end = 1, nf

    # light: emissive core + point lamp, keyed straight onto path positions
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08)
    core = bpy.context.active_object
    core.name = "CoreGlow"
    _link(c, core)
    cmat = bpy.data.materials.new("CoreGlow")
    cmat.use_nodes = True
    cn = cmat.node_tree
    cn.nodes.clear()
    o_ = cn.nodes.new("ShaderNodeOutputMaterial")
    e_ = cn.nodes.new("ShaderNodeEmission")
    e_.inputs["Color"].default_value = (1.0, 0.95, 0.9, 1)
    e_.inputs["Strength"].default_value = 40.0
    cn.links.new(e_.outputs[0], o_.inputs[0])
    core.data.materials.append(cmat)
    ld = bpy.data.lights.new("Core", "POINT")
    ld.energy = 1800
    ld.color = (1.0, 0.93, 0.86)
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new("Core", ld)
    c.objects.link(lo)
    lo.parent = core

    cd = bpy.data.cameras.new("Cam")
    cd.lens = 20
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.rotation_mode = "QUATERNION"
    sc.camera = cam
    fd = bpy.data.lights.new("Fill", "POINT")
    fd.energy = p["fill_energy"]
    fd.specular_factor = 0.3
    fd.color = (1.0, 0.85, 0.75)
    fo = bpy.data.objects.new("Fill", fd)
    c.objects.link(fo)
    fo.parent = cam
    fo.location = (0.0, 0.3, 0.6)
    fw = bpy.data.lights.new("FillAhead", "POINT")
    fw.energy = p["fwd_fill"]
    fw.color = (1.0, 0.88, 0.78)
    fw.use_shadow = False
    fw.specular_factor = 0.0          # no hot halos on the wet coat
    fwo = bpy.data.objects.new("FillAhead", fw)
    c.objects.link(fwo)
    fwo.parent = cam
    fwo.location = (0.0, 0.0, -p["fwd_dist"])

    # camera: position on path, aim at a point a little ahead, bank into turns + slow roll.
    # Keyed per frame (no constraints) so the headless render needs nothing live.
    up = Vector((0, 0, 1))
    bank_s = 0.0
    for f in range(nf):
        t = f / fps
        s = p["start"] + p["speed"] * t
        P, _ = _at(pts, cum, s)
        A, _ = _at(pts, cum, s + p["look"])
        fwd = (A - P).normalized()
        right = fwd.cross(up).normalized()
        # lateral turn ahead: how much the path swings right/left over the next few metres
        _, T0 = _at(pts, cum, s + 1.0)
        _, T1 = _at(pts, cum, s + 4.0)
        target_bank = -p["bank"] * (T1 - T0).dot(right)
        bank_s += (target_bank - bank_s) * 0.08          # eased, never snaps
        roll = math.radians(p["roll_rate"] * t + p["roll_wave"] * math.sin(t * 0.4)) + bank_s
        q = fwd.to_track_quat("-Z", "Y")
        q = q @ Quaternion((0, 0, 1), roll)
        cam.location = P
        cam.rotation_quaternion = q
        cam.keyframe_insert("location", frame=f + 1)
        cam.keyframe_insert("rotation_quaternion", frame=f + 1)
        L_, _ = _at(pts, cum, s + p["lead"])
        core.location = L_
        core.keyframe_insert("location", frame=f + 1)

    # breath + colour clocks; pre-rolled so the filter is already talking on frame 1
    pre = int(p["preroll"] * fps)
    curves = _filter_curve(seconds + p["preroll"] + 0.5, fps, bpm=70)
    scale = {"Open": BRE["open_amp"], "A2": BRE["lobe_amp"], "A3": BRE["lobe_amp"] * 0.6, "Phi": 1.0}
    for f in range(nf):
        for kk in ("Open", "A2", "A3", "Phi"):
            sock = gn.nodes[kk].outputs[0]
            sock.default_value = curves[kk][f + pre] * scale[kk]
            sock.keyframe_insert("default_value", frame=f + 1)
        t = f / fps
        for kk, v in (("Time", t), ("Drift", BRE["drift"] * t)):
            sock = mat.node_tree.nodes[kk].outputs[0]
            sock.default_value = v
            sock.keyframe_insert("default_value", frame=f + 1)
    print("wander built: path", round(cum[-1], 1), "m, min bend radius", round(rmin, 2), "m,", nf, "frames")
