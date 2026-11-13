"""STILL TIPPIN — bold moiré, attempt 2 (2026-11-13). Run after exec(moire.py) (PALETTES, _hex, _col).

Attempt 1 (8 multicolour sheets) averaged into shimmer — Nick: "very soft... a shimmering texture".
Strong moiré needs: TWO gratings, max contrast (black occluding lines over a light field, ~50%
duty), near-identical spacing. Depth drives it: gratings at slightly different depths; as the
camera sinks the near one grows faster, the ratio changes and the bands race and morph. The
descent and the moiré are one mechanism.
"""
import bpy, math

BOLD = dict(
    palette="rust",
    dA=2.0, dB=2.15,       # grating depths
    S=3.0,                 # world half-size of both gratings
    scale=200.0,           # wave scale (lines per object unit)
    duty=0.5,              # black share of each period
    angleB=1.2,            # degrees
    warpA=0.0, warpB=0.0, warp_scale=0.5,
    swimB=1.6,             # phase rad/s on grating B — bands sweep ~1/eps faster
    sink=0.6,              # metres the camera descends over the clip
    plate_d=3.5,
    plate_strength=1.0,
)


def _grating(c, name, depth, ang, warp, p):
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -depth))
    ob = bpy.context.active_object
    ob.name = name
    for cc in list(ob.users_collection):
        cc.objects.unlink(ob)
    c.objects.link(ob)
    ob.scale = (p["S"], p["S"], 1)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    try:
        m.surface_render_method = "BLENDED"
    except AttributeError:
        pass
    nt = m.node_tree
    nt.nodes.clear()
    N, Lk = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    tc = N("ShaderNodeTexCoord")
    mp = N("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(ang))
    Lk(tc.outputs["Object"], mp.inputs["Vector"])
    wv = N("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.wave_profile = "SAW"
    wv.inputs["Scale"].default_value = p["scale"]
    wv.inputs["Distortion"].default_value = warp
    wv.inputs["Detail"].default_value = 0.0
    wv.inputs["Detail Scale"].default_value = p["warp_scale"]
    Lk(mp.outputs[0], wv.inputs["Vector"])
    # hard-ish edge: black where saw < duty
    mr = N("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = p["duty"] - 0.04
    mr.inputs["From Max"].default_value = p["duty"] + 0.04
    mr.inputs["To Min"].default_value = 1.0     # 1 = black line (opaque)
    mr.inputs["To Max"].default_value = 0.0
    Lk(wv.outputs["Fac"], mr.inputs["Value"])
    blk = N("ShaderNodeEmission")
    blk.inputs["Color"].default_value = (0, 0, 0, 1)
    blk.inputs["Strength"].default_value = 0.0
    tr = N("ShaderNodeBsdfTransparent")
    mix = N("ShaderNodeMixShader")
    Lk(mr.outputs[0], mix.inputs[0])
    Lk(tr.outputs[0], mix.inputs[1])
    Lk(blk.outputs[0], mix.inputs[2])
    Lk(mix.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    return ob, wv


def _plate(c, p, pal):
    """Light field behind the gratings: slow palette noise, mid -> highlight of the brief."""
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -p["plate_d"]))
    ob = bpy.context.active_object
    ob.name = "Plate"
    for cc in list(ob.users_collection):
        cc.objects.unlink(ob)
    c.objects.link(ob)
    ob.scale = (p["plate_d"] * 1.2, p["plate_d"] * 1.2, 1)
    m = bpy.data.materials.new("Plate")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, Lk = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    nz = N("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.2
    nz.inputs["Detail"].default_value = 1.0
    ramp = N("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.3, _hex(pal[2])
    cr.elements[1].position, cr.elements[1].color = 0.7, _hex(pal[4])
    e = cr.elements.new(0.5)
    e.color = _hex(pal[3])
    Lk(nz.outputs["Fac"], ramp.inputs["Fac"])
    em = N("ShaderNodeEmission")
    em.inputs["Strength"].default_value = p["plate_strength"]
    Lk(ramp.outputs["Color"], em.inputs["Color"])
    Lk(em.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)


def build_bold(seconds=5.0, fps=30, **overrides):
    p = dict(BOLD, **overrides)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = fps
    sc.view_settings.view_transform = "Standard"
    c = _col()
    pal = PALETTES[p["palette"]]
    w = bpy.data.worlds.get("MoireWorld") or bpy.data.worlds.new("MoireWorld")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = _hex(pal[0])
    sc.world = w
    _plate(c, p, pal)
    A, wvA = _grating(c, "GratingA", p["dA"], 0.0, p["warpA"], p)
    B, wvB = _grating(c, "GratingB", p["dB"], p["angleB"], p["warpB"], p)
    cd = bpy.data.cameras.new("Cam")
    cd.lens = 30
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.rotation_euler = (0, 0, math.radians(8))
    sc.camera = cam
    nf = int(seconds * fps)
    sc.frame_start, sc.frame_end = 1, nf
    for f in (1, nf):
        t = (f - 1) / fps
        cam.location.z = -p["sink"] * t / seconds
        cam.keyframe_insert("location", index=2, frame=f)
        wvB.inputs["Phase Offset"].default_value = p["swimB"] * t
        wvB.inputs["Phase Offset"].keyframe_insert("default_value", frame=f)
    for idb in (cam, B.data.materials[0].node_tree):
        ad = idb.animation_data
        for l in ad.action.layers:
            for st in l.strips:
                for fc in st.channelbag(ad.action_slot).fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = "LINEAR"
    print("bold built", {k: p[k] for k in ("dA", "dB", "scale", "angleB", "warpA", "warpB")})
