"""MAKYO - kick breaks the nearest shards. Run inside makyo_shards_v3.blend after makyo_audio.py.

A simulation zone remembers, per shard, whether a kick has shattered it:
  break fires when MAKYO_CTRL kick_idx steps (a kick lands) and the shard is inside Break Zone
  (0.3 m .. Break Zone m in front of the camera) and not already broken;
  a broken shard stays broken until it wraps back to the break point.
Broken shards hide; each is replaced by Fragments smaller pieces that burst outward from it
(speed x kick velocity, slowed by drag), spin faster, and keep riding the parent's path past you.

The sim must run from the scene's start frame: play through, or bake (simulation_nodes_cache_bake).
"""
import bpy

NEW_INPUTS = [
    ("Break Zone", "NodeSocketFloat", 9.0),
    ("Fragments", "NodeSocketInt", 6),
    ("Frag Speed", "NodeSocketFloat", 5.0),     # m/s at kick velocity 1
    ("Frag Drag", "NodeSocketFloat", 0.35),     # s: burst speed decays with this time constant
    ("Frag Scale", "NodeSocketFloat", 0.42),
    ("Frag Spin", "NodeSocketFloat", 1.2),      # extra turns per second right after the hit, decays with drag
    ("Toward Camera", "NodeSocketFloat", 0.35),  # bias of the burst along the flight direction
]


def build(ng):
    nodes, links = ng.nodes, ng.links
    if nodes.get("BreakSimIn"):
        print("break already built")
        return
    have = {i.name for i in ng.interface.items_tree if getattr(i, "in_out", None) == "INPUT"}
    for name, st, dv in NEW_INPUTS:
        if name not in have:
            s = ng.interface.new_socket(name, in_out="INPUT", socket_type=st)
            s.default_value = dv
    gi = next(n for n in nodes if n.bl_idname == "NodeGroupInput")
    G = lambda name: gi.outputs[name]
    pos_x = [2600]

    def N(kind, **kw):
        n = nodes.new(kind)
        pos_x[0] += 60
        n.location = (pos_x[0], -1400 - (pos_x[0] % 600))
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def math(op, a, b=None):
        m = N("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                links.new(v, m.inputs[i])
        return m.outputs[0]

    def named(name, dt="FLOAT"):
        n = N("GeometryNodeInputNamedAttribute", data_type=dt)
        n.inputs["Name"].default_value = name
        return n.outputs["Attribute"]

    def store(geo, name, val, dt="FLOAT"):
        s = N("GeometryNodeStoreNamedAttribute", data_type=dt, domain="POINT")
        s.name = "Store_" + name
        s.inputs["Name"].default_value = name
        links.new(geo, s.inputs["Geometry"])
        links.new(val, s.inputs["Value"])
        return s.outputs["Geometry"]

    pts = next(n for n in nodes if n.bl_idname == "GeometryNodePoints")
    inst = next(n for n in nodes if n.bl_idname == "GeometryNodeInstanceOnPoints")
    vr = nodes["VortexRotate"]
    t = next(n for n in nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "FRACT").outputs[0]
    scale_src = next(l.from_socket for l in links if l.to_node == inst and l.to_socket.name == "Scale")
    rot_src = nodes["VortexRotRot"].outputs[0]
    pick_src = next(l.from_socket for l in links if l.to_node == inst and l.to_socket.name == "Instance Index")

    kidx = N("ShaderNodeValue"); kidx.name = kidx.label = "KickIdx"
    kvel = N("ShaderNodeValue"); kvel.name = kvel.label = "KickVel"
    bon = N("ShaderNodeValue"); bon.name = bon.label = "BreakOn"
    frame = N("GeometryNodeInputSceneTime").outputs["Frame"]

    si = N("GeometryNodeSimulationInput"); si.name = "BreakSimIn"
    so = N("GeometryNodeSimulationOutput"); so.name = "BreakSimOut"
    si.pair_with_output(so)
    links.new(pts.outputs[0], si.inputs["Geometry"])

    # current analytic state of every shard
    sp = N("GeometryNodeSetPosition")
    links.new(si.outputs["Geometry"], sp.inputs["Geometry"])
    links.new(vr.outputs[0], sp.inputs["Position"])
    sep = N("ShaderNodeSeparateXYZ")
    links.new(vr.outputs[0], sep.inputs[0])
    y = sep.outputs["Y"]

    broken, prev_t, kprev = named("broken"), named("prev_t"), named("kprev")
    break_f, break_v = named("break_f"), named("break_v")
    wrap = math("LESS_THAN", t, prev_t)
    event = math("GREATER_THAN", kidx.outputs[0], kprev)
    near = math("MULTIPLY", math("LESS_THAN", y, G("Break Zone")), math("GREATER_THAN", y, 0.3))
    cond = math("MULTIPLY", math("MULTIPLY", event, near), math("SUBTRACT", 1.0, broken))
    cond = math("MULTIPLY", math("MULTIPLY", cond, math("SUBTRACT", 1.0, wrap)), bon.outputs[0])
    broken_next = math("MULTIPLY", math("SUBTRACT", 1.0, wrap), math("MAXIMUM", broken, cond))
    bf_next = math("ADD", break_f, math("MULTIPLY", cond, math("SUBTRACT", frame, break_f)))
    bv_next = math("ADD", break_v, math("MULTIPLY", cond, math("SUBTRACT", kvel.outputs[0], break_v)))

    # read-before-write order: break_f/break_v use the old `broken`, everything uses the old prev_t/kprev
    g = store(sp.outputs[0], "break_f", bf_next)
    g = store(g, "break_v", bv_next)
    g = store(g, "broken", broken_next)
    g = store(g, "prev_t", t)
    g = store(g, "kprev", kidx.outputs[0])
    links.new(g, so.inputs["Geometry"])

    # parent attributes the fragments need after duplication
    g = store(so.outputs["Geometry"], "pscale", scale_src)
    g = store(g, "prot", rot_src, "QUATERNION")
    sid = N("GeometryNodeInputIndex").outputs[0]
    g = store(g, "sid", sid, "INT")
    after = g

    # whole shards: hide the broken ones
    links.new(after, inst.inputs["Points"])
    keep = math("SUBTRACT", 1.0, named("broken"))
    links.new(math("MULTIPLY", scale_src, keep), inst.inputs["Scale"])

    # fragments
    dup = N("GeometryNodeDuplicateElements"); dup.domain = "POINT"
    links.new(after, dup.inputs["Geometry"])
    links.new(math("MULTIPLY", named("broken"), G("Fragments")), dup.inputs["Amount"])
    di = dup.outputs["Duplicate Index"]
    fid = math("ADD", math("MULTIPLY", named("sid", "INT"), 37.0), di)

    def frnd(seed, lo=0.0, hi=1.0, vec=False):
        r = N("FunctionNodeRandomValue", data_type="FLOAT_VECTOR" if vec else "FLOAT")
        r.inputs["Min"].default_value = (lo,) * 3 if vec else lo
        r.inputs["Max"].default_value = (hi,) * 3 if vec else hi
        links.new(fid, r.inputs["ID"])
        r.inputs["Seed"].default_value = seed
        return r.outputs["Value"]

    dt = math("MAXIMUM", math("DIVIDE", math("SUBTRACT", frame, named("break_f")), 30.0), 0.0)
    drag = G("Frag Drag")
    travel = math("MULTIPLY", drag, math("SUBTRACT", 1.0, math("EXPONENT", math("DIVIDE", math("MULTIPLY", dt, -1.0), drag))))
    speed = math("MULTIPLY", math("MULTIPLY", G("Frag Speed"), named("break_v")), frnd(11, 0.4, 1.3))

    # burst direction: random sphere + radial outward + along the flight (toward camera, -Y)
    rs = N("ShaderNodeVectorMath", operation="NORMALIZE")
    links.new(frnd(12, -1.0, 1.0, vec=True), rs.inputs[0])
    ppos = N("GeometryNodeInputPosition").outputs[0]
    rad = N("ShaderNodeVectorMath", operation="MULTIPLY")
    links.new(ppos, rad.inputs[0]); rad.inputs[1].default_value = (1, 0, 1)
    radn = N("ShaderNodeVectorMath", operation="NORMALIZE"); links.new(rad.outputs[0], radn.inputs[0])
    flight = N("ShaderNodeCombineXYZ")
    links.new(math("MULTIPLY", G("Toward Camera"), -1.0), flight.inputs[1])
    a1 = N("ShaderNodeVectorMath", operation="ADD"); links.new(rs.outputs[0], a1.inputs[0]); links.new(radn.outputs[0], a1.inputs[1])
    a2 = N("ShaderNodeVectorMath", operation="SCALE"); links.new(a1.outputs[0], a2.inputs[0]); a2.inputs["Scale"].default_value = 0.5
    a3 = N("ShaderNodeVectorMath", operation="ADD"); links.new(a2.outputs[0], a3.inputs[0]); links.new(flight.outputs[0], a3.inputs[1])
    dirn = N("ShaderNodeVectorMath", operation="NORMALIZE"); links.new(a3.outputs[0], dirn.inputs[0])
    off = N("ShaderNodeVectorMath", operation="SCALE")
    links.new(dirn.outputs[0], off.inputs[0]); links.new(math("MULTIPLY", speed, travel), off.inputs["Scale"])
    fsp = N("GeometryNodeSetPosition")
    links.new(dup.outputs["Geometry"], fsp.inputs["Geometry"])
    links.new(off.outputs[0], fsp.inputs["Offset"])

    # fragment rotation: parent rotation + a spin that decays with drag (angle = spin * travel)
    axis = N("ShaderNodeVectorMath", operation="NORMALIZE"); links.new(frnd(13, -1.0, 1.0, vec=True), axis.inputs[0])
    ang = math("MULTIPLY", math("MULTIPLY", G("Frag Spin"), 6.2832), math("ADD", travel, math("MULTIPLY", dt, 0.4)))
    aa = N("FunctionNodeAxisAngleToRotation"); links.new(axis.outputs[0], aa.inputs["Axis"]); links.new(ang, aa.inputs["Angle"])
    r0 = N("FunctionNodeRandomValue", data_type="FLOAT_VECTOR"); r0.inputs["Max"].default_value = (6.2832,) * 3
    links.new(fid, r0.inputs["ID"]); r0.inputs["Seed"].default_value = 14
    e2r = N("FunctionNodeEulerToRotation"); links.new(r0.outputs["Value"], e2r.inputs[0])
    rr = N("FunctionNodeRotateRotation"); rr.rotation_space = "LOCAL"
    links.new(e2r.outputs[0], rr.inputs["Rotation"]); links.new(aa.outputs[0], rr.inputs["Rotate By"])

    fscale = math("MULTIPLY", math("MULTIPLY", named("pscale"), G("Frag Scale")), frnd(15, 0.55, 1.25))
    pick = N("FunctionNodeRandomValue", data_type="INT")
    pick.inputs["Min"].default_value = 0; pick.inputs["Max"].default_value = 23
    links.new(fid, pick.inputs["ID"]); pick.inputs["Seed"].default_value = 16

    coll = next(l.from_socket for l in links if l.to_node == inst and l.to_socket.name == "Instance")
    finst = N("GeometryNodeInstanceOnPoints"); finst.name = "FragmentInstances"
    links.new(fsp.outputs[0], finst.inputs["Points"])
    links.new(coll, finst.inputs["Instance"])
    finst.inputs["Pick Instance"].default_value = True
    links.new(pick.outputs["Value"], finst.inputs["Instance Index"])
    links.new(rr.outputs[0], finst.inputs["Rotation"])
    links.new(fscale, finst.inputs["Scale"])

    out = next(n for n in nodes if n.bl_idname == "NodeGroupOutput")
    join = N("GeometryNodeJoinGeometry")
    links.new(inst.outputs[0], join.inputs[0])
    links.new(finst.outputs[0], join.inputs[0])
    links.new(join.outputs[0], out.inputs[0])

    drive_ns = globals().get("drive")
    drive_ns(kidx.outputs[0], "default_value", "k", [("k", "kick_idx")])
    drive_ns(kvel.outputs[0], "default_value", "v", [("v", "kick_vel")])
    drive_ns(bon.outputs[0], "default_value", "b * kon", [("b", "break_on"), ("kon", "kick_on")])
    # sockets added to an existing group arrive on its modifiers as 0, not the socket default
    for ob in bpy.data.objects:
        for md in ob.modifiers:
            if md.type == "NODES" and md.node_group == ng:
                for it in ng.interface.items_tree:
                    if getattr(it, "in_out", None) == "INPUT" and it.name in dict((n, 1) for n, _, _ in NEW_INPUTS):
                        getattr(md.properties.inputs, it.identifier).value = it.default_value
    print("break system built", flush=True)
