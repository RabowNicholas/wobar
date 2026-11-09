"""The valley beyond the landslide (2026-10-21), seen across the slide at the edge (~5:21-5:46).

Why: from the lip the view ran into a bare, rounded rim against the sky - the far end of `SlideTerrain`, where the
side valley used to fade back up to rim level (a dam across the valley), cut flat by the 300 m camera clip, with
no fog past the 160 m volumetric end. slide_terrain.py now lets the valley run on past the slide (`runs_on`);
this script builds what lies beyond:

  FarValley   coarse terrain from the end of SlideTerrain out ~2 km: the valley carrying on down to the stream,
              its far side rising to a forested crest, a further ridge behind; the uphill side rising left
  FarForest   low-poly firs (FarFir_*, ~300 tris) only where the camera sees ground during the edge, plus the
              skyline band at any distance; the canopy material on FarValley fills between them
  haze        distance haze in the far materials (the fog stops at the 160 m volumetric end; opening that
              thins the near fog), keyed on inside WINDOW
  keys        FarValley / FarForest render only in WINDOW; the camera clip opens in it

Run inside Blender (after slide_terrain.build()):  ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

ST = "/Users/nicholasrabow/Desktop/vaults/Vaults/wobar/wobar/scripts/blender/slide_terrain.py"
WINDOW = (7600, 8320)                  # frames: 5:16.7 (nothing past 300 m in frame until ~7680) to 5:46.7 (down into the mist)
CLIP = 3000.0                          # camera clip inside WINDOW (300 outside)
CAM_FRAMES = (7700, 7800, 7860, 7921, 7980, 8040, 8100, 8200, 8300)
Q = dict(
    s_end=2200.0, xa_lo=-700.0, xa_hi=1500.0, step_k=0.028, step_min=3.0, step_max=45.0,
    crest=(330.0, 58.0),               # opposite side: xa (from the lane) and height above rim of its crest
    back_slope=22.0,                   # degrees, down the far side of the crest
    ridge2=(950.0, 110.0, 24.0),       # a further ridge: xa, height above rim, flank degrees
    uphill=(150.0, 16.0, 140.0),       # left: starts rising past xr -150 at 16 deg, up to +140 m
    undulate=(22.0, 1.0 / 420.0),      # amplitude (m) and frequency of the large rolls, faded in from the seam
    seam=192.0, seam_drop=0.5,
    density_near=0.035, near_d=750.0, density_far=0.004, band_deg=1.2,
    haze_d=(150.0, 700.0, 0.9), haze_col=(0.019, 0.026, 0.039),   # from 150 m, e-folding 700 m, at most 90%; the sky at the horizon
    glint_d=(120.0, 160.0, 0.45), far_shade=0.4,      # SlideGround: no rougher than this past these distances (moon glints read as lamps)
)


def _st():
    ns = {}
    exec(open(ST).read(), ns)
    F = ns["Frame"]()
    return ns, F, ns["Slide"](F)


def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _axis(lo, hi, c):
    """grid lines from lo to hi, spaced by distance from c"""
    out, v = [c], c
    while v < hi:
        v += min(max(Q["step_k"] * abs(v - c), Q["step_min"]), Q["step_max"]); out.append(min(v, hi))
    v = c
    while v > lo:
        v -= min(max(Q["step_k"] * abs(v - c), Q["step_min"]), Q["step_max"]); out.append(max(v, lo))
    return np.array(sorted(set(round(x, 2) for x in out)))


def height(ns, F, S, s, xa):
    x, y = F.xy(s, xa)
    z, a, lat, e, strip = S.height(x, y)
    R = F.rim(F.along_far(s))
    if abs(lat) < 15.0:
        z = R                          # the lane's shelf: from this far the sunken lane is lost in the trees
    xo = xa - S.x0
    # the far side tops out in a crest, falls away behind it, and a further ridge rises beyond
    cx, ch = Q["crest"]
    crest = R + ch + 14.0 * noise.noise(Vector((s * 0.004, 5.0, 0.0)))
    if xo > Q["crest"][0] - 200:
        z = min(z, crest - math.tan(math.radians(Q["back_slope"])) * max(0.0, xo - cx))
        rx, rh, rd = Q["ridge2"]
        z = max(z, R + rh - math.tan(math.radians(rd)) * abs(xo - rx) + 20.0 * noise.noise(Vector((s * 0.003, 9.0, 0.0))))
    # uphill, left of the lane: the valley side keeps climbing
    ux, ud, uc = Q["uphill"]
    if lat > ux:
        z = max(z, R + min(math.tan(math.radians(ud)) * (lat - ux), uc))
    amp, fq = Q["undulate"]
    z += amp * sstep(Q["seam"], Q["seam"] + 250.0, s) * noise.noise(Vector((s * fq, xa * fq, 17.0)))
    return x, y, z


def terrain(ns, F, S):
    cam_s, cam_xa = F.sx(*F.at(1201.0))
    ss = _axis(Q["seam"] - 3.0, Q["s_end"], Q["seam"] - 3.0)
    xs = _axis(S.x0 + Q["xa_lo"], S.x0 + Q["xa_hi"], S.x0 + 40.0)
    bm = bmesh.new()
    grid = []
    for s in ss:
        row = []
        for xa in xs:
            x, y, z = height(ns, F, S, s, xa)
            if s < Q["seam"] + 2.0:
                z -= Q["seam_drop"]        # tucked under SlideTerrain's last row
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(len(ss) - 1):
        for i in range(len(xs) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update(); bm.faces.ensure_lookup_table()
    if bm.faces[0].normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.get("FarValley") or bpy.data.meshes.new("FarValley")
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.get("FarValley") or bpy.data.objects.new("FarValley", me)
    ob.data = me
    if not ob.users_collection:
        (bpy.data.collections.get("LANE") or bpy.context.scene.collection).objects.link(ob)
    print("FarValley:", len(ss), "x", len(xs), len(me.vertices), "verts")
    return ob


def canopy_material():
    m = bpy.data.materials.get("FarCanopy") or bpy.data.materials.new("FarCanopy")
    m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial"); bs = N.new("ShaderNodeBsdfPrincipled")
    tc = N.new("ShaderNodeTexCoord")
    crowns = N.new("ShaderNodeTexVoronoi"); crowns.inputs["Scale"].default_value = 0.22    # ~4.5 m crowns
    L.new(tc.outputs["Object"], crowns.inputs["Vector"])
    gaps = N.new("ShaderNodeMapRange"); gaps.inputs["From Min"].default_value, gaps.inputs["From Max"].default_value = 0.1, 0.9
    L.new(crowns.outputs["Distance"], gaps.inputs["Value"])
    col = N.new("ShaderNodeMix"); col.data_type = "RGBA"
    col.inputs[6].default_value = (0.020, 0.030, 0.022, 1)     # crown tops, fir needles at the v2 surface colours
    col.inputs[7].default_value = (0.004, 0.005, 0.004, 1)     # the shade between crowns
    L.new(gaps.outputs["Result"], col.inputs[0]); L.new(col.outputs[2], bs.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.8; bump.inputs["Distance"].default_value = 2.0
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    L.new(gaps.outputs["Result"], inv.inputs[1]); L.new(inv.outputs[0], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], bs.inputs["Normal"])
    bs.inputs["Roughness"].default_value = 0.85
    L.new(bs.outputs[0], out.inputs["Surface"])
    return m


def far_firs():
    """three low-poly firs: a trunk and tiers of drooping star-shaped whorls"""
    col = bpy.data.collections.get("FAR_FIRS") or bpy.data.collections.new("FAR_FIRS")
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    col.hide_render = col.hide_viewport = False
    lc = bpy.context.view_layer.layer_collection.children.get(col.name)
    if lc: lc.exclude = False; lc.hide_viewport = True
    mat = bpy.data.materials.get("FarFir") or bpy.data.materials.new("FarFir")
    mat.use_nodes = True
    bs = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value = (0.018, 0.028, 0.020, 1)
    bs.inputs["Roughness"].default_value = 0.8
    rng = random.Random(7)
    obs = []
    for k, (h, w, tiers) in enumerate(((19.0, 6.4, 13), (15.0, 5.6, 11), (22.0, 5.2, 15))):
        bm = bmesh.new()
        # trunk
        bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=0.22, radius2=0.05, depth=h)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
        for t in range(tiers):
            f = t / (tiers - 1)
            zt = h * (0.22 + 0.76 * f)                           # bare bole below the lowest whorl
            r = w / 2 * (1 - f) ** 0.9 * rng.uniform(0.85, 1.15) + 0.25
            arms = 7 if f < 0.7 else 5
            top = bm.verts.new((0, 0, zt + 0.35))
            ring = []
            for i in range(arms * 2):
                ang = math.pi * i / arms + rng.uniform(-0.15, 0.15) + t * 0.7
                rr = r if i % 2 == 0 else r * 0.45
                droop = 0.9 * rr * 0.45 if i % 2 == 0 else 0.15
                ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), zt - droop)))
            for i in range(len(ring)):
                bm.faces.new((top, ring[i], ring[(i + 1) % len(ring)]))
        me = bpy.data.meshes.get(f"FarFir_{k}") or bpy.data.meshes.new(f"FarFir_{k}")
        bm.to_mesh(me); bm.free()
        me.materials.clear(); me.materials.append(mat)
        ob = bpy.data.objects.get(f"FarFir_{k}") or bpy.data.objects.new(f"FarFir_{k}", me)
        ob.data = me
        ob.visible_shadow = False
        if ob.name not in col.objects:
            col.objects.link(ob)
        ob.location = (0, 0, -2000)
        obs.append(ob)
    print("far firs:", [len(o.data.polygons) for o in obs], "tris")
    return col


def visibility(objs, F, S):
    """per-vertex 'farvis' on each terrain: 1 where the edge camera sees the ground (frustum + line of sight),
    or on the skyline band"""
    sc = bpy.context.scene; cam = sc.camera; dg = bpy.context.evaluated_depsgraph_get()
    bms, trees = [], []
    for ob in objs:
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world); bms.append(bm)
    allbm = bmesh.new()
    for ob in objs:
        allbm.from_mesh(ob.data)       # both are in world space already (identity matrices)
    bvh = BVHTree.FromBMesh(allbm)
    poses = []
    f0 = sc.frame_current
    for f in CAM_FRAMES:
        sc.frame_set(f)
        M = cam.matrix_world.copy()
        poses.append((M.translation.copy(), M.to_3x3().inverted(), M.to_3x3()))
    sc.frame_set(f0)
    tx = math.tan(cam.data.angle / 2) * 1.15
    ty = tx * sc.render.resolution_y / sc.render.resolution_x * 1.15
    out = []
    for ob, bm in zip(objs, bms):
        n = len(bm.verts)
        vis = np.zeros(n); band = np.zeros(n)
        co = np.array([v.co[:] for v in bm.verts])
        for (o, Minv, M3) in poses:
            d = co - np.array(o)
            loc = d @ np.array(Minv).T             # camera space: -z forward
            fz = -loc[:, 2]
            inf = (fz > 1) & (np.abs(loc[:, 0]) < fz * tx) & (np.abs(loc[:, 1]) < fz * ty)
            dist = np.linalg.norm(d, axis=1)
            elev = np.degrees(np.arcsin(np.clip(d[:, 2] / np.maximum(dist, 1e-6), -1, 1)))
            az = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
            # horizon profile: highest elevation per 0.25 deg of azimuth, over everything in front
            bins = np.floor(az / 0.25).astype(int)
            prof = {}
            for b, el, ok in zip(bins, elev, inf):
                if ok and el > prof.get(b, -90):
                    prof[b] = el
            for i in np.nonzero(inf & (dist > 120))[0]:
                if elev[i] > prof.get(bins[i], -90) - Q["band_deg"]:
                    band[i] = 1.0
                if vis[i] < 1 and dist[i] < Q["near_d"] + 200:
                    p = Vector(co[i]); dv = (p - o)
                    hit = bvh.ray_cast(o, dv.normalized(), dv.length - 1.0)
                    if hit[0] is None:
                        vis[i] = 1.0
        a = ob.data.attributes.get("farvis") or ob.data.attributes.new("farvis", "FLOAT", "POINT")
        a.data.foreach_set("value", vis)
        b = ob.data.attributes.get("farband") or ob.data.attributes.new("farband", "FLOAT", "POINT")
        b.data.foreach_set("value", band)
        print(ob.name, "visible", int(vis.sum()), "band", int(band.sum()), "of", n)
        bm.free()
    allbm.free()


def forest(F, S):
    """FarForest: firs on FarValley everywhere it is seen, and on SlideTerrain's far part that Scatter_Slide leaves bare"""
    ob = bpy.data.objects.get("FarForest")
    if not ob:
        ob = bpy.data.objects.new("FarForest", bpy.data.meshes.new("FarForest"))
        (bpy.data.collections.get("LANE") or bpy.context.scene.collection).objects.link(ob)
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    g = bpy.data.node_groups.get("FarForest")
    if g: bpy.data.node_groups.remove(g)
    g = bpy.data.node_groups.new("FarForest", "GeometryNodeTree")
    g.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = g.nodes, g.links
    out = N.new("NodeGroupOutput")
    join = N.new("GeometryNodeJoinGeometry")
    cam = N.new("GeometryNodeObjectInfo"); cam.inputs["Object"].default_value = bpy.context.scene.camera
    for k, nm in enumerate(("FarValley", "SlideTerrain")):
        oi = N.new("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = bpy.data.objects[nm]
        oi.transform_space = "RELATIVE"
        vis = N.new("GeometryNodeInputNamedAttribute"); vis.inputs["Name"].default_value = "farvis"
        band = N.new("GeometryNodeInputNamedAttribute"); band.inputs["Name"].default_value = "farband"
        # density: near where seen, thin far where seen, full on the skyline band
        pos = N.new("GeometryNodeInputPosition")
        dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"
        L.new(pos.outputs[0], dist.inputs[0]); dist.inputs[1].default_value = tuple(F_cam)
        near = N.new("ShaderNodeMapRange"); near.clamp = True
        near.inputs["From Min"].default_value, near.inputs["From Max"].default_value = Q["near_d"] - 150, Q["near_d"]
        near.inputs["To Min"].default_value, near.inputs["To Max"].default_value = Q["density_near"], Q["density_far"]
        L.new(dist.outputs["Value"], near.inputs["Value"])
        dv = N.new("ShaderNodeMath"); dv.operation = "MULTIPLY"
        L.new(vis.outputs["Attribute"], dv.inputs[0]); L.new(near.outputs["Result"], dv.inputs[1])
        db = N.new("ShaderNodeMath"); db.operation = "MULTIPLY"; db.inputs[1].default_value = Q["density_near"]
        L.new(band.outputs["Attribute"], db.inputs[0])
        dmax = N.new("ShaderNodeMath"); dmax.operation = "MAXIMUM"
        L.new(dv.outputs[0], dmax.inputs[0]); L.new(db.outputs[0], dmax.inputs[1])
        dens = dmax
        if nm == "SlideTerrain":   # only its far part beyond the slide, where Scatter_Slide plants nothing
            fill = N.new("GeometryNodeInputNamedAttribute"); fill.inputs["Name"].default_value = "farfill"
            m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
            L.new(dmax.outputs[0], m2.inputs[0]); L.new(fill.outputs["Attribute"], m2.inputs[1])
            dens = m2
        dist_pts = N.new("GeometryNodeDistributePointsOnFaces"); dist_pts.inputs["Seed"].default_value = 11 + k
        L.new(oi.outputs["Geometry"], dist_pts.inputs["Mesh"]); L.new(dens.outputs[0], dist_pts.inputs["Density"])
        L.new(dist_pts.outputs["Points"], join.inputs[0])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = bpy.data.collections["FAR_FIRS"]
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    L.new(join.outputs[0], iop.inputs["Points"]); L.new(ci.outputs[0], iop.inputs["Instance"])
    rid = N.new("FunctionNodeRandomValue"); rid.data_type = "INT"; rid.inputs["Max"].default_value = 2
    L.new(rid.outputs[0], iop.inputs["Instance Index"])
    rot = N.new("FunctionNodeRandomValue"); rot.data_type = "FLOAT_VECTOR"
    rot.inputs["Max"].default_value = (0.04, 0.04, 6.283); rot.inputs["Min"].default_value = (-0.04, -0.04, 0)
    L.new(rot.outputs[0], iop.inputs["Rotation"])
    scl = N.new("FunctionNodeRandomValue"); scl.inputs["Min"].default_value, scl.inputs["Max"].default_value = 0.55, 1.3
    # stands: patches of taller and younger trees, so the skyline is not a comb of equal crowns
    sp = N.new("GeometryNodeInputPosition")
    stn = N.new("ShaderNodeTexNoise"); stn.inputs["Scale"].default_value = 0.012; stn.inputs["Detail"].default_value = 1.0
    L.new(sp.outputs[0], stn.inputs["Vector"])
    stm = N.new("ShaderNodeMapRange"); stm.inputs["From Min"].default_value, stm.inputs["From Max"].default_value = 0.35, 0.65
    stm.inputs["To Min"].default_value, stm.inputs["To Max"].default_value = 0.6, 1.35
    L.new(stn.outputs["Fac"], stm.inputs["Value"])
    smul = N.new("ShaderNodeMath"); smul.operation = "MULTIPLY"
    L.new(scl.outputs[0], smul.inputs[0]); L.new(stm.outputs["Result"], smul.inputs[1])
    L.new(smul.outputs[0], iop.inputs["Scale"])
    L.new(iop.outputs[0], out.inputs[0])
    md = ob.modifiers.new("FarForest", "NODES"); md.node_group = g
    return ob


def farfill(F, S):
    """SlideTerrain's far part: 1 beyond the slide (past along 1400 or far downhill) and >12 m from any Scatter_Slide tree"""
    from mathutils import kdtree
    sc = bpy.context.scene; f0 = sc.frame_current
    T = {}                             # Scatter_Slide is culled to the camera: every tree seen across the edge, not one frame's
    for f in range(WINDOW[0], WINDOW[1] + 1, 24):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        for i in dg.object_instances:
            if i.is_instance and i.parent and i.parent.original.name == "Scatter_Slide":
                p = i.matrix_world.translation; T[(round(p.x, 2), round(p.y, 2))] = p.copy()
    sc.frame_set(f0)
    T = list(T.values())
    assert T, "no Scatter_Slide instances evaluated"
    kd = kdtree.KDTree(len(T))
    for i, p in enumerate(T):
        kd.insert((p.x, p.y, 0.0), i)
    kd.balance()
    me = bpy.data.objects["SlideTerrain"].data
    v = np.zeros(len(me.vertices))
    for i, p in enumerate(me.vertices):
        s, xa = F.sx(p.co.x, p.co.y)
        if s < S.sD + 20 and xa - S.x0 < 120:
            continue
        d = kd.find((p.co.x, p.co.y, 0.0))[2]
        v[i] = sstep(10.0, 16.0, d)
    a = me.attributes.get("farfill") or me.attributes.new("farfill", "FLOAT", "POINT")
    a.data.foreach_set("value", v)
    print("farfill", int(v.sum()), "of", len(v))


def haze_materials():
    """Distance haze in the far materials, on inside WINDOW only. (A haze volume needs volumetric_end opened past
    160 m, and that thins the near fog too - it popped on both window edges.) Each Principled's colour is pulled
    toward black and its emission toward HAZE_COL by the same amount, so the alpha-cut leaves stay cut."""
    mats = {"FarCanopy", "FarFir", "SlideGround"}
    for c in ("SLIDE_FIR_FAR", "SLIDE_SAPLING"):
        for o in bpy.data.collections[c].all_objects:
            mats |= {m.name for m in o.data.materials if m}
    d0, L_, top = Q["haze_d"]
    for mn in sorted(mats):
        nt = bpy.data.materials[mn].node_tree; N, L = nt.nodes, nt.links
        for n in [n for n in N if n.name.startswith("FV_HazeMul")]:
            L.new(n.inputs[0].links[0].from_socket, n.outputs[0].links[0].to_socket) if n.inputs[0].is_linked else None
        for n in [n for n in N if n.name.startswith("FV_Haze")]:
            N.remove(n)
        cd = N.new("ShaderNodeCameraData"); cd.name = "FV_HazeCam"
        a = N.new("ShaderNodeMath"); a.name = "FV_HazeD"; a.operation = "MULTIPLY_ADD"
        a.inputs[1].default_value = -1.0 / L_; a.inputs[2].default_value = d0 / L_
        L.new(cd.outputs["View Distance"], a.inputs[0])
        mn0 = N.new("ShaderNodeMath"); mn0.name = "FV_HazeClip"; mn0.operation = "MINIMUM"; mn0.inputs[1].default_value = 0.0
        L.new(a.outputs[0], mn0.inputs[0])
        ex = N.new("ShaderNodeMath"); ex.name = "FV_HazeExp"; ex.operation = "EXPONENT"; L.new(mn0.outputs[0], ex.inputs[0])
        f = N.new("ShaderNodeMath"); f.name = "FV_HazeF"; f.operation = "MULTIPLY_ADD"
        f.inputs[1].default_value = -top; f.inputs[2].default_value = top     # top * (1 - exp(-(d-d0)/L))
        L.new(ex.outputs[0], f.inputs[0])
        _unkey(nt, "FV_HazeWin")
        win = N.new("ShaderNodeValue"); win.name = "FV_HazeWin"
        # ramped over 2 s, not switched: the slide's own trees 150-300 m out are in view at the window's edges
        for fr, v in ((WINDOW[0], 0.0), (WINDOW[0] + 48, 1.0), (WINDOW[1] - 48, 1.0), (WINDOW[1], 0.0)):
            win.outputs[0].default_value = v; win.outputs[0].keyframe_insert("default_value", frame=fr)
        amt = N.new("ShaderNodeMath"); amt.name = "FV_HazeAmt"; amt.operation = "MULTIPLY"
        L.new(f.outputs[0], amt.inputs[0]); L.new(win.outputs[0], amt.inputs[1])
        keep = N.new("ShaderNodeMath"); keep.name = "FV_HazeKeep"; keep.operation = "SUBTRACT"; keep.inputs[0].default_value = 1.0
        L.new(amt.outputs[0], keep.inputs[1])
        for k, b in enumerate([n for n in N if n.type in ("BSDF_PRINCIPLED", "BSDF_TRANSLUCENT")]):
            col = b.inputs["Base Color"] if b.type == "BSDF_PRINCIPLED" else b.inputs["Color"]
            mul = N.new("ShaderNodeVectorMath"); mul.name = f"FV_HazeMul{k}"; mul.operation = "SCALE"
            if col.is_linked: L.new(col.links[0].from_socket, mul.inputs[0])
            else: mul.inputs[0].default_value = col.default_value[:3]
            L.new(keep.outputs[0], mul.inputs["Scale"]); L.new(mul.outputs[0], col)
            if b.type == "BSDF_PRINCIPLED" and not b.inputs["Emission Color"].is_linked:
                hc = N.new("ShaderNodeRGB"); hc.name = f"FV_HazeCol{k}"; hc.outputs[0].default_value = (*Q["haze_col"], 1.0)
                L.new(hc.outputs[0], b.inputs["Emission Color"]); L.new(amt.outputs[0], b.inputs["Emission Strength"])
        ad = nt.animation_data
        for lay in ad.action.layers:
            for st in lay.strips:
                for fc in st.channelbag(ad.action_slot).fcurves:
                    if "FV_HazeWin" in fc.data_path:
                        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
                        fc.extrapolation = "CONSTANT"
    print("haze in", len(mats), "materials")


def ground_glint():
    """SlideGround's wet patches mirror the moon; 340 m away a single glint reads as a lamp. Rougher with distance."""
    nt = bpy.data.materials["SlideGround"].node_tree; N, L = nt.nodes, nt.links
    bs = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    if "FV_GlintMax" in N:
        src = N["FV_GlintMax"].inputs[0].links[0].from_socket
        if "FV_ShadeMul" in N:
            L.new(N["FV_ShadeMul"].inputs[0].links[0].from_socket, bs.inputs["Base Color"])
        if "FV_CoatFar" in N:
            bs.inputs["Coat Weight"].default_value = N["FV_CoatFar"].inputs["To Min"].default_value
        for n in [n for n in N if n.name.startswith("FV_")]: N.remove(n)
        L.new(src, bs.inputs["Roughness"])
    src = bs.inputs["Roughness"].links[0].from_socket
    cd = N.new("ShaderNodeCameraData"); cd.name = "FV_Cam"
    mr = N.new("ShaderNodeMapRange"); mr.name = "FV_GlintFar"; mr.clamp = True
    d0, d1, r = Q["glint_d"]
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = d0, d1
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.0, r
    L.new(cd.outputs["View Distance"], mr.inputs["Value"])
    mx = N.new("ShaderNodeMath"); mx.name = "FV_GlintMax"; mx.operation = "MAXIMUM"
    L.new(src, mx.inputs[0]); L.new(mr.outputs["Result"], mx.inputs[1]); L.new(mx.outputs[0], bs.inputs["Roughness"])
    # the glint itself is the thin clear coat (weight 0.03, a mirror): fade it out over the same distance
    if not bs.inputs["Coat Weight"].is_linked:
        cw = N.new("ShaderNodeMapRange"); cw.name = "FV_CoatFar"; cw.clamp = True
        cw.inputs["From Min"].default_value, cw.inputs["From Max"].default_value = d0, d1
        cw.inputs["To Min"].default_value, cw.inputs["To Max"].default_value = bs.inputs["Coat Weight"].default_value, 0.0
        L.new(cd.outputs["View Distance"], cw.inputs["Value"]); L.new(cw.outputs["Result"], bs.inputs["Coat Weight"])
    # far off, the ground between the trees is in their shade: darker, so it does not stripe the slopes
    col = bs.inputs["Base Color"].links[0].from_socket
    sh = N.new("ShaderNodeMapRange"); sh.name = "FV_ShadeFar"; sh.clamp = True
    sh.inputs["From Min"].default_value, sh.inputs["From Max"].default_value = d0, d1 + 60.0
    sh.inputs["To Min"].default_value, sh.inputs["To Max"].default_value = 1.0, Q["far_shade"]
    L.new(cd.outputs["View Distance"], sh.inputs["Value"])
    mul = N.new("ShaderNodeVectorMath"); mul.name = "FV_ShadeMul"; mul.operation = "SCALE"
    L.new(col, mul.inputs[0]); L.new(sh.outputs["Result"], mul.inputs["Scale"]); L.new(mul.outputs[0], bs.inputs["Base Color"])


def _unkey(idb, match):
    """drop the fcurves whose data path contains `match`, so a rebuild with a new WINDOW leaves no stale keys"""
    ad = idb.animation_data
    if not (ad and ad.action): return
    for lay in ad.action.layers:
        for st in lay.strips:
            cb = st.channelbag(ad.action_slot)
            for fc in [fc for fc in cb.fcurves if match in fc.data_path]:
                cb.fcurves.remove(fc)


def keys(objs):
    sc = bpy.context.scene; cam = sc.camera.data
    for ob in objs: _unkey(ob, "hide_render")
    _unkey(cam, "clip_end")
    def key(idb, path, pre, val, post):
        for f, v in ((WINDOW[0] - 1, pre), (WINDOW[0], val), (WINDOW[1], val), (WINDOW[1] + 1, post)):
            setattr(idb, path, v); idb.keyframe_insert(path, frame=f)
    for ob in objs:
        key(ob, "hide_render", True, False, True)
    key(cam, "clip_end", 300.0, CLIP, 300.0)
    # interpolation: constant, so nothing ramps
    for idb in [*objs, cam]:
        ad = idb.animation_data
        if not (ad and ad.action): continue
        for lay in ad.action.layers:
            for st in lay.strips:
                for fc in st.channelbag(ad.action_slot).fcurves:
                    if fc.data_path in ("hide_render", "clip_end"):
                        for k in fc.keyframe_points: k.interpolation = "CONSTANT"


F_cam = (0.0, 0.0, 0.0)


def build():
    global F_cam
    ns, F, S = _st()
    sc = bpy.context.scene; f0 = sc.frame_current
    sc.frame_set(7921); F_cam = tuple(sc.camera.matrix_world.translation); sc.frame_set(f0)
    fv = terrain(ns, F, S)
    fv.data.materials.clear(); fv.data.materials.append(canopy_material())
    far_firs()
    farfill(F, S)
    visibility([fv, bpy.data.objects["SlideTerrain"]], F, S)
    ff = forest(F, S)
    haze_materials()
    ground_glint()
    keys([fv, ff])
    print("far valley built")
