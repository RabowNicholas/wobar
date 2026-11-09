"""MAKYO shard field - concept blockout.

    blender -b --factory-startup -P scripts/blender/makyo_shards.py -- out.png [out.blend] [k=v ...]

Thousands of thin mirror shards hang in black around a distant white core. Each shard
is metallic; its tint comes from the WOBAR Rust ramp, indexed by the shard's random id
and its facing angle, so a glint is copper -> amber -> orange -> bone as it turns.
`align` (0..1) slerps every shard from its random tumble toward the heliostat pose that
throws the core straight into the camera - the makyo whiteout.
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Quaternion, Matrix

P = dict(
    count=2600, seed=7,
    depth_near=3.0, depth_far=70.0,   # shard field along +Y
    spread=1.0,                       # radius growth with depth (cone)
    corridor=0.35,                    # fraction of cone radius kept clear-ish so the core shows
    size=0.35, size_var=0.6,
    rough=0.12,
    core_y=90.0, core_r=1.2, core_strength=400.0, light_w=1.5e6,
    fill=0.004,                      # world fill so shard silhouettes read
    align=0.0,
    halo_r=40.0, halo_strength=6.0, halo_pow=3.0,   # soft body of light behind the core
    res_pct=50, samples=32, frame_shift=0,
)

RUST = ["#0E0813", "#6F4E3A", "#8A5A3D", "#A6633D", "#C17A4E", "#C7BBA6"]
PATINA = "#5C7470"


def parse():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    outs = []
    for a in argv:
        if "=" in a:
            k, v = a.split("=", 1)
            P[k] = type(P[k])(v)
        else:
            outs.append(a)
    return outs


def lin(h):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)


def shard_mesh(rng, name):
    """Irregular convex polygon, thin slab - a broken mirror piece."""
    n = rng.randint(4, 7)
    angs = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    bm = bmesh.new()
    sx, sy = rng.uniform(0.5, 1.0), rng.uniform(0.9, 1.6)
    verts = [bm.verts.new((math.cos(a) * sx * rng.uniform(0.6, 1.0),
                           math.sin(a) * sy * rng.uniform(0.6, 1.0), 0)) for a in angs]
    f = bm.faces.new(verts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, -0.03),
                        verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def node(nt, kind, loc, **kw):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def mirror_material():
    m = bpy.data.materials.new("MakyoMirror")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = P["rough"]
    oi = node(nt, "ShaderNodeObjectInfo", (-900, 0))
    lw = node(nt, "ShaderNodeLayerWeight", (-900, -200))
    lw.inputs["Blend"].default_value = 0.4
    # ramp index = random * 0.7 + facing * 0.5, wrapped -> the colour moves as the shard turns
    m1 = node(nt, "ShaderNodeMath", (-700, 0), operation="MULTIPLY")
    m1.inputs[1].default_value = 0.7
    nt.links.new(oi.outputs["Random"], m1.inputs[0])
    m2 = node(nt, "ShaderNodeMath", (-700, -200), operation="MULTIPLY")
    m2.inputs[1].default_value = 0.5
    nt.links.new(lw.outputs["Facing"], m2.inputs[0])
    add = node(nt, "ShaderNodeMath", (-520, -100), operation="ADD")
    nt.links.new(m1.outputs[0], add.inputs[0])
    nt.links.new(m2.outputs[0], add.inputs[1])
    wrap = node(nt, "ShaderNodeMath", (-360, -100), operation="PINGPONG")
    wrap.inputs[1].default_value = 1.0
    nt.links.new(add.outputs[0], wrap.inputs[0])
    # keep the bottom (offblack) stop out of the mirror tint: remap 0..1 -> 0.2..1
    mr = node(nt, "ShaderNodeMapRange", (-200, -100))
    mr.inputs["To Min"].default_value = 0.2
    nt.links.new(wrap.outputs[0], mr.inputs["Value"])
    ramp = node(nt, "ShaderNodeValToRGB", (0, -100))
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, (*lin(RUST[0]), 1)
    els[1].position, els[1].color = 1.0, (*lin(RUST[5]), 1)
    for i, h in enumerate(RUST[1:5], 1):
        e = els.new(i / 5)
        e.color = (*lin(h), 1)
    nt.links.new(mr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc = bpy.context.scene
    rng = random.Random(P["seed"])

    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    ee = sc.eevee
    for attr, val in (("use_raytracing", True), ("taa_render_samples", P["samples"])):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    if hasattr(ee, "ray_tracing_options"):
        ee.ray_tracing_options.resolution_scale = "1"
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = P["res_pct"]
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy" if "AgX - Punchy" in [
        i.identifier for i in type(sc.view_settings).bl_rna.properties["look"].enum_items] else "None"

    w = bpy.data.worlds.new("MakyoWorld")
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (*lin(PATINA), 1)   # the one cool element: faint patina ambient
    bg.inputs[1].default_value = P["fill"]
    sc.world = w

    cam_d = bpy.data.cameras.new("Cam")
    cam_d.lens = 28
    cam_d.clip_end = 500
    cam = bpy.data.objects.new("Cam", cam_d)
    cam.location = (0, 0, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam

    core_pos = Vector((0, P["core_y"], 0))
    em = bpy.data.materials.new("Core")
    em.use_nodes = True
    ent = em.node_tree
    ent.nodes.clear()
    out = node(ent, "ShaderNodeOutputMaterial", (300, 0))
    es = node(ent, "ShaderNodeEmission", (0, 0))
    es.inputs["Color"].default_value = (1, 1, 1, 1)
    es.inputs["Strength"].default_value = P["core_strength"]
    ent.links.new(es.outputs[0], out.inputs["Surface"])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=P["core_r"], location=core_pos)
    core = bpy.context.active_object
    core.name = "Core"
    core.data.materials.append(em)

    # halo: big camera-facing disc behind the core, white centre -> Rust ramp -> black edge,
    # so shards whose reflection lands near the core catch a colour, not just white or nothing
    hm = bpy.data.materials.new("Halo")
    hm.use_nodes = True
    hn = hm.node_tree
    hn.nodes.clear()
    ho = node(hn, "ShaderNodeOutputMaterial", (600, 0))
    tc = node(hn, "ShaderNodeTexCoord", (-800, 0))
    ln = node(hn, "ShaderNodeVectorMath", (-600, 0), operation="LENGTH")
    hn.links.new(tc.outputs["Object"], ln.inputs[0])
    inv = node(hn, "ShaderNodeMapRange", (-420, 0))
    inv.inputs["From Max"].default_value = 1.0
    inv.inputs["To Min"].default_value = 1.0
    inv.inputs["To Max"].default_value = 0.0
    hn.links.new(ln.outputs["Value"], inv.inputs["Value"])
    pw = node(hn, "ShaderNodeMath", (-240, 0), operation="POWER")
    pw.inputs[1].default_value = P["halo_pow"]
    hn.links.new(inv.outputs[0], pw.inputs[0])
    hr = node(hn, "ShaderNodeValToRGB", (-60, 150))
    he = hr.color_ramp.elements
    he[0].position, he[0].color = 0.0, (*lin(RUST[0]), 1)
    he[1].position, he[1].color = 1.0, (1, 1, 1, 1)
    for i, h in enumerate(RUST[1:], 1):
        e = he.new(i / 6.5)
        e.color = (*lin(h), 1)
    hn.links.new(pw.outputs[0], hr.inputs["Fac"])
    hs = node(hn, "ShaderNodeMath", (-60, -100), operation="MULTIPLY")
    hs.inputs[1].default_value = P["halo_strength"]
    hn.links.new(pw.outputs[0], hs.inputs[0])
    he_ = node(hn, "ShaderNodeEmission", (300, 0))
    hn.links.new(hr.outputs["Color"], he_.inputs["Color"])
    hn.links.new(hs.outputs[0], he_.inputs["Strength"])
    hn.links.new(he_.outputs[0], ho.inputs["Surface"])
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1.0, fill_type="NGON",
                                      location=core_pos + Vector((0, 4, 0)),
                                      rotation=(math.radians(90), 0, 0))
    halo = bpy.context.active_object
    halo.name = "Halo"
    halo.scale = (P["halo_r"],) * 3
    halo.data.materials.append(hm)

    ld = bpy.data.lights.new("CoreLight", "POINT")
    ld.energy = P["light_w"]
    ld.shadow_soft_size = P["core_r"]
    ld.color = (1, 0.97, 0.92)
    lo = bpy.data.objects.new("CoreLight", ld)
    lo.location = core_pos
    sc.collection.objects.link(lo)

    mat = mirror_material()
    variants = [shard_mesh(rng, f"shard_{i}") for i in range(24)]
    for me in variants:
        me.materials.append(mat)

    col = bpy.data.collections.new("Shards")
    sc.collection.children.link(col)
    eye = Vector((0, 0, 0))
    half_h = math.tan(cam_d.angle / 2)
    for i in range(P["count"]):
        y = P["depth_near"] + (P["depth_far"] - P["depth_near"]) * rng.random() ** 1.6
        rmax = y * half_h * P["spread"]
        r = rmax * math.sqrt(rng.uniform(P["corridor"] ** 2, 1.0))
        if rng.random() < 0.08:   # a few strays inside the corridor
            r = rmax * rng.uniform(0.05, P["corridor"])
        a = rng.uniform(0, 2 * math.pi)
        pos = Vector((math.cos(a) * r, y, math.sin(a) * r * 1.6))
        o = bpy.data.objects.new(f"S{i:04d}", rng.choice(variants))
        o.location = pos
        s = P["size"] * (1 + P["size_var"] * (rng.random() * 2 - 1)) * (0.6 + y / P["depth_far"])
        o.scale = (s, s, s)
        q_rand = Quaternion((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        # heliostat pose: shard normal (+Z) bisects shard->core and shard->eye
        n = ((core_pos - pos).normalized() + (eye - pos).normalized()).normalized()
        q_al = Vector((0, 0, 1)).rotation_difference(n)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = q_rand.slerp(q_al, P["align"])
        o["tumble"] = rng.random()
        col.objects.link(o)
    print(f"built {P['count']} shards", flush=True)


def main():
    outs = parse()
    build()
    sc = bpy.context.scene
    png = next((o for o in outs if o.endswith(".png")), None)
    blend = next((o for o in outs if o.endswith(".blend")), None)
    if blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend))
    if png:
        sc.render.filepath = os.path.abspath(png)
        bpy.ops.render.render(write_still=True)
        print("wrote", png, flush=True)
    sys.stdout.flush()
    os._exit(0)


main()
