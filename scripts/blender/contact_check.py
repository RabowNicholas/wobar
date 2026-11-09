"""Check that things rest on the ground: nothing floating, nothing swallowed.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns)
    report = ns["check"](frames=[240, 1200], radius=35.0)
    ns["print_report"](report)

For every instance (and every plain object in `extra`) within `radius` metres of the camera, a sample
of the source mesh's vertices is moved into place and dropped onto the ground with a ray from above:

    gap     smallest signed distance from a sampled vertex to the nearest ground surface (positive =
            on the open side of the surface). Above ~2 cm, nothing touches: the thing hovers.
            (Ground = the full Lane mesh and the forest floor.)
    buried  share of the sampled vertices on the inside of the ground.

The first version dropped vertical rays from above. On the steep, ledged banks that measured the drop
to the next ledge down, so moss lying flat on a wall read as hovering 20-30 cm - distance to the
nearest surface, signed by its normal, is the right measure on walls.

Plants are judged only on their foot (the lowest 8% of their height) - fronds hanging over a slope are
meant to clear it.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

PLANT_HINTS = ("fern", "nettle", "shrub", "sapling", "fir_tree", "moss")
_CACHE = {}


def ground_bvh(names=("Lane", "ForestFloor")):
    key = tuple(names)
    if key in _CACHE:
        return _CACHE[key]
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for n in names:
        ob = bpy.data.objects[n].evaluated_get(dg)
        me = ob.to_mesh()
        base = len(verts)
        mw = ob.matrix_world
        verts += [mw @ v.co for v in me.vertices]
        polys += [tuple(i + base for i in p.vertices) for p in me.polygons]
        ob.to_mesh_clear()
    _CACHE[key] = BVHTree.FromPolygons(verts, polys)
    return _CACHE[key]


def _sample(mesh, n=160):
    vs = mesh.vertices
    step = max(1, len(vs) // n)
    return [vs[i].co.copy() for i in range(0, len(vs), step)]


_SAMPLES = {}


def _verts_of(ob):
    if ob.name not in _SAMPLES:
        _SAMPLES[ob.name] = _sample(ob.data) if ob.type == 'MESH' else []
    return _SAMPLES[ob.name]


def measure(matrix, src, bvh):
    pts = [matrix @ v for v in _verts_of(src)]
    if not pts:
        return None
    zs = [p.z for p in pts]
    zmin, zmax = min(zs), max(zs)
    h = max(zmax - zmin, 1e-4)
    plant = any(k in src.name.lower() for k in PLANT_HINTS)
    foot = [p for p in pts if p.z <= zmin + 0.08 * h] if plant else pts
    gaps, below = [], 0
    for p in pts:
        loc, nor, _, dist = bvh.find_nearest(p, 3.0)
        if loc is None:
            continue
        signed = dist if (p - loc).dot(nor) >= 0 else -dist
        if signed < 0:
            below += 1
        if p in foot or not plant:
            gaps.append(signed)
    if not gaps:
        return None
    return dict(gap=min(gaps), buried=below / len(pts), height=h)


def check(frames, radius=35.0, extra=(), camera="Camera", parents=None):
    sc = bpy.context.scene
    bvh = ground_bvh()
    cam = bpy.data.objects[camera]
    rows = []
    for f in frames:
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.evaluated_get(dg).matrix_world.translation.copy()
        for inst in dg.object_instances:
            if not (inst.is_instance and inst.parent):
                continue
            parent = inst.parent.original.name
            if parents and parent not in parents:
                continue
            if parent.startswith(("Scatter_KickCages", "Scatter_TreeCages", "Scatter_KickLights", "Scatter_SnareLights")):
                continue
            m = inst.matrix_world.copy()
            if (m.translation - cp).length > radius:
                continue
            r = measure(m, inst.object.original, bvh)
            if r:
                rows.append(dict(frame=f, parent=parent, source=inst.object.original.name, **r))
    for name in extra:
        ob = bpy.data.objects[name]
        r = measure(ob.matrix_world, ob, bvh)
        if r:
            rows.append(dict(frame=None, parent="(placed)", source=name, **r))
    return rows


def print_report(rows, float_cm=2.0):
    groups = {}
    for r in rows:
        key = (r["parent"], r["source"].rstrip("0123456789_.").replace("_LOD", ""))
        groups.setdefault(key, []).append(r)
    print("%-22s %-34s %5s %8s %10s %9s" % ("scatter", "source", "n", "floating", "worst gap", "buried"))
    for (p, s), rs in sorted(groups.items()):
        fl = [r for r in rs if r["gap"] > float_cm / 100.0]
        worst = max(r["gap"] for r in rs)
        bur = sum(r["buried"] for r in rs) / len(rs)
        print("%-22s %-34s %5d %7d%% %8.1f cm %8.0f%%" % (p, s[:34], len(rs), 100 * len(fl) / len(rs), worst * 100, bur * 100))
