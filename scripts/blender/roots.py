"""Exposed tree roots running down the banks of the lane.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns); ns["build_roots"]()

A sunken lane cuts through the root plates of the trees on its rim, so their roots hang out of the
banks. For every fir standing near the edge, a few roots are walked from the tree's base toward the
lane: each step moves across the ground, is dropped onto the lane surface, and is lifted off it by an
arching profile, so the root dives into the soil at both ends and stands proud between. All roots are
splines of one curve object (`BankRoots`) with a round bevel and a tapering radius.

Static: rerun after the lane or the tree scatter changes.
"""
import math
import random

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


def _tree_bases(scatter="Scatter_Trees", prefix="fir_tree", frame_step=150, frame_end=None):
    """World position and scale of every scattered fir (the scatter is camera-culled, so walk the shot)."""
    sc = bpy.context.scene
    keep = sc.frame_current
    found = {}
    for f in range(sc.frame_start, (frame_end or sc.frame_end) + 1, frame_step):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        for inst in dg.object_instances:
            if inst.is_instance and inst.parent and inst.parent.original.name == scatter \
                    and inst.object.original.name.startswith(prefix):
                p = inst.matrix_world.translation
                found[(round(p.x, 2), round(p.y, 2))] = (p.copy(), inst.matrix_world.to_scale().x)
    sc.frame_set(keep)
    return list(found.values())


def build_roots(obj_name="BankRoots", collection="LANE", seed=7, per_tree=(2, 4), lat_range=(2.2, 5.4),
                length=(1.6, 4.8), radius=(0.025, 0.11), arch=(0.02, 0.11), stop_lat=1.25,
                material="fir_tree_01_bark", step=0.22, frame_end=None,
                deep=(1040.0, 1550.0), deep_per_tree=(6, 10), deep_lat_max=7.5, deep_traverse=0.2):
    """`deep`: the stretch (metres along) of ABGRUND's full-height walls, where the cut is mostly roots -
    there trees further back from the edge send roots down too (`deep_lat_max`), each sends more
    (`deep_per_tree`), and most hang straight down the wall instead of traversing it."""
    rng = random.Random(seed)
    dg = bpy.context.evaluated_depsgraph_get()
    lane = bpy.data.objects["Lane"].evaluated_get(dg)
    me = lane.to_mesh()
    mw = lane.matrix_world
    cos = [mw @ v.co for v in me.vertices]
    lat = [d.value for d in me.attributes["lat"].data]
    along = [d.value for d in me.attributes["along"].data]
    bvh = BVHTree.FromPolygons(cos, [tuple(p.vertices) for p in me.polygons])
    kd = KDTree(len(cos))
    centre = [c for c, la in zip(cos, lat) if abs(la) < 0.06]
    for i, c in enumerate(cos):
        kd.insert(c, i)
    kd.balance()
    kc = KDTree(len(centre))
    for i, c in enumerate(centre):
        kc.insert(Vector((c.x, c.y, 0.0)), i)
    kc.balance()
    lane.to_mesh_clear()

    def ground(x, y, z):
        hit, nor, _, _ = bvh.ray_cast(Vector((x, y, z + 4.0)), Vector((0, 0, -1)), 12.0)
        return hit, nor

    def walk(start, heading, n_steps, r0, lift, arches):
        pts = []
        x, y, z = start.x, start.y, start.z
        for i in range(n_steps + 1):
            u = i / n_steps
            hit, nor = ground(x, y, z)
            if hit is None:
                break
            if abs(lat[kd.find(hit)[1]]) < stop_lat:
                break
            z = hit.z
            # proud of the soil in the middle, buried at both ends
            off = lift * math.sin(math.pi * u * arches) ** 2 + 0.015 - 0.07 * (u ** 6) - 0.05 * ((1 - u) ** 8)
            r = r0 * (1.0 - u) ** 0.8 + 0.007
            pts.append((hit + nor * (off + r * 0.4), r))
            heading += rng.uniform(-0.4, 0.4)
            x += math.cos(heading) * step
            y += math.sin(heading) * step
        return pts

    splines = []
    n_trees = 0
    for base, scale in _tree_bases(frame_end=frame_end):
        hit, _ = ground(base.x, base.y, base.z)
        if hit is None:
            continue
        vi = kd.find(hit)[1]
        la = abs(lat[vi])
        in_deep = deep[0] <= along[vi] <= deep[1]
        if not (lat_range[0] <= la <= (deep_lat_max if in_deep else lat_range[1])):
            continue
        n_trees += 1
        c = centre[kc.find(Vector((base.x, base.y, 0.0)))[1]]
        to_lane = math.atan2(c.y - base.y, c.x - base.x)
        for _ in range(rng.randint(*(deep_per_tree if in_deep else per_tree))):
            # On a steep bank anything heading for the lane reads as a straight line down the wall, so
            # half the roots traverse: they run along the bank and only drift downhill.
            if rng.random() < (deep_traverse if in_deep else 0.5):
                heading = to_lane + rng.choice((-1, 1)) * rng.uniform(1.0, 1.45)
            else:
                heading = to_lane + rng.uniform(-0.9, 0.9)
            r0 = rng.uniform(*radius) * min(max(scale, 0.6), 1.3)
            start = hit + Vector((math.cos(heading), math.sin(heading), 0.0)) * rng.uniform(0.1, 0.3) * scale
            n = int(rng.uniform(*length) / step)
            pts = walk(start, heading, n, r0, rng.uniform(*arch), rng.choice((1, 1, 2, 2, 3)))
            if len(pts) >= 5:
                splines.append(pts)
                if rng.random() < 0.55:      # a side root
                    k = rng.randint(2, max(3, len(pts) // 2))
                    p, r = pts[k]
                    side = walk(p, heading + rng.choice((-1, 1)) * rng.uniform(0.5, 1.1), int(n * 0.5), r * 0.6,
                                rng.uniform(arch[0], arch[1] * 0.6), rng.choice((1, 2)))
                    if len(side) >= 5:
                        splines.append(side)

    cu = bpy.data.curves.get(obj_name) or bpy.data.curves.new(obj_name, 'CURVE')
    cu.splines.clear()
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0            # point radius is then the root's radius in metres
    cu.bevel_resolution = 2
    cu.resolution_u = 3
    cu.use_fill_caps = True
    for pts in splines:
        sp = cu.splines.new('NURBS')
        sp.points.add(len(pts) - 1)
        for pt, (co, r) in zip(sp.points, pts):
            pt.co = (co.x, co.y, co.z, 1.0)
            pt.radius = r
        sp.order_u = 4
        sp.use_endpoint_u = True
        sp.use_smooth = True
    ob = bpy.data.objects.get(obj_name)
    if ob is None:
        ob = bpy.data.objects.new(obj_name, cu)
        bpy.data.collections[collection].objects.link(ob)
    cu.materials.clear()
    cu.materials.append(bpy.data.materials[material])
    return ob, n_trees, len(splines)


# ---------------------------------------------------------------------------------------------------
# v2 (2026-10-14, Nick: "push the roots ... to look more realistic and be scattered more realistically").
# v1 roots walked straight down the walls as a curtain of even ropes. v2 grows each root over the
# surface of the lane mesh: buried while the ground is flat (the rim), exposed where the cut is steep,
# running sideways near the top before gravity wins, meandering with kinks, branching two levels and
# tapering to millimetres, with fine roots hanging free below. Main roots and their first branches go
# to `BankRoots` (the root forms are built from these); finer branches and hanging hairs go to
# `BankRootsFine`.

def build_roots_v2(obj_name="BankRoots", fine_name="BankRootsFine", collection="LANE", seed=11,
                   per_tree=(3, 5), deep_per_tree=(6, 9), lat_range=(2.2, 5.4), deep_lat_max=7.5,
                   deep=(1040.0, 1550.0), wall_len=(1.0, 3.8), radius=(0.03, 0.11), step=0.1,
                   stop_lat=1.25, steep=0.72, material="RootBark", frame_end=None, trees=None):
    rng = random.Random(seed)
    dg = bpy.context.evaluated_depsgraph_get()
    lane = bpy.data.objects["Lane"].evaluated_get(dg)
    me = lane.to_mesh()
    mw = lane.matrix_world
    cos = [mw @ v.co for v in me.vertices]
    lat = [d.value for d in me.attributes["lat"].data]
    along = [d.value for d in me.attributes["along"].data]
    bvh = BVHTree.FromPolygons(cos, [tuple(p.vertices) for p in me.polygons])
    kd = KDTree(len(cos))
    for i, c in enumerate(cos):
        kd.insert(c, i)
    kd.balance()
    centre = [c for c, la in zip(cos, lat) if abs(la) < 0.06]
    kc = KDTree(len(centre))
    for i, c in enumerate(centre):
        kc.insert(Vector((c.x, c.y, 0.0)), i)
    kc.balance()
    lane.to_mesh_clear()
    down = Vector((0, 0, -1))

    def surf(p):
        hit, nor, _, _ = bvh.find_nearest(p, 3.0)
        if hit is None:
            return None, None
        if nor.dot(Vector((0, 0, 1))) < -0.2:        # back face of a slumped lobe
            nor = -nor
        return hit, nor

    def rotate_about(v, axis, ang):
        from mathutils import Matrix
        return Matrix.Rotation(ang, 3, axis) @ v

    mains, fines = [], []

    def hang(p, n_out, length, r0):
        """A fine root dangling free of the wall."""
        pts, d = [], (down + Vector((rng.gauss(0, 0.25), rng.gauss(0, 0.25), 0))).normalized()
        q = p + n_out * r0
        steps = max(3, int(length / 0.05))
        for i in range(steps + 1):
            u = i / steps
            pts.append((q.copy(), r0 * (1 - u) ** 0.7 + 0.0008))
            d = (d + Vector((rng.gauss(0, 0.18), rng.gauss(0, 0.18), -0.25))).normalized()
            q = q + d * 0.05 + n_out * 0.004
        fines.append(pts)

    def grow(start, d, r0, length, depth, sinker=False):
        """Walk over the surface. `length` counts exposed (wall) metres."""
        pts, p = [], start.copy()
        wall_m, buried_m, omega = 0.0, 0.0, 0.0
        emerged, lift = depth > 0, rng.uniform(0.0, 0.07 if depth == 0 else 0.03)   # branches start on the wall
        arches = rng.choice((1, 2, 2, 3))
        while True:
            hit, nor = surf(p)
            if hit is None:
                break
            la = abs(lat[kd.find(hit)[1]])
            if la < stop_lat:
                break
            is_wall = nor.z < steep
            if not is_wall and not emerged:
                buried_m += step
                if buried_m > 3.5:
                    return
            if is_wall and not emerged:
                emerged = True
                # turn on the wall: most roots traverse near the top, the rest head downhill
                g = (down - nor * down.dot(nor)).normalized()
                side = nor.cross(g).normalized() * rng.choice((-1, 1))
                ang = rng.uniform(0.0, 0.45) if sinker else (rng.uniform(1.0, 1.5) if rng.random() < 0.75 else rng.uniform(0.3, 0.8))
                d = (g * math.cos(ang) + side * math.sin(ang)).normalized()
            u = min(wall_m / length, 1.0)
            r = r0 * (1 - u) ** 1.15 + 0.0025
            if emerged:
                off = r * 0.55 + lift * math.sin(math.pi * u * arches) ** 2 - 0.06 * u ** 8
            else:
                off = -r * 1.6                                  # under the rim soil
            pts.append((hit + nor * off, r))
            if emerged:
                wall_m += step
                if wall_m >= length:
                    break
                # branching: dense near where the root leaves the soil (the tangle), sparse lower
                pb = (0.22 if wall_m < 0.7 else 0.07) if depth < 2 else 0.0
                if r > 0.006 and rng.random() < pb:
                    cd = rotate_about(d, nor, rng.choice((-1, 1)) * rng.uniform(0.45, 1.2))
                    grow(hit + nor * off, cd, r * rng.uniform(0.4, 0.65),
                         rng.uniform(0.3, 1.0) * (length - wall_m + 0.3), depth + 1)
                if rng.random() < (0.05 if depth < 2 else 0.02):
                    for _ in range(rng.randint(1, 3)):
                        hang(hit + nor * off, nor, rng.uniform(0.12, 0.6), rng.uniform(0.0012, 0.0035))
            # steer: meander (smoothed turn rate), occasional kink, gravity growing with wall length
            omega = omega * 0.75 + rng.gauss(0, 0.16)
            turn = omega + (rng.choice((-1, 1)) * rng.uniform(0.35, 0.7) if rng.random() < 0.06 else 0.0)
            d = rotate_about(d, nor, turn)
            if emerged:
                g = (down - nor * down.dot(nor))
                if g.length > 1e-4:
                    gw = (0.12 + 0.25 * min(wall_m / 2.0, 1.0)) if sinker else 0.02 + 0.22 * min(wall_m / 2.5, 1.0) ** 2
                    d = (d + g.normalized() * gw).normalized()
            d = (d - nor * d.dot(nor))
            if d.length < 1e-4:
                break
            d.normalize()
            p = hit + d * step
        if len(pts) >= 4 and emerged:
            (mains if depth <= 1 else fines).append(pts)
            if depth == 0 and rng.random() < 0.6:                # hair at the tip
                q, rr = pts[-1]
                hit, nor = surf(q)
                if nor is not None:
                    for _ in range(rng.randint(2, 5)):
                        hang(q, nor, rng.uniform(0.2, 0.8), rng.uniform(0.0015, 0.004))

    n_trees = 0
    for base, scale in (trees if trees is not None else _tree_bases(frame_end=frame_end)):
        hit, _ = surf(base)
        if hit is None:
            continue
        vi = kd.find(hit)[1]
        la = abs(lat[vi])
        in_deep = deep[0] <= along[vi] <= deep[1]
        if not (lat_range[0] <= la <= (deep_lat_max if in_deep else lat_range[1])):
            continue
        n_trees += 1
        c = centre[kc.find(Vector((base.x, base.y, 0.0)))[1]]
        to_lane = math.atan2(c.y - base.y, c.x - base.x)
        for _ in range(rng.randint(*(deep_per_tree if in_deep else per_tree))):
            h = to_lane + rng.uniform(-1.1, 1.1)
            d = Vector((math.cos(h), math.sin(h), 0.0))
            r0 = rng.uniform(*radius) * min(max(scale, 0.6), 1.3)
            start = hit + d * rng.uniform(0.15, 0.4) * scale
            sinker = rng.random() < (0.45 if in_deep else 0.2)       # old roots that run down the full wall
            L = rng.uniform(3.0, 8.0) if sinker else rng.uniform(*wall_len) * (1.3 if in_deep else 1.0)
            grow(start, d, r0, L, 0, sinker)

    def write(name, groups, bevel_res, res_u):
        cu = bpy.data.curves.get(name) or bpy.data.curves.new(name, 'CURVE')
        cu.splines.clear()
        cu.dimensions = '3D'
        cu.bevel_depth = 1.0
        cu.bevel_resolution = bevel_res
        cu.resolution_u = res_u
        cu.use_fill_caps = True
        for pts in groups:
            sp = cu.splines.new('NURBS')
            sp.points.add(len(pts) - 1)
            for pt, (co, r) in zip(sp.points, pts):
                pt.co = (co.x, co.y, co.z, 1.0)
                pt.radius = r
            sp.order_u = 4
            sp.use_endpoint_u = True
            sp.use_smooth = True
        ob = bpy.data.objects.get(name)
        if ob is None:
            ob = bpy.data.objects.new(name, cu)
            bpy.data.collections[collection].objects.link(ob)
        cu.materials.clear()
        cu.materials.append(bpy.data.materials[material])
        return ob

    root_bark(material)
    write(obj_name, mains, 2, 3)
    write(fine_name, fines, 0, 2)
    return n_trees, len(mains), len(fines)


def root_bark(name="RootBark", bark="fir_tree_01_bark"):
    """Bark caked with soil: the fir bark, darkened and mixed toward wet loam in noisy patches."""
    src = bpy.data.materials[bark]
    m = bpy.data.materials.get(name)
    if m is None:
        m = src.copy()
        m.name = name
    nt = m.node_tree
    if "SoilCake" in nt.nodes:
        return m
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col_in = bsdf.inputs["Base Color"]
    src_sock = col_in.links[0].from_socket if col_in.links else None
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6.0; nz.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.name = "SoilMask"
    ramp.inputs["From Min"].default_value = 0.42; ramp.inputs["From Max"].default_value = 0.62
    ramp.inputs["To Min"].default_value = 0.1; ramp.inputs["To Max"].default_value = 0.5
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.name = "SoilCake"; mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (0.11, 0.085, 0.06, 1.0)     # dry loam
    nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    if src_sock:
        dark = nt.nodes.new("ShaderNodeHueSaturation"); dark.inputs["Value"].default_value = 1.1; dark.inputs["Saturation"].default_value = 0.6   # weathered, greyer
        nt.links.new(src_sock, dark.inputs["Color"])
        nt.links.new(dark.outputs["Color"], mix.inputs["A"])
    nt.links.new(mix.outputs["Result"], col_in)
    rough = bsdf.inputs["Roughness"]
    if not rough.links:
        rough.default_value = 0.8
    return m
