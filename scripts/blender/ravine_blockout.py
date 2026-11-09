"""ABGRUND breakdown — the landslide crossing, grey blockout (2026-10-19).

Nick: "lets have the camera just gliding along a rail in the scene ... the camera could even stay
at the same height and let the ground fall out below. then we could have lights down in the
bottom that are reactive and expose the landscape naturally." Supersedes the slide and FPV tests.

The hollow way is cut by a gorge. At the edge (5:30.5) the trench runs out at the rim and the
ground drops away; the camera keeps its height and ABGRUND's speed, crossing ~115 m of open air
with a slow tilt down into the depth; the ground returns at the far rim exactly on the drop
(6:11.6) and the lane carries on. Forms at the bottom (lavender here) are where the reactive
lights will be.

    Blender -b --factory-startup --python ravine_blockout.py
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix, Euler, noise

P = dict(
    fps=24, t_start=320.0, t_end=380.0,
    TE=330.5, TC=344.2, TL2=364.8, TD=371.6,   # measured cue points (full piece, s)
    v=2.8, eye=1.6, lens=28.0, aim_ahead=8.0,
    wall=9.5,                                  # lane depth = rim height above the lane floor
    # the landslide (Nick: landslide; old but raw at the top; valley downhill to the right)
    hill=36.0, stream_x=120.0, valley_z=-75.0, stream_w=6.0,
    slip_z=-55.0, slip=20.0, scarp_h=8.0, head_h=20.0, scarp_w=3.0, flank=38.0,
    scar_cx=40.0, scarp=0.85,  # props only
    # v3 (Nick): the far notch 30 m lower; the camera falls into the gap; "it should just look down into
    # the bottom. like you fell off the cliff"; sink through a mist layer
    drop=30.0, freefall2=1.0, sink=1.3, fall_ease=5.0, catch=2.0, sink_roll=0.2,
    look_down=-55.0, look_in=None, look_roll=-30.0, look_fall2=0.8, look_up=3.0,
    mist_top=-25.0, mist_band=2.5,
    out="/Volumes/music/blender/renders/ravine_blockout_05/f_",
    blend="/Volumes/music/blender/abgrund_ravine_blockout.blend",
    res=(1280, 720),
)


def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


T0 = P["t_start"]
s_at = lambda t: (t - T0) * P["v"]
sE, sD = s_at(P["TE"]), s_at(P["TD"])
yc0, half = (sE + sD) / 2, (sD - sE) / 2
path_x = lambda y: 1.2 * math.sin(y / 38.0) + 0.4 * math.sin(y / 13.0 + 1.0)
zl = lambda y: -P["drop"] * min(max((y - sE) / (sD - sE), 0.0), 1.0)   # lane level: 30 m lower beyond the slide


def hillside_z(x):
    # the valley side the lane contours along: falls to the right (+x) toward the stream, rises to the left
    hs = math.tan(math.radians(P["hill"]))
    if x >= 3.3:
        z = P["wall"] - hs * (x - 3.3)
        return max(z, P["valley_z"] + hs * (x - P["stream_x"])) if x > P["stream_x"] else z
    if x <= -3.3:
        return P["wall"] + hs * (-x - 3.3)
    return P["wall"]


SC_X = [-35.0, -25.0, 0.0, 50.0, 100.0, 125.0]       # plan of the slide: half-width across the slope
SC_W = [0.0, 35.0, 57.5, 65.0, 58.0, 45.0]           # tongue-shaped: narrow head, widest mid-slope, spreads to the toe


def scar_e(x, y):
    # metres inside the slide's edge (negative = outside)
    if x < SC_X[0] or x > SC_X[-1]:
        return -1.0
    return float(np.interp(x, SC_X, SC_W)) - abs(y - yc0)


def scar_r(x, y):
    # kept for the props: < 1 inside the slide, ~1 at the torn edge
    e = scar_e(x, y)
    return 1.0 - e / 60.0


def scar_floor(x, y):
    # slip surface: below the lane line, falling down-valley; then the debris lobe on the valley floor
    z = P["slip_z"] - math.tan(math.radians(P["slip"])) * x
    lobe = P["valley_z"] + 0.5 * zl(y) + 3.0 + 3.0 * noise.noise(Vector((x * 0.06, y * 0.06, 4.0)))
    z = max(z, lobe)
    return z + 1.2 * noise.noise(Vector((x * 0.08, y * 0.08, 9.0)))


def ground_z(x, y):
    lat = x - path_x(y)
    h = hillside_z(x)
    lane = zl(y) + (h * sstep(1.35, 3.3, abs(lat)) if abs(lat) < 3.3 else h + 0.4 * noise.noise(Vector((x * 0.1, y * 0.1, 11.0))))
    e = scar_e(x, y)
    if e <= 0.0:
        return lane
    # raw scarp at the torn edge (taller toward the head), then debris slopes down to the trough floor
    sh = P["scarp_h"] + (P["head_h"] - P["scarp_h"]) * sstep(0.0, -30.0, x)
    sh *= 1.0 + 0.35 * noise.noise(Vector((x * 0.05, y * 0.05, 2.0)))
    z = lane - sh * sstep(0.0, P["scarp_w"], e) - math.tan(math.radians(P["flank"])) * max(0.0, e - P["scarp_w"])
    z += 0.8 * noise.noise(Vector((x * 0.12, y * 0.12, 6.0))) * sstep(P["scarp_w"], P["scarp_w"] + 4, e)  # lumpy debris
    return max(z, scar_floor(x, y))


def scar_young(x, y):
    # where the old slide has grown over: below the raw top band
    return scar_e(x, y) > P["scarp_w"] + 2.0


# ---------------------------------------------------------------- scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)
sc = bpy.context.scene
sc.render.fps = P["fps"]
sc.frame_start = 1
sc.frame_end = int(round((P["t_end"] - T0) * P["fps"]))
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


def terrain():
    lats = np.concatenate([np.arange(-120, -10, 1.5), np.arange(-10, 10, 0.15), np.arange(10, 220.01, 1.5)])
    rows = np.arange(-40, sD + 90, 0.3)
    bm = bmesh.new()
    grid = []
    for y in rows:
        cx = path_x(y)
        row = []
        for lat in lats:
            x = cx + lat
            z = ground_z(x, y)
            if 1.4 < abs(lat) < 3.25 and z > 0.05:  # trench wall relief
                x += math.copysign(0.35 * noise.noise(Vector((lat * 0.4, y * 0.45, z * 0.5))), lat)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(len(rows) - 1):
        for i in range(len(lats) - 1):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    ob = link("Terrain", bm, (0.5, 0.5, 0.5))
    for p in ob.data.polygons:
        p.use_smooth = True


def water():
    bm = bmesh.new()
    zw = lambda y: P["valley_z"] + 0.5 * zl(y) + 0.2
    ys = np.arange(-60, sD + 120, 2.0)
    wob = lambda y: P["stream_x"] + 4 * math.sin(y / 30.0)
    vs = [(bm.verts.new((wob(y) - P["stream_w"] / 2, y, zw(y))), bm.verts.new((wob(y) + P["stream_w"] / 2, y, zw(y)))) for y in ys]
    for (a, b), (c, d) in zip(vs, vs[1:]):
        bm.faces.new((a, c, d, b))
    link("Stream", bm, (0.16, 0.26, 0.30))


def props():
    rnd = random.Random(7)
    trees, young, lane, forms = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()

    def box(bm, c, sz, rot):
        r = bmesh.ops.create_cube(bm, size=1.0)
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*sz, 1))
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

    def cyl(bm, a, b, rad, seg=6, taper=0.6):
        d = b - a
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=rad, radius2=rad * taper, depth=d.length)
        m = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=m, verts=r["verts"])

    # mature forest on the intact hillside; trees right at the torn lip lean out over the void
    for _ in range(9000):
        x, y = rnd.uniform(-115, 215), rnd.uniform(-40, sD + 85)
        if abs(x - path_x(y)) < 3.6 or abs(x - P["stream_x"]) < 5:
            continue
        e = scar_e(x, y)
        if e > 0.0:
            continue
        base = Vector((x, y, ground_z(x, y) - 0.3))
        up = Vector((rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04), 1.0))
        if e > -5.0:  # undercut by the slide: leaning toward it
            to_c = Vector((P["scar_cx"] - x, yc0 - y, 0)).normalized()
            up = (up + to_c * rnd.uniform(0.15, 0.6)).normalized()
        cyl(trees, base, base + up * rnd.uniform(25, 35), rnd.uniform(0.25, 0.45))
    # the old slide grown over: young spruce and birch, low, on the slip surface only
    for _ in range(2500):
        x, y = rnd.uniform(-30, 115), rnd.uniform(yc0 - 70, yc0 + 70)
        if not scar_young(x, y) or abs(x - P["stream_x"]) < 4:
            continue
        base = Vector((x, y, ground_z(x, y) - 0.1))
        cyl(young, base, base + Vector((0, 0, rnd.uniform(2, 8))), rnd.uniform(0.6, 1.4), seg=5, taper=0.05)
    # roots hanging down the raw scarps from the torn edge
    for k in range(700):
        x = rnd.uniform(SC_X[0], P["stream_x"] - 10)
        y = yc0 + rnd.choice((-1, 1)) * (float(np.interp(x, SC_X, SC_W)) - 0.2)
        top = Vector((x, y, ground_z(x * 1.0, y) - 0.2))
        inward = Vector((P["scar_cx"] - x, yc0 - y, 0)).normalized()
        L = rnd.uniform(1.5, 7.0)
        bot_xy = Vector((x, y, 0)) + inward * L * 0.35
        cyl(lane, top, Vector((bot_xy.x, bot_xy.y, top.z - L)), rnd.uniform(0.03, 0.12))
    # the lane on both sides of the slide: stones on the floor, roots down the walls
    y = -40.0
    while y < sD + 85:
        cx = path_x(y)
        if scar_e(cx, y) < -0.5:
            for _ in range(2):
                sz = rnd.uniform(0.08, 0.4)
                box(lane, Vector((cx + rnd.uniform(-1.3, 1.3), y + rnd.uniform(0, 1), zl(y) + sz * 0.2)), (sz, sz * 1.2, sz * 0.7),
                    (rnd.random(), rnd.random(), rnd.random()))
            for _ in range(2):
                side = rnd.choice((-1, 1))
                top = Vector((cx + side * 3.25, y + rnd.uniform(0, 1), zl(y) + P["wall"] - 0.1))
                lb = 3.3 - 1.9 * rnd.uniform(0.25, 0.95)
                cyl(lane, top, Vector((cx + side * (lb + 0.15), top.y + rnd.uniform(-1.5, 1.5), zl(y) + P["wall"] * sstep(1.35, 3.3, lb) + 0.1)),
                    rnd.uniform(0.03, 0.09))
        y += 1.0
    # forms: toppled trunks and boulders the slide carried — on the slip surface under the crossing, and the toe
    for _ in range(260):
        q = rnd.random()
        if q < 0.35:
            x, y = rnd.uniform(-20, 25), rnd.uniform(yc0 - 50, yc0 + 50)    # below the fall, where the camera looks
        elif q < 0.6:
            # lodged on the far flank, where the view lands in the last seconds of the roll (measured: the
            # forms in view fell to zero by 6:01 without these)
            x, y = rnd.uniform(-14, 16), rnd.uniform(yc0 + 30, yc0 + 50)
        else:
            x, y = rnd.uniform(70, 118), rnd.uniform(yc0 - 55, yc0 + 55)    # the toe, in and by the stream
        if scar_e(x, y) < P["scarp_w"] + 6:
            continue
        z = ground_z(x, y)
        if rnd.random() < 0.55:
            sz = rnd.uniform(0.8, 3.0)
            box(forms, Vector((x, y, z + sz * 0.25)), (sz, sz * 1.1, sz * 0.7), (rnd.random(), rnd.random(), rnd.random()))
        else:
            a = rnd.uniform(0, math.pi)
            L = rnd.uniform(10, 28)
            d = Vector((math.cos(a), math.sin(a), 0)) * L / 2
            p0, p1 = Vector((x, y, 0)) - d, Vector((x, y, 0)) + d
            p0.z, p1.z = ground_z(p0.x, p0.y) + 0.5, ground_z(p1.x, p1.y) + 0.5
            cyl(forms, p0, p1, rnd.uniform(0.3, 0.5))
    link("Trees", trees, (0.62, 0.62, 0.62))
    link("YoungGrowth", young, (0.45, 0.52, 0.45))
    link("LaneProps", lane, (0.6, 0.6, 0.6))
    link("Forms", forms, (0.72, 0.6, 0.85))


def mist():
    # the top of the mist pooled in the slide bowl, shown as flat wisps so their motion reads in grey
    rnd = random.Random(11)
    bm = bmesh.new()
    for _ in range(3000):
        x, y = rnd.uniform(-30, 120), rnd.uniform(yc0 - 70, yc0 + 70)
        if scar_e(x, y) < 2.0:
            continue
        z = P["mist_top"] - rnd.uniform(0, P["mist_band"])
        if z < ground_z(x, y) + 1.0:
            continue
        sz = rnd.uniform(0.15, 0.4)  # flecks: a few percent coverage, enough to show the layer and its motion
        r = bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=sz)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x, y, z)) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, "Z") @ Matrix.Diagonal((1.0, 0.4, 1, 1)), verts=r["verts"])
    link("MistTop", bm, (0.75, 0.75, 0.78))


def fall_z():
    # camera height offset: free fall off the edge, a steady sink, held by the roll, a second free fall at the cut,
    # then eased into the far notch exactly on the drop
    TE, TC, TL2, TD = P["TE"], P["TC"], P["TL2"], P["TD"]
    dt = 1.0 / 240
    tt = np.arange(T0, P["t_end"] + 1, dt)
    rate = np.zeros_like(tt)
    g = 9.81
    for i, t in enumerate(tt):
        if TE <= t < TC:  # v4: a smooth fall, gathering speed (Nick: "the first is too abrupt")
            r = P["sink"] * sstep(TE, TE + P["fall_ease"], t)
        elif TC <= t < TL2:  # caught by the snare roll
            r = P["sink"] + (P["sink_roll"] - P["sink"]) * sstep(TC, TC + P["catch"], t)
        elif TL2 <= t < TL2 + P["freefall2"]:
            r = P["sink_roll"] + g * (t - TL2)
        elif TL2 + P["freefall2"] <= t < TD:
            r = -1.0  # filled below: glide into the notch
        else:
            r = 0.0
        rate[i] = r
    i0 = np.searchsorted(tt, TL2 + P["freefall2"])
    i1 = np.searchsorted(tt, TD)
    fallen = rate[:i0].sum() * dt
    v0 = P["sink_roll"] + g * P["freefall2"]
    # last stretch: decelerate from v0 and land the remaining distance exactly at TD
    rest = P["drop"] - fallen
    n = i1 - i0
    u = np.linspace(0, 1, n)
    shape = 1 - sstep_arr(u)
    k = (rest / dt - v0 * 0) / shape.sum()
    rate[i0:i1] = shape * k
    # blend the start of the glide from v0 so there is no step in speed
    blend = np.clip(u / 0.15, 0, 1)
    rate[i0:i1] = (1 - blend) * v0 + blend * rate[i0:i1]
    rate[i0:i1] *= rest / (rate[i0:i1].sum() * dt)
    z = -np.cumsum(rate) * dt
    return tt, z


def sstep_arr(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def look(t):
    # down into the bottom off the edge; rising through the snare roll; back down with the second fall; up for the notch
    TE, TC, TL2, TD = P["TE"], P["TC"], P["TL2"], P["TD"]
    a = P["look_down"] * sstep(TE, TC if P["look_in"] is None else TE + P["look_in"], t)  # v5: tipping forward until the catch
    a += (P["look_roll"] - P["look_down"]) * sstep(TC, TL2, t)
    a += (P["look_down"] - P["look_roll"]) * sstep(TL2, TL2 + P["look_fall2"], t)
    return a * (1 - sstep(TD - P["look_up"], TD - 0.2, t))


def wobble(t):
    fr = t * P["fps"]
    pitch = 0.33 * math.sin(2 * math.pi * fr / 72 + 0.3) + 0.08 * math.sin(2 * math.pi * fr / 11.5 + 1.1)
    yaw = 0.43 * math.sin(2 * math.pi * fr / 95 + 2.0) + 0.08 * math.sin(2 * math.pi * fr / 12.7 + 0.4)
    roll = 0.27 * math.sin(2 * math.pi * fr / 120 + 4.1)
    return pitch, yaw, roll, 0.015 * math.sin(2 * math.pi * fr / 83 + 0.7), 0.015 * math.sin(2 * math.pi * fr / 101 + 2.2)


def bake_camera():
    cd = bpy.data.cameras.new("Cam")
    cd.lens = P["lens"]
    cd.sensor_fit = "AUTO"
    cam = bpy.data.objects.new("Cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    tt, zf = fall_z()
    for f in range(sc.frame_start, sc.frame_end + 1):
        t = T0 + (f - 1) / P["fps"]
        y = s_at(t)
        pitch, yaw, roll, dz, dx = wobble(t)
        cz = P["eye"] + float(np.interp(t, tt, zf))
        loc = Vector((path_x(y) + dx, y, cz + dz))
        ya = y + P["aim_ahead"]
        aim = Vector((path_x(ya), ya, cz))
        q = (aim - loc).to_track_quat("-Z", "Y")
        m = q.to_matrix().to_4x4() @ Euler((math.radians(pitch + look(t)), math.radians(yaw), math.radians(roll)), "XYZ").to_matrix().to_4x4()
        cam.matrix_world = Matrix.Translation(loc) @ m
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)


terrain()
water()
props()
mist()
bake_camera()
import itertools
cross = [y for y in np.arange(sE - 5, sD + 5, 0.25) if ground_z(path_x(y), y) < zl(y) - 0.5]
tt_, zf_ = fall_z()
for tq in (P["TE"] + 5, P["TC"], P["TL2"], P["TL2"] + 1.0, P["TD"]):
    yq = s_at(tq); cz = P["eye"] + float(np.interp(tq, tt_, zf_))
    print(f"t {tq:.1f}: camera z {cz:.1f}, ground below {ground_z(path_x(yq), yq):.1f}, clearance {cz - ground_z(path_x(yq), yq):.1f}")
print("edge s", round(sE, 1), "far rim s", round(sD, 1), "open air over the lane from", round(cross[0], 1), "to", round(cross[-1], 1),
      "| drop below camera at mid-crossing", round(P["eye"] - ground_z(path_x(yc0), yc0), 1),
      "| drop below camera 5 s after the edge", round(P["eye"] - ground_z(path_x(sE + 14), sE + 14), 1),
      "| toe / valley floor", round(ground_z(100, yc0), 1))
bpy.ops.wm.save_as_mainfile(filepath=P["blend"])
