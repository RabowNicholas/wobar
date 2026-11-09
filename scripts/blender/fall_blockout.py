"""ABGRUND fall — grey blockout (2026-10-19).

Standalone test of the camera motion for the fall at 5:30.5–6:11.6, built in a
fresh scene so hohlweg_2.blend is untouched. Run in background Blender:

    Blender -b --factory-startup --python fall_blockout.py -- [render]

Builds a straight-ish trench whose floor goes over two lips and down a steep
grade, rims lagging behind so the walls deepen, grey props for parallax, and a
camera baked per frame: speed profile, ballistic air off each lip, soft
landing, handheld tremor that stops while weightless, slow roll.
All the tunable numbers are in P.
"""
import bpy, bmesh, math, sys, random
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

P = dict(
    fps=24, t_start=320.0, t_end=380.0,
    # cue points, seconds on the full piece (measured from the audio)
    TE=330.5, TC=344.2, TL2=364.8, TD=371.6,
    eye=1.6, aim_ahead=8.0, lens=28.0,
    # v5 (Nick): "more like a water slide ... the slide should continue the whole time until the drop.
    # it can keep speeding up until the second lip ... then airtime and you land on the drop and keep running"
    v_run=2.8, v_mid=5.5, v_cut=7.0, v_launch=8.5,
    air_t=1.2,                 # launch is this long before the drop; you land on TD
    crest=(14.0, 3.0),         # slope (deg) reached over the rounded crest (m)
    slope_slide=(12.0, 15.0),  # edge -> cut, steepening
    slope_cut=(20.0, 6.0),     # at the cut the chute pitches over to this, over this many m
    runup=(4.0, 12.0, 3.0),    # chute flattens to this before the lip, over m; lip kicks up (deg)
    land=(14.0, 2.0, 30.0),    # landing slope (deg) easing to this over m
    # slide body: eye height, lean back (deg, + = up), side swing (m), bank (deg), yaw (deg), rumble (deg)
    slide_eye=0.55, slide_lean=4.0, slide_side=0.25, slide_bank=3.0, slide_yaw=2.0, slide_rumble=0.04,
    v_slide=8.5, knee=0.8, drop_s=1.0,
    wall=9.5, rim_lag=25.0, rim_smooth=15.0,
    out="/Volumes/music/blender/renders/fall_blockout_05/f_",
    blend="/Volumes/music/blender/abgrund_fall_blockout.blend",
    res=(1280, 720),
)
G = 9.81
P["T_launch"] = P["TD"] - P["air_t"]


def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- distance
def speed(t):
    TE, TL2, TD, TLa = P["TE"], P["TL2"], P["TD"], P["T_launch"]
    if t < TE:
        return P["v_run"]
    if t < TL2:  # one long slide, always gaining
        v = P["v_run"] + (P["v_mid"] - P["v_run"]) * sstep(TE, TE + 5, t)
        return v + (P["v_cut"] - P["v_mid"]) * max(t - TE - 5, 0) / (TL2 - TE - 5)
    if t < TD:  # the cut pitches you faster, then you fly
        return P["v_cut"] + (P["v_launch"] - P["v_cut"]) * sstep(TL2, TL2 + 2.5, t)
    return P["v_launch"] + (P["v_run"] - P["v_launch"]) * sstep(TD, TD + 2.0, t)  # hit the water


DT = 1.0 / 240
ts = np.arange(P["t_start"], P["t_end"] + 1, DT)
ss = np.zeros_like(ts)
for i in range(1, len(ts)):
    ss[i] = ss[i - 1] + speed(ts[i - 1]) * DT
s_at = lambda t: float(np.interp(t, ts, ss))
sE, sC, sL2, sD, sLa = (s_at(P[k]) for k in ("TE", "TC", "TL2", "TD", "T_launch"))

# ---------------------------------------------------------------- floor + rim
DS = 0.05
S0, S1 = -15.0, ss[-1] + 80.0
sg = np.arange(S0, S1, DS)
CLIFF = 0.6


def slope_deg(s):
    a, L = P["crest"]
    if s < sE:
        return 0.0
    if s < sE + L:
        return a * sstep(sE, sE + L, s)
    if s < sL2:
        a0, a1 = P["slope_slide"]; return a0 + (a1 - a0) * (s - sE - L) / (sL2 - sE - L)
    c, cl = P["slope_cut"]
    r, rl, kick = P["runup"]
    if s < sLa - rl:
        return P["slope_slide"][1] + (c - P["slope_slide"][1]) * sstep(sL2, sL2 + cl, s)
    if s < sLa - 2.0:
        return c + (r - c) * sstep(sLa - rl, sLa - 2.0, s)
    if s < sLa:
        return -kick
    if s < sLa + CLIFF:
        return 0.0  # the cliff itself is added as a step below
    l0, l1, ll = P["land"]
    return l0 + (l1 - l0) * min((s - sLa - CLIFF) / ll, 1.0)


fl = np.zeros_like(sg)
for i in range(1, len(sg)):
    fl[i] = fl[i - 1] - math.tan(math.radians(slope_deg(sg[i]))) * DS
# cliff height so a ballistic flight off the lip lands exactly on the drop
vz0 = P["v_launch"] * math.tan(math.radians(P["runup"][2]))
dz = vz0 * P["air_t"] - 0.5 * G * P["air_t"] ** 2
HC = -dz - math.tan(math.radians(P["land"][0])) * (P["v_launch"] * P["air_t"] - CLIFF)
fl -= HC * np.array([sstep(sLa, sLa + CLIFF, s) for s in sg])
# rims follow the floor rim_lag metres later, smoothed: walls deepen, rims never climb
lagged = np.interp(sg - P["rim_lag"], sg, fl, left=fl[0])
k = int(P["rim_smooth"] / DS)
rim = np.convolve(np.pad(lagged, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
rim = np.minimum.accumulate(rim) + P["wall"]

floor_z = lambda s: float(np.interp(s, sg, fl))
rim_z = lambda s: float(np.interp(s, sg, rim))
chute = lambda s: sstep(sE, sE + 4, s) * (1 - sstep(sLa - 1, sLa, s))  # smooth water-slide channel
path_x = lambda s: 1.8 * math.sin(s / 38.0) + 0.6 * math.sin(s / 13.0 + 1.0)

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
sh.color_type = "SINGLE"
sh.single_color = (0.55, 0.55, 0.55)
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_shadows = True
sc.display.shadow_focus = 0.3
sc.world = sc.world or bpy.data.worlds.new("W")
sc.world.color = (0.06, 0.07, 0.10)
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = P["out"]


def lane_mesh():
    lats = np.concatenate([np.arange(-14, -3.5, 0.5), np.arange(-3.5, 3.5, 0.12), np.arange(3.5, 14.01, 0.5)])
    rows = np.arange(S0, S1, 0.25)
    bm = bmesh.new()
    grid = []
    for s in rows:
        F, R = floor_z(s), rim_z(s)
        H = R - F
        cx = path_x(s)
        row = []
        for lat in lats:
            a = abs(lat)
            w = sstep(1.35, 3.3, a)
            z = F + H * w
            x = cx + lat
            if 0.02 < w < 0.98:  # wall relief: lumps and ledges
                n = noise.noise(Vector((lat * 0.4, s * 0.45, z * 0.5)))
                x += math.copysign(0.35 * n, lat)
                z += 0.25 * noise.noise(Vector((s * 0.2, z * 0.8, 3.0)))
            elif w <= 0.02:  # floor: two ruts and some lumps; in the chute a smooth concave channel
                m = chute(s)
                z -= (1 - m) * 0.12 * math.exp(-((a - 0.75) / 0.18) ** 2)
                z += (1 - m) * 0.05 * noise.noise(Vector((lat * 1.2, s * 0.7, 7.0)))
                z += m * 0.3 * (lat / 1.35) ** 2
                z += m * 0.04 * noise.noise(Vector((lat * 3.0, s * 0.12, 5.0)))  # grooves along the flow
            else:  # forest floor above
                z += 0.4 * noise.noise(Vector((lat * 0.15, s * 0.15, 11.0)))
            row.append(bm.verts.new((x, s, z)))
        grid.append(row)
    for j in range(len(rows) - 1):
        for i in range(len(lats) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new("Lane")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Lane", me)
    sc.collection.objects.link(ob)


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
        q = d.to_track_quat("Z", "Y")
        m = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

    s = S0
    while s < S1:
        cx, F, R = path_x(s), floor_z(s), rim_z(s)
        # stones on the floor
        for _ in range(0 if chute(s) > 0.5 else 2):
            lat = rnd.uniform(-1.3, 1.3)
            sz = rnd.uniform(0.08, 0.4)
            box(Vector((cx + lat, s + rnd.uniform(0, 1), F + sz * 0.2)), (sz, sz * 1.2, sz * 0.7),
                (rnd.random(), rnd.random(), rnd.random()))
        # rocks stuck in the walls
        if rnd.random() < 0.6:
            side = rnd.choice((-1, 1))
            h = rnd.uniform(0.3, 0.9)
            lat = 1.35 + (3.3 - 1.35) * h
            z = F + (R - F) * sstep(1.35, 3.3, lat) - 0.2
            sz = rnd.uniform(0.3, 0.9)
            box(Vector((cx + side * (lat - 0.25), s, z)), (sz, sz, sz * 0.8), (rnd.random(), 0, rnd.random()))
        # roots hanging down the walls
        for _ in range(2):
            side = rnd.choice((-1, 1))
            top = Vector((cx + side * 3.25, s + rnd.uniform(0, 1), R - 0.1))
            depth = rnd.uniform(0.25, 0.95)
            lat_b = 3.3 - (3.3 - 1.4) * depth
            zb = F + (R - F) * sstep(1.35, 3.3, lat_b)
            bot = Vector((cx + side * (lat_b + 0.15), top.y + rnd.uniform(-1.5, 1.5), zb + 0.1))
            cyl(top, bot, rnd.uniform(0.03, 0.09))
        # trunks on the rims
        for _ in range(3):
            side = rnd.choice((-1, 1))
            lat = rnd.uniform(3.6, 12.0)
            base = Vector((cx + side * lat, s + rnd.uniform(0, 1), R - 0.3))
            cyl(base, base + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(12, 20))),
                rnd.uniform(0.15, 0.3))
        s += 1.0
    me = bpy.data.meshes.new("Props")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Props", me)
    sc.collection.objects.link(ob)


# ---------------------------------------------------------------- camera
def wobble(t, f):
    # handheld drift (cycles 72/95/120 frames) + faint tremor (11–13 frames), degrees
    fr = t * P["fps"]
    pitch = 0.33 * math.sin(2 * math.pi * fr / 72 + 0.3) + 0.08 * math.sin(2 * math.pi * fr / 11.5 + 1.1)
    yaw = 0.43 * math.sin(2 * math.pi * fr / 95 + 2.0) + 0.08 * math.sin(2 * math.pi * fr / 12.7 + 0.4)
    roll = 0.27 * math.sin(2 * math.pi * fr / 120 + 4.1)
    dz = 0.015 * math.sin(2 * math.pi * fr / 83 + 0.7)
    dx = 0.015 * math.sin(2 * math.pi * fr / 101 + 2.2)
    return pitch * f, yaw * f, roll * f, dz * f, dx * f


def slide_w(t):
    # 1 = sliding (low, leaning back), 0 = on your feet. One slide from the edge to the landing.
    return sstep(P["TE"], P["TE"] + 0.5, t) * (1 - sstep(P["TD"], P["TD"] + P["drop_s"], t))


def eye_h(t):
    return P["eye"] - slide_w(t) * (P["eye"] - P["slide_eye"])


def slide(t):
    # water slide: lean back, a slow gentle sway across the channel, banking with it, almost no rumble.
    # Returns pitch, yaw, roll (deg) and sideways offset (m).
    u = t - P["TE"]
    sw = lambda a, b, c, d: 0.6 * math.sin(2 * math.pi * a * u + b) + 0.4 * math.sin(2 * math.pi * c * u + d)
    side = P["slide_side"] * sw(0.07, 0.6, 0.16, 5.1)
    rumble = min(speed(t) / P["v_slide"], 1.0) * P["slide_rumble"]
    fr = t * P["fps"]
    pitch = P["slide_lean"] + rumble * (math.sin(2 * math.pi * fr / 9.3) + 0.5 * math.sin(2 * math.pi * fr / 5.1 + 1))
    yaw = P["slide_yaw"] * sw(0.053, 2.1, 0.13, 0.4)
    roll = -P["slide_bank"] * side / P["slide_side"]
    return pitch, yaw, roll, side


def bake_camera():
    cd = bpy.data.cameras.new("Cam")
    cd.lens = P["lens"]
    cd.sensor_fit = "AUTO"
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    # vertical dynamics at 240 Hz: riding the surface; ballistic off the launch lip only; knee on landing
    z = floor_z(0) + eye_h(ts[0])
    vz, air, knee, kv = 0.0, False, 0.0, 0.0
    zs, airs = np.zeros_like(ts), np.zeros_like(ts)
    for i, t in enumerate(ts):
        tgt = floor_z(ss[i]) + eye_h(t)
        if air:
            vz -= G * DT
            z += vz * DT
            if z <= tgt:
                air = False
                vg = (tgt - (floor_z(ss[i - 1]) + eye_h(ts[i - 1]))) / DT
                kv = min(vz - vg, 0.0) * P["knee"]
                z = tgt
                print("landed at", round(t, 2), "impact m/s", round(vz - vg, 1))
        else:
            tgt_next = floor_z(ss[min(i + 1, len(ts) - 1)]) + eye_h(ts[min(i + 1, len(ts) - 1)])
            vg = (tgt_next - tgt) / DT
            if t > P["T_launch"] - 0.2 and vg < vz - G * DT * 1.5:
                air = True
                vz -= G * DT
                z += vz * DT
                print("launched at", round(t, 2))
            else:
                vz = vg
                z = tgt
        # knee: critically damped spring, absorbs the landing
        ka = -144.0 * knee - 24.0 * kv
        kv += ka * DT
        knee += kv * DT
        zs[i] = z + knee
        airs[i] = air
    aim_h = floor_z(P["aim_ahead"]) + P["eye"]
    for f in range(sc.frame_start, sc.frame_end + 1):
        t = P["t_start"] + (f - 1) / P["fps"]
        i = int((t - P["t_start"]) / DT)
        s = ss[i]
        w = slide_w(t)
        pitch, yaw, roll, dz, dx = wobble(t, 1.0 - w)  # footstep tremor only while on your feet
        tp, ty, tr, side = slide(t)
        pitch, yaw, roll = pitch + w * tp, yaw + w * ty, roll + w * tr
        loc = Vector((path_x(s) + dx + w * side, s, zs[i] + dz))
        sa = s + P["aim_ahead"]
        aim_h += ((floor_z(sa) + eye_h(t)) - aim_h) * (1 - math.exp(-(1 / P["fps"]) / 0.35))
        aim = Vector((path_x(sa), sa, aim_h))
        q = (aim - loc).to_track_quat("-Z", "Y")
        m = q.to_matrix().to_4x4() @ Euler((math.radians(pitch), math.radians(yaw),
                                            math.radians(roll)), "XYZ").to_matrix().to_4x4()
        cam.matrix_world = Matrix.Translation(loc) @ m
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    air_t = ts[airs > 0]
    print("AIR:", (round(air_t[0], 2), round(air_t[-1], 2)) if len(air_t) else None,
          "total air s:", round(len(air_t) * DT, 2), "cliff m:", round(HC, 2))


lane_mesh()
props()
bake_camera()
print("s at events:", [round(x, 1) for x in (sE, sC, sL2, sLa, sD)],
      "floor at events:", [round(floor_z(x), 1) for x in (sE + 1, sC, sL2, sLa, sD, sD + 30)],
      "wall height:", [round(rim_z(x) - floor_z(x), 1) for x in (sE, sC, sL2, sLa, sD, sD + 40)])
bpy.ops.wm.save_as_mainfile(filepath=P["blend"])
if "render" in sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else False:
    bpy.ops.render.render(animation=True)
