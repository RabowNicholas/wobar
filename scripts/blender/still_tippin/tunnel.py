"""STILL TIPPIN — THE CHAMBER as a winding tunnel (2026-11-13). Run after exec(chamber.py) and
exec(chamber_motion.py) — reuses _tube/_radius, _gn (breath), _band_mat (contour bands), _filter_curve.

Nick on chamber_breath v1: "closer. it moves too quickly. i want to be inside of the tunnel more.
the perspective point should be with the light in the middle. a tunnel that you are moving down
that is winding." Reference: an Instagram post (not viewable without login).

  tunnel    the straight membrane tube (built along +Y, no pinch — the pinch was the 'pupil')
            bent along a winding, descending path with a Curve modifier AFTER the breath GN,
            so breath stays in straight local coords.
  camera    follows the path slowly; Track To a light that rides the path ahead — the light
            is always the vanishing point, the centre of frame (L10). Off-centre framing was only
            needed for the static pinch shot; moving down a winding tube, the hole stops being
            a pupil because the walls keep turning.
  slower    filter targets per beat (not per 8th), softer spring, slower crawl + drift.
"""
import bpy, math
from mathutils import Vector

TUN = dict(
    length=64.0,
    path_amp_x=3.0, path_per_x=9.0,      # sideways winding
    path_amp_z=1.6, path_per_z=13.0,     # up/down winding
    descent=0.18,                         # metres down per metre forward
    speed=1.0,                            # m/s camera travel
    start=2.0,                            # camera start along the path
    lead=11.0,                            # light distance ahead of the camera
    core_energy=1800,
    fill_energy=35,
)


def _path(c, p):
    cu = bpy.data.curves.new("TunnelPath", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    ys = [i * 0.5 for i in range(int(p["length"] / 0.5) + 1)]
    sp.points.add(len(ys) - 1)
    pts = []
    for i, y in enumerate(ys):
        x = p["path_amp_x"] * math.sin(y / p["path_per_x"])
        z = -p["descent"] * y + p["path_amp_z"] * math.sin(y / p["path_per_z"] + 1.0) \
            - p["path_amp_z"] * math.sin(1.0)                      # starts at z = 0
        sp.points[i].co = (x, y, z, 1)
        pts.append(Vector((x, y, z)))
    ob = bpy.data.objects.new("TunnelPath", cu)
    c.objects.link(ob)
    L = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1))
    return ob, L


def build_tunnel(seconds=8.0, fps=30, **over):
    p = dict(TUN, **over)
    sc = bpy.context.scene
    sc.render.fps = fps
    # slower breath and colour (Nick: "moves too quickly")
    BRE.update(crawl=0.12, drift=0.025, stiff=90.0, damp=6.0, open_amp=0.45, glow=2.5)
    build("membrane", length=p["length"], n_y=900, n_theta=192, pinch=0.0, flare=0.0,
          lobe2=0.12, lobe3=0.08, twist=6.0, noise=0.08)
    c = bpy.data.collections["STILL_TIPPIN"]
    for o in list(c.objects):                       # outside lights / static cam from chamber.py
        if o.name.startswith("Out") or o.name in ("Cam", "Fill", "Core", "CoreGlow"):
            bpy.data.objects.remove(o, do_unlink=True)
    ob = bpy.data.objects["Chamber"]
    gn = _gn(ob)
    ob.data.materials.clear()
    mat = _band_mat(BRE)
    ob.data.materials.append(mat)
    path, L = _path(c, p)
    cm = ob.modifiers.new("Wind", "CURVE")
    cm.object = path
    cm.deform_axis = "POS_Y"

    nf = int(seconds * fps)
    sc.frame_start, sc.frame_end = 1, nf

    def follow(o, offset_m):
        con = o.constraints.new("FOLLOW_PATH")
        con.target = path
        con.use_fixed_location = True
        con.use_curve_follow = False
        for f in (1, nf):
            t = (f - 1) / fps
            con.offset_factor = min(1.0, (p["start"] + offset_m + p["speed"] * t) / L)
            con.keyframe_insert("offset_factor", frame=f)
        return con

    # the light: an emissive core + point lamp riding ahead
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
    follow(core, p["lead"])
    ld = bpy.data.lights.new("Core", "POINT")
    ld.energy = p["core_energy"]
    ld.color = (1.0, 0.93, 0.86)
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new("Core", ld)
    c.objects.link(lo)
    lo.parent = core

    cd = bpy.data.cameras.new("Cam")
    cd.lens = 22
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    follow(cam, 0.0)
    tr = cam.constraints.new("TRACK_TO")
    tr.target = core
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    sc.camera = cam
    fd = bpy.data.lights.new("Fill", "POINT")
    fd.energy = p["fill_energy"]
    fd.color = (1.0, 0.85, 0.75)
    fo = bpy.data.objects.new("Fill", fd)
    c.objects.link(fo)
    fo.parent = cam
    fo.location = (0.0, 0.3, 0.6)

    # breath + colour clocks, filter targets per beat (bpm=70 → 8ths at 70 = beats at 140)
    curves = _filter_curve(seconds, fps, bpm=70)
    scale = {"Open": BRE["open_amp"], "A2": BRE["lobe_amp"], "A3": BRE["lobe_amp"] * 0.6, "Phi": 1.0}
    for f in range(nf):
        for kk in ("Open", "A2", "A3", "Phi"):
            sock = gn.nodes[kk].outputs[0]
            sock.default_value = curves[kk][f] * scale[kk]
            sock.keyframe_insert("default_value", frame=f + 1)
        t = f / fps
        for kk, v in (("Time", t), ("Drift", BRE["drift"] * t)):
            sock = mat.node_tree.nodes[kk].outputs[0]
            sock.default_value = v
            sock.keyframe_insert("default_value", frame=f + 1)
    for idb in (cam, core):
        ad = idb.animation_data
        for l in ad.action.layers:
            for st in l.strips:
                for fc in st.channelbag(ad.action_slot).fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = "LINEAR"
    print("tunnel built: path length", round(L, 1), "m,", nf, "frames")
