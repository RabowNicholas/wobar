"""STILL TIPPIN — Moiré Lace over Endless Descent (idea A + B), stills stage.

Psychedelic per Nick's brief (WOBAR_STAGE_LOOPS_BRIEF): stop trusting what you see — near/far,
big/small unreadable. Mechanism, not material:

  descent (B)  sheets of fine lines stacked under the camera at geometric depths d0·2^i,
               each scaled 2^i, so every sheet projects at the same size — depth is unreadable.
  moiré (A)    each sheet's line frequency / angle / warp is slightly off its neighbours; where
               they overlap, phantom shapes appear that exist in no sheet.

All lines, frame filled, muted palettes from the brief. Camera looks straight down: sheets are
parallel to the sensor, so there is no vanishing point and nothing radial (no mandala, L5).

build(variant_name) clears and rebuilds.  exec(open(PATH).read()); build("rust_lines")
"""
import bpy, math

PALETTES = {   # brief: dark -> light
    "rust":   ["#0E0813", "#6F4E3A", "#8A5A3D", "#A6633D", "#C7BBA6"],
    "purple": ["#190028", "#2D0546", "#5A0F78", "#6B2E87", "#A085AE"],
    "green":  ["#0E0813", "#1E505A", "#4D6149", "#5C7470", "#7A8A6F"],
    "blue":   ["#0E0813", "#2C4554", "#3B4C73", "#4A6479", "#948C9E"],
}

BASE = dict(
    palette="rust",
    sheets=5,
    d0=2.0,            # first sheet depth below camera
    ratio=2.0,         # depth/scale step: 2 = perfect self-similarity
    freq=60.0,         # lines across a sheet
    width=0.10,        # line thickness (fraction of a period, 0-1)
    angles=(0, 4, -3, 7, -6),        # degrees per sheet — small offsets make the moiré
    freq_mul=(1.0, 1.04, 0.97, 1.07, 0.95),
    warp=(2.0, 2.4, 1.8, 2.8, 2.2),  # wave distortion per sheet: curves the lines
    warp_scale=1.5,
    lace=False,        # True: two crossing line families per sheet (spoke lacing)
    lace_angle=50.0,
    strength=(1.6, 1.4, 1.3, 1.2, 1.1),
    fog=False,         # True: deeper sheets fade + core below (depth readable — the control)
    core=True,
    lens=30,
)

VARIANTS = {
    "rust_lines":   dict(),
    "rust_lace":    dict(lace=True, freq=45.0),
    "purple_swirl": dict(palette="purple", warp=(4.0, 5.0, 3.5, 6.0, 4.5), warp_scale=0.8, width=0.12),
    "rust_fog":     dict(fog=True, warp=(3.0, 3.5, 2.6, 4.0, 3.2)),
    "rust_fine":    dict(freq=150.0, width=0.14, warp=(0.6, 0.8, 0.5, 0.9, 0.7), warp_scale=0.6,
                         angles=(0, 2, -1.5, 3, -2.5)),   # near-straight fine lines: pure moiré
}

OWN = "STILL_TIPPIN"


def _hex(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1,)


def _col():
    c = bpy.data.collections.get(OWN)
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new(OWN)
        bpy.context.scene.collection.children.link(c)
    for db in (bpy.data.meshes, bpy.data.lights, bpy.data.cameras, bpy.data.curves):
        for d in list(db):
            if d.users == 0:
                db.remove(d)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    return c


def _lines(nt, p, i, angle_off=0.0):
    """Wave-texture line family -> 0-1 line mask."""
    N, Lk = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    mp = N("ShaderNodeMapping")
    mp.name = f"Map{i}_{int(angle_off)}"
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(p["angles"][i] + angle_off))
    Lk(tc.outputs["Object"], mp.inputs["Vector"])
    wv = N("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.wave_profile = "SAW"
    wv.inputs["Scale"].default_value = p["freq"] * p["freq_mul"][i] / 6.2832
    wv.inputs["Distortion"].default_value = p["warp"][i]
    wv.inputs["Detail"].default_value = 0.0
    wv.inputs["Detail Scale"].default_value = p["warp_scale"]
    Lk(mp.outputs[0], wv.inputs["Vector"])
    mr = N("ShaderNodeMapRange")          # saw 0-1 -> thin line at the top of each period
    mr.inputs["From Min"].default_value = 1.0 - p["width"]
    mr.inputs["From Max"].default_value = 1.0
    Lk(wv.outputs["Fac"], mr.inputs["Value"])
    return mr.outputs[0]


def _sheet_mat(p, i, color):
    m = bpy.data.materials.new(f"Sheet{i}")
    m.use_nodes = True
    try:
        m.surface_render_method = "BLENDED"
    except AttributeError:
        m.blend_method = "BLEND"
    nt = m.node_tree
    nt.nodes.clear()
    N, Lk = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")
    mask = _lines(nt, p, i)
    if p["lace"]:
        mask2 = _lines(nt, p, i, p["lace_angle"])
        mx = N("ShaderNodeMath"); mx.operation = "MAXIMUM"
        Lk(mask, mx.inputs[0]); Lk(mask2, mx.inputs[1])
        mask = mx.outputs[0]
    fade = 1.0
    if p["fog"]:
        fade = 0.55 ** i
    em = N("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    em.inputs["Strength"].default_value = p["strength"][i] * fade
    tr = N("ShaderNodeBsdfTransparent")
    mix = N("ShaderNodeMixShader")
    Lk(mask, mix.inputs[0])
    Lk(tr.outputs[0], mix.inputs[1])
    Lk(em.outputs[0], mix.inputs[2])
    Lk(mix.outputs[0], out.inputs["Surface"])
    return m


def build(name="rust_lines", **overrides):
    p = dict(BASE, **VARIANTS.get(name, {}))
    p.update(overrides)
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"     # palette hexes land as written
    c = _col()
    w = bpy.data.worlds.get("MoireWorld") or bpy.data.worlds.new("MoireWorld")
    w.use_nodes = True
    w.node_tree.nodes.clear()
    wo = w.node_tree.nodes.new("ShaderNodeOutputWorld")
    bg = w.node_tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = _hex(PALETTES[p["palette"]][0])
    w.node_tree.links.new(bg.outputs[0], wo.inputs["Surface"])
    sc.world = w
    pal = PALETTES[p["palette"]]
    for i in range(p["sheets"]):
        d = p["d0"] * p["ratio"] ** i
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -d))
        ob = bpy.context.active_object
        ob.name = f"Sheet{i}"
        for cc in list(ob.users_collection):
            cc.objects.unlink(ob)
        c.objects.link(ob)
        s = d * 1.3                       # covers the frame at its depth (30 mm)
        ob.scale = (s, s, 1)
        color = _hex(pal[1 + (i % 4)])
        ob.data.materials.append(_sheet_mat(p, i, color))
    if p["core"]:
        dz = p["d0"] * p["ratio"] ** p["sheets"] * 1.2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=dz * 0.012, location=(0.0, 0.0, -dz))
        core = bpy.context.active_object
        core.name = "Core"
        for cc in list(core.users_collection):
            cc.objects.unlink(core)
        c.objects.link(core)
        m = bpy.data.materials.new("CoreLight")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        o = nt.nodes.new("ShaderNodeOutputMaterial")
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Color"].default_value = _hex(pal[4])
        e.inputs["Strength"].default_value = 6.0
        nt.links.new(e.outputs[0], o.inputs[0])
        core.data.materials.append(m)
    cd = bpy.data.cameras.new("Cam")
    cd.lens = p["lens"]
    cd.clip_end = 2000
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.location = (0, 0, 0)
    cam.rotation_euler = (0, 0, math.radians(8))     # looking straight down (-Z), slight roll
    sc.camera = cam
    print("built", name)
