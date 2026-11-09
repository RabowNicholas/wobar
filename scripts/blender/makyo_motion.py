"""MAKYO - base motion: the mirror breaks in front of the light and the shards rush past you.

Run inside makyo_shards_v*.blend (live via MCP: exec(open(path).read())).
Replaces the static S#### shard objects with one Geometry Nodes object, `ShardStream`:
each shard has its own phase t = fract(phase + frame / Loop Frames), flies a straight line
from the break (near the core, small radius) to past the camera (large radius), grows in
from zero at the break and tumbles as it goes. Every input is on the modifier panel.
"""
import bpy, math

def lin(h):
    h = h.lstrip("#"); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)

INPUTS = [  # name, type, default
    ("Count", "NodeSocketInt", 3000),
    ("Loop Frames", "NodeSocketFloat", 600.0),   # 20 s at 30 fps: one shard's whole flight
    ("Break Depth", "NodeSocketFloat", 80.0),    # y where shards appear
    ("Pass Depth", "NodeSocketFloat", -8.0),     # y where they leave (behind camera)
    ("Break Radius", "NodeSocketFloat", 6.0),
    ("Pass Radius Min", "NodeSocketFloat", 1.8),  # keeps shards out of the lens
    ("Pass Radius Max", "NodeSocketFloat", 22.0),
    ("Vertical Stretch", "NodeSocketFloat", 1.6),
    ("Size Min", "NodeSocketFloat", 0.12),
    ("Size Max", "NodeSocketFloat", 1.1),
    ("Size Skew", "NodeSocketFloat", 2.5),       # >1: mostly small, a few big
    ("Grow In", "NodeSocketFloat", 0.06),        # fraction of the flight spent growing in
    ("Tumble", "NodeSocketFloat", 1.5),          # turns over a whole flight, max
    ("Seed", "NodeSocketInt", 7),
]


def kit_collection():
    kit = bpy.data.collections.get("ShardKit")
    if kit is None:
        kit = bpy.data.collections.new("ShardKit")
        bpy.context.scene.collection.children.link(kit)
        for me in sorted((m for m in bpy.data.meshes if m.name.startswith("shard_")), key=lambda m: m.name):
            o = bpy.data.objects.new("K_" + me.name, me)
            kit.objects.link(o)
    lc = bpy.context.view_layer.layer_collection.children.get("ShardKit")
    if lc:
        lc.exclude = True
    return kit


def build_tree():
    ng = bpy.data.node_groups.get("ShardStream")
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new("ShardStream", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for name, st, dv in INPUTS:
        s = ng.interface.new_socket(name, in_out="INPUT", socket_type=st)
        s.default_value = dv
    nodes, links = ng.nodes, ng.links
    x = [0]

    def N(kind, **kw):
        n = nodes.new(kind)
        x[0] += 1
        n.location = ((x[0] % 12) * 200, -(x[0] // 12) * 260)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    gi = N("NodeGroupInput")
    G = lambda name: gi.outputs[name]
    out = N("NodeGroupOutput")

    def math(op, a, b=None, c=None):
        m = N("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                links.new(v, m.inputs[i])
        return m.outputs[0]

    idx = N("GeometryNodeInputIndex").outputs[0]

    def rnd(seed_off, lo=0.0, hi=1.0):
        r = N("FunctionNodeRandomValue", data_type="FLOAT")
        r.inputs["Min"].default_value = lo
        r.inputs["Max"].default_value = hi
        links.new(idx, r.inputs["ID"])
        links.new(math("ADD", G("Seed"), seed_off), r.inputs["Seed"])
        return r.outputs["Value"]

    time = N("GeometryNodeInputSceneTime")
    # t = fract(phase + frame / loop)
    t = math("FRACT", math("ADD", rnd(1), math("DIVIDE", time.outputs["Frame"], G("Loop Frames"))))

    ang = rnd(2, 0.0, 2 * math_pi)
    r0 = math("MULTIPLY", math("SQRT", rnd(3)), G("Break Radius"))
    r1 = N("ShaderNodeMapRange")
    links.new(rnd(4), r1.inputs["Value"])
    links.new(G("Pass Radius Min"), r1.inputs["To Min"])
    links.new(G("Pass Radius Max"), r1.inputs["To Max"])
    lerp = lambda a, b, f: math("ADD", a, math("MULTIPLY", math("SUBTRACT", b, a), f))
    r = lerp(r0, r1.outputs["Result"], t)
    y = lerp(G("Break Depth"), G("Pass Depth"), t)
    px = math("MULTIPLY", r, math("COSINE", ang))
    pz = math("MULTIPLY", math("MULTIPLY", r, math("SINE", ang)), G("Vertical Stretch"))
    pos = N("ShaderNodeCombineXYZ")
    links.new(px, pos.inputs[0]); links.new(y, pos.inputs[1]); links.new(pz, pos.inputs[2])

    pts = N("GeometryNodePoints")
    links.new(G("Count"), pts.inputs["Count"])
    links.new(pos.outputs[0], pts.inputs["Position"])

    coll = N("GeometryNodeCollectionInfo")
    coll.inputs["Collection"].default_value = kit_collection()
    coll.inputs["Separate Children"].default_value = True
    coll.inputs["Reset Children"].default_value = True

    pick = N("FunctionNodeRandomValue", data_type="INT")
    pick.inputs["Min"].default_value = 0      # 5.x: sockets are rebuilt per data type, look up by name
    pick.inputs["Max"].default_value = 23
    links.new(idx, pick.inputs["ID"])
    links.new(math("ADD", G("Seed"), 5), pick.inputs["Seed"])

    # rotation: random start + tumble about a random axis, proportional to t
    rot0 = N("FunctionNodeRandomValue", data_type="FLOAT_VECTOR")
    rot0.inputs["Max"].default_value = (2 * math_pi,) * 3
    links.new(idx, rot0.inputs["ID"])
    links.new(math("ADD", G("Seed"), 6), rot0.inputs["Seed"])
    e2r = N("FunctionNodeEulerToRotation")
    links.new(rot0.outputs["Value"], e2r.inputs[0])
    axis = N("FunctionNodeRandomValue", data_type="FLOAT_VECTOR")
    axis.inputs["Min"].default_value = (-1, -1, -1)
    axis.inputs["Max"].default_value = (1, 1, 1)
    links.new(idx, axis.inputs["ID"])
    links.new(math("ADD", G("Seed"), 7), axis.inputs["Seed"])
    spin = math("MULTIPLY", math("MULTIPLY", t, G("Tumble")), math("MULTIPLY", rnd(8, 0.2, 1.0), 2 * math_pi))
    aa = N("FunctionNodeAxisAngleToRotation")
    links.new(axis.outputs["Value"], aa.inputs["Axis"])
    links.new(spin, aa.inputs["Angle"])
    rr = N("FunctionNodeRotateRotation")
    links.new(e2r.outputs[0], rr.inputs["Rotation"])
    links.new(aa.outputs[0], rr.inputs["Rotate By"])

    size = lerp(G("Size Min"), G("Size Max"), math("POWER", rnd(9), G("Size Skew")))
    grow = N("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
    links.new(t, grow.inputs["Value"])
    links.new(G("Grow In"), grow.inputs["From Max"])
    scale = math("MULTIPLY", size, grow.outputs["Result"])

    inst = N("GeometryNodeInstanceOnPoints")
    links.new(pts.outputs[0], inst.inputs["Points"])
    links.new(coll.outputs[0], inst.inputs["Instance"])
    inst.inputs["Pick Instance"].default_value = True
    links.new(pick.outputs["Value"], inst.inputs["Instance Index"])
    links.new(rr.outputs[0], inst.inputs["Rotation"])
    links.new(scale, inst.inputs["Scale"])
    links.new(inst.outputs[0], out.inputs[0])
    return ng


math_pi = math.pi


def build():
    for o in [o for o in bpy.data.objects if o.name.startswith("S") and o.name[1:].isdigit()]:
        bpy.data.objects.remove(o)
    old = bpy.data.collections.get("Shards")
    if old and not old.objects:
        bpy.data.collections.remove(old)
    ng = build_tree()
    me = bpy.data.meshes.get("ShardStreamMesh") or bpy.data.meshes.new("ShardStreamMesh")
    ob = bpy.data.objects.get("ShardStream")
    if ob is None:
        ob = bpy.data.objects.new("ShardStream", me)
        bpy.context.scene.collection.objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    ob.modifiers.new("ShardStream", "NODES").node_group = ng

    sc = bpy.context.scene
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, 600

    # bigger, blinding core
    core = bpy.data.objects["Core"]
    core.scale = (2.6,) * 3
    em = next(n for n in core.active_material.node_tree.nodes if n.type == "EMISSION")
    em.inputs["Strength"].default_value = 1500.0
    print("ShardStream built", flush=True)


build()
