"""MAKYO - section controls + the intact-mirror opening. Run in makyo_shards_v4.blend after
makyo_audio.py (needs its drive() and ctrl_object() in the exec namespace) and makyo_break.py.

Curves (makyo_curves.json, keyed onto MAKYO_CTRL by ctrl_object): sec_density, sec_speed ->
stream_base, sec_glow, sec_core, intact, crack; st_drop / drop_frame are constants.

ShardStream: StreamTime = stream_base + surge * kick_acc (section speed integrated, kicks on top).
Each shard's scale x visibility:
  density  - a per-shard random below sec_density (soft edge), so sections thin the field;
  reveal   - nothing before the drop; after it, a shard shows if it was behind the mirror plane
             (y > Mirror Depth) at the drop, or has respawned since. The pieces just behind the
             plane appear at it and fly at you: the mirror shattering.
IntactMirror: dark polished disc in front of the core until the drop. Voronoi cracks open cell by
cell with each intro snare (crack), and leak the core's light (pulses with the snare light).
"""
import bpy, math

MIRROR_Y, MIRROR_R = 14.0, 7.0   # close and big: the shatter reveals near pieces at once
KEYS_NEW = ("sec_density", "stream_base", "sec_glow", "sec_core", "intact", "crack")


def lin(h):
    h = h.lstrip("#"); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)


def ensure_input(ng, md, name, dv):
    if name not in {i.name for i in ng.interface.items_tree if getattr(i, "in_out", None) == "INPUT"}:
        s = ng.interface.new_socket(name, in_out="INPUT", socket_type="NodeSocketFloat")
        s.default_value = dv
    ident = next(i.identifier for i in ng.interface.items_tree
                 if getattr(i, "in_out", None) == "INPUT" and i.name == name)
    getattr(md.properties.inputs, ident).value = dv


def stream_time_drivers():
    for ng in (bpy.data.node_groups["ShardStream"], bpy.data.node_groups["HatDust"]):
        drive(ng.nodes["StreamTime"].outputs[0], "default_value", "sb + (sz * ka if on > 0.5 else 0)",
              [("sb", "stream_base"), ("ka", "kick_acc"), ("sz", "kick_surge"), ("on", "kick_on")])


def visibility(C):
    ob = bpy.data.objects["ShardStream"]; md = ob.modifiers[0]; ng = md.node_group
    nodes, links = ng.nodes, ng.links
    if nodes.get("SecDensity"):
        print("visibility already built"); return
    ensure_input(ng, md, "Mirror Depth", MIRROR_Y)
    gi = next(n for n in nodes if n.bl_idname == "NodeGroupInput")
    G = lambda n: gi.outputs[n]

    def val(name):
        v = nodes.new("ShaderNodeValue"); v.name = v.label = name; return v

    def m(op, a, b=None):
        n = nodes.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                links.new(x, n.inputs[i])
        return n.outputs[0]

    dens, intact, std = val("SecDensity"), val("Intact"), val("STDrop")
    drive(dens.outputs[0], "default_value", "d", [("d", "sec_density")])
    drive(intact.outputs[0], "default_value", "i", [("i", "intact")])
    std.outputs[0].default_value = C["st_drop"]

    idx = next(n for n in nodes if n.bl_idname == "GeometryNodeInputIndex").outputs[0]
    r = nodes.new("FunctionNodeRandomValue"); r.data_type = "FLOAT"; r.inputs["Seed"].default_value = 31
    links.new(idx, r.inputs["ID"])
    dvis = m("MINIMUM", m("MAXIMUM", m("DIVIDE", m("SUBTRACT", dens.outputs[0], r.outputs["Value"]), 0.04), 0.0), 1.0)

    fr = next(n for n in nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "FRACT")
    add = next(l.from_node for l in links if l.to_node == fr)                 # phase + ST / loop
    phase = next(l.from_socket for l in links if l.to_node == add and l.to_socket == add.inputs[0])
    st = nodes["StreamTime"].outputs[0]
    t_drop = m("FRACT", m("ADD", phase, m("DIVIDE", std.outputs[0], G("Loop Frames"))))
    y_drop = m("ADD", G("Break Depth"), m("MULTIPLY", m("SUBTRACT", G("Pass Depth"), G("Break Depth")), t_drop))
    behind = m("GREATER_THAN", y_drop, G("Mirror Depth"))
    elapsed = m("DIVIDE", m("SUBTRACT", st, std.outputs[0]), G("Loop Frames"))
    wrapped = m("GREATER_THAN", elapsed, m("SUBTRACT", 1.0, t_drop))
    reveal = m("MULTIPLY", m("SUBTRACT", 1.0, intact.outputs[0]), m("MAXIMUM", behind, wrapped))
    vis = m("MULTIPLY", dvis, reveal)

    inst = next(n for n in nodes if n.bl_idname == "GeometryNodeInstanceOnPoints" and n.name != "FragmentInstances")
    keep_mul = next(l.from_node for l in links if l.to_node == inst and l.to_socket.name == "Scale")
    scale_src = next(l.from_socket for l in links if l.to_node == keep_mul and l.to_socket == keep_mul.inputs[0])
    vscale = m("MULTIPLY", scale_src, vis)
    for l in [l for l in links if l.from_socket == scale_src and l.to_node != vscale.node]:
        ts = l.to_socket; links.remove(l); links.new(vscale, ts)
    print("visibility built; invalid", sum(1 for l in links if not l.is_valid))


def glow_core():
    expr, v = LIGHT                      # from makyo_audio.py's namespace
    drive(bpy.data.materials["HazeVol"].node_tree.nodes["GlowStrength"].inputs[1], "default_value",
          f"0.06 * ({expr}) * sg", v + [("sg", "sec_glow")])
    core = bpy.data.objects["Core"]
    for i in range(3):
        drive(core, "scale", "2.6 * c", [("c", "sec_core")], index=i)


def crack_material():
    m = bpy.data.materials.get("IntactMirror")
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new("IntactMirror"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes.new; L = nt.links.new
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin("#6F4E3A"), 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.07
    tc = N("ShaderNodeTexCoord")
    vor = N("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 0.22
    vor2 = N("ShaderNodeTexVoronoi"); vor2.feature = "F1"; vor2.inputs["Scale"].default_value = 0.22
    L(tc.outputs["Object"], vor.inputs["Vector"]); L(tc.outputs["Object"], vor2.inputs["Vector"])
    # a cell's crack opens once the crack curve passes the cell's random value
    cellr = N("ShaderNodeSeparateColor"); L(vor2.outputs["Color"], cellr.inputs[0])
    crack = N("ShaderNodeValue"); crack.name = "Crack"
    open_ = N("ShaderNodeMath"); open_.operation = "LESS_THAN"
    L(cellr.outputs[0], open_.inputs[0]); L(crack.outputs[0], open_.inputs[1])
    line = N("ShaderNodeMapRange"); line.inputs["From Min"].default_value = 0.0
    line.inputs["From Max"].default_value = 0.035; line.inputs["To Min"].default_value = 1.0
    line.inputs["To Max"].default_value = 0.0
    L(vor.outputs["Distance"], line.inputs["Value"])
    mask = N("ShaderNodeMath"); mask.operation = "MULTIPLY"
    L(line.outputs["Result"], mask.inputs[0]); L(open_.outputs[0], mask.inputs[1])
    light = N("ShaderNodeValue"); light.name = "CrackLight"
    strength = N("ShaderNodeMath"); strength.operation = "MULTIPLY"
    L(mask.outputs[0], strength.inputs[0]); L(light.outputs[0], strength.inputs[1])
    ramp = N("ShaderNodeValToRGB"); e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (*lin("#A6633D"), 1)
    e[1].position, e[1].color = 1.0, (*lin("#C7BBA6"), 1)
    L(line.outputs["Result"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], b.inputs["Emission Color"]); L(strength.outputs[0], b.inputs["Emission Strength"])
    drive(crack.outputs[0], "default_value", "c", [("c", "crack")])
    drive(light.outputs[0], "default_value", "60 * ((fl + (1 - fl) * max(s, kl * kf * ko)) if on > 0.5 else 1.0)",
          [("s", "snare"), ("fl", "snare_floor"), ("on", "snare_on"),
           ("kf", "kick_flash"), ("kl", "kick_light"), ("ko", "kick_on")])
    return m


def intact_mirror():
    ob = bpy.data.objects.get("IntactMirror")
    if ob is None:
        bpy.ops.mesh.primitive_circle_add(vertices=96, radius=1.0, fill_type="NGON",
                                          location=(0, MIRROR_Y, 0), rotation=(math.radians(90), 0, 0))
        ob = bpy.context.active_object; ob.name = "IntactMirror"
        # slightly irregular rim so it reads as a found object, not a CG disc
        import random
        rng = random.Random(3)
        for v in ob.data.vertices:
            if v.co.length > 0.5:
                v.co *= 1 + rng.uniform(-0.03, 0.03)
    ob.scale = (MIRROR_R,) * 3
    ob.data.materials.clear(); ob.data.materials.append(crack_material())
    for i in range(3):
        drive(ob, "scale", f"{MIRROR_R} * i", [("i", "intact")], index=i)
    ob.visible_shadow = True


def main(C):
    stream_time_drivers()
    visibility(C)
    glow_core()
    intact_mirror()
    print("sections built", flush=True)
