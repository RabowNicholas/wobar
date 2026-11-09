"""The rolling layer (I-7, 2026-10-19): chains of light driven by the two pluck stems.

Decided (Nick): each pluck note lights one small form, the next note the next one along; a run per cycle,
reset every cycle, brightness from the note's level. One form class each, never the kick's or snare's.

  ABGRUND - runs DOWN the hanging fine roots (`BankRootsFine`, plus the landslide's `SlideRoots`): each
            half-note burst (4-6 notes ~70 ms apart) is a streak running down a root, top to bottom. Each
            cycle picks a root or two in front of the camera.
  GRUND   - runs AWAY through the tall grass: each beat's four 16ths light bands of grass cages at 8, 12,
            16 and 20 m ahead (camera depth). The grass cages leave the snare for this; their lights go
            (the 16ths are continuous - lights on them would read as a constant glow).

Notes: hohlweg_assets/audio/hohlweg_pluck_notes.json ([t, vel, cycle, step], master seconds; ABGRUND's
857 ms lag already corrected) from scripts/post/pluck_notes.py.

On FORM_CTRL: stepped keys pa_t{k}/pa_v{k} (ABGRUND step k), pa_cycle; pg_t{k}/pg_v{k}, pg_cycle; driven
envelopes pa_e{k}, pg_e{k} (same shape as the drum flashes, fade `pl_fade`) and pa_emax for the light.

    ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy, bmesh, json, math, random
import numpy as np
from mathutils import Vector

CTRL = "FORM_CTRL"
NOTES = "/Volumes/music/blender/hohlweg_assets/audio/hohlweg_pluck_notes.json"
NA, NG = 6, 4                      # steps per cycle: ABGRUND burst, GRUND beat
KNOBS = dict(pl_fade=0.18, pa_peak=0.9, pa_light_w=8.0, pg_peak=0.7, pa_count=2.0,
             pg_d0=8.0, pg_step=4.0, pg_half=1.6)
ROOT_SPAN = (780.0, 1610.0)        # metres along: the ABGRUND pluck plays 3:05 -> 7:35
FPS = 24


def _fcurve(ob, prop):
    ad = ob.animation_data
    for L in ad.action.layers:
        for st in L.strips:
            for fc in st.channelbag(ad.action_slot).fcurves:
                if fc.data_path == '["%s"]' % prop:
                    return fc


def _keys(ob, prop, rows, init):
    ob[prop] = init
    ob.keyframe_insert('["%s"]' % prop, frame=0)
    fc = _fcurve(ob, prop)
    fc.keyframe_points.clear()
    rows = [(0, init)] + rows
    fc.keyframe_points.add(len(rows))
    for kp, (f, v) in zip(fc.keyframe_points, rows):
        kp.co = (f, v)
        kp.interpolation = "CONSTANT"
    fc.update()


def _driver(owner, path, expr, props, index=-1):
    ob = bpy.data.objects[CTRL]
    try:
        owner.driver_remove(path, index) if index >= 0 else owner.driver_remove(path)
    except TypeError:
        pass
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for name, prop in props.items():
        v = d.variables.new()
        v.name = name
        v.type = "SINGLE_PROP"
        v.targets[0].id = ob
        v.targets[0].data_path = '["%s"]' % prop
    d.expression = expr
    return fc


def keys_and_envelopes():
    ob = bpy.data.objects[CTRL]
    for k, v in KNOBS.items():
        if k not in ob:
            ob[k] = v
    notes = json.load(open(NOTES))
    for tag, song, n in (("pa", "abgrund", NA), ("pg", "grund", NG)):
        rows_t = {k: [] for k in range(n)}
        rows_v = {k: [] for k in range(n)}
        cyc, last = [], None
        for t, vel, c, s in notes[song]:
            f = round(1 + t * FPS)
            k = min(int(s), n - 1)
            rows_t[k].append((f, f))
            rows_v[k].append((f, vel))
            if c != last:
                cyc.append((f, c))
                last = c
        for k in range(n):
            _keys(ob, f"{tag}_t{k}", rows_t[k], -100000.0)
            _keys(ob, f"{tag}_v{k}", rows_v[k], 0.0)
            ob[f"{tag}_e{k}"] = 0.0
            _driver(ob, f'["{tag}_e{k}"]', "strength * v * exp(-3 * max(frame - t, 0) / (fade * %d))" % FPS,
                    dict(strength="strength", v=f"{tag}_v{k}", t=f"{tag}_t{k}", fade="pl_fade"))
        _keys(ob, f"{tag}_cycle", cyc, -1)
        print(tag, {k: len(rows_t[k]) for k in range(n)}, "notes per step,", len(cyc), "cycles")
    ob["pa_emax"] = 0.0
    _driver(ob, '["pa_emax"]', "max(%s)" % ", ".join(f"e{k}" for k in range(NA)), {f"e{k}": f"pa_e{k}" for k in range(NA)})


# ---------------------------------------------------------------- ABGRUND: rootlet streaks
def _along_lookup():
    dg = bpy.context.evaluated_depsgraph_get()
    le = bpy.data.objects["Lane"].evaluated_get(dg)
    me = le.to_mesh()
    al = np.empty(len(me.vertices)); me.attributes["along"].data.foreach_get("value", al)
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    le.to_mesh_clear()
    from mathutils.kdtree import KDTree
    kd = KDTree(len(co))
    for i, p in enumerate(co):
        kd.insert(p, i)
    kd.balance()
    return lambda p: al[kd.find(p)[1]]


def rootlet_candidates(share_fine=0.12, min_len=1.0, seed=17):
    """A static mesh of tubes (4 lines + rings) around candidate roots, with per-vertex `u` (0 at the root's
    top -> 1 at its bottom), `rid` (per root) and `mid` (1 on one vertex per root, for its light)."""
    rng = random.Random(seed)
    along = _along_lookup()
    bm = bmesh.new()
    lu = bm.verts.layers.float.new("u")
    lr = bm.verts.layers.int.new("rid")
    lm = bm.verts.layers.float.new("mid")
    rid = 0
    for src, share in (("BankRootsFine", share_fine), ("SlideRoots", 1.0)):
        ob = bpy.data.objects[src]
        M = ob.matrix_world
        for s in ob.data.splines:
            pts = [M @ Vector(p.co[:3]) for p in s.points] if s.type != "BEZIER" else [M @ p.co for p in s.bezier_points]
            rad = [p.radius for p in s.points] if s.type != "BEZIER" else [p.radius for p in s.bezier_points]
            if len(pts) < 4:
                continue
            L = sum((pts[i + 1] - pts[i]).length for i in range(len(pts) - 1))
            if L < min_len or rng.random() > share:
                continue
            if src == "BankRootsFine" and not (ROOT_SPAN[0] < along(pts[0]) < ROOT_SPAN[1]):
                continue
            if pts[0].z < pts[-1].z:                 # u runs from the top of the root down
                pts, rad = pts[::-1], rad[::-1]
            acc = [0.0]
            for i in range(len(pts) - 1):
                acc.append(acc[-1] + (pts[i + 1] - pts[i]).length)
            rings = []
            step = max(1, len(pts) // 8)
            idx = list(range(0, len(pts), step))
            if idx[-1] != len(pts) - 1:
                idx.append(len(pts) - 1)
            for j, i in enumerate(idx):
                p = pts[i]
                t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
                a = t.orthogonal().normalized()
                b = t.cross(a)
                r = (rad[i] if rad[i] > 0 else 0.01) * (ob.data.bevel_depth or 1.0) + 0.01
                ring = []
                for q in range(4):
                    ang = q * math.pi / 2 + (j % 2) * math.pi / 4
                    v = bm.verts.new(p + (a * math.cos(ang) + b * math.sin(ang)) * r)
                    v[lu] = acc[i] / L
                    v[lr] = rid
                    v[lm] = 0.0
                    ring.append(v)
                for q in range(4):
                    bm.edges.new((ring[q], ring[(q + 1) % 4]))
                if rings:
                    for q in range(4):
                        bm.edges.new((rings[-1][q], ring[q]))
                rings.append(ring)
            rings[len(rings) // 2][0][lm] = 1.0
            rid += 1
    me = bpy.data.meshes.get("RootletCandidates") or bpy.data.meshes.new("RootletCandidates")
    bm.to_mesh(me)
    bm.free()
    obc = bpy.data.objects.get("RootletCandidates") or bpy.data.objects.new("RootletCandidates", me)
    obc.data = me
    if not obc.users_collection:
        bpy.data.collections["FORMS"].objects.link(obc)
    obc.hide_render = True
    obc.hide_viewport = True
    print("rootlet candidates:", rid, "roots,", len(me.vertices), "verts")
    return obc


def _chosen_tree(g, N, L, src_geo):
    """Keep only this cycle's roots: in the camera's frame 3-30 m away, and of those about `pa_count`, picked by
    a per-cycle random. The pick rate adapts to how many candidate roots are in frame, so a burst lights about
    two roots whether there are 10 or 50 in view."""
    cyc = N.new("ShaderNodeValue"); cyc.name = "Cycle"
    _driver(g, 'nodes["Cycle"].outputs[0].default_value', "c", dict(c="pa_cycle"))
    want = N.new("ShaderNodeValue"); want.name = "Count"
    _driver(g, 'nodes["Count"].outputs[0].default_value', "n", dict(n="pa_count"))
    rid = N.new("GeometryNodeInputNamedAttribute"); rid.data_type = "INT"; rid.inputs["Name"].default_value = "rid"
    cam = N.new("GeometryNodeObjectInfo"); cam.transform_space = "RELATIVE"
    cam.inputs["Object"].default_value = bpy.data.objects["Camera"]
    pos = N.new("GeometryNodeInputPosition")
    rel = N.new("ShaderNodeVectorMath"); rel.operation = "SUBTRACT"
    L.new(pos.outputs[0], rel.inputs[0]); L.new(cam.outputs["Location"], rel.inputs[1])

    def axis(v):
        r = N.new("FunctionNodeRotateVector"); r.inputs["Vector"].default_value = v
        L.new(cam.outputs["Rotation"], r.inputs["Rotation"])
        d = N.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"
        L.new(rel.outputs[0], d.inputs[0]); L.new(r.outputs[0], d.inputs[1])
        return d.outputs["Value"]

    def M(op, a, b):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    depth, right, up = axis((0, 0, -1)), axis((1, 0, 0)), axis((0, 1, 0))
    lim = M("MULTIPLY", depth, 0.55)                  # about the 28 mm frame's half-width, a little inside it
    inview = M("MULTIPLY", M("MULTIPLY", M("GREATER_THAN", depth, 3.0), M("LESS_THAN", depth, 30.0)),
               M("MULTIPLY", M("LESS_THAN", M("ABSOLUTE", right, None), lim), M("LESS_THAN", M("ABSOLUTE", up, None), lim)))
    midv = N.new("GeometryNodeInputNamedAttribute"); midv.data_type = "FLOAT"; midv.inputs["Name"].default_value = "mid"
    candidate = M("MULTIPLY", inview, midv.outputs[0])           # 1 on the middle vertex of each root in view
    stat = N.new("GeometryNodeAttributeStatistic"); stat.data_type = "FLOAT"; stat.domain = "POINT"
    L.new(src_geo, stat.inputs["Geometry"]); L.new(candidate, stat.inputs["Attribute"])
    share = M("DIVIDE", want.outputs[0], M("MAXIMUM", stat.outputs["Sum"], 1.0))
    rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "FLOAT"
    L.new(rid.outputs[0], rnd.inputs["ID"]); L.new(cyc.outputs[0], rnd.inputs["Seed"])
    pick = M("MULTIPLY", candidate, M("LESS_THAN", rnd.outputs["Value"], share))
    # spread the decision from the root's middle vertex to the whole root
    acc = N.new("GeometryNodeAccumulateField"); acc.data_type = "FLOAT"; acc.domain = "POINT"
    L.new(pick, acc.inputs["Value"]); L.new(rid.outputs[0], acc.inputs[1])
    drop = M("LESS_THAN", acc.outputs["Total"], 0.5)
    de = N.new("GeometryNodeDeleteGeometry"); de.domain = "POINT"
    L.new(src_geo, de.inputs["Geometry"]); L.new(drop, de.inputs["Selection"])
    return de.outputs["Geometry"]


def _group(name):
    g = bpy.data.node_groups.get(name)
    if g:
        bpy.data.node_groups.remove(g)
    g = bpy.data.node_groups.new(name, "GeometryNodeTree")
    g.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    g.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return g


def _object(name, g, collection="FORMS"):
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
    if not ob.users_collection:
        bpy.data.collections[collection].objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    ob.modifiers.new("GeometryNodes", "NODES").node_group = g
    return ob


def rootlet_cages(mat_name="FormWire_Pluck"):
    g = _group("RootletCages")
    N, L = g.nodes, g.links
    out = N.new("NodeGroupOutput")
    src = N.new("GeometryNodeObjectInfo"); src.transform_space = "RELATIVE"
    src.inputs["Object"].default_value = bpy.data.objects["RootletCandidates"]
    geo = _chosen_tree(g, N, L, src.outputs["Geometry"])
    m2c = N.new("GeometryNodeMeshToCurve"); L.new(geo, m2c.inputs["Mesh"])
    circ = N.new("GeometryNodeCurvePrimitiveCircle"); circ.inputs["Resolution"].default_value = 4; circ.inputs["Radius"].default_value = 0.005
    c2m = N.new("GeometryNodeCurveToMesh"); L.new(m2c.outputs[0], c2m.inputs["Curve"]); L.new(circ.outputs[0], c2m.inputs["Profile Curve"])
    sm = N.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = bpy.data.materials[mat_name]
    L.new(c2m.outputs[0], sm.inputs["Geometry"]); L.new(sm.outputs[0], out.inputs[0])
    ob = _object("RootletCages", g)
    ob.visible_shadow = False
    return ob


def rootlet_lights():
    g = _group("RootletLights")
    N, L = g.nodes, g.links
    out = N.new("NodeGroupOutput")
    src = N.new("GeometryNodeObjectInfo"); src.transform_space = "RELATIVE"
    src.inputs["Object"].default_value = bpy.data.objects["RootletCandidates"]
    geo = _chosen_tree(g, N, L, src.outputs["Geometry"])
    midv = N.new("GeometryNodeInputNamedAttribute"); midv.data_type = "FLOAT"; midv.inputs["Name"].default_value = "mid"
    notmid = N.new("ShaderNodeMath"); notmid.operation = "LESS_THAN"; notmid.inputs[1].default_value = 0.5
    L.new(midv.outputs[0], notmid.inputs[0])
    de = N.new("GeometryNodeDeleteGeometry"); de.domain = "POINT"
    L.new(geo, de.inputs["Geometry"]); L.new(notmid.outputs[0], de.inputs["Selection"])
    m2p = N.new("GeometryNodeMeshToPoints"); L.new(de.outputs[0], m2p.inputs["Mesh"])
    col = bpy.data.collections.get("LIGHT_PLUCK")
    if not col:
        col = bpy.data.collections.new("LIGHT_PLUCK"); bpy.data.collections["ASSETS"].children.link(col)
        ld = bpy.data.lights.new("FormLight_Pluck", "POINT")
        ld.use_shadow = False; ld.specular_factor = 0.0; ld.volume_factor = 2.5
        ld.use_custom_distance = True; ld.cutoff_distance = 2.5; ld.shadow_soft_size = 0.05
        lo = bpy.data.objects.new("FormLight_Pluck", ld); col.objects.link(lo)
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = col
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    ip = N.new("GeometryNodeInstanceOnPoints"); L.new(m2p.outputs[0], ip.inputs["Points"]); L.new(ci.outputs[0], ip.inputs["Instance"])
    L.new(ip.outputs[0], out.inputs[0])
    ob = _object("RootletLights", g)
    ld = bpy.data.lights["FormLight_Pluck"]
    _driver(ld, "energy", "w * e", dict(w="pa_light_w", e="pa_emax"))
    for i, ch in enumerate("rgb"):
        _driver(ld, "color", ch, {ch: "form_" + ch}, index=i)
    return ob


def _strip_drivers(nt, paths):
    if nt.animation_data:
        for d in list(nt.animation_data.drivers):
            if d.data_path in paths:
                nt.animation_data.drivers.remove(d)


def _set_strength(m, strength_socket):
    """Feed a computed flash strength into a FormWire material's emission, AOV and on/off switch."""
    nt = m.node_tree
    _strip_drivers(nt, ('nodes["FormEmission"].inputs[1].default_value', 'nodes["FormAOVColor"].inputs[3].default_value',
                        'nodes["FormOnOff"].inputs[0].default_value'))
    nt.links.new(strength_socket, nt.nodes["FormEmission"].inputs[1])
    nt.links.new(strength_socket, nt.nodes["FormAOVColor"].inputs[3])
    on = nt.nodes.new("ShaderNodeMath"); on.operation = "GREATER_THAN"; on.inputs[1].default_value = 0.02
    nt.links.new(strength_socket, on.inputs[0]); nt.links.new(on.outputs[0], nt.nodes["FormOnOff"].inputs[0])


def pluck_material():
    """FormWire_Pluck: a copy of the kick wire whose strength is the streak: segment k of the root (u) lights
    with step k's envelope."""
    m = bpy.data.materials.get("FormWire_Pluck")
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials["FormWire_Kick"].copy()
    m.name = "FormWire_Pluck"
    nt = m.node_tree
    for i, ch in enumerate("rgb"):
        _driver(nt, 'nodes["FormEmission"].inputs[0].default_value', ch, {ch: "form_" + ch}, index=i)
        _driver(nt, 'nodes["FormAOVColor"].inputs[0].default_value', ch, {ch: "form_" + ch}, index=i)
    u = nt.nodes.new("ShaderNodeAttribute"); u.attribute_name = "u"
    seg = nt.nodes.new("ShaderNodeMath"); seg.operation = "FLOOR"
    sc6 = nt.nodes.new("ShaderNodeMath"); sc6.operation = "MULTIPLY"; sc6.inputs[1].default_value = NA - 0.001
    nt.links.new(u.outputs["Fac"], sc6.inputs[0]); nt.links.new(sc6.outputs[0], seg.inputs[0])
    total = None
    for k in range(NA):
        val = nt.nodes.new("ShaderNodeValue"); val.name = f"PA_e{k}"
        _driver(nt, f'nodes["PA_e{k}"].outputs[0].default_value', "e", dict(e=f"pa_e{k}"))
        eq = nt.nodes.new("ShaderNodeMath"); eq.operation = "COMPARE"; eq.inputs[1].default_value = k; eq.inputs[2].default_value = 0.1
        nt.links.new(seg.outputs[0], eq.inputs[0])
        term = nt.nodes.new("ShaderNodeMath"); term.operation = "MULTIPLY"
        nt.links.new(eq.outputs[0], term.inputs[0]); nt.links.new(val.outputs[0], term.inputs[1])
        if total is None:
            total = term.outputs[0]
        else:
            add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
            nt.links.new(total, add.inputs[0]); nt.links.new(term.outputs[0], add.inputs[1]); total = add.outputs[0]
    peak = nt.nodes.new("ShaderNodeValue"); peak.name = "PA_peak"
    _driver(nt, 'nodes["PA_peak"].outputs[0].default_value', "p", dict(p="pa_peak"))
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"
    nt.links.new(total, st.inputs[0]); nt.links.new(peak.outputs[0], st.inputs[1])
    _set_strength(m, st.outputs[0])
    return m


def grass_waves():
    """FormWire_Grass leaves the snare: band k of camera depth (8, 12, 16, 20 m) lights with step k's envelope."""
    m = bpy.data.materials["FormWire_Grass"]
    nt = m.node_tree
    if "PG_total" in nt.nodes:
        print("grass waves already wired"); return
    cd = nt.nodes.new("ShaderNodeCameraData")
    total = None
    ob = bpy.data.objects[CTRL]
    for k in range(NG):
        d = ob["pg_d0"] + k * ob["pg_step"]
        h = ob["pg_half"]
        band = nt.nodes.new("ShaderNodeMapRange"); band.interpolation_type = "SMOOTHSTEP"
        band.inputs["From Min"].default_value, band.inputs["From Max"].default_value = d - 2 * h, d - h
        band2 = nt.nodes.new("ShaderNodeMapRange"); band2.interpolation_type = "SMOOTHSTEP"
        band2.inputs["From Min"].default_value, band2.inputs["From Max"].default_value = d + h, d + 2 * h
        band2.inputs["To Min"].default_value, band2.inputs["To Max"].default_value = 1.0, 0.0
        nt.links.new(cd.outputs["View Z Depth"], band.inputs["Value"]); nt.links.new(cd.outputs["View Z Depth"], band2.inputs["Value"])
        bm = nt.nodes.new("ShaderNodeMath"); bm.operation = "MULTIPLY"
        nt.links.new(band.outputs["Result"], bm.inputs[0]); nt.links.new(band2.outputs["Result"], bm.inputs[1])
        val = nt.nodes.new("ShaderNodeValue"); val.name = f"PG_e{k}"
        _driver(nt, f'nodes["PG_e{k}"].outputs[0].default_value', "e", dict(e=f"pg_e{k}"))
        term = nt.nodes.new("ShaderNodeMath"); term.operation = "MULTIPLY"
        nt.links.new(bm.outputs[0], term.inputs[0]); nt.links.new(val.outputs[0], term.inputs[1])
        if total is None:
            total = term.outputs[0]
        else:
            add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
            nt.links.new(total, add.inputs[0]); nt.links.new(term.outputs[0], add.inputs[1]); total = add.outputs[0]
    peak = nt.nodes.new("ShaderNodeValue"); peak.name = "PG_peak"
    _driver(nt, 'nodes["PG_peak"].outputs[0].default_value', "p", dict(p="pg_peak"))
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; st.name = "PG_total"
    nt.links.new(total, st.inputs[0]); nt.links.new(peak.outputs[0], st.inputs[1])
    _set_strength(m, st.outputs[0])
    bpy.data.objects["Scatter_GrassLights"].hide_render = True
    bpy.data.objects["Scatter_GrassLights"].hide_viewport = True


def build():
    keys_and_envelopes()
    pluck_material()
    rootlet_candidates()
    rootlet_cages()
    rootlet_lights()
    grass_waves()
    print("pluck rig built - save, revert, then check drivers (new drivers stay invalid until reload)")


# ---------------------------------------------------------------- v2: pulses, not chains (Nick, 2026-10-20)
# "rather than running down they should just light up all the forms. so it is obvious what is causing it ... the
# concept is great, we just need to execute it in a way that is hypnotic". Every pluck note lights every pluck form
# in view at once: ABGRUND's bursts read as one shimmering pulse every half note (longer fade), GRUND's 16ths as a
# stream with the accent on each beat standing out (shorter fade).
PULSE = dict(pa_fade=0.25, pg_fade=0.35, light_every=5, view_near=2.0, view_far=35.0)
# pg_fade 0.12 -> 0.35 (Nick, 2026-11-03): at 0.12 each 16th died before the next and the grass read as flicker; at
# 0.35 the notes overlap into a glow that never drops to dark, accents still riding on top.


def pulse_envelopes():
    ob = bpy.data.objects[CTRL]
    for k in ("pa_fade", "pg_fade"):
        if k not in ob:
            ob[k] = PULSE[k]
    for tag, n in (("pa", NA), ("pg", NG)):
        for k in range(n):
            _driver(ob, f'["{tag}_e{k}"]', "strength * v * exp(-3 * max(frame - t, 0) / (fade * %d))" % FPS,
                    dict(strength="strength", v=f"{tag}_v{k}", t=f"{tag}_t{k}", fade=f"{tag}_fade"))
        ob[f"{tag}_emax"] = 0.0
        _driver(ob, f'["{tag}_emax"]', "max(%s)" % ", ".join(f"e{k}" for k in range(n)), {f"e{k}": f"{tag}_e{k}" for k in range(n)})


def _in_view_tree(g, N, L, src_geo, every=None):
    """Every candidate root in the camera's frame (whole roots, judged by their middle vertex); with `every`, only
    roots whose rid is a multiple of it (the ones that carry a light)."""
    rid = N.new("GeometryNodeInputNamedAttribute"); rid.data_type = "INT"; rid.inputs["Name"].default_value = "rid"
    cam = N.new("GeometryNodeObjectInfo"); cam.transform_space = "RELATIVE"
    cam.inputs["Object"].default_value = bpy.data.objects["Camera"]
    pos = N.new("GeometryNodeInputPosition")
    rel = N.new("ShaderNodeVectorMath"); rel.operation = "SUBTRACT"
    L.new(pos.outputs[0], rel.inputs[0]); L.new(cam.outputs["Location"], rel.inputs[1])

    def axis(v):
        r = N.new("FunctionNodeRotateVector"); r.inputs["Vector"].default_value = v
        L.new(cam.outputs["Rotation"], r.inputs["Rotation"])
        d = N.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"
        L.new(rel.outputs[0], d.inputs[0]); L.new(r.outputs[0], d.inputs[1])
        return d.outputs["Value"]

    def M(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    depth, right, up = axis((0, 0, -1)), axis((1, 0, 0)), axis((0, 1, 0))
    lim = M("MULTIPLY", depth, 0.7)
    inview = M("MULTIPLY", M("MULTIPLY", M("GREATER_THAN", depth, PULSE["view_near"]), M("LESS_THAN", depth, PULSE["view_far"])),
               M("MULTIPLY", M("LESS_THAN", M("ABSOLUTE", right), lim), M("LESS_THAN", M("ABSOLUTE", up), lim)))
    midv = N.new("GeometryNodeInputNamedAttribute"); midv.data_type = "FLOAT"; midv.inputs["Name"].default_value = "mid"
    keep = M("MULTIPLY", inview, midv.outputs[0])
    if every:
        keep = M("MULTIPLY", keep, M("LESS_THAN", M("FLOORED_MODULO", rid.outputs[0], float(every)), 0.5))
    acc = N.new("GeometryNodeAccumulateField"); acc.data_type = "FLOAT"; acc.domain = "POINT"
    L.new(keep, acc.inputs["Value"]); L.new(rid.outputs[0], acc.inputs[1])
    de = N.new("GeometryNodeDeleteGeometry"); de.domain = "POINT"
    L.new(src_geo, de.inputs["Geometry"]); L.new(M("LESS_THAN", acc.outputs["Total"], 0.5), de.inputs["Selection"])
    return de.outputs["Geometry"]


def pulse_rootlets():
    global _chosen_tree
    _chosen_tree = lambda g, N, L, src: _in_view_tree(g, N, L, src)
    rootlet_cages()
    _chosen_tree = lambda g, N, L, src: _in_view_tree(g, N, L, src, every=PULSE["light_every"])
    rootlet_lights()
    # the whole wire pulses with the note, no segments
    m = bpy.data.materials["FormWire_Pluck"]
    nt = m.node_tree
    val = nt.nodes.get("PA_all") or nt.nodes.new("ShaderNodeValue"); val.name = "PA_all"
    _driver(nt, 'nodes["PA_all"].outputs[0].default_value', "e", dict(e="pa_emax"))
    st = [n for n in nt.nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "MULTIPLY"
          and any(l.from_node.name == "PA_peak" for l in n.inputs[1].links)][0]
    for l in list(st.inputs[0].links):
        nt.links.remove(l)
    nt.links.new(val.outputs[0], st.inputs[0])


def pulse_grass():
    m = bpy.data.materials["FormWire_Grass"]
    nt = m.node_tree
    val = nt.nodes.get("PG_all") or nt.nodes.new("ShaderNodeValue"); val.name = "PG_all"
    _driver(nt, 'nodes["PG_all"].outputs[0].default_value', "e", dict(e="pg_emax"))
    st = nt.nodes["PG_total"]
    for l in list(st.inputs[0].links):
        nt.links.remove(l)
    nt.links.new(val.outputs[0], st.inputs[0])


def build_pulses():
    pulse_envelopes()
    pulse_rootlets()
    pulse_grass()
    print("pulses built - save, revert, then check drivers")


# ---------------------------------------------------------------- v3: ABGRUND beads run down the roots (Nick, 2026-10-20)
# "could we have the abgrund pulses run down the roots. they start at the top when the sounds comes in and run down to
# the tip of the root ... grund is perfect". Every ABGRUND note launches a bead at the top of every pluck root in view;
# it reaches the tip `pa_travel` s later on every root, whatever its length, so a burst is a train of beads arriving
# together. Sharp leading edge (`pa_head`), soft tail (`pa_tail`), both as fractions of the root. The root's light
# flares as the bead passes its middle. GRUND unchanged.
BEAD = dict(pa_travel=0.7, pa_head=0.02, pa_tail=0.25)


def _bead(s, u):
    return "exp(-max(%s - %s, 0) / tail) * exp(min(%s - %s, 0) / head)" % (s, u, s, u)


def bead_drivers():
    ob = bpy.data.objects[CTRL]
    for k, v in BEAD.items():
        if k not in ob:
            ob[k] = v
    for k in range(NA):                       # bead position along the root: 0 at the note, 1 at the tip
        ob[f"pa_s{k}"] = 10.0
        _driver(ob, f'["pa_s{k}"]', "(frame - t) / (travel * %d)" % FPS, dict(t=f"pa_t{k}", travel="pa_travel"))
    for k in range(NA):                       # the bead's brightness at the root's middle, where its light sits
        ob[f"pa_m{k}"] = 0.0
        _driver(ob, f'["pa_m{k}"]', "strength * v * " + _bead("s", "0.5"),
                dict(s=f"pa_s{k}", v=f"pa_v{k}", strength="strength", head="pa_head", tail="pa_tail"))
    ob["pa_mid"] = 0.0
    _driver(ob, '["pa_mid"]', "max(%s)" % ", ".join(f"m{k}" for k in range(NA)), {f"m{k}": f"pa_m{k}" for k in range(NA)})
    ld = bpy.data.lights["FormLight_Pluck"]
    _driver(ld, "energy", "w * e", dict(w="pa_light_w", e="pa_mid"))


def bead_material():
    m = bpy.data.materials["FormWire_Pluck"]
    nt = m.node_tree
    for n in [n for n in nt.nodes if n.name.startswith("BEAD")]:
        nt.nodes.remove(n)
    def node(kind, name, **kw):
        n = nt.nodes.new(kind); n.name = "BEAD_" + name
        for a, b in kw.items():
            setattr(n, a, b)
        return n
    def M(op, a, b, name):
        n = node("ShaderNodeMath", name, operation=op)
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    def V(name, prop):
        n = node("ShaderNodeValue", name)
        _driver(nt, f'nodes["{n.name}"].outputs[0].default_value', "x", dict(x=prop))
        return n.outputs[0]
    u = node("ShaderNodeAttribute", "u"); u.attribute_name = "u"
    head, tail, strength = V("head", "pa_head"), V("tail", "pa_tail"), V("strength", "strength")
    total = None
    for k in range(NA):
        d = M("SUBTRACT", V(f"s{k}", f"pa_s{k}"), u.outputs["Fac"], f"d{k}")
        # exp(-max(d, 0) / tail) * exp(min(d, 0) / head): soft tail behind the bead, sharp edge ahead of it
        e1 = M("EXPONENT", M("MULTIPLY", M("DIVIDE", M("MAXIMUM", d, 0.0, f"mx{k}"), tail, f"dt{k}"), -1.0, f"ng{k}"), None, f"e1{k}")
        e2 = M("EXPONENT", M("DIVIDE", M("MINIMUM", d, 0.0, f"mn{k}"), head, f"dh{k}"), None, f"e2{k}")
        term = M("MULTIPLY", M("MULTIPLY", e1, e2, f"w{k}"), V(f"v{k}", f"pa_v{k}"), f"t{k}")
        total = term if total is None else M("ADD", total, term, f"sum{k}")
    total = M("MULTIPLY", total, strength, "strength_mul")
    st = [n for n in nt.nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "MULTIPLY"
          and any(l.from_node.name == "PA_peak" for l in n.inputs[1].links)][0]
    for l in list(st.inputs[0].links):
        nt.links.remove(l)
    nt.links.new(total, st.inputs[0])


def build_beads():
    bead_drivers()
    bead_material()
    print("beads built - save, revert, then check drivers")
