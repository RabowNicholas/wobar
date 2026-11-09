"""MAKYO - kick breaks with real fracture. Run in makyo_shards_v6.blend after makyo_break.py
(needs makyo_audio.py's namespace for nothing here; pure bpy).

Pre-fracture: each kit shape shard_k (instance index k of ShardKit, creation order) is cut along a
glass pattern - radials from an off-centre impact point plus up to two rings - by clipping its
convex outline with convex cells. Pieces become objects F_#### (mesh centred on the piece's
centroid, parent-local units) in collection FracPieces (excluded). Lookups:
  FracTable    - one point per piece: position = centroid in the parent's local space
  FracVariants - one point per kit shape: start, count (INT), impact (FLOAT_VECTOR)
ShardStream: the old swap-in fragment branch is cut off; a broken shard is duplicated once per piece
of its own shape; each copy is placed at parent position + rotate(centroid * scale, parent rotation)
and breaks away from the impact point: 2-frame creep, then a burst slowed by drag, spin decaying.
"""
import bpy, bmesh, math, random
from mathutils import Vector
from mathutils.geometry import convex_hull_2d

SEED = 5


def outline(me):
    pts = [(v.co.x, v.co.y) for v in me.vertices]
    hull = convex_hull_2d(pts)
    poly = [pts[i] for i in hull]
    zs = [v.co.z for v in me.vertices]
    return poly, max(zs), min(zs)


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def clip(subject, clipper):
    """Sutherland-Hodgman; clipper convex, counter-clockwise."""
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def inter(p, q, a, b):
        x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
        x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-12:
            return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    out = subject
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        if not inp:
            break
        s = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(s, a, b):
                    out.append(inter(s, e, a, b))
                out.append(e)
            elif inside(s, a, b):
                out.append(inter(s, e, a, b))
            s = e
    return out


def fracture(poly, rng):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    size = max(max(xs) - min(xs), max(ys) - min(ys))
    imp = (cx + rng.uniform(-0.25, 0.25) * size, cy + rng.uniform(-0.25, 0.25) * size)
    n = rng.randint(5, 8)
    base = rng.uniform(0, 2 * math.pi)
    angs = [base + (i + rng.uniform(-0.3, 0.3)) * 2 * math.pi / n for i in range(n)]
    rings = [r * size for r, p in ((0.16, 0.8), (0.42, 0.6)) if rng.random() < p]
    bands = [0.0] + rings + [10.0 * size]
    pieces = []
    for i in range(n):
        a0, a1 = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
        for ri, ro in zip(bands, bands[1:]):
            j0, j1 = rng.uniform(0.85, 1.15), rng.uniform(0.85, 1.15)
            d0 = (math.cos(a0), math.sin(a0)); d1 = (math.cos(a1), math.sin(a1))
            if ri == 0:
                cell = [imp, (imp[0] + d0[0] * ro, imp[1] + d0[1] * ro), (imp[0] + d1[0] * ro, imp[1] + d1[1] * ro)]
            else:
                cell = [(imp[0] + d0[0] * ri * j0, imp[1] + d0[1] * ri * j0), (imp[0] + d0[0] * ro, imp[1] + d0[1] * ro),
                        (imp[0] + d1[0] * ro, imp[1] + d1[1] * ro), (imp[0] + d1[0] * ri * j1, imp[1] + d1[1] * ri * j1)]
            if area(cell) < 0:
                cell.reverse()
            pc = clip(poly, cell)
            if len(pc) >= 3 and abs(area(pc)) > 0.002 * size * size:
                pieces.append(pc)
    return pieces, imp


def piece_mesh(name, poly, ztop, zbot):
    if area(poly) < 0:
        poly = list(reversed(poly))
    cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
    cz = (ztop + zbot) / 2
    bm = bmesh.new()
    top = [bm.verts.new((x - cx, y - cy, ztop - cz)) for x, y in poly]
    bot = [bm.verts.new((x - cx, y - cy, zbot - cz)) for x, y in poly]
    ft = bm.faces.new(top); fb = bm.faces.new(list(reversed(bot)))
    ft.material_index = fb.material_index = 0
    n = len(poly)
    for k in range(n):
        f = bm.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k])); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me, (cx, cy, cz)


def build_kit():
    old = bpy.data.collections.get("FracPieces")
    if old:
        for o in list(old.objects):
            me = o.data; bpy.data.objects.remove(o)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        bpy.data.collections.remove(old)
    col = bpy.data.collections.new("FracPieces")
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.layer_collection.children["FracPieces"].exclude = True
    mats = [bpy.data.materials["MakyoMirror"], bpy.data.materials["MakyoEdge"]]
    rng = random.Random(SEED)
    cents, starts, counts, impacts = [], [], [], []
    g = 0
    for k in range(24):
        me = bpy.data.meshes[f"shard_{k}"]
        poly, ztop, zbot = outline(me)
        pieces, imp = fracture(poly, rng)
        starts.append(g); counts.append(len(pieces)); impacts.append((imp[0], imp[1], (ztop + zbot) / 2))
        for pc in pieces:
            pm, c = piece_mesh(f"F_{g:04d}", pc, ztop, zbot)
            for m in mats:
                pm.materials.append(m)
            o = bpy.data.objects.new(f"F_{g:04d}", pm); col.objects.link(o)
            cents.append(c); g += 1

    tcol = bpy.data.collections.get("FracTables")
    if tcol is None:
        tcol = bpy.data.collections.new("FracTables"); bpy.context.scene.collection.children.link(tcol)
    bpy.context.view_layer.layer_collection.children["FracTables"].exclude = True

    def table(name, pts):          # own excluded collection: readable by Object Info, never instanced
        me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
        me.clear_geometry(); me.vertices.add(len(pts)); me.vertices.foreach_set("co", [c for p in pts for c in p])
        ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
        ob.data = me
        if ob.name not in tcol.objects:
            tcol.objects.link(ob)
        return me, ob
    tme, tob = table("FracTable", cents)
    vme, vob = table("FracVariants", [(0, 0, 0)] * 24)
    for nm, vals in (("start", starts), ("count", counts)):
        a = vme.attributes.get(nm) or vme.attributes.new(nm, "INT", "POINT"); a.data.foreach_set("value", vals)
    a = vme.attributes.get("impact") or vme.attributes.new("impact", "FLOAT_VECTOR", "POINT")
    a.data.foreach_set("vector", [c for p in impacts for c in p])
    print(f"fractured 24 shapes into {g} pieces ({min(counts)}-{max(counts)} each)", flush=True)
    return col, tob, vob


def branch(col, tob, vob):
    ng = bpy.data.node_groups["ShardStream"]; nodes, links = ng.nodes, ng.links
    for n in [n for n in nodes if n.name.startswith("KF_")]:
        nodes.remove(n)
    gi = next(n for n in nodes if n.bl_idname == "NodeGroupInput"); G = lambda n: gi.outputs[n]
    join = next(n for n in nodes if n.bl_idname == "GeometryNodeJoinGeometry")
    # cut the old swap-in fragments off the join
    for l in list(links):
        if l.to_node == join and l.from_node.name in ("Store_hitglow", "FragmentInstances"):
            links.remove(l)
    cnt = [0]

    def N(kind, **kw):
        n = nodes.new(kind); cnt[0] += 1; n.name = f"KF_{cnt[0]:03d}"
        n.location = (4200 + (cnt[0] % 10) * 180, -2600 - (cnt[0] // 10) * 200)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def M(op, a, b=None):
        n = N("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]

    def V(op, a, b=None, scale=None):
        n = N("ShaderNodeVectorMath", operation=op)
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
        return n.outputs["Value"] if op in ("LENGTH", "DOT_PRODUCT") else n.outputs[0]

    def named(name, dt="FLOAT"):
        n = N("GeometryNodeInputNamedAttribute", data_type=dt); n.inputs["Name"].default_value = name
        return n.outputs["Attribute"]

    def sample(obj, field_name, dt, index):
        oi = N("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = obj; oi.transform_space = "ORIGINAL"
        s = N("GeometryNodeSampleIndex", data_type=dt, domain="POINT")
        links.new(oi.outputs["Geometry"], s.inputs["Geometry"])
        if field_name == "position":
            links.new(N("GeometryNodeInputPosition").outputs[0], s.inputs["Value"])
        else:
            links.new(named(field_name, dt), s.inputs["Value"])
        links.new(index, s.inputs["Index"])
        return s.outputs["Value"]

    # store the parent's variant index next to sid / prot / pscale
    ssid = nodes["Store_sid"]
    consumers = [l.to_socket for l in links if l.from_node == ssid]
    inst = next(n for n in nodes if n.bl_idname == "GeometryNodeInstanceOnPoints" and n.name != "FragmentInstances"
                and not n.name.startswith("KF_"))
    pick_src = next(l.from_socket for l in links if l.to_node == inst and l.to_socket.name == "Instance Index")
    sp = N("GeometryNodeStoreNamedAttribute", data_type="INT", domain="POINT"); sp.inputs["Name"].default_value = "ppick"
    links.new(ssid.outputs[0], sp.inputs["Geometry"]); links.new(pick_src, sp.inputs["Value"])
    for s in consumers:
        links.new(sp.outputs[0], s)
    after = sp.outputs[0]

    k = named("ppick", "INT")
    count = sample(vob, "count", "INT", k)
    dup = N("GeometryNodeDuplicateElements"); dup.domain = "POINT"
    links.new(after, dup.inputs["Geometry"])
    links.new(M("MULTIPLY", named("broken"), count), dup.inputs["Amount"])
    di = dup.outputs["Duplicate Index"]
    k2 = named("ppick", "INT")
    gidx = M("ADD", sample(vob, "start", "INT", k2), di)
    cen = sample(tob, "position", "FLOAT_VECTOR", gidx)
    imp = sample(vob, "impact", "FLOAT_VECTOR", named("ppick", "INT"))
    prot = named("prot", "QUATERNION"); psc = named("pscale")

    def rotv(v):
        r = N("FunctionNodeRotateVector"); links.new(v, r.inputs["Vector"]); links.new(prot, r.inputs["Rotation"])
        return r.outputs[0]

    base = V("ADD", N("GeometryNodeInputPosition").outputs[0], rotv(V("SCALE", cen, scale=psc)))
    away_l = V("SUBTRACT", cen, imp)
    dist = M("MULTIPLY", V("LENGTH", away_l), psc)                               # metres from the impact
    away = V("NORMALIZE", rotv(V("MULTIPLY", away_l, (1.0, 1.0, 0.0))))

    def rnd(seed, lo=0.0, hi=1.0, vec=False):
        r = N("FunctionNodeRandomValue", data_type="FLOAT_VECTOR" if vec else "FLOAT")
        r.inputs["Min"].default_value = (lo,) * 3 if vec else lo
        r.inputs["Max"].default_value = (hi,) * 3 if vec else hi
        links.new(M("ADD", M("MULTIPLY", named("sid", "INT"), 53.0), di), r.inputs["ID"])
        r.inputs["Seed"].default_value = seed
        return r.outputs["Value"]

    frame = N("GeometryNodeInputSceneTime").outputs["Frame"]
    dt = M("MAXIMUM", M("DIVIDE", M("SUBTRACT", frame, named("break_f")), 30.0), 0.0)
    creep = V("SCALE", away, scale=M("MULTIPLY", M("MULTIPLY", psc, 0.04), M("MINIMUM", M("DIVIDE", dt, 0.06), 1.0)))
    delay = M("ADD", 0.035, M("MULTIPLY", dist, 0.02))
    tb = M("MAXIMUM", M("SUBTRACT", dt, delay), 0.0)
    drag = G("Frag Drag")
    travel = M("MULTIPLY", drag, M("SUBTRACT", 1.0, M("EXPONENT", M("DIVIDE", M("MULTIPLY", tb, -1.0), drag))))
    near = M("DIVIDE", 1.0, M("ADD", M("DIVIDE", dist, M("MAXIMUM", psc, 0.05)), 0.4))   # small pieces near impact fly fastest
    speed = M("MULTIPLY", M("MULTIPLY", G("Frag Speed"), named("break_v")), M("MULTIPLY", M("ADD", 0.35, M("MULTIPLY", near, 0.5)), rnd(1, 0.7, 1.3)))
    fl = N("ShaderNodeCombineXYZ"); links.new(M("MULTIPLY", G("Toward Camera"), -1.0), fl.inputs[1])
    dirn = V("NORMALIZE", V("ADD", V("ADD", away, fl.outputs[0]), V("SCALE", rnd(2, -1.0, 1.0, vec=True), scale=0.35)))
    off = V("ADD", creep, V("SCALE", dirn, scale=M("MULTIPLY", speed, travel)))
    spos = N("GeometryNodeSetPosition")
    links.new(dup.outputs["Geometry"], spos.inputs["Geometry"]); links.new(V("ADD", base, off), spos.inputs["Position"])

    axis = V("NORMALIZE", rnd(3, -1.0, 1.0, vec=True))
    ang = M("MULTIPLY", M("MULTIPLY", G("Frag Spin"), 6.2832), M("MULTIPLY", M("ADD", travel, M("MULTIPLY", tb, 0.3)),
                                                                      M("MULTIPLY", near, rnd(4, 0.4, 1.4))))
    aa = N("FunctionNodeAxisAngleToRotation"); links.new(axis, aa.inputs["Axis"]); links.new(ang, aa.inputs["Angle"])
    rr = N("FunctionNodeRotateRotation"); rr.rotation_space = "LOCAL"
    links.new(prot, rr.inputs["Rotation"]); links.new(aa.outputs[0], rr.inputs["Rotate By"])

    ci = N("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = col
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    fi = N("GeometryNodeInstanceOnPoints"); fi.name = "KF_Pieces"
    links.new(spos.outputs[0], fi.inputs["Points"]); links.new(ci.outputs[0], fi.inputs["Instance"])
    fi.inputs["Pick Instance"].default_value = True
    links.new(gidx, fi.inputs["Instance Index"]); links.new(rr.outputs[0], fi.inputs["Rotation"])
    links.new(psc, fi.inputs["Scale"])
    links.new(fi.outputs[0], join.inputs[0])
    print("kick fracture branch built; invalid links", sum(1 for l in links if not l.is_valid), flush=True)


def main():
    col, tob, vob = build_kit()
    branch(col, tob, vob)
