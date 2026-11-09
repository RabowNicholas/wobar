"""MAKYO - audio reactivity. Run inside makyo_shards_v2.blend after makyo_motion.py.

    exec(open(".../makyo_audio.py").read())      # live via MCP

MAKYO_CTRL (empty) carries the baked curves from makyo_curves.json as keyed custom props, plus
static switches/strengths you can edit in its Object Properties > Custom Properties:
  snare_on / kick_on / vortex_on / hats_on   1 = layer active, 0 = layer off (snare off = light full)
  snare_floor   light level between hits (ember)
  kick_surge    frames of stream travel per kick
  vortex_turn   seconds per full turn at full 808
  dust_density  share of dust specks that glint per hat hit (scaled up by hat brightness)
Layers:
  snare -> core emission, core light, haze glow, edge glow
  kick  -> ShardStream / HatDust stream time
  808   -> both streams rotate about the view axis
  hats  -> HatDust: per-hit random specks glint bone -> white
"""
import bpy, json, math
from bpy_extras import anim_utils

CURVES = "/Volumes/music/blender/makyo_assets/makyo_curves.json"
MASTER = "/Volumes/music/sessions/WIP (ACTIVE)/yagami Project/11326_makyo.wav"
STATIC = dict(snare_on=1.0, kick_on=1.0, vortex_on=1.0, hats_on=1.0,
              snare_floor=0.08, kick_light=0.35, kick_surge=7.5, break_on=1.0, vortex_turn=12.0, dust_density=0.05)
KEYED = ("snare", "kick_acc", "kick_idx", "kick_vel", "kick_flash", "vortex_acc", "low", "hat_env", "hat_idx", "hat_bright",
         "sec_density", "stream_base", "sec_glow", "sec_core", "intact", "crack", "drop_flash", "jolt_x", "jolt_z", "jolt_r")


def lin(h):
    h = h.lstrip("#"); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)


def ctrl_object(C):
    ob = bpy.data.objects.get("MAKYO_CTRL")
    if ob is None:
        ob = bpy.data.objects.new("MAKYO_CTRL", None)
        bpy.context.scene.collection.objects.link(ob)
    for k, v in STATIC.items():
        if k not in ob:
            ob[k] = v
    for k in KEYED:
        ob[k] = float(C[k][0])
    if ob.animation_data and ob.animation_data.action:
        bpy.data.actions.remove(ob.animation_data.action)
    for k in KEYED:
        ob.keyframe_insert(f'["{k}"]', frame=1)
    act = ob.animation_data.action
    cb = anim_utils.action_get_channelbag_for_slot(act, ob.animation_data.action_slot)
    n = C["frames"]
    for fc in cb.fcurves:
        k = fc.data_path[2:-2]
        vals = C[k]
        kp = fc.keyframe_points
        kp.add(n - len(kp))
        co = [0.0] * (2 * n)
        for i in range(n):
            co[2 * i], co[2 * i + 1] = i + 1, vals[i]
        kp.foreach_set("co", co)
        interp = "CONSTANT" if k in ("hat_idx", "kick_idx", "kick_vel") else "LINEAR"
        for p in kp:
            p.interpolation = interp
        fc.update()
    return ob


def drive(owner, path, expr, vars_, index=-1):
    try:
        owner.driver_remove(path, index)
    except TypeError:
        pass
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for v in list(d.variables):
        d.variables.remove(v)
    for name, prop in vars_:
        var = d.variables.new()
        var.name = name
        var.type = "SINGLE_PROP"
        var.targets[0].id_type = "OBJECT"
        var.targets[0].id = bpy.data.objects["MAKYO_CTRL"]
        var.targets[0].data_path = f'["{prop}"]'
    d.expression = expr
    return fc


LIGHT = ("(fl + (1 - fl) * max(s, kl * kf * ko, df)) if on > 0.5 else 1.0",
         [("s", "snare"), ("fl", "snare_floor"), ("on", "snare_on"), ("df", "drop_flash"),
          ("kf", "kick_flash"), ("kl", "kick_light"), ("ko", "kick_on")])


def wire_light():
    expr, v = LIGHT
    core = bpy.data.objects["Core"]
    em = next(n for n in core.active_material.node_tree.nodes if n.type == "EMISSION")
    drive(em.inputs["Strength"], "default_value", f"1500 * ({expr}) ** 2", v)
    drive(bpy.data.objects["CoreLight"].data, "energy", f"3e6 * ({expr})", v)
    drive(bpy.data.materials["HazeVol"].node_tree.nodes["GlowStrength"].inputs[1], "default_value",
          f"0.06 * ({expr})", v)
    drive(bpy.data.materials["MakyoEdge"].node_tree.nodes["EdgeStrength"].inputs[1], "default_value",
          f"45 * ({expr})", v)


def wire_kick_rim(watts=8000.0):
    """Soft muted-orange disc light behind the camera, flashed by each kick: the light the near
    mirrors physically reflect (option B, 2026-11-03). Strength is in the expression - a driver
    variable on a custom prop added after the depsgraph was built read 0 here."""
    import math as _m
    ld = bpy.data.lights.get("KickRim") or bpy.data.lights.new("KickRim", "AREA")
    ld.shape, ld.size, ld.color = "DISK", 6.0, lin("#C17A4E")
    ob = bpy.data.objects.get("KickRim") or bpy.data.objects.new("KickRim", ld)
    if ob.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(ob)
    ob.location, ob.rotation_euler = (0, -6, 1.5), (_m.radians(90), 0, 0)   # faces +Y, into the field
    drive(ld, "energy", f"{watts} * kf * ko", [("kf", "kick_flash"), ("ko", "kick_on")])


def stream_controls(ng):
    """Swap Scene Time for a driven StreamTime value; add the vortex rotation. Idempotent."""
    nodes, links = ng.nodes, ng.links
    st = nodes.get("StreamTime")
    if st is None:
        st = nodes.new("ShaderNodeValue"); st.name = st.label = "StreamTime"
        stime = next(n for n in nodes if n.bl_idname == "GeometryNodeInputSceneTime")
        for l in list(links):
            if l.from_node == stime:
                links.new(st.outputs[0], l.to_socket)
        nodes.remove(stime)
    drive(st.outputs[0], "default_value", "frame + (sz * ka if on > 0.5 else 0)",
          [("ka", "kick_acc"), ("sz", "kick_surge"), ("on", "kick_on")])

    vx = nodes.get("Vortex")
    if vx is None:
        vx = nodes.new("ShaderNodeValue"); vx.name = vx.label = "Vortex"
        pts = next(n for n in nodes if n.bl_idname == "GeometryNodePoints")
        pos_link = next(l for l in links if l.to_node == pts and l.to_socket.name == "Position")
        vr = nodes.new("ShaderNodeVectorRotate"); vr.rotation_type = "Y_AXIS"; vr.name = "VortexRotate"
        links.new(pos_link.from_socket, vr.inputs["Vector"])
        links.new(vx.outputs[0], vr.inputs["Angle"])
        links.new(vr.outputs[0], pts.inputs["Position"])
        inst = next(n for n in nodes if n.bl_idname == "GeometryNodeInstanceOnPoints")
        rot_link = next(l for l in links if l.to_node == inst and l.to_socket.name == "Rotation")
        aa = nodes.new("FunctionNodeAxisAngleToRotation")
        aa.inputs["Axis"].default_value = (0, 1, 0)
        links.new(vx.outputs[0], aa.inputs["Angle"])
        rr = nodes.new("FunctionNodeRotateRotation"); rr.name = "VortexRotRot"
        rr.rotation_space = "GLOBAL"
        links.new(rot_link.from_socket, rr.inputs["Rotation"])
        links.new(aa.outputs[0], rr.inputs["Rotate By"])
        links.new(rr.outputs[0], inst.inputs["Rotation"])
    drive(vx.outputs[0], "default_value", "(va * 6.2832 / vt) if on > 0.5 else 0",
          [("va", "vortex_acc"), ("vt", "vortex_turn"), ("on", "vortex_on")])


def set_input(ob, name, v):
    mod = ob.modifiers[0]
    ident = next(i.identifier for i in mod.node_group.interface.items_tree
                 if getattr(i, "in_out", None) == "INPUT" and i.name == name)
    getattr(mod.properties.inputs, ident).value = v


def dust_material():
    m = bpy.data.materials.get("DustGlint")
    if m:
        return m
    m = bpy.data.materials.new("DustGlint")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = "INSTANCER"; at.attribute_name = "glint"
    em = nt.nodes.new("ShaderNodeEmission")
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.name = "DustColour"
    mix.inputs["A"].default_value = (*lin("#C7BBA6"), 1)
    mix.inputs["B"].default_value = (1, 1, 1, 1)
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 60.0
    k.name = "DustStrength"
    nt.links.new(at.outputs["Fac"], k.inputs[0])
    nt.links.new(mix.outputs["Result"], em.inputs["Color"])
    nt.links.new(k.outputs[0], em.inputs["Strength"])
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (0.05, 0.04, 0.035, 1)
    bs.inputs["Metallic"].default_value = 1.0
    bs.inputs["Roughness"].default_value = 0.2
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(bs.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    drive(mix.inputs["Factor"], "default_value", "max(0, (hb - 0.4) / 0.4)", [("hb", "hat_bright")])
    return m


def dust_layer():
    src = bpy.data.node_groups["ShardStream"]
    old = bpy.data.node_groups.get("HatDust")
    if old:
        bpy.data.node_groups.remove(old)
    ng = src.copy(); ng.name = "HatDust"
    nodes, links = ng.nodes, ng.links
    me = bpy.data.meshes.get("speck")
    if me is None:
        me = bpy.data.meshes["shard_3"].copy(); me.name = "speck"
    mat = dust_material()
    me.materials.clear(); me.materials.append(mat); me.materials.append(mat)
    speck = bpy.data.objects.get("K_speck") or bpy.data.objects.new("K_speck", me)
    coll = next(n for n in nodes if n.bl_idname == "GeometryNodeCollectionInfo")
    oi = nodes.new("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = speck
    oi.transform_space = "RELATIVE"
    inst = next(n for n in nodes if n.bl_idname == "GeometryNodeInstanceOnPoints")
    links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
    nodes.remove(coll)
    inst.inputs["Pick Instance"].default_value = False
    idx = nodes.new("GeometryNodeInputIndex")
    hidx = nodes.new("ShaderNodeValue"); hidx.name = "HatIdx"
    henv = nodes.new("ShaderNodeValue"); henv.name = "HatEnv"
    dens = nodes.new("ShaderNodeValue"); dens.name = "DustDensity"
    rv = nodes.new("FunctionNodeRandomValue"); rv.data_type = "FLOAT"
    links.new(idx.outputs[0], rv.inputs["ID"]); links.new(hidx.outputs[0], rv.inputs["Seed"])
    cmp = nodes.new("FunctionNodeCompare"); cmp.data_type = "FLOAT"; cmp.operation = "LESS_THAN"
    links.new(rv.outputs["Value"], cmp.inputs["A"]); links.new(dens.outputs[0], cmp.inputs["B"])
    mul = nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    links.new(cmp.outputs[0], mul.inputs[0]); links.new(henv.outputs[0], mul.inputs[1])
    sto = nodes.new("GeometryNodeStoreNamedAttribute"); sto.data_type = "FLOAT"; sto.domain = "INSTANCE"
    sto.inputs["Name"].default_value = "glint"
    out = next(n for n in nodes if n.bl_idname == "NodeGroupOutput")
    links.new(inst.outputs[0], sto.inputs["Geometry"])
    links.new(mul.outputs[0], sto.inputs["Value"])
    links.new(sto.outputs[0], out.inputs[0])
    drive(hidx.outputs[0], "default_value", "hi", [("hi", "hat_idx")])
    drive(henv.outputs[0], "default_value", "he if on > 0.5 else 0", [("he", "hat_env"), ("on", "hats_on")])
    drive(dens.outputs[0], "default_value", "dd * (0.3 + 1.7 * hb)", [("dd", "dust_density"), ("hb", "hat_bright")])
    stream_controls(ng)

    ob = bpy.data.objects.get("HatDust")
    if ob is None:
        ob = bpy.data.objects.new("HatDust", bpy.data.meshes.new("HatDustMesh"))
        bpy.context.scene.collection.objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    ob.modifiers.new("HatDust", "NODES").node_group = ng
    for k, v in (("Count", 7000), ("Size Min", 0.015), ("Size Max", 0.05), ("Size Skew", 1.5),
                 ("Seed", 101), ("Pass Radius Min", 0.6), ("Pass Radius Max", 6.0), ("Tumble", 3.0)):
        set_input(ob, k, v)


def main():
    C = json.load(open(CURVES))
    ctrl_object(C)
    wire_light()
    wire_kick_rim()
    stream_controls(bpy.data.node_groups["ShardStream"])
    dust_layer()
    sc = bpy.context.scene
    sc.render.fps = C["fps"]
    sc.frame_start, sc.frame_end = 1, C["frames"]
    if not sc.sequence_editor:
        sc.sequence_editor_create()
    se = sc.sequence_editor
    strips = getattr(se, "strips", None)
    if strips is None:
        strips = se.sequences
    if not any(s.name == "MAKYO_master" for s in strips):
        strips.new_sound("MAKYO_master", MASTER, 1, 1)
    sc.sync_mode = "AUDIO_SYNC"
    print("audio wired", flush=True)


main()
