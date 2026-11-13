"""STILL TIPPIN — step 1: the static form.

A cone of chrome spokes in black, abstracted from the swanga elbow on the cover
(VISUAL_RESET L1: a form, never the wheel). Candy-coat finish: tinted chrome under a
deep maroon clearcoat with flake. One near-white core past the tip (L10).

build(**overrides) clears and rebuilds everything it owns, so tuning is
"change a number, rerun". No audio yet.

Run in the live session:
    exec(open(PATH).read()); build()
"""
import bpy, math
from mathutils import Vector

P = dict(
    spokes=20,            # per layer; two layers twisted opposite ways = the lace
    length=6.0,           # base ring -> tip, metres, along +Y (away from camera)
    base_r=2.2,           # base ring radius
    tip_r=0.22,           # where spokes meet the hub
    twist=0.55,           # radians of twist per layer, base -> tip
    spoke_r=0.05,        # tube radius
    sag=0.10,             # outward bow at mid-length, fraction of base_r
    candy=(0.42, 0.11, 0.10),    # coat tint, muted maroon (cover paint) — L2 ceiling
    chrome=(0.85, 0.80, 0.78),   # base metal, slightly warm
    core_strength=60.0,
    core_gap=1.2,         # core distance past the tip
    fill=0.0035,          # world fill so silhouettes read
    res=(1920, 1080),
    # camera just behind the outer base, on-axis, looking at the core.
    # history: inside the cones (0.25, 0.6, -0.15) @24mm; far out (1, -20, 0.7) read as a
    # front-on wheel / mandala (L1, L5) — keep the outer spokes breaking the frame edge
    cam_loc=(0.6, -11.0, 0.4),
    cam_tgt=(0.0, 7.2, 0.0),
    lens=35,
    ring_lights=6,
    ring_light_r=6.0,
    ring_light_e=900,
    # second cone: same shape, scaled about the shared tip so the two nest
    outer_scale=1.8,
    outer_phase=0.5,      # in spoke steps — outer spokes sit between inner ones
)

OWN = "STILL_TIPPIN"


def _col():
    c = bpy.data.collections.get(OWN)
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new(OWN)
        bpy.context.scene.collection.children.link(c)
    return c


def _spokes(c, p):
    cu = bpy.data.curves.new("Spokes", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = p["spoke_r"]
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    n, L = p["spokes"], p["length"]
    for layer, sgn in ((0, 1), (1, -1)):
        for i in range(n):
            a0 = 2 * math.pi * (i + 0.5 * layer) / n
            sp = cu.splines.new("POLY")
            steps = 24
            sp.points.add(steps - 1)
            for k in range(steps):
                t = k / (steps - 1)
                a = a0 + sgn * p["twist"] * t
                r = p["base_r"] + (p["tip_r"] - p["base_r"]) * t
                r += p["sag"] * p["base_r"] * math.sin(math.pi * t)
                sp.points[k].co = (r * math.cos(a), L * t, r * math.sin(a), 1)
    ob = bpy.data.objects.new("Spokes", cu)
    c.objects.link(ob)
    return ob


def _cone(c, p, m, name, scale, phase):
    """One spoke cone + its two rings, parented to an empty at the tip.
    The empty is the handle for motion: rotate/scale/move it and the cone follows.
    Geometry is built tip-relative (tip at local origin, base at -length*scale)."""
    pivot = bpy.data.objects.new(name, None)
    pivot.empty_display_type = "PLAIN_AXES"
    pivot.location = (0, p["length"], 0)
    c.objects.link(pivot)
    sp = _spokes(c, p)
    sp.name = name + "_Spokes"
    sp.data.name = name + "_Spokes"
    rings = (_ring(c, name + "_BaseRing", p["base_r"], 0.0, 0.06),
             _ring(c, name + "_TipRing", p["tip_r"], p["length"], 0.05))
    for ob in (sp,) + rings:
        ob.data.materials.clear()
        ob.data.materials.append(m)
        ob.location.y -= p["length"]          # tip-relative
        ob.parent = pivot
    pivot.scale = (scale,) * 3
    pivot.rotation_euler.y = 2 * math.pi * phase / p["spokes"]
    return pivot


def _ring(c, name, r, y, minor):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=minor,
                                     major_segments=128, minor_segments=16,
                                     location=(0, y, 0), rotation=(math.pi / 2, 0, 0))
    ob = bpy.context.active_object
    ob.name = name
    for cc in ob.users_collection:
        cc.objects.unlink(ob)
    c.objects.link(ob)
    bpy.ops.object.shade_smooth()
    return ob


def _candy(p):
    m = bpy.data.materials.get("CandyChrome") or bpy.data.materials.new("CandyChrome")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs[0])
    bs.inputs["Base Color"].default_value = (*p["chrome"], 1)
    bs.inputs["Metallic"].default_value = 1.0
    bs.inputs["Roughness"].default_value = 0.16
    bs.inputs["Coat Weight"].default_value = 1.0
    bs.inputs["Coat Roughness"].default_value = 0.02
    bs.inputs["Coat IOR"].default_value = 1.6
    bs.inputs["Coat Tint"].default_value = (*p["candy"], 1)
    # flake: fine voronoi into the base normal only, so the coat stays glass-smooth
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 600.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    nt.links.new(vo.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def _core(c, p):
    y = p["length"] + p["core_gap"]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, y, 0))
    ob = bpy.context.active_object
    ob.name = "Core"
    for cc in ob.users_collection:
        cc.objects.unlink(ob)
    c.objects.link(ob)
    m = bpy.data.materials.get("CoreLight") or bpy.data.materials.new("CoreLight")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.96, 0.92, 1)
    em.inputs["Strength"].default_value = p["core_strength"]
    nt.links.new(em.outputs[0], out.inputs[0])
    ob.data.materials.append(m)
    # the core as a real light too, so the chrome picks it up
    ld = bpy.data.lights.new("CoreLamp", "POINT")
    ld.energy = 900
    ld.color = (1.0, 0.95, 0.9)
    ld.shadow_soft_size = 0.12
    lo = bpy.data.objects.new("CoreLamp", ld)
    lo.location = (0, y, 0)
    c.objects.link(lo)
    return ob


def _strips(c):
    # two dim strip lights for chrome highlights — the "street light on the paint" read
    for name, loc, rot, e in (("StripKey", (-4.5, 2.0, 3.5), (0.9, 0, -0.8), 600),
                              ("StripRim", (4.0, 5.0, -2.5), (-1.9, 0, 0.6), 300)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = 0.25, 6.0
        ld.energy = e
        ld.color = (1.0, 0.93, 0.88)
        lo = bpy.data.objects.new(name, ld)
        lo.location, lo.rotation_euler = loc, rot
        c.objects.link(lo)


def _ring_lights(c, p):
    # EEVEE chrome can't reflect camera-invisible cards from inside the cone, but it
    # always takes specular from lights: strips parallel to the axis, around the outside,
    # aimed at the axis, give every spoke a running highlight
    n = p["ring_lights"]
    for i in range(n):
        a = 2 * math.pi * (i + 0.25) / n
        loc = Vector((p["ring_light_r"] * math.cos(a), p["length"] * 0.45,
                      p["ring_light_r"] * math.sin(a)))
        ld = bpy.data.lights.new(f"RingStrip{i}", "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = 0.2, p["length"] * 1.1
        ld.energy = p["ring_light_e"]
        ld.color = (1.0, 0.93, 0.88)
        lo = bpy.data.objects.new(f"RingStrip{i}", ld)
        lo.location = loc
        aim = Vector((0, loc.y, 0)) - loc
        lo.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
        c.objects.link(lo)


def _cards(c):
    # emissive cards the chrome reflects but the camera never sees
    m = bpy.data.materials.get("CardGlow") or bpy.data.materials.new("CardGlow")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 0.94, 0.9, 1)
    em.inputs["Strength"].default_value = 2.5
    nt.links.new(em.outputs[0], out.inputs[0])
    for name, loc, size in (("CardTop", (0, 3, 6), (1.2, 14)),
                            ("CardLeft", (-7, 3, 1), (1.0, 14)),
                            ("CardLow", (5, 2, -5), (0.6, 14))):
        bpy.ops.mesh.primitive_plane_add(location=loc)
        ob = bpy.context.active_object
        ob.name = name
        for cc in ob.users_collection:
            cc.objects.unlink(ob)
        c.objects.link(ob)
        ob.scale = (size[0], size[1], 1)
        ob.rotation_euler = (Vector((0, 3, 0)) - Vector(loc)).to_track_quat("Z", "Y").to_euler()
        ob.data.materials.append(m)
        ob.visible_camera = False


def _camera(c, p):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = p["lens"]
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.location = p["cam_loc"]
    tgt = Vector(p["cam_tgt"])
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def _scene(p):
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    sc.render.resolution_x, sc.render.resolution_y = p["res"]
    try:
        sc.eevee.use_raytracing = True
    except AttributeError:
        pass
    w = bpy.data.worlds.get("TippinWorld") or bpy.data.worlds.new("TippinWorld")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (p["fill"],) * 3 + (1,)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = w
    sc.view_settings.view_transform = "AgX"


def build(**overrides):
    p = dict(P, **overrides)
    for n in ("Cube", "Light", "Camera"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    c = _col()
    _scene(p)
    m = _candy(p)
    _cone(c, p, m, "ConeInner", 1.0, 0.0)
    _cone(c, p, m, "ConeOuter", p["outer_scale"], p["outer_phase"])
    _core(c, p)
    _strips(c)
    _cards(c)
    _ring_lights(c, p)
    _camera(c, p)
    print("built", {k: p[k] for k in ("spokes", "length", "base_r", "twist")})
