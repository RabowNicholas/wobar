"""MAKYO - the intact mirror, pre-fractured along its own crack pattern.

Run in makyo_shards_v5.blend (exec with makyo_audio.py's namespace for drive()).

One crack pattern, generated here, drives everything:
  MirrorPieces  - the disc cut into wedge/arc pieces along wandering radials + broken rings,
                  assembled edge to edge (reads intact). GN `MirrorShatter` moves each island
                  from the drop frame: a short creep along the cracks, then a burst toward the
                  camera and out from the impact point, spinning; small central pieces fastest.
  MirrorCracks  - thin emissive ribbons laid on exactly those seams. Each radial opens at its own
                  `open` threshold of MAKYO_CTRL["crack"] and grows outward; ring segments open
                  later. Hidden from the drop on.
The mirror sits at y = DEPTH facing the camera (-Y), built in metres in world orientation.
"""
import bpy, bmesh, math, random

DEPTH, R = 14.0, 7.0
SEED = 11
N_RAD = 26
RINGS = (0.06, 0.13, 0.22, 0.34, 0.48, 0.64, 0.82)   # fractions of R
THICK = 0.035
HUB = 0.012


def lin(h):
    h = h.lstrip("#"); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)


def pattern():
    rng = random.Random(SEED)
    base = sorted((i + rng.uniform(-0.35, 0.35)) / N_RAD * 2 * math.pi for i in range(N_RAD))
    radials = []
    for th in base:
        ph, amp, fr = rng.uniform(0, 6.3), rng.uniform(0.015, 0.05), rng.uniform(5, 11)
        radials.append(dict(th=th, ph=ph, amp=amp, fr=fr, open=rng.uniform(0.12, 0.8)))

    def rad_angle(i, r):   # r as fraction of R
        d = radials[i % N_RAD]
        return d["th"] + (2 * math.pi if i >= N_RAD else 0) + d["amp"] * math.sin(r * d["fr"] + d["ph"]) * min(r * 6, 1)

    rings = {}             # (sector, ring) -> dict(present, jitter phase, open)
    for s in range(N_RAD):
        for j, rr in enumerate(RINGS):
            p_present = 0.55 + 0.35 * (1 - j / len(RINGS))
            rings[(s, j)] = dict(present=rng.random() < p_present, ph=rng.uniform(0, 6.3),
                                 amp=rng.uniform(0.004, 0.012), open=0.35 + 0.07 * j + rng.uniform(0, 0.12))
    return radials, rad_angle, rings


def radial_pts(i, ra, rb, rad_angle, step=0.025):
    n = max(2, int((rb - ra) / step) + 1)
    out = []
    for k in range(n):
        r = ra + (rb - ra) * k / (n - 1)
        a = rad_angle(i, r)
        out.append((r, a))
    return out


def ring_r(s, j, a, rings, rim=False):
    if rim:
        return 1.0 + 0.012 * math.sin(a * 23 + 1.3) + 0.008 * math.sin(a * 57)
    d = rings[(s, j)]
    return RINGS[j] + d["amp"] * math.sin(a * 31 + d["ph"])


def arc_pts(s, j, a0, a1, rings, rim=False, step=0.04):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(ring_r(s, j, a0 + (a1 - a0) * k / (n - 1), rings, rim), a0 + (a1 - a0) * k / (n - 1)) for k in range(n)]


def to_world(r, a, y=0.0):
    return (math.cos(a) * r * R, y, math.sin(a) * r * R)


def build_pieces_mesh(radials, rad_angle, rings):
    """Collect each piece's outline, then build each as its own closed slab."""
    outlines = []
    for s in range(N_RAD):
        bounds = [("hub", None)] + [("ring", j) for j in range(len(RINGS)) if rings[(s, j)]["present"]] + [("rim", None)]
        for (ka, ja), (kb, jb) in zip(bounds, bounds[1:]):
            def rr_at(kind, j, i):
                if kind == "hub":
                    return HUB
                a = rad_angle(i, RINGS[j] if kind == "ring" else 1.0)
                return ring_r(s, j, a, rings, rim=(kind == "rim"))
            left = radial_pts(s, rr_at(ka, ja, s), rr_at(kb, jb, s), rad_angle)
            right = radial_pts(s + 1, rr_at(ka, ja, s + 1), rr_at(kb, jb, s + 1), rad_angle)
            top = arc_pts(s, jb, left[-1][1], right[-1][1], rings, rim=(kb == "rim"))
            bot = [(HUB, left[0][1]), (HUB, right[0][1])] if ka == "hub" else arc_pts(s, ja, left[0][1], right[0][1], rings)
            loop = left + top[1:-1] + list(reversed(right)) + list(reversed(bot))[1:-1]
            pts = []
            for r, a in loop:
                p = to_world(r, a)
                if not pts or (abs(p[0] - pts[-1][0]) + abs(p[2] - pts[-1][2])) > 1e-4:
                    pts.append(p)
            if len(pts) >= 3:
                outlines.append(pts)

    bm = bmesh.new()
    for pts in outlines:
        front = [bm.verts.new((x, -THICK / 2, z)) for x, _, z in pts]
        back = [bm.verts.new((x, THICK / 2, z)) for x, _, z in pts]
        try:
            ff = bm.faces.new(front); fb = bm.faces.new(list(reversed(back)))
        except ValueError:
            continue
        ff.material_index = fb.material_index = 0
        n = len(pts)
        for k in range(n):
            a, b = front[k], front[(k + 1) % n]
            c, d = back[(k + 1) % n], back[k]
            try:
                sf = bm.faces.new((a, d, c, b)); sf.material_index = 1
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.get("MirrorPiecesMesh")
    if me:
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new("MirrorPiecesMesh")
    bm.to_mesh(me); bm.free()
    return me, len(outlines)


def build_cracks_mesh(radials, rad_angle, rings, w=0.0045):
    """Ribbons on the seams. Point attributes: open (crack threshold), u (0 at hub .. 1 at rim for
    radials; 0 for rings), kind (0 radial, 1 ring)."""
    bm = bmesh.new()
    lay_open = bm.verts.layers.float.new("open")
    lay_u = bm.verts.layers.float.new("u")
    lay_k = bm.verts.layers.float.new("kind")
    y = -THICK / 2 - 0.01

    def ribbon(poly, opens, us, kind):
        prev = None
        for k, (r, a) in enumerate(poly):
            # normal in the disc plane, perpendicular to the polyline
            r2, a2 = poly[min(k + 1, len(poly) - 1)]
            r1, a1 = poly[max(k - 1, 0)]
            p1, p2 = to_world(r1, a1), to_world(r2, a2)
            tx, tz = p2[0] - p1[0], p2[2] - p1[2]
            ln = math.hypot(tx, tz) or 1
            nx, nz = -tz / ln * w * R / 2, tx / ln * w * R / 2
            c = to_world(r, a)
            v1 = bm.verts.new((c[0] + nx, y, c[2] + nz)); v2 = bm.verts.new((c[0] - nx, y, c[2] - nz))
            for v in (v1, v2):
                v[lay_open], v[lay_u], v[lay_k] = opens, us[k], kind
            if prev:
                try:
                    bm.faces.new((prev[0], prev[1], v2, v1))
                except ValueError:
                    pass
            prev = (v1, v2)

    for i, d in enumerate(radials):
        poly = radial_pts(i, HUB, 1.0, rad_angle, step=0.012)
        ribbon(poly, d["open"], [p[0] for p in poly], 0.0)
    for s in range(N_RAD):
        for j in range(len(RINGS)):
            d = rings[(s, j)]
            if not d["present"]:
                continue
            a0, a1 = rad_angle(s, RINGS[j]), rad_angle(s + 1, RINGS[j])
            poly = arc_pts(s, j, a0, a1, rings, step=0.015)
            ribbon(poly, d["open"], [0.0] * len(poly), 1.0)
    me = bpy.data.meshes.get("MirrorCracksMesh")
    if me:
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new("MirrorCracksMesh")
    bm.to_mesh(me); bm.free()
    return me


def crack_material():
    m = bpy.data.materials.get("MirrorCrackLight")
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new("MirrorCrackLight"); m.use_nodes = True
    nt = m.node_tree; nodes, links = nt.nodes, nt.links
    for n in list(nodes):
        if n.type != "OUTPUT_MATERIAL":
            nodes.remove(n)
    out = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")

    def attr(name):
        a = nodes.new("ShaderNodeAttribute"); a.attribute_type = "GEOMETRY"; a.attribute_name = name
        return a.outputs["Fac"]

    def M(op, a, b=None):
        n = nodes.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]

    crack = nodes.new("ShaderNodeValue"); crack.name = "Crack"
    light = nodes.new("ShaderNodeValue"); light.name = "CrackLight"
    since = M("SUBTRACT", crack.outputs[0], attr("open"))
    # radials grow outward: reach = since * 3 (full length ~0.33 crack units after opening)
    reach = M("MULTIPLY", since, 3.0)
    rad_vis = M("MINIMUM", M("MAXIMUM", M("MULTIPLY", M("SUBTRACT", reach, attr("u")), 40.0), 0.0), 1.0)
    ring_vis = M("MINIMUM", M("MAXIMUM", M("MULTIPLY", since, 30.0), 0.0), 1.0)
    k = attr("kind")
    vis = M("ADD", M("MULTIPLY", rad_vis, M("SUBTRACT", 1.0, k)), M("MULTIPLY", ring_vis, k))
    em = nodes.new("ShaderNodeEmission")
    ramp = nodes.new("ShaderNodeValToRGB"); e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (*lin("#8A5A3D"), 1)
    e[1].position, e[1].color = 1.0, (*lin("#C7BBA6"), 1)
    links.new(M("SUBTRACT", 1.0, M("MULTIPLY", attr("u"), 0.6)), ramp.inputs["Fac"])   # brighter at the impact
    links.new(ramp.outputs["Color"], em.inputs["Color"])
    links.new(M("MULTIPLY", vis, light.outputs[0]), em.inputs["Strength"])
    tr = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(vis, mix.inputs["Fac"])
    links.new(tr.outputs[0], mix.inputs[1]); links.new(em.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs["Surface"])
    drive(crack.outputs[0], "default_value", "c", [("c", "crack")])
    expr, v = LIGHT
    drive(light.outputs[0], "default_value", f"14 * ({expr})", v)
    return m


def shatter_tree(drop_frame):
    ng = bpy.data.node_groups.get("MirrorShatter")
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new("MirrorShatter", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for name, dv in (("Drop Frame", float(drop_frame)), ("Creep", 0.03), ("Creep Time", 0.07),
                     ("Burst Delay", 0.05), ("Toward Camera", 9.0), ("Outward", 2.2), ("Impact Boost", 5.0),
                     ("Spin", 7.0)):
        s = ng.interface.new_socket(name, in_out="INPUT", socket_type="NodeSocketFloat"); s.default_value = dv
    nodes, links = ng.nodes, ng.links
    gi = nodes.new("NodeGroupInput"); go = nodes.new("NodeGroupOutput")
    G = lambda n: gi.outputs[n]

    def M(op, a, b=None):
        n = nodes.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]

    def V(op, a, b=None, scale=None):
        n = nodes.new("ShaderNodeVectorMath"); n.operation = op
        links.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, tuple):
                n.inputs[1].default_value = b
            else:
                links.new(b, n.inputs[1])
        if scale is not None:
            if isinstance(scale, (int, float)):
                n.inputs["Scale"].default_value = scale
            else:
                links.new(scale, n.inputs["Scale"])
        return n.outputs[0] if op not in ("LENGTH", "DOT_PRODUCT") else n.outputs["Value"]

    isl = nodes.new("GeometryNodeInputMeshIsland")
    pos = nodes.new("GeometryNodeInputPosition").outputs[0]
    acc = nodes.new("GeometryNodeAccumulateField"); acc.data_type = "FLOAT_VECTOR"; acc.domain = "POINT"
    links.new(pos, acc.inputs[0]); links.new(isl.outputs["Island Index"], acc.inputs["Group ID"])
    cnt = nodes.new("GeometryNodeAccumulateField"); cnt.data_type = "FLOAT"; cnt.domain = "POINT"
    cnt.inputs[0].default_value = 1.0; links.new(isl.outputs["Island Index"], cnt.inputs["Group ID"])
    cen = V("SCALE", acc.outputs["Total"], scale=M("DIVIDE", 1.0, cnt.outputs["Total"]))

    def rnd(seed, lo=0.0, hi=1.0, vec=False):
        r = nodes.new("FunctionNodeRandomValue"); r.data_type = "FLOAT_VECTOR" if vec else "FLOAT"
        r.inputs["Min"].default_value = (lo,) * 3 if vec else lo
        r.inputs["Max"].default_value = (hi,) * 3 if vec else hi
        links.new(isl.outputs["Island Index"], r.inputs["ID"]); r.inputs["Seed"].default_value = seed
        return r.outputs["Value"]

    frame = nodes.new("GeometryNodeInputSceneTime").outputs["Frame"]
    dt = M("MAXIMUM", M("DIVIDE", M("SUBTRACT", frame, G("Drop Frame")), 30.0), 0.0)
    # radial direction in the disc plane, and distance from the impact (metres)
    flat = V("MULTIPLY", cen, (1.0, 0.0, 1.0))
    rdist = V("LENGTH", flat)
    rdir = V("NORMALIZE", flat)
    # 1) creep: gaps open along the cracks before anything flies
    cx = M("MINIMUM", M("DIVIDE", dt, G("Creep Time")), 1.0)
    creep = V("SCALE", rdir, scale=M("MULTIPLY", G("Creep"), M("MULTIPLY", cx, M("SUBTRACT", 3.0, M("MULTIPLY", cx, 2.0)))))
    # 2) burst after a short, per-piece delay (later further from the impact: the break propagates)
    delay = M("ADD", G("Burst Delay"), M("ADD", M("MULTIPLY", rdist, 0.006), M("MULTIPLY", rnd(1), 0.02)))
    tb = M("MAXIMUM", M("SUBTRACT", dt, delay), 0.0)
    near = M("DIVIDE", 1.0, M("ADD", M("DIVIDE", rdist, 1.5), 0.35))       # ~2.9 at the hub, ~0.2 at the rim
    jit = rnd(2, 0.75, 1.3)
    vy = M("MULTIPLY", M("MULTIPLY", G("Toward Camera"), M("ADD", 0.6, M("MULTIPLY", near, 0.45))), jit)
    vr = M("MULTIPLY", M("ADD", G("Outward"), M("MULTIPLY", G("Impact Boost"), M("MULTIPLY", near, 0.35))), jit)
    vel = V("ADD", V("SCALE", rdir, scale=vr), nodes.new("ShaderNodeCombineXYZ").outputs[0])
    vel_comb = vel.node.inputs[1].links[0].from_node
    links.new(M("MULTIPLY", vy, -1.0), vel_comb.inputs[1])
    # a little out-of-plane scatter so pieces don't stay coplanar
    vel = V("ADD", vel, V("SCALE", rnd(3, -1.0, 1.0, vec=True), scale=1.2))
    off = V("ADD", creep, V("SCALE", vel, scale=tb))
    # spin about the piece centre, faster for small pieces near the impact
    axis = V("NORMALIZE", rnd(4, -1.0, 1.0, vec=True))
    ang = M("MULTIPLY", M("MULTIPLY", G("Spin"), M("ADD", 0.3, M("MULTIPLY", near, 0.5))), M("MULTIPLY", tb, rnd(5, 0.4, 1.2)))
    vrot = nodes.new("ShaderNodeVectorRotate"); vrot.rotation_type = "AXIS_ANGLE"
    links.new(pos, vrot.inputs["Vector"]); links.new(cen, vrot.inputs["Center"])
    links.new(axis, vrot.inputs["Axis"]); links.new(ang, vrot.inputs["Angle"])
    sp = nodes.new("GeometryNodeSetPosition")
    links.new(gi.outputs[0], sp.inputs["Geometry"])
    links.new(V("ADD", vrot.outputs[0], off), sp.inputs["Position"])
    links.new(sp.outputs[0], go.inputs[0])
    return ng


def main(C):
    radials, rad_angle, rings = pattern()
    pme, npieces = build_pieces_mesh(radials, rad_angle, rings)
    pme.materials.append(bpy.data.materials["MakyoMirror"]); pme.materials.append(bpy.data.materials["MakyoEdge"])
    ob = bpy.data.objects.get("MirrorPieces") or bpy.data.objects.new("MirrorPieces", pme)
    ob.data = pme
    if ob.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(ob)
    ob.location = (0, DEPTH, 0)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    ob.modifiers.new("MirrorShatter", "NODES").node_group = shatter_tree(C["drop_frame"])

    cme = build_cracks_mesh(radials, rad_angle, rings)
    cme.materials.append(crack_material())
    co = bpy.data.objects.get("MirrorCracks") or bpy.data.objects.new("MirrorCracks", cme)
    co.data = cme
    if co.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(co)
    co.location = (0, DEPTH, 0)
    co.visible_shadow = False
    for i in range(3):
        drive(co, "scale", "i", [("i", "intact")], index=i)

    old = bpy.data.objects.get("IntactMirror")
    if old:
        if old.animation_data:
            for i in range(3):
                try:
                    old.driver_remove("scale", i)
                except TypeError:
                    pass
        old.hide_render = old.hide_viewport = True
    print(f"mirror fractured: {npieces} pieces, {len(cme.polygons)} crack faces", flush=True)
