"""Low-poly wireframe cages: "the code underneath" the real forest.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns)
    ns["form_material"]()                               # the pale-teal emissive material
    ns["tree_cage"]("fir_tree_01_a_LOD2", "cage_fir_a")  # one cage per kit tree, same local space
    ns["rock_cage"]("rock_moss_set_02_rock11", "cage_rock11")   # also used for ferns: any small object

Two materials: FormWire_Snare (trees) and FormWire_Kick (ferns, rocks) - the snare lights the trees,
the kick lights the low things.

A cage is a coarse, triangulated shell fitted to the real object, turned into real beams with a
Wireframe modifier (WOBAR_VISUAL_RESET build rule: real geometry, not a shader). It lives in the
same local space as its source object, so scattering the cage collection with the same layers and
seeds as the source collection puts every cage exactly on its tree.
"""
import math

import bmesh
import bpy

# The cover's wire colour, sampled from assets/cover-art/hohlweg/hohlweg.png: sRGB #A0BFC9
TEAL_SRGB = (0xA0 / 255, 0xBF / 255, 0xC9 / 255)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def form_material(name="FormWire", strength=0.7):
    mat = bpy.data.materials.get(name)
    if mat is not None and mat.node_tree and mat.node_tree.nodes.get("FormEmission"):
        # Never rebuild an existing form material: clearing its nodes deletes the FORM_CTRL driver on
        # FormEmission, and the wires then glow constantly (found 2026-10-13: every kick wire stayed lit).
        return mat
    mat = mat or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission')
    em.name = "FormEmission"
    em.inputs['Color'].default_value = (*[_lin(c) for c in TEAL_SRGB], 1.0)
    em.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    mat.use_fake_user = True
    return mat


def _rings_to_mesh(rings, sides, cap=True):
    """Stack of rings -> antiprism-triangulated shell. Each ring: (cx, cy, z, radius)."""
    verts, faces = [], []
    for i, (cx, cy, z, r) in enumerate(rings):
        off = (math.pi / sides) * (i % 2)          # alternate rings are rotated: triangles, not quads
        for k in range(sides):
            a = off + 2 * math.pi * k / sides
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    for i in range(len(rings) - 1):
        a0, b0 = i * sides, (i + 1) * sides
        for k in range(sides):
            k1 = (k + 1) % sides
            if i % 2 == 0:
                faces.append((a0 + k, a0 + k1, b0 + k))
                faces.append((a0 + k1, b0 + k1, b0 + k))
            else:
                faces.append((a0 + k, a0 + k1, b0 + k1))
                faces.append((a0 + k, b0 + k1, b0 + k))
    if cap:
        top = len(verts)
        cx, cy, z, _ = rings[-1]
        verts.append((cx, cy, z + 0.6 * rings[-1][3]))
        b = (len(rings) - 1) * sides
        for k in range(sides):
            faces.append((b + k, b + (k + 1) % sides, top))
    return verts, faces


def _pct(vals, p):
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(len(vals) * p))]


def _finish(name, verts, faces, collection, thickness, mat):
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    me.clear_geometry()
    me.from_pydata(verts, [], faces)
    me.materials.clear()
    me.materials.append(mat)
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
    col = bpy.data.collections.get(collection) or bpy.data.collections.new(collection)
    if col.name not in [c.name for c in bpy.data.collections["FORMS"].children]:
        bpy.data.collections["FORMS"].children.link(col)
    if ob.name not in col.objects:
        col.objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    wf = ob.modifiers.new("Beams", 'WIREFRAME')
    wf.thickness = thickness
    wf.use_replace = True
    wf.use_even_offset = False
    ob.visible_shadow = False
    return ob


def tree_cage(src_name, cage_name, collection="CAGE_FIR", trunk_sides=5, trunk_rings=6,
              crown_sides=5, crown_rings=3, thickness=0.02, mat_name="FormWire_Snare", root_depth=1.1):
    """Trunk tube + crown shell fitted to the real tree, in the tree's local space.

    The trunk does not stop at the ground: it carries on down for `root_depth` metres, flaring as it
    goes, so the soil cuts through the cage (the cover: the form is being unearthed, not placed)."""
    src = bpy.data.objects[src_name]
    me = src.data
    slot_kind = []
    for s in src.material_slots:
        n = s.material.name.lower() if s.material else ""
        slot_kind.append("trunk" if ("trunk" in n or "bark" in n) else "crown" if "twig" in n else "other")
    trunk_v, crown_v = set(), set()
    for p in me.polygons:
        k = slot_kind[p.material_index] if p.material_index < len(slot_kind) else "other"
        (trunk_v if k == "trunk" else crown_v if k == "crown" else set()).update(p.vertices)
    tv = [me.vertices[i].co for i in trunk_v]
    cv = [me.vertices[i].co for i in crown_v]
    verts, faces = [], []

    # trunk: slice by height, fit a centre and a radius to each slice
    z0, z1 = min(v.z for v in tv), max(v.z for v in tv)
    rings = []
    for i in range(trunk_rings):
        za = z0 + (z1 - z0) * i / trunk_rings
        zb = z0 + (z1 - z0) * (i + 1) / trunk_rings
        sl = [v for v in tv if za <= v.z <= zb]
        if len(sl) < 6:
            continue
        cx = sum(v.x for v in sl) / len(sl)
        cy = sum(v.y for v in sl) / len(sl)
        r = _pct([math.hypot(v.x - cx, v.y - cy) for v in sl], 0.7)
        rings.append((cx, cy, (za + zb) / 2, max(r * 1.25, 0.05)))
    if root_depth and rings:
        cx, cy, zb, rb = rings[0]
        rings = [(cx, cy, z0 - root_depth, rb * 2.4), (cx, cy, z0 - root_depth * 0.35, rb * 1.7)] + rings
    v, f = _rings_to_mesh(rings, trunk_sides)
    verts += v
    faces += f

    # crown: a faceted spindle around the foliage
    if cv:
        z0, z1 = _pct([v.z for v in cv], 0.03), max(v.z for v in cv)
        rings = []
        for i in range(crown_rings):
            za = z0 + (z1 - z0) * i / crown_rings
            zb = z0 + (z1 - z0) * (i + 1) / crown_rings
            sl = [v for v in cv if za <= v.z <= zb]
            if len(sl) < 12:
                continue
            cx = sum(v.x for v in sl) / len(sl)
            cy = sum(v.y for v in sl) / len(sl)
            r = _pct([math.hypot(v.x - cx, v.y - cy) for v in sl], 0.8)
            rings.append((cx, cy, (za + zb) / 2, r))
        base = len(verts)
        v, f = _rings_to_mesh(rings, crown_sides)
        verts += v
        faces += [tuple(i + base for i in face) for face in f]
    return _finish(cage_name, verts, faces, collection, thickness, form_material(mat_name))


def rock_cage(src_name, cage_name, collection="CAGE_ROCK", target_faces=36, thickness=0.012, inflate=0.02,
              mat_name="FormWire_Kick", root_depth=0.0, root_foot=0.16):
    """Decimated copy of a rock, pushed slightly outward so the beams sit proud of the stone."""
    src = bpy.data.objects[src_name]
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    tmp = bpy.data.meshes.new("_tmp_rock")
    bm.to_mesh(tmp)
    bm.free()
    tob = bpy.data.objects.new("_tmp_rock", tmp)
    bpy.context.scene.collection.objects.link(tob)
    dec = tob.modifiers.new("d", 'DECIMATE')
    dec.ratio = max(target_faces / max(len(tmp.polygons), 1), 0.0005)
    ev = tob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    em = ev.to_mesh()
    verts = [tuple(v.co + v.normal * inflate) for v in em.vertices]
    faces = [tuple(p.vertices) for p in em.polygons]
    ev.to_mesh_clear()
    bpy.data.objects.remove(tob, do_unlink=True)
    bpy.data.meshes.remove(tmp)
    if root_depth:
        # A tight spike under the base, so the form carries on into the soil without widening.
        zs = [v[2] for v in verts]
        zmin, h = min(zs), max(zs) - min(zs)
        low = [v for v in verts if v[2] <= zmin + 0.15 * h] or verts
        cx = sum(v[0] for v in low) / len(low)
        cy = sum(v[1] for v in low) / len(low)
        rad = _pct([math.hypot(v[0] - cx, v[1] - cy) for v in verts], 0.9)
        rings = [(cx, cy, zmin - root_depth * h, root_foot * rad * 0.35),
                 (cx, cy, zmin - root_depth * h * 0.45, root_foot * rad * 0.8),
                 (cx, cy, zmin + 0.04 * h, root_foot * rad)]
        base = len(verts)
        v, f = _rings_to_mesh(rings, 3, cap=False)
        verts += v
        faces += [tuple(i + base for i in face) for face in f]
    return _finish(cage_name, verts, faces, collection, thickness, form_material(mat_name))


def hull_cage(src_name, cage_name, collection="CAGE_FERN", target_faces=22, thickness=0.006, depth=0.45,
              foot=0.5, mat_name="FormWire_Kick"):
    """A faceted shell around a plant that carries on below the ground - the cover's polyhedron.

    Convex hull of the plant plus a ring of points `depth` x its height under its base (`foot` x its
    radius wide), decimated to a few facets. The ground slices through the lower facets, so the form
    reads as half-buried. Used for ferns, whose own decimated fronds read as shards."""
    src = bpy.data.objects[src_name]
    cos = [v.co.copy() for v in src.data.vertices]
    zmin, zmax = min(c.z for c in cos), max(c.z for c in cos)
    cx = sum(c.x for c in cos) / len(cos)
    cy = sum(c.y for c in cos) / len(cos)
    rad = _pct([math.hypot(c.x - cx, c.y - cy) for c in cos], 0.9)
    bm = bmesh.new()
    for c in cos:
        bm.verts.new(c)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        bm.verts.new((cx + foot * rad * math.cos(a), cy + foot * rad * math.sin(a), zmin - depth * (zmax - zmin)))
    res = bmesh.ops.convex_hull(bm, input=bm.verts)
    drop = {g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)}
    bmesh.ops.delete(bm, geom=list(drop), context='VERTS')
    bmesh.ops.triangulate(bm, faces=bm.faces)
    tmp = bpy.data.meshes.new("_tmp_hull")
    bm.to_mesh(tmp)
    bm.free()
    tob = bpy.data.objects.new("_tmp_hull", tmp)
    bpy.context.scene.collection.objects.link(tob)
    dec = tob.modifiers.new("d", 'DECIMATE')
    dec.ratio = min(1.0, max(target_faces / max(len(tmp.polygons), 1), 0.0005))
    ev = tob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    em = ev.to_mesh()
    verts = [tuple(v.co) for v in em.vertices]
    faces = [tuple(p.vertices) for p in em.polygons]
    ev.to_mesh_clear()
    bpy.data.objects.remove(tob, do_unlink=True)
    bpy.data.meshes.remove(tmp)
    return _finish(cage_name, verts, faces, collection, thickness, form_material(mat_name))


def root_cages(roots="BankRoots", lane="Lane", span=(985.0, 1040.0, 1484.0, 1600.0), share=0.35, seed=7,
               every=3, sides=4, pad=0.02, thickness=0.01, mat_name="FormWire_Kick",
               cage_name="RootCages", light_points="RootLightPts", collection="CAGE_ROOTS",
               deep=(984.0, 1219.0, 1484.0, 1600.0), deep_share=0.8, light_share=0.085, min_pts=6):
    """Wireframe tubes around a share of the exposed roots - the kick forms of ABGRUND, where the banks are
    bare walls and the roots are what the cut is made of.

    Each chosen root is followed through every `every`-th control point; a ring of `sides` points sits
    around it there (radius = root radius + `pad`), alternate rings rotated so the faces are triangles.
    Roots are chosen by where they start along the lane: `span` is a trapezoid (in0, in1, out1, out0) in
    metres, times `share`. Also writes `light_points`: one vertex at the middle of each chosen root, for
    instancing the kick light.

    The share rises with the depth of the cut (`deep`, the same stretch as the DepthProfile walls) from
    `share` to `deep_share` - the code shows through most at the bottom of ABGRUND (Nick). Lights stay at
    `light_share` of the roots whatever the depth, so render time does not climb with the wires."""
    import random
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    rng = random.Random(seed)
    dg = bpy.context.evaluated_depsgraph_get()
    le = bpy.data.objects[lane].evaluated_get(dg)
    me = le.to_mesh()
    al = [d.value for d in me.attributes["along"].data]
    kd = KDTree(len(me.vertices))
    for i, v in enumerate(me.vertices):
        kd.insert(le.matrix_world @ v.co, i)
    kd.balance()
    along_of = lambda p: al[kd.find(p)[1]]
    le.to_mesh_clear()

    def weight(a):
        s0, s1, s2, s3 = span
        if a <= s0 or a >= s3:
            return 0.0
        if a < s1:
            return (a - s0) / (s1 - s0)
        if a > s2:
            return (s3 - a) / (s3 - s2)
        return 1.0

    def smooth(x, a, b):
        u = min(max((x - a) / (b - a), 0.0), 1.0)
        return u * u * (3 - 2 * u)

    def depth(a):
        d0, d1, d2, d3 = deep
        return smooth(a, d0, d1) * (1.0 - smooth(a, d2, d3))

    verts, faces, mids = [], [], []
    for sp in bpy.data.objects[roots].data.splines:
        pts = [(Vector(p.co[:3]), p.radius) for p in sp.points]
        if len(pts) < min_pts:
            continue
        a_here = along_of(pts[0][0])
        s_here = (share + (deep_share - share) * depth(a_here)) * weight(a_here)
        if rng.random() > s_here:
            continue
        lit = rng.random() < (light_share / max(share + (deep_share - share) * depth(a_here), 1e-6))
        chain = pts[::every]
        if chain[-1] is not pts[-1]:
            chain.append(pts[-1])
        base0 = len(verts)
        for k, (p, r) in enumerate(chain):
            a = chain[max(k - 1, 0)][0]
            b = chain[min(k + 1, len(chain) - 1)][0]
            t = (b - a).normalized()
            n = t.cross(Vector((0, 0, 1)))
            if n.length < 1e-4:
                n = t.cross(Vector((1, 0, 0)))
            n.normalize()
            bvec = t.cross(n)
            off = (math.pi / sides) * (k % 2)
            for j in range(sides):
                ang = off + 2 * math.pi * j / sides
                verts.append(tuple(p + (n * math.cos(ang) + bvec * math.sin(ang)) * (r + pad)))
        for k in range(len(chain) - 1):
            a0, b0 = base0 + k * sides, base0 + (k + 1) * sides
            for j in range(sides):
                j1 = (j + 1) % sides
                if k % 2 == 0:
                    faces += [(a0 + j, a0 + j1, b0 + j), (a0 + j1, b0 + j1, b0 + j)]
                else:
                    faces += [(a0 + j, a0 + j1, b0 + j1), (a0 + j, b0 + j1, b0 + j)]
        if lit:
            mids.append(tuple(chain[len(chain) // 2][0]))

    ob = _finish(cage_name, verts, faces, collection, thickness, form_material(mat_name))
    lm = bpy.data.meshes.get(light_points) or bpy.data.meshes.new(light_points)
    lm.clear_geometry()
    lm.from_pydata(mids, [], [])
    lo = bpy.data.objects.get(light_points) or bpy.data.objects.new(light_points, lm)
    if lo.name not in bpy.data.collections[collection].objects:
        bpy.data.collections[collection].objects.link(lo)
    lo.hide_render = True
    lo.hide_viewport = True
    return ob, len(mids)
