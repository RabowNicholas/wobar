"""Trim BankLip where it has no ground under it (2026-11-05).

bank_lip.py built the lip from Lane, which is hidden in renders and still runs straight across the landslide gap, so the
lip hung up to 37 m over the slide (along ~1252-1372 m): black "branches" across the sky at the edge (5:29-5:35) and a
dark column in the mist from its moon shadow (5:35-5:40). Nick saw it on the walkthrough.

Per ring (9 verts, consecutive), support = distance from its bank-top vertex to the rendered ground (LaneView evaluated
at frame FR, whose window covers 1216-1456 m, plus SlideTerrain). Rings over SUP_MAX are deleted; rings within TAPER m
(along the lane) of a deleted ring are pulled back toward the bank, so each lip end thins out to nothing with the broken
lane end instead of stopping as a cut slab. Only along 1222-1450 is touched (LaneView at FR covers it).
    LT_FR (7840)  LT_SUP (0.6 m)  LT_TAPER (5.0 m)
"""
import bpy, bmesh, os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.context.scene
if sc.get("lip_slide_trim_applied"): raise SystemExit("lip_slide_trim already applied")
FR = int(os.environ.get("LT_FR", "7840")); SUP = float(os.environ.get("LT_SUP", "0.6")); TAP = float(os.environ.get("LT_TAPER", "5.0"))
sc.frame_set(FR); dg = bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o = bpy.data.objects[n].evaluated_get(dg); m = o.to_mesh(); m.transform(o.matrix_world)
    t = BVHTree.FromPolygons([tuple(v.co) for v in m.vertices], [tuple(p.vertices) for p in m.polygons]); o.to_mesh_clear(); return t
T = [bvh("LaneView"), bvh("SlideTerrain")]
B = bpy.data.objects["BankLip"]; me = B.data; MW = B.matrix_world; MI = MW.inverted()
nv = len(me.vertices); assert nv % 9 == 0, nv
al = np.empty(nv, np.float32); me.attributes["along"].data.foreach_get("value", al)
co = np.empty(nv * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 9, 3)
ra = al.reshape(-1, 9)[:, 0]
zone = (ra > 1222) & (ra < 1450)   # inside the frame-FR LaneView window; the gap is ~1252-1372
sup = np.zeros(len(ra))
for r in np.where(zone)[0]:
    sup[r] = min((t.find_nearest(MW @ Vector(co[r, 0]))[3] or 99.0) for t in T)
dead = zone & (sup > SUP)
# taper: distance (along) to the nearest dead ring on the same side (sides told apart by the ring's lateral sign)
lat = np.empty(nv, np.float32); me.attributes["lat"].data.foreach_get("value", lat); side = np.sign(lat.reshape(-1, 9)[:, 0])
scale = np.ones(len(ra))
for s in (-1, 1):
    da = ra[dead & (side == s)]
    if len(da) == 0: continue
    idx = np.where(zone & ~dead & (side == s))[0]
    gap = np.min(np.abs(ra[idx, None] - da[None, :]), axis=1)
    scale[idx] = np.clip(gap / TAP, 0, 1) ** 1.5
tap = zone & ~dead & (scale < 1)
for r in np.where(tap)[0]:
    anchor = co[r, 1].copy()                          # profile point on the bank top, at the crest
    co[r] = anchor + (co[r] - anchor) * max(scale[r], 0.02)
me.vertices.foreach_set("co", co.ravel()); me.update()
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
kill = [bm.verts[r * 9 + i] for r in np.where(dead)[0] for i in range(9)]
bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
# keep BankLipCrest (roots' target points) consistent: drop crest points over the gap
C = bpy.data.objects.get("BankLipCrest"); cdrop = 0
if C:
    cb = bmesh.new(); cb.from_mesh(C.data)
    bad = [v for v in cb.verts if min((t.find_nearest(C.matrix_world @ v.co)[3] or 99.0) for t in T) > SUP
           and 1222 < (v.co.y) < 1450]
    cdrop = len(bad); bmesh.ops.delete(cb, geom=bad, context='VERTS'); cb.to_mesh(C.data); cb.free()
st = dict(rings_zone=int(zone.sum()), rings_deleted=int(dead.sum()), rings_tapered=int(tap.sum()),
          dead_along=(round(float(ra[dead].min()), 1), round(float(ra[dead].max()), 1)) if dead.any() else None,
          sup_kept_max=round(float(sup[zone & ~dead].max()), 2), crest_dropped=cdrop, verts=len(me.vertices))
sc["lip_slide_trim_applied"] = f"2026-11-05 sup {SUP} taper {TAP}"
print("LT", st, flush=True)
if bpy.app.background and not os.environ.get("LT_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("LT saved", bpy.data.filepath, flush=True)
