"""Soil lip over the trench crest (Nick 2026-11-04, "do 1-3": roots read as hanging off the wall because the crest is a
clean crease with nothing over the root tops). Builds BankLip: a turf/soil overhang along both crests of Lane, so the
roots come out from under soil. Overhang 0.1-0.4 m, thickness 0.25-0.5 m, broken in places; tapers out where the wall
is under ~1.5 m. Carries Lane's point attributes (lat/along/prof_h/...) and UVs from the nearest Lane vertex so
LaneGround shades it as bank-top soil.
    LIP_O (overhang scale, 1.0)  LIP_T (thickness scale, 1.0)
"""
import bpy, bmesh, os, math
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
sc = bpy.context.scene
if sc.get("bank_lip_applied"): raise SystemExit("bank_lip already applied")
OS = float(os.environ.get("LIP_O", "1.0")); TS = float(os.environ.get("LIP_T", "1.0"))
dg = bpy.context.evaluated_depsgraph_get()
L = bpy.data.objects["Lane"]; Le = L.evaluated_get(dg); me = Le.to_mesh(); MW = Le.matrix_world
NC = 340; n = len(me.vertices); NS = n // NC
co = np.empty(n * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(NS, NC, 3)
nr = np.empty(n * 3, np.float32); me.vertices.foreach_get("normal", nr); nr = nr.reshape(NS, NC, 3)
def att(nm):
    a = me.attributes[nm]; v = np.empty(len(a.data), np.float32); a.data.foreach_get("value", v); return v
lat = att("lat").reshape(NS, NC); al = att("along").reshape(NS, NC)
# smooth noise along the trench
rng = np.random.default_rng(31)
def nz(x, waves):
    return sum(a * np.sin(2 * math.pi * x / l + rng.uniform(0, 2 * math.pi)) for a, l in waves) / sum(a for a, _ in waves)
s_al = al[:, NC // 2]
verts, faces = [], []
stat = dict(stations=NS, rings=0)
crest_out = []
for side in (1, -1):
    crest = np.zeros((NS, 3)); ok = np.zeros(NS, bool); inward = np.zeros((NS, 3)); height = np.zeros(NS)
    for k in range(NS):
        l = lat[k] * side; js = np.where((l > 3.3) & (nr[k, :, 2] > 0.8))[0]
        if len(js) == 0: continue
        j = js[np.argmin(l[js])]
        c = co[k, j]; ctr = co[k, np.argmin(np.abs(lat[k]))]
        u = ctr - c; u[2] = 0; ln = np.linalg.norm(u)
        if ln < 1e-3: continue
        crest[k] = c; inward[k] = u / ln; ok[k] = True; height[k] = c[2] - co[k, :, 2].min()
    # smooth the crest line and its frame (the grid's crest index jumps between stations)
    w = 9; ker = np.ones(w) / w
    for arr in (crest, inward):
        for d in range(3): arr[:, d] = np.convolve(np.pad(arr[:, d], w // 2, mode="edge"), ker, "valid")
    inward /= np.linalg.norm(inward, axis=1, keepdims=True) + 1e-9
    amp = np.clip((height - 1.0) / 1.5, 0, 1); amp = amp * amp * (3 - 2 * amp)
    O = OS * (0.1 + 0.3 * (0.5 + 0.5 * nz(s_al, [(1, 7.3), (0.6, 2.9), (0.3, 1.1)])))
    T = TS * (0.25 + 0.25 * (0.5 + 0.5 * nz(s_al, [(1, 5.1), (0.5, 1.7)])))
    brk = np.clip(nz(s_al, [(1, 13.0), (0.7, 4.3)]) * 3 + 2.2, 0, 1)   # occasional collapsed stretches
    O = O * amp * brk; T = T * np.maximum(amp, 0.0) * (0.4 + 0.6 * brk)
    for k in range(0, NS, 2):
        if ok[k] and height[k] > 1.0: crest_out.append(tuple(MW @ Vector(crest[k])))
    base = len(verts); prev = None
    for k in range(NS):
        if not ok[k] or amp[k] <= 0.02:
            prev = None; continue
        c = Vector(crest[k]); u = Vector(inward[k]); z = Vector((0, 0, 1)); o = float(O[k]); t = float(T[k])
        prof = [(-0.45, -0.15), (-0.12, 0.02), (o * 0.55, 0.05), (o * 0.95, 0.0), (o * 1.05, -t * 0.45),
                (o * 0.85, -t * 0.9), (o * 0.35, -t * 1.05), (-0.1, -t * 1.15), (-0.4, -t * 1.0)]
        ring = []
        for a, b in prof:
            ring.append(len(verts)); verts.append(MW @ (c + u * a + z * b))
        if prev is not None:
            for i in range(len(ring) - 1):
                f = (prev[i], prev[i + 1], ring[i + 1], ring[i])
                faces.append(f if side > 0 else f[::-1])
        prev = ring; stat["rings"] += 1
mesh = bpy.data.meshes.new("BankLip"); mesh.from_pydata([tuple(v) for v in verts], [], faces); mesh.validate()
# carry Lane's point attributes and UVs from the nearest Lane vertex
flat = co.reshape(-1, 3); kd = KDTree(len(flat))
for i, p in enumerate(flat): kd.insert(p, i)
kd.balance()
near = np.array([kd.find(v)[1] for v in verts])
for a in me.attributes:
    if a.domain == 'POINT' and a.data_type == 'FLOAT' and not a.name.startswith('.'):
        v = np.empty(len(a.data), np.float32); a.data.foreach_get("value", v)
        na = mesh.attributes.new(a.name, 'FLOAT', 'POINT'); na.data.foreach_set("value", v[near])
uvsrc = me.uv_layers.get("UVMap") or (me.uv_layers[0] if me.uv_layers else None)
if uvsrc:
    vuv = np.zeros((n, 2), np.float32); lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", lv)
    luv = np.empty(len(me.loops) * 2, np.float32); uvsrc.data.foreach_get("uv", luv); vuv[lv] = luv.reshape(-1, 2)
    uv = mesh.uv_layers.new(name=uvsrc.name); mlv = np.empty(len(mesh.loops), np.int32); mesh.loops.foreach_get("vertex_index", mlv)
    uv.data.foreach_set("uv", vuv[near[mlv]].ravel())
for p in mesh.polygons: p.use_smooth = True
mesh.materials.append(bpy.data.materials["LaneGround"])
ob = bpy.data.objects.new("BankLip", mesh)
for col in bpy.data.objects["LaneView"].users_collection: col.objects.link(ob)
Le.to_mesh_clear()
cm = bpy.data.meshes.new("BankLipCrest"); cm.from_pydata(crest_out, [], [])
cob = bpy.data.objects.new("BankLipCrest", cm); cob.hide_render = True; cob.hide_viewport = True
for col in bpy.data.objects["LaneView"].users_collection: col.objects.link(cob)
stat["crest_pts"] = len(crest_out)
stat["verts"] = len(verts); stat["faces"] = len(faces)
sc["bank_lip_applied"] = f"2026-11-04 O {OS} T {TS}"
print("LIP", stat, flush=True)
if bpy.app.background and not os.environ.get("RS_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("LIP saved", bpy.data.filepath, flush=True)
