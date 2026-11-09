"""Trench roots made to read like real exposed roots (Nick, 2026-11-04, on the 4K reel: "the roots dont touch the
trench walls close enough. this is a cg tell"; then "do the roots look realistic and follow the contour of the wall
like real roots would" -> agreed 1-3 below).

    blender -b hohlweg_3.blend -P root_shape.py                     (saves; refuses a second run - scene key root_shape_applied)
    RS_NOSAVE=1 blender -b ... -P root_shape.py -P <stills script>  (test in memory)

The roots are deformed in place, not regrown, so every form built from them (RootCages, RootletCandidates and their
cages and lights, RootLightPts) keeps its root and is carried along with it.

  1 ON THE WALL   every wall root point is pulled in along the wall normal until RS_BURY of its diameter is sunk
                  (default 0.3); deeper points are left (roots diving into the soil). Before: 15-20% of points stood
                  > 1 cm off the wall, 3-6% > 3 cm (the v2 arch lift, and the wall reshaped after the roots grew).
  2 THICKER TOP   main roots (BankRoots, radius > 1.5 cm) swell toward where they leave the soil: x(1 + RS_THICK) at
                  the start, back to x1 over ~0.7 m - the thick part of a real root is at the bank lip.
  3 LESS COMBED   each wall root gets a sideways run near the top (up to RS_RUN m along the wall, eased in over the
                  first metre) and a slow meander (amplitude RS_WIGGLE m, wavelength 0.8-2.2 m), so the walls stop
                  reading as parallel vertical strands. Branches inherit their parent's displacement where they join,
                  so nothing detaches. Hanging hairs (point spacing < 7 cm) move rigidly with the root they hang from.
After 2-3 the roots are re-projected onto the wall (step 1), so the shape follows the wall's contour.
"""
import bpy, os, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

BURY = float(os.environ.get("RS_BURY", "0.3"))
THICK = float(os.environ.get("RS_THICK", "0.7"))
RUN = float(os.environ.get("RS_RUN", "0.6"))
WIGGLE = float(os.environ.get("RS_WIGGLE", "0.12"))
TOPBURY = float(os.environ.get("RS_TOPBURY", "0.6"))  # main roots sunk this much of their diameter where they leave the soil
LOOPS = int(os.environ.get("RS_LOOPS", "1"))  # straighten loops (a root that curls back on itself within 1.5 m)
REACH = float(os.environ.get("RS_REACH", "3.0"))  # how far off the wall a root point is still pulled onto it
sc = bpy.context.scene
if sc.get("root_shape_applied"):
    raise SystemExit("root_shape already applied")
rng = random.Random(23)
import numpy as np
stats_loops = [0, 0]
Z = Vector((0, 0, 1))

dg = bpy.context.evaluated_depsgraph_get()
lane = bpy.data.objects["Lane"].evaluated_get(dg)
me = lane.to_mesh(); mw = lane.matrix_world
bvh = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
lane.to_mesh_clear()


crest_ob = bpy.data.objects.get("BankLipCrest")
crest_kd = None
if crest_ob is not None and len(crest_ob.data.vertices):
    crest_kd = KDTree(len(crest_ob.data.vertices))
    for i, v in enumerate(crest_ob.data.vertices): crest_kd.insert(crest_ob.matrix_world @ v.co, i)
    crest_kd.balance()


def on_bank_top(q, nor):
    """A root point lying on the flat ground behind a crest: real roots there are underground."""
    if crest_kd is None or nor.z < 0.7: return False
    c, _, d = crest_kd.find(q)
    return d < 1.2 and q.z > c.z - 0.25


def wall(p, reach=1.5):
    hit, nor, _, _ = bvh.find_nearest(p, reach)
    if hit is not None and nor.z < -0.2:
        nor = -nor
    return hit, nor


# ---- gather every spline of both root objects
S = []          # dict(ob, sp, P(world), R(world radius), hair, main)
for name in ("BankRoots", "BankRootsFine"):
    ob = bpy.data.objects[name]; M = ob.matrix_world; bev = ob.data.bevel_depth
    for sp in ob.data.splines:
        if len(sp.points) < 2:
            continue
        P = [M @ p.co.xyz for p in sp.points]
        seg = sum((P[i + 1] - P[i]).length for i in range(len(P) - 1)) / (len(P) - 1)
        S.append(dict(ob=ob, sp=sp, P=P, R=[p.radius * bev for p in sp.points], hair=seg < 0.07,
                      main=(name == "BankRoots")))

# ---- own displacement (3): sideways run + meander, along the wall, eased in from the root's start
for s in S:
    P = s["P"]; n = len(P)
    s["own"] = [Vector() for _ in P]
    if s["hair"]:
        continue
    if LOOPS and n > 4:
        A = np.array([p[:] for p in P]); arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(A, axis=0), axis=1))])
        i = 0
        while i < n - 2:
            best = -1
            for j in range(i + 2, n):
                da = arc[j] - arc[i]
                if da > 1.5: break
                if da > 0.25 and np.linalg.norm(A[j] - A[i]) < 0.4 * da: best = j
            if best > 0:
                for k in range(i + 1, best):
                    t = (arc[k] - arc[i]) / (arc[best] - arc[i])
                    s["own"][k] += Vector(A[i] + (A[best] - A[i]) * t) - P[k]
                stats_loops[0] += 1; i = best
            else:
                i += 1
    acc = [0.0]
    for i in range(n - 1):
        acc.append(acc[-1] + (P[i + 1] - P[i]).length)
    run = rng.uniform(0.3, 1.0) * RUN * rng.choice((-1, 1))
    amp = rng.uniform(0.4, 1.0) * WIGGLE * (1.0 if s["main"] else 0.5)
    lam, ph = rng.uniform(0.8, 2.2), rng.uniform(0, 2 * math.pi)
    for i, p in enumerate(P):
        hit, nor = wall(p)
        if hit is None:
            continue
        side = nor.cross(Z)
        if side.length < 1e-3:
            continue
        side.normalize()
        u = acc[i]
        ease = min(u / 1.0, 1.0); ease = ease * ease * (3 - 2 * ease)
        lat = run * ease + amp * min(u / 0.3, 1.0) * math.sin(2 * math.pi * u / lam + ph)
        s["own"][i] += side * lat

# ---- branches inherit the parent's displacement at the join (iterate: children are written before parents)
pts_all = [(si, i) for si, s in enumerate(S) for i in range(len(s["P"]))]
kd = KDTree(len(pts_all))
for k, (si, i) in enumerate(pts_all):
    kd.insert(S[si]["P"][i], k)
kd.balance()
parent = {}
for si, s in enumerate(S):
    for co, k, dist in kd.find_n(s["P"][0], 6):
        sj, j = pts_all[k]
        # a parent is written after its children within one object (grow() appends on return), and a fine root's
        # parent may be a main - this order rules out cycles where two roots merely cross
        ok = (S[sj]["ob"] == s["ob"] and sj > si) or (not s["main"] and S[sj]["main"])
        if ok and dist < 0.03:
            parent[si] = (sj, j); break
for s in S:
    s["tot"] = [v.copy() for v in s["own"]]
for _ in range(4):
    for si, (sj, j) in parent.items():
        base = S[sj]["tot"][j]
        S[si]["tot"] = [o + base for o in S[si]["own"]] if not S[si]["hair"] else [base.copy() for _ in S[si]["P"]]

# ---- (2) thicker toward the lip, then (1) back onto the wall with the new radius
stats = dict(points=0, onto_wall=0, swelled=0, hairs=0, max_move_m=0.0)
before, after_pos, ratio = [], [], []
for s in S:
    P, R = s["P"], s["R"]
    acc = [0.0]
    for i in range(len(P) - 1):
        acc.append(acc[-1] + (P[i + 1] - P[i]).length)
    newR = list(R)
    if s["main"] and max(R) > 0.015:
        newR = [r * (1 + THICK * math.exp(-acc[i] / 0.7)) for i, r in enumerate(R)]
        stats["swelled"] += 1
    Q = [p + d for p, d in zip(P, s["tot"])]
    if True:  # hairs too: hanging curtains are draped onto the face below (Nick: "they hang off of the wall")
        if s["hair"]: stats["hairs"] += 1
        for i, q in enumerate(Q):
            hit, nor = wall(q, REACH)
            if hit is None:
                continue
            gap = (q - hit).dot(nor) - newR[i]
            bury = BURY + (TOPBURY - BURY) * math.exp(-acc[i] / 0.6) if s["main"] else BURY
            target = -bury * 2 * newR[i]
            if on_bank_top(q, nor):
                target = -2 * newR[i] - 0.01; stats["buried_on_top"] = stats.get("buried_on_top", 0) + 1
            if gap > target:
                Q[i] = q - nor * (gap - target); stats["onto_wall"] += 1
        # smooth the correction lightly so pulled points don't kink
        Q = [Q[0]] + [(Q[i - 1] + 2 * Q[i] + Q[i + 1]) / 4 for i in range(1, len(Q) - 1)] + [Q[-1]]
        # second loop pass on the final shape: the wall projection can fold a root into a hairpin or ring
        if LOOPS and not s["hair"] and len(Q) > 4:
            for _ in range(3):
                A = np.array([q[:] for q in Q]); arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(A, axis=0), axis=1))])
                hit_any = False; i = 0
                while i < len(Q) - 2:
                    best = -1
                    for j in range(i + 2, len(Q)):
                        da = arc[j] - arc[i]
                        if da > 2.0: break
                        if da > 0.15 and np.linalg.norm(A[j] - A[i]) < 0.5 * da: best = j
                    if best > 0:
                        for k in range(i + 1, best):
                            t = (arc[k] - arc[i]) / (arc[best] - arc[i])
                            q = Vector(A[i] + (A[best] - A[i]) * t)
                            hit, nor = wall(q, REACH)
                            if hit is not None:
                                gap = (q - hit).dot(nor) - newR[k]
                                q = q - nor * (gap + BURY * 2 * newR[k])
                            Q[k] = q
                        stats_loops[1] += 1; hit_any = True; i = best
                    else:
                        i += 1
                if not hit_any: break
    s["Q"], s["newR"], s["acc"] = Q, newR, acc


def target_of(s, i, q, nor):
    r = s["newR"][i]
    bury = BURY + (TOPBURY - BURY) * math.exp(-s["acc"][i] / 0.6) if s["main"] else BURY
    return -2 * r - 0.01 if on_bank_top(q, nor) else -bury * 2 * r


def corners(pts, deg=60.0):
    """interior points where the root turns sharper than `deg` - straight chords and hairpins read as CG"""
    c = 0
    for i in range(1, len(pts) - 1):
        a, b = pts[i] - pts[i - 1], pts[i + 1] - pts[i]
        if a.length > 1e-5 and b.length > 1e-5 and math.degrees(a.angle(b)) > deg: c += 1
    return c


# ---- (4) smooth out the corners the chords and the wall projection leave, then re-seat on the wall (pull in only).
# Done after every root has its shape, so branch starts can snap to their parent's final point.
SMOOTH = int(os.environ.get("RS_SMOOTH", "4"))
k_before = k_after = 0
for s in S:
    if s["hair"]: continue
    Q = s["Q"]; k_before += corners(Q)
    for _ in range(SMOOTH):
        if len(Q) < 3: break
        Q = [Q[0]] + [(Q[i - 1] + 2 * Q[i] + Q[i + 1]) / 4 for i in range(1, len(Q) - 1)] + [Q[-1]]
    for i, q in enumerate(Q):
        hit, nor = wall(q, REACH)
        if hit is None: continue
        gap = (q - hit).dot(nor) - s["newR"][i]; t = target_of(s, i, q, nor)
        if gap > t: Q[i] = q - nor * (gap - t)
    s["Q"] = Q; k_after += corners(Q)
for _ in range(4):
    for si, (sj, j) in parent.items():
        S[si]["Q"][0] = S[sj]["Q"][j].copy()
stats["corners_gt60_before_smooth"] = k_before; stats["corners_gt60_after"] = k_after
stats["corners_gt60_original"] = sum(corners(s["P"]) for s in S if not s["hair"])

for s in S:
    P, R, Q, newR = s["P"], s["R"], s["Q"], s["newR"]
    Mi = s["ob"].matrix_world.inverted(); bev = s["ob"].data.bevel_depth
    for pt, p, q, r0, r1 in zip(s["sp"].points, P, Q, R, newR):
        pt.co = (*(Mi @ q), pt.co[3]); pt.radius = r1 / bev
        before.append(p); after_pos.append(q); ratio.append(r1 / max(r0, 1e-6))
        stats["max_move_m"] = max(stats["max_move_m"], (q - p).length)
    stats["points"] += len(P)

# ---- carry every form built from the roots: nearest original root point -> its move, rings scaled with the radius
kd2 = KDTree(len(before))
for i, p in enumerate(before):
    kd2.insert(p, i)
kd2.balance()


def carry(name, ring=4, radius=0.3, scale_rings=True):
    """Cages are rings of `ring` consecutive vertices around a root point: the ring's centre finds its root point,
    and the whole ring moves (and scales) with it. Per-vertex lookup tore cages where two roots pass close."""
    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != 'MESH':
        stats[name] = "missing"; return
    M = ob.matrix_world; Mi = M.inverted(); k = 0
    vs = ob.data.vertices
    for a in range(0, len(vs) - ring + 1, ring):
        grp = [M @ vs[a + j].co for j in range(ring)]
        c = sum(grp, Vector()) / ring
        _, i, dist = kd2.find(c)
        if dist > radius:
            continue
        for j, p in enumerate(grp):
            off = p - before[i]
            vs[a + j].co = Mi @ (after_pos[i] + (off * ratio[i] if scale_rings else off))
            k += 1
    ob.data.update()
    stats[name] = f"{k}/{len(vs)} verts"


carry("RootCages"); carry("RootletCandidates"); carry("RootLightPts", ring=1, scale_rings=False)
stats["max_move_m"] = round(stats["max_move_m"], 3); stats["loops_straightened"] = stats_loops[0]; stats["loops_final_pass"] = stats_loops[1]
mv = sorted((q - p).length for p, q in zip(before, after_pos))
stats["move_p50_p99_m"] = (round(mv[len(mv) // 2], 3), round(mv[int(len(mv) * 0.99)], 3))
mv = sorted((q - p).length for p, q in zip(before, after_pos))
stats["move_p50_p99_m"] = (round(mv[len(mv) // 2], 3), round(mv[int(len(mv) * 0.99)], 3))
sc["root_shape_applied"] = f"2026-11-04 bury {BURY} thick {THICK} run {RUN} wiggle {WIGGLE}"
print("RS", stats, flush=True)
if bpy.app.background and not os.environ.get("RS_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("RS saved", bpy.data.filepath, flush=True)
