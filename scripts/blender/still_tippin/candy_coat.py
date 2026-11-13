"""STILL TIPPIN — Candy Coat, step 1: the static surface.

One large, slow surface of maroon candy paint in black — a hood or door panel at night,
abstracted (VISUAL_RESET L1). The camera skims it low; the light core (L10) sits on the
horizon where the surface curves away, and the paint carries its reflection.

Replaces the spoke-cone direction (swanga_form.py), dropped 2026-11-12: radial + on-axis
read as a mandala (L5) and a wheel (L1).

build(**overrides) clears and rebuilds everything it owns. No audio yet.
    exec(open(PATH).read()); build()
"""
import bpy, math
from mathutils import Vector

P = dict(
    size=30.0,            # surface extent, metres
    grid=500,             # vertices per side (0.06 m — fine enough for the crease)
    # the body: a long rounded roll along +Y (a fender / hood crown, abstracted) with one
    # sharp character line on its flank. Profile is across X; it drifts slowly along Y.
    roll_h=1.4,           # crown height
    roll_w=3.2,           # crown half-width (gaussian sigma)
    crease_x=1.9,         # character line position across the roll
    crease_d=0.10,        # its depth
    crease_w=0.12,        # its sharpness
    drift=0.6,            # how far the crown wanders sideways along its length
    fall=0.006,           # the far end drops away so the core sits on a horizon
    swell=0.12,           # low-frequency body undulation, metres
    swell_size=6.0,       # its wavelength scale (>= 4x mesh spacing — BUILD_LOG geo rule)
    paint=(0.55, 0.05, 0.05),      # bright metallic base: the colour lives here under the coat   # base layer under the coat: deep maroon (cover)
    coat_tint=(0.75, 0.18, 0.15),
    flake_scale=260.0,
    flake_strength=0.08,
    core_dist=19.0,       # core position along +Y
    core_h=0.9,
    core_strength=80.0,
    cam_loc=(1.3, -4.5, 1.75),   # low over the flank, pitched down: paint fills the frame
    cam_tgt=(-0.3, 7.0, 0.0),
    glide=0.7,                   # m/s forward dolly (continuous version)
    lens=40,
    fill=0.002,
    band_scale=3.0,       # reflection-only world bands (see _scene)
    band_strength=0.45,
    res=(1920, 1080),
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
    for db in (bpy.data.curves, bpy.data.meshes, bpy.data.lights, bpy.data.cameras):
        for d in list(db):
            if d.users == 0:
                db.remove(d)
    return c


def _link(c, ob):
    for cc in list(ob.users_collection):
        cc.objects.unlink(ob)
    c.objects.link(ob)


def _paint(p):
    m = bpy.data.materials.get("CandyPaint") or bpy.data.materials.new("CandyPaint")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N("ShaderNodeOutputMaterial")
    bs = N("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs[0])
    bs.inputs["Base Color"].default_value = (*p["paint"], 1)
    bs.inputs["Metallic"].default_value = 0.85
    bs.inputs["Roughness"].default_value = 0.22
    bs.inputs["Coat Weight"].default_value = 0.6   # at grazing a full coat drowns the colour
    bs.inputs["Coat Roughness"].default_value = 0.015
    bs.inputs["Coat IOR"].default_value = 1.55
    bs.inputs["Coat Tint"].default_value = (*p["coat_tint"], 1)
    # flake: each voronoi cell tilts the base normal a random way; the coat stays smooth
    tc = N("ShaderNodeTexCoord")
    vo = N("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = p["flake_scale"]
    sub = N("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    nm = N("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = p["flake_strength"]
    mix = N("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = p["flake_strength"]
    mix.inputs[6].default_value = (0.5, 0.5, 1.0, 1)
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    nt.links.new(vo.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bs.inputs["Normal"])
    return m


def _surface(c, p):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=p["grid"], y_subdivisions=p["grid"],
                                    size=p["size"], location=(0, p["size"] * 0.25, 0))
    ob = bpy.context.active_object
    ob.name = "Paint"
    _link(c, ob)
    me = ob.data
    y0 = p["size"] * 0.25
    for v in me.vertices:
        wy = v.co.y + y0                        # world y
        cx = p["drift"] * math.sin(wy / 9.0)    # crown wanders
        x = v.co.x - cx
        z = p["roll_h"] * math.exp(-(x / p["roll_w"]) ** 2)
        z -= p["crease_d"] * math.exp(-((x - p["crease_x"]) / p["crease_w"]) ** 2)
        z -= p["fall"] * max(0.0, wy - 4.0) ** 2   # falls away to the horizon
        v.co.z = z
    # bake the offset into the mesh so local == world (liquid.py hit positions are world XY)
    from mathutils import Matrix
    me.transform(Matrix.Translation((0, y0, 0)))
    ob.location = (0, 0, 0)
    me.update()
    tex = bpy.data.textures.get("PaintSwell") or bpy.data.textures.new("PaintSwell", "CLOUDS")
    tex.noise_scale = p["swell_size"]
    tex.noise_depth = 0
    md = ob.modifiers.new("Swell", "DISPLACE")
    md.texture = tex
    md.texture_coords = "GLOBAL"
    md.strength = p["swell"]
    md.mid_level = 0.5
    for f in me.polygons:
        f.use_smooth = True
    ob.data.materials.append(_paint(p))
    return ob


def _core(c, p):
    loc = (0, p["core_dist"], p["core_h"])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=loc)
    ob = bpy.context.active_object
    ob.name = "Core"
    _link(c, ob)
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
    ld = bpy.data.lights.new("CoreLamp", "POINT")
    ld.energy = 6000
    ld.color = (1.0, 0.95, 0.9)
    ld.shadow_soft_size = 0.18
    lo = bpy.data.objects.new("CoreLamp", ld)
    lo.location = loc
    c.objects.link(lo)


def _strips(c):
    # long overhead strips — the street-light streak that makes paint read as paint
    # low on the far horizon, facing the camera: the glossy coat stretches each into a
    # long streak running toward the lens. Area lights never render, only their reflection.
    # softboxes above the crown, long along it: their reflections wrap over the roll
    for name, loc, rot, w, h, e in (("StripA", (-1.5, 8.0, 6.0), (0, -0.35, 0), 2.2, 16.0, 110),
                                    ("StripB", (4.0, 6.0, 4.0), (0, 0.9, 0), 1.6, 12.0, 50)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = w, h
        ld.energy = e
        ld.color = (1.0, 0.86, 0.80)     # warm, dimmer than the core (L10)
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        lo.rotation_euler = rot
        c.objects.link(lo)


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
    if p["glide"]:
        sc = bpy.context.scene
        fps = sc.render.fps
        y0 = cam.location.y
        for f in (1, 2401):          # 80 s of linear travel; extend per piece
            cam.location.y = y0 + p["glide"] * (f - 1) / fps
            cam.keyframe_insert("location", index=1, frame=f)
        cam.location.y = y0
        act = cam.animation_data.action
        for l in act.layers:
            for st in l.strips:
                for fc in st.channelbag(cam.animation_data.action_slot).fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = "LINEAR"


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
    nt = w.node_tree
    nt.nodes.clear()
    N, Lk = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputWorld")
    # camera sees black (L3); reflections see soft overhead bands — a street at night in
    # the paint. Every slope change in the liquid catches one of them.
    lp = N("ShaderNodeLightPath")
    tc = N("ShaderNodeTexCoord")
    sep = N("ShaderNodeSeparateXYZ")
    Lk(tc.outputs["Generated"], sep.inputs[0])       # world direction
    wave = N("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Y"
    wave.wave_profile = "SIN"
    wave.inputs["Scale"].default_value = p["band_scale"]
    wave.inputs["Distortion"].default_value = 2.0
    wave.inputs["Detail"].default_value = 0.0
    Lk(tc.outputs["Generated"], wave.inputs["Vector"])
    shp = N("ShaderNodeMapRange")                    # sharpen bands into soft strips
    shp.inputs["From Min"].default_value = 0.75
    shp.inputs["From Max"].default_value = 1.0
    Lk(wave.outputs["Fac"], shp.inputs["Value"])
    up = N("ShaderNodeMapRange")                     # only above the horizon
    up.inputs["From Min"].default_value = 0.0
    up.inputs["From Max"].default_value = 0.35
    Lk(sep.outputs["Z"], up.inputs["Value"])
    m1 = N("ShaderNodeMath"); m1.operation = "MULTIPLY"
    Lk(shp.outputs[0], m1.inputs[0]); Lk(up.outputs[0], m1.inputs[1])
    bands = N("ShaderNodeBackground")
    bands.inputs["Color"].default_value = (1.0, 0.82, 0.70, 1)
    m2 = N("ShaderNodeMath"); m2.operation = "MULTIPLY"
    m2.inputs[1].default_value = p["band_strength"]
    Lk(m1.outputs[0], m2.inputs[0]); Lk(m2.outputs[0], bands.inputs["Strength"])
    black = N("ShaderNodeBackground")
    black.inputs["Color"].default_value = (p["fill"],) * 3 + (1,)
    mix = N("ShaderNodeMixShader")
    Lk(lp.outputs["Is Camera Ray"], mix.inputs[0])
    Lk(bands.outputs[0], mix.inputs[1])
    Lk(black.outputs[0], mix.inputs[2])
    Lk(mix.outputs[0], out.inputs["Surface"])
    sc.world = w
    sc.view_settings.view_transform = "AgX"


def build(**overrides):
    p = dict(P, **overrides)
    c = _col()
    _scene(p)
    _surface(c, p)
    _core(c, p)
    _strips(c)
    _camera(c, p)
    print("built candy coat")
