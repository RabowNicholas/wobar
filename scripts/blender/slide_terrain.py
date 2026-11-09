"""ABGRUND's landslide crossing in hohlweg_3 (I-3, 2026-10-19).

Builds `SlideTerrain`: the old landslide that cut the lane between the edge (along 1257.2, 5:30.5) and the
drop (along 1372.2, 6:11.6), set into a side of the valley the lane descends - the valley falls away to the
right of travel toward a stream, the slope rises to the left. Geography as approved in the grey blockout
(ravine_blockout.py v5): raw scarps at the torn edge (~8 m, ~20 m at the uphill head), debris flanks at ~38 deg
down to a grown-over slip floor ~55 m below the near edge, a hummocky toe at the stream; the lane resumes on
the far flank 30 m lower (the lane_zshift step).

Laid out on a straight axis fitted through this stretch of the spine (the lane itself wiggles with ~30 m
radius bends, so lane coordinates would fold at distance); the slide's plan is solved so its edge crosses the
lane exactly at along 1257.2 and 1372.2.

Also builds two hidden flat masks far below the scene, used by raycast to tag what the slide replaces:
`SlideMask_bowl` (the slide's interior - lane, water, roots and lane plants there are cut) and
`SlideMask_footprint` (where the terrain replaces the forest floor). Nothing is deleted from the source
meshes, so scatter triangle numbering - and so every plant - stays put.

Coarse far away on purpose (render time): 0.6 m near the slide and the lane, 3 m on the distant hillside.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy, bmesh, math
from mathutils.bvhtree import BVHTree
import numpy as np
from mathutils import Vector, kdtree, noise

P = dict(
    A0=1257.2, A1=1372.2,                 # edge / drop, metres along the spine
    hill=38.0, valley_x=120.0, valley_depth=82.0, opp_hill=30.0,
    uphill=18.0, uphill_cap=14.0,          # a gentle rise; at 26 deg / 32 m it read as an isolated dome (polish 2026-10-20)
    fade_before=60.0, fade_after=95.0, fade_len=40.0,   # side valley extent around the gap (s), and its fade
    # past the slide the valley runs on (2026-10-21, the bare "dam" closing the view at 5:30): the fade only applies
    # within this band right of the lane, so the lane's own shelf returns to forest floor but the valley does not
    runs_on=(30.0, 60.0),
    # slide plan: half-width across the slope (x = metres right of the lane). Flat over x -30..0 so the torn edge
    # cuts straight across the whole lane, which wiggles about +-12 m here; the head sits further uphill.
    # v3 (Nick, after two reference photos; "lean #2"): a deep amphitheatre head with slumped blocks below it,
    # a streaked chute down the slope, a fan on the valley floor. Narrow at the crown, widest at the lane (fixed by
    # the timing), a neck, then the fan spreading along the valley.
    SC_X=(-62.0, -55.0, -45.0, -30.0, -12.0, 0.0, 30.0, 70.0, 105.0, 125.0, 145.0, 160.0),
    SC_W=(0.0, 28.0, 42.0, 52.0, 57.5, 57.5, 52.0, 42.0, 38.0, 58.0, 62.0, 0.0),
    # v4 (Nick: "is that how we are building it" - the USGS rotational-slide diagram; "yes rebuild"): the ground
    # moved down rather than vanishing. Surface = the old slope displaced by D(x): ~45-47 m down at the head (under
    # the lane), less down the body, 0 at the toe of the surface of rupture, then pushed UP over the intact slope at
    # the foot. The body breaks into back-tilted blocks between minor scarps.
    D_X=(-62.0, 0.0, 100.0, 112.0, 140.0, 160.0), D_V=(47.0, 45.0, 0.0, -9.0, -10.0, 0.0),
    SCARPS=(20.0, 45.0, 70.0),             # minor scarps: x where one block ends and the next begins
    BLOCK_A=(8.0, 6.0, 4.0, 3.0),           # back-tilt of each block (head first): metres higher at its downhill end
    # (Nick, 2026-10-20: "what are the ripples at the edges? shouldnt those be more smooth. they are off in the
    # distance anyways") - crown cracks, foot ridges and toe cracks off, walls barely ragged; body cracks stay (near)
    crown_wall=68.0, flank_wall=62.0, wall_ragged=0.5,
    CRACKS_T=(32.0, 38.0, 55.0, 61.0, 80.0, 88.0),   # transverse cracks across the body (x)
    ridges=(88.0, 100.0, 140.0, 152.0), ridge_h=0.0, ridge_wl=6.5,  # transverse ridges in the foot
    radial=(1e9, 1e9 + 1), radial_n=9,      # radial cracks at the toe
    CRACKS_C=(),              # crown cracks: metres outside the main scarp's edge
    scarp_h=8.0, head_h=20.0, scarp_w=3.0, flank=38.0, slip_z=-55.0, slip=20.0,
    lane_half=11.0, under=0.4,             # 11 not 15: the lane's swept edge and the nearest-point distance disagree on bends
    ragged=2.5,
    # the lane's ends broken by the slide (Nick: "just 1" - not cut with a knife): walls slump over the last 14 m
    # (the same rule as the EdgeSlump group on the lane), and the old lane's runoff has cut a gully into the scarp
    # below each mouth with a debris fan at its foot
    slump_len=14.0, slump=0.62, floor_sag=0.5, gully=3.5, gully_w=2.5, fan=2.5, fan_w=7.0,             # terrain tucks this far under the lane's own 15 m strip / the forest floor
    fine=0.6, coarse=3.0, fine_x=45.0, fine_x_down=100.0, far_x=330.0,
    mask_z=-1000.0,
)


def sstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


class Frame:
    """Spine lookups and the straight axis through the slide stretch."""

    def __init__(self):
        sp = bpy.data.objects["Spine"]
        cu = sp.data
        r0 = cu.resolution_u
        cu.resolution_u = 64
        dg = bpy.context.evaluated_depsgraph_get()
        me = sp.evaluated_get(dg).to_mesh()
        V = np.array([v.co[:] for v in me.vertices])
        sp.evaluated_get(dg).to_mesh_clear()
        cu.resolution_u = r0
        self.V = V[:, :2]
        self.acc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(V, axis=0), axis=1))]
        self.kd = kdtree.KDTree(len(V))
        for i, v in enumerate(V):
            self.kd.insert((v[0], v[1], 0.0), i)
        self.kd.balance()
        sel = (self.acc > 1150) & (self.acc < 1500)
        pts = self.V[sel]
        self.O = pts.mean(0)
        u = np.linalg.svd(pts - self.O)[2][0]
        if np.dot(u, self.V[-1] - self.V[0]) < 0:
            u = -u
        self.u = u
        self.r = np.array([u[1], -u[0]])           # right of travel
        # the lane's own edge height (forest-floor level at |lat| 15), per metre along
        L = bpy.data.objects["Lane"].evaluated_get(dg).to_mesh()
        n = len(L.vertices)
        co = np.empty(n * 3); L.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        al = np.empty(n); L.attributes["along"].data.foreach_get("value", al)
        la = np.empty(n); L.attributes["lat"].data.foreach_get("value", la)
        bpy.data.objects["Lane"].evaluated_get(dg).to_mesh_clear()
        e = np.abs(np.abs(la) - 15.0) < 0.05
        order = np.argsort(al[e])
        self.edge_a, self.edge_z = al[e][order], co[e, 2][order]
        # the lane's actual (collapsed) surface around the two lips, to start the scarp exactly from it
        bm = bmesh.new()
        bm.from_object(bpy.data.objects["Lane"], dg)
        far = [v for v in bm.verts if v.index < len(al) and not (abs(al[v.index] - P["A0"]) < 22 or abs(al[v.index] - P["A1"]) < 22)]
        bmesh.ops.delete(bm, geom=far, context="VERTS")
        self.lane_bvh = BVHTree.FromBMesh(bm)
        bm.free()
        # along as a function of the straight-axis coordinate s (for points far from the snaking lane)
        s_sp = (self.V - self.O) @ self.u
        keep = np.r_[True, np.diff(np.maximum.accumulate(s_sp)) > 0]
        self.s_sp, self.a_sp = np.maximum.accumulate(s_sp)[keep], self.acc[keep]
        self.x_sp = ((self.V - self.O) @ self.r)[keep]      # the lane's lateral position along the axis

    def at(self, a):
        i = int(np.clip(np.searchsorted(self.acc, a), 1, len(self.acc) - 1))
        return self.V[i]

    def lane(self, x, y):
        """(along, signed lat: + left, - right) of the nearest lane point."""
        _, i, _ = self.kd.find((x, y, 0.0))
        i = min(max(i, 1), len(self.V) - 2)
        t = self.V[i + 1] - self.V[i - 1]
        t /= np.linalg.norm(t)
        d = np.array([x, y]) - self.V[i]
        return self.acc[i], float(d[0] * -t[1] + d[1] * t[0])

    def sx(self, x, y):
        d = np.array([x, y]) - self.O
        return float(d @ self.u), float(d @ self.r)

    def xy(self, s, xa):
        p = self.O + s * self.u + xa * self.r
        return float(p[0]), float(p[1])

    def lane_z(self, x, y):
        hit = self.lane_bvh.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200.0)
        return None if hit[0] is None else hit[0].z

    def rim(self, a):
        return float(np.interp(a, self.edge_a, self.edge_z))

    def lane_x(self, s):
        return float(np.interp(s, self.s_sp, self.x_sp))

    def along_far(self, s):
        return float(np.interp(s, self.s_sp, self.a_sp))


def zl(a):
    A0, A1, DZ = bpy.context.scene["lane_zshift"]
    return DZ * min(max((a - A0) / (A1 - A0), 0.0), 1.0)


class Slide:
    def __init__(self, F):
        self.F = F
        sE, xE = F.sx(*F.at(P["A0"]))
        sD, xD = F.sx(*F.at(P["A1"]))
        gap = (F.acc > P["A0"]) & (F.acc < P["A1"])
        self.x0 = float(np.mean([F.sx(*v)[1] for v in F.V[gap]]))     # the lane's mean lateral position in the gap
        h1, h2 = self.hw(xE - self.x0), self.hw(xD - self.x0)
        self.k = (sD - sE) / (h1 + h2)                                    # plan solved through both crossings
        self.sc = sE + self.k * h1
        self.sE, self.sD = sE, sD
        print(f"slide plan: centre s {self.sc:.1f}, scale {self.k:.3f}, lane x0 {self.x0:.1f}; edge s {sE:.1f}, drop s {sD:.1f}")

    def hw(self, x):
        if x < P["SC_X"][0] or x > P["SC_X"][-1]:
            return -1.0
        return float(np.interp(x, P["SC_X"], P["SC_W"]))

    def e(self, s, xa):
        h = self.hw(xa - self.x0)
        if h < 0:
            return -1e3
        # a torn edge wanders: up to ~2.5 m either way (the masks use this too, so the lane's cut follows it)
        # ...except across the lane itself, so the lip still crosses it exactly at the edge and the drop (5:30.5 / 6:11.6)
        damp = sstep(5.0, 12.0, abs(xa - self.F.lane_x(s)))
        return self.k * h - abs(s - self.sc) + damp * P["ragged"] * noise.noise(Vector((s * 0.12, xa * 0.12, 3.0)))

    def fade(self, s):
        return sstep(self.sE - P["fade_before"] - P["fade_len"], self.sE - P["fade_before"], s) * \
            (1 - sstep(self.sD + P["fade_after"], self.sD + P["fade_after"] + P["fade_len"], s))

    def height(self, x, y):
        """-> (z, along, lat, e, inside_lane_strip)"""
        F = self.F
        a, lat = F.lane(x, y)
        s, xa = F.sx(x, y)
        xr = -lat                      # metres right of the lane (downhill)
        hf = self.fade(s)
        # near the lane take the level from the lane itself; further out from the straight axis (the snaking lane's
        # nearest point can be 30 m lower or higher on the far side of a bend)
        w = sstep(20.0, 40.0, abs(lat))
        a_lvl = (1 - w) * a + w * F.along_far(s)
        R = F.rim(a_lvl)
        n = 0.4 * noise.noise(Vector((x * 0.1, y * 0.1, 11.0)))
        # the slope the lane contours along
        if xr > 15.0:
            if s > self.sc:
                hf += (1.0 - hf) * sstep(*P["runs_on"], xr)
            z = R + n - hf * math.tan(math.radians(P["hill"])) * (xr - 15.0)
            vz = R - hf * P["valley_depth"]
            vx = self.x0 + P["valley_x"]
            z = max(z, vz + hf * math.tan(math.radians(P["opp_hill"])) * max(0.0, xa - vx - 6.0) - 0.8 * hf * (1 - sstep(2, 6, abs(xa - vx))))
        elif xr < -15.0:
            z = R + n + hf * min(math.tan(math.radians(P["uphill"])) * (-xr - 15.0), P["uphill_cap"])
        else:                          # the trench (only matters inside the slide, where the lane is cut)
            D = min(abs(a - P["A0"]), abs(a - P["A1"]))
            f = 1.0 - sstep(0.0, P["slump_len"], D)
            e0 = self.e(s, xa)
            n = 1.3 if e0 <= 0.0 else 0.6 + 0.65 * (0.5 + 0.5 * noise.noise(Vector((x * 0.35, y * 0.35, 7.0))))
            wall = sstep(1.35, 3.3, abs(lat)) * (1.0 - P["slump"] * f * n)
            z = zl(a_lvl) + (R - zl(a_lvl)) * wall - P["floor_sag"] * f * (1.0 - sstep(0.6, 1.6, abs(lat)))
            if D < 20.0:               # at the lips: the lane's real collapsed surface, so lane and scarp meet exactly
                lz = F.lane_z(x, y)
                if lz is not None:
                    z = lz
            # inside the slide the lane went with the ground: past the first few metres from a lip there is no trench
            if e0 > 0.0:
                z += (R - z) * sstep(3.0, 9.0, e0)
        e = self.e(s, xa)
        self.last_block, self.last_raw = 0.0, 0.0
        x = xa - self.x0
        u = s - self.sc
        if -12.0 < e <= 0.0 and x < -20.0:     # crown cracks: tension cracks on the intact ground above the main scarp
            for c in P["CRACKS_C"]:
                g = math.exp(-((-e - c + 0.6 * noise.noise(Vector((u * 0.08, x * 0.08, 31.0 + c)))) / 0.25) ** 2)
                z -= 0.9 * g
                self.last_raw = max(self.last_raw, g)
        if e > 0.0:
            pre = z
            D = float(np.interp(x, P["D_X"], P["D_V"]))
            # back-tilted blocks between minor scarps: each block's surface rises toward its downhill end, then drops
            b = [P["D_X"][0]] + list(P["SCARPS"]) + [P["D_X"][2]]
            seg = 0
            while seg < len(b) - 2 and x >= b[seg + 1]:
                seg += 1
            frac = min(max((x - b[seg]) / (b[seg + 1] - b[seg]), 0.0), 1.0)
            A = P["BLOCK_A"][min(seg, len(P["BLOCK_A"]) - 1)] * (1.0 - sstep(85.0, 100.0, x))
            D -= A * (frac - 0.5)
            scarp_face = 0.0
            for xb in P["SCARPS"]:
                scarp_face = max(scarp_face, math.exp(-((x - xb) / 1.1) ** 2))
            # walls: how deep the ground can sit this far inside the edge (main scarp near-vertical, flanks steep)
            wall_deg = P["crown_wall"] + (P["flank_wall"] - P["crown_wall"]) * sstep(-35.0, -5.0, x)
            wall = math.tan(math.radians(wall_deg)) * e + P["wall_ragged"] * noise.noise(Vector((x * 0.2, s * 0.2, 2.0)))
            half = self.k * max(self.hw(x), 1e-3)
            q = min(max(1.0 - e / half, 0.0), 1.0)          # 0 down the middle, 1 at the edge
            if D > 0.0:
                cut = min(wall, D)
                zz = pre - cut
                on_wall = 1.0 if wall < D else 0.0
            else:                                           # the foot rides up over the slope, thinning to its edges
                zz = pre - D * (1.0 - q * q)
                on_wall = 0.0
            # transverse cracks across the body, ridges in the foot, radial cracks at the toe
            crack = 0.0
            for xc in P["CRACKS_T"]:
                crack = max(crack, math.exp(-((x - xc + 1.2 * noise.noise(Vector((u * 0.06, 41.0 + xc, 0.0)))) / 0.35) ** 2) * (1 - q ** 4))
            zz -= 1.3 * crack
            r0, r1, r2, r3 = P["ridges"]
            zz += P["ridge_h"] * math.sin(2 * math.pi * x / P["ridge_wl"]) * sstep(r0, r1, x) * (1 - sstep(r2, r3, x)) * (1 - q * q)
            rc = 0.0
            if x > P["radial"][0]:
                th = math.atan2(u, x - P["radial"][0] + 10.0)
                rc = math.exp(-(math.sin(th * P["radial_n"]) / 0.12) ** 2) * sstep(P["radial"][0], P["radial"][1], x) * sstep(0.0, 4.0, e)
                zz -= 0.9 * rc
            zz += 0.5 * noise.noise(Vector((u * 0.15, x * 0.15, 9.0))) * sstep(2.0, 6.0, e)
            if abs(lat) < 12.0:        # the runoff gully below each lane mouth, and its fan
                zz -= P["gully"] * math.exp(-(lat / P["gully_w"]) ** 2) * sstep(0.0, 3.0, e) * (1 - sstep(14.0, 24.0, e))
            raw = max(on_wall, scarp_face * (1.0 if D > 0 else 0.0), crack, rc)
            self.last_raw = raw
            self.last_block = 1.0 - raw                    # the moved ground keeps its vegetation
            z = zz
        return z, a, lat, e, abs(lat) < P["lane_half"]


def _grid_axis(lo, hi, flo, fhi, fine, coarse):
    out = list(np.arange(lo, flo, coarse)) + list(np.arange(flo, fhi, fine)) + list(np.arange(fhi, hi + 1e-6, coarse))
    return np.array(sorted(set(round(v, 3) for v in out)))


def build():
    F = Frame()
    S = Slide(F)
    ss = _grid_axis(S.sE - P["fade_before"] - P["fade_len"] - 15, S.sD + P["fade_after"] + P["fade_len"] + 15,
                    S.sE - 15, S.sD + 15, P["fine"], P["coarse"] * 0.8)
    xs = _grid_axis(S.x0 - 150, S.x0 + 170, S.x0 - 70, S.x0 + P["fine_x_down"], P["fine"], P["coarse"])
    # the valley's far side, out to where it rises past the rim and closes the horizon - very coarse, it is only a skyline
    xs = np.array(sorted(set(list(xs) + list(np.arange(S.x0 + 178, S.x0 + P["far_x"] + 1, 8.0)))))
    print("grid", len(ss), "x", len(xs))
    bm = bmesh.new()
    lay = {k: bm.verts.layers.float.new(k) for k in ("along", "lat", "slide_e", "keep", "xr", "block", "raw")}
    f0, f1 = S.sE - P["fade_before"] - P["fade_len"], S.sD + P["fade_after"] + P["fade_len"]   # the footprint
    grid = []
    for s in ss:
        row = []
        for xa in xs:
            x, y = F.xy(s, xa)
            z, a, lat, e, strip = S.height(x, y)
            keep = 1.0
            if strip and e < -2.5 and not (P["A0"] + 0.3 < a < P["A1"] - 0.3):
                keep = 0.0             # the lane's own mesh covers this (everything between the lips is cut from the lane)
            elif strip or (e > -2.5 and e <= 0.0) or s < f0 or s > f1:
                z -= P["under"]        # tucked under the lane's edge / the forest floor beyond the footprint
            v = bm.verts.new((x, y, z))
            v[lay["along"]], v[lay["lat"]], v[lay["slide_e"]], v[lay["keep"]] = a, lat, e, keep
            v[lay["xr"]] = xa - S.x0
            v[lay["block"]], v[lay["raw"]] = (S.last_block, S.last_raw) if e > 0.0 else (0.0, 0.0)
            row.append(v)
        grid.append(row)
    for j in range(len(ss) - 1):
        for i in range(len(xs) - 1):
            q = (grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])
            if sum(v[lay["keep"]] for v in q) >= 4:
                bm.faces.new(q)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    me = bpy.data.meshes.get("SlideTerrain") or bpy.data.meshes.new("SlideTerrain")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.get("SlideTerrain") or bpy.data.objects.new("SlideTerrain", me)
    ob.data = me
    if not ob.users_collection:
        (bpy.data.collections.get("LANE") or bpy.context.scene.collection).objects.link(ob)
    print("SlideTerrain:", len(me.vertices), "verts", len(me.polygons), "faces")
    _masks(F, S)
    return ob


def _mask(name, F, cells):
    bm = bmesh.new()
    for (s0, x0, s1, x1) in cells:
        vs = [bm.verts.new((*F.xy(s, x), P["mask_z"])) for s, x in ((s0, x0), (s1, x0), (s1, x1), (s0, x1))]
        bm.faces.new(vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3)
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
    ob.data = me
    if not ob.users_collection:
        bpy.context.scene.collection.objects.link(ob)
    ob.hide_render = True
    ob.hide_viewport = True
    return ob


def _masks(F, S):
    # the slide's interior (where the lane, its water, roots and plants are gone), as 0.5 m cells
    cells = []
    for s in np.arange(S.sc - 75, S.sc + 75, 0.5):
        for xa in np.arange(S.x0 - 75, S.x0 + 130, 0.5):
            if S.e(s + 0.25, xa + 0.25) > 0.0:
                cells.append((s, xa, s + 0.5, xa + 0.5))
    _mask("SlideMask_bowl", F, cells)
    # where the terrain replaces the forest floor: its full width, between the fades
    s0 = S.sE - P["fade_before"] - P["fade_len"]
    s1 = S.sD + P["fade_after"] + P["fade_len"]
    _mask("SlideMask_footprint", F, [(s0, S.x0 - 160, s1, S.x0 + P["far_x"] + 10)])
    print("masks: bowl", len(cells), "cells")
