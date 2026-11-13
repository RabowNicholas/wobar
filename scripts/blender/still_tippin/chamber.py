"""STILL TIPPIN — THE CHAMBER, material exploration (2026-11-13). Stills only, static shape.

Concept (Nick, from listening): drop 1 — heavy formant-like filter automation, bouncy, "an
alien voice talking"; drop 2 — sustained hits, psychedelic, inevitable, "some object or space
being crushed by the sound". A formant IS a cavity changing shape, so: one hollow chamber, camera
inside. Drop 1 it articulates like a vocal tract; drop 2 it is crushed, resets, crushed another
way. Nick wants an ORGANIC material this time. Geometry stays abstract (L1: no mouth, no creature).

build(material) rebuilds everything it owns.
"""
import bpy, math, bmesh
from mathutils import Vector

OWN = "STILL_TIPPIN"

GEO = dict(
    length=12.0, R=1.6,
    n_theta=256, n_y=320,
    lobe2=0.18, lobe3=0.10,     # vowel-ish cross-section lobes
    twist=0.9,                  # lobe rotation along the length (radians over the tube)
    pinch=0.25, pinch_y=5.5, pinch_w=1.3,     # a constriction partway down
    flare=0.25,                 # chamber widens past the pinch
    pleat=0.0, pleat_n=36,      # gill pleats (0 = smooth)
    noise=0.06,
)


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
    for db in (bpy.data.meshes, bpy.data.lights, bpy.data.cameras, bpy.data.materials):
        for d in list(db):
            if d.users == 0:
                db.remove(d)
    return c


def _link(c, ob):
    for cc in list(ob.users_collection):
        cc.objects.unlink(ob)
    c.objects.link(ob)


def _radius(th, y, g):
    L = g["length"]
    t = y / L
    a = g["twist"] * t
    r = g["R"] * (1 + g["lobe2"] * math.cos(2 * (th + a)) + g["lobe3"] * math.cos(3 * th - 2 * a))
    r *= 1 - g["pinch"] * math.exp(-((y - g["pinch_y"]) / g["pinch_w"]) ** 2)
    r *= 1 + g["flare"] * max(0.0, (y - g["pinch_y"]) / (L - g["pinch_y"]))
    if g["pleat"]:
        r += g["pleat"] * math.sin(g["pleat_n"] * th + 0.6 * y)
    # cheap organic wobble
    r += g["noise"] * (math.sin(3 * th + 1.7 * y) * math.sin(1.3 * y + 0.5) +
                       0.6 * math.sin(5 * th - 0.9 * y + 2.0))      # integer θ terms: no seam
    return r


def _tube(c, g):
    me = bpy.data.meshes.new("Chamber")
    bm = bmesh.new()
    nt, ny = g["n_theta"], g["n_y"]
    verts = []
    for j in range(ny):
        y = g["length"] * j / (ny - 1)
        row = []
        for i in range(nt):
            th = 2 * math.pi * i / nt
            r = _radius(th, y, g)
            row.append(bm.verts.new((r * math.cos(th), y, r * math.sin(th))))
        verts.append(row)
    for j in range(ny - 1):
        for i in range(nt):
            a, b = verts[j][i], verts[j][(i + 1) % nt]
            cc, d = verts[j + 1][(i + 1) % nt], verts[j + 1][i]
            bm.faces.new((a, b, cc, d))          # winding -> normals face inward (verified: dot(n, radial) < 0)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    ob = bpy.data.objects.new("Chamber", me)
    c.objects.link(ob)
    # UV-ish attribute for materials: generated coords are fine; store along/around too
    return ob


# ---------------------------------------------------------------- materials
def _base_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bs.outputs[0], out.inputs["Surface"])
    return m, nt, bs, out


def _noise(nt, scale, detail=2.0, dist=0.0, coord="Object"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Distortion"].default_value = dist
    nt.links.new(tc.outputs[coord], nz.inputs["Vector"])
    return nz


def _bump(nt, bs, height, strength):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = strength
    nt.links.new(height, b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bs.inputs["Normal"])
    if "Coat Normal" in bs.inputs:
        pass


def _ramp(nt, fac, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0]
    els[1].position, els[1].color = stops[-1]
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = col
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def mat_membrane():
    """Translucent wet membrane, lit from outside: the walls glow where they are thin."""
    m, nt, bs, out = _base_mat("Membrane")
    # mottled membrane, features stretched along the tube (Y) — fibres, not rings
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 2.5
    fib.inputs["Detail"].default_value = 6.0
    fib.inputs["Distortion"].default_value = 0.8
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (3.0, 0.35, 3.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], fib.inputs["Vector"])
    col = _ramp(nt, fib.outputs["Fac"], [(0.35, _hex("#6F4E3A")), (0.5, _hex("#A6633D")), (0.68, _hex("#C7BBA6"))])
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.28
    bs.inputs["Subsurface Weight"].default_value = 1.0
    bs.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.18)
    bs.inputs["Subsurface Scale"].default_value = 0.25
    bs.inputs["Coat Weight"].default_value = 0.5
    bs.inputs["Coat Roughness"].default_value = 0.08
    _bump(nt, bs, fib.outputs["Fac"], 0.15)
    # translucency so outside lights show through
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(col, tr.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.35
    nt.links.new(bs.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def mat_gills():
    """Velvet pleats, like the underside of a mushroom cap."""
    m, nt, bs, out = _base_mat("Gills")
    nz = _noise(nt, 2.0, 3.0)
    col = _ramp(nt, nz.outputs["Fac"], [(0.3, _hex("#5A0F78")), (0.55, _hex("#6B2E87")), (0.8, _hex("#A085AE"))])
    nt.links.new(col, bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.65
    bs.inputs["Sheen Weight"].default_value = 0.8
    bs.inputs["Sheen Roughness"].default_value = 0.4
    bs.inputs["Subsurface Weight"].default_value = 0.4
    bs.inputs["Subsurface Scale"].default_value = 0.05
    fine = _noise(nt, 40.0, 4.0)
    _bump(nt, bs, fine.outputs["Fac"], 0.2)
    return m


def mat_nacre():
    """Mother-of-pearl: pale shell with thin-film iridescence — the colour is built into the
    material, muted by a pale base."""
    m, nt, bs, out = _base_mat("Nacre")
    nz = _noise(nt, 1.5, 3.0, 1.5)
    bs.inputs["Base Color"].default_value = _hex("#C7BBA6")
    bs.inputs["Metallic"].default_value = 0.35
    bs.inputs["Roughness"].default_value = 0.14
    tf = nt.nodes.new("ShaderNodeMapRange")
    tf.inputs["To Min"].default_value = 250.0
    tf.inputs["To Max"].default_value = 700.0
    nt.links.new(nz.outputs["Fac"], tf.inputs["Value"])
    nt.links.new(tf.outputs[0], bs.inputs["Thin Film Thickness"])
    bs.inputs["Thin Film IOR"].default_value = 1.45
    lay = nt.nodes.new("ShaderNodeTexWave")          # growth layers
    lay.wave_type = "RINGS"
    lay.inputs["Scale"].default_value = 3.0
    lay.inputs["Distortion"].default_value = 8.0
    lay.inputs["Detail"].default_value = 2.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Object"], lay.inputs["Vector"])
    _bump(nt, bs, lay.outputs["Fac"], 0.12)
    return m


def mat_clay():
    """Wet clay / mud: dark earth, glossy where wet, matte where drying."""
    m, nt, bs, out = _base_mat("Clay")
    nz = _noise(nt, 3.0, 6.0, 0.4)
    col = _ramp(nt, nz.outputs["Fac"], [(0.35, _hex("#0E0813")), (0.5, _hex("#6F4E3A")), (0.7, _hex("#8A5A3D"))])
    nt.links.new(col, bs.inputs["Base Color"])
    wet = _noise(nt, 0.8, 2.0)
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["From Min"].default_value = 0.4
    rr.inputs["From Max"].default_value = 0.6
    rr.inputs["To Min"].default_value = 0.08
    rr.inputs["To Max"].default_value = 0.7
    nt.links.new(wet.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs[0], bs.inputs["Roughness"])
    bs.inputs["Coat Weight"].default_value = 0.4
    bs.inputs["Coat Roughness"].default_value = 0.05
    fine = _noise(nt, 25.0, 8.0)
    _bump(nt, bs, fine.outputs["Fac"], 0.35)
    return m


MATS = {"membrane": (mat_membrane, {}),
        "gills": (mat_gills, dict(pleat=0.07, pleat_n=48)),
        "nacre": (mat_nacre, {}),
        "clay": (mat_clay, {})}


def build(material="membrane", **geo):
    fn, g_over = MATS[material]
    g = dict(GEO, **g_over)
    g.update(geo)
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    try:
        sc.eevee.use_raytracing = True
    except AttributeError:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    c = _col()
    w = bpy.data.worlds.get("ChamberWorld") or bpy.data.worlds.new("ChamberWorld")
    w.use_nodes = True
    w.node_tree.nodes.clear()
    wo = w.node_tree.nodes.new("ShaderNodeOutputWorld")
    bg = w.node_tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1)
    w.node_tree.links.new(bg.outputs[0], wo.inputs["Surface"])
    sc.world = w
    ob = _tube(c, g)
    ob.data.materials.append(fn())
    # the light at the far end (L10)
    ld = bpy.data.lights.new("Core", "POINT")
    ld.energy = 900
    ld.color = (1.0, 0.93, 0.86)
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new("Core", ld)
    lo.location = (0.1, g["length"] - 1.2, 0.05)
    c.objects.link(lo)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=lo.location)
    core = bpy.context.active_object
    core.name = "CoreGlow"
    _link(c, core)
    cm = bpy.data.materials.new("CoreGlow")
    cm.use_nodes = True
    cn = cm.node_tree
    cn.nodes.clear()
    co_ = cn.nodes.new("ShaderNodeOutputMaterial")
    ce = cn.nodes.new("ShaderNodeEmission")
    ce.inputs["Color"].default_value = (1.0, 0.95, 0.9, 1)
    ce.inputs["Strength"].default_value = 40.0
    cn.links.new(ce.outputs[0], co_.inputs[0])
    core.data.materials.append(cm)
    # soft light from behind the camera, down the tube, so the walls carry the material
    ld2 = bpy.data.lights.new("Fill", "AREA")
    ld2.size = 1.2
    ld2.energy = 160
    ld2.color = (1.0, 0.85, 0.75)
    lo2 = bpy.data.objects.new("Fill", ld2)
    lo2.location = (0.0, 0.1, 0.3)
    lo2.rotation_euler = (math.radians(90), 0, 0)       # -Z -> +Y (verified)
    c.objects.link(lo2)
    if material == "membrane":
        # outside lights: the walls glow where they are thin
        for i, (x, z) in enumerate(((3.5, 1.5), (-3.0, -2.0), (0.5, 3.6))):
            l = bpy.data.lights.new(f"Out{i}", "AREA")
            l.size = 6.0
            l.energy = 120
            l.color = (1.0, 0.75, 0.6)
            o = bpy.data.objects.new(f"Out{i}", l)
            o.location = (x, 4.0 + 2 * i, z)
            o.rotation_euler = (Vector((0, 4.0 + 2 * i, 0)) - o.location).to_track_quat("-Z", "Y").to_euler()
            c.objects.link(o)
    cd = bpy.data.cameras.new("Cam")
    # off-axis, close to one wall, passage off to the side: dead-centre down a narrowing
    # tube reads as an EYE (pupil = the pinch) — the ATEM pareidolia trap, L1
    cd.lens = 24
    cd.clip_start = 0.01
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.location = (0.95, 0.5, -0.55)
    tgt = Vector((-1.5, 4.0, 1.1))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    print("chamber built:", material)
