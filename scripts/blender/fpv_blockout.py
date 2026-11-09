"""ABGRUND fall — FPV drone grey blockout (2026-10-19).

Nick: "lets move the whole camera movement into FPV drone ... start with this section and then
if it works we can do the whole thing as fpv drone." Supersedes the walker/slide tests in
fall_blockout.py for this section.

The place: the hollow way runs into a gorge. Past the edge (5:30.5) the floor is a wet bedrock
flume; at the cut (6:04.8) it goes over a four-step cascade; the drone dives the falls and pulls
out over the plunge pool on the drop (6:11.6), then runs on along the gorge floor.

    Blender -b --factory-startup --python fpv_blockout.py

All tunable numbers are in P. The drone path is a "rubber band": floor + clearance, relaxed by
repeated blurring while never allowed below a minimum clearance, so it hugs slopes and arcs over
lips. The camera looks along its own flight and banks with horizontal curvature.
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

P = dict(
    fps=24, t_start=320.0, t_end=380.0,
    TE=330.5, TC=344.2, TL2=364.8, TD=371.6,   # measured cue points (full piece, s)
    lens=28.0,
    # horizontal speed, m/s
    v_run=2.8, v_mid=5.5, v_cut=7.0, v_dive=6.0,
    # terrain
    crest=(14.0, 3.0), slope_flume=(12.0, 15.0),
    falls=(7.0, 9.0, 11.0, 15.0), fall_w=1.5, ledge_slope=5.0, pool_before_drop=6.0,
    pool_len=25.0, pool_dip=1.0, gorge_slope=2.0,
    hw=(1.35, 4.0), wt=(3.3, 7.5),   # floor half-width and wall-top offset: lane -> gorge
    wall=9.5, rim_lag=25.0, rim_smooth=15.0,
    # drone
    clear_cruise=1.3, clear_flume=0.45, clear_cascade=1.2, clear_pool=0.6,
    min_flume=0.3, min_cascade=0.8, min_lip=2.5, relax_sigma=1.5, relax_iter=80,
    dive_shape=2.0, look_dive=1.0,   # dive curve (higher = stays out level longer); look-ahead in the dive (s)
    look_ahead=0.3, uptilt=3.0, bank_gain=5.0, bank_max=25.0, jitter=0.08,
    out="/Volumes/music/blender/renders/fpv_blockout_01/f_",
    blend="/Volumes/music/blender/abgrund_fpv_blockout.blend",
    res=(1280, 720),
)


def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- distance
def speed(t):
    TE, TL2, TD = P["TE"], P["TL2"], P["TD"]
    if t < TE:
        return P["v_run"]
    if t < TL2:
        v = P["v_run"] + (P["v_mid"] - P["v_run"]) * sstep(TE, TE + 5, t)
        return v + (P["v_cut"] - P["v_mid"]) * max(t - TE - 5, 0) / (TL2 - TE - 5)
    if t < TD:
        return P["v_cut"] + (P["v_dive"] - P["v_cut"]) * sstep(TL2, TL2 + 1.5, t)
    return P["v_dive"] + (P["v_run"] - P["v_dive"]) * sstep(TD, TD + 3.0, t)


DT = 1.0 / 240
ts = np.arange(P["t_start"], P["t_end"] + 1, DT)
ss = np.zeros_like(ts)
for i in range(1, len(ts)):
    ss[i] = ss[i - 1] + speed(ts[i - 1]) * DT
s_at = lambda t: float(np.interp(t, ts, ss))
sE, sC, sL2, sD = (s_at(P[k]) for k in ("TE", "TC", "TL2", "TD"))

# ---------------------------------------------------------------- terrain along s
DS = 0.05
S0, S1 = -15.0, ss[-1] + 60.0
sg = np.arange(S0, S1, DS)
nf = len(P["falls"])
s_pool = sD - P["pool_before_drop"]              # foot of the last fall
ledge = (s_pool - sL2 - nf * P["fall_w"]) / (nf - 1)
fall_starts = [sL2 + k * (P["fall_w"] + ledge) for k in range(nf)]
assert ledge > 3.0, ledge

fl = np.zeros_like(sg)
for i in range(1, len(sg)):
    s = sg[i]
    a, L = P["crest"]
    if s < sE:
        d = 0.0
    elif s < sE + L:
        d = math.tan(math.radians(a * sstep(sE, sE + L, s)))
    elif s < sL2:
        a0, a1 = P["slope_flume"]
        d = math.tan(math.radians(a0 + (a1 - a0) * (s - sE - L) / (sL2 - sE - L)))
    elif s < s_pool:
        d = math.tan(math.radians(P["ledge_slope"]))
    else:
        d = 0.0 if s < s_pool + P["pool_len"] else math.tan(math.radians(P["gorge_slope"]))
    fl[i] = fl[i - 1] - d * DS
for s0, h in zip(fall_starts, P["falls"]):
    fl -= h * np.array([sstep(s0, s0 + P["fall_w"], s) for s in sg])
pool_bowl = np.array([sstep(s_pool, s_pool + 3, s) * (1 - sstep(s_pool + P["pool_len"] - 4, s_pool + P["pool_len"], s)) for s in sg])
water_z = float(np.interp(s_pool + 1, sg, fl)) - 0.1
fl -= P["pool_dip"] * pool_bowl

lagged = np.interp(sg - P["rim_lag"], sg, fl, left=fl[0])
k = int(P["rim_smooth"] / DS)
rim = np.convolve(np.pad(lagged, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
rim = np.minimum.accumulate(rim) + P["wall"]

floor_z = lambda s: float(np.interp(s, sg, fl))
rim_z = lambda s: float(np.interp(s, sg, rim))
path_x = lambda s: 1.8 * math.sin(s / 38.0) + 0.6 * math.sin(s / 13.0 + 1.0)
gorge = lambda s: sstep(sL2 - 20, sL2 + 5, s)          # lane -> gorge widening
hw = lambda s: P["hw"][0] + (P["hw"][1] - P["hw"][0]) * gorge(s)
wt = lambda s: P["wt"][0] + (P["wt"][1] - P["wt"][0]) * gorge(s)
chute = lambda s: sstep(sE, sE + 4, s) * (1 - sstep(sL2 - 1, sL2, s))

# ---------------------------------------------------------------- scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
sc = bpy.context.scene
sc.render.fps = P["fps"]
sc.frame_start = 1
sc.frame_end = int(round((P["t_end"] - P["t_start"]) * P["fps"]))
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x, sc.render.resolution_y = P["res"]
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "OBJECT"
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_shadows = True
sc.display.shadow_focus = 0.3
sc.world = sc.world or bpy.data.worlds.new("W")
sc.world.color = (0.06, 0.07, 0.10)
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = P["out"]


def link(name, bm, color):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.color = (*color, 1.0)
    sc.collection.objects.link(ob)
    return ob


def lane_mesh():
    lats = np.concatenate([np.arange(-16, -8, 0.5), np.arange(-8, 8, 0.15), np.arange(8, 16.01, 0.5)])
    rows = np.arange(S0, S1, 0.2)
    bm = bmesh.new()
    grid = []
    for s in rows:
        F, R, h0, h1 = floor_z(s), rim_z(s), hw(s), wt(s)
        cx, m = path_x(s), chute(s)
        row = []
        for lat in lats:
            a = abs(lat)
            w = sstep(h0, h1, a)
            z = F + (R - F) * w
            x = cx + lat
            if 0.02 < w < 0.98:  # rock / earth wall relief
                x += math.copysign(0.4 * noise.noise(Vector((lat * 0.4, s * 0.45, z * 0.5))), lat)
                z += 0.25 * noise.noise(Vector((s * 0.2, z * 0.8, 3.0)))
            elif w <= 0.02:
                z -= (1 - m) * 0.12 * math.exp(-((a - 0.75) / 0.18) ** 2) * (1 - gorge(s))
                z += (1 - m) * 0.05 * noise.noise(Vector((lat * 1.2, s * 0.7, 7.0)))
                z += m * (0.3 * (lat / h0) ** 2 + 0.04 * noise.noise(Vector((lat * 3.0, s * 0.12, 5.0))))
            else:
                z += 0.4 * noise.noise(Vector((lat * 0.15, s * 0.15, 11.0)))
            row.append(bm.verts.new((x, s, z)))
        grid.append(row)
    for j in range(len(rows) - 1):
        for i in range(len(lats) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    ob = link("Lane", bm, (0.55, 0.55, 0.55))
    for p in ob.data.polygons:
        p.use_smooth = True


def water():
    bm = bmesh.new()

    def quad(c):
        bm.faces.new([bm.verts.new(v) for v in c])
    # plunge pool
    for s in np.arange(s_pool, s_pool + P["pool_len"], 1.0):
        x0, x1, h = path_x(s), path_x(s + 1), hw(s) + 0.6
        quad([(x0 - h, s, water_z), (x0 + h, s, water_z), (x1 + h, s + 1, water_z), (x1 - h, s + 1, water_z)])
    # a sheet of falling water down each fall face
    for s0, hgt in zip(fall_starts, P["falls"]):
        top, bot = floor_z(s0) + 0.05, floor_z(s0 + P["fall_w"] + 1.0)
        x = path_x(s0)
        quad([(x - 1.2, s0 + 0.1, top), (x + 1.2, s0 + 0.1, top),
              (x + 1.4, s0 + P["fall_w"] + 0.6, bot), (x - 1.4, s0 + P["fall_w"] + 0.6, bot)])
    link("Water", bm, (0.16, 0.26, 0.30))


def props():
    rnd = random.Random(7)
    bm = bmesh.new()

    def box(c, sz, rot):
        r = bmesh.ops.create_cube(bm, size=1.0)
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*sz, 1))
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

    def cyl(a, b, rad, seg=6):
        d = b - a
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=rad, radius2=rad * 0.6, depth=d.length)
        m = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

    s = S0
    while s < S1:
        cx, F, R, h0, h1 = path_x(s), floor_z(s), rim_z(s), hw(s), wt(s)
        in_fall = any(s0 - 0.5 < s < s0 + P["fall_w"] + 0.5 for s0 in fall_starts)
        # stones: none in the flume, boulders at the edges of ledges and pool
        if chute(s) < 0.5 and not in_fall:
            for _ in range(2):
                lat = rnd.uniform(-h0, h0) if gorge(s) < 0.5 else rnd.choice((-1, 1)) * rnd.uniform(h0 * 0.6, h0)
                if s > sE - 8 and abs(lat) < 0.9:
                    lat = math.copysign(rnd.uniform(0.9, h0), lat)
                sz = rnd.uniform(0.08, 0.4) * (1 + 2 * gorge(s))
                box(Vector((cx + lat, s + rnd.uniform(0, 1), F + sz * 0.2)), (sz, sz * 1.2, sz * 0.7),
                    (rnd.random(), rnd.random(), rnd.random()))
        if rnd.random() < 0.6:  # rocks in the walls
            side = rnd.choice((-1, 1))
            lat = h0 + (h1 - h0) * rnd.uniform(0.3, 0.9)
            z = F + (R - F) * sstep(h0, h1, lat) - 0.2
            sz = rnd.uniform(0.3, 0.9)
            box(Vector((cx + side * (lat - 0.25), s, z)), (sz, sz, sz * 0.8), (rnd.random(), 0, rnd.random()))
        for _ in range(2):  # roots down the walls, from the rim
            side = rnd.choice((-1, 1))
            top = Vector((cx + side * (h1 - 0.05), s + rnd.uniform(0, 1), R - 0.1))
            lat_b = h1 - (h1 - h0) * rnd.uniform(0.25, 0.95)
            zb = F + (R - F) * sstep(h0, h1, lat_b)
            cyl(top, Vector((cx + side * (lat_b + 0.15), top.y + rnd.uniform(-1.5, 1.5), zb + 0.1)), rnd.uniform(0.03, 0.09))
        for _ in range(3):  # trunks on the rims
            side = rnd.choice((-1, 1))
            base = Vector((cx + side * rnd.uniform(h1 + 0.3, h1 + 9), s + rnd.uniform(0, 1), R - 0.3))
            cyl(base, base + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(12, 20))), rnd.uniform(0.15, 0.3))
        s += 1.0
    link("Props", bm, (0.6, 0.6, 0.6))


# ---------------------------------------------------------------- drone
def clearance(t):
    TE, TL2, TD = P["TE"], P["TL2"], P["TD"]
    c = P["clear_cruise"] + (P["clear_flume"] - P["clear_cruise"]) * sstep(TE - 0.3, TE + 0.4, t)
    c += (P["clear_cascade"] - c) * sstep(TL2 - 0.5, TL2, t)
    c += (P["clear_pool"] - c) * sstep(TD - 1.0, TD - 0.2, t)
    c += (P["clear_cruise"] - c) * sstep(TD + 0.3, TD + 3.0, t)
    return c


def drone_path():
    # in s, on the terrain grid: target height, then relax (blur) under a no-collision floor
    tgrid = np.interp(sg, ss, ts, left=ts[0], right=ts[-1])
    in_pool = (sg > s_pool) & (sg < s_pool + P["pool_len"])
    ground = np.maximum(fl, np.where(in_pool, water_z, -1e9))
    target = ground + np.array([clearance(t) for t in tgrid])
    # cascade: out level over the first lip, steepening dive, flatten over the pool on the drop
    z_top = floor_z(sL2) + P["clear_cascade"]
    z_bot = water_z + P["clear_pool"]
    for i, s in enumerate(sg):
        if sL2 <= s <= sD:
            u = (s - sL2) / (sD - sL2)
            g = u ** P["dive_shape"] * (P["dive_shape"] + 1 - P["dive_shape"] * u)  # flat start, flat end
            target[i] = z_top - (z_top - z_bot) * g
    near_lip = np.zeros_like(sg, dtype=bool)
    for s0 in fall_starts[1:]:
        near_lip |= (sg > s0 - 3) & (sg < s0 + 2)
    zmin = ground + np.where(near_lip, P["min_lip"], np.where((sg > sL2 - 2) & (sg < s_pool + 4), P["min_cascade"], P["min_flume"]))
    sig = int(P["relax_sigma"] / DS)
    kern = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    kern /= kern.sum()
    z = np.maximum(target, zmin)
    for _ in range(P["relax_iter"]):
        z = np.convolve(np.pad(z, (3 * sig, 3 * sig), mode="edge"), kern, "valid")
        z = np.maximum(z, zmin)
        z = 0.85 * z + 0.15 * np.maximum(target, zmin)  # keep pulling toward the target height
    return z


def bake_camera():
    cd = bpy.data.cameras.new("Cam")
    cd.lens = P["lens"]
    cd.sensor_fit = "AUTO"
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    zd = drone_path()
    pos = lambda t: Vector((path_x(s_at(t)), s_at(t), float(np.interp(s_at(t), sg, zd))))
    lo_clear = 1e9
    for f in range(sc.frame_start, sc.frame_end + 1):
        t = P["t_start"] + (f - 1) / P["fps"]
        la = P["look_ahead"] + (P["look_dive"] - P["look_ahead"]) * sstep(P["TL2"] - 0.5, P["TL2"] + 0.5, t) * (1 - sstep(P["TD"] - 0.8, P["TD"] + 0.5, t))
        p0, p1 = pos(t), pos(t + la)
        fwd = (p1 - p0).normalized()
        # coordinated-turn bank from horizontal curvature, exaggerated FPV-style
        h = 0.25
        a = pos(t - h).to_2d(); b = p0.to_2d(); c = pos(t + h).to_2d()
        v1, v2 = (b - a) / h, (c - b) / h
        lat_acc = (v1.x * v2.y - v1.y * v2.x) / max(v1.length, 0.1) / h
        bank = max(-P["bank_max"], min(P["bank_max"], P["bank_gain"] * math.degrees(math.atan(lat_acc / 9.81))))
        fr = t * P["fps"]
        jit = P["jitter"]
        q = fwd.to_track_quat("-Z", "Y")
        m = q.to_matrix().to_4x4() @ Euler((math.radians(P["uptilt"] + jit * math.sin(fr * 1.9)),
                                            math.radians(jit * math.sin(fr * 2.3 + 1)),
                                            math.radians(-bank + jit * math.sin(fr * 1.7 + 2))), "XYZ").to_matrix().to_4x4()
        cam.matrix_world = Matrix.Translation(p0) @ m
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        lo_clear = min(lo_clear, p0.z - max(floor_z(p0.y), water_z if s_pool < p0.y < s_pool + P["pool_len"] else -1e9))
    print("min clearance over the shot (m):", round(lo_clear, 2))


lane_mesh()
water()
props()
bake_camera()
print("s at events:", [round(x, 1) for x in (sE, sC, sL2, s_pool, sD)], "ledge m:", round(ledge, 1),
      "floor at events:", [round(floor_z(x), 1) for x in (sE + 1, sC, sL2, s_pool + 1, sD + 30)],
      "wall height:", [round(rim_z(x) - floor_z(x), 1) for x in (sE, sC, sL2, s_pool + 1, sD + 40)])
bpy.ops.wm.save_as_mainfile(filepath=P["blend"])
